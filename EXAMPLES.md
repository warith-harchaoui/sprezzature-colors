# Examples

Every command below is installed by `pip install sprezzature-colors`. The
contrast checks follow WCAG (Web Content Accessibility Guidelines, the
international rules for readable web content); a palette file is JSON
(JavaScript Object Notation, a text format of named fields); the fixes move
along the lightness axis of OKLCH (OK Lightness Chroma Hue, a colour model in
which equal steps look equally different to the eye).

## Audit a palette for WCAG contrast

```bash
sprezzature-colors-contrast
```

Output (text, abridged), on the built-in default palette:

```
Target ratio: 4.5

  ✗             brand-blue  on         surface-primary   ratio 4.02
  ✓             brand-blue  on    surface-primary-dark   ratio 5.23
  ✗             brand-blue  on       surface-secondary   ratio 3.60
  ...

34 pass, 22 fail.
```

Exit code: `1` (at least one pair failed). `0` means every checked pair passed.

## Audit an external palette with fix suggestions

```bash
sprezzature-colors-contrast --palette my-palette.json --target 7 --fix
```

`my-palette.json`:

```json
{
  "brand-red": { "DEFAULT": "#FF383C", "dark": "#FF4245" },
  "surface-primary": { "DEFAULT": "#FFFFFF", "dark": "#000000" }
}
```

Variants other than `DEFAULT` become suffixed roles (`brand-red-dark`,
`surface-primary-dark`). Each failing pair gets a suggested OKLCH-neighbour
hex that clears the target ratio:

```
Target ratio: 7.0

  ✗              brand-red  on         surface-primary   ratio 3.57
      → suggest #B40000  (ratio 7.14)
  ✗              brand-red  on    surface-primary-dark   ratio 5.88
      → suggest #FF5F5A  (ratio 7.04)
  ✗         brand-red-dark  on    surface-primary-dark   ratio 6.12
      → suggest #FF5F5D  (ratio 7.05)

0 pass, 3 fail.
```

`brand-red-dark` is not checked on `surface-primary`: a dark-theme colour is
only paired with dark surfaces. Pass `--all-pairs` for the full cross-product.

Keys must start with `label-`, `brand-` or `surface-`. Any other key is
ignored, and a palette with no matching key is reported on standard error
with exit code `2`: nothing was checked, so nothing passed. A file that is
missing, not JSON, or holds a colour that is not hex exits `2` the same way.

## JSON output for continuous integration

A continuous integration job, the server that reruns every check each time code is pushed, reads the exit code and, with `--format json`, the pairs:

```bash
sprezzature-colors-contrast --palette my-palette.json --format json | jq '.pairs | map(select(.passes == false)) | length'
```

Each entry of `pairs` carries `fg` and `bg` (`role`, `hex`), `ratio`,
`passes`, and `suggested` (`hex`, `ratio`) when `--fix` found one.

## Simulate color-blindness on a screenshot

```bash
# Three sibling files: hero-protanopia.png, hero-deuteranopia.png, hero-tritanopia.png
# (always .png, the bytes are PNG: hero.jpg gives hero-protanopia.png too)
sprezzature-colors-cvd hero.png

# One mosaic for a design review, with a grayscale panel added
sprezzature-colors-cvd hero.png --grid --grayscale --out hero-cvd-review.png

# Only deuteranopia (the most common form)
sprezzature-colors-cvd hero.png --types deut
```

## Preview an accessibility level

```bash
sprezzature-colors-levels --level deuteranopia
sprezzature-colors-levels --level deuteranopia --theme print   # or academic
```

```
Red          #DF001F  contrast-vs-white 5.1:1
Orange       #E67600  contrast-vs-white 3.0:1
Yellow       #BC8A00  contrast-vs-white 3.1:1
...
```

## Export the palette to Tailwind

```bash
# Just the brand: { ... } block, ready to paste into an existing config
sprezzature-colors-palette-to-tailwind

# Full tailwind.config.js, with derived dark-mode variants, written to disk
sprezzature-colors-palette-to-tailwind --emit config --with-dark --out tailwind.config.js

# The academic palette (Okabe and Ito, readable with colour blindness) or the
# print palette instead of the corporate one (Apple system colours)
sprezzature-colors-palette-to-tailwind --theme academic
sprezzature-colors-palette-to-tailwind --theme print
```

## Ask the web server

The app answers over HTTP (HyperText Transfer Protocol, the request-and-reply exchange a browser makes for each page), as an API (Application Programming Interface, web addresses another program sends a request to), the questions that need no file:

```bash
uvicorn sprezzature_colors.api:app --port 8000 &
curl -s -X POST localhost:8000/v1/cvd \
     -H 'content-type: application/json' -d '{"colors":["Red"]}'
# {"results":[{"input":"#FF383C","simulated":{"protanopia":"#776C3A",
#   "deuteranopia":"#A89733","tritanopia":"#FF003C"}}]}
curl -s "localhost:8000/v1/concepts?keyword=trust"
# {"keyword":"trust","colors":["#0088FF"]}
```

## Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: contrast-audit
        name: WCAG contrast audit
        entry: sprezzature-colors-contrast
        language: python
        additional_dependencies: [sprezzature-colors]
        files: tokens/colors\.json$
        pass_filenames: false
        args: ["--palette", "tokens/colors.json"]
```

## Install the skill for an agent

```bash
sprezzature-colors-skill                    # is the copy in ~/.claude/skills in step?
# sprezzature-colors: differs: SKILL.md (/home/you/.claude/skills/sprezzature-colors)
# Pass --install to copy the shipped skill there.

sprezzature-colors-skill --install          # copy it; any previous copy goes to ~/.claude/skills-superseded/
sprezzature-colors-skill --install --agent opencode   # ~/.opencode/skills instead
sprezzature-colors skill --path             # the same command through the front door: where pip put it
```

The skill is the fifth surface, beside the library, the command line, the
HTTP API and the MCP (Model Context Protocol, the protocol through which AI
agents call tools in English) server. It ships inside the package, in
`sprezzature_colors/skill/`, and `sprezzature_colors.skill_path()` returns
that folder.

## Library usage

```python
import sprezzature_colors as sc

ratio = sc.contrast_ratio_hex("#0088FF", "#FFFFFF")                # -> 3.52 (rounded)
ok = sc.meets_wcag("#0088FF", "#FFFFFF", level="AA", size="large")  # -> True
sc.lighten("#0088FF", 0.15)                                          # -> "#4CB9FF"
sc.print_palette()["Blue"]                                           # -> "#437DB5"
```

The `Color` wrapper gives a chainable form of the same functions. It is not
re-exported by `sprezzature_colors`; import it from the module that holds the
implementation:

```python
from sprezzature_colors_scripts._colors import Color

blue = Color("#0088FF")
blue.lighten(0.15).hex        # -> "#4CB9FF", hue preserved
blue.contrast_with("#FFFFFF") # -> 3.52 (rounded)
blue.meets_wcag("#FFFFFF")    # -> False: AA body text needs 4.5
Color.from_name("Blue").hex   # -> "#0088FF"
```
