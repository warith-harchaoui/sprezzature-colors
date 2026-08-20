# Landscape

Color-accessibility tools split into two families by what they check.
A **contrast/CVD checker** looks at rendered pixels or resolved hex
values and asks whether two colors are far enough apart, for a normal
viewer or for a color-vision-deficient one. A **design-token pipeline**
looks at the source of truth for a palette (a CSV, a JSON file, a
Figma library) and asks how to get it into a build system without
hand-copying hex codes. `sprezzature-colors` does both, deliberately,
because the two problems share the same underlying color math (sRGB,
WCAG luminance, OKLab/OKLCH) and keeping them in one small package
means that math is written once.

## Tool comparison

| Tool | Type | Browser needed | Fix suggestions | CI-friendly | Python |
|---|---|---|---|---|---|
| **sprezzature-colors** | Contrast audit + CVD sim + token export | No | Yes (OKLCH neighbour) | Yes | Yes |
| axe-core / Lighthouse | Runtime DOM contrast check | Yes | No | Yes (via CLI) | No |
| Stark (Figma/Sketch plugin) | Design-tool contrast + CVD sim | No (plugin) | No | No | No |
| Coblis / Color Oracle | Standalone CVD simulator | No | No | No | No (Color Oracle: native app) |
| Style Dictionary | Design-token pipeline | No | N/A | Yes | No (Node) |

### Ratings

| Dimension | sprezzature-colors | axe-core | Stark | Style Dictionary |
|---|---|---|---|---|
| Contrast coverage | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | N/A |
| CVD simulation | ⭐⭐⭐⭐ | N/A | ⭐⭐⭐⭐ | N/A |
| Token export | ⭐⭐⭐ | N/A | N/A | ⭐⭐⭐⭐⭐ |
| Zero-dep install | ⭐⭐⭐⭐⭐ | ⭐⭐ | N/A (plugin) | ⭐⭐⭐ |
| Fix suggestions | ⭐⭐⭐⭐ | ⭐ | ⭐ | N/A |

## When to use what

Use `sprezzature-colors` as the **CI gate** for both problems at once:
`audit_contrast.py` fails the build on a real contrast regression,
`simulate_cvd.py --grid` produces an artifact a reviewer can glance at,
and `palette_to_tailwind.py` keeps every consuming project's
`tailwind.config.js` generated from the same `palette.csv` instead of
drifting.

axe-core (or Lighthouse's accessibility audit) is the right tool for
runtime DOM contrast, since it reads the actual computed styles of a
live page, catching cases where CSS cascades or opacity change the
rendered color in ways a static palette check cannot see.

Stark and Color Oracle are the right tools for a designer working
inside Figma or Sketch, previewing CVD live while a mockup is still
being drawn, before any code exists to run `simulate_cvd.py` against.

Style Dictionary is the right tool once a design-token system needs to
emit to many platforms (iOS, Android, web, multiple CSS frameworks) at
once; `palette_to_tailwind.py` is intentionally narrower, one CSV in,
one Tailwind block out, because that is the only export this stack
needs today.
