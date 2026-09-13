# Texts reveal

## When to use

A headline + supporting line that rise into view with staggered blur — hero copy, empty states, onboarding steps. Exit is decoupled: a single quiet fade with no Y-return so dismissing doesn't replay the reveal in reverse.

## HTML usage

```html
<div class="t-stagger">
  <strong class="t-stagger-line t-stagger-line--1">…</strong>
  <span class="t-stagger-line t-stagger-line--2">…</span>
</div>
```

State:
  - Add `.is-shown` to play the staggered entrance.
  - Add `.is-hiding` (and remove `.is-shown`) to fade
    out in place over a short 200ms — independent of the
    entrance timing so the exit doesn't replay the stagger.

Add more lines by adding `.t-stagger-line--N` with
`transition-delay: calc(var(--stagger-stagger) * (N - 1))`.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--stagger-dur` | `500ms` |
| `--stagger-distance` | `12px` |
| `--stagger-stagger` | `40ms` |
| `--stagger-blur` | `3px` |
| `--stagger-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --stagger-dur: 500ms;
  --stagger-distance: 12px;
  --stagger-stagger: 40ms;
  --stagger-blur: 3px;
  --stagger-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
/* Lines start translated down + blurred + invisible; .is-shown
   on the parent flips them to their resting state. The second
   line's transition-delay holds it back by --stagger-stagger
   so the eye lands on the headline first. */
.t-stagger-line {
  display: block;
  opacity: 0;
  transform: translateY(var(--stagger-distance));
  filter: blur(var(--stagger-blur));
  transition:
    opacity   var(--stagger-dur) var(--stagger-ease),
    transform var(--stagger-dur) var(--stagger-ease),
    filter    var(--stagger-dur) var(--stagger-ease);
  will-change: transform, opacity, filter;
}
.t-stagger-line--2 { transition-delay: var(--stagger-stagger); }

.t-stagger.is-shown .t-stagger-line {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}
/* Exit decouples from the stagger: same fade for every line,
   no Y return, no blur — so the disappearance reads as a
   single quiet fade instead of a reverse reveal. */
.t-stagger.is-hiding .t-stagger-line {
  opacity: 0;
  transform: translateY(0);
  filter: blur(0);
  transition:
    opacity 200ms ease,
    transform 0s linear,
    filter 0s linear;
  transition-delay: 0s;
}

@media (prefers-reduced-motion: reduce) {
  .t-stagger-line { transition: none !important; }
}
```

The `@media (prefers-reduced-motion: reduce)` guard at the bottom of the snippet is required — keep it. It zeroes the transition for users who have asked for less motion at the OS level.

## JavaScript orchestration

```js
const block = document.querySelector(".t-stagger");

function showText() {
  block.classList.remove("is-hiding");
  block.classList.remove("is-shown");
  void block.offsetHeight;
  block.classList.add("is-shown");
}
function hideText() {
  block.classList.add("is-hiding");
  block.classList.remove("is-shown");
  setTimeout(() => block.classList.remove("is-hiding"), 200);
}
```

## Group entry with keyframes

For a list or grid shown occasionally, fixed keyframes can stagger entry. Use transitions for values that must retarget during rapid interaction. Use the project’s `--ease-out` token; if absent, start with `cubic-bezier(0.23, 1, 0.32, 1)`.

```css
.item {
  opacity: 0;
  transform: translateY(8px);
  animation: fadeIn 300ms var(--ease-out) forwards;
}

.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
.item:nth-child(4) { animation-delay: 150ms; }

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

Cap the last item’s delay and keep controls usable. Add a reduced-motion rule that makes every item visible at once. See [tuning](../tuning.md) for total delay and finish time.
