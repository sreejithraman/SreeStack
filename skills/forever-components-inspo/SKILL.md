---
name: forever-components-inspo
metadata:
  owner: sree
description: Forever Components manifest search for UI inspiration. Use when the user mentions Forever Components, the infinite canvas URL, or wants design/code inspiration from that site.
---

# Forever Components Inspo

Catalog URL: `https://forever-components.vercel.app/infinite/manifest.js`

## Loop

1. Fetch the manifest:

   ```bash
   curl -L -o /tmp/forever-manifest.js https://forever-components.vercel.app/infinite/manifest.js
   ```

2. Read entries as `f`, `t`, and `theme`; rank them semantically against the user's prompt. Treat wording as intent over exact keywords.

   Example: "cards that tilt and have foil effect" should rank these highly:

   - `cards/11-holographic-foil-card.html`
   - `cards/08-holographic-iridescent.html`
   - `cards/01-tilt-parallax.html`
   - `css-3d/06-parallax-tilt.html`

3. Use `rg` only to discover nearby vocabulary when semantic ranking needs help:

   ```bash
   rg -n -i "foil|tilt|holo|glare|shine|shimmer|irides|chrome|metal|card|glass|parallax" /tmp/forever-manifest.js
   ```

4. Fetch source for the strongest candidates. Build each URL as `https://forever-components.vercel.app/infinite/{f}`:

   ```bash
   curl -L -o /tmp/forever-example.html https://forever-components.vercel.app/infinite/cards/11-holographic-foil-card.html
   ```

5. Inspect source mechanics:

   ```bash
   rg -n -i "transform|rotateX|rotateY|pointer|mousemove|gradient|mix-blend|mask|background|requestAnimationFrame|prefers-reduced-motion|document.hidden|--" /tmp/forever-example.html
   ```

## Use The Findings

For inspiration requests, return component names, source URLs, selection reasons, and transferable mechanics.

For implementation requests, adapt the mechanics into the current repo. Direct ports need explicit user intent plus licensing/attribution checked first.

## Done

Done means the answer or implementation is backed by manifest-ranked candidates and fetched source for every component that materially informed the result.
