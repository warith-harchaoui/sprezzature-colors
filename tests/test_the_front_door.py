"""
One front door, two spellings, and the catalogue behind it.

There were two front doors until 2026-10-25 — an argparse one and a click one,
kept in step by sharing a table and a sentence. The click module imported
``TOOLS`` from the argparse module, so neither could be removed without the
other, every sub-command had to be written twice, and the conditional
``main`` the click twin needed when click was optional cost a mypy suppression
in every package of the suite.

Click is now the only parser and a base dependency. These tests guard what
replaced that arrangement: that ``make-colors`` and ``sprezzature-colors`` are
two names for one callable rather than two implementations, that the catalogue
is still the single source of the command list, and that the old shape does not
grow back.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest
import tomllib
from click.testing import CliRunner

from sprezzature_colors._tools import TOOLS, missing_extra_message
from sprezzature_colors.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent


def _pyproject() -> dict:
    return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _subcommands() -> set[str]:
    return set(main.commands) - {"tools"}


# ---------------------------------------------------------------- the door


def test_the_two_spellings_are_one_callable() -> None:
    """
    ``make-colors`` and ``sprezzature-colors`` must resolve to the same target.

    This is the whole point of removing the second parser: two names that each
    had their own implementation is exactly how the two drifted. Two names
    pointing at one function cannot.
    """
    scripts = _pyproject()["project"]["scripts"]
    assert scripts["make-colors"] == scripts["sprezzature-colors"]
    assert scripts["make-colors"] == "sprezzature_colors.cli:main"


def test_click_is_a_base_dependency_not_an_extra() -> None:
    """
    With argparse gone, no parser ships with Python, so an optional click means
    a `pip install sprezzature-colors` whose own commands do not run.
    """
    project = _pyproject()["project"]
    assert any(dep.startswith("click") for dep in project["dependencies"])
    extras = project.get("optional-dependencies", {})
    assert "click" not in extras, "the [click] extra promises something already installed"


def test_the_argparse_front_door_is_gone() -> None:
    """
    Guard against the old shape growing back.

    A second parser would re-introduce the duplicate command list and the
    conditional ``main`` whose two definitions had to be kept in signature
    agreement by hand.
    """
    assert not (REPO_ROOT / "sprezzature_colors" / "cli_click.py").exists()
    source = (REPO_ROOT / "sprezzature_colors" / "cli.py").read_text(encoding="utf-8")
    assert "import argparse" not in source


@pytest.mark.parametrize("front_door", ["make-colors", "sprezzature-colors"])
def test_both_spellings_start(front_door: str) -> None:
    """`--help` answers in 0, and names the command the user typed."""
    done = subprocess.run([front_door, "--help"], capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr
    assert front_door in done.stdout


# ----------------------------------------------------------- the catalogue


def test_the_command_list_is_the_table() -> None:
    """The group's sub-commands are the catalogue, no more and no less."""
    assert _subcommands() == set(TOOLS)


def test_every_tool_names_a_module_that_exists() -> None:
    """A catalogue entry pointing at nothing fails at dispatch, not at import."""
    for tool, (module_name, _extra, _summary) in TOOLS.items():
        spec = importlib.util.find_spec(f"sprezzature_colors_scripts.{module_name}")
        assert spec is not None, f"{tool} names {module_name}, which does not exist"


def test_every_tool_has_a_summary_the_help_can_print() -> None:
    """An undocumented tool is a tool nobody finds."""
    for tool, (_module, _extra, summary) in TOOLS.items():
        assert summary.strip(), f"{tool} has no summary"


def test_the_help_lists_every_tool() -> None:
    """Click builds the list from the registered commands, so this holds as tools are added."""
    out = CliRunner().invoke(main, ["--help"]).output
    for tool in TOOLS:
        assert tool in out, f"{tool} is missing from the command list"


def test_an_extra_named_in_the_table_is_an_extra_that_exists() -> None:
    """`pip install 'sprezzature-colors[cvd]'` has to be real advice."""
    declared = set(_pyproject()["project"].get("optional-dependencies", {}))
    for tool, (_module, extra, _summary) in TOOLS.items():
        if extra:
            assert extra in declared, (
                f"{tool} tells the reader to install [{extra}], "
                f"which pyproject.toml does not declare"
            )


def test_the_missing_extra_message_names_the_extra() -> None:
    """It carries the install line, and invents nothing when there is no extra."""
    said = missing_extra_message("cvd", "cvd", ImportError("no module named PIL"))
    assert "pip install 'sprezzature-colors[cvd]'" in said

    said = missing_extra_message("contrast", "", ImportError("boom"))
    assert "pip install" not in said


# ------------------------------------------------------------- the extras


def test_the_tools_command_reports_readiness() -> None:
    """
    `tools` says which tools can actually run here.

    "Installed" and "will run" are different questions when one tool needs an
    extra, and a reader should not have to learn the difference from a
    traceback.
    """
    out = CliRunner().invoke(main, ["tools"]).output
    for tool in TOOLS:
        assert tool in out
    assert "ready" in out or "needs [" in out


def test_the_help_points_at_shell_completion() -> None:
    """
    A four-tool front door is where completion pays off, and nobody finds it by
    guessing.
    """
    out = CliRunner().invoke(main, ["--help"]).output
    assert "_SPREZZATURE_COLORS_COMPLETE" in out
