---
name: ui-component-inspiration
description: Find a small, checked set of strong UI component references for a feature.
disable-model-invocation: true
---

# UI Component Inspiration

Find ideas that make a real feature clearer, more useful, or more distinct. A result that says the feature needs no extra component is valid.

## Scout

1. Read the request and inspect the current interface and code when they exist. Write a short fit brief that states the feature's job, where it appears, the front-end stack, nearby visual rules, and hard limits such as access needs, motion, speed, package policy, and paid code.
2. Name at most three parts of the feature where a fresh pattern could help. Tie each slot to a user need, such as clearer feedback, faster scanning, spatial context, or a rare moment of delight. Drop slots that would add flair without value.
3. Read [sources.md](references/sources.md). Honor any source the user names; otherwise pick the source groups that fit the slots and stack. Follow the linked search guide for Kinetics or Forever Components when selected; search live catalogs for the other sources. Treat names as hints: search with the interface role, user action, visual character, and nearby terms.
4. Gather about twice as many candidates as the final list needs. Open the exact demo or docs page for each serious candidate. Read [source-code.md](references/source-code.md), inspect the public source without changing the project, and record:

   - what the live example does;
   - the docs and source URLs, plus a revision when the source lives in a repository;
   - its framework, packages, and setup cost;
   - whether it is free, paid, or unclear;
   - the current reuse terms before suggesting a direct port;
   - keyboard, touch, focus, reduced-motion, and small-screen gaps;
   - likely speed or bundle costs.

5. Group candidates by the user-facing pattern, not the source's name. Keep one main pick from each group. Keep an alternate only when it offers a real tradeoff, such as less code, better access, or a quieter look.
6. Rank fit first, then clarity, product match, build cost, access, and speed. Use novelty only to break a close tie.

## Return

Give one to five checked picks. For each pick, include:

- the opportunity it serves;
- the component and source name with a direct link;
- how its code can be inspected or added;
- why it fits this product;
- the small part worth borrowing;
- build cost and packages;
- cost, terms, access, motion, or speed concerns.

End with a clear first choice and a plain "skip it" option when the gain looks weak. For an ideas-only request, leave the project unchanged and ask the user which pick they want.

## Build

When the user has chosen a pick or has asked you to choose and build, follow the build rules in [source-code.md](references/source-code.md). Fit the pattern to the product's own components and tokens. Recreate the useful behavior instead of copying a full demo when that cuts code or avoids terms. Check reuse terms before copying source. Exercise the changed path, including keyboard, touch, reduced motion, and narrow screens.

## Done

Discovery is done when every pick has live docs and source links, a distinct reason to exist, and checked tradeoffs, or is marked as inspiration-only when no public source exists. A build is done when the chosen behavior works on the real interface and the checks above pass or any test limit is clear.
