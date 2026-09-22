# Web visual systems

Use the product's coherent tokens first. When the system is missing or cannot
express the required roles, establish a small set of scales and tune them
together. The values below are starting points, not universal requirements.

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

Keep more space around a group than within it. This relationship matters more
than any particular scale.

### Typography

A practical UI type scale might begin with:

```text
12  14  16  18  20  24  30  36  48  60  72
```

Use `rem` when values should follow the root text scale, `em` when a measure or
component should follow its own text size, and pixels where a fixed rendering
value is intentional. Test computed results, nesting, zoom, and user text
settings instead of enforcing a single unit everywhere.

Choose typefaces that cover the product's writing systems, symbols, styles, and
needed weights. Use enough weights to make roles clear without creating nearly
indistinguishable steps. Light weights often lose legibility at small sizes;
de-emphasize with role, color, size, or placement when that communicates the
hierarchy better.

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

Use [systems](systems.md) when building or repairing a palette from scratch.

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

## Working method

1. Start with a real feature and representative content. Let the shell emerge
   from what the product must do.
2. Resolve layout and hierarchy before decorative detail. A grayscale pass can
   expose dependence on color, but it is a diagnostic technique rather than a
   required phase.
3. Explore in disposable sketches or prototypes, then move to the real surface
   once the direction is decided.
4. Build the smallest useful version. Add capability and visual detail when the
   product can support them.
5. Compare a candidate token with its neighboring values. If the distinction is
   not visible or meaningful, reuse a neighbor.
6. Begin with enough whitespace to see the groups, then tighten deliberately for
   the product's density.
7. Start at the narrowest relevant surface and test wider compositions. That
   may be a compact component, a mobile viewport, a desktop tool, or an embedded
   panel; it is not always a 400-pixel canvas.

## Hierarchy and composition

Build primary, secondary, and tertiary roles with position, spacing, weight,
color, and size together. When the primary element still does not stand out,
soften its competitors before amplifying it again.

Use as many text-color roles as the content hierarchy and contrast requirements
need, and no more. Name the roles by meaning. Every text/surface pairing must
meet the applicable contrast criterion; a tertiary role is not permission to
make normal text unreadable.

Style actions by task importance:

- Primary actions receive the strongest treatment.
- Secondary actions remain clearly available without competing.
- Tertiary actions can use quiet or link-like treatment.

Destructive is a semantic role, not automatically the strongest visual action.
It can become primary inside a confirmation step where deletion is the actual
decision.

Treat semantic markup and visual weight as separate, coordinated choices. Keep
the correct heading and landmark structure even when a section title is visually
quiet.

Put controls near what they affect. Let familiar placement and behavior carry
the interaction unless the product has evidence for a different pattern.

## Invariants to verify

- Color is not the only signal for state or meaning.
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
