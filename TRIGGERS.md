# Triggers

What a user might say about colour, and what to call when they say it.

This file is written for an agent: a Claude Code or OpenCode skill, an MCP
host (MCP is the Model Context Protocol, the standard an assistant uses to
call tools), anything choosing a tool on someone's behalf.

---

## The generalisation, stated once

> **Any sentence where a colour is being chosen, varied, judged or exported
> is a trigger.** Do not wait for the word "WCAG", "contrast" or
> "accessibility". "What colour should this button be", "does this look OK
> on dark", "pick something that feels trustworthy", « quelle couleur pour ce
> fond », « on change le bleu ? »: all of it routes here, because all of it
> ends with a hex code that someone will ship.

Route on the domain's vocabulary, which is closed, and not on phrasings,
which are not. A request belongs here when it names one of these objects:

- **a colour**: a hex code (`#RRGGBB`, `#RRGGBBAA`), a palette name (`Red`,
  `Orange`, `Yellow`, `Green`, `Turquoise`, `Blue`, `Purple`, `Pink`,
  `Brown`, `Black`, `Gray`, `White`), or a role (`label-…`, `brand-…`,
  `surface-…`);
- **a pair**: foreground and background, text on a surface;
- **a measure**: contrast ratio, WCAG level (AA, AAA), text size (normal,
  large), lightness (OKLab, OKLCH);
- **a viewer**: colour vision deficiency (CVD), protanopia, deuteranopia,
  tritanopia, grayscale, low vision;
- **a palette artefact**: the palette CSV, a palette JSON, a Tailwind
  config, an accessibility level;
- **a meaning**: an emotion or a concept a colour carries.

Colour requests then come in seven shapes. The set is closed.

| The user is… | Call | Typical phrasings (EN / FR) |
|---|---|---|
| **judging a pair**: will this text be readable on this background | `check_contrast`, or `sprezzature-colors-contrast` for a whole palette file | "does this pass WCAG", "contrast audit", "is my palette accessible", « est-ce lisible », « ça passe en AA ? » |
| **judging a distinction**: will colour-blind readers tell these apart | `simulate_color_blindness` for colours, `sprezzature-colors-cvd` for an image | "colourblind preview", "deuteranopia", "is this CVD-safe", « daltonisme », « et pour un daltonien ? » |
| **choosing a colour**: needs one, by name or by feeling | `get_palette`, `search_concepts` | "our brand colours", "the palette", "something that says trust", « une couleur qui inspire confiance » |
| **varying a colour**: a lighter, darker or hover twin | `adjust_lightness` | "lighter version", "hover state", "darken it slightly", « éclaircir », « une variante plus sombre » |
| **interpreting a colour**: what does this one connote | `get_color_psychology` | "what does blue convey", "is red wrong here", « que signifie cette couleur » |
| **levelling a palette**: the same names, for one kind of viewer | `sprezzature-colors-levels` | "high-contrast palette", "a palette for deuteranopes", "monochrome version", « palette fort contraste » |
| **exporting a palette**: tokens for a build | `sprezzature-colors-palette-to-tailwind` | "palette to Tailwind", "generate tailwind.config.js", "Okabe-Ito tokens", « exporter la palette » |

The last two, and the image half of the second, are **file** jobs: they read
or write a file, so they live on the command line and not among the MCP
tools.

---

## Every tool, and the request it answers

| Tool | Answers | Takes | Returns |
|---|---|---|---|
| `health` | "is the colour server up" (diagnosis only) | nothing | `{"status": "ok"}` |
| `get_palette` | "what are our colours" | nothing | every palette row: `Base` name, `Hexcode`, `LightHex`, `Emotion`, `Concepts`, positive and negative psychology |
| `check_contrast` | "is this pair readable" | `pairs`: `foreground`, `background`, `level` (AA or AAA), `size` (normal or large) | per pair: `ratio`, `required`, `passes` |
| `simulate_color_blindness` | "what does a colour-blind viewer see" | `colors`, optional `kinds` | per colour: the perceived hex for each deficiency |
| `adjust_lightness` | "a lighter or darker version" | `colors`, `amount` from -1 to 1 (default 0.1) | per colour: the adjusted hex |
| `get_color_psychology` | "what does this colour connote" | `color` (hex or palette name) | positive and negative associations, plus the emotion table; 404 when the colour has no entry |
| `search_concepts` | "which colour says this" | `keyword` | palette hex codes associated with the concept, possibly none |
| `sprezzature-colors-contrast` | "audit this palette file" | `--palette`, `--target`, `--fix`, `--format`, `--all-pairs` | one line per pair; exit 1 on any failure |
| `sprezzature-colors-cvd` | "show me this screenshot as a colour-blind viewer sees it" | an image, `--types`, `--grid`, `--grayscale`, `--out` | PNG files beside the source, always named `.png` |
| `sprezzature-colors-levels` | "the palette at this accessibility level" | `--level`, `--csv` | name, hex and contrast against white, per colour |
| `sprezzature-colors-palette-to-tailwind` | "the palette as Tailwind tokens" | `--emit`, `--with-dark`, `--include-neutrals`, `--theme`, `--out` | a `brand` block or a full `tailwind.config.js` |
| `sprezzature-colors tools` | "which colour tools run on this machine" | nothing | one line per tool, ready or not |

