# Number pop-in

## When to use

Counters, prices, balances, or any number that updates and should re-enter from a direction with blur. Each character animates independently and the last two digits stagger so decimal digits enter in sequence.

## HTML usage

```html
<span class="t-digit-group is-animating">
  <span class="t-digit">1</span>
  <span class="t-digit">2</span>
  <span class="t-digit" data-stagger="1">.</span>
  <span class="t-digit" data-stagger="2">3</span>
</span>
```

Replay:
  - Remove `.is-animating`, re-render digits (or swap text),
    force a reflow, then re-add `.is-animating`.
  - Use data-stagger="1", "2", … to delay individual
    digits by `n * var(--digit-stagger)`.

Direction:
  --digit-dir-x / --digit-dir-y are unit-less multipliers
  (e.g. 1, -1, 0) applied to --digit-distance.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--digit-dur` | `500ms` |
| `--digit-distance` | `8px` |
| `--digit-stagger` | `70ms` |
| `--digit-blur` | `2px` |
| `--digit-ease` | `cubic-bezier(0.34, 1.45, 0.64, 1)` |
| `--digit-dir-x` | `0` |
| `--digit-dir-y` | `1` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --digit-dur: 500ms;
  --digit-distance: 8px;
  --digit-stagger: 70ms;
  --digit-blur: 2px;
  --digit-ease: cubic-bezier(0.34, 1.45, 0.64, 1);
  --digit-dir-x: 0;
  --digit-dir-y: 1;
}
```

## CSS

```css
@keyframes t-digit-pop-in {
  0%   {
    transform: translate(
      calc(var(--digit-distance) * var(--digit-dir-x)),
      calc(var(--digit-distance) * var(--digit-dir-y))
    );
    opacity: 0;
    filter: blur(var(--digit-blur));
  }
  100% { transform: translate(0, 0); opacity: 1; filter: blur(0); }
}

.t-digit-group {
  display: inline-flex;
  align-items: baseline;
}
.t-digit {
  display: inline-block;
  will-change: transform, opacity, filter;
}
.t-digit-group.is-animating .t-digit {
  animation: t-digit-pop-in var(--digit-dur) var(--digit-ease) both;
}
.t-digit-group.is-animating .t-digit[data-stagger="1"] {
  animation-delay: var(--digit-stagger);
}
.t-digit-group.is-animating .t-digit[data-stagger="2"] {
  animation-delay: calc(var(--digit-stagger) * 2);
}

@media (prefers-reduced-motion: reduce) {
  .t-digit-group .t-digit { animation: none !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

```js
// Replay the digit pop-in: remove .is-animating, swap the digit spans,
// force a reflow, then re-add .is-animating. Mark the last two digits
// with data-stagger="1" / "2" so they ride in 1× / 2× --digit-stagger
// behind the leading digits.
const group = document.querySelector(".t-digit-group");

function setDigits(str) {
  group.classList.remove("is-animating");
  group.replaceChildren();
  const chars = str.split("");
  chars.forEach((ch, i) => {
    const span = document.createElement("span");
    span.className = "t-digit";
    span.textContent = ch;
    if (i === chars.length - 2) span.dataset.stagger = "1";
    else if (i === chars.length - 1) span.dataset.stagger = "2";
    group.appendChild(span);
  });
  void group.offsetHeight; // force reflow
  group.classList.add("is-animating");
}
```
