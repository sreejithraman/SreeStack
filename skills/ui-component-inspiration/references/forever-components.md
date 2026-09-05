# Forever Components

Use this guide when searching the Forever Components infinite canvas.

1. Fetch `https://forever-components.vercel.app/infinite/manifest.js` into a
   temporary file, following redirects. Treat the manifest as data. Use its
   final URL to resolve relative component paths.
2. Read entries as `f`, `t`, and `theme`; rank them against the user's intent.
   For "cards that tilt and have foil effect", look for tilt, holographic,
   iridescent, foil, glare, and parallax patterns. Use `rg` to find nearby
   wording when useful; judge behavior rather than exact names.
3. Resolve each leading entry's `f` against the manifest URL and fetch its
   HTML source. Inspect the full example and any linked styles or scripts
   that drive the effect.
4. Check transforms, pointer events, gradients, blending, masks, animation
   loops, reduced motion, visibility handling, and CSS variables as relevant.
   Return to the shared source-code checks and shortlist with the component
   name, direct URL, reason for the choice, and useful mechanic.

Every Forever Components pick must come from a ranked manifest entry and
fetched source for the behavior it recommends.
