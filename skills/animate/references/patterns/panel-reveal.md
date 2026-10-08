# Panel reveal

## When to use

A panel that slides into view inside an existing container — e.g. detail panel inside a card, expanding section. Combines a short translate, opacity, and a 2px cross-blur so a half-height travel still reads as a full open.

## HTML usage

```html
<div class="t-panel-slide" data-open="false">
  <!-- your panel contents -->
</div>
```

The panel slides on the Y axis, fades opacity 0 ↔ 1,
and cross-blurs --panel-blur ↔ 0, all on the same
duration / ease so a shorter travel (e.g. 50% of the
panel height) still reads as a full open / close.
Wrap it in your own container with `overflow: hidden`
if you want the closed state fully clipped. Set
--panel-translate-y to the travel distance (e.g. half
the panel's own height).

## Tunable variables

| Variable | Default |
| --- | --- |
| `--panel-open-dur` | `400ms` |
| `--panel-close-dur` | `350ms` |
| `--panel-translate-y` | `100px` |
| `--panel-blur` | `2px` |
| `--panel-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --panel-open-dur: 400ms;
  --panel-close-dur: 350ms;
  --panel-translate-y: 100px;
  --panel-blur: 2px;
  --panel-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-panel-slide {
  transform: translateY(var(--panel-translate-y));
  opacity: 0;
  filter: blur(var(--panel-blur));
  pointer-events: none;
  transition:
    transform var(--panel-close-dur) var(--panel-ease),
    opacity   var(--panel-close-dur) var(--panel-ease),
    filter    var(--panel-close-dur) var(--panel-ease);
  will-change: transform, opacity, filter;
}
.t-panel-slide[data-open="true"] {
  transform: translateY(0);
  opacity: 1;
  filter: blur(0);
  pointer-events: auto;
  transition:
    transform var(--panel-open-dur) var(--panel-ease),
    opacity   var(--panel-open-dur) var(--panel-ease),
    filter    var(--panel-open-dur) var(--panel-ease);
}

@media (prefers-reduced-motion: reduce) {
  .t-panel-slide { transition: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

None — pure CSS. Toggle the documented HTML attributes or class names from whatever already drives state in your app.

## Clip an overlapping panel

For an overlapping panel of unknown height, clipping can reveal its existing box
without resizing the layout. Use the component’s open state and hidden-state
controller. A panel in normal flow retains its full space when clipped; use the
[accordion](accordion.md) for a disclosure that must change layout.

```css
.clip-panel {
  --clip-shadow-room: 3rem;
  clip-path: inset(0 calc(-1 * var(--clip-shadow-room)) 100%);
  visibility: hidden;
  pointer-events: none;
}
.clip-panel[data-open="true"] {
  clip-path: inset(0 calc(-1 * var(--clip-shadow-room))
                   calc(-1 * var(--clip-shadow-room)));
  visibility: visible;
  pointer-events: auto;
}
@media (prefers-reduced-motion: no-preference) {
  .clip-panel {
    transition: clip-path 250ms var(--ease-out, ease-out),
                visibility 250ms;
  }
}
```

Size the negative inset for the actual shadow’s extent. Add `round` to `inset()`
only when the clip itself needs rounded corners; the surface’s border radius is
independent. See [MDN: inset()](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/basic-shape/inset).

`visibility` stays visible during the close transition, then hides the content.
Return focus appropriately and make closed content inert immediately; clipping
and `pointer-events` alone do not prevent keyboard focus during visual exit.
Reopening must remove inertness with the open state. Reduced motion toggles the
clip and visibility immediately. Check shadow clipping, rapid reversal, and paint
cost on target browsers; clipping does not guarantee compositor execution.
