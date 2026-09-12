"""
sprezzature-colors: the FastAPI HTTP surface.

Module summary
--------------
FastAPI is a Python web framework for building HTTP APIs. This module
exposes the functions in :mod:`sprezzature_colors` over HTTP, so a design
system in TypeScript, a CI job in Go, or a shell script with ``curl`` can
run the same colour checks the Python library and the command lines run.
There is one implementation underneath: every route below calls a function
re-exported by the package, never a second copy of the arithmetic.

What ships here
---------------
- ``GET  /health``: a liveness probe, so a monitor can tell the app is up.
- ``GET  /v1/palette``: the house palette, as name → hex.
- ``POST /v1/contrast``: contrast ratios and WCAG verdicts for colour pairs.
- ``POST /v1/cvd``: how colours look to a colour-blind viewer.
- ``POST /v1/adjust``: lighten or darken, in perceptual OKLab space.
- ``GET  /v1/psychology/{colour}``: what a colour is associated with.

Why these six
-------------
They are the questions a design review actually asks, and each one has a
defensible answer rather than an opinion: a contrast ratio is a number the
WCAG standard defines, a CVD simulation is a published matrix, and the
palette is a file. Anything that would need taste rather than arithmetic
belongs in the skill, not here.

Install the extra to get the runtime dependencies::

    pip install 'sprezzature-colors[api]'

Then run the app with any ASGI server::

    uvicorn sprezzature_colors.api:app --host 0.0.0.0 --port 8000

Usage example
-------------
>>> # Start the server:
>>> #   uvicorn sprezzature_colors.api:app --reload
>>> # Check a pair:
>>> #   curl -X POST localhost:8000/v1/contrast \\
>>> #        -H 'content-type: application/json' \\
>>> #        -d '{"pairs":[{"foreground":"#595959","background":"#ffffff"}]}'
>>> # Full OpenAPI docs at http://localhost:8000/docs

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

from typing import Literal

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import RedirectResponse
except ImportError as exc:  # pragma: no cover - dependency guard
    raise ImportError(
        "The FastAPI HTTP surface requires the [api] extra. "
        "Install with: pip install 'sprezzature-colors[api]'"
    ) from exc

from pydantic import BaseModel, Field

from . import (
    CVD_MATRICES,
    __version__ as _VERSION,
    concept_search,
    contrast_ratio_hex,
    darken,
    emotions,
    lighten,
    load_palette,
    meets_wcag,
    name_to_hex,
    parse_hex,
    psychology_for,
    rgb_to_hex,
    simulate_pixel,
)

app = FastAPI(
    title="Sprezzature Colors API",
    description=(
        "HTTP surface for sprezzature-colors: WCAG contrast, colour-vision-"
        "deficiency simulation, the house palette, and colour psychology."
    ),
    version=_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


class Pair(BaseModel):
    """One foreground/background pair to check."""

    foreground: str = Field(description='Hex colour, e.g. "#595959". A palette name also works.')
    background: str = Field(description='Hex colour, e.g. "#ffffff". A palette name also works.')
    level: Literal["AA", "AAA"] = Field(default="AA", description="WCAG conformance level.")
    size: Literal["normal", "large"] = Field(
        default="normal",
        description='Text size band. "large" is 18 pt, or 14 pt bold, and has a lower threshold.',
    )


class ContrastRequest(BaseModel):
    """Body for ``POST /v1/contrast``."""

    pairs: list[Pair] = Field(description="Pairs to check. One request can carry a whole palette.")


class CvdRequest(BaseModel):
    """Body for ``POST /v1/cvd``."""

    colors: list[str] = Field(description="Hex colours, or palette names.")
    kinds: list[Literal["protanopia", "deuteranopia", "tritanopia"]] | None = Field(
        default=None, description="Which deficiencies to simulate. Omit for all three."
    )


class AdjustRequest(BaseModel):
    """Body for ``POST /v1/adjust``."""

    colors: list[str] = Field(description="Hex colours, or palette names.")
    amount: float = Field(
        default=0.1, ge=-1.0, le=1.0,
        description="How far to move, in OKLab lightness. Positive lightens, negative darkens.",
    )


def _resolve(value: str) -> str:
    """
    Accept either a hex string or a palette name, and return hex.

    Letting a caller write ``"Blue"`` where a hex is expected is the kind of
    convenience that pays for itself: the palette is the point of having a
    palette, and forcing everyone to look up the hex first invites the
    hand-copied codes this repository exists to stop.

    Parameters
    ----------
    value : str
        ``"#2563eb"`` or a palette name.

    Returns
    -------
    str
        Hex colour.

    Raises
    ------
    fastapi.HTTPException
        400 if the value is neither a hex colour nor a known palette name.
    """
    if value.startswith("#"):
        return value
    try:
        return name_to_hex(value)
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{value!r} is neither a hex colour nor a palette name.",
        ) from exc


@app.get("/health", tags=["meta"], operation_id="health")
def health() -> dict:
    """
    Liveness probe — no dependency check, just proves the app is up.

    Returns
    -------
    dict
        ``{"status": "ok"}``.
    """
    return {"status": "ok"}


@app.get("/v1/palette", tags=["palette"], operation_id="get_palette")
def palette() -> dict:
    """
    The house palette: every name, its hex, and its light variant.

    Returns
    -------
    dict
        ``{"colors": [{"name": ..., "hex": ...}, ...]}``.
    """
    return {"colors": load_palette()}


@app.post("/v1/contrast", tags=["accessibility"], operation_id="check_contrast")
def contrast(request: ContrastRequest) -> dict:
    """
    Contrast ratio and WCAG verdict for each pair.

    The ratio is the WCAG 2.x definition: relative luminance of the lighter
    colour plus 0.05, over the darker plus 0.05, so it runs from 1 (identical)
    to 21 (black on white).

    Parameters
    ----------
    request : ContrastRequest
        The pairs to check.

    Returns
    -------
    dict
        One result per pair, with ``ratio``, ``passes``, and the ``required``
        threshold that verdict was measured against.
    """
    thresholds = {("AA", "normal"): 4.5, ("AA", "large"): 3.0,
                  ("AAA", "normal"): 7.0, ("AAA", "large"): 4.5}
    results = []
    for pair in request.pairs:
        fg, bg = _resolve(pair.foreground), _resolve(pair.background)
        ratio = contrast_ratio_hex(fg, bg)
        results.append({
            "foreground": fg,
            "background": bg,
            "ratio": round(ratio, 2),
            "level": pair.level,
            "size": pair.size,
            "required": thresholds[(pair.level, pair.size)],
            "passes": meets_wcag(fg, bg, level=pair.level, size=pair.size),
        })
    return {"results": results}


@app.post("/v1/cvd", tags=["accessibility"], operation_id="simulate_color_blindness")
def cvd(request: CvdRequest) -> dict:
    """
    How each colour looks to a viewer with each colour-vision deficiency.

    Uses the Machado matrices, the published linear approximations. Two
    colours that stay distinct here survive the most common form of
    colour blindness; two that converge were never a safe pair.

    Parameters
    ----------
    request : CvdRequest
        Colours and which deficiencies to simulate.

    Returns
    -------
    dict
        One entry per input colour, mapping each deficiency to the hex a
        viewer with it would perceive.
    """
    kinds = request.kinds or list(CVD_MATRICES)
    results = []
    for raw in request.colors:
        hex_value = _resolve(raw)
        simulated = {
            kind: rgb_to_hex(simulate_pixel(parse_hex(hex_value), CVD_MATRICES[kind]))
            for kind in kinds
        }
        results.append({"input": hex_value, "simulated": simulated})
    return {"results": results}


@app.post("/v1/adjust", tags=["palette"], operation_id="adjust_lightness")
def adjust(request: AdjustRequest) -> dict:
    """
    Lighten or darken colours in OKLab, not in RGB.

    OKLab is perceptually uniform, so the same step looks like the same step
    whatever the hue. Doing this in RGB makes yellows wash out while blues
    barely move, which is why hand-tuned "hover" colours so often look
    inconsistent across a palette.

    Parameters
    ----------
    request : AdjustRequest
        Colours and how far to move them.

    Returns
    -------
    dict
        One entry per colour, with the adjusted hex.
    """
    move = lighten if request.amount >= 0 else darken
    amount = abs(request.amount)
    return {
        "results": [
            {"input": (c := _resolve(raw)), "adjusted": move(c, amount)}
            for raw in request.colors
        ]
    }


@app.get("/v1/psychology/{color}", tags=["psychology"], operation_id="get_color_psychology")
def psychology(color: str) -> dict:
    """
    What a colour is conventionally associated with.

    Returns associations, not facts: these are Western design conventions,
    and they are the kind of thing to check against an audience rather than
    to apply blindly.

    Parameters
    ----------
    color : str
        Hex colour or palette name.

    Returns
    -------
    dict
        Associations for the colour, plus the emotion table for context.

    Raises
    ------
    fastapi.HTTPException
        404 when the colour has no entry.
    """
    found = psychology_for(_resolve(color))
    if found is None:
        raise HTTPException(status_code=404, detail=f"no psychology entry for {color!r}")
    return {"color": color, "associations": found, "emotions": emotions()}


@app.get("/v1/concepts", tags=["psychology"], operation_id="search_concepts")
def concepts(keyword: str) -> dict:
    """
    Colours associated with a concept keyword.

    Parameters
    ----------
    keyword : str
        A word such as ``"trust"`` or ``"urgency"``.

    Returns
    -------
    dict
        Matching colour names, possibly empty.
    """
    return {"keyword": keyword, "colors": concept_search(keyword)}


@app.get("/docs-redirect", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    """Convenience redirect to the interactive API docs."""
    return RedirectResponse(url="/docs")
