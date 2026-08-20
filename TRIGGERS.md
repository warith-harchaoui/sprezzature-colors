# Triggers

Natural-language phrases that invoke the sprezzature-colors skill.

## Direct invocations

- "WCAG check" / "contrast audit"
- "Is my palette accessible?"
- "Colorblind preview" / "deuteranope" / "CVD"
- "Lighten this color" / "darken this color"
- "OKLCH"
- "Apple palette" / "emotion color" / "concept color"
- "Palette to tailwind"
- "Regenerate brand tokens"
- "Tailwind config from palette"
- "Brand colors"
- "Accessible color pair"
- "Color-blind safe"
- "Protanopia" / "tritanopia"
- "Generate palette"

## Intent-based phrases

- "Does this color pair meet WCAG AA?"
- "Suggest a fix for this contrast failure"
- "What does this screenshot look like for a colorblind user?"
- "Give me a Tailwind theme from our brand colors"
- "What emotion does this color signal?"
- "Preview our palette at high contrast"
- "Which colors in this palette collapse for deuteranopia?"

## File patterns

Palette JSON files, `tailwind.config.js`, and image files (`*.png`,
`*.jpg`) routed to this skill when a color-accessibility or
palette-export concern is expressed.

## Related scripts

- `scripts/audit_contrast.py` — WCAG contrast audit + OKLCH fix suggester
- `scripts/simulate_cvd.py` — color-vision-deficiency image simulation
- `scripts/accessibility_levels.py` — palette remapped to an accessibility level
- `scripts/palette_to_tailwind.py` — palette CSV to Tailwind config
- `scripts/_colors.py` — shared color math and palette accessors
- `scripts/_argparse.py` — shared parser factory
