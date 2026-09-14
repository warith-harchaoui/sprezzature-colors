"""
Tests for sprezzature_colors and its core scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Scripts use sys.path insertions at import time; mirror that for tests.
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_package_imports() -> None:
    """sprezzature_colors package should be importable with correct metadata."""
    import sprezzature_colors

    # The version itself is checked against pyproject.toml and the
    # CHANGELOG in test_release_consistency.py. Asserting the literal
    # here only made the next release a red build.
    assert sprezzature_colors.__version__
    assert sprezzature_colors.__author__ == "Warith HARCHAOUI"


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


def test_academic_palette_matches_apple_keys() -> None:
    """academic_palette() must expose the same base names as apple_palette()."""
    from _colors import academic_palette, apple_palette

    assert set(academic_palette().keys()) == set(apple_palette().keys())
    assert academic_palette()["Blue"] == "#0072B2"


def test_academic_palette_rows_shape() -> None:
    """academic_palette_rows() rows must carry Base/Hexcode/LightHex like load_palette()."""
    from _colors import academic_palette_rows

    rows = academic_palette_rows()
    assert len(rows) == 8
    for row in rows:
        assert set(row.keys()) == {"Base", "Hexcode", "LightHex"}
        assert row["Hexcode"].startswith("#")
        assert row["LightHex"].startswith("#")


def test_palette_to_tailwind_theme_flag() -> None:
    """--theme academic must emit Okabe-Ito hexes; default stays corporate."""
    import contextlib
    import io

    from palette_to_tailwind import main as ptt_main

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert ptt_main(["--theme", "academic"]) == 0
    assert "#0072B2" in out.getvalue()
    assert "#007AFF" not in out.getvalue()


# ── Color class ──────────────────────────────────────────────────────────────

def test_color_from_hex_and_tuple_agree() -> None:
    """Color built from a hex string and from an equivalent RGB tuple must match."""
    from _colors import Color

    a = Color("#007AFF")
    b = Color((0, 122, 255))
    assert a == b
    assert a.rgb == (0, 122, 255)
    assert a.hex == "#007AFF"


def test_color_from_name() -> None:
    """Color.from_name looks up the curated palette (case-insensitive)."""
    from _colors import Color

    assert Color.from_name("Red").hex == "#FF3B30"
    assert Color.from_name("red").hex == "#FF3B30"
    with pytest.raises(KeyError):
        Color.from_name("Not-A-Color")


def test_color_invalid_rgb_raises() -> None:
    """Out-of-range channel values must raise ValueError, not silently clamp."""
    from _colors import Color

    with pytest.raises(ValueError):
        Color((256, 0, 0))
    with pytest.raises(ValueError):
        Color((0, -1, 0))


def test_color_lighten_darken_return_color_instances() -> None:
    """Color.lighten/darken return new Color objects with L shifted the right way."""
    from _colors import Color

    base = Color("#007AFF")
    lighter = base.lighten(0.15)
    darker = base.darken(0.15)
    assert isinstance(lighter, Color)
    assert isinstance(darker, Color)
    assert lighter.oklch[0] > base.oklch[0]
    assert darker.oklch[0] < base.oklch[0]
    # Original is untouched (immutability).
    assert base.hex == "#007AFF"


def test_color_contrast_with_and_meets_wcag() -> None:
    """Color.contrast_with / meets_wcag must accept Color, hex, and tuple partners."""
    from _colors import Color

    black = Color("#000000")
    white = Color("#FFFFFF")
    assert abs(black.contrast_with(white) - 21.0) < 0.01
    assert black.contrast_with("#FFFFFF") == black.contrast_with(white)
    assert black.contrast_with((255, 255, 255)) == black.contrast_with(white)
    assert black.meets_wcag(white, level="AAA", size="normal")
    assert not white.meets_wcag(white, level="AA", size="normal")


def test_color_repr_eq_hash() -> None:
    """__repr__, __eq__, __hash__ round-trip sensibly."""
    from _colors import Color

    c1 = Color("#007AFF")
    c2 = Color("#007AFF")
    c3 = Color("#FF3B30")
    assert repr(c1) == "Color('#007AFF')"
    assert c1 == c2
    assert c1 != c3
    assert c1 != "#007AFF"  # not a Color instance
    assert hash(c1) == hash(c2)
    assert {c1, c2, c3} == {c1, c3}  # dedupes equal colors in a set


def test_color_linear_and_oklch_properties() -> None:
    """linear and oklch properties must be internally consistent for white/black."""
    from _colors import Color

    white = Color("#FFFFFF")
    black = Color("#000000")
    assert all(abs(v - 1.0) < 1e-6 for v in white.linear)
    assert all(v == 0.0 for v in black.linear)
    l_white, _, _ = white.oklch
    l_black, _, _ = black.oklch
    assert l_white > l_black


# ── Alpha-aware helpers ────────────────────────────────────────────────────

def test_parse_hex_rgba_variants() -> None:
    """3/4/6/8-digit hex must parse to the right (R, G, B, A) shape."""
    from _colors import parse_hex_rgba

    assert parse_hex_rgba("#FFF") == (255, 255, 255, 1.0)
    assert parse_hex_rgba("#000000") == (0, 0, 0, 1.0)
    r, g, b, a = parse_hex_rgba("#00000080")
    assert (r, g, b) == (0, 0, 0)
    assert abs(a - 128 / 255.0) < 1e-6
    with pytest.raises(ValueError):
        parse_hex_rgba("#12345")  # 5 hex digits is not a valid shape


def test_composite_over_opaque_and_half_alpha() -> None:
    """compositing at alpha=1 returns the fg unchanged; alpha=0.5 is the midpoint."""
    from _colors import composite_over

    assert composite_over((10, 20, 30, 1.0), (0, 0, 0)) == (10, 20, 30)
    assert composite_over((255, 255, 255, 0.5), (0, 0, 0)) == (128, 128, 128)


def test_flatten_alpha_hex_and_tuple() -> None:
    """flatten_alpha must composite translucent hex/tuple input over the given bg."""
    from _colors import flatten_alpha

    # Half-white over black background -> mid gray.
    assert flatten_alpha("#FFFFFF80", "#000000") == (128, 128, 128)
    # Opaque input passes through unchanged regardless of bg.
    assert flatten_alpha("#FF3B30", "#000000") == (255, 59, 48)
    # Tuple form with explicit alpha behaves the same as the hex form.
    assert flatten_alpha((255, 255, 255, 0.5), "#000000") == (128, 128, 128)


def test_contrast_ratio_hex_alpha_aware() -> None:
    """A translucent foreground must be judged post-composite, not pre-composite."""
    from _colors import contrast_ratio_hex

    # Fully transparent black "foreground" over white bg is indistinguishable
    # from white-on-white: contrast collapses to 1.0, not black-on-white's 21.
    ratio_transparent = contrast_ratio_hex("#00000000", "#FFFFFF")
    assert abs(ratio_transparent - 1.0) < 0.05
    # Fully opaque black over white is still the WCAG max.
    ratio_opaque = contrast_ratio_hex("#000000FF", "#FFFFFF")
    assert abs(ratio_opaque - 21.0) < 0.01


def test_meets_wcag_alpha_aware_translucent_label() -> None:
    """meets_wcag must flatten a translucent label color before judging it."""
    from _colors import meets_wcag

    # Apple's translucent secondary label (60% black) on white should fail AA
    # normal text -- it never reaches full black's contrast.
    assert not meets_wcag("#3C3C434D", "#FFFFFF", level="AA", size="normal")


# ── Semantic palette accessors ─────────────────────────────────────────────

def test_palette_names_includes_known_bases() -> None:
    """palette_names() must include both saturated hues and neutrals."""
    from _colors import palette_names

    names = palette_names()
    for expected in ("Red", "Blue", "Black", "White", "Gray"):
        assert expected in names


def test_name_to_hex_and_rgb_case_insensitive() -> None:
    """name_to_hex/name_to_rgb resolve case-insensitively and raise on unknown names."""
    from _colors import name_to_hex, name_to_rgb

    assert name_to_hex("Blue") == "#007AFF"
    assert name_to_hex("BLUE") == "#007AFF"
    assert name_to_rgb("Blue") == (0, 122, 255)
    with pytest.raises(KeyError):
        name_to_hex("Chartreuse")


def test_light_variant_by_name_and_hex() -> None:
    """light_variant resolves via base name or hex and returns the curated LightHex."""
    from _colors import light_variant

    assert light_variant("Red") == "#FFD8D6"
    assert light_variant("#FF3B30") == "#FFD8D6"
    assert light_variant("#123456") is None  # not in the palette


def test_emotions_and_emotion_to_hex() -> None:
    """emotions() maps every named emotion to its hex; emotion_to_hex is case-insensitive."""
    from _colors import emotion_to_hex, emotions

    table = emotions()
    assert table["Anger"] == "#FF3B30"
    assert emotion_to_hex("anger") == "#FF3B30"
    with pytest.raises(KeyError):
        emotion_to_hex("Ennui")


def test_concepts_and_concept_search() -> None:
    """concept_search finds the hex(es) tagged with a given concept keyword."""
    from _colors import concept_search, concepts

    assert len(concepts()) > 0
    matches = concept_search("Bold")
    assert "#FF3B30" in matches
    assert concept_search("NoSuchConcept") == []


def test_psychology_for_by_name_and_hex() -> None:
    """psychology_for returns positive/negative associations, or None if unknown."""
    from _colors import psychology_for

    result = psychology_for("Red")
    assert result is not None
    assert "Danger" in result["negative"]
    assert "Power" in result["positive"]
    assert psychology_for("#FF3B30") == result
    assert psychology_for("Not-A-Color") is None


# ── apply_level (accessibility_levels.py) ──────────────────────────────────

def test_apply_level_universal_is_identity() -> None:
    """The 'universal' level must return the palette unchanged (same dict values)."""
    from accessibility_levels import apply_level

    pal = {"Blue": "#007AFF", "Green": "#34C759"}
    out = apply_level(pal, "universal")
    assert out == pal
    assert out is not pal  # a copy, not the same object


def test_apply_level_unknown_raises() -> None:
    """An unsupported level name must raise ValueError, not fail silently."""
    from accessibility_levels import apply_level

    with pytest.raises(ValueError):
        apply_level({"Blue": "#007AFF"}, "not-a-level")


def test_apply_level_high_contrast_clears_aaa() -> None:
    """Every color under 'high-contrast' must clear WCAG AAA (7:1) against bg."""
    from _colors import contrast_ratio_hex
    from accessibility_levels import apply_level

    pal = {"Yellow": "#FFCC00", "Turquoise": "#79DBDC", "Blue": "#007AFF"}
    out = apply_level(pal, "high-contrast", bg="#FFFFFF")
    assert set(out) == set(pal)
    for hexv in out.values():
        assert contrast_ratio_hex(hexv, "#FFFFFF") >= 7.0 - 0.05


def test_apply_level_monochrome_is_grayscale_and_separable() -> None:
    """Monochrome must strip all chroma and keep categories distinguishable by L."""
    from _colors import linear_to_oklab, oklab_to_oklch, parse_hex_linear
    from accessibility_levels import apply_level

    pal = {"Red": "#FF3B30", "Green": "#28CD41", "Blue": "#007AFF"}
    out = apply_level(pal, "monochrome", bg="#FFFFFF")
    assert set(out) == set(pal)
    lightnesses = []
    for hexv in out.values():
        _, c, _ = oklab_to_oklch(linear_to_oklab(parse_hex_linear(hexv)))
        assert c < 1e-6  # chroma stripped -> a true gray
        L, _, _ = oklab_to_oklch(linear_to_oklab(parse_hex_linear(hexv)))
        lightnesses.append(L)
    # Three distinct categories must land at three distinct lightness ranks.
    assert len(set(round(v, 3) for v in lightnesses)) == 3


def test_apply_level_cvd_levels_keep_keys_and_hue() -> None:
    """Each CVD level must return the same keys and roughly preserve hue.

    The OKLCH L move is exact in OKLCH space, but re-encoding to 8-bit sRGB
    clips out-of-gamut channels, which can drag the realized hue a handful
    of degrees off the original for deeply saturated colors pushed toward
    the lightness extremes (measured up to ~7 degrees for pure blue here).
    That is a known consequence of simple per-channel gamut clipping, not a
    level-policy bug, so the tolerance is generous rather than exact.
    """
    from _colors import linear_to_oklab, oklab_to_oklch, parse_hex_linear
    from accessibility_levels import apply_level

    pal = {"Red": "#FF3B30", "Green": "#28CD41", "Blue": "#007AFF"}
    for level in ("deuteranopia", "protanopia", "tritanopia"):
        out = apply_level(pal, level, bg="#FFFFFF")
        assert set(out) == set(pal)
        for name, hexv in out.items():
            _, orig_c, orig_h = oklab_to_oklch(linear_to_oklab(parse_hex_linear(pal[name])))
            _, new_c, new_h = oklab_to_oklch(linear_to_oklab(parse_hex_linear(hexv)))
            assert abs(new_h - orig_h) < 10.0 or orig_c < 1e-6


# ── Palette data quality ─────────────────────────────────────────────────────

def test_every_light_hex_is_a_pale_wash() -> None:
    """Every curated LightHex must be a low-chroma pastel, like its siblings.

    Regression test: ``Turquoise``'s LightHex once shipped as ``#00FFEF``, a
    saturated neon cyan (OKLCH chroma ~0.157) rather than a pale wash like
    every other row (chroma ~0.03-0.05) — a data-entry mistake that would
    have flowed straight into ``palette_to_tailwind.py``'s ``light`` token.
    This guards against a repeat for any row, not just Turquoise.
    """
    from _colors import linear_to_oklab, load_palette, oklab_to_oklch, parse_hex_linear

    for row in load_palette():
        light = row.get("LightHex", "").strip()
        if not light:
            continue
        _, chroma, _ = oklab_to_oklch(linear_to_oklab(parse_hex_linear(light)))
        assert chroma < 0.08, f"{row['Base']}'s LightHex {light} is not a pale wash (chroma={chroma:.3f})"


# ── accessibility_levels.py CLI ──────────────────────────────────────────────

def test_accessibility_levels_csv_default_resolves_to_a_real_file() -> None:
    """The ``--csv`` default must exist, in a source checkout or an install.

    Regression test: this used to hardcode ``Path(__file__).parent.parent /
    "references" / "palette.csv"``, which only resolves in a source
    checkout. Once installed, the CSV ships as the sibling package
    ``sprezzature_colors_references/palette.csv`` and that hardcoded path
    does not exist, so ``sprezzature-colors-levels`` crashed with
    ``FileNotFoundError`` for anyone who ran it after a plain ``pip
    install`` (confirmed with a real non-editable install into a fresh
    venv). The fix reuses ``_colors._PALETTE_PATH``, which already resolves
    both layouts.
    """
    from accessibility_levels import _PALETTE_PATH

    assert _PALETTE_PATH.is_file()


def test_accessibility_levels_main_cli(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI entry point must print one line per color at the chosen level."""
    from accessibility_levels import main as levels_main

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-levels", "--level", "monochrome"])
    assert levels_main() == 0
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.strip()]
    assert len(lines) >= 8  # at least the 8 saturated Apple bases
    assert "contrast-vs-white" in lines[0]


