# PR title and body

Name the concrete resulting behavior in the title. In the body, lead with that
behavior and why it matters. Follow the repository's PR template and domain
glossary. Otherwise use Summary, Evidence, and Merge Danger; a small PR can use
a sentence for each or concise prose.

Include what changed, why, its user or developer effect, and the root cause of
a fix. For stacks, name the immediate base, link adjacent PRs when available,
and distinguish this layer's effect from dependent work.

## Summary

Use a visual only when it makes the change easier to understand. Put it beside
its explanation and keep the participants and boundaries that matter:

| Question | Useful view |
| --- | --- |
| How does the decision work? | Pseudocode |
| What runs, and who owns it? | Call tree |
| Where do UI state and components belong? | Component/view tree |
| Which files own which responsibilities? | Shallow file tree |
| How do components interact? | Mermaid sequence or flow diagram |
| What changed in a familiar shape? | Diff sketch |
| What is the new or copyable shape? | Complete short block |

For example, a diff sketch can show changed request ordering:

```diff
 on search(query)
-  publish(await fetchResults(query))
+  generation = startRequest()
+  results = await fetchResults(query)
+  if generation is current
+    publish(results)
```

Label sketches as illustrative when they are not exact code. Include surrounding
structure when it explains ownership or execution. Choose several views only
when each answers a different question; simple changes often need prose alone.

## Evidence

Report observed checks and results. For fixes, pair the failure with success on
the same scenario when available. Name the workflow or command, expected
behavior, and observed outcome. Link logs and artifacts instead of dumping runs.
Reuse [showroom](../../showroom/SKILL.md)'s checked demonstrations and access links.
For UI, use comparable before/after views when useful; for other behavior,
use tests, terminal output, API responses, or workflow observations.

Evidence must apply to the described revision, configuration, and scenario.
Distinguish local checks, CI, and human approval; label pending, blocked, and
unrun checks. Disclose unavailable before-state evidence and show the observed
after state. New features can show acceptance without inventing a prior failure.
Keep extra checks within scope; report missing proof rather than filling gaps
with claims.

## Merge Danger

Explain whether a code revert restores the prior state (**two-way door**) or
whether effects need restoration or coordination beyond a revert (**one-way
door**). Name the rollback path and its limits. Persisted-data deletion, schema
rewrites, public contracts, and removed resources deserve concrete treatment.

Name affected users, platforms, consumers, data, and dependent stack layers.
Include material rollout ordering, compatibility, deployment, and restoration
requirements. Separate demonstrated effects from assumptions; use
[blast-radius](../../blast-radius/SKILL.md) for an uncertain contract. Judge the
consequences, not the diff size or an unsupported risk label. A small reversible
change needs only a short statement of scope and rollback.
