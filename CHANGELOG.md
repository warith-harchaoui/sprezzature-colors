# Changelog

## [Unreleased]

### Changed

- The last argparse command lines are click now: `sprezzature-colors-contrast`,
  `sprezzature-colors-cvd`, `sprezzature-colors-levels`,
  `sprezzature-colors-palette-to-tailwind` and `sprezzature-colors-mcp`. Option
  names, defaults, choices and exit codes are unchanged (a usage error still
  exits 2); the help now opens on click's `Usage:` line, `-V` prints the
  package's real version (it said 1.0.0), and every `main` takes
  `argv: list[str] | None = None`. `scripts/_argparse.py` is deleted and
  `scripts/_click.py` joins the synced helpers.
  `tests/test_every_command_is_click.py` checks every console script's
  `--help` and that nothing shipped imports argparse.
- The Docker image and `docker compose up` run `sprezzature-colors-mcp` on
  `0.0.0.0:8000` instead of bare uvicorn on `api:app`, so one container
  serves the HTTP routes and the MCP endpoint at `/mcp`. Before, the image
  had no `/mcp`.

### Fixed

- `sprezzature-colors-cvd` wrote PNG bytes under the source's extension:
  `hero.jpg` gave `hero-protanopia.jpg` holding a PNG. The per-type and
  grayscale files are now always named `.png`, and `--help` says so.
  `--out` keeps its meaning (a directory per type, a file for `--grid`).
- `sprezzature-colors-contrast` on a palette whose keys match no role
  printed `0 pass, 0 fail.` and exited 0, exactly like a palette that
  passed. It now says that nothing was checked and exits 2.
- `sprezzature-colors tools` cut every summary at its first period, so the
  contrast line ended at "(4.". It now cuts at a sentence end.
- Stale comments in `pyproject.toml`, the `Dockerfile` and
  `requirements.txt` still described argparse front doors, `cvd`/`api`/`mcp`
  extras and a base install with no dependencies.

### Docs

The Markdown files were checked against the code and rewritten where they
disagreed with it.

- **README / LISEZMOI.** The library example imported `scripts._colors`,
  which exists only in a checkout; it now uses `import sprezzature_colors as
  sc`. Its values were wrong: `#007AFF` on white is 4.02, not 4.55, so
  `meets_wcag` at AA normal is `False`, not `True`; `lighten(…, 0.15)` is
  `#47ABFF` and `darken(…, 0.10)` is `#0059DC`. The sample audit output was
  replaced by a real run. The install section still said "every heavier
  thing is an extra"; it now says one `pip install` brings everything and
  `[dev]` is only the test toolchain. Added: the five surfaces, the HTTP
  routes with their `operation_id`, Docker and compose, the MCP server and
  its `/mcp` endpoint, the accessibility levels as a fourth tool,
  `--all-pairs`, `--include-neutrals`, `--theme academic`, and the CVD type
  shorthands. The figure now opens both files. The suite table dropped
  best-engine-ai-helper, and the two languages now agree on the hub (ten
  bricks, where LISEZMOI said nine).
- **TRIGGERS.** Routed on the domain's closed vocabulary; added `health`, a
  table of every tool and the request it answers, the library and HTTP
  columns, `sprezzature-colors tools`, and the audit's key-name rule.
- **EXAMPLES.** The `Color` wrapper was imported from `scripts._colors` and
  promised `meets_wcag("#FFFFFF") -> True`; it is `False`. The sample
  outputs (audit, fix, levels) were invented and are now real. The
  pre-commit hook lacked `additional_dependencies`, so pre-commit would not
  have installed the command.
- **references/contrast-audit.md.** `-dark` roles are foregrounds, not
  excluded; the role tests are prefixes, not regexes; the CI step calls the
  installed command.
- **references/cvd-simulation.md.** Pillow is in the base install;
  `--grayscale`, `--out` as a directory, and the PNG-in-any-extension output
  are documented.
- **references/accessibility-levels.md.** The levels were described as a
  roadmap; they ship as `apply_level` and `sprezzature-colors-levels`.
