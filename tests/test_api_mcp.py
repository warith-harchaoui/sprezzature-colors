"""
Tests for the HTTP and MCP surfaces.

These check the *seam*, not the colour arithmetic — that is covered by
``test_colors.py`` and is the same code underneath. What can break here is
the wiring: a route that stops matching its Pydantic model, an
``operation_id`` renamed so an agent's tool disappears, or a fastapi-mcp
upgrade that moves ``mount()``. All three fail silently at import time
rather than loudly, which is what these tests are for.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from sprezzature_colors.api import app  # noqa: E402

client = TestClient(app)


def test_health() -> None:
    """The liveness probe answers."""
    assert client.get("/health").json() == {"status": "ok"}


def test_contrast_matches_the_library() -> None:
    """A known pair returns the WCAG ratio, not an approximation of it."""
    body = {"pairs": [{"foreground": "#000000", "background": "#ffffff"}]}
    result = client.post("/v1/contrast", json=body).json()["results"][0]
    assert result["ratio"] == 21.0
    assert result["passes"] is True


def test_contrast_fails_a_pair_that_should_fail() -> None:
    """A test that only ever passes proves nothing; this one must fail."""
    body = {"pairs": [{"foreground": "#999999", "background": "#ffffff"}]}
    result = client.post("/v1/contrast", json=body).json()["results"][0]
    assert result["ratio"] < 4.5
    assert result["passes"] is False


def test_large_text_has_a_lower_bar() -> None:
    """The size band changes the threshold, as WCAG defines it."""
    pair = {"foreground": "#767676", "background": "#ffffff"}
    normal = client.post("/v1/contrast", json={"pairs": [pair]}).json()["results"][0]
    large = client.post(
        "/v1/contrast", json={"pairs": [{**pair, "size": "large"}]}
    ).json()["results"][0]
    assert normal["required"] == 4.5
    assert large["required"] == 3.0


def test_palette_name_is_accepted_where_a_hex_is() -> None:
    """Callers may write "Blue"; the palette is the point of having one."""
    body = {"pairs": [{"foreground": "Blue", "background": "#ffffff"}]}
    response = client.post("/v1/contrast", json=body)
    assert response.status_code == 200
    assert response.json()["results"][0]["foreground"].startswith("#")


def test_unknown_colour_is_a_400_not_a_500() -> None:
    """A bad input is the caller's fault and must say so."""
    body = {"pairs": [{"foreground": "chartreuse-ish", "background": "#fff"}]}
    assert client.post("/v1/contrast", json=body).status_code == 400


def test_red_and_green_collide_under_deuteranopia() -> None:
    """
    The simulation must actually simulate something.

    Red and green are the canonical unsafe pair; if the matrices were
    identity, this test would fail — which is the point of asserting on a
    *collision* rather than on exact hex values.
    """
    body = {"colors": ["#e74c3c", "#2ecc71"], "kinds": ["deuteranopia"]}
    red, green = client.post("/v1/cvd", json=body).json()["results"]

    def rgb(h: str) -> tuple[int, int, int]:
        return tuple(int(h[i : i + 2], 16) for i in (1, 3, 5))

    before = sum(abs(a - b) for a, b in zip(rgb("#e74c3c"), rgb("#2ecc71")))
    after = sum(
        abs(a - b)
        for a, b in zip(rgb(red["simulated"]["deuteranopia"]), rgb(green["simulated"]["deuteranopia"]))
    )
    assert after < before / 2, f"red/green should converge: {before} -> {after}"


def test_adjust_moves_in_the_asked_direction() -> None:
    """Negative darkens, positive lightens."""
    darker = client.post(
        "/v1/adjust", json={"colors": ["#2563eb"], "amount": -0.2}
    ).json()["results"][0]["adjusted"]
    lighter = client.post(
        "/v1/adjust", json={"colors": ["#2563eb"], "amount": 0.2}
    ).json()["results"][0]["adjusted"]
    luminance = lambda h: sum(int(h[i : i + 2], 16) for i in (1, 3, 5))  # noqa: E731
    assert luminance(darker) < luminance("#2563eb") < luminance(lighter)


def test_openapi_names_every_tool() -> None:
    """
    Each route carries an operation_id, because that *is* the MCP tool name.

    A route without one gets an auto-generated name derived from the path,
    which changes whenever the path does — silently renaming an agent's tool.
    """
    paths = client.get("/openapi.json").json()["paths"]
    for path, methods in paths.items():
        for verb, spec in methods.items():
            assert "operationId" in spec, f"{verb.upper()} {path} has no operation_id"


def test_mcp_mounts_and_publishes_the_tools() -> None:
    """The MCP endpoint exists and carries the expected tool names."""
    pytest.importorskip("fastapi_mcp")
    from sprezzature_colors.mcp import mcp

    assert mcp is not None
    mounted = {getattr(r, "path", "") for r in app.routes}
    assert any(p.startswith("/mcp") for p in mounted), sorted(mounted)

    names = {t.name for t in mcp.tools}
    for expected in ("check_contrast", "simulate_color_blindness", "get_palette"):
        assert expected in names, f"{expected} missing from {sorted(names)}"
