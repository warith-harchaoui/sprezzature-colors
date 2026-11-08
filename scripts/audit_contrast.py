#!/usr/bin/env python3
"""
audit_contrast
==============

Audit a palette's foreground / background contrast against the WCAG
(Web Content Accessibility Guidelines) ratio thresholds: 4.5:1 for body
text, 3:1 for large text and UI, 7:1 for the stricter AAA level. The
ratio is a single number from 1 (identical brightness, unreadable) to
21 (pure black on pure white); the higher it is, the easier two colors
are to tell apart. For failing pairs, propose the nearest accessible
alternative by walking the OKLCH lightness axis: OKLCH is a color model
in which moving the lightness number by a fixed step produces a change
the eye perceives as equally large everywhere in the space, so nudging
along it gives a color that looks like "the same hue, just brighter or
darker" rather than a different color entirely.

The script accepts two input shapes:

* A JSON palette: ``{"role": "#RRGGBB", ...}`` or ``{"role": {"DEFAULT": "#…", "dark": "#…"}, ...}``.
* The skill's built-in default palette (when no ``--palette`` is given).

It is **deterministic**: no model, no network, and it uses standard formulas:

* WCAG relative luminance (the 2.4-gamma formula the standard specifies).
* OKLab / OKLCH conversion via Björn Ottosson's published matrices
  (https://bottosson.github.io/posts/oklab/).

Usage
-----
::

    # Audit the skill's built-in palette at WCAG AA (4.5:1)
    python audit_contrast.py

    # AAA threshold
    python audit_contrast.py --target 7

    # External palette + suggested fixes
    python audit_contrast.py --palette my-palette.json --fix

    # JSON output for CI
    python audit_contrast.py --format json

Notes
-----
* Python 3.10+. The arithmetic is standard library only; the command line is click.
* The "fix" search walks the OKLCH L axis at 0.01 resolution; in practice
  the search converges in tens of microseconds per pair.
* Color math (sRGB transfer, WCAG luminance, OKLab / OKLCH) lives in
  ``_colors.py`` next to this script. Both ``audit_contrast`` and
  ``simulate_cvd`` import from it.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _click import run_command, sprezzature_command  # noqa: E402
from _colors import (  # noqa: E402
    contrast_ratio,
    contrast_ratio_hex,
    linear_to_oklab,
    oklab_to_linear,
    oklab_to_oklch,
    oklch_to_oklab,
    parse_hex_linear,
    to_hex,
)
from _colors import (
    relative_luminance as relative_luminance,  # re-exported for tests/consumers
)

# Re-export under the legacy name so external callers / tests that import
# ``parse_hex`` from ``audit_contrast`` keep working. The function returns
# a *linear* sRGB triple (gamma-decoded), as it has always done here.
parse_hex = parse_hex_linear


# ── Skill's built-in palette ────────────────────────────────────────────────

#: Default palette used when ``--palette`` is not supplied. Mirrors the
#: skill's semantic Tailwind tokens.
DEFAULT_PALETTE: dict[str, dict[str, str]] = {
    "brand-blue":      {"DEFAULT": "#007AFF", "dark": "#0A84FF", "light": "#CCE4FF"},
    "brand-red":       {"DEFAULT": "#FF3B30", "dark": "#FF453A", "light": "#FFD8D6"},
    "brand-green":     {"DEFAULT": "#28CD41", "dark": "#30D158", "light": "#D4F5D9"},
    "brand-orange":    {"DEFAULT": "#FF9500", "dark": "#FF9F0A", "light": "#FFEACC"},
    "brand-yellow":    {"DEFAULT": "#FFCC00", "dark": "#FFD60A", "light": "#FFF5CC"},
    "brand-purple":    {"DEFAULT": "#AF52DE", "dark": "#BF5AF2", "light": "#EFDCF8"},
    "brand-pink":      {"DEFAULT": "#FF2D55", "dark": "#FF375F", "light": "#FFD5DD"},
    "brand-turquoise": {"DEFAULT": "#79DBDC", "dark": "#64D2FF", "light": "#C0E7E7"},
    "label-primary":   {"DEFAULT": "#000000", "dark": "#FFFFFF"},
    "label-secondary": {"DEFAULT": "#3C3C434D", "dark": "#EBEBF54D"},
    "surface-primary": {"DEFAULT": "#FFFFFF", "dark": "#000000"},
    "surface-secondary": {"DEFAULT": "#F2F2F7", "dark": "#1C1C1E"},
}


# ── Suggestion search ──────────────────────────────────────────────────────

def adjust_for_contrast(
    fg_linear: tuple[float, float, float],
    bg_linear: tuple[float, float, float],
    target: float,
) -> tuple[str, float] | None:
    """
    Find the nearest accessible alternative to ``fg_linear`` on the
    OKLCH lightness axis (keeping hue and chroma fixed).

    The search walks L from 0 to 1 in 0.01 steps, picks the candidate that
    passes the target *and* is closest to the original L.

    Parameters
    ----------
    fg_linear : tuple of float
        Source foreground in linear sRGB.
    bg_linear : tuple of float
        Background in linear sRGB.
    target : float
        Minimum acceptable contrast ratio.

    Returns
    -------
    tuple of (str, float) or None
        ``(suggested_hex, achieved_ratio)`` or ``None`` if no candidate
        meets the target (very rare — usually means the background itself
        is very close to mid-gray).
    """
    L, C, H = oklab_to_oklch(linear_to_oklab(fg_linear))
    best: tuple[float, tuple[float, float, float]] | None = None
    for i in range(0, 101):
        l_test: float = i / 100.0
        candidate = oklab_to_linear(oklch_to_oklab((l_test, C, H)))
        ratio = contrast_ratio(candidate, bg_linear)
        if ratio >= target:
            distance: float = abs(l_test - L)
            if best is None or distance < best[0]:
                best = (distance, candidate)
    if best is None:
        return None
    return to_hex(best[1]), contrast_ratio(best[1], bg_linear)


# ── Audit logic ─────────────────────────────────────────────────────────────

def normalize_palette(raw: dict) -> dict[str, str]:
    """
    Flatten a nested palette to ``{role: hex}``.

    Accepts both flat (``{"key": "#fff"}``) and nested
    (``{"key": {"DEFAULT": "#fff", "dark": "#000"}}``) shapes.

    Raises
    ------
    TypeError
        When ``raw`` is not a mapping, or when a key the audit would check
        (:func:`is_foreground` / :func:`is_background`) does not hold a string.
        Keys the audit ignores may hold anything: a tokens file has its own
        metadata.
    """
    if not isinstance(raw, dict):
        raise TypeError(f"expected a JSON object of role to colour, got {type(raw).__name__}")

    def checked(key: str, value: object) -> None:
        """Refuse a non-string under a role the audit is going to read."""
        if not isinstance(value, str) and (is_foreground(key) or is_background(key)):
            raise TypeError(f"{key!r} holds {value!r}, not a colour")

    flat: dict[str, str] = {}
    for role, value in raw.items():
        if isinstance(value, str):
            flat[role] = value
        elif isinstance(value, dict):
            for variant, hex_val in value.items():
                key: str = role if variant.upper() == "DEFAULT" else f"{role}-{variant}"
                checked(key, hex_val)
                if isinstance(hex_val, str):
                    flat[key] = hex_val
        else:
            checked(role, value)
    return flat


def is_foreground(role: str) -> bool:
    """Return True when ``role`` is conventionally drawn on top of a surface.

    ``-light`` brand tints are wash backgrounds, never text. ``-dark``
    label variants ARE foregrounds -- they are the dark theme's text
    colours, paired with the dark surfaces by :func:`themes_compatible`.
    """
    return role.startswith(("label-", "brand-")) and not role.endswith("-light")


def is_background(role: str) -> bool:
    """Return True when ``role`` is conventionally a surface colour."""
    return role.startswith("surface-")


def role_theme(role: str) -> str | None:
    """Which theme a role belongs to: ``"dark"``, ``"light"``, or ``None``.

    A ``-dark`` suffix marks the dark theme's variant of a role; its
    unsuffixed sibling is the light theme's. Brand accents carry no
    ``-dark`` sibling and are used in both themes, so they are
    theme-neutral (``None``).
    """
    if role.endswith("-dark"):
        return "dark"
    if role.startswith("brand-"):
        return None
    return "light"


def themes_compatible(fg_role: str, bg_role: str) -> bool:
    """True when the pair can actually co-occur in a rendered theme.

    The light label on the dark surface is never drawn: each theme pairs
    its own labels with its own surfaces. Theme-neutral brand accents
    pair with every surface.
    """
    fg_theme = role_theme(fg_role)
    return fg_theme is None or fg_theme == role_theme(bg_role)


def audit(
    palette: dict[str, str],
    target: float,
    propose_fix: bool,
    all_pairs: bool = False,
) -> dict:
    """
    Audit the palette's (foreground, background) pairs against the target.

    By default only pairs that co-occur in a rendered theme are checked
    (light labels on light surfaces, dark labels on dark surfaces, brand
    accents on everything); ``all_pairs=True`` restores the exhaustive
    cross-product, cross-theme combinations included.

    Returns ``{"target": <target>, "pairs": [...]}`` where each pair entry has
    ``fg``, ``bg``, ``ratio``, ``passes``, and optionally ``suggested``.
    """
    out: list[dict] = []
    for fg_role, fg_hex in palette.items():
        if not is_foreground(fg_role):
            continue
        for bg_role, bg_hex in palette.items():
            if not is_background(bg_role):
                continue
            if not all_pairs and not themes_compatible(fg_role, bg_role):
                continue
            # Alpha-aware: a translucent foreground (#RRGGBBAA) is composited
            # over its background before the ratio, so the audit judges the
            # color as rendered, not the raw un-painted foreground. The opaque
            # linear pair is still needed by the fix search below.
            fg = parse_hex(fg_hex)
            bg = parse_hex(bg_hex)
            ratio = contrast_ratio_hex(fg_hex, bg_hex)
            entry: dict = {
                "fg": {"role": fg_role, "hex": fg_hex.upper()},
                "bg": {"role": bg_role, "hex": bg_hex.upper()},
                "ratio": round(ratio, 2),
                "passes": ratio >= target,
            }
            if not entry["passes"] and propose_fix:
                fix = adjust_for_contrast(fg, bg, target)
                if fix is not None:
                    entry["suggested"] = {"hex": fix[0], "ratio": round(fix[1], 2)}
            out.append(entry)
    return {"target": target, "pairs": out}


# ── CLI entry point ────────────────────────────────────────────────────────

#: Exit code when the palette yields no pair at all: distinct from 0 (every
#: pair passes) and 1 (a pair fails), because nothing was checked.
EXIT_NO_PAIRS: int = 2

@sprezzature_command(
    name="sprezzature-colors-contrast",
    help="Audit a palette's foreground/background contrast against WCAG. "
    "Walks the (label, surface) pairs that co-occur in a rendered "
    "theme (--all-pairs for the full cross-product), suggests the "
    "nearest OKLCH neighbour for failing pairs when --fix is set.",
    epilog="\b\nExamples:\n"
    "  sprezzature-colors-contrast --palette palette.json\n"
    "  sprezzature-colors-contrast --palette palette.json --target 7 --fix\n"
    "  sprezzature-colors-contrast --format json --palette palette.json\n",
)
@click.option(
    "--palette",
    type=click.Path(path_type=Path),
    default=None,
    help="JSON palette. When omitted, the skill's built-in default is used.",
)
@click.option(
    "--target",
    type=float,
    default=4.5,
    help="Minimum acceptable WCAG contrast ratio. 4.5 (AA body), 7 (AAA), or 3 (UI/large).",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Propose a suggested fix for each failing pair (nearest OKLCH neighbour).",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format. Default: text.",
)
@click.option(
    "--all-pairs",
    is_flag=True,
    help="Also check cross-theme pairs (light labels on dark surfaces and "
    "vice versa). Default: only pairs that co-occur in a rendered theme.",
)
def _command(palette: Path | None, target: float, fix: bool, fmt: str, all_pairs: bool) -> int:
    """Run the audit; the exit code is :func:`main`'s."""
    # A value this module cannot read (``rgba(...)``, ``hsl(...)``, a typo), a
    # file that is not JSON, or a file that is not there ended on a raw Python
    # traceback, and a traceback exits 1, which a CI job reads as "a pair
    # failed". All of them are a usage error: say which, and exit 2 like any
    # other.
    try:
        if palette is not None:
            raw = json.loads(palette.read_text(encoding="utf-8"))
        else:
            raw = DEFAULT_PALETTE
        flat = normalize_palette(raw)
        result = audit(flat, target, fix, all_pairs=all_pairs)
    except OSError as exc:
        sys.stderr.write(f"sprezzature-colors-contrast: cannot read the palette: {exc}.\n")
        return EXIT_NO_PAIRS
    except (ValueError, TypeError) as exc:
        sys.stderr.write(
            f"sprezzature-colors-contrast: cannot read the palette: {exc}. "
            "Colours must be hex (#RGB, #RRGGBB or #RRGGBBAA).\n"
        )
        return EXIT_NO_PAIRS

    # No pair checked is not a pass. A palette whose keys match no role
    # (``label-``/``brand-`` against ``surface-``) used to print
    # "0 pass, 0 fail." and exit 0, exactly like a palette that passed.
    if not result["pairs"]:
        sys.stderr.write(
            "sprezzature-colors-contrast: no (foreground, background) pair to check. "
            "Foreground keys must start with 'label-' or 'brand-' and background "
            "keys with 'surface-'; nothing in this palette matched.\n"
        )
        return EXIT_NO_PAIRS

    if fmt == "json":
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(f"Target ratio: {result['target']}")
        print()
        passing = 0
        failing = 0
        for pair in result["pairs"]:
            mark = "✓" if pair["passes"] else "✗"
            print(
                f"  {mark} {pair['fg']['role']:>22}  on  {pair['bg']['role']:>22}"
                f"   ratio {pair['ratio']:.2f}"
            )
            if not pair["passes"]:
                failing += 1
                if "suggested" in pair:
                    print(
                        f"      → suggest {pair['suggested']['hex']}  "
                        f"(ratio {pair['suggested']['ratio']:.2f})"
                    )
            else:
                passing += 1
        print()
        print(f"{passing} pass, {failing} fail.")

    failing_count: int = sum(1 for p in result["pairs"] if not p["passes"])
    return 0 if failing_count == 0 else 1


def main(argv: list[str] | None = None) -> int:
    """Run the audit. Exit 0 when every checked pair passes, 1 when one fails,
    2 when the palette yields no pair to check (or on a usage error)."""
    return run_command(_command, argv)


if __name__ == "__main__":
    sys.exit(main())
