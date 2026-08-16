"""
sprezzature_colors: color accessibility and palette tooling.

Three checks a design should pass before it ships: enough contrast between
text and its background (an audit against the WCAG standard, short for the
Web Content Accessibility Guidelines, the reference rules for accessible
web content), a design that still reads correctly for a color-blind viewer
(color vision deficiency simulation), and one shared source of brand
colors instead of every project hand-copying hex codes (Tailwind CSS
palette export). This top-level package is what `pip install
sprezzature-colors` provides; the command-line tools themselves live one
level down, in the sibling `sprezzature_colors_scripts` package.

Author
------
Warith Harchaoui <warith.harchaoui@gmail.com>
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Warith Harchaoui"
__email__ = "warith.harchaoui@gmail.com"
