---
name: correct
description: Use when asked to investigate recurring agent mistakes or prevent a known recurring failure pattern.
---

# Correct

Investigate recurring agent mistakes and connect evidenced failure classes to
structural repairs that prevent the same mechanism from recurring. Start from
supplied examples or a bounded repository history window and a requested finish
line (plan vs authorized repair). Leave ranked live failure classes with a
proof-backed prevention plan—and, when repairs are authorized, implemented guards
verified against historical failures and supported paths. You are done when
planning returns traceable evidence and concrete guard-proof plans, or
authorized repairs and checks pass with explicit dispositions for remaining
classes.

Use [Engineering Principles](../engineering-principles/SKILL.md) for design and
enforcement choices and
[preventing recurring mistakes](../codebase-design/references/preventing-mistakes.md)
for historical rejection and repaired-path guard proof.

## Establish the evidence

Honor the requested repository, area, history window, and finish line. A
planning request ends with a supported plan; a repair request includes
implementation and verification within that scope.

Start from supplied examples; otherwise pick and report a bounded recent window
and inspect commits, reverts, substantive review feedback, and explanatory
comments, following leads to their actual diffs. Use scoped T3 thread
search/read or local session logs when conversations explain a correction.
Report searched sources, coverage limits, and unavailable records.

Group by failure mechanism and count independent occurrences (never multiple
records of one incident). Require at least two independent occurrences before
calling a class recurring, keeping single incidents and suspected risks
separate. Check current code and enforcement: an already-prevented mistake is a
resolved class, not work to rebuild.

Rank live classes by frequency, impact, and current exposure, separating observed
facts from inferred causes. Done when each class cites examples, names a live
path that still permits the failure, and notes search limits (or reports that no
recurring class is supported).

## Choose and test the repair

For each class worth addressing, identify the invariant and its owner, apply
[Encode Lessons in Structure](../engineering-principles/references/encode-lessons-in-structure.md),
and explain why higher-level enforcement would not work or would cost too much.
Settle technical uncertainty with focused
[architecture experiments](../codebase-design/references/experiments.md).

Return a prioritized plan in chat (unless another destination was requested; no
permanent rule table is required) connecting each class to:
- occurrences, frequency, impact, and current exposure;
- invariant, owner, proposed repair, and enforcement mechanism;
- historical failing case and repaired path that will prove the guard;
- experiment results, tradeoffs, affected callers, migration steps, and checks.

Separate proposed proof from checks run, include experiment commands and
artifact paths, and name unresolved facts with their next settling check.

## Implement within the requested finish line

Planning requests stop after returning the plan. For authorized repairs, migrate
affected callers and examples, implement the guard, and prove both historical
rejection and repaired-path success—including legitimate supported paths (never
hide failures by narrowing valid behavior).

Use [Orchestration](../orchestration/SKILL.md) for bounded assignments,
[Swarm](../swarm/SKILL.md) for bounded parallel investigation or implementation,
[Verify](../verify/SKILL.md) when repairs change a user workflow, and
[gh-stack](../gh-stack/SKILL.md) when stacked delivery is requested. Multi-outcome
program execution, behavioral evaluation beyond guard proof, and PR/merge
delivery follow the caller's workflow and requested finish line.

Report each class as `planned`, `prevented`, `partly covered`,
`resolved already`, or `deferred`, with evidence, checks, and remaining exposure.
