# Changelog

## [Unreleased]

## [1.4.0] — 2026-11-14

### Changed

- **The colours come from [deraison.ai/colors](https://deraison.ai/colors/)
  now, and nowhere else.** The site publishes three palettes with the same
  eleven names; the package ships its three CSV files byte for byte
  (`references/palette-corporate.csv`, `palette-academic.csv`,
  `palette-print.csv`), and `palette.csv` is derived from the corporate one.
  The values change accordingly:
  - **corporate**: Apple's system colours of June 9, 2025, where the old file
    had an earlier set. Red `#FF3B30` → `#FF383C`, orange `#FF9500` →
    `#FF8D28`, green `#28CD41` → `#34C759`, turquoise `#79DBDC` → `#00C3D0`,
    blue `#007AFF` → `#0088FF`, purple `#AF52DE` → `#CB30E0`, brown
    `#A52A2A` → `#AC7F5E`, gray `#808080` → `#8E8E93`; yellow, pink and black
    unchanged. Every light tint follows.
  - **academic**: the red is the CUD (Colour Universal Design) vermilion
    `#E73121` instead of Okabe and Ito's `#D55E00`; pink is `#FF8082` and no
    longer borrows purple's `#CC79A7`; brown `#804000`, black and gray
    `#84919E` are part of it. Its light tints are the site's, no longer
    derived by `lighten` (`ACADEMIC_LIGHT_DELTA` is gone).
  - **white has left the palettes**, as on the site on 2026-11-13: eleven
    names, not twelve.
  - **no RGB columns**: the site keeps hexadecimal codes only, so
    `palette.csv` dropped `R`, `G` and `B`. `name_to_rgb` still answers,
    from the hex.
- `audit_contrast.py`'s built-in brand tokens carry the corporate hex and
  light tint, and Apple's dark-mode value of the same date for `dark`.

### Fixed

- **`--fix` suggested colours that fail the target.** The search measured
  each candidate before it became a hex code: before rounding to 8 bits and,
  worse, before the out-of-gamut ones were clipped into sRGB. A suggestion
  could then miss its own threshold by a wide margin: `#C30000` was offered
  "at 7.10" for a red on white and measures 6.33; `#0074E9` "at 4.55"
  measures 4.49. The candidate is now judged as the hex that is printed,
  and a test checks every suggestion of the built-in audit against its
  target.

### Added

- **The print palette**, checked for offset printing on coated paper:
  `print_palette()`, and `--theme print` on `palette-to-tailwind` and on
  `levels`.
- `THEMES`, `theme_rows(theme)` (the site's rows, English and French),
  `theme_palette(theme)` (the eight hues) and `theme_palette_rows(theme)`
  (eleven `Base` / `Hexcode` / `LightHex` rows), exported by the package.
- `GET /v1/palette?theme=corporate|academic|print`, and the same argument on
  the MCP tool `get_palette`; the answer names its `theme` and no longer
  carries `R`, `G`, `B`.
- `sprezzature-colors-levels --theme corporate|academic|print`; `--csv`
  also reads a `Name` column, so the site's files work as they are.
- `scripts/sync_palettes.py` copies the three files from the site (or a
  checkout of it) into `references/` and the skill, and rewrites
  `palette.csv`. The site serves them with `\r\n` line ends; the copy is
  normalised to `\n`, so where it was read from changes nothing.
- `tests/test_palettes.py`: eleven names in order in each palette,
  `palette.csv` equal to what the sync derives, the skill's copies equal to
  the package's, every CSV declared as package data, and the audit's brand
  tokens equal to the corporate palette.

### Docs

- Every example that printed a palette value was run again: contrast of the
  blue on white 3.52 (was 4.02), the audit's `35 pass, 21 fail` (was 34 and
  22), the levels preview, the API answers. The collision given as an example
  of what the deficiency levels cannot always prevent is now Orange and
  Yellow under deuteranopia, measured on the new palette (Yellow and White
  was the old one, and white is gone).

## [1.3.0] — 2026-11-12

### Added

- **The skill travels with the package.** `SKILL.md`, its reference documents,
  `palette.csv` and its trigger catalogue lived only in the `sprezzature` hub,
  so `pip install sprezzature-colors` gave the library, the command line, the
  HTTP (HyperText Transfer Protocol, the request-and-reply exchange a browser
  makes for each page) API (Application Programming Interface, web addresses
  another program sends a request to) and the MCP (Model Context Protocol, the
  protocol through which AI agents call tools in English) server, and nothing
  an agent could route on. They now ship in `sprezzature_colors/skill/`, inside
  the wheel: one install carries all five surfaces.
- `sprezzature-colors-skill`, and the same command as `sprezzature-colors
  skill`, reports whether the copy an agent reads is in step with the
  package; `--install` copies it into `~/.claude/skills` (`--agent opencode`
  for `~/.opencode/skills`), moving any previous copy to `skills-superseded/`
  beside the skills folder; `--path` prints where pip put it.
- `sprezzature_colors.skill_path()` returns that folder, and is in `__all__`.

### Docs

The Markdown files were checked against the code again.

- README, LISEZMOI, `TRIGGERS.md` and the skill said the skill lived in the
  hub under `sprezzature/sprezzature-colors/`; it is in the package. The
  `skill` sub-command was missing from every list of the front door's
  sub-commands, and `TRIGGERS.md` now routes "is the skill installed" to it.
- `CONTRIBUTING.md` says where the skill lives, which of its parts are
  generated by the hub, and that `references/*.md` and the skill's
  `references/*.md` are two copies to change together.
- `EXAMPLES.md` shows the skill command.
- `LANDSCAPE.md` and `PAYSAGE.md` said the package does three things on the
  standard library; it does four (the accessibility levels were missing), and
  only its colour arithmetic is standard library. They gave
  sprezzature-figures 167 chart types; its catalogue holds 168.
- The README said "Missing directories are created." twice in a row.
- Every acronym of these documents is now spelt out where it first appears:
  WCAG (Web Content Accessibility Guidelines, the international rules for
  readable web content), OKLCH (OK Lightness Chroma Hue, a colour model in
  which equal steps look equally different to the eye) and the rest.

## [1.2.4] — 2026-11-08

### Fixed

- `sprezzature-colors-levels --level monochrome` gave two categories the same
  grey. The 3:1 floor darkened every rank above it onto one value, so on the
  house palette Yellow and Turquoise came out as one `#909090` and four colours
  sat within a shade of each other. The grey band now stops where it clears the
  floor, and the twelve colours get twelve greys. Figures that ask for this
  level change colour.
- `contrast --palette` on a file that is not there, on JSON (JavaScript Object Notation, a text
  format of named fields) that is not an object, or on a role holding something other than a string ended on a
  traceback, and a traceback exits 1, which a CI (continuous integration, a server that
  reruns every check each time code is pushed) job reads as a failing pair.
  They now exit 2 with one line. A role holding a number used to be dropped in
  silence when it was flat; it is refused too. Keys that are not roles may
  still hold anything.
- `levels --csv` on a missing file was a traceback, and on a file with neither
  column printed nothing and exited 0. Both now exit 2 with one line.
- `cvd --grid --out dir/x.png` ended on a traceback when `dir` did not exist,
  where the per-type mode has always created its directory; the example in
  `references/cvd-simulation.md` did exactly that. An output that cannot be
  written is now one line and exit 1.
- The HTTP routes answered 500 on a malformed hex such as `#zzz`. Everything
  starting with `#` went past the check that gives a 400 to an unknown colour.
- The MCP server told every host that its version was a sentence: fastapi-mcp
  0.4 passes the description in the version slot of `Server`. It now announces
  the package version, and the description as its instructions.
- `_click.SKILL_VERSION`, the version a bare clone prints, was still 1.2.2.

### Docs

- The exit code 2 of the audit also covers a palette it cannot read; the README,
  the LISEZMOI, `EXAMPLES.md`, `TRIGGERS.md` and the audit's reference said only
  "no pair".
- `references/accessibility-levels.md` and the module docstring said monochrome
  gives each colour the grey of its own luminance; it ranks them and spreads the
  ranks. The README, the LISEZMOI and the docstring said the deficiency levels
  separate or guarantee every category; measured on the house palette they do
  not always (Yellow and White under tritanopia), and the text now says so.
- The "standard library only" claims about the audit and the Tailwind emitter
  date from before click: it is the arithmetic that is.
- The CI recipes of the audit reference wrote into an `artifacts/` directory
  nothing created, and uploaded nothing when the audit failed.

## [1.2.3] — 2026-11-05

### Fixed

- `contrast --palette` on a colour it cannot read (`rgba(...)`, `hsl(...)`)
  or on a file that is not JSON ended on a raw Python traceback. It now says
  it cannot read the palette, names the value, and exits 2. Reading `rgba()`
  is still to do (LANDSCAPE, entry 6).

### Docs

- `LANDSCAPE.md` and `PAYSAGE.md` still listed the silent pass on a palette
  with no matching key as a defect to fix; 1.2.0 fixed it (exit 2), and the
  entry now says so and points at what remains, a `--pairs` file.
- The README, the LISEZMOI and the how-it-works figure spoke of three tools
  where the package ships four, and the figure's footer called the whole
  package standard library only; it is the colour arithmetic that is, and
  the figure now says so.

## [1.2.2] — 2026-11-05

### Fixed

- `requirements-cvd.txt`, which installs the colour-blindness simulator on
  its own from a source checkout, listed Pillow but not click, which
  `simulate_cvd.py` imports; it now lists both, and
  `references/cvd-simulation.md` says so.

## [1.2.1] — 2026-11-05

### Docs

- `references/cvd-simulation.md` still said `hero.jpg` gives
  `hero-protanopia.jpg` holding PNG data, the defect 1.2.0 fixed; it now
  says every file is named `.png`.
- `sprezzature-colors-cvd --grid` promised a 2×2 mosaic. The mosaic is two
  panels per row, so `--grayscale` makes three rows; the help and the
  module docstring now say so.
- `CODING.md` and `references/CODING.md` pointed at a gist that does not
  exist; they now name the real one.
- The MCP fallback's docstring and a CI comment still spoke of the `[mcp]`
  and `[api,mcp]` extras, and so did the docstring of
  `tests/test_mcp_fallback_signature.py`.

### Changed

- The front door `sprezzature-colors` (and `make-colors`) answers `-V` as
  well as `--version`, like every per-tool command already did; a test
  holds both flags.
- `sprezzature-colors-levels --level` has a help text and shows its default.
- `sprezzature-colors tools` lost its "needs [extra]" branch, which nothing
  could reach since every tool's extra is empty; the output is unchanged.

## [1.2.0] - 2026-11-04: click everywhere, and an audit that cannot pass on nothing

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
  `meets_wcag` at AA (the standard WCAG level) normal is `False`, not `True`; `lighten(…, 0.15)` is
  `#47ABFF` and `darken(…, 0.10)` is `#0059DC`. The sample audit output was
  replaced by a real run. The install section still said "every heavier
  thing is an extra"; it now says one `pip install` brings everything and
  `[dev]` is only the test toolchain. Added: the five surfaces, the HTTP
  routes with their `operation_id`, Docker and compose, the MCP server and
  its `/mcp` endpoint, the accessibility levels as a fourth tool,
  `--all-pairs`, `--include-neutrals`, `--theme academic`, and the CVD (colour vision deficiency) type
  shorthands. The figure now opens both files. The suite table dropped
  best-engine-ai-helper, and the two languages now agree on the hub (ten
  bricks, where LISEZMOI said nine).
- **TRIGGERS.md.** Routed on the domain's closed vocabulary; added `health`, a
  table of every tool and the request it answers, the library and HTTP
  columns, `sprezzature-colors tools`, and the audit's key-name rule.
- **EXAMPLES.md.** The `Color` wrapper was imported from `scripts._colors` and
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
- **CONTRIBUTING.md.** A new tool must also be registered in
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
them together — four commands on the `PATH` and no catalogue.

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
