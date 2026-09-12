"""
sprezzature_colors: color accessibility and palette tooling.

Three checks a design should pass before it ships: enough contrast between
text and its background (an audit against the WCAG standard, short for the
Web Content Accessibility Guidelines, the reference rules for accessible
web content), a design that still reads correctly for a color-blind viewer
(color vision deficiency simulation), and one shared source of brand
colors instead of every project hand-copying hex codes (Tailwind CSS
palette export).

Four ways in, one implementation
--------------------------------
Everything below is re-exported from ``sprezzature_colors_scripts._colors``,
which stays the single real implementation. Nothing here is a second copy;
this module exists so the library reads like a library:

``import sprezzature_colors as sc``
    The functions, directly. This module.
``sprezzature-colors-contrast`` and friends
    The command lines, one per tool.
``sprezzature_colors.api``
    The same tools over HTTP. Needs the ``[api]`` extra.
``sprezzature_colors.mcp``
    The same HTTP routes as MCP tools, for an AI assistant. ``[mcp]``.

Usage example
-------------
>>> import sprezzature_colors as sc
>>> round(sc.contrast_ratio_hex("#000000", "#ffffff"), 1)
21.0
>>> sc.meets_wcag("#595959", "#ffffff")
True
>>> sc.darken("#2563eb", 0.2)[:1]
'#'

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""
from __future__ import annotations

from sprezzature_colors_scripts._colors import (
    CVD_LABELS,
    CVD_MATRICES,
    CVD_SHORTHAND,
    academic_palette,
    academic_palette_rows,
    apple_palette,
    composite_over,
    concept_search,
    concepts,
    contrast_ratio,
    contrast_ratio_hex,
    darken,
    emotion_to_hex,
    emotions,
    flatten_alpha,
    light_variant,
    lighten,
    linear_to_oklab,
    linear_to_srgb,
    load_palette,
    meets_wcag,
    name_to_hex,
    name_to_rgb,
    oklab_to_linear,
    oklab_to_oklch,
    oklch_to_oklab,
    palette_names,
    parse_hex,
    parse_hex_linear,
    parse_hex_rgba,
    psychology_for,
    relative_luminance,
    rgb_to_hex,
    simulate_pixel,
    srgb_to_linear,
    to_hex,
)

__version__ = "1.0.0"
__author__ = "Warith HARCHAOUI"
__email__ = "warith.harchaoui@gmail.com"

#: The public surface, grouped the way the documentation presents it:
#: contrast and WCAG, color spaces, palette lookup, and color psychology.
__all__ = [
    # contrast and WCAG
    "contrast_ratio",
    "contrast_ratio_hex",
    "meets_wcag",
    "relative_luminance",
    # parsing, compositing, and hex
    "parse_hex",
    "parse_hex_linear",
    "parse_hex_rgba",
    "composite_over",
    "flatten_alpha",
    "rgb_to_hex",
    "to_hex",
    "srgb_to_linear",
    "linear_to_srgb",
    # perceptual color spaces
    "linear_to_oklab",
    "oklab_to_linear",
    "oklab_to_oklch",
    "oklch_to_oklab",
    "lighten",
    "darken",
    # palettes
    "load_palette",
    "palette_names",
    "name_to_hex",
    "name_to_rgb",
    "light_variant",
    "apple_palette",
    "academic_palette",
    "academic_palette_rows",
    # color vision deficiency
    "simulate_pixel",
    "CVD_MATRICES",
    "CVD_LABELS",
    "CVD_SHORTHAND",
    # color psychology
    "emotions",
    "emotion_to_hex",
    "concepts",
    "concept_search",
    "psychology_for",
    # metadata
    "__version__",
]
