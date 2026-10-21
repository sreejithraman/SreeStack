---
name: correct
description: Investigate and prevent recurring agent mistakes in a repository. Use when asked to find repeated corrections or turn known failure patterns into architecture changes and enforceable checks.
---

# Correct

Own recurring failure prevention: connect actual mistakes to a repair that
prevents the same failure mechanism. Use
[Engineering Principles](../engineering-principles/SKILL.md) for design decisions
and enforcement selection, and the shared
[guard proof](../codebase-design/references/preventing-mistakes.md) for historical
rejection and repaired-path success.

## Establish the evidence

Honor the requested repository, area, history window, and finish line. A request
for a plan ends with a supported plan; a request to fix recurring mistakes
includes implementation and verification within that scope.

Start with the supplied examples. Otherwise choose and report a bounded recent
history window, then inspect commits, reverts, substantive review feedback, and
instructions or comments that explain past failures. Follow promising records
to their actual diffs. When conversations could explain a correction, use scoped
T3 thread search/read or available local session logs. Report searched sources,
coverage limits, and unavailable records; bounded search is not exhaustive recall.

Group examples by failure mechanism. Count separate occurrences, not several
records of one incident. Cite at least two occurrences before calling a class
recurring. Keep single incidents and suspected risks distinct. Check current
code and enforcement: an old mistake that is already prevented is evidence of
a resolved class, not a reason to rebuild its guard.

Rank the live classes by observed frequency, impact, and current exposure.
Keep observed facts separate from inferred causes. Finish this step with cited
examples, a current path that still permits each failure, and the limits of the
search. If no recurring class is supported, say so rather than inventing one.

## Choose and test the repair

For each class worth addressing, identify the invariant and its owner. Apply
[Encode Lessons in Structure](../engineering-principles/references/encode-lessons-in-structure.md)
and explain why a higher-level repair would not help or would cost too much.

Resolve technical uncertainty with focused
[architecture experiments](../improve-codebase-architecture/references/experiments.md).
Use the experiment evidence to decide routine technical questions within the
requested scope.

Return a prioritized plan connecting each class to:

- Its occurrences, frequency, impact, and current exposure.
- The invariant, owner, proposed repair, and enforcement mechanism.
- The historical failing case and repaired path that will prove the guard.
- Experiment results, tradeoffs, affected callers, migration steps, and checks.

Label proposed proof separately from checks already run. Include reproduction
commands and artifact paths for experiments, and name unresolved facts with the
next check that would settle them. Keep the plan in chat unless the user or
project requests another destination. No permanent rule table is required.

## Implement within the requested finish line

For a planning request, hand back the evidence and recommendation for review.
For an authorized repair, migrate the affected callers and examples, implement
the guard, and prove historical rejection and repaired-path success using the
shared guidance. Verify legitimate supported paths too; narrowing the accepted
behavior to hide the failure is not prevention.

Use [orchestration](../orchestration/SKILL.md) for bounded assignments and
[review-fix-loop](../review-fix-loop/SKILL.md) for behavior or procedure changes.
Use [verify](../verify/SKILL.md) when the repair changes a user workflow.
Requested stacked delivery uses [gh-stack](../gh-stack/SKILL.md); explicitly
requested goal or swarm execution uses [goal-swarm](../goal-swarm/SKILL.md).
The requested finish line governs PR publication and merging.

Report each class as planned, prevented, partly covered, resolved already, or deferred,
with its evidence, checks, and remaining exposure. Planning is complete when
the recommendations have traceable evidence and a usable migration/proof plan.
Implementation is complete when the selected repairs and checks pass, required
review is settled, and remaining classes have explicit dispositions.
