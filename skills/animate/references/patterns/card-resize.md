# Card resize

## When to use

Tweening a container's width or height when its layout state changes (compact ↔ expanded card, collapsing panel, list row toggling extra detail). Pure CSS — no JS required beyond the class toggle that drives the size change.

## HTML usage

```html
<div class="t-resize">…</div>
```

Put `.t-resize` on any element and change its width/height
(directly, or via a state class such as `.is-small`). The
transition will tween the two sizes.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--resize-dur` | `300ms` |
| `--resize-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --resize-dur: 300ms;
  --resize-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-resize {
  transition:
    width  var(--resize-dur) var(--resize-ease),
    height var(--resize-dur) var(--resize-ease);
  will-change: width, height;
}

@media (prefers-reduced-motion: reduce) {
  .t-resize { transition: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

None — pure CSS. Toggle the documented HTML attributes or class names from whatever already drives state in your app.
