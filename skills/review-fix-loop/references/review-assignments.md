# Review assignments

Use [Review](../../review/SKILL.md) and the canonical
[review brief](../../review/references/review-brief.md) for every assessment.
Report material issues noticed outside the assigned lens.

| Assignment | Criteria |
| --- | --- |
| Primary | Correctness, regressions, security/data loss, test gaps; [Spec](../../review/references/spec.md) and [Standards](../../review/references/standards.md) |
| Ponytail | Proven simplification, deletion, reuse, and root-cause repairs using [Ponytail](../../review/references/ponytail.md) |
| Thermo | Structure, boundaries, abstractions, types, and concrete design improvements using [Thermo](../../review/references/thermo.md) |
| Adversarial | Challenge assumptions and trace material failure scenarios using [Adversarial](../../review/references/adversarial.md); required for substantial changes under Prepare |
| Additional reviewer | General review across Review's applicable criteria |

Primary also owns Review's applicable indirect-consumer and React/Next checks,
including react-best-practices and React Doctor evidence.

## Select reviewers

Map the required assessments chosen in Prepare to the required-review row in
[model defaults](../../orchestration/references/agent-routing.md#model-defaults).
For every independent review round, add one general reviewer from each named
additional-review pool. These supplement required assessments. Parent-only
prose review needs no additional agents.

Resolve candidates through agent routing and record unavailable targets with
reasons. Within each pool, use a tool-backed uniform random draw among eligible
models. Use the sole eligible candidate when only one remains; skip an empty
pool. Record one mapping per loop and retain it through fixes unless the user
changes the selection policy. Each round is a new independent assignment.

## Use the selected provider

Run a read-only Review assignment in the selected provider's harness through
Orchestration. Include the applicable checked-in provider reference linked from
[Review](../../review/SKILL.md), alongside any assigned lens. OpenCode and Gemini
reviews use these repository instructions without installing plugins or invoking
native review commands. Keep the selected model, effort, complete snapshot, and
common review contract. Record which references the reviewer read; an unread
required reference is incomplete coverage.

## Handle failures

Use agent routing's recovery for required reviewers and uncertain dispatches.
Additional reviewers override its transient-retry default: on a confirmed quota
or rate limit, authentication failure, unavailable model, runtime error, or
incomplete review, skip that assignment for the rest of the loop. Retain partial
findings for Review Sweep and continue the other assignments. Do not retry,
redraw, substitute providers, or add a replacement for a skipped slot.
Skipped additional coverage does not block completion.

Review Sweep resolves overlapping or conflicting findings using its
[classification](../../review-sweep/references/classification.md).
