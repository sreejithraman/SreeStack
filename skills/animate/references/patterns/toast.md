# Toast open / close

## When to use

Toasts, snackbars, and transient confirmations that rise into view from the bottom edge — "Saved", "Copied", "Message sent". The toast translates up with a fade, a slight scale, and a cross-blur; entry is slower than dismissal.

Use **toast** when the surface announces itself and goes away on its own; use **modal** when the user must respond before continuing.

## HTML usage

```html
<div class="t-toast" data-open="false"> … </div>
```

Toggle `.is-open` on the toast. It rises from below with a
fade + cross-blur + slight scale; opening uses the slower
open clock, the resting (closed) transition uses the faster
close clock, so a single class gives the open/close asymmetry.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--toast-open` | `350ms` |
| `--toast-close` | `250ms` |
| `--toast-distance` | `16px` |
| `--toast-blur` | `2px` |
| `--toast-scale` | `0.97` |
| `--toast-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --toast-open: 350ms;
  --toast-close: 250ms;
  --toast-distance: 16px;
  --toast-blur: 2px;
  --toast-scale: 0.97;
  --toast-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-toast {
  opacity: 0;
  transform: translateY(var(--toast-distance)) scale(var(--toast-scale));
  filter: blur(var(--toast-blur));
  will-change: transform, opacity, filter;
  transition:
    opacity var(--toast-close) var(--toast-ease),
    transform var(--toast-close) var(--toast-ease),
    filter var(--toast-close) var(--toast-ease);
}
.t-toast.is-open {
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0);
  transition:
    opacity var(--toast-open) var(--toast-ease),
    transform var(--toast-open) var(--toast-ease),
    filter var(--toast-open) var(--toast-ease);
}

@media (prefers-reduced-motion: reduce) {
  .t-toast { transition: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

None — pure CSS. Toggle the documented HTML attributes or class names from whatever already drives state in your app.

## Entry on mount

Use `@starting-style` when the toast component owns dismissal and only needs a mount transition. This example uses a longer 400ms ease; shorten it for frequent notifications. Check browser targets. If unsupported, use a mount flag with matching initial and mounted CSS. The flag alone supplies no styles.

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 400ms ease,
    transform 400ms ease;

  @starting-style {
    opacity: 0;
    transform: translateY(100%);
  }
}
```

```jsx
useEffect(() => { setMounted(true); }, []);
// <div data-mounted={mounted}>
```

When toasts stack, tune opacity together with list movement. See [banner stacking](banner-stacking.md) for depth and hover expansion. Preserve the component’s exit lifecycle.
