# Menu dropdown

## When to use

Contextual menus, dropdowns, popovers — anything that opens from a trigger and should visually grow from that trigger's position. Origin-aware via `data-origin` (top-left, top-center, top-right, bottom-*).

## HTML usage

```html
<div class="t-dropdown" data-origin="top-center">
  <!-- your menu contents -->
</div>
```

State:
  - Add `.is-open` to show.
  - On close, swap `.is-open` for `.is-closing`, then remove
    `.is-closing` after --dropdown-close-dur.

data-origin values: top-left | top-center | top-right |
                    bottom-left | bottom-center | bottom-right.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--dropdown-open-dur` | `250ms` |
| `--dropdown-close-dur` | `150ms` |
| `--dropdown-pre-scale` | `0.97` |
| `--dropdown-closing-scale` | `0.99` |
| `--dropdown-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --dropdown-open-dur: 250ms;
  --dropdown-close-dur: 150ms;
  --dropdown-pre-scale: 0.97;
  --dropdown-closing-scale: 0.99;
  --dropdown-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-dropdown {
  transform-origin: top left;
  transform: scale(var(--dropdown-pre-scale));
  opacity: 0;
  pointer-events: none;
  transition:
    transform var(--dropdown-open-dur) var(--dropdown-ease),
    opacity   var(--dropdown-open-dur) var(--dropdown-ease);
  will-change: transform, opacity;
}
.t-dropdown[data-origin="top-right"]     { transform-origin: top right; }
.t-dropdown[data-origin="top-center"]    { transform-origin: top center; }
.t-dropdown[data-origin="bottom-left"]   { transform-origin: bottom left; }
.t-dropdown[data-origin="bottom-center"] { transform-origin: bottom center; }
.t-dropdown[data-origin="bottom-right"]  { transform-origin: bottom right; }

.t-dropdown.is-open {
  transform: scale(1);
  opacity: 1;
  pointer-events: auto;
}
.t-dropdown.is-closing {
  transform: scale(var(--dropdown-closing-scale));
  opacity: 0;
  pointer-events: none;
  transition:
    transform var(--dropdown-close-dur) var(--dropdown-ease),
    opacity   var(--dropdown-close-dur) var(--dropdown-ease);
}

@media (prefers-reduced-motion: reduce) {
  .t-dropdown { transition: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

```js
// Toggle .is-open / .is-closing with a setTimeout cleanup so the closing
// scale animates before the element resets to its pre-open rest state.
const dropdown = document.querySelector(".t-dropdown");
const closeMs = parseFloat(
  getComputedStyle(document.documentElement).getPropertyValue("--dropdown-close-dur")
) || 150;

function openDropdown() {
  dropdown.classList.remove("is-closing");
  dropdown.classList.add("is-open");
}
function closeDropdown() {
  dropdown.classList.remove("is-open");
  dropdown.classList.add("is-closing");
  setTimeout(() => dropdown.classList.remove("is-closing"), closeMs);
}
```

## Component lifecycle hooks

When the component already exposes entry and exit attributes, style those states instead of adding a second class-driven lifecycle. Base UI uses the attributes below and supplies the trigger origin. Use the project’s `--ease-out` token; if absent, start with `cubic-bezier(0.23, 1, 0.32, 1)`.

```css
.popover {
  transform-origin: var(--transform-origin); /* Base UI supplies this */
  transition:
    opacity 200ms var(--ease-out),
    transform 200ms var(--ease-out);
}

.popover[data-starting-style],
.popover[data-ending-style] {
  opacity: 0;
  transform: scale(0.95);
}
```

Keep the origin at the trigger. Confirm the installed component’s attribute names.

## Native popover entry and exit

Use this variant when the existing component uses the Popover API. A popover
provides showing and dismissal behavior; its contents still need the correct
semantics. Use a real menu component for menu keyboard navigation, or ordinary
links and buttons for an action panel.

```html
<button type="button" popovertarget="actions">Options</button>
<div id="actions" class="motion-popover" popover>
  <button type="button">Rename</button>
</div>
```

```css
.motion-popover[popover] { opacity: 0; }
.motion-popover[popover]:popover-open { opacity: 1; }

@media (prefers-reduced-motion: no-preference) {
  .motion-popover[popover] {
    translate: 0 0.5rem;
    transition: opacity 200ms var(--ease-out, ease-out),
                translate 200ms var(--ease-out, ease-out);
    transition: opacity 200ms var(--ease-out, ease-out),
                translate 200ms var(--ease-out, ease-out),
                display 200ms allow-discrete,
                overlay 200ms allow-discrete;
  }
  .motion-popover[popover]:popover-open { translate: 0 0; }
  @starting-style {
    .motion-popover[popover]:popover-open {
      opacity: 0;
      translate: 0 0.5rem;
    }
  }
}
```

Use the project’s popover timing and positioning. This example owns only motion;
test the existing placement near viewport edges and with long content. If scale
better explains the origin, use a small scale and a trigger-based transform origin.
`@starting-style` follows the open rule. `display` and `overlay` with
`allow-discrete` enable supported native exits without a separate closing timer.
See [Chrome: entry and exit transitions](https://developer.chrome.com/blog/entry-exit-animations).

Keep the popover mounted while an exit runs. Test light dismissal, Escape, keyboard
activation, and quick reopen. Confirm the actual browsers’ entry and exit behavior;
fall back to instant state changes where the enhancement is unavailable. Reduced
motion is instant in this variant. An unsupported Popover API needs the project’s
working component fallback, not just a motion fallback. Keep `:popover-open`
selectors separate from native dialog open-state rules.