- **CONTRIBUTING.** A new tool must also be registered in
  `sprezzature_colors/_tools.py`; `[tool.setuptools.package-dir]` needs no
  change; CI runs mypy.
- **Docstrings and help strings.** The `api` module listed six routes and
  missed `/v1/concepts`; `get_palette` documented `name`/`hex` keys the
  palette rows do not have; `search_concepts` said it returns names, it
  returns hex codes. The package docstring, `_tools.TOOLS` and the
  `sprezzature-colors` help still spoke of `[api]`, `[mcp]` and tools that
  need an extra. The `Color` doctest now passes, and the
  `sprezzature-colors-cvd` example gives `--grid` a file, not a directory.

### Changed — one `pip install`

**Everything this package does now installs with it.** 4 extras became
**one**, and it is not a feature: `[dev]` is the test toolchain.

  The colour-vision-deficiency simulator (Pillow) and both surfaces. The base
  was **one** dependency, so `pip install sprezzature-colors` could not simulate
  the deficiency the package exists to check for.

Measured across the suite before touching anything: **59 extras over eleven
repositories**, and **six bricks whose base was a single dependency** — so
`pip install <brick>` installed almost nothing and did almost nothing, and
choosing the right extra was a thing a reader had to know *before* the package
could do its job. Here the base goes from **1** to **6**
dependencies.

All eleven unions were dry-run resolved in a clean venv before any manifest was
edited, so this is a measured feasibility and not an optimistic one.

### Fixed — the places that encoded the extras

Install lines, error messages, docstrings, the `Dockerfile`, the CI workflow and
the README/LISEZMOI install sections all named extras that no longer exist. pip
treats an unknown extra as a **warning and exits 0**, so none of these would
have failed loudly: they would have quietly installed nothing.

The hub's `test_no_document_promises_an_extra_that_does_not_exist` found the
cross-repository ones — a document in one brick naming another brick's extra —
which no per-repository pass would have caught.

### Changed
- **One command line, not two.** The argparse front door is gone; click is the
  only parser and both `make-colors` and `sprezzature-colors` resolve to the
  same callable. Until now the click module imported `TOOLS` from the argparse
  module, so neither could be removed without the other and every sub-command
  had to be written twice.
- `click` moves from an optional extra to a **base dependency**. This package
  deliberately carried none, and this is the one bought on purpose: with
  argparse gone there is no parser that ships with Python, so an optional click
  would mean an install whose own commands do not run. The per-tool scripts
  still need nothing beyond it.
- The catalogue and the missing-extra sentence moved to
  `sprezzature_colors/_tools.py`, so they owe nothing to whichever parser reads
  them.

### Added
- `sprezzature-colors tools` — lists the tools and says which can actually run
  here. "Installed" and "will run" are different questions when a tool needs an
  extra.
- Shell-completion instructions in the group help.

### Removed
- `sprezzature_colors/cli_click.py`, the `[click]` extra, and the mypy
  `attr-defined` suppression the two-branch guard required.


All notable changes to sprezzature-colors are documented here.

## [1.1.0] - 2026-10-19: two front doors over the four tools

Until now there was no way to find out what this package does except by
reading its README. Each tool had its own console script and nothing listed
them together — four commands on the PATH and no catalogue.

### Added

- **`make-colors` (argparse) and `sprezzature-colors` (click)**, two front
  doors over the same four tools. Both read a single table
  (`sprezzature_colors/cli.py`) and share the one sentence said about a
  missing extra, so a tool cannot appear in one and be missing from the
  other, nor be explained differently by each. `make-colors --help` prints
  the catalogue.

  Each tool is still its own command — `sprezzature-colors-contrast`,
  `-cvd`, `-levels`, `-palette-to-tailwind` — which is what a script should
  call. Nothing is taken away.

- **A `[click]` extra.** Click belongs to one of the two front doors, so it
  is an extra rather than a dependency, and the import in `cli_click.py` is
  **guarded**. That matters more here than in most packages: this one
  declares no base dependencies at all, which is the whole reason its
  contrast audit is cheap enough to live in a pre-commit hook. A twin that
  imported click at module load would end that silently, because the failure
  arrives at the console script rather than at the install. A bare install
  gets a sentence naming the extra, and is told that `make-colors` needs
  nothing.

  The guard is checked by hiding click from a subprocess rather than by
  reading the source, and the check was verified by sabotage: with the
  `try/except` removed, three tests fail.

