# sprezzature-colors

Color accessibility and palette tooling for the [sprezzature](https://sprezzature.ai/) stack: contrast measured against WCAG (Web Content Accessibility Guidelines, the international rulebook that says, for example, how dark text must be against its background), colors adjusted in OKLCH (OK Lightness Chroma Hue, a color model in which raising lightness by 0.1 looks like the same brightening whatever the hue).

## How it works

![Flow diagram. At the top, a palette or an image feeds two lanes. The left lane audits: it composites any translucent colour, measures the WCAG contrast ratio of every pair, and simulates the three colour-vision deficiencies, returning a pass or fail per pair. The right lane makes: it holds hue and saturation fixed, walks the OKLCH lightness axis, and levels the whole palette, returning the nearest passing colour and a Tailwind configuration. Both meet in one outcome, a palette that survives a cheap screen, bright sunlight and a grayscale printer.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-colors/main/assets/how-it-works.svg)

## What problem this solves

Take a button with light-gray text on a white background. To most people it reads fine. To someone with low vision, or in bright sunlight on a phone screen, the same button can be unreadable: the text and the background are too close in brightness for the eye to separate them. The same gap shows up when a chart uses red for "down" and green for "up": about 1 man in 12 has a form of color vision deficiency (CVD, the inability to tell certain hues apart, most often red from green) and sees both bars as the same color.

This package gives four deterministic tools that catch these gaps before a design ships, rather than relying on someone happening to notice:

- **Contrast auditing.** Checks the (text, background) color pairs of a palette against the thresholds of the Web Content Accessibility Guidelines (WCAG, the standard body of rules for making web content usable by people with disabilities), and suggests a fix that stays visually close to the original color.
- **Color-blindness simulation.** Renders an image the way a person with protanopia, deuteranopia, or tritanopia (the three forms of red, green and blue color blindness) would see it, plus an optional grayscale version.
- **Accessibility levels.** Remaps the house palette to one of six levels (universal, high-contrast, monochrome, and one per deficiency) while keeping every color's name.
- **Tailwind palette export.** Writes the project's approved brand colors as a ready-to-use configuration block for Tailwind CSS (Cascading Style Sheets, the rules that set a web page's colors, fonts and spacing, such as "every heading in blue"), so every project in the stack draws from the same source instead of each one hand-copying hex codes.

The color arithmetic is written on the Python standard library. Pillow, a Python imaging library, reads and writes the image files of the simulation. Nothing here calls out to the network or an AI model.

---

## Install

```bash
pip install sprezzature-colors
```

That one line installs everything: the four tools, the command line (click), the image simulation (Pillow), the HTTP (HyperText Transfer Protocol, the request-and-reply exchange a browser makes each time it loads a page) API (Application Programming Interface, web addresses another program sends a request to and gets an answer from, served by FastAPI and uvicorn) and the MCP (Model Context Protocol, the protocol through which AI agents call tools in English) server (fastapi-mcp). There is no feature extra. The only extra is `[dev]`, the test toolchain (pytest, ruff, mypy), for a source checkout:

```bash
git clone https://github.com/warith-harchaoui/sprezzature-colors
cd sprezzature-colors
pip install -e ".[dev]"
```

## Five surfaces

| Surface | Entry point |
|---|---|
| Library | `import sprezzature_colors as sc` |
| Command line | `sprezzature-colors` (also `make-colors`), and one command per tool |
| HTTP API | `uvicorn sprezzature_colors.api:app`, or `docker compose up` (which serves the MCP endpoint too) |
| MCP server | `sprezzature-colors-mcp` |
| Skill | `sprezzature_colors/skill/` (`SKILL.md` and its references), shipped inside the package; `sprezzature-colors-skill --install` puts it where the agent reads |

