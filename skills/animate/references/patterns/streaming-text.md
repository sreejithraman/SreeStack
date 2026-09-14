# Streaming text

## When to use

Model output arriving word by word — chat responses, AI completions, any streamed paragraph. JS wraps each word in a span; words rest visible, and a replay wipes them all, then resolves them in order through opacity plus a small blur, one every `--stream-gap`.

Use this when whole words arrive together. Each word fades from blurred to clear rather than appearing one character at a time.

## HTML usage

```html
<div class="t-stream">Your streamed paragraph…</div>
```

JS wraps each word in a .t-stream-w span; spans rest visible.
To replay the stream: wipe every span with transition: none,
force one reflow, restore the transition, then add .is-in word
by word every --stream-gap — each word resolves through
opacity + a small blur over --stream-fade.

## Tunable variables

| Variable | Default |
| --- | --- |
| `--stream-gap` | `60ms` |
| `--stream-fade` | `350ms` |
| `--stream-blur` | `1px` |
| `--stream-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

Map these defaults to the project’s tokens. Install only the variables this pattern needs.

```css
:root {
  --stream-gap: 60ms;
  --stream-fade: 350ms;
  --stream-blur: 1px;
  --stream-ease: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## CSS

```css
.t-stream-w {
  opacity: 0;
  filter: blur(var(--stream-blur));
  transition:
    opacity var(--stream-fade) var(--stream-ease),
    filter var(--stream-fade) var(--stream-ease);
}
.t-stream-w.is-in {
  opacity: 1;
  filter: blur(0);
}

@media (prefers-reduced-motion: reduce) {
  .t-stream-w { transition: none !important; filter: none !important; opacity: 1 !important; }
}
```

Keep the reduced-motion CSS and make the final useful state available without movement. Follow the [implementation checks](../implementation.md) for JavaScript cancellation and preference changes.

## JavaScript orchestration

```js
// Wrap each word in a span once; stream() wipes them (no transition)
// and resolves them in order, one every --stream-gap.
const block = document.querySelector(".t-stream");
const words = block.textContent.trim().split(/\s+/);
block.textContent = "";
const spans = words.map((w, i) => {
  const s = document.createElement("span");
  s.className = "t-stream-w is-in";
  s.textContent = w;
  block.appendChild(s);
  if (i < words.length - 1) block.appendChild(document.createTextNode(" "));
  return s;
});

const gap = parseFloat(
  getComputedStyle(document.documentElement).getPropertyValue("--stream-gap")
) || 60;

function stream() {
  // Snap back to nothing without animating the wipe itself.
  spans.forEach((s) => {
    s.style.transition = "none";
    s.classList.remove("is-in");
  });
  void block.offsetWidth; // flush the wipe
  spans.forEach((s) => { s.style.transition = ""; });
  (function next(n) {
    if (n >= spans.length) return;
    spans[n].classList.add("is-in");
    setTimeout(() => next(n + 1), gap);
  })(0);
}
```
