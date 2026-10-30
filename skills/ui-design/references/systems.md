# Optional HSL ramp workflow

Use this workflow when a web product needs a new numbered ramp and HSL is a
useful tuning model. It is one way to choose related values, not a required
palette structure. Existing brand systems, perceptual color spaces, wide-gamut
workflows, and tools that produce stable accessible tokens can be equally valid.
Rendered contrast and recognizable semantic roles are the invariants.

## HSL and HSB

When transferring swatches from a design tool, check its color model. In HSB,
100% brightness is white only at 0% saturation; HSB at S100/B100 corresponds to
HSL at S100/L50. Equal HSL lightness also does not imply equal perceived
brightness or measured contrast.

## Choose important usage colors first

There is no universal base formula. For a numbered primary or accent ramp, one
practical starting point is the shade used by a high-emphasis action. Choose its
foreground and background together, measure contrast, and check that the result
has the intended weight. A different product may anchor the ramp on data,
illustration, content, or another brand-critical usage.

For neutral ramps, it can be easier to begin with the darkest text and lightest
surface roles instead of inventing a middle swatch first.

## Add edge roles when needed

In a `100`–`900` convention, `900` can serve strong text and `100` a tinted
surface. Design a representative component that uses both, measure the pairing,
and tune it in context. Other naming schemes or role-first tokens are fine.

## Filling the gaps

If the product needs a full nine-step ramp, values such as `700` and `300` can
split the visual distance between the anchors before filling smaller gaps. This
is an efficient construction order, not a required shade count. Keep only the
steps that serve semantic roles.

Then adjust on rendered components. Expect to change saturation, lightness, or
hue once the colors appear at real sizes and proportions. When a new shade is needed, add it
to the system with a named role rather than letting one-off values accumulate
at call sites.

## Keeping saturation alive

In HSL, saturation's effect weakens as lightness approaches 0% or 100%. The same S value that
looks vivid at L50 looks washed out at L90.

When an HSL ramp looks washed out near its light or dark ends, try increasing
saturation as lightness moves away from 50%. Judge the adjustment across the
whole ramp; some identities or color spaces need a different correction.

Tinted neutral ramps can show the same drift toward neutral at their extremes.

## Perceived brightness and hue rotation

Every hue has an inherent perceived brightness. Yellow and blue at identical HSL lightness
look nothing alike in brightness, because the eye weights the channels unevenly:

```
perceived brightness = sqrt(0.299·r² + 0.587·g² + 0.114·b²) / 255
```

This is a palette-tuning heuristic, not the WCAG contrast calculation. Measure
each actual pairing against the contrast criterion below.

Across the wheel this gives three local maxima — **60° (yellow), 180° (cyan), 300° (magenta)**
— and three minima — **0° (red), 120° (green), 240° (blue)**.

This suggests an optional way to change perceived brightness without relying
only on HSL lightness:

- **To lighten:** rotate the hue toward the nearest of 60° / 180° / 300°.
- **To darken:** rotate the hue toward the nearest of 0° / 120° / 240°.

Keep hue rotation small enough that the ramp still reads as one color. Around
20–30° total is a useful starting limit, but judge the rendered ramp and the
identity it must preserve.

This can help scales built on light hues. A yellow darkened by lightness alone can go
muddy olive-brown; a yellow darkened by rotating gradually toward orange gives you warm, rich
dark shades. Combine both approaches freely — take some brightness from hue, some from
lightness.

## Warm and cool greys

True grey is S0%—no color at all. A tinted neutral can connect surfaces and
text to the palette. These are example starting regions:

- **Cool** (blue-ish): hue ~207–210, saturation ~12–21%
- **Warm** (yellow/orange-ish): hue ~39–41, saturation ~12–21%

How far to push the tint is an identity and contrast decision. Inspect the
extremes beside their actual neighboring colors.

## Dark mode

This example extends the same role-first reasoning to dark appearance.

Test dark roles independently instead of assuming a mechanical inversion will
preserve hierarchy and contrast:

- **Tune surface separation.** Try a dark neutral base when pure black makes
  the surface harsh. Lighter raised surfaces can help when shadows barely
  register, but adjacent dark ramp steps can still provide weak separation.
  For example, `#18181b` against `#27272a` has about 1.19:1 contrast; measure the
  actual token pair rather than assuming the next step establishes elevation.
  A hairline border can clarify the boundary without further lightening the
  surface. Check the text pairings before lightening it, especially tertiary
  text. See [contrast-ratio calculation](https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio).
- **Retune accents in context.** A `500` carrying white text on a light page may
  dominate a dark one. Try a `300`/`400` and lower saturation, then check its role
  and foreground pairing.
- **Check text independently.** Compare `grey-100`, `grey-200`, or `grey-300` on
  the actual dark surface for visual weight, then measure contrast. Token names
  alone establish neither comfort nor conformance.
- Try the pairing and hue adjustments below in dark appearance too; measure
  the result rather than assuming a direction of hue rotation adds contrast.

## Hitting contrast ratios without ugly color

For text covered by [WCAG AA Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html),
normal text needs 4.5:1. Large text—18pt (24px) regular, or 14pt (about 18.67px)
bold—needs 3:1. An 18px regular label still needs 4.5:1.

When a colored pairing misses its target, these two candidate moves often help.

### 1. Flip the contrast

White text on a colored background needs the background to be *very* dark to reach 4.5:1 — and
a page full of dark saturated badges grabs attention that those elements don't deserve.

One option is **dark colored text on a light colored tint.** A compatible dark
and light pair can keep the semantic color while sitting quietly in the
hierarchy. This often works well for status pills, tags, and badges.

### 2. Rotate the hue toward a brighter one

For colored text on a colored background — secondary text inside a dark colored panel — raising
lightness alone drives you to near-white before you hit the ratio, and then the primary and
secondary text look identical.

Try a small hue shift toward cyan, magenta, or yellow, then measure the actual
foreground/background pairing. Keep the text visibly colored and secondary
only while meeting its contrast target. For a blue-violet panel, cyan-shifted
body text is one candidate to test.
