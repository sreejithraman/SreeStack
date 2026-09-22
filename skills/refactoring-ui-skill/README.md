# Refactoring UI skill

A cross-platform skill for improving visual hierarchy and styling in web,
SwiftUI, and UIKit interfaces. Its web guidance preserves the concrete rules
derived from *[Refactoring UI](https://www.refactoringui.com/)* by Adam Wathan
and Steve Schoger. Its Apple-platform branch adapts the same systems thinking
to native typography, semantic colors, adaptive layout, and accessibility.

The web rules and CSS values were cross-checked against the book. Typography
and material guidance also adapts Emil Kowalski's `apple-design` skill.
Apple-specific guidance follows current Apple documentation instead of
translating CSS values literally.

## What it does

When styling, reviewing, or defining a visual system, this skill helps an agent:

- Preserve coherent product tokens, or establish small deliberate scales and
  semantic roles where the system has gaps
- Build hierarchy through weight/color rather than piling on font-size
- Diagnose vague complaints ("looks off", "feels cheap") into specific, mechanical fixes
- Apply concrete techniques for depth, contrast, images, and breaking generic component
  shapes

It does **not** include the book itself — see [Credits](#credits).

## Repo structure

```
SKILL.md                 shared procedure, principles, and platform routing
references/
  web.md                  web systems, procedure, hierarchy, and hard rules
  apple-platforms.md      native typography, color, layout, and verification
  systems.md              building a color palette from scratch (HSL, saturation, hue rotation)
  diagnose.md              symptom -> fix table, for improving existing UI
  techniques.md            depth/light simulation, typefaces, grids, images
assets/
  tokens.css               a complete, contrast-verified starter token set
```

## Use

Install or link this skill through the repository-level instructions in the
root [README](../../README.md). It is automatically discoverable for visual
hierarchy, styling, and design-system work on its supported platforms.

## Credits

The web rules and CSS are original notes derived from *Refactoring UI* by Adam
Wathan and Steve Schoger. This repo does not include the book's text or images.
If you find the web guidance useful, buy the book:
**https://www.refactoringui.com/**

The Apple-platform guidance follows the Apple documentation cited in that
reference. The typography and material additions credit Emil Kowalski; see the
repository's [third-party notices](../../THIRD_PARTY_NOTICES.md).

## License

MIT for the contents of this repo (see [LICENSE](LICENSE)). Does not extend to
the book itself. Imported material is covered by the repository's
[third-party notices](../../THIRD_PARTY_NOTICES.md).