The fifth surface is the skill: the folder an agent such as Claude Code or OpenCode reads to know when to reach for these tools and which command to run. It ships in the wheel, so `pip install` carries all five surfaces. [TRIGGERS.md](https://github.com/warith-harchaoui/sprezzature-colors/blob/main/TRIGGERS.md) says which tool answers which request, on every surface.

---

## Command line

### One front door, two spellings, four tools

```bash
sprezzature-colors --help             # the four tools, with what each does
sprezzature-colors tools              # which tools can run on this machine
sprezzature-colors contrast --fix     # run a tool through the front door
make-colors contrast --fix            # the same command, historical name
sprezzature-colors skill              # is the installed skill in step with this package?
```

`make-colors` and `sprezzature-colors` resolve to the same click group, so they cannot drift. Its sub-commands are `contrast`, `cvd`, `levels`, `palette-to-tailwind`, `tools` and `skill`. The group answers `-V` / `--version`, and prints shell-completion lines for bash and zsh at the end of `--help`.

Each tool is also its own command, which is what a script or a pre-commit hook should call:

| Command | Tool |
|---|---|
| `sprezzature-colors-contrast` | WCAG contrast audit of a palette |
| `sprezzature-colors-cvd` | Color-blindness simulation of an image |
| `sprezzature-colors-levels` | Palette remapped to an accessibility level |
| `sprezzature-colors-palette-to-tailwind` | Palette exported as Tailwind configuration |

These four parse their own flags; the front door hands every argument after the sub-command name to them unchanged. From a source checkout the same tools run as `python scripts/audit_contrast.py --fix`, one file per command.

### The skill

```bash
sprezzature-colors-skill                         # report: is the installed copy in step?
sprezzature-colors-skill --install               # copy it into ~/.claude/skills/sprezzature-colors
sprezzature-colors-skill --install --agent opencode   # ~/.opencode/skills instead
sprezzature-colors-skill --path                  # where pip put it
```

`sprezzature-colors skill` is the same command through the front door. By default it only reports, and exits 0 whether or not the copies differ. `--install` writes under your home directory; a previous copy is moved aside to `~/.claude/skills-superseded/`, outside the skills folder, so the agent does not read it as a second skill. From Python, `sprezzature_colors.skill_path()` returns the folder.

---

## Quick start

### Contrast audit

```bash
sprezzature-colors-contrast --fix
# Target ratio: 4.5
#
#   ✗             brand-blue  on         surface-primary   ratio 4.02
#       → suggest #006FF3  (ratio 4.61)
#   ✓             brand-blue  on    surface-primary-dark   ratio 5.23
#   ...
# 34 pass, 22 fail.
```

"Ratio" here is the WCAG contrast ratio: a number from 1 (identical brightness, unreadable) to 21 (pure black on pure white). 4.5 is the WCAG threshold for normal body text. Without `--palette`, the audit reads its built-in default palette. The exit code is 0 when every checked pair passes, 1 when a pair fails, and 2 when nothing could be checked: no pair in the palette, or a palette it cannot read.

By default only pairs that can appear together in a rendered theme are checked: light labels on light surfaces, dark labels on dark surfaces, brand accents on every surface. `--all-pairs` checks the full cross-product. Roles are recognised by prefix: `label-` and `brand-` are foregrounds (except `-light` tints), `surface-` is a background, and every other key is ignored.

With a custom palette in JSON (JavaScript Object Notation, a text format in which programs store data as named fields, like {"name": "Ada"}):

```bash
sprezzature-colors-contrast --palette my-palette.json --target 7 --fix
sprezzature-colors-contrast --palette my-palette.json --format json
```

### Color-blindness simulation

```bash
# Three sibling files: hero-protanopia.png, hero-deuteranopia.png, hero-tritanopia.png
sprezzature-colors-cvd hero.png

# Every file written is a PNG and named .png, whatever the source: hero.jpg gives hero-protanopia.png
sprezzature-colors-cvd hero.jpg

# One mosaic for design review: the original and each simulation, two per row
sprezzature-colors-cvd hero.png --grid --out hero-cvd-grid.png

# Only deuteranopia, plus a grayscale version
sprezzature-colors-cvd hero.png --types deut --grayscale
```

`--types` takes full names or the shorthands `prot`, `deut` and `trit`, comma-separated. In per-type mode `--out` is a directory; with `--grid` it is a file. Missing directories are created.

### Palette to Tailwind

```bash
# Copy-paste block for an existing config
sprezzature-colors-palette-to-tailwind

# Full tailwind.config.js with derived dark variants
sprezzature-colors-palette-to-tailwind --emit config --with-dark --out tailwind.config.js

# The Okabe-Ito color-blind-safe set instead of the brand palette
sprezzature-colors-palette-to-tailwind --theme academic
```

`--include-neutrals` adds the Brown, Black, Gray and White tokens, which are left out by default.

### Accessibility levels

```bash
# Preview the house palette at the high-contrast level (7:1, WCAG AAA)
sprezzature-colors-levels --level high-contrast

# Available levels: universal (default), high-contrast, monochrome,
#                   deuteranopia, protanopia, tritanopia
```

Each line prints the color name, its hex at that level, and its contrast against white. `--csv` reads another palette file with the same columns; a file it cannot read, or without those columns, exits 2.

---

## Library usage

```python
import sprezzature_colors as sc

# WCAG contrast ratio
sc.contrast_ratio_hex("#007AFF", "#FFFFFF")          # -> 4.02 (rounded)

# WCAG tests: fails AA for body text, passes for large text
sc.meets_wcag("#007AFF", "#FFFFFF", level="AA", size="normal")  # -> False
sc.meets_wcag("#007AFF", "#FFFFFF", level="AA", size="large")   # -> True

# Perceptual lighten / darken on the OKLCH lightness axis, hue preserved.
# OKLCH is a color model built so that a fixed numeric step in lightness
# matches what a human eye perceives as an equal step in brightness, unlike
# raw RGB.
sc.lighten("#007AFF", 0.15)   # -> "#47ABFF"
sc.darken("#007AFF", 0.10)    # -> "#0059DC"

# CVD pixel simulation (8-bit sRGB in, 8-bit sRGB out)
sc.simulate_pixel((255, 0, 0), sc.CVD_MATRICES["protanopia"])  # -> (109, 95, 0)

# The house palette and its color psychology
sc.palette_names()            # -> ['Red', 'Orange', ..., 'White'], 12 names
sc.name_to_hex("Blue")        # -> "#007AFF"
sc.concept_search("trust")    # -> ['#007AFF']
sc.psychology_for("Blue")     # -> {'positive': ['Trust', ...], 'negative': [...]}
```

`sprezzature_colors.__all__` lists the whole public surface: contrast and WCAG, hex parsing and alpha compositing, OKLab / OKLCH conversions, palette lookup, CVD simulation, color psychology, and `skill_path()`, the folder of the skill the package ships.

---

## HTTP API

FastAPI is a Python web framework for HTTP APIs. The app in `sprezzature_colors.api` serves the library over HTTP, so a design system in TypeScript or a CI (continuous integration, a server that reruns all the tests every time code is pushed and flags any that fail) job in another language can run the same checks.

```bash
uvicorn sprezzature_colors.api:app --host 0.0.0.0 --port 8000
curl -X POST localhost:8000/v1/contrast \
     -H 'content-type: application/json' \
     -d '{"pairs":[{"foreground":"#595959","background":"#ffffff"}]}'
# {"results":[{"foreground":"#595959","background":"#ffffff","ratio":7.0,
#   "level":"AA","size":"normal","required":4.5,"passes":true}]}
```

| Route | `operation_id` | Answers |
|---|---|---|
| `GET /health` | `health` | Is the server up |
| `GET /v1/palette` | `get_palette` | The house palette, one row per color |
| `POST /v1/contrast` | `check_contrast` | Ratio and WCAG verdict per pair (`level` AA or AAA (the standard and enhanced WCAG levels: a contrast of 4.5:1 and 7:1 for body text), `size` normal or large) |
| `POST /v1/cvd` | `simulate_color_blindness` | The hex each deficiency perceives, per color |
| `POST /v1/adjust` | `adjust_lightness` | Lighter (`amount` > 0) or darker (`amount` < 0) colors, in OKLab |
| `GET /v1/psychology/{color}` | `get_color_psychology` | Positive and negative associations of a palette color |
| `GET /v1/concepts?keyword=` | `search_concepts` | Palette hex codes associated with a concept |

Every route that takes a color accepts a hex code or a palette name such as `"Blue"`; anything else is a 400. Interactive documentation is at `/docs`.

### Docker

```bash
docker compose up -d
curl -s localhost:8000/health
docker compose run --rm api sprezzature-colors-contrast --target 7
docker compose run --rm api sprezzature-colors-cvd /work/hero.png --grid
```

The image runs `sprezzature-colors-mcp --host 0.0.0.0 --port 8000`, so one container answers both the HTTP routes (`/health`, `/v1/...`) and the MCP endpoint (`/mcp`) on port 8000. The compose file mounts `./work` on `/work`, writable, because the simulation writes its files next to the source image.

## MCP server

```bash
sprezzature-colors-mcp                       # 127.0.0.1:8000
sprezzature-colors-mcp --host 0.0.0.0 --port 9000
```

The server wraps the same FastAPI app with fastapi-mcp and mounts the MCP endpoint at `/mcp`, beside the HTTP routes. Each route's `operation_id` is the MCP tool name, so the seven tools are `health`, `get_palette`, `check_contrast`, `simulate_color_blindness`, `adjust_lightness`, `get_color_psychology` and `search_concepts`. `SPREZZATURE_COLORS_HOST` and `SPREZZATURE_COLORS_PORT` set the defaults. The Docker image runs this same server, so `docker compose up` gives you `/mcp` as well.

---

## Features

| Feature | Detail |
|---|---|
| WCAG contrast audit | AA (4.5:1), AA-large (3:1), AAA (7:1) |
| Alpha-aware compositing | Translucent `#RRGGBBAA` foregrounds composited before the ratio |
| Fix suggestions | Nearest OKLCH neighbour that passes the threshold |
| CVD simulation | MACHADO et al. 2009 matrices (protanopia, deuteranopia, tritanopia) |
| Grayscale luminance check | Relative-luminance gray to catch hue-only distinctions |
| Tailwind theme export | `brand` block or full `module.exports` config, corporate or Okabe-Ito |
| Accessibility levels | universal / high-contrast / monochrome / CVD-specific palette remapping |
| Palette science | OKLab / OKLCH conversions, sRGB transfer functions, curated Apple base palette |
| Color psychology | Emotion, concepts and associations for each of the 12 palette colors |
| Dependencies | One install: click, FastAPI, uvicorn, Pillow, fastapi-mcp, mcp |

---

## The one channel that survives

Four tools, one idea underneath them.

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
is ranked by how bright it looks *to that viewer*, under the MACHADO matrices,
and the lightnesses are then spread across a legible band. Hue and saturation
are left alone. That spreads the categories for that reader without proving
them apart: the 3:1 floor against white and the gamut can bring two back
together, as Yellow and White under tritanopia on the house palette, which is
why shape and label stay on the job.

That is also why the deficiency palettes are options rather than the default.
No single set of colours is best for protanopia, deuteranopia and tritanopia
at once: improving the spacing for one eye closes it for another. The default
(`universal`) is the palette that is already separated by lightness for
everybody, with shape, label and position carrying the rest.

---

## Color science

Contrast ratios follow WCAG 2.x: relative luminance (how bright a color looks to the eye, not just its raw RGB (red, green, blue, the three lights a screen mixes into every color: #FF0000 is pure red) numbers) uses the 2.4-gamma transfer function that the standard specifies. Perceptual adjustments use OKLab / OKLCH, a color model designed by Björn OTTOSSON (2020) precisely so that "move the lightness value by X" matches how much brighter the color actually looks, which plain RGB does not guarantee. Color-blindness simulation matrices come from MACHADO, OLIVEIRA, and FERNANDES (2009, IEEE (Institute of Electrical and Electronics Engineers, the world's largest engineering society, which publishes this journal) Transactions on Visualization and Computer Graphics), a widely cited paper that measured how each type of color blindness transforms a color and published the transformation as a matrix of numbers, which is exactly what `CVD_MATRICES` stores, at full severity.

---

## Part of sprezzature

| Repo | What it does |
|---|---|
| [sprezzature](https://github.com/warith-harchaoui/sprezzature) | The hub: ten bricks, their skills, and the website |
| [sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors) | This repo |
| [sprezzature-accessibility](https://github.com/warith-harchaoui/sprezzature-accessibility) | Static HTML accessibility lint |
| [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures) | Data visualization; applies the accessibility levels |
| [sprezzature-ui](https://github.com/warith-harchaoui/sprezzature-ui) | UI (user interface, the buttons, menus and forms people click) components; consumes the Tailwind export |

---

## Author

Warith HARCHAOUI, [deraison.ai](https://deraison.ai)

License: Berkeley Software Distribution, three-clause version (BSD-3-Clause, a permissive licence: anyone may use, change and resell the code if they keep the copyright notice)
