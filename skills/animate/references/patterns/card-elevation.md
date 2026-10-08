# Card elevation

For a shadow change that passes the motion gate, start with a direct `box-shadow`
transition on a small isolated card. When measurement shows paint cost in larger
surfaces or grids, try fading two fixed shadows instead. Compare paint and layer
cost on the target page; opacity does not guarantee that a shadow paints only once.
See [web.dev: high-performance animations](https://web.dev/articles/animations-guide).

```css
.elevation-card {
  position: relative;
  isolation: isolate;
  background: var(--card-surface, white);
}
.elevation-card::before,
.elevation-card::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  pointer-events: none;
}
.elevation-card::before {
  box-shadow: var(--card-shadow-rest, 0 2px 10px rgb(0 0 0 / 12%));
}
.elevation-card::after {
  box-shadow: var(--card-shadow-raised, 0 12px 32px rgb(0 0 0 / 18%));
  opacity: 0;
}
.elevation-card:focus-within::before { opacity: 0; }
.elevation-card:focus-within::after { opacity: 1; }
@media (hover: hover) and (pointer: fine) {
  .elevation-card:hover::before { opacity: 0; }
  .elevation-card:hover::after { opacity: 1; }
}
@media (prefers-reduced-motion: no-preference) {
  .elevation-card::before,
  .elevation-card::after {
    transition: opacity 180ms var(--ease-out, ease-out);
  }
}
```

Map surface and shadow values to product tokens. Crossfade both shadows so the
raised state ends with one shadow rather than their sum. The isolated stacking
context keeps negative layers with the card; provide its opaque surface and test
ancestor clipping. Both pseudo-elements are occupied. If the component uses one
for a stretched link, hit area, or decoration, choose another wrapper or direct
shadow transition. Keep the actual keyboard focus ring visible; elevation is
optional emphasis. Reduced motion changes shadow state instantly.
