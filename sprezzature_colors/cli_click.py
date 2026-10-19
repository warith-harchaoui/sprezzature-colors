"""
The click command line — ``sprezzature-colors``.

The twin of :mod:`sprezzature_colors.cli`: same four tools, same dispatch,
the other parser. Both read the single ``TOOLS`` table and share the one
sentence said about a missing extra, so a tool cannot appear in one front
door and be missing from the other, nor be explained differently by each —
which is the failure a second command line invites, and the reason this one
is plumbing rather than a second catalogue.

Click is an extra here (``[click]``), and that matters more in this package
than in most: ``sprezzature-colors`` declares **no** base dependencies at all,
which is why its contrast audit is cheap enough to sit in a pre-commit hook.
A click twin that imported click at module load would quietly end that — so
the import below is guarded, and a command somebody's own ``pip install`` just
put on ``PATH`` answers a sentence naming the extra rather than a traceback
about a package they never asked for.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib
import sys

from sprezzature_colors.cli import TOOLS, _missing_extra_message

try:
    import click
except ImportError:  # pragma: no cover - exercised by a bare install

    def main(argv: list[str] | None = None) -> int:
        """Say which extra installs this command, and exit non-zero.

        The signature matches the real ``main`` exactly. Two conditional
        definitions that disagree are a trap: a caller who imports ``main``
        and passes an argv would get a TypeError on the machine where the
        extra is missing, and nowhere else.
        """
        del argv  # the message is the same whatever was asked for
        print(
            "sprezzature-colors is the click front door, and click is an "
            "optional extra here:\n"
            "    pip install 'sprezzature-colors[click]'\n"
            "The argparse front door, `make-colors`, needs nothing — this "
            "package has no base dependencies, which is the point of it.",
            file=sys.stderr,
        )
        return 1
else:

    @click.group(
        context_settings={"help_option_names": ["-h", "--help"]},
        help=(
            "Everything this package does with a palette. Each tool below is "
            "also its own command (sprezzature-colors-contrast and so on), "
            "which is what a script should call."
        ),
    )
    @click.version_option(package_name="sprezzature-colors")
    def main() -> None:  # type: ignore[misc]  # pragma: no cover - click dispatches
        """Front door over the four tools this package ships."""

    def _attach(name: str, module_name: str, extra: str, summary: str) -> None:
        """Register one tool as a click sub-command.

        Built in a loop rather than written out four times: the catalogue
        lives in one table, and a tool added there appears in both command
        lines without anybody remembering to add it twice.
        """

        # `main` is a click Group here, but mypy only sees the first of the
        # two conditional definitions — the plain function that refuses when
        # click is missing — and a function has no `.command`. The guard is
        # the point of this module, so the suppression stays and says why.
        @main.command(  # type: ignore[attr-defined]
            name,
            help=summary,
            context_settings={
                "ignore_unknown_options": True,
                "allow_extra_args": True,
            },
        )
        @click.argument("rest", nargs=-1, type=click.UNPROCESSED)
        def _run(
            rest: tuple[str, ...],
            _module: str = module_name,
            _name: str = name,
            _extra: str = extra,
        ) -> None:
            try:
                module = importlib.import_module(
                    f"sprezzature_colors_scripts.{_module}"
                )
            except ImportError as exc:  # pragma: no cover - dependency guard
                raise SystemExit(
                    _missing_extra_message(_name, _extra, exc).rstrip()
                ) from exc

            # The tools read sys.argv themselves — they were commands before
            # they were sub-commands, and they still are.
            saved = sys.argv
            try:
                sys.argv = [f"sprezzature-colors {_name}", *rest]
                raise SystemExit(int(module.main() or 0))
            finally:
                sys.argv = saved

    for _tool, (_module_name, _extra, _summary) in TOOLS.items():
        _attach(_tool, _module_name, _extra, _summary)


if __name__ == "__main__":
    main()
