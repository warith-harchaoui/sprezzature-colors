#!/usr/bin/env python3
"""
The catalogue of tools this package ships, and the one sentence said about a
missing extra.

Lifted out of the command line on 2026-10-25, when the argparse front door was
removed and click became the only one. It lives here rather than in ``cli`` so
that the catalogue owes nothing to whichever parser happens to read it — the
previous arrangement had the click module importing ``TOOLS`` from the argparse
module, which is why neither could be deleted without the other.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

#: Tool name -> (module under sprezzature_colors_scripts, extra, summary).
#:
#: A tool missing from this table is unreachable, or reachable and
#: undocumented.
#:
#: ``extra`` is the empty string for the three tools that need nothing beyond
#: a bare install — which is most of them, and deliberately so. This package
#: declares **no** base dependencies, and the contrast audit is the one most
#: likely to sit in a pre-commit hook, where a colour library is the last
#: thing anybody wants to install.
TOOLS: dict[str, tuple[str, str, str]] = {
    "contrast": (
        "audit_contrast",
        "",
        "Audit a palette against the WCAG contrast ratios (4.5:1 body, 3:1 "
        "large and UI, 7:1 AAA) and propose the nearest accessible "
        "alternative for every failing pair. Standard library only.",
    ),
    "cvd": (
        "simulate_cvd",
        "cvd",
        "Render an image as a colour-blind viewer sees it — protanopia, "
        "deuteranopia, tritanopia — so a reviewer can look rather than "
        "guess. Needs Pillow.",
    ),
    "levels": (
        "accessibility_levels",
        "",
        "Print the canonical palette at one accessibility level, keeping "
        "every colour's name so a consumer asking for 'Blue' still gets one.",
    ),
    "palette-to-tailwind": (
        "palette_to_tailwind",
        "",
        "Emit the palette as a Tailwind config snippet, so a consuming "
        "project generates its tokens instead of copy-pasting them.",
    ),
}


def missing_extra_message(tool: str, extra: str, exc: Exception) -> str:
    """What to say when a tool's dependency is not installed.

    One sentence in one place: the command line and anything else that has
    to explain a missing extra say it the same way.
    """
    if extra:
        return (
            f"{tool}: its dependencies are an optional extra, so a bare "
            f"install stays small. Add them with:\n"
            f"    pip install 'sprezzature-colors[{extra}]'\n"
            f"  ({exc})\n"
        )
    return (
        f"{tool}: needs nothing optional, so this is not a missing extra — "
        f"something else failed to import.\n  ({exc})\n"
    )
