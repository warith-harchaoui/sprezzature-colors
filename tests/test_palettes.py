"""
The three palettes of https://deraison.ai/colors, as this package ships them.

The site is the source of truth for every colour in the suite. These tests
check that the copies agree with one another; whether they agree with the site
is ``scripts/sync_palettes.py``'s job, run when the site changes.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

THEMES = ("corporate", "academic", "print")
NAMES = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Turquoise",
    "Blue",
    "Purple",
    "Pink",
    "Brown",
    "Black",
    "Gray",
]


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.parametrize("theme", THEMES)
def test_each_palette_has_the_eleven_names_in_order(theme: str) -> None:
    """Same eleven names, same order, in every palette; no white since 2026-11-13."""
    rows = _rows(REPO / "references" / f"palette-{theme}.csv")
    assert [r["Name"] for r in rows] == NAMES
    for r in rows:
        assert r["Hexcode"].startswith("#") and len(r["Hexcode"]) == 7
        assert r["LightHex"].startswith("#") and len(r["LightHex"]) == 7


def test_palette_csv_is_derived_from_the_corporate_csv() -> None:
    """palette.csv is what sync_palettes makes of palette-corporate.csv, nothing else."""
    from sync_palettes import derive_palette_csv

    corporate = (REPO / "references" / "palette-corporate.csv").read_text(encoding="utf-8")
    assert (REPO / "references" / "palette.csv").read_text(encoding="utf-8") == derive_palette_csv(
        corporate
    )


@pytest.mark.parametrize("name", ["palette.csv"] + [f"palette-{t}.csv" for t in THEMES])
def test_skill_copy_matches_references(name: str) -> None:
    """The skill an agent reads carries the same palettes as the package."""
    skill = REPO / "sprezzature_colors" / "skill" / "references" / name
    assert skill.read_bytes() == (REPO / "references" / name).read_bytes()


def test_palettes_ship_in_the_wheel() -> None:
    """Every palette CSV is declared as package data, or pip installs none of them."""
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    for name in ["palette.csv"] + [f"palette-{t}.csv" for t in THEMES]:
        assert f'"{name}"' in text


def test_default_audit_palette_follows_the_corporate_palette() -> None:
    """The audit's built-in brand tokens carry the corporate hex and light tint."""
    from _colors import theme_rows
    from audit_contrast import DEFAULT_PALETTE

    rows = {r["Name"].lower(): r for r in theme_rows("corporate")}
    brands = {
        k.removeprefix("brand-"): v for k, v in DEFAULT_PALETTE.items() if k.startswith("brand-")
    }
    assert brands
    for name, token in brands.items():
        assert token["DEFAULT"] == rows[name]["Hexcode"]
        assert token["light"] == rows[name]["LightHex"]


@pytest.mark.parametrize("theme", THEMES)
def test_theme_palette_has_the_eight_hues(theme: str) -> None:
    """theme_palette() returns the eight hues, all distinct (pink no longer borrows purple)."""
    from _colors import SATURATED, theme_palette

    pal = theme_palette(theme)
    assert list(pal) == list(SATURATED)
    assert len(set(pal.values())) == 8


def test_unknown_theme_raises() -> None:
    from _colors import theme_rows

    with pytest.raises(ValueError):
        theme_rows("pastel")


@pytest.mark.parametrize("target", [3.0, 4.5, 7.0])
def test_every_fix_suggestion_meets_its_target_as_a_hex(target: float) -> None:
    """A suggested hex is measured as shipped: rounded to 8 bits, inside sRGB.

    The search used to judge the unrounded, possibly out-of-gamut colour, and
    offered #C30000 at 7.10 for a red that measures 6.33.
    """
    from _colors import contrast_ratio_hex, parse_hex_linear
    from audit_contrast import DEFAULT_PALETTE, adjust_for_contrast, normalize_palette

    flat = normalize_palette(DEFAULT_PALETTE)
    for fg in flat.values():
        for bg in ("#FFFFFF", "#000000", "#F2F2F7", "#1C1C1E"):
            if len(fg) != 7:
                continue
            found = adjust_for_contrast(parse_hex_linear(fg), parse_hex_linear(bg), target)
            if found is None:
                continue
            hexv, ratio = found
            assert contrast_ratio_hex(hexv, bg) >= target, (fg, bg, hexv)
            assert abs(contrast_ratio_hex(hexv, bg) - ratio) < 1e-9