Every MCP tool that takes a colour accepts a hex code or a palette name.

---

## What to call, on every surface

The MCP tool name is the route's `operation_id`. The front door
`sprezzature-colors` (also spelled `make-colors`) runs each CLI tool as a
sub-command: `sprezzature-colors contrast` is `sprezzature-colors-contrast`.

| Job | Library (`import sprezzature_colors as sc`) | CLI | HTTP route | MCP tool (`operation_id`) |
|---|---|---|---|---|
| Server liveness | — | — | `GET /health` | `health` |
| The house palette | `sc.load_palette()`, `sc.palette_names()`, `sc.name_to_hex()` | — | `GET /v1/palette` | `get_palette` |
| WCAG contrast | `sc.contrast_ratio_hex()`, `sc.meets_wcag()` | `sprezzature-colors-contrast` (`contrast`) | `POST /v1/contrast` | `check_contrast` |
| Colour-vision simulation | `sc.simulate_pixel()`, `sc.CVD_MATRICES` | `sprezzature-colors-cvd` (`cvd`), on images | `POST /v1/cvd`, on colours | `simulate_color_blindness` |
| Perceptual lighten / darken | `sc.lighten()`, `sc.darken()` | — | `POST /v1/adjust` | `adjust_lightness` |
| Colour → connotations | `sc.psychology_for()`, `sc.emotions()` | — | `GET /v1/psychology/{color}` | `get_color_psychology` |
| Concept → colours | `sc.concept_search()`, `sc.emotion_to_hex()` | — | `GET /v1/concepts?keyword=` | `search_concepts` |
| Palette remapped to an accessibility level | — | `sprezzature-colors-levels` (`levels`) | — | *(not an MCP tool)* |
| Palette CSV → Tailwind config | `sc.apple_palette()`, `sc.academic_palette()` (data only) | `sprezzature-colors-palette-to-tailwind` (`palette-to-tailwind`) | — | *(not an MCP tool)* |
| Which tools can run here | — | `sprezzature-colors tools` | — | *(not an MCP tool)* |

The server is `sprezzature-colors-mcp` (default `127.0.0.1:8000`, endpoint
`/mcp`). The skill is `SKILL.md` in the hub, under
`sprezzature/sprezzature-colors/`.

The gaps are deliberate. The two CLI-only jobs write project files from a
palette CSV; an HTTP tool that returns a config an agent must then write by
hand is worse than the command that writes it. And `simulate_color_blindness`
takes colours, while the CLI takes a whole **image**: for "what does this
screenshot look like to a colour-blind user", the command is the answer, not
the tool.

---

## Three contracts an agent must not break

**1. Never invent a hex.** Call `get_palette` and use the project's own. Every
tool here accepts a palette *name* wherever it accepts a hex, so once you have
the palette you can talk in names and stop moving digits around.

**2. Contrast and colour-vision are different questions.** Passing
`check_contrast` does not mean passing `simulate_color_blindness`: red and
green can contrast perfectly against their background and still converge into
the same colour for a deuteranope. If colour is the **only** thing separating
two things, run both.

**3. Do not hand-tune a lighter or darker shade.** `adjust_lightness` moves
along the OKLab lightness axis, where one step looks like one step whatever
the hue. Nudging RGB digits washes yellows out while blues barely move, which
is the usual reason a hand-built palette looks uneven.

**Key names matter in the audit.** `sprezzature-colors-contrast` only checks
keys named `label-…` or `brand-…` against keys named `surface-…`. A palette
with other key names yields no pair and exits 2 with a message on standard
error. Rename the keys rather than reading exit 2 as a pass or a fail.

---

## Not this brick

- Structural defects in HTML (missing alt, unlabelled inputs, colour-only
  state in markup): `sprezzature-accessibility`.
- The colours of a chart being drawn: `sprezzature-figures`.

## File patterns

Palette CSV / JSON files, `tailwind.config.js`, and images (`*.png`, `*.jpg`)
route here when a colour-accessibility or palette-export concern is expressed.
