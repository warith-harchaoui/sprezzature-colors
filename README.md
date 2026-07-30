# sprezzature-colors

Color accessibility and palette tooling for the [sprezzature](https://harchaoui.org/warith/sprezzature/) stack.

Three tools in one package:

- **WCAG contrast auditing** -- check every (foreground, background) pair against the 4.5:1, 3:1, or 7:1 thresholds. Get suggested fixes that stay on the same hue.
- **Color vision deficiency simulation** -- render images as protanopia, deuteranopia, or tritanopia viewers see them. Produces sibling files or a 2x2 review mosaic.
- **Tailwind CSS palette export** -- write the canonical brand palette as a `tailwind.config.js` theme block or full config, with optional derived dark variants.

All scripts are deterministic and run on pure stdlib (CVD simulation adds Pillow). No network at import time.

---

## Install

```bash
pip install sprezzature-colors
```

For CVD image simulation:

```bash
pip install sprezzature-colors[cvd]
```

---

## Quick start

### Contrast audit

```bash
python scripts/audit_contrast.py
# Target ratio: 4.5
#
#   ✓      brand-blue  on  surface-primary   ratio 4.55
#   ✗      brand-red   on  surface-secondary  ratio 2.83
#       -> suggest #D4000A  (ratio 4.51)
```

With a custom palette JSON:

```bash
python scripts/audit_contrast.py --palette my-palette.json --target 7 --fix
python scripts/audit_contrast.py --palette my-palette.json --format json
```

### CVD simulation

```bash
# Three sibling PNG files
python scripts/simulate_cvd.py hero.png

# 2x2 mosaic for design review
python scripts/simulate_cvd.py hero.png --grid --out hero-cvd-grid.png

# Only deuteranopia + grayscale
python scripts/simulate_cvd.py hero.png --types deut --grayscale
```

### Palette to Tailwind

```bash
# Copy-paste block for an existing config
python scripts/palette_to_tailwind.py

# Full tailwind.config.js with derived dark variants
python scripts/palette_to_tailwind.py --emit config --with-dark --out tailwind.config.js
```

### Accessibility levels

```bash
# Preview the canonical palette at AAA high-contrast
python scripts/accessibility_levels.py --level high-contrast

# Available levels: universal (default), high-contrast, monochrome,
#                   deuteranopia, protanopia, tritanopia
```

---

## Library usage

```python
from scripts._colors import contrast_ratio_hex, meets_wcag, lighten, darken, simulate_pixel, CVD_MATRICES

# WCAG contrast ratio
ratio = contrast_ratio_hex("#007AFF", "#FFFFFF")   # -> 4.55

# WCAG AA test
ok = meets_wcag("#007AFF", "#FFFFFF", level="AA", size="normal")   # -> True

# Perceptual lighten/darken (OKLCH axis, hue preserved)
lighter = lighten("#007AFF", 0.15)   # -> "#5FA8FF" (approx.)
darker  = darken("#007AFF", 0.10)    # -> "#005DC2" (approx.)

# CVD pixel simulation
r, g, b = simulate_pixel((255, 0, 0), CVD_MATRICES["protanopia"])
```

---

## Features

| Feature | Detail |
|---|---|
| WCAG contrast audit | AA (4.5:1), AA-large (3:1), AAA (7:1) |
| Alpha-aware compositing | Translucent `#RRGGBBAA` foregrounds composited before the ratio |
| Fix suggestions | Nearest OKLCH neighbour that passes the threshold |
| CVD simulation | Machado et al. 2009 matrices (protanopia, deuteranopia, tritanopia) |
| Grayscale luminance check | Relative-luminance gray to catch hue-only distinctions |
| Tailwind theme export | `theme.extend.colors` block or full `module.exports` config |
| Accessibility levels | universal / high-contrast / monochrome / CVD-specific palette remapping |
| Palette science | OKLab / OKLCH conversions, sRGB transfer functions, curated Apple base palette |
| Dependencies | stdlib only (+ Pillow for CVD image rendering) |

---

## Color science

Contrast ratios follow WCAG 2.x: relative luminance uses the 2.4-gamma transfer function. Perceptual adjustments use OKLab / OKLCH (Bjorn Ottosson, 2020). CVD matrices come from Machado, Oliveira, Fernandes (2009), IEEE TVCG.

---

## Part of sprezzature

| Repo | What it does |
|---|---|
| [sprezzature](https://github.com/warith-harchaoui/sprezzature) | Nine skill collection + web |
| [sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors) | This repo |
| [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures) | Data visualization |
| [sprezzature-local](https://github.com/warith-harchaoui/sprezzature-local) | Offline LLM runtime |

---

## Author

Warith Harchaoui -- [harchaoui.org/warith](https://harchaoui.org/warith)

License: BSD-3-Clause
