"""
The argparse command line — ``make-colors``.

Four commands shipped, and until this module existed there was no way to find
out what this package does except by reading its README: each tool had its own
console script and nothing listed them together. One front door fixes that
without taking anything away — every tool is still its own command, which is
what a script should call.

The twin :mod:`sprezzature_colors.cli_click` reads the same :data:`TOOLS`
table and shares :func:`_missing_extra_message`, so a tool cannot appear in
one front door and be missing from the other, nor be explained differently by
each.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import importlib
import sys

from sprezzature_colors_scripts._argparse import make_parser

#: ``name -> (module, extra, summary)``, the single catalogue both front doors
#: read. The summary is what ``--help`` prints, so a tool cannot be listed and
#: unreachable, or reachable and undocumented.
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


def build_parser() -> argparse.ArgumentParser:
    """The parser, built separately so a test can read it without running it."""
    width = max(len(name) for name in TOOLS)
    catalogue = "\n".join(
        f"  {name:<{width}}  {summary}" for name, (_, _, summary) in TOOLS.items()
    )
    parser = make_parser(
        prog="make-colors",
        description=(
            "Everything this package does with a palette. One front door over "
            "the four tools it ships; each is also its own command, which is "
            "what a script should call."
        ),
        epilog=(
            f"Tools:\n{catalogue}\n"
            "\n"
            "Examples:\n"
            "  make-colors contrast references/palette.csv\n"
            "  make-colors cvd screenshot.png --type deuteranopia\n"
            "  make-colors levels --level universal\n"
            "  make-colors palette-to-tailwind > tailwind.colors.js\n"
            "\n"
            "Every argument after the tool name belongs to that tool; run\n"
            "`make-colors <tool> --help` to see them.\n"
        ),
    )
    parser.add_argument(
        "tool",
        choices=sorted(TOOLS),
        help="Which tool to run. See the list below.",
    )
    # Everything after the tool name belongs to the tool, including flags this
    # parser also defines. Without REMAINDER, `make-colors contrast --help`
    # would print *this* help rather than the audit's, which is the opposite
    # of what the reader asked for.
    parser.add_argument(
        "rest",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to the tool.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Dispatch to one of the four tools.

    Parameters
    ----------
    argv : list of str or None, optional
        Argument vector without ``argv[0]``. Reads ``sys.argv`` when ``None``.

    Returns
    -------
    int
        Whatever the dispatched tool returns.
    """
    args = build_parser().parse_args(argv)
    module_name, extra, _ = TOOLS[args.tool]
    try:
        module = importlib.import_module(f"sprezzature_colors_scripts.{module_name}")
    except ImportError as exc:  # pragma: no cover - dependency guard
        sys.stderr.write(_missing_extra_message(args.tool, extra, exc))
        return 2

    # The tools read sys.argv themselves — they were commands before they were
    # sub-commands, and they still are. Handing them a rewritten argv is what
    # lets both be true.
    saved = sys.argv
    try:
        sys.argv = [f"make-colors {args.tool}", *args.rest]
        return int(module.main() or 0)
    finally:
        sys.argv = saved


def _missing_extra_message(tool: str, extra: str, exc: Exception) -> str:
    """What to say when a tool's dependency is not installed.

    Shared with the click twin so the two front doors cannot drift into
    saying different things about the same missing package.
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


if __name__ == "__main__":
    sys.exit(main())
