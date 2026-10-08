# Web CSS foundations

Read the sections for the stylesheet or token work in scope. Preserve existing
tokens, theme ownership, reset, font loading, and authoring conventions. Check
new features against the project's browser targets and test the rendered result
with zoom, larger text, appearance modes, and the required writing systems.

## Base styles with known effects

For a new surface without a reset, a small starting point is:

```css
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; min-block-size: 100svh; }
img, video { display: block; max-inline-size: 100%; block-size: auto; }
```

Apply changes individually in an established product. Set `min-inline-size: 0`
on flex/grid items that need to shrink, and `flex: none` on media/actions that
must retain their size. A global minimum-size reset changes intrinsic sizing.
Use [mobile browser guidance](mobile-web.md) for input zoom, touch selection,
tap feedback, safe areas, and viewport sizing. Apply control-specific selection
or touch rules to the controls that need them.

Use `text-wrap: balance` for short headings and consider `pretty` for static
prose. Preserve predictable editing in textareas and contenteditable regions;
use `text-wrap: stable` where supported if rebalancing moves text while typing.
Keep wrapping scoped to the relevant content. `font-synthesis: none` requires
actual font files for every needed style and weight; inspect missing-font and
fallback cases. Font smoothing is a platform rendering choice, not a universal
reset improvement. Reserve `scrollbar-gutter` where avoiding layout shifts
matters, accounting for the space it also reserves on short content.
See [text wrapping](https://drafts.csswg.org/css-text-4/#text-wrap),
[font synthesis](https://drafts.csswg.org/css-fonts-4/#font-synthesis), and
[scrollbar gutters](https://drafts.csswg.org/css-overflow-3/#scrollbar-gutter-property).

## Logical geometry

Prefer flow-relative spacing, dimensions, borders, and alignment when they
should follow writing direction. Keep physical geometry when it is intentional,
such as a physical screen edge or an art-directed image crop.

```css
.card {
  position: relative;
  padding-inline: 1.5rem;
  margin-block-end: 2rem;
  border-inline-start: 4px solid;
  text-align: start;
}
.card-close { inset-block-start: 1rem; inset-inline-end: 1rem; }
```

The close control also needs its existing positioning and target-size rules.
Four-value `margin`, `padding`, and `inset` shorthands remain physical; use
`*-inline` and `*-block` for flow-relative pairs. Check RTL and vertical writing
where supported; changing spacing alone does not reverse an interaction's
directional icons or keyboard contract.
See [logical properties](https://drafts.csswg.org/css-logical-1/).

## Related colors and appearance

OKLCH and `color-mix()` can express a new palette's relationships. Preserve a
working palette and semantic roles in other formats. Computed colors still
need contrast checks on their real backgrounds and in every affected state.

```css
:root {
  --action: oklch(55% 0.15 250);
  --action-hover: color-mix(in oklch, var(--action), black 15%);
  --action-tint: color-mix(in oklch, var(--action) 12%, transparent);
}
```

For achromatic colors in polar-space mixing, `none` expresses a missing hue,
as in `oklch(98% 0 none)`. Check the actual interpolation method and gamut;
color arithmetic does not guarantee a perceptually uniform or accessible ramp.
See [missing and powerless components](https://drafts.csswg.org/css-color-4/#missing)
and [color mixing](https://drafts.csswg.org/css-color-5/#color-mix).

`light-dark()` can hold a pair of semantic colors in one declaration when the
project's theme system uses `color-scheme`:

```css
:root {
  color-scheme: light dark;
  --surface: light-dark(oklch(1 0 none), oklch(0.145 0 none));
  --text: light-dark(oklch(0.145 0 none), oklch(0.985 0 none));
}
[data-theme="light"] { color-scheme: light; }
[data-theme="dark"] { color-scheme: dark; }
```

Set the scheme at the scope that owns the theme, including nested themed regions.
Preserve the existing override mechanism when it already works. Images and
non-color theme variants need their own rules. A matching HTML
`<meta name="color-scheme" content="light dark">` can inform early browser
painting; align it with the modes the product actually supports. Keep existing
theme declarations as the fallback when target browsers lack `light-dark()`.
See [scheme-dependent colors](https://drafts.csswg.org/css-color-5/#light-dark)
and [color-scheme](https://drafts.csswg.org/css-color-adjust-1/#color-scheme-prop).

## Fluid sizes from two endpoints

Use `clamp()` when a size should interpolate continuously; use layout changes
when content needs a different composition. Keep font bounds relative to the
root text size and include a relative component in the preferred value:

```css
:root {
  --text-body: clamp(1rem, 0.75rem + 1vw, 1.75rem);
  --space-section: clamp(3rem, 1rem + 6vw, 8rem);
}
```

Given two endpoint sizes and viewport widths in consistent units, the slope is
`(sizeWide - sizeNarrow) / (widthWide - widthNarrow)`. Multiply by 100 for the
`vw` coefficient; the intercept is `sizeNarrow - slope * widthNarrow`. Convert
the intercept and bounds to the intended relative units, then verify computed
values rather than treating the arithmetic as an accessibility proof.

Viewport terms respond to viewport changes, so text may grow less than expected
when zoom changes both the root scale and available width. Test resizing text
to 200%, browser zoom, user font settings, and content reflow. There is no
universal max/min ratio that proves WCAG conformance for an arbitrary layout.
See [clamp](https://drafts.csswg.org/css-values-4/#funcdef-clamp) and
[Resize Text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html).

## A fluid type and spacing scale

For several related sizes, blend two modular scales rather than duplicating
endpoint math in every component. Use plain numbers for the widths, base sizes,
and ratios below; the result stays a length and divides only by a number.

```css
:root {
  --scale-narrow: 20;
  --scale-wide: 77.5;
  --base-narrow: 1.125;
  --base-wide: 1.25;
  --ratio-narrow: 1.2;
  --ratio-wide: 1.25;
  --fluid: clamp(0rem,
    (100vw - var(--scale-narrow) * 1rem) /
    (var(--scale-wide) - var(--scale-narrow)), 1rem);
  --at-narrow: calc(var(--base-narrow) * (1rem - var(--fluid)));
  --at-wide: calc(var(--base-wide) * var(--fluid));
  --step-0: calc(var(--at-narrow) + var(--at-wide));
  --step--1: calc(var(--step-0) / var(--ratio-narrow));
  --step-1: calc(var(--at-narrow) * var(--ratio-narrow) +
    var(--at-wide) * var(--ratio-wide));
  --step-2: calc(var(--at-narrow) * pow(var(--ratio-narrow), 2) +
    var(--at-wide) * pow(var(--ratio-wide), 2));
  --space-s: var(--step-0);
  --space-m: calc(1.5 * var(--step-0));
  --space-l: calc(2 * var(--step-0));
  --space-s-l: calc(var(--at-narrow) + 2 * var(--at-wide));
}
```

Extend positive steps with the same powers only for roles the product needs.
The negative step uses one ratio to avoid a size shrinking as the viewport
widens. Steep spacing pairs such as `--space-s-l` are for layout, not text.
Change scale inputs where the derived tokens are declared: changing an inherited
input on a descendant does not recompute already-resolved parent tokens.
For container-relative scales, declare the derived tokens inside the intended
container and use `cqi`; read [container sizing](web-layout.md#container-responsive-components).
Check `pow()` and the complete arithmetic in target browsers. Use explicit
`clamp()` tokens or a generated scale when this formula is unsupported.
See [exponential functions](https://drafts.csswg.org/css-values-4/#exponent-funcs)
and [custom-property computation](https://drafts.csswg.org/css-variables-1/#defining-variables).
