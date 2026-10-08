# Modal open / close

## When to use

Modal dialogs and full-overlay surfaces that scale up from center. Use when the surface is conceptually "on top of" the page rather than anchored to a trigger.

## HTML usage

```html
<div class="t-modal" role="dialog">…</div>
```

State:
  - Add `.is-open` to open (scales up from --modal-scale).
  - On close, swap `.is-open` for `.is-closing`, then remove
    `.is-closing` after --modal-close-dur.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--modal-open-dur` | `250ms` |
| `--modal-close-dur` | `150ms` |
| `--modal-scale` | `0.96` |
| `--modal-scale-close` | `0.96` |
| `--modal-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --modal-open-dur: 250ms;
  --modal-close-dur: 150ms;
  --modal-scale: 0.96;
  --modal-scale-close: 0.96;
  --modal-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-modal {
  transform-origin: center;
  transform: scale(var(--modal-scale));
  opacity: 0;
  pointer-events: none;
  transition:
    transform var(--modal-open-dur) var(--modal-ease),
    opacity   var(--modal-open-dur) var(--modal-ease);
  will-change: transform, opacity;
}
.t-modal.is-open {
  transform: scale(1);
  opacity: 1;
  pointer-events: auto;
}
.t-modal.is-closing {
  transform: scale(var(--modal-scale-close));
  opacity: 0;
  pointer-events: none;
  transition:
    transform var(--modal-close-dur) var(--modal-ease),
    opacity   var(--modal-close-dur) var(--modal-ease);
}

@media (prefers-reduced-motion: reduce) {
  .t-modal { transition: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

```js
// Same close-then-cleanup pattern as the dropdown — modals scale from
// --modal-scale up to 1, then on close dip to --modal-scale-close.
const modal = document.querySelector(".t-modal");
const closeMs = parseFloat(
  getComputedStyle(document.documentElement).getPropertyValue("--modal-close-dur")
) || 150;

function openModal() {
  modal.classList.remove("is-closing");
  modal.classList.add("is-open");
}
function closeModal() {
  modal.classList.remove("is-open");
  modal.classList.add("is-closing");
  setTimeout(() => modal.classList.remove("is-closing"), closeMs);
}
```

## Component lifecycle and backdrop

For a dialog with entry and exit attributes, attach motion to those states. Keep the unanchored dialog centered and coordinate backdrop opacity with its open and close phases. Use the project’s `--ease-out` token; if absent, start with `cubic-bezier(0.23, 1, 0.32, 1)`.

```css
.modal {
  transform-origin: center; /* exempt — not anchored to a trigger */
  transition:
    opacity 250ms var(--ease-out),
    transform 250ms var(--ease-out);
}

.modal[data-starting-style],
.modal[data-ending-style] {
  opacity: 0;
  transform: scale(0.96);
}

.backdrop {
  transition: opacity 250ms var(--ease-out);
}
```

Match the backdrop’s close time to the dialog when tuning exit separately.

## Native dialog entry and exit

For an existing native `<dialog>`, let `showModal()` and `close()` own the state.
Apply this variant instead of the class-driven controller above. The dialog must
have an accessible name, a dismissal control, and the product’s focus behavior;
setting `open` alone does not create a modal interaction.

```css
dialog.motion-dialog {
  opacity: 0;
}
dialog.motion-dialog[open] {
  opacity: 1;
}
dialog.motion-dialog::backdrop {
  opacity: 0;
  background: rgb(0 0 0 / 40%);
}
dialog.motion-dialog[open]::backdrop {
  opacity: 1;
}

@media (prefers-reduced-motion: no-preference) {
  dialog.motion-dialog {
    transform: scale(0.96);
    transition: opacity 200ms var(--ease-out, ease-out),
                transform 200ms var(--ease-out, ease-out);
    transition: opacity 200ms var(--ease-out, ease-out),
                transform 200ms var(--ease-out, ease-out),
                display 200ms allow-discrete,
                overlay 200ms allow-discrete;
  }
  dialog.motion-dialog[open] {
    transform: scale(1);
  }
  dialog.motion-dialog::backdrop {
    transition: opacity 200ms var(--ease-out, ease-out);
    transition: opacity 200ms var(--ease-out, ease-out),
                display 200ms allow-discrete,
                overlay 200ms allow-discrete;
  }
  @starting-style {
    dialog.motion-dialog[open] {
      opacity: 0;
      transform: scale(0.96);
    }
    dialog.motion-dialog[open]::backdrop {
      opacity: 0;
    }
  }
}
```

Map 200ms to the project’s dialog token. `@starting-style` follows the open rules
at equal specificity. Discrete `display` transitions keep a closing box visible;
`overlay` can defer its removal from the top layer. The first transition declaration
retains ordinary-property behavior when the enhanced shorthand is unsupported.
See [CSS Transitions Level 2](https://drafts.csswg.org/css-transitions-2/#defining-before-change-style)
and [MDN: overlay](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overlay).

Entry, exit, and backdrop support can differ across target browsers. Confirm the
native `close()`, Escape, and rapid-reopen paths; an instant close is acceptable
when motion is optional. Keep the dialog node mounted through a supported visual
exit. Reduced motion uses the useful open and closed states immediately. Keep
popover selectors separate so an unsupported selector cannot invalidate the
dialog’s open rule.