### Fixed

- **The README's PyPI-safety check read code blocks as links.** An example
  containing `'<a href="/">x</a>'` counted as a relative link and failed the
  build. The rule is narrowed to the prose rather than weakened by an
  allow-list, with a second test proving a real relative link in prose still
  fails.

## [1.0.1] - 2026-10-02: the half of the dependency guard nobody runs

### Fixed

- **`mcp.py` defined `main` twice, and the two took different arguments.** One
  definition sits in the `except ImportError` branch reached when the `[mcp]`
  extra is absent, the other in the `else` branch that serves the real
  endpoint. A single console script reaches both, so to a caller they are one
  function. They were not: the fallback took nothing while the real one took
  `argv`, so `main(["--host", "127.0.0.1"])` answered on a machine with the
  extra and raised `TypeError` on a machine without it. The broken half is the
  one a reader who skipped the extra meets first.
- **`harchaoui.org` is gone, and every reference pointed at it.** The host now
  answers 503; the links go to `deraison.ai` and `sprezzature.ai`, including
  the `project.urls` homepage PyPI prints on the package page.
- **The quick start showed a command a PyPI reader cannot run.** `python
  scripts/...` is a path that exists in a clone and not in a wheel.

### Added

- **A type gate**, `mypy.ini` plus one CI step. The monorepo carried one while
  the skills lived there; at the split ruff came with the package and mypy did
  not, so no standalone package checked its own annotations. Run by hand, it
  found the `main` defect above in six packages at once. The step runs once, on
  3.12: this is a gate, not a test matrix.
- **Two tests for the same ground.** `test_mcp_fallback_signature.py` reads the
  source as a syntax tree, so it needs neither mypy nor an install.
  `test_console_scripts_exist.py` checks that every command the help text names
  is a command pip installs; it could previously report green while testing
  nothing when its scan found no candidates, which a new case rules out.
- **A versioned `.githooks/pre-push`** running the same lint, type and test
  steps as the workflow, in the same order, so a red state cannot reach the
  remote.

## [1.0.0] - 2026-07-27

### Added

- Initial release extracted from the sprezzature monorepo.
- `scripts/_colors.py`: shared color primitives — sRGB transfer, hex
  parsing, WCAG luminance and contrast (including alpha-aware
  compositing), OKLab/OKLCH conversion, perceptual `lighten`/`darken`,
  the Machado et al. (2009) CVD matrices, and the curated palette
  accessors (Apple base, emotion, concept, and psychology
  projections).
- `scripts/audit_contrast.py`: WCAG contrast audit over a JSON
  palette, with an OKLCH-neighbour fix suggester for failing pairs.
- `scripts/simulate_cvd.py`: protanopia/deuteranopia/tritanopia image
  simulation via Pillow, with a side-by-side mosaic mode and an
  optional grayscale panel.
- `scripts/palette_to_tailwind.py`: renders `references/palette.csv`
  as a Tailwind `theme.extend.colors` block or a full
  `tailwind.config.js`.
- `scripts/accessibility_levels.py`: remaps the canonical palette to
  an accessibility level (`universal`, `high-contrast`, `monochrome`,
  or a specific CVD type) while keeping the same color names.
- `scripts/_argparse.py`: shared argparse parser factory used across
  all scripts.
- `references/palette.csv`: the canonical Apple-inspired palette with
  semantic projections (emotion, concepts, psychology).
- `references/contrast-audit.md`, `references/cvd-simulation.md`,
  `references/accessibility-levels.md`: usage and design-rationale
  documentation for each tool.
- Academic (Okabe-Ito 2002) palette theme: `_colors.academic_palette`,
  `_colors.academic_palette_rows`, and `palette_to_tailwind.py
  --theme academic`, for output that needs a citable
  colour-vision-deficiency-safe standard rather than the brand
  palette.
