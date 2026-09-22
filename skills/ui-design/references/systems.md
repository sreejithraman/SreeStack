# Optional HSL ramp workflow

Use this workflow when a web product needs a new numbered ramp and HSL is a
useful tuning model. It is one way to choose related values, not a required
palette structure. Existing brand systems, perceptual color spaces, wide-gamut
workflows, and tools that produce stable accessible tokens can be equally valid.
Rendered contrast and recognizable semantic roles are the invariants.

## Why HSL

Hex and RGB describe colors in terms a machine cares about. HSL describes them in the terms
your eye already uses:

- **Hue** — position on the wheel, in degrees. 0° red, 120° green, 240° blue. This is what
  makes two different colors both read as "blue".
- **Saturation** — how vivid. 0% is grey (at which point hue is meaningless), 100% is intense.
- **Lightness** — 0% black, 100% white, 50% the pure hue.

Two shades of the same color share a hue in HSL and look unrelated in hex. Design tools
often show HSB, while browsers accept HSL directly — don't confuse the models. In HSB,
100% brightness is only white when saturation is 0; HSB at S100/B100 equals HSL at
S100/L50.

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

- **Avoid pure black when it makes surfaces harsh.** A `grey-900`-like base often
  leaves more room for separation. Build *elevation by getting
  lighter*, not darker. "Raised is lighter than the page" holds in both modes — what changes
  is that shadows barely register against a dark surface, so lightness has to carry the depth
  cue on its own. Surfaces stack upward in lightness; shadows do progressively less work.
  But adjacent steps on a grey ramp are a *thin* cue — typically under 1.3:1 — so a raised
  dark surface usually also needs a hairline border to read as raised at all. Don't just
  reach for a lighter surface: pushing it further up the ramp squeezes the text sitting on
  it, and tertiary text is the first thing to fail.
- **Retune accents in context.** A `500` tuned to carry white text on a light page may vibrate
  against a dark one. Shift toward the `300`/`400` end and drop saturation.
- **Re-check contrast; don't assume it mirrors.** Light-on-dark at the same nominal ratio
  reads heavier, so text often wants to be a shade *dimmer* than the equivalent light-mode
  pairing, not brighter. `grey-100` on `grey-900` is usually too much; `grey-200`/`grey-300`
  is the comfortable body color.
- The two escape hatches below work in reverse too: on a dark colored panel, rotating hue
  toward cyan/magenta/yellow buys contrast without washing to white.

## Hitting contrast ratios without ugly color

WCAG wants 4.5:1 for normal text. The relaxed 3:1 threshold applies only to *large* text —
defined as **18pt (24px) regular, or 14pt (≈18.66px) bold**. 18px regular text is normal text
and needs the full 4.5:1; the book's "~18px" phrasing is looser than the spec.

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

Try perceived brightness instead: **rotate the text's hue toward cyan, magenta or yellow.** You
gain contrast while keeping the text visibly colored and visibly secondary. A blue-violet panel
with cyan-shifted body text can clear AAA and still look like part of the panel.
