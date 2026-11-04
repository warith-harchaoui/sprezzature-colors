"""
Every command this package installs is a click command, and nothing here
imports argparse.

The suite decided on 2026-11-04 that its own command lines are click only.
The front door had been click since 2026-10-25, but the four per-tool
commands (``sprezzature-colors-contrast``, ``-cvd``, ``-levels``,
``-palette-to-tailwind``) and ``sprezzature-colors-mcp`` were still argparse:
two help layouts, two error formats and two ways of writing an option, behind
one ``pip install``.

Two checks, because either half can grow back without the other noticing:

* each console script answers ``--help`` with exit 0 and click's ``Usage:``
  line (argparse writes a lowercase ``usage:``);
* no Python file the package ships imports ``argparse``, read from the syntax
  tree so a docstring that mentions the word does not count.

Author
------
Warith HARCHAOUI <warithmetics@deraison.ai>
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The directories whose Python the wheel ships (see ``[tool.setuptools]``).
SHIPPED_DIRS = ("sprezzature_colors", "scripts")

_ENTRY_POINT = re.compile(r'^([\w.-]+)\s*=\s*"([\w.]+):(\w+)"', re.M)


def _commands() -> list[tuple[str, str, str]]:
    """Every (command, module, function) under ``[project.scripts]``."""
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^\[project\.scripts\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    return _ENTRY_POINT.findall(block.group(1)) if block else []


def _help(command: str, module: str, function: str) -> subprocess.CompletedProcess:
    """``command --help`` through the installed wrapper, or its equivalent."""
    found = shutil.which(command)
    if found is not None:
        return subprocess.run([found, "--help"], capture_output=True, text=True)
    code = (
        "import sys\n"
        f"sys.argv = [{command!r}, '--help']\n"
        f"from {module} import {function}\n"
        f"raise SystemExit({function}())\n"
    )
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


def test_there_are_commands_to_check() -> None:
    """An empty table would turn the case below into a skip that reads as a pass."""
    assert len(_commands()) >= 7


@pytest.mark.parametrize("command,module,function", _commands(), ids=lambda v: v)
def test_the_command_answers_help_the_click_way(command: str, module: str, function: str) -> None:
    """Exit 0, and click's capitalised ``Usage:`` rather than argparse's ``usage:``."""
    proc = _help(command, module, function)
    output = proc.stdout + proc.stderr
    if f"No module named '{module.split('.')[0]}'" in output:
        pytest.skip("sprezzature-colors is not installed here: pip install -e '.[dev]'")
    assert proc.returncode == 0, f"{command} --help exited {proc.returncode}:\n{output}"
    first = output.lstrip().splitlines()[0] if output.strip() else ""
    assert first.startswith("Usage:"), (
        f"{command} --help does not open on click's usage line; it opens on "
        f"{first!r}. A lowercase 'usage:' is argparse."
    )


def _shipped_sources() -> list[Path]:
    """Every Python file the wheel ships."""
    return sorted(
        path
        for folder in SHIPPED_DIRS
        for path in (REPO_ROOT / folder).rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _imports_argparse(path: Path) -> bool:
    """True when ``path`` imports argparse anywhere, at module level or inside a function."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name.split(".")[0] == "argparse" for alias in node.names
        ):
            return True
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "argparse":
            return True
    return False


def test_the_scan_reads_the_shipped_sources() -> None:
    """A scan that read nothing would pass the check below for nothing."""
    names = {path.name for path in _shipped_sources()}
    assert {"cli.py", "mcp.py", "simulate_cvd.py", "audit_contrast.py"} <= names


def test_nothing_shipped_imports_argparse() -> None:
    """The suite's command lines are click only; the parser factory is gone too."""
    offenders = [
        str(path.relative_to(REPO_ROOT)) for path in _shipped_sources() if _imports_argparse(path)
    ]
    assert not offenders, f"these shipped modules import argparse: {offenders}"
    assert not (REPO_ROOT / "scripts" / "_argparse.py").exists()
