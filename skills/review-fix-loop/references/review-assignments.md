# Review assignments

Use [Review](../../review/SKILL.md) and the canonical
[review brief](../../review/references/review-brief.md) for every assessment.
Report material issues noticed outside the assigned lens.

| Assignment | Criteria |
| --- | --- |
| Primary | Correctness, regressions, security/data loss, test gaps; [Spec](../../review/references/spec.md) and [Standards](../../review/references/standards.md) |
| Ponytail | Proven simplification, deletion, reuse, and root-cause repairs using [Ponytail](../../review/references/ponytail.md) |
| Thermo | Structure, boundaries, abstractions, types, and concrete design improvements using [Thermo](../../review/references/thermo.md) |
| Adversarial | Challenge assumptions and trace material failure scenarios using [Adversarial](../../review/references/adversarial.md) |

Primary also owns Review's applicable indirect-consumer and React/Next checks,
including `react-best-practices` and React Doctor evidence. A single-reviewer
repair pass gives that reviewer the criteria and references of every row the
repair made stale or newly required.

## Select reviewers

Map each required assessment to its named review default in
[model defaults](../../orchestration/references/models.md#model-defaults).
Record unavailable targets with reasons, and retain the mapping per loop
through repairs and any superseded first pass unless the selection policy
changes.

## Use the selected provider

Run a read-only Review assignment in the selected provider's harness through
Orchestration. Include the applicable checked-in provider reference linked from
Review alongside any assigned lens. Gemini reviews use
these repository instructions without installing plugins or invoking native
review commands; when Gemini runs an assigned review, the assigned criteria —
including indirect consumers, missing proof, and test gaps — override
`gemini.md`'s changed-lines-only, cursory-test, and verify/ensure constraints.
Keep the selected model, effort, complete snapshot, and common review contract.
Record which references the reviewer read; an unread required reference is
incomplete coverage.

## Handle failures

Use Orchestration's
[recovery](../../orchestration/references/reuse-and-recovery.md#recover-work)
for every reviewer at every stage and for uncertain dispatches. A reviewer
that stays unknown after recovery is an incomplete review and gets a fresh run.

Review Sweep resolves overlapping or conflicting findings using its
[classification](../../review-sweep/references/classification.md).
