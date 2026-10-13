---
name: review-fix-loop
description: Review and fix a change through independent T3 review rounds. Use before handing off behavior or agent-procedure changes, or when asked to review and fix a branch, PR, or local diff.
---

# Review Fix Loop

The parent coordinates rounds. [Review](../review/SKILL.md) assesses one
snapshot; [Review Sweep](../review-sweep/SKILL.md) validates and fixes findings.
The caller owns commits, publication, replies, and merging.

## Prepare

Resolve the original base once using Review. Gather the complete snapshot,
requirements, and verification evidence with the canonical
[review brief](../review/references/review-brief.md). Keep the reviewed scope
stable while a round runs; a moving snapshot supersedes that round.

Choose coverage in this order, honoring explicit user requests:

| Change | Required assessment |
| --- | --- |
| Ordinary prose or wording only, with no procedure change | Parent review |
| Shared contracts, risky logic, multiple behaviors/authors, substantial code or instruction workflows | Primary, Ponytail, and Thermo, even for a small diff |
| Remaining small behavior or agent-procedure change | One independent primary reviewer |

Finish preparation when scope, proof, required assignments, and their model
mapping are recorded. Use [review assignments](references/review-assignments.md)
for criteria, the alternate draw, and replacements; model defaults and execution
come from [agent routing](../orchestration/references/agent-routing.md).

## Review, settle, repeat

1. Dispatch fresh **T3-owned** review tasks for the selected assignments. Give
   each the same snapshot and its assigned criteria using the review brief's
   round context and peer isolation. Retain task IDs and request keys. Run in
   waves when slots are fewer than reviewers, until all required coverage returns.
2. Recheck the snapshot before accepting results. If it moved, cancel obsolete
   tasks, retain useful observations as unverified claims, and return to step 1
   with a refreshed snapshot against the original base. End this step there;
   superseded assessments do not satisfy coverage.
   For a matching snapshot, inspect completion, findings, and assigned-criteria
   coverage. An unread input
   or missing assessment is a gap, including when the task reports success.
   Give every result and partial finding to Review Sweep with its provenance.
3. Settle every finding and run checks for accepted fixes through the working
   model. Preserve valid proof; record blockers and model-diversity gaps apart
   from coverage. After code or substantive instruction fixes, refresh the full
   snapshot against the original base and start a new round. Ordinary prose and
   wording-only fixes use targeted checks instead.

Finish when the required assessments cover the final snapshot, accepted fixes
and checks are settled, and code/substantive instructions have a final round
with no fixes. Missing required coverage blocks completion. Reopen a settled
finding only with new evidence; report a stalled dispute or exhausted permitted
recovery rather than repeating equivalent rounds.

Return scope/base, rounds, prompt/model mapping and confirmed settings, task
IDs, findings/dispositions, checks, coverage/diversity gaps, and remaining work.
