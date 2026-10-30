# Web visual systems

Use the product's coherent tokens first. When the system is missing or cannot
express the required roles, establish a small set of scales and tune them
together. The values below are starting points, not universal requirements.

For implementing fluid scales, logical dimensions, and theme/color functions,
read [CSS foundations](web-css-foundations.md). For intrinsic grids, container
queries, content breakouts, and spacing mechanics, read [web layout](web-layout.md).
These implement a chosen system; they do not replace the product's tokens.

## Foundations

### Spacing and sizing

A useful starter scale is:

```text
4  8  12  16  24  32  48  64  96  128  192  256
```

Keep adjacent choices distinct enough to make decisions clear. A denser product
may need intermediate values; a marketing surface may need larger ones. Use
tokens for repeated spacing, sizing, border widths, and opacity rather than
inventing values component by component.

### Typography

A practical UI type scale might begin with:

```text
12  14  16  18  20  24  30  36  48  60  72
```

Use `rem` when values should follow the root text scale, `em` when a measure or
component should follow its own text size, and pixels where a fixed rendering
value is intentional. Test computed results, nesting, zoom, and user text
settings instead of enforcing a single unit everywhere.

Choose a typeface that covers the product's writing systems, symbols, styles,
and needed weights. A neutral sans-serif or system stack can fit when another
element carries the identity: `-apple-system, Segoe UI, Roboto, Noto Sans,
Ubuntu, Cantarell, Helvetica Neue`. Inspect the actual face, fallback, sizes,
and content for legibility; x-height, width, and tracking affect small UI text.
Use enough weights to distinguish roles. Light weights or condensed faces with
short x-heights can lose legibility at small sizes; use role, color, size, or
placement when that communicates hierarchy better.

When a variable face supports an optical-size axis, consider
`font-optical-sizing: auto` and verify it at the actual rendered sizes. Keep the
project's explicit optical-size settings when they are intentional.

Tune tracking, line height, and measure for the face, script, size, and content.
Body text commonly reads well around 45–75 characters per line, but dense data,
editorial prose, and localized content can need different measures.

### Color

Start with semantic needs: surfaces, text levels, interactive actions,
separators, focus, selection, and status. Build only enough ramp steps to serve
those roles and their appearance variants. A simple product may need a few; a
data-rich product may need many.

When deriving a ramp, choose the important usage values first—for example, an
action background, its readable foreground, a quiet tint, and strong text—then
fill gaps that have a real role. HSL or OKLCH can make relationships easier to
reason about, but preserve the project's token format and validate rendered
contrast.

Generated or computed shades are acceptable when they produce stable,
reviewable, accessible tokens. Avoid uncontrolled runtime transformations that
create slightly different colors across components or states.

On a colored surface, a neutral gray foreground can read muddy and detached.
Start from the surface hue, then tune saturation and lightness until the role is
clear and the rendered pairing meets its contrast target.

Use the [optional HSL workflow](systems.md) when building or repairing a numbered
ramp in that color model.

### Shape, borders, and depth

Define shape and elevation by component family and structural role. Related
controls should feel related, but a sheet, compact control, and branded hero do
not need one universal radius.

Use solid surfaces for primary content, raised or translucent surfaces for
elements above it, and scrims for blocking tasks. A surface rarely needs a
strong border, shadow, blur, and background change at once. Each cue should
explain a boundary, layer, or interaction.

A small elevation scale is often enough. Starter shadows might range from a
tight `0 1px 3px` contact shadow to a softer `0 15px 35px` overlay shadow, but
tune color, opacity, and geometry against the actual surfaces. Use
[techniques](techniques.md) when emulated light or prominent shadows are part of
the direction.

When elevation communicates interaction, move a pressed control toward its
surface and lift a legitimately dragged item above its siblings. Treat that as
supporting feedback, not the only state cue, and use `animate` for timing and
interruption.

## Hierarchy and composition

When the primary element still does not stand out, soften its competitors
before amplifying it again. A grayscale pass can expose dependence on color;
use it as a diagnostic technique when the hierarchy is unclear.

Use as many text-color roles as the content hierarchy and contrast requirements
need, and no more. Name the roles by meaning. Every text/surface pairing must
meet the applicable contrast criterion; a tertiary role is not permission to
make normal text unreadable.

Treat semantic markup and visual weight as separate, coordinated choices. Keep
the correct heading and landmark structure even when a section title is visually
quiet.

Put controls near what they affect. Let familiar placement and behavior carry
the interaction unless the product has evidence for a different pattern.

## Component composition

When a standard composition hides the content's relationships, consider these
alternatives while preserving semantics and the interaction contract:

- **Dropdown:** sections, columns, icons, item descriptions, or a status badge
  can expose meaningful groups or differences.
- **Table:** merge a non-sortable field into a related column, such as name over
  role or amount over policy type. Use avatars or status pills when they help
  identify the record.
- **Radio group:** selectable cards can show the actual differences when that
  choice is central to the page.

Use the [browser behavior contract](web-behavior-and-accessibility.md) for custom
controls. Add structure only when it improves the actual task.

## Invariants to verify

- Color is not the only signal for state or meaning. In charts, make series
  separable by lightness or contrast and a secondary cue such as shape, pattern,
  label, or position rather than relying on hue alone.
- Text and essential graphics meet the applicable measured contrast criterion
  on every real surface and material.
- Functional control boundaries remain perceptible; decorative separators need
  not be promoted to controls.
- Responsive changes follow content pressure. Large and small elements do not
  have to scale proportionally.
- Fixed-purpose regions such as a readable form or sidebar use the width their
  content needs and shrink only when the available space requires it.
- Icons render near a size for which their geometry was designed. A surrounding
  shape can give a small icon more presence without distorting it.
- Appearance modes, forced colors, zoom, larger text, localization, and relevant
  viewport sizes preserve the hierarchy and content.

## Starter asset

[`../assets/tokens.css`](../assets/tokens.css) is a contrast-checked example for
projects with no usable tokens. Treat its spacing, type, palette, radius, and
elevation values as a coherent starting system, then retune or prune them for
the product. Reference semantic roles in components rather than coupling them
to raw ramp values.
