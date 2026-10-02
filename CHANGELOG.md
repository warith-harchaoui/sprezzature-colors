# Changelog

All notable changes to sprezzature-colors are documented here.

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
