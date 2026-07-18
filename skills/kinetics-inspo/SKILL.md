---
name: kinetics-inspo
description: Kinetics pattern search for interface motion. Use when the user mentions Kinetics or kinetics.colorion.co.
---

# Kinetics Inspo

## Loop

1. Run the bundled search from this skill directory:

   ```bash
   node scripts/search.mjs "toast notification overshoot" --limit 6
   ```

   Search by requested interaction, interface role, and motion character; vary the vocabulary when the shortlist is weak. Use `--json` for exact keywords and pinned source fields.

   Open [catalog.json](references/catalog.json) for source auditing or exhaustive entry inspection; normal discovery runs through the script.

   Complete when each leading candidate matches all three dimensions of the request.

2. Fetch the `Source` URL printed by the search:

   ```bash
   SOURCE_URL="$(node scripts/search.mjs --source)"
   curl -L --fail --silent --show-error -o /tmp/kinetics-body.html "$SOURCE_URL"
   ```

   Complete when `/tmp/kinetics-body.html` contains `.card` blocks from the pinned catalog revision.

3. Locate every leading candidate and read its whole `.card` block: parameter readout, description, CSS, React, and prompt where present.

   ```bash
   rg -n -F '<div class="name">Toast Overshoot</div>' /tmp/kinetics-body.html
   ```

   When a card delegates mechanics to demo classes or JavaScript, fetch the matching `public/css/effects-*.css` or `public/js/main.js` file at the catalog's pinned `source.ref`.

4. Use the findings:

   - For inspiration, return effect names, selection reasons, transferable mechanics, and links to `https://kinetics.colorion.co` or the source.
   - For implementation, fit the mechanic to the current component, style system, input modes, and reduced-motion state. Check the upstream license or explicit permission before a direct port; otherwise create an independent implementation from the observed behavior.

## Done

Done means every material recommendation is backed by a semantically ranked catalog entry and its fetched source. An implementation also has exercised interaction and reduced-motion behavior, with copied code covered by reuse permission.
