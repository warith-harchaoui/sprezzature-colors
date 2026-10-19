"""
Two front doors over four tools, and neither may drift from the other.

`make-colors` (argparse) and `sprezzature-colors` (click) exist so somebody
can find out what this package does without reading its README — until they
existed, each tool had its own console script and nothing listed them
together. The moment there are two of them, the interesting failure is not
that one breaks: it is that they quietly stop agreeing. A tool added to one,
an extra named differently by the other, a summary edited in one place.

So both read one table and share one sentence about a missing extra, and
these tests hold that shape rather than the behaviour of either.

The last test is the one with teeth. This package declares **no** base
dependencies, which is the whole reason its contrast audit is cheap enough to
live in a pre-commit hook. A click twin that imported click at module load
would end that silently — the import error arrives at the console script, not
at the install — so the guard is checked by actually hiding click.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from sprezzature_colors.cli import TOOLS, _missing_extra_message, build_parser

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def test_both_front_doors_offer_exactly_the_same_tools() -> None:
    """The click group's sub-commands are the table, no more and no less."""
    from sprezzature_colors.cli_click import main as click_main

    assert set(click_main.commands) == set(TOOLS)


def test_every_tool_names_a_module_that_exists() -> None:
    """A catalogue entry pointing at nothing fails at dispatch, not at import."""
    for tool, (module_name, _extra, _summary) in TOOLS.items():
        assert (SCRIPTS_DIR / f"{module_name}.py").is_file(), (
            f"{tool} dispatches to {module_name}, which is not in scripts/"
        )


def test_every_tool_has_a_summary_the_help_can_print() -> None:
    """An undocumented tool is a tool nobody finds."""
    for tool, (_module, _extra, summary) in TOOLS.items():
        assert summary.strip(), f"{tool} has no summary"
        assert summary.rstrip().endswith("."), f"{tool}'s summary is not a sentence"


def test_the_argparse_help_lists_every_tool() -> None:
    """The epilog is built from the table, so this holds as tools are added."""
    epilog = build_parser().epilog or ""
    for tool in TOOLS:
        assert tool in epilog, f"{tool} is in the table and not in the help"


def test_an_extra_named_in_the_table_is_an_extra_that_exists() -> None:
    """`pip install 'sprezzature-colors[cvd]'` has to be real advice."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = re.search(
        r"^\[project\.optional-dependencies\]\s*$(.*?)(?=^\[|\Z)",
        pyproject,
        re.M | re.S,
    )
    assert section
    declared = set(re.findall(r"^\s*([A-Za-z0-9._-]+)\s*=", section.group(1), re.M))
    for tool, (_module, extra, _summary) in TOOLS.items():
        if extra:
            assert extra in declared, (
                f"{tool} tells the reader to install [{extra}], "
                f"which pyproject.toml does not declare"
            )


def test_the_missing_extra_message_names_the_extra() -> None:
    """Both front doors print this, so it has to carry the install line."""
    said = _missing_extra_message("cvd", "cvd", ImportError("no module named PIL"))
    assert "pip install 'sprezzature-colors[cvd]'" in said

    # And when there is no extra, it must not invent one to recommend.
    said = _missing_extra_message("contrast", "", ImportError("boom"))
    assert "pip install" not in said


@pytest.mark.parametrize("front_door", ["make-colors", "sprezzature-colors"])
def test_both_front_doors_are_declared_as_console_scripts(front_door: str) -> None:
    """A front door nobody can type is not a front door."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = re.search(
        r"^\[project\.scripts\]\s*$(.*?)(?=^\[|\Z)", pyproject, re.M | re.S
    )
    assert section
    assert re.search(rf"^{re.escape(front_door)}\s*=", section.group(1), re.M)


def test_the_click_twin_refuses_politely_when_click_is_missing() -> None:
    """A bare install must get a sentence, not a traceback.

    Checked by hiding click from a subprocess rather than by reading the
    source: the whole point is what happens at import time on a machine that
    never installed it, and that is not visible from inside a session where
    it is importable.
    """
    program = (
        "import sys\n"
        # `find_spec`, not `find_module`: the legacy finder API was removed
        # in Python 3.12, so a blocker written that way is simply never
        # consulted — click imports normally and the test passes by not
        # testing anything. This one was written that way first.
        "class Blocked:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'click':\n"
        "            raise ImportError('click is not installed')\n"
        "        return None\n"
        "sys.meta_path.insert(0, Blocked())\n"
        "from sprezzature_colors.cli_click import main\n"
        "sys.exit(main())\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert done.returncode == 1, done.stderr
    assert "sprezzature-colors[click]" in done.stderr
    assert "make-colors" in done.stderr, (
        "the refusal has to point at the front door that needs nothing"
    )
    assert "Traceback" not in done.stderr


def test_the_refusal_and_the_real_command_agree_on_their_signature() -> None:
    """Two conditional definitions that disagree are a trap.

    A caller who imports ``main`` and passes an argv would get a TypeError on
    the machine where click is missing and nowhere else — the hardest kind of
    bug to be told about, because the person who hits it has the broken
    install and you have the working one.
    """
    program = (
        "import inspect, sys\n"
        # `find_spec`, not `find_module`: the legacy finder API was removed
        # in Python 3.12, so a blocker written that way is simply never
        # consulted — click imports normally and the test passes by not
        # testing anything. This one was written that way first.
        "class Blocked:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'click':\n"
        "            raise ImportError('click is not installed')\n"
        "        return None\n"
        "sys.meta_path.insert(0, Blocked())\n"
        "from sprezzature_colors.cli_click import main\n"
        "print(list(inspect.signature(main).parameters))\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert done.returncode == 0, done.stderr
    # The real `main` is a click Group, called with no arguments by the
    # console script; the refusal takes an optional argv and returns a code.
    # What matters is that passing nothing works on both.
    assert done.stdout.strip() == "['argv']"
