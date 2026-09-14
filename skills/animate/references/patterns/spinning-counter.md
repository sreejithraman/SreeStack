# Spinning counter

## When to use

Use for a rare, emphasized change in a score or count. Each digit is a clipped vertical reel of 0-9 cells; the strip translates up through several full spins before landing on the target digit, with a per-column stagger and a vertical-only SVG blur while moving.

Use this for a rare, emphasized number change. For a brief update, use [number pop-in](number-pop-in.md). This guide supplies the CSS and construction steps. The project must build and drive the reels in JavaScript; there is no ready-made builder here.

## HTML usage

```html
<div class="t-reel"></div>  <!-- reels built in JS -->
```

Build one .t-reel-col per digit, each clipping a strip
(.t-reel-strip) of 0-9 cells; translate the strip up by
(spins*10 + digit) cells to spin then land. A directional
(vertical-only) SVG feGaussianBlur stdDeviation="0 Y" gives
the motion streak (CSS blur() would smear sideways); decay it
to 0 per column as each reel settles.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--reel-dur` | `1400ms` |
| `--reel-cell` | `30px` |
| `--reel-spin-blur` | `3px` |
| `--reel-stagger` | `90ms` |
| `--reel-ease` | `cubic-bezier(0.16, 1, 0.3, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --reel-dur: 1400ms;
  --reel-cell: 30px;
  --reel-spin-blur: 3px;
  --reel-stagger: 90ms;
  --reel-ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

## CSS

```css
.t-reel { display: inline-flex; align-items: center; height: var(--reel-cell); font-variant-numeric: tabular-nums; }
.t-reel-col {
  position: relative; height: var(--reel-cell); overflow: hidden;
  /* Soft-fade the window edges instead of hard-cropping. */
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, #000 22%, #000 78%, transparent 100%);
  mask-image: linear-gradient(to bottom, transparent 0%, #000 22%, #000 78%, transparent 100%);
}
.t-reel-strip { display: flex; flex-direction: column; will-change: transform, filter; }
.t-reel-digit { height: var(--reel-cell); display: flex; align-items: center; justify-content: center; }
/* JS drives the tween: strip.style.transition =
     'transform var(--reel-dur) var(--reel-ease) ' + (col*var(--reel-stagger)) + 'ms';
   and decays each column's feGaussianBlur stdDeviation from
   var(--reel-spin-blur) to 0 over its own window. */

@media (prefers-reduced-motion: reduce) {
  .t-reel-strip { transition: none !important; filter: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

Implement these mechanics in the component's lifecycle:

1. Create one `.t-reel-col` per digit and give it a width that fits a digit. Inside it, create a `.t-reel-strip` with enough repeated 0–9 cells for the chosen spin count. Render decimal separators and signs as steady text.
2. Give each moving strip its own SVG filter with a unique ID and an `feGaussianBlur` element. Set `stdDeviation` to `0 Y` for vertical blur; size the filter region so it does not clip the moving digits.
3. Start each strip at its current visible position. Read the computed cell height and numeric timing values, then set its target offset to `-(spins * 10 + digit) * cellHeight`. Use a column delay of `columnIndex * staggerMs`.
4. Decay that column's blur to zero as it settles. On a new value, retarget from the live state and cancel old callbacks. Handle changes in digit count and keep one accessible text value while the reels remain decorative.
5. For reduced motion, render the final digits at once without repeated cells, delays, blur, or animation work. Cancel drivers on teardown and when the preference changes.

The CSS above describes the rendering structure; these JavaScript steps are required to make it run.
