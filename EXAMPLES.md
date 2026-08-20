# Examples

## Audit a palette for WCAG contrast

```bash
python scripts/audit_contrast.py
```

Output (text):

```
Target ratio: 4.5

  ✓      brand-blue  on  surface-primary    ratio 4.55
  ✗      brand-red   on  surface-secondary  ratio 2.83

1 pass, 1 fail.
```

Exit code: `1` (a pair failed).

## Audit an external palette with fix suggestions

```bash
python scripts/audit_contrast.py --palette my-palette.json --target 7 --fix
```

`my-palette.json`:

```json
{
  "brand-red": { "DEFAULT": "#FF3B30", "dark": "#FF453A" },
  "surface-primary": { "DEFAULT": "#FFFFFF", "dark": "#000000" }
}
```

Each failing pair gets a suggested OKLCH-neighbour hex that clears the
target ratio:

```
  ✗   brand-red  on  surface-primary   ratio 4.02
      → suggest #D4000A  (ratio 7.02)
```

## JSON output for CI

```bash
python scripts/audit_contrast.py --palette my-palette.json --format json | jq '.pairs | map(select(.passes == false)) | length'
```

## Simulate color-blindness on a screenshot

```bash
# Three sibling PNGs: hero-protanopia.png, hero-deuteranopia.png, hero-tritanopia.png
python scripts/simulate_cvd.py hero.png

# One 2x2 mosaic for a design review, with a grayscale panel added
python scripts/simulate_cvd.py hero.png --grid --grayscale --out hero-cvd-review.png

# Only deuteranopia (the most common form)
python scripts/simulate_cvd.py hero.png --types deut
```

## Preview an accessibility level

```bash
python scripts/accessibility_levels.py --level deuteranopia
```

```
Red          #C75A2E  contrast-vs-white 3.1:1
Orange       #B8853A  contrast-vs-white 2.4:1
...
```

## Export the palette to Tailwind

```bash
# Just the brand: { ... } block, ready to paste into an existing config
python scripts/palette_to_tailwind.py

# Full tailwind.config.js, with derived dark-mode variants, written to disk
python scripts/palette_to_tailwind.py --emit config --with-dark --out tailwind.config.js

# The Okabe-Ito academic standard instead of the Apple-derived brand palette
python scripts/palette_to_tailwind.py --theme academic
```

## Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: contrast-audit
        name: WCAG contrast audit
        entry: python scripts/audit_contrast.py
        language: python
        files: tokens/colors\.json$
        args: ["--palette", "tokens/colors.json"]
```

## Library usage

```python
from scripts._colors import contrast_ratio_hex, meets_wcag, lighten, Color

# Direct function calls
ratio = contrast_ratio_hex("#007AFF", "#FFFFFF")           # -> 4.55
ok = meets_wcag("#007AFF", "#FFFFFF", level="AA", size="normal")  # -> True

# Or the Color wrapper, for a chainable API
blue = Color("#007AFF")
blue.lighten(0.15).hex        # -> a lighter blue, hue preserved
blue.meets_wcag("#FFFFFF")    # -> True
```
