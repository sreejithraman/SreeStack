# Scroll reveal

Use for occasional explanatory or marketing content. Keep frequently used functional content visible. Use the project’s `--ease-in-out`, or start with `cubic-bezier(0.77, 0, 0.175, 1)`.

```css
.reveal {
  clip-path: inset(0 0 100% 0);
  transition: clip-path 600ms var(--ease-in-out);
}

.reveal[data-visible] {
  clip-path: inset(0 0 0 0);
}
```

Trigger once with `IntersectionObserver`, or the installed motion library’s viewport hook, such as `useInView` with `{ once: true, margin: "-100px" }`. Repeated reveals should not interrupt reading. Show content immediately for reduced motion, failed initialization, and unsupported APIs. Check mask/clip rendering on target browsers.
