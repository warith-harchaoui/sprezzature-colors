#!/usr/bin/env python3
"""
``sprezzature-colors`` — the command line over this package's four tools.

One front door. Until 2026-10-25 there were two, an argparse one and a click
one, kept in step by sharing a table and a sentence; the click module imported
``TOOLS`` from the argparse module, so neither could be removed without the
other and every new sub-command had to be written twice. The catalogue now
lives in :mod:`sprezzature_colors._tools`, and this is the only parser.

``make-colors`` and ``sprezzature-colors`` both land here. The first name is
kept because it is what the skill, the README and years of notes tell people to
type; they are two spellings of one command, not two commands.

Each tool below is also its own console script — ``sprezzature-colors-contrast``
and friends — which is what a script or a pre-commit hook should call. This
front door is for a person who does not remember the exact name.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib
import importlib.util
import sys

import click

from sprezzature_colors._tools import TOOLS, missing_extra_message

#: Shown under the command list. Completion is click's, and worth saying out
#: loud: a four-tool front door is exactly where tab completion pays off, and
#: nobody discovers it by guessing.
_EPILOG = """\
Shell completion:

  \b
  eval "$(_SPREZZATURE_COLORS_COMPLETE=bash_source sprezzature-colors)"   # bash
  eval "$(_SPREZZATURE_COLORS_COMPLETE=zsh_source sprezzature-colors)"    # zsh

Run `sprezzature-colors tools` to see which tools are ready to run on this
machine and which need an extra installed.
"""


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog=_EPILOG,
    help=(
        "Everything this package does with a palette. Each tool below is also "
        "its own command (sprezzature-colors-contrast and so on), which is "
        "what a script should call."
    ),
)
@click.version_option(package_name="sprezzature-colors")
def main() -> None:
    """Front door over the four tools this package ships."""


@main.command(name="tools")
def list_tools() -> None:
    """
    List the tools, and say which ones can run here.

    The second half is the point. Three of these need nothing and one needs an
    extra, so "it is installed" and "it will run" are different questions, and
    a reader should not have to discover the difference from a traceback.
    """
    width = max(len(name) for name in TOOLS)
    for name, (module_name, extra, summary) in TOOLS.items():
        ready = importlib.util.find_spec(f"sprezzature_colors_scripts.{module_name}") is not None
        if ready and extra:
            # The module is importable, but its extra may still be absent --
            # the module is ours, the dependency is not.
            try:
                importlib.import_module(f"sprezzature_colors_scripts.{module_name}")
            except ImportError:
                ready = False
        mark = "ready" if ready else f"needs [{extra}]" if extra else "unavailable"
        click.echo(f"  {name:<{width}}  {mark:<14}  {summary.split('.')[0]}.")


def _attach(name: str, module_name: str, extra: str, summary: str) -> None:
    """
    Register one tool as a sub-command.

    Built in a loop rather than written out four times: the catalogue lives in
    one table, so a tool added there appears on the command line without
    anybody remembering to add it in a second place.
    """

    @main.command(
        name,
        help=summary,
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    )
    @click.argument("rest", nargs=-1, type=click.UNPROCESSED)
    def _run(
        rest: tuple[str, ...],
        _module: str = module_name,
        _name: str = name,
        _extra: str = extra,
    ) -> None:
        try:
            module = importlib.import_module(f"sprezzature_colors_scripts.{_module}")
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise SystemExit(missing_extra_message(_name, _extra, exc).rstrip()) from exc

        # The tools read sys.argv themselves -- they were commands before they
        # were sub-commands, and they still are. Handing them a rewritten argv
        # is what lets both be true.
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
