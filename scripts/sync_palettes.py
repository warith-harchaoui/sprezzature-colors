"""
sync_palettes: copy the three palettes of https://deraison.ai/colors into this package.

The site is the source of truth for every colour in the suite (decided by
Warith HARCHAOUI on 2026-11-14). It publishes one CSV per palette,
``palette-corporate.csv``, ``palette-academic.csv`` and ``palette-print.csv``,
with the same eleven names in the same order. This script copies them byte for
byte into ``references/`` and into the skill's ``references/``, then rewrites
``references/palette.csv``, the corporate palette in the column layout
:func:`_colors.load_palette` has always read and that ``sprezzature-figures``
looks for beside it.

The source is a directory holding the three files (a checkout of the site) or,
by default, the site itself over HTTPS. ``tests/test_palettes.py`` checks that
``palette.csv`` is what :func:`derive_palette_csv` makes of the corporate file,
so a hand edit of one without the other fails the build.

Usage
-----
    python scripts/sync_palettes.py                          # from deraison.ai
    python scripts/sync_palettes.py --source ~/web/deraison/colors

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import csv
import io
import sys
import urllib.request
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _click import run_command, sprezzature_command  # noqa: E402

#: Where the site publishes its CSVs.
SITE: str = "https://deraison.ai/colors/"

#: The three palettes, in the order the site shows them.
THEMES: tuple[str, ...] = ("corporate", "academic", "print")

REPO: Path = Path(__file__).resolve().parent.parent

#: Every folder that carries a copy of the palettes.
TARGETS: tuple[Path, ...] = (
    REPO / "references",
    REPO / "sprezzature_colors" / "skill" / "references",
)

#: Columns of ``palette.csv``, and the site column each one comes from.
DERIVED_COLUMNS: tuple[tuple[str, str], ...] = (
    ("Hexcode", "Hexcode"),
    ("Base", "Name"),
    ("LightHex", "LightHex"),
    ("Emotion", "Emotion"),
    ("Concepts", "Concepts"),
    ("PsychologyPositive", "Positive"),
    ("PsychologyNegative", "Negative"),
)


def derive_palette_csv(corporate_csv: str) -> str:
    """Return ``palette.csv`` as text, made from the site's corporate CSV."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow([dst for dst, _ in DERIVED_COLUMNS])
    for row in csv.DictReader(io.StringIO(corporate_csv)):
        writer.writerow([row[src] for _, src in DERIVED_COLUMNS])
    return out.getvalue()


def _read(source: str, name: str) -> str:
    """Read one CSV from a directory or from the site, with ``\\n`` line ends.

    The site serves the same bytes as its checkout but with ``\\r\\n``: the FTP
    upload converts them. Without this, the copy would change on every sync
    depending on where it was read from.
    """
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source.rstrip("/") + "/" + name, timeout=30) as resp:
            text = resp.read().decode("utf-8")
    else:
        text = (Path(source).expanduser() / name).read_text(encoding="utf-8")
    return text.replace("\r\n", "\n")


@sprezzature_command(
    name="sync-palettes",
    help="Copy the three palettes of deraison.ai/colors into references/ and rewrite palette.csv.",
)
@click.option(
    "--source",
    default=SITE,
    show_default=True,
    help="Directory holding palette-<theme>.csv, or the site's URL.",
)
def _command(source: str) -> int:
    """Copy, derive, and report each file written."""
    texts: dict[str, str] = {}
    for theme in THEMES:
        name = f"palette-{theme}.csv"
        try:
            texts[name] = _read(source, name)
        except OSError as exc:
            sys.stderr.write(f"sync-palettes: cannot read {name} from {source}: {exc}.\n")
            return 2
    texts["palette.csv"] = derive_palette_csv(texts["palette-corporate.csv"])
    for target in TARGETS:
        for name, text in texts.items():
            path = target / name
            path.write_text(text, encoding="utf-8")
            print(path.relative_to(REPO))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the sync; 0 on success, 2 when a file cannot be read."""
    return run_command(_command, argv)


if __name__ == "__main__":
    sys.exit(main())
