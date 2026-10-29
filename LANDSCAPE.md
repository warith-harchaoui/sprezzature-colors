# Landscape

`sprezzature-colors` is the colour brick of the [sprezzature](https://sprezzature.ai/) suite, ten Python packages for building web content that holds up. It does three deterministic things on the standard library: it audits a palette against the Web Content Accessibility Guidelines (WCAG) contrast thresholds and proposes a correction that stays visually close to the colour you chose, it redraws a real image the way a viewer with one of the three colour vision deficiencies (CVD) sees it, and it exports the palette as a Tailwind configuration so every project in the suite draws from one source.

## How it fits in the ecosystem

```
sprezzature suite
├── sprezzature-colors          ← this package (contrast, CVD, palette export)
├── sprezzature-ui              (components and design tokens; consumer of the Tailwind export)
├── sprezzature-accessibility   (static HTML lint, 20 rules; the sister brick)
├── sprezzature-figures         (167 chart types; applies the accessibility levels)
├── sprezzature-maps            (choropleths and situation plates)
├── sprezzature-ux-laws         (Laws of UX audit)
├── sprezzature-publish         (Markdown to site, meta tags, narration)
├── sprezzature-audio           (captions and speech)
├── sprezzature-cli-gui         (a command line wrapped in a page)
└── sprezzature-video           (what a film claims, checked against the code)
```

What comes before: a palette, whether it is a brand CSV, a Figma library or a `tailwind.config.js` somebody already wrote. What comes after: `sprezzature-ui` consumes the emitted Tailwind block, and `sprezzature-figures` calls the accessibility levels so a chart can be re-coloured for one deficiency without a single colour name changing.

The sister brick is `sprezzature-accessibility`. It reads HTML and reports twenty rules; one of them, `color-only-state`, catches a state carried by hue alone. It stops there on purpose. Whether a given pair of hex codes clears 4.5:1, and what the nearest passing colour is, belongs here.

## When to choose it

- You want a contrast check in a pre-commit hook or in continuous integration. The audit is standard library only, exits 1 on any failing pair, and prints JSON on request. There is no browser to start and no Node to install.
- You have a screenshot, a chart or a hero image and you want to see it under protanopia, deuteranopia and tritanopia, plus a relative-luminance greyscale, written as files you can attach to a review.
- You want the fix, not just the verdict. The audit holds your hue and your chroma fixed and walks the OKLCH lightness axis in hundredth steps until the pair clears the threshold, so the proposal reads as your colour, lighter or darker, rather than as a different colour.
- You have several projects and one palette, and you are tired of hex codes drifting between them. One CSV in, one Tailwind block out, with the source file named in a comment at the top of the generated code.

## When to pick something else

- **axe-core** or **Lighthouse** when the question is the page as rendered. They read the computed styles of a live DOM, catch the cascade, inherited colours and opacity, and attach the failure to the element. `sprezzature-colors` judges a palette and an image; it never opens a page. axe-core is also honest about its own limit: text over a CSS gradient comes back `incomplete` rather than pass or fail, because there is no single background colour to measure against.
- **Colour Contrast Analyser** by TPGi when you need an eyedropper. It samples any pixel on the screen, including a native application or a PDF that no script will ever parse, and it is free and has been maintained for years.
- **Stark** or **Polychrom** when the work is still in Figma. Nothing in a Python package helps a designer who has not exported anything yet, and Polychrom in particular resolves the real background behind a selection through opacity, multiple fills and blend modes, which is exactly the case a flat hex list cannot describe. Polychrom is free and open source; Stark is the broader commercial suite, with a team and support behind it.
- **Adobe Leonardo**, **Huetone** or **Accessible Palette** when you are generating a scale rather than checking one. They build a ramp from target contrast ratios in a perceptual space, which is a different and larger job than nudging one failing pair.
- **Style Dictionary** or **Tokens Studio** when the tokens have to reach more than one platform. The export here is one target, Tailwind, because that is the only one this suite needs; Style Dictionary emits to iOS, Android, CSS, Swift and anything you write a transform for, and reads the W3C Design Tokens format natively.
- **colorjs.io** or **coloraide** when you want the colour science itself. colorjs.io implements the CSS Color 4 and 5 specifications and six contrast algorithms; coloraide covers CAM16, HCT and the three published CVD models with a severity parameter. Both are far wider than this package, and neither is trying to be a command line gate.
- **Color Oracle** or **Sim Daltonism** when the thing to check cannot be exported as an image: a running application, a video, a map you are panning. A full-screen filter sees everything a screenshot would miss.

## Ideas worth stealing

Studying a competitor and bringing nothing back is wasted reading. Eight things the tools above do better, ordered by what they return for what they cost, including two this package should not take.

**1. Style Dictionary, a second emit target that buys all the others.** [Style Dictionary](https://styledictionary.com/) reads the [W3C Design Tokens](https://www.designtokens.org/) JSON format natively and turns it into CSS, Swift, Kotlin, Android XML and anything else a transform exists for. Here, `scripts/palette_to_tailwind.py` would gain `--emit dtcg`, writing `{"brand": {"blue": {"$type": "color", "$value": "#007AFF"}}}` beside the existing `theme` and `config` modes. That one flag turns the package's single export target into every target Style Dictionary supports, without this package learning what a Swift colour literal looks like. Cost: an hour or two, no new dependency, the renderer already walks the same rows. The only ongoing cost is tracking the format version.

**2. DaltonLens, severity and a named model.** The [DaltonLens review](https://daltonlens.org/opensource-cvd-simulation/) compares BRETTEL 1997, VIÉNOT 1999, MACHADO 2009 and the HCIRN function against reference data and concludes that BRETTEL is still the only solid choice for tritanopia. `_colors.CVD_MATRICES` hard-codes MACHADO at severity 1.0 and the docstring says so, which means the package already names the limitation it has not yet fixed. MACHADO, OLIVEIRA and FERNANDES publish their matrices at eleven severity steps per deficiency, so `simulate_cvd.py` could take `--severity 0.0..1.0` on pure tabulated data: thirty-three matrices of nine floats, still stdlib, still deterministic. Most CVD is anomalous trichromacy rather than full dichromacy, so severity is the realistic case, not an edge case. Cost: half a day for the severity table; adding BRETTEL for tritanopia is another half day because it needs the LMS plane projection rather than a lookup. Best technical ratio in this list.

**3. ColorBrewer, a one-word verdict on a whole scheme.** [ColorBrewer](https://colorbrewer2.org/), Cynthia BREWER's scheme picker, tags every scheme as colourblind safe, print friendly or photocopy safe, so a cartographer picks without running anything. `scripts/accessibility_levels.py` already computes everything that verdict needs (`_cvd_luminance`, `_relative_luminance_hex`, `contrast_ratio_hex`) and does not emit one. A `sprezzature-colors-levels --check` would print three booleans for a palette: every category separable under each of the three simulations, separable in greyscale, every mark clearing 3:1 against the background. That is the line `sprezzature-figures` could gate a figure on. Cost: an afternoon. The only real decision is the minimum lightness gap that counts as separable, and it has to be written down rather than tuned.

**4. axe-core, a third verdict and no silent pass.** axe-core returns `incomplete` instead of pass or fail when it cannot read a single background colour, and the reason is that a quiet pass is worse than an honest "I could not tell". `audit_contrast.py` has the failure axe-core avoided: `is_foreground()` and `is_background()` match on the `label-`, `brand-` and `surface-` prefixes, so an external palette named `{"text": ..., "bg": ...}` produces zero pairs, prints `0 pass, 0 fail.` and exits 0. A palette that was never checked currently looks exactly like a palette that passed. The fix is two lines and a test: exit non-zero with "no pairs checked, see --pairs" when the pair list is empty. Cost: an afternoon, and it is the entry with the shortest distance between reading a competitor and finding a defect at home.

**5. Adobe Leonardo, generation by target ratio.** [Leonardo](https://leonardocolor.io/) takes key colours and a list of target contrast ratios and returns the scale that hits them, which is the inverse of checking and strictly more useful once a design system exists. The machinery is half built here already: `accessibility_levels._darken_to_contrast` walks the L axis to a target ratio today. What is missing is the entry point that does it N times. A `sprezzature-colors-levels --ratios 1.2,1.5,3,4.5,7,12` would emit a Tailwind-shaped 50 to 900 ramp per hue, feeding straight into `palette_to_tailwind.py`. Cost: about a day. Half of it is naming the steps, because a ramp whose names do not match Tailwind's is a ramp nobody pastes.

**6. Polychrom, the background you actually sit on.** [Polychrom](https://evilmartians.com/opensource/polychrom) walks the Figma node tree to find the real background behind a selection, through opacity, multiple fills and blend modes, rather than trusting the frame it is nominally inside. The transferable half is a `--pairs pairs.json` file naming explicit (foreground, background) pairs, so a project whose tokens are not named the suite's way can be audited at all. There is a sharper reason to do it: `palette_to_tailwind.py` emits `'rgba(60,60,67,0.6)'` for `label.secondary` in its own `--emit config` output, and feeding that same string back to `audit_contrast.py` raises `ValueError: Bad hex color`. The package cannot currently read back what it writes. Cost: a day, counting an `rgba()` parser in `_colors.py` next to `parse_hex_rgba` and the test that round-trips the emitted config through the audit.

**7. colorjs.io and APCA, taken as a number and refused as a gate.** [colorjs.io](https://colorjs.io/) exposes six contrast algorithms behind one call, WCAG 2.1 and APCA among them, and several tools in the table above already report an APCA Lc value: Polypane, Polychrom, Huetone. The algorithm is Andrew SOMERS' work and the [introduction](https://git.apcacontrast.com/documentation/APCAeasyIntro.html) is readable; the formula is about sixty lines of standard library. It should be reported here as an advisory second number and must not become the thing `--target` compares against, because APCA was pulled from the WCAG 3 working draft in July 2023 and the draft of September 2026 still says the contrast algorithm is yet to be determined. A gate that fails a build on a candidate method is a gate that fails a build on a guess. Cost: half a day for the number, plus the standing cost of tracking a moving target, which is the part that argues for advisory only.

**8. Color Oracle, refused.** [Color Oracle](https://colororacle.org/) applies a full-screen colour filter to whatever is on the display, which is how you check a running application, a video or a map you are panning, and no image-file simulator reaches any of those. It will not be taken. A screen filter is a native graphical application per platform, with a display server behind it; this package is a headless, deterministic, standard-library tool that a continuous integration runner invokes with no screen at all. The right answer is to say in the README that Color Oracle is the tool for that case, which costs nothing and is more useful than a half-built imitation.

## The families of the domain

The first split is **static against runtime**. A static tool is handed colours, or an image, and answers from them alone: WebAIM's checker, Who Can Use, Coblis, every palette generator, and this package. A runtime tool is handed a page and reads what the browser actually computed: axe-core, Lighthouse, Polypane. The runtime family catches what no palette file can predict, a colour arriving through three levels of cascade and a 60 % opacity; the static family runs before anything is rendered, which is why it fits a pre-commit hook and a CI job. The honest summary is that they are complements, and a project with only one of the two has a gap.

The second split is **check against make**. Checking is the older and more crowded half: WebAIM, Colour Contrast Analyser, Who Can Use, Stark, Polychrom, the whole simulator family. Making is the newer half, and it grew out of a frustration with the first: Adobe Leonardo generates by target contrast ratio instead of by eye, Huetone and Accessible Palette build scales whose lightness steps are predictable, Radix Colors and Open Props ship the scales already built. A tool that only checks hands you a failure; a tool that makes hands you a palette that cannot fail the same way twice. `sprezzature-colors` sits across the line, which is deliberate and is also why it is best at neither extreme: the contrast audit proposes a minimal edit rather than regenerating the scale.

The third split is **product against library**. A product has a user interface and a designer can open it: Stark, the Figma plugins, the web checkers, Color Oracle. A library has an application programming interface and a build step can call it: chroma.js, culori, colorjs.io, coloraide, Style Dictionary. The products are where accessibility work actually happens in most teams, because the person choosing the colour is the person who should see the number. The libraries are where the work becomes repeatable. This package is a library with a command line attached, which places it firmly on the engineering side of that line, and a designer who will not open a terminal gets nothing from it.

A fourth distinction cuts across all three and matters more than its size suggests: **which CVD model a simulator uses**. The published candidates are BRETTEL (1997), VIÉNOT (1999), MACHADO, OLIVEIRA and FERNANDES (2009), and the older HCIRN function. The [DaltonLens review](https://daltonlens.org/opensource-cvd-simulation/) compares them against reference data and is worth reading before trusting any simulator: BRETTEL remains the only solid choice for tritanopia, VIÉNOT, BRETTEL and MACHADO are all defensible for the red and green deficiencies, and the HCIRN function used by Sim Daltonism and by the original Coblis is the weakest of the set. This package uses MACHADO at full severity, which is a defensible choice for protanopia and deuteranopia and the less exact one for tritanopia. That is a real limit, and it is why the table below does not give it five stars for simulation.

## How it compares

Every tool is rated 1 to 5 on each criterion, higher is better (⭐ weak to ⭐⭐⭐⭐⭐ strongest). The scores are a considered judgement from reading the documentation and the source, not a benchmark, and every axis is oriented so that more stars mean stronger on that trait. A ⭐ means the tool does not do the thing at all, which on a capability scale is the bottom of the scale and not a missing value. `sprezzature-colors` is the first row because `standpoint` orients the whole map around the first row and places it top right; that is a convention of the drawing, not a claim about quality, and the four columns where this package scores 1 or 2 are the ones to read first.

One criterion that might be expected is absent. Nearly every tool here is free, and most are open source, so an openness column would have given the same score to 22 of the 26 rows and told the projection nothing. What does separate them is whether a company answers support requests, which is the last column.

| Colour tool | Contrast coverage | Colour-vision-deficiency simulation | Fix close to the original colour | Design-token export | Palette generation | Local and offline | Dependency-free install | Fits continuous integration | Usable without writing code | Perceptual colour space | Grounded in a published source | Works on what is actually rendered | Maturity and ecosystem | Commercial backing and support |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| sprezzature-colors | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| WebAIM Contrast Checker | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Colour Contrast Analyser | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| axe-core | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Lighthouse | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Polypane | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Stark | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Polychrom | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Who Can Use | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ |
| Color Oracle | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Coblis | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Sim Daltonism | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| DaltonLens | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Adobe Leonardo | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Huetone | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ |
| Accessible Palette | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ |
| Radix Colors | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Open Props | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Style Dictionary | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Tokens Studio | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| chroma.js | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| culori | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| colorjs.io | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| coloraide | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| ColorBrewer | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| viz-palette | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |

![Positioning map of sprezzature-colors against 25 other colour tools, on two axes derived by principal component analysis. The horizontal axis separates, on the left, tools you point at something already on screen (Color Oracle, Colour Contrast Analyser, axe-core, Polypane, Sim Daltonism) from, on the right, tools that make colours and get called by code (chroma.js, colorjs.io, Accessible Palette, Open Props). The vertical axis separates, at the bottom, established build infrastructure, with Style Dictionary the lowest point on the map and axe-core and Tokens Studio above it, from, at the top, the single-purpose accessibility helper. sprezzature-colors sits at the top right, level with Accessible Palette and just above Huetone, which is where standpoint anchors the reference row.](assets/landscape.svg)

The source is [`assets/landscape.csv`](assets/landscape.csv), the star table above and nothing added, and the map is regenerated from the sprezzature hub with:

```sh
python scripts/landscape_to_csv.py ~/sprezzature-colors/LANDSCAPE.md
standpoint ~/sprezzature-colors/assets/landscape.csv --outdir ~/sprezzature-colors/assets --stem landscape --check
```

The geometry is ordinary correlation principal component analysis (PCA) and is deterministic: the same table gives the same map every run, with no model involved. The four words at the edges should have been named by a local model and were not. Ollama was reachable but saturated, three attempts timed out at 120 seconds each, so the poles carry standpoint's built-in fallback names (Practicality against Innovation, Stability against Accessibility) and the prose interpretation it usually writes is missing from [`assets/landscape.md`](assets/landscape.md). Those four words are the one part of this map that is not evidence. The loadings are, and here is what the two axes are actually made of.

**Horizontal.** Works on what is actually rendered (−0.46), usable without writing code (−0.31), commercial backing and support (−0.23) and colour-vision-deficiency simulation (−0.23) pull one way; palette generation (+0.45), perceptual colour space (+0.38), design-token export (+0.31) and dependency-free install (+0.30) pull the other. The axis opposes a tool you point at something already on screen against a thing that makes colours and gets called by code. Color Oracle (−2.57), Colour Contrast Analyser (−2.48) and axe-core (−2.27) hold the left end; chroma.js and this package (+2.57) and colorjs.io (+2.52) hold the right. `sprezzature-colors` is at the right end by construction, because it is the reference row and `standpoint` anchors the reference top right.

**Vertical.** Maturity and ecosystem (−0.41), fits continuous integration (−0.39), commercial backing and support (−0.34), design-token export (−0.33) and local and offline (−0.27) all load together at the bottom; usable without writing code (+0.31), a fix close to the original colour (+0.30), colour-vision-deficiency simulation (+0.27) and dependency-free install (+0.26) load at the top. The bottom pole is one coherent thing, established build infrastructure: Style Dictionary is the lowest point on the map at −3.58, with axe-core (−2.59), Tokens Studio (−1.22) and Lighthouse (−1.19) above it. The top is the single-purpose accessibility helper, and the honest reading of sitting up there is that part of what puts a tool at the top is having no ecosystem and no company behind it. Accessible Palette shares the exact top value with this package, and Huetone (+3.09) and Who Can Use (+2.96) are just below.

**Two axes carry 44.2 % of the table**, 23.4 % horizontally and 20.8 % vertically. That is the number to hold onto: more than half of what these 14 criteria say is not on this page. With 14 criteria across 26 tools a figure that low is expected, and it means the map is a first orientation while the table is the evidence.

`standpoint --check` reports the leader top right and the axis labels visible, and it fails the readability test: four pairs of labels risk overlapping (`sprezzature-colors` with Accessible Palette, Polypane with Sim Daltonism, Who Can Use with viz-palette, Open Props with chroma.js). Two of those four are the genuinely close calls in the table, which is the map telling the truth rather than a defect in the drawing, but the labels do collide and the SVG is the version to read, because its points carry their values on hover.

## Sources

- [DaltonLens, "Review of Open Source Color Blindness Simulations"](https://daltonlens.org/opensource-cvd-simulation/), the comparison of BRETTEL, VIÉNOT, MACHADO and HCIRN against reference data.
- [Polychrom](https://evilmartians.com/opensource/polychrom), Evil Martians' open-source Figma plugin, and their [survey of the OKLCH ecosystem](https://evilmartians.com/chronicles/exploring-the-oklch-ecosystem-and-its-tools).
- [axe-core issue 4628](https://github.com/dequelabs/axe-core/issues/4628), on why contrast over a CSS gradient comes back `incomplete`.
- [The Easy Intro to the APCA Contrast Method](https://git.apcacontrast.com/documentation/APCAeasyIntro.html), Andrew SOMERS' own introduction to the algorithm several tools here already report.
- [Accessible color for design systems just got easier](https://medium.com/@NateBaldwin/accessible-color-for-design-systems-just-got-easier-40e8420a8371), Nate BALDWIN on the thinking behind Adobe Leonardo.
- [npm trends: chroma-js against colorjs.io against culori](https://npmtrends.com/chroma-js-vs-color.js-vs-colord-vs-colorjs.io-vs-culori), for the relative sizes of the JavaScript libraries.
- [Style Dictionary](https://styledictionary.com/) and the [W3C Design Tokens format](https://www.designtokens.org/), the token pipeline this package deliberately does not try to be.
