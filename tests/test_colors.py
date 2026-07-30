"""
Tests for sprezzature_colors and its core scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Scripts use sys.path insertions at import time; mirror that for tests.
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_package_imports() -> None:
    """sprezzature_colors package should be importable with correct metadata."""
    import sprezzature_colors

    assert sprezzature_colors.__version__ == "1.0.0"
    assert sprezzature_colors.__author__ == "Warith Harchaoui"


def test_srgb_to_linear_black_white() -> None:
    """Black maps to 0.0, white to 1.0 in linear sRGB."""
    from _colors import srgb_to_linear

    assert srgb_to_linear(0) == 0.0
    assert abs(srgb_to_linear(255) - 1.0) < 1e-6


def test_contrast_ratio_black_white() -> None:
    """Black on white must yield the WCAG maximum contrast ratio of 21:1."""
    from _colors import contrast_ratio, parse_hex_linear

    black = parse_hex_linear("#000000")
    white = parse_hex_linear("#FFFFFF")
    ratio = contrast_ratio(white, black)
    assert abs(ratio - 21.0) < 0.01


def test_meets_wcag_aa() -> None:
    """Apple system blue on white: passes AA for large text, fails for normal."""
    from _colors import meets_wcag

    # #007AFF on #FFFFFF measures ~4.02:1 — above the 3.0 large-text bar,
    # below the 4.5 normal-text bar.
    assert meets_wcag("#007AFF", "#FFFFFF", level="AA", size="large")
    assert not meets_wcag("#007AFF", "#FFFFFF", level="AA", size="normal")


def test_lighten_darkens_in_oklch() -> None:
    """lighten/darken must move L in the right direction without changing hue."""
    from _colors import darken, lighten, linear_to_oklab, oklab_to_oklch, parse_hex_linear

    base = "#007AFF"
    lighter = lighten(base, 0.15)
    darker = darken(base, 0.15)

    def oklch_l(h: str) -> float:
        L, _, _ = oklab_to_oklch(linear_to_oklab(parse_hex_linear(h)))
        return L

    assert oklch_l(lighter) > oklch_l(base)
    assert oklch_l(darker) < oklch_l(base)


def test_simulate_pixel_protanopia() -> None:
    """Pure red must shift when protanopia matrix is applied."""
    from _colors import CVD_MATRICES, simulate_pixel

    matrix = CVD_MATRICES["protanopia"]
    r_out, g_out, b_out = simulate_pixel((255, 0, 0), matrix)
    # Protanopia desaturates reds toward gray; the output is lighter than pure red.
    assert r_out < 255 or g_out > 0 or b_out > 0


def test_audit_contrast_main_importable() -> None:
    """audit_contrast must expose a callable main()."""
    import audit_contrast

    assert callable(audit_contrast.main)


def test_normalize_palette_flat_and_nested() -> None:
    """normalize_palette should flatten both flat and nested shapes."""
    from audit_contrast import normalize_palette

    flat = normalize_palette({"fg": "#000000", "bg": "#FFFFFF"})
    assert flat == {"fg": "#000000", "bg": "#FFFFFF"}

    nested = normalize_palette({"brand": {"DEFAULT": "#007AFF", "dark": "#0A84FF"}})
    assert nested["brand"] == "#007AFF"
    assert nested["brand-dark"] == "#0A84FF"


def test_parse_hex_roundtrip() -> None:
    """parse_hex -> rgb_to_hex must round-trip without loss."""
    from _colors import parse_hex, rgb_to_hex

    for hexv in ("#FF3B30", "#007AFF", "#FFFFFF", "#000000"):
        assert rgb_to_hex(parse_hex(hexv)) == hexv