# ── audit_contrast.py CLI ────────────────────────────────────────────────────

def test_audit_contrast_main_cli_json(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """``--format json`` must emit valid, well-shaped JSON on stdout."""
    import json

    from audit_contrast import main as audit_main

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-contrast", "--format", "json", "--fix"])
    audit_main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["target"] == 4.5
    assert len(payload["pairs"]) > 0
    assert all({"fg", "bg", "ratio", "passes"} <= set(p) for p in payload["pairs"])


def test_audit_contrast_main_cli_exit_code_reflects_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exit code must be 0 when every pair passes, 1 when at least one fails."""
    from audit_contrast import main as audit_main

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-contrast", "--target", "1.0"])
    assert audit_main() == 0  # trivial target: every pair passes

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-contrast", "--target", "21.0"])
    assert audit_main() == 1  # impossible target: every pair fails


def test_audit_contrast_main_cli_all_pairs_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """``--all-pairs`` must check strictly more pairs than the themed default."""
    import contextlib
    import io
    import json

    from audit_contrast import main as audit_main

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-contrast", "--format", "json"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        audit_main()
    default_pairs = len(json.loads(out.getvalue())["pairs"])

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-contrast", "--format", "json", "--all-pairs"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        audit_main()
    all_pairs = len(json.loads(out.getvalue())["pairs"])

    assert all_pairs > default_pairs


# ── simulate_cvd.py ──────────────────────────────────────────────────────────

@pytest.fixture
def sample_image():
    """A tiny 4x4 RGB image with a handful of distinct colors, for CVD tests."""
    from PIL import Image

    im = Image.new("RGB", (4, 4), (255, 0, 0))
    px = im.load()
    px[1, 1] = (0, 255, 0)
    px[2, 2] = (0, 0, 255)
    px[3, 3] = (255, 255, 255)
    return im


def test_simulate_image_changes_saturated_colors(sample_image) -> None:
    """Applying a CVD matrix must change at least some pixels of a colorful image."""
    from simulate_cvd import simulate_image

    out = simulate_image(sample_image, "deuteranopia")
    assert out.size == sample_image.size
    assert list(out.getdata()) != list(sample_image.getdata())


def test_grayscale_image_strips_all_chroma() -> None:
    """Every output pixel of grayscale_image must have R == G == B."""
    from PIL import Image
    from simulate_cvd import grayscale_image

    im = Image.new("RGB", (2, 2))
    im.putpixel((0, 0), (255, 0, 0))
    im.putpixel((1, 0), (0, 255, 0))
    im.putpixel((0, 1), (0, 0, 255))
    im.putpixel((1, 1), (128, 64, 200))
    out = grayscale_image(im)
    for r, g, b in out.getdata():
        assert r == g == b


def test_parse_types_shorthands_and_default() -> None:
    """parse_types must expand shorthands and default to all three kinds."""
    from simulate_cvd import parse_types

    assert parse_types("prot,deut") == ["protanopia", "deuteranopia"]
    assert set(parse_types("")) == {"protanopia", "deuteranopia", "tritanopia"}
    with pytest.raises(Exception):  # argparse.ArgumentTypeError
        parse_types("not-a-type")


def test_make_grid_layout_matches_cell_count() -> None:
    """make_grid must size the mosaic canvas to the number of cells supplied."""
    from PIL import Image
    from simulate_cvd import make_grid

    original = Image.new("RGB", (10, 10), (200, 200, 200))
    simulated = {"protanopia": Image.new("RGB", (10, 10), (50, 50, 50))}
    grid = make_grid(original, simulated)
    # 2 cells -> 1x2 grid -> canvas is 2 cells wide, 1 cell tall.
    assert grid.size == (20, 10)


def test_simulate_cvd_main_cli_writes_sibling_files(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI must write one sibling PNG per requested CVD type."""
    from PIL import Image
    from simulate_cvd import main as cvd_main

    src = tmp_path / "hero.png"
    Image.new("RGB", (3, 3), (10, 200, 30)).save(src)

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-cvd", str(src), "--types", "prot,deut"])
    assert cvd_main() == 0
    assert (tmp_path / "hero-protanopia.png").is_file()
    assert (tmp_path / "hero-deuteranopia.png").is_file()
    assert not (tmp_path / "hero-tritanopia.png").is_file()


def test_simulate_cvd_main_cli_grid_and_grayscale(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``--grid --grayscale`` must write a single mosaic file that includes a grayscale panel."""
    from PIL import Image
    from simulate_cvd import main as cvd_main

    src = tmp_path / "hero.png"
    Image.new("RGB", (3, 3), (10, 200, 30)).save(src)
    out = tmp_path / "grid.png"

    monkeypatch.setattr(
        "sys.argv",
        ["sprezzature-colors-cvd", str(src), "--grid", "--grayscale", "--out", str(out)],
    )
    assert cvd_main() == 0
    assert out.is_file()
    with Image.open(out) as im:
        # 1 original + 3 CVD types + 1 grayscale = 5 cells -> 2 cols x 3 rows.
        assert im.size == (6, 9)


def test_simulate_cvd_main_cli_missing_source_returns_1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Opening a nonexistent source image must fail cleanly with exit code 1."""
    from simulate_cvd import main as cvd_main

    monkeypatch.setattr("sys.argv", ["sprezzature-colors-cvd", "/no/such/file.png"])
    assert cvd_main() == 1
