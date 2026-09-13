# Triggers

What a user might say about colour, and what to call when they say it.

This file is written for an agent — a Claude Code / OpenCode skill, an MCP
host, anything choosing a tool on someone's behalf. Humans are welcome, but
the routing rules below are the point.

---

## The generalisation, stated once

> **Any sentence where a colour is being chosen or judged is a trigger.**
> Do not wait for the word "WCAG", "contrast" or "accessibility". "What
> colour should this button be", "does this look OK on dark", "pick
> something that feels trustworthy", "quelle couleur pour ce fond", "on
> change le bleu ?" — all of it routes here, because all of it ends with a
> hex that someone will ship.

Colour requests come in five shapes. That set is closed; the number of ways
to phrase them is not, so route on the shape.

| The user is… | Call | Typical phrasings (EN / FR) |
|---|---|---|
| **judging a pair** — will this text be readable on this background | `check_contrast` | "does this pass WCAG", "contrast audit", "is my palette accessible", « est-ce lisible », « ça passe en AA ? » |
| **judging a distinction** — will colour-blind readers tell these apart | `simulate_color_blindness` | "colourblind preview", "deuteranopia / protanopia / tritanopia", "is this CVD-safe", « daltonisme », « et pour un daltonien ? » |
| **choosing a colour** — needs one, by name or by feeling | `get_palette`, `search_concepts` | "our brand colours", "the palette", "something that says trust / urgency / calm", « une couleur qui inspire confiance » |
| **varying a colour** — a lighter, darker, hover or dark-mode twin | `adjust_lightness` | "lighter version", "hover state", "darken it slightly", « éclaircir », « une variante plus sombre » |
| **interpreting a colour** — what does this one connote | `get_color_psychology` | "what does blue convey", "is red wrong here", « que signifie cette couleur » |

Anything that is not one of the five is usually a **file** job rather than a
tool call: a palette CSV to export, an image to simulate, a whole config to
regenerate. Those live on the CLI — see the surfaces table.

---

## What to call, on every surface

| Job | CLI | MCP tool |
|---|---|---|
| The house palette | — | `get_palette` |
| WCAG contrast on pairs | `sprezzature-colors-contrast` | `check_contrast` |
| Colour-vision simulation | `sprezzature-colors-cvd` (works on images) | `simulate_color_blindness` (colours only) |
| Perceptual lighten / darken | — | `adjust_lightness` |
| Colour → connotations | — | `get_color_psychology` |
| Concept → colours | — | `search_concepts` |
| Palette remapped to an accessibility level | `sprezzature-colors-levels` | *(not an MCP tool)* |
| Palette CSV → `tailwind.config.js` | `sprezzature-colors-palette-to-tailwind` | *(not an MCP tool)* |

The gaps are deliberate. The two CLI-only jobs write project files from a
palette CSV; an HTTP tool that returns a config an agent must then write by
hand is worse than the command that writes it. And `simulate_color_blindness`
takes colours, while the CLI takes a whole **image** — for "what does this
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
the hue. Nudging RGB digits washes yellows out while blues barely move — the
usual reason a hand-built palette looks uneven.

---

## File patterns

Palette CSV / JSON files, `tailwind.config.js`, and images (`*.png`, `*.jpg`)
route here when a colour-accessibility or palette-export concern is expressed.
