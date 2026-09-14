# Crossfade with overlap

Use when two visible states overlap poorly during a swap. First tune opacity and timing. A small blur can soften remaining overlap if it fits the design and performs well.

```css
.content {
  transition:
    filter 200ms ease,
    opacity 200ms ease;
}

.content.transitioning {
  filter: blur(2px);
  opacity: 0.7;
}
```

Start near 2px and measure the actual surface; larger blur costs more. Keep one accessible content state and avoid duplicate announcements. For reduced motion, use a short fade or instant swap without blur.
