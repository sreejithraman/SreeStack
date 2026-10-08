# Web layout

Use the sections matching the container, grid, responsive component, spacing,
or overflow in scope. Start with real content and the product's tokens. Prefer
intrinsic adaptation when it expresses the design; use container or viewport
queries for actual changes of composition. Keep semantic reading order intact.

## Content widths and breakouts

A named content grid lets CMS blocks choose reading width, breakout width,
or full width without adding a separate container around each block:

```css
.content-grid {
  --gutter: 1.5rem;
  --content: 64rem;
  --breakout: 80rem;
  display: grid;
  grid-template-columns:
    [full-width-start] minmax(var(--gutter), 1fr)
    [breakout-start] minmax(0, calc((var(--breakout) - var(--content)) / 2))
    [content-start] min(100% - var(--gutter) * 2, var(--content)) [content-end]
    minmax(0, calc((var(--breakout) - var(--content)) / 2)) [breakout-end]
    minmax(var(--gutter), 1fr) [full-width-end];
}
:is(.content-grid, .full-width) > * { grid-column: content; }
:is(.content-grid, .full-width) > .breakout { grid-column: breakout; }
:is(.content-grid, .full-width) > .full-width {
  grid-column: full-width;
  display: grid;
  grid-template-columns: inherit;
}
```

