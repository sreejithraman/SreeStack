---
name: web-component-inspiration
description: Find and assess web UI component references for a feature.
---

# Web Component Inspiration

Find web patterns that could make a real feature clearer, more useful, or more
distinct. Treat “the current design is stronger” as a valid result.

## Frame the opportunity

Inspect the request, current interface, and nearby code. Write a short fit brief
covering the feature’s job, location, web stack, existing visual and interaction
rules, and material constraints such as accessibility, motion, performance,
package policy, or paid code.

This catalog is web-only. For a SwiftUI or UIKit target, state that boundary
and use `ui-design` with `swiftui` or `uikit` instead. Consult these web sources
in [sources.md](references/sources.md) only when the user explicitly wants
mechanic-level inspiration across platforms, and label the fidelity limits.

Identify only the parts where a different pattern could improve a user outcome,
such as clearer feedback, faster scanning, spatial context, or a deliberate
moment of delight. Drop opportunities that add novelty without value.

Use `ui-design` to judge visual fit and browser behavior or accessibility. Use
`animate` when motion is part of the opportunity.

## Scout live sources

Read [sources.md](references/sources.md). Honor a source the user names;
otherwise choose the source groups that fit the opportunity and stack. Follow
the linked guide when selecting Kinetics or Forever Components. Search other
catalogs live using the interface role, user action, visual character, and
mechanic rather than relying on a component’s marketing name.

Build a candidate pool broad enough to reveal distinct tradeoffs. Open the
exact demo or documentation page for every serious candidate. Then read
[source-code.md](references/source-code.md), inspect the public source without
changing the project, and record:

- what the live example does;
- the exact demo, documentation, and source URLs, plus a revision for repository
  source;
- its framework, packages, assets, and setup cost;
- whether access is free, paid, or unclear, and the current reuse terms before
  suggesting a direct port;
- keyboard, touch, focus, reduced-motion, and narrow-screen gaps;
- likely runtime, rendering, or bundle costs.

Group candidates by the user-facing pattern, not the source. Keep alternatives
only when they expose a real tradeoff, such as lower implementation cost, better
accessibility, or a quieter visual treatment. Rank product fit first, then
clarity, implementation cost, accessibility, and performance. Use novelty only
to break a close tie.

## Present the shortlist

Return only enough checked picks to expose the useful choices. Honor a count the
user specifies when that many genuinely distinct, checked candidates exist;
otherwise return the supported set and explain the shortfall. For each, include:

- the opportunity it serves;
- the component and source with a direct demo link and a public source link when
  available;
- how its code can be inspected or integrated, or what access is missing for an
  inspiration-only pick;
- why it fits this product;
- the mechanic or behavior worth borrowing;
- implementation cost, packages, and assets;
- cost, terms, access, motion, or speed concerns.

End with a first choice and a plain “skip it” option when the gain looks weak.
For an ideas-only request, leave the project unchanged and let the user choose.

## Adapt a chosen pattern

Build only when the user has chosen a pick or asked you to choose and implement
one. Follow the build rules in [source-code.md](references/source-code.md). Fit
the pattern to the product’s components and tokens. Recreate the useful mechanic
when that reduces code, dependencies, or licensing obligations. Check the exact
reuse terms before copying source.

Exercise the changed path with the relevant keyboard, pointer, touch,
reduced-motion, and narrow-screen conditions. Use `manual-verify` when the
result needs hands-on workflow judgment, then use `showroom` for visual proof.

## Done

Discovery is done when every pick has a distinct reason to exist, checked
tradeoffs, and live demo and source links—or is clearly marked
inspiration-only when public source is unavailable. A build is done when the
adapted behavior works in the real interface, the relevant condition checks
pass, useful visual proof is supplied through `showroom`, and any check that
could not run is named with its limit.
