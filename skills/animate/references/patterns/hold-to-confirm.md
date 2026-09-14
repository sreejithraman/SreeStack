# Hold to confirm

Use when the product calls for a deliberate hold. The fill shows elapsed hold time and clears promptly on release. Use the project’s `--ease-out` token; if absent, start with `cubic-bezier(0.23, 1, 0.32, 1)`.

```css
.overlay {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms var(--ease-out); /* release: snappy */
}

.button:active .overlay {
  clip-path: inset(0 0 0 0);
  transition: clip-path 2s linear;             /* press: slow and deliberate */
}

.button:active {
  transform: scale(0.97);
}
```

Use linear timing for elapsed progress. This CSS does not perform confirmation: add input handling, cancel on release or pointer cancellation, and provide an accessible way to confirm. Reduced motion must retain clear progress and outcome feedback. Do not make a destructive action depend on a CSS transition event.
