# Changelog

All notable changes to sprezzature-colors are documented here.

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
