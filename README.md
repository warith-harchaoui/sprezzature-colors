# sprezzature-colors

Color accessibility and palette tooling for the [sprezzature](https://sprezzature.ai/) stack.

## What problem this solves

Take a button with light-gray text on a white background. To most people it reads fine. To someone with low vision, or in bright sunlight on a phone screen, the same button can be unreadable: the text and the background are too close in brightness for the eye to separate them. The same gap shows up when a chart uses red for "down" and green for "up": about 1 man in 12 has a form of color vision deficiency (CVD, the inability to tell certain hues apart, most often red from green) and sees both bars as the same color.

This package gives three deterministic, stdlib-only tools that catch these gaps before a design ships, rather than relying on someone happening to notice:

- **Contrast auditing.** Checks every (text, background) color pair in a palette against the accessibility thresholds published by the Web Content Accessibility Guidelines (WCAG, the standard body of rules for making web content usable by people with disabilities), and suggests a fix that stays visually close to the original color.
- **Color-blindness simulation.** Renders an image the way a person with protanopia, deuteranopia, or tritanopia (the three common forms of red/green/blue color blindness) would actually see it, so a design can be checked before it ships rather than after a complaint.
- **Tailwind palette export.** Writes the project's approved brand colors as a ready-to-use Tailwind CSS configuration block, so every project in the stack draws from the same source instead of each one hand-copying hex codes.

All three run on pure stdlib (the color-blindness simulation additionally needs Pillow, a Python imaging library, to read and write image files). Nothing here calls out to the network or an AI model.

---

## How it works

![Flow diagram. At the top, a palette or an image feeds two lanes. The left lane audits: it composites any translucent colour, measures the WCAG contrast ratio of every pair, and simulates the three colour-vision deficiencies, returning a pass or fail per pair. The right lane makes: it holds hue and saturation fixed, walks the OKLCH lightness axis, and levels the whole palette, returning the nearest passing colour and a Tailwind configuration. Both meet in one outcome, a palette that survives a cheap screen, bright sunlight and a grayscale printer.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-colors/main/assets/how-it-works.svg)

## Install

```bash
pip install sprezzature-colors
```

For color-blindness image simulation:

```bash
pip install sprezzature-colors[cvd]       # + Pillow
pip install "sprezzature-colors[api,mcp]" # + the HTTP and agent surfaces
```

That the audit itself is **standard library only** is the point of this
package, and the reason it is cheap enough to put in a pre-commit hook. The
one base dependency is click, for the command line. Every heavier thing is an
extra, named after the tool that needs it, so an install says what it is
for.

### One front door, two spellings, four tools

```bash
make-colors contrast                  # the historical name
sprezzature-colors contrast           # the suite-wide name
sprezzature-colors tools              # which tools can run on this machine
make-colors --help                    # the four tools, with what each does
```

Both names resolve to the same callable, so they cannot drift. There were two
parsers until 2026-10-25 — an argparse one and a click one sharing a table —
and every sub-command had to be written twice; click is now the only one, and
a base dependency rather than an extra, because with argparse gone no parser
ships with Python. Each tool is also still its own
command — `sprezzature-colors-contrast`, `-cvd`, `-levels`,
`-palette-to-tailwind` — which is what a script should call. The examples
below use those. From a source checkout (`git clone` + `pip install -e
".[dev,cvd]"`) the same thing reads `python scripts/audit_contrast.py --fix`,
one file per command.

---

## Quick start

### Contrast audit

```bash
sprezzature-colors-contrast
# Target ratio: 4.5
#
#   ✓      brand-blue  on  surface-primary   ratio 4.55
#   ✗      brand-red   on  surface-secondary  ratio 2.83
#       -> suggest #D4000A  (ratio 4.51)
```

"Ratio" here is the WCAG contrast ratio: a number from 1 (identical brightness, unreadable) to 21 (pure black on pure white). 4.5 is the WCAG threshold for normal body text.

With a custom palette JSON:

```bash
sprezzature-colors-contrast --palette my-palette.json --target 7 --fix
sprezzature-colors-contrast --palette my-palette.json --format json
```

### Color-blindness simulation

```bash
# Three sibling PNG files
sprezzature-colors-cvd hero.png

# 2x2 mosaic for design review
sprezzature-colors-cvd hero.png --grid --out hero-cvd-grid.png

# Only deuteranopia + grayscale
sprezzature-colors-cvd hero.png --types deut --grayscale
```

### Palette to Tailwind

```bash
# Copy-paste block for an existing config
sprezzature-colors-palette-to-tailwind

# Full tailwind.config.js with derived dark variants
sprezzature-colors-palette-to-tailwind --emit config --with-dark --out tailwind.config.js
```

### Accessibility levels

```bash
# Preview the canonical palette at AAA high-contrast
sprezzature-colors-levels --level high-contrast

# Available levels: universal (default), high-contrast, monochrome,
#                   deuteranopia, protanopia, tritanopia
```

---

## Library usage

```python
from scripts._colors import (
    contrast_ratio_hex,
    meets_wcag,
    lighten,
    darken,
    simulate_pixel,
    CVD_MATRICES,
)

# WCAG contrast ratio
ratio = contrast_ratio_hex("#007AFF", "#FFFFFF")  # -> 4.55

# WCAG AA test
ok = meets_wcag("#007AFF", "#FFFFFF", level="AA", size="normal")  # -> True

# Perceptual lighten/darken (OKLCH axis, hue preserved): OKLCH is a color
# model built so that a fixed numeric step in lightness matches what a human
# eye perceives as an equal step in brightness, unlike raw RGB where the same
# numeric step can look barely different in one area and drastic in another.
lighter = lighten("#007AFF", 0.15)  # -> "#5FA8FF" (approx.)
darker = darken("#007AFF", 0.10)  # -> "#005DC2" (approx.)

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

## The one channel that survives

Three tools, one idea underneath them.

A colour has three parts you can move: hue, how saturated it is, and how light
it is. Red-green colour blindness takes hue away. Grayscale printing takes
saturation away. **Lightness is the only one that no deficiency, no printer
and no hostile screen removes.** So lightness is what every tool here works
on.

The contrast audit does not propose a different colour. It holds your hue and
your saturation fixed, walks the lightness axis in hundredth steps, and stops
at the nearest value that clears the threshold. Your brand blue stays your
brand blue; it gets lighter or darker until it is legible.

The deficiency-specific palettes do the same thing one level up. Each colour
is ranked by how bright it looks *to that viewer*, under the Machado matrices,
and the lightnesses are then spread across a legible band. Hue and saturation
are left alone. For that reader, every category separates.

That is also why the deficiency palettes are options rather than the default.
No single set of colours is best for protanopia, deuteranopia and tritanopia
at once: improving the spacing for one eye closes it for another. The default
(`universal`) is the palette that is already separated by lightness for
everybody, with shape, label and position carrying the rest.

---

## Color science

Contrast ratios follow WCAG 2.x: relative luminance (how bright a color looks to the eye, not just its raw RGB numbers) uses the 2.4-gamma transfer function that the standard specifies. Perceptual adjustments use OKLab / OKLCH, a color model designed by Björn Ottosson (2020) precisely so that "move the lightness value by X" matches how much brighter the color actually looks, which plain RGB does not guarantee. Color-blindness simulation matrices come from Machado, Oliveira, and Fernandes (2009, IEEE Transactions on Visualization and Computer Graphics), a widely cited paper that measured how each type of color blindness transforms a color and published the transformation as a matrix of numbers, which is exactly what `CVD_MATRICES` stores.

---

## Part of sprezzature

| Repo | What it does |
|---|---|
| [sprezzature](https://github.com/warith-harchaoui/sprezzature) | Ten-package collection + web |
| [sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors) | This repo |
| [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures) | Data visualization |
| [best-engine-ai-helper](https://github.com/warith-harchaoui/best-engine-ai-helper) | Offline LLM/VLM runtime |

---

## Author

Warith HARCHAOUI, [deraison.ai](https://deraison.ai)

License: BSD-3-Clause