Place every direct child deliberately; auto-placement otherwise starts in a
gutter track. Wrap a run of inline content into its intended grid item. Keep
`--breakout >= --content`, adjust both widths coherently, and check the narrow
container including gutters and long content. A nested full-width grid copies
the template and establishes the same named lines. In an authoring system
without child selectors, give each child its intended `grid-column` directly.
See [named grid lines](https://drafts.csswg.org/css-grid-2/#named-lines).

## Intrinsic card grids and subgrid

```css
.cards {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
}
```

The nested `min()` allows a track to fit a slot narrower than the ideal card.
`auto-fit` collapses empty repeated tracks, allowing a short row to expand;
`auto-fill` retains them. Choose based on whether a filtered/short collection
should keep its track layout. Both allow populated `1fr` tracks to grow.

When cards have corresponding parts that must line up across a row:

```css
.card {
  display: grid;
  grid-row: span 3;
  grid-template-rows: subgrid;
  row-gap: 0.5rem;
}
```

Match the row span to the number of parts and give missing parts a deliberate
place. Set the card's row gap or it inherits the parent's. Keep independent
card layout as a usable fallback where subgrid is unavailable. Check multi-row
placement, unequal text, and visual versus semantic ordering.
See [auto-repeat](https://drafts.csswg.org/css-grid-2/#auto-repeat) and
[subgrids](https://drafts.csswg.org/css-grid-2/#subgrids).

## A sidebar that wraps under content pressure

```css
.with-sidebar { display: flex; flex-wrap: wrap; gap: 1rem; }
.sidebar { flex-basis: 20rem; flex-grow: 1; }
.main { flex-basis: 0; flex-grow: 999; min-inline-size: 50%; }
```

The main region's minimum share and the sidebar basis determine when they wrap.
Tune these to content; use a content-based basis when the aside needs it. A
sticky aside needs `align-self: start` and the appropriate inset so stretching
does not consume its travel space. Bare media may stretch in the cross axis;
use `align-items: start` and explicit media geometry where necessary.
See [flex wrapping](https://drafts.csswg.org/css-flexbox-1/#flex-wrap-property).

## Container-responsive components

```css
.slot { container: card-slot / inline-size; }
.card h2 { font-size: clamp(1.25rem, 1rem + 2cqi, 2rem); }
@container card-slot (inline-size > 30rem) {
  .card { display: grid; grid-template-columns: 12rem minmax(0, 1fr); }
}
```

A size query styles descendants of an eligible ancestor, not the container
itself. Give the slot a width from its surrounding layout: inline-size
containment removes its content's intrinsic inline-size contribution, so a
shrink-to-fit slot can become unexpectedly small. Place containment on a wrapper
when it would interfere with a subgrid axis or intrinsic track sizing; evaluate
the actual axis rather than prohibiting every combination of subgrid and queries.

Container units resolve against an eligible ancestor on the relevant axis;
without one they fall back to the small viewport size. Naming a query does not
bind every `cqi` unit to that named container. Keep units and nested containers
scoped deliberately. Root-declared derived tokens, especially registered
lengths, can resolve before reaching the intended slot. Declare and consume
container-derived tokens below that slot and test values in two different slots.
See [container queries and units](https://drafts.csswg.org/css-conditional-5/#container-queries)
and [inline-size containment](https://drafts.csswg.org/css-contain-2/#containment-inline-size).

## Layers, alignment, and clipping

Grid can overlay elements that should still contribute to their container size:

```css
.stack { display: grid; }
.stack > * { grid-area: 1 / 1; }
.stack > .title { place-self: center; }
.stack > .badge { place-self: start end; }
```

Use positioning for layers that should be removed from normal sizing. DOM order
influences painting; manage z-index/stacking contexts deliberately when needed.

For an overflowing centered row, `justify-content: safe center` lets alignment
fall back toward the start instead of making start-side content unreachable.
Use `safe` with supported positional alignment values; it is not valid for
every alignment keyword. Auto margins on an item can also consume positive
free space while allowing overflow to remain reachable.
See [overflow alignment](https://drafts.csswg.org/css-align-3/#overflow-values).

Use `overflow: clip` for intentional clipping without a scroll container.
`hidden` allows programmatic scrolling; `auto` exposes scrolling as needed.
`clip` also does not establish the formatting context that `hidden` does; use
`display: flow-root` separately if that isolation is required. Keep resizable
areas scrollable and check focus rings, sticky descendants, and expanded hit
regions before clipping. Address the overflowing component rather than masking
page-wide overflow. See [overflow values](https://drafts.csswg.org/css-overflow-3/#overflow-properties).

## Spacing owned by groups and neighbors

Use a parent gap for known component children:

```css
.fields { display: flex; flex-direction: column; gap: 1rem; }
.fields > .compact-action { align-self: start; }
```

Flex columns stretch their children by default. For CMS/prose where changing
every child into a flex item would alter flow, scope a margin rhythm:

```css
.prose > * { margin-block: 0; }
.prose > * + * { margin-block-start: var(--flow-space, 1em); }
.prose > :is(h2, h3) { --flow-space: 2em; }
.prose > :is(h2, h3) + * { --flow-space: 0.5em; }
```

Keep the direct-child combinator so nested lists retain their own rhythm.
Hidden elements remain in selector matching, so inspect hidden first children
and conditional blocks; gap follows rendered items whereas sibling selectors
follow the DOM. See [gap](https://drafts.csswg.org/css-align-3/#gap-shorthand).

For reorderable sections, change the relevant edge when a meaningful pair meets:

```css
.page-section { padding-block: var(--space-section, 6rem); }
.logos:has(+ .features) { padding-block-end: 2rem; }
.hero + .logos { padding-block-start: 2rem; }
.logos:where(.hero + *) { border-block-start: 1px solid; }
```

Use semantic section classes and a short set of justified relationships. When
many pairs share a cause, express that common cause. Keep these selectors in
the project's stylesheet when utilities cannot express them cleanly. `:has()`
lets a section look ahead; a following-sibling selector looks back. Default
spacing remains usable where the enhanced relationship is unsupported.
See [relational selectors](https://drafts.csswg.org/selectors-4/#relational).

## Separate an action with auto margins

```css
.card { display: flex; flex-direction: column; gap: 0.5rem; }
.card > .actions { margin-block-start: auto; }
.toolbar { display: flex; gap: 1rem; }
.toolbar > .account { margin-inline-start: auto; }
```

Auto margins consume remaining positive space. A bottom action needs a card
with extra height; the margin cannot create that space by itself. Two block
auto margins can center a region between surrounding content, falling back
to normal flow when no free space remains. Check overflowing neighbors and
wrap behavior. See [flex auto margins](https://drafts.csswg.org/css-flexbox-1/#auto-margins).

## Nested rounded corners

For concentric rounded boxes, start with the inner radius equal to the outer
radius minus the effective inset, bounded at zero:

```css
.frame { --outer-radius: 1rem; --inset: 0.25rem;
  border-radius: var(--outer-radius); padding: var(--inset); }
.frame > .inner {
  border-radius: max(0px, calc(var(--outer-radius) - var(--inset)));
}
```

Include borders in the effective inset. Tune unequal insets, elliptical corners,
and independently branded shapes on the actual surface; the simple subtraction
assumes matching concentric geometry. See [corner shaping](https://drafts.csswg.org/css-backgrounds-3/#corner-shaping).
