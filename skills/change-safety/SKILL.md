---
name: change-safety
description: Assess a code change's blast radius beyond its diff. Use for subtle contract changes, migrations, or an explicit question about what else could break.
---

# Change Safety

Find the consequential effects a symbol search could miss. Keep the investigation proportional to the changed contract and the cost of being wrong.

1. **Anchor the change.** Identify the intended behavior, affected revision or diff, changed symbols and data shapes, and the relevant callers. Include uncommitted work when it is in scope. State any ambiguity in the change being assessed.
2. **Trace outward.** Follow observable boundaries that can carry the change farther than a direct call: persisted data, wire formats, generated code, other languages, background jobs, lifecycle ordering, library behavior at the pinned version, and feature flags. Search only paths relevant to a plausible failure.
3. **Name the safety assumptions.** Write the smallest set of facts on which the change's safety depends and a concrete bad case if each fact is false. Distinguish a real failure path from an imagined caller or a generic possibility.
4. **Test the important facts.** Prefer an existing test or runnable product path. When it is cheap and useful, make a small check that executes the real code and would fail for the bad case; keep a one-off probe outside the product diff unless it is a valuable regression test. Use isolated fixtures or a safe test mode for code with consequential side effects. Record the command, observed result, and relevant revision without exposing credentials or private data. A code citation or argument can support a fact when execution is unavailable, but label the remaining uncertainty.
5. **Report the verdict.** State what changed, the assumptions and their proof level, confirmed risks with likely impact, risks checked and cleared, and the cheapest remaining check. Use `unproven` for a critical fact you could not verify. Do not turn an incomplete check into a pass.

When the task is a code review, return findings to its review owner. When it includes a fix, verify the changed user workflow through `manual-verify` if product behavior needs hands-on acceptance.
