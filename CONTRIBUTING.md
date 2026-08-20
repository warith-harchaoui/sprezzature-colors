# Contributing

## Setup

```bash
git clone https://github.com/warith-harchaoui/sprezzature-colors
cd sprezzature-colors
pip install -e ".[dev,cvd]"
```

## Tests

```bash
pytest
```

## Lint

`ruff` is the Python linter and formatter this project uses: it reads
the source without running it and flags style issues (unused imports,
wrong quote style, and the like) in one fast pass.

```bash
ruff check .
```

## Adding a script

1. Put shared color math in `scripts/_colors.py`, not in the new
   script. Every existing script (`audit_contrast.py`,
   `simulate_cvd.py`, `accessibility_levels.py`,
   `palette_to_tailwind.py`) imports its color primitives from there;
   a new script should do the same rather than reimplementing sRGB or
   OKLCH conversion.
2. Build the CLI parser with `_argparse.make_parser`, not a bare
   `argparse.ArgumentParser`, so `--version` and the help formatting
   stay consistent across scripts.
3. Add the script to `[tool.setuptools.package-dir]` /
   `[project.scripts]` in `pyproject.toml` if it needs a console entry
   point.
4. Add a test in `tests/test_colors.py`.
5. Document the script in `EXAMPLES.md` and in the relevant `README.md`
   / `LISEZMOI.md` quick-start section. If the script is substantial
   enough to need design rationale (not just usage), add a matching
   `references/<script-name>.md`.

## Code standards

See `CODING.md`. NumPy docstrings, full typing, ~25-30% comment
density.

## Prose standards

See `references/WRITING.md` (EN) and `references/ECRITURE.md` (FR).
No punctuation dashes, no machine tells.
