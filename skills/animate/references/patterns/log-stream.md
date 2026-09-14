# Log stream

## When to use

Show real status entries or logs in a fixed-height viewport. Move by a few lines per step, with a pause to read and fades at the edges. A cloned copy can hide the wrap in a decorative loop; keep it out of the accessibility tree.

Use the application’s real state to decide when to advance or stop. For reduced motion, stop the loop and expose useful content without clipping it to an unreadable region.

## HTML usage

```html
<div class="t-reason">
  <div class="t-reason-viewport">
    <div class="t-reason-scroll">
      <div class="t-reason-text">
        <p>…transcript…</p>
      </div>
    </div>
  </div>
</div>
```

The card clips a tall transcript; JS steps the scroll up
--reason-lines lines every --reason-hold and clones
.t-reason-text once so the offset can wrap by one copy's
height mid-hold — the loop never shows a jump. The edge fades
are a mask on the viewport (not gradients painted over the
text), so the card background can be anything.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--reason-hold` | `840ms` |
| `--reason-step` | `500ms` |
| `--reason-lines` | `2` |
| `--reason-fade` | `28px` |
| `--reason-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --reason-hold: 840ms;
  --reason-step: 500ms;
  --reason-lines: 2;
  --reason-fade: 28px;
  --reason-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-reason { position: relative; overflow: hidden; }
.t-reason-viewport {
  position: absolute;
  inset: 0;
  overflow: hidden;
  /* Edge fades are a mask, not painted gradients, so the card
     background can be anything. */
  -webkit-mask-image: linear-gradient(
    transparent 0,
    black var(--reason-fade),
    black calc(100% - var(--reason-fade)),
    transparent 100%);
  mask-image: linear-gradient(
    transparent 0,
    black var(--reason-fade),
    black calc(100% - var(--reason-fade)),
    transparent 100%);
}
.t-reason-scroll {
  position: absolute;
  left: 0;
  right: 0;
  transform: translateY(0);
  will-change: transform;
}
/* JS drives the tween:
     scroll.style.transition = 'transform var(--reason-step) var(--reason-ease)';
     scroll.style.transform  = 'translateY(-' + offset + 'px)';
   and wraps the offset by one copy's height with transition: none. */

@media (prefers-reduced-motion: reduce) {
  .t-reason-scroll { transition: none !important; transform: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript loop mechanics

This excerpt shows the stepping and wrap calculation. It is not a lifecycle controller. Before using it in a component:

- Retain both timer IDs and cancel them on completion, teardown, or a reduced-motion change. Schedule another step only while the real operation is active and motion is allowed.
- Mark the cloned text `aria-hidden="true"` and remove focus targets and duplicate IDs from it. Keep one accessible log.
- For reduced motion, bypass this loop, remove the clone, and show a readable log with normal document flow or user-controlled scrolling. Remove the absolute positioning and clipping that would hide its contents; resetting the transform alone is insufficient.
- When resuming motion, measure the current content and reset the offset before restarting. Bind preference and application-state changes through the project's lifecycle.

```js
// Clone the transcript once so the wrap has no visible jump, then step the
// scroll up --reason-lines lines every --reason-hold. The offset
// wraps by one copy's height the moment a step lands past it — the
// clone underneath makes the jump invisible.
const scroll = document.querySelector(".t-reason-scroll");
const text = scroll.querySelector(".t-reason-text");
scroll.appendChild(text.cloneNode(true));

const num = (name, fb) => {
  const v = parseFloat(
    getComputedStyle(document.documentElement).getPropertyValue(name)
  );
  return Number.isFinite(v) ? v : fb;
};

let offset = 0;
(function step() {
  setTimeout(() => {
    const lineH = parseFloat(getComputedStyle(text).lineHeight) || 18;
    const stepPx = lineH * num("--reason-lines", 2);
    const dur = num("--reason-step", 500);
    const ease = getComputedStyle(document.documentElement)
      .getPropertyValue("--reason-ease").trim() || "ease-out";
    offset += stepPx;
    scroll.style.transition = "transform " + dur + "ms " + ease;
    scroll.style.transform = "translateY(" + (-offset) + "px)";
    setTimeout(() => {
      const copyH = text.offsetHeight;
      if (offset >= copyH) {
        offset -= copyH;
        scroll.style.transition = "none";
        scroll.style.transform = "translateY(" + (-offset) + "px)";
        void scroll.offsetWidth; // flush before the next tween
      }
      step();
    }, dur + 30);
  }, num("--reason-hold", 1200));
})();
```
