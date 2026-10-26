---
name: review-fix-loop
description: Review and fix a change through independent T3 review rounds. Use before handing off behavior or agent-procedure changes, or when asked to review and fix a branch, PR, or local diff.
---

# Review Fix Loop

The parent coordinates rounds. [Orchestration](../orchestration/SKILL.md) owns
model defaults, delegation, recovery, and the general handoff.
[Review](../review/SKILL.md) assesses one snapshot;
[Review Sweep](../review-sweep/SKILL.md) validates and fixes findings.
The caller owns commits, publication, replies, and merging.

## Prepare

Resolve the original base once using Review. Gather the complete snapshot,
requirements, and verification evidence with the canonical
[review brief](../review/references/review-brief.md).

Choose coverage in this order, honoring explicit user requests:

| Change | Required assessment |
| --- | --- |
| Ordinary prose or wording only, with no procedure change | Parent review |
| Shared contracts, risky logic, multiple behaviors/authors, substantial code or instruction workflows | Primary, Ponytail, and Thermo, even for a small diff |
| Remaining small behavior or agent-procedure change | One independent primary reviewer |

For behavior or agent-procedure changes, add a separate **Adversarial**
assessment when the combined change is substantial: it changes a shared
contract or ownership boundary, introduces
interacting behaviors across modules, redesigns a multi-step workflow, or alters
security, data integrity, concurrency, retries, partial failure, migrations, or
recovery. Broad implementation or instruction rewrites also qualify. Judge the
changed behavior and consequences, rather than line count or file count alone.
Record the decision and a one-sentence reason in the brief. Keep required
coverage through fix rounds against the original base; expand it if fixes
introduce a new trigger. When a plausible material consequence remains uncertain,
include Adversarial.

Apply [review assignments](references/review-assignments.md) for the criteria,
model mapping, additional draws, provider references, and skip policy. Finish
preparation when scope, proof, and assignments are recorded.

## Review, settle, repeat

1. Run each selected assessment as a **T3-owned** task through Orchestration,
   using the shared review brief. Await the required assessments and all
   additional reviews that have not been skipped.
2. Recheck the snapshot before accepting results. If it moved, cancel obsolete
   tasks, retain useful observations as unverified claims, and return to step 1
   with a refreshed snapshot against the original base. End this step there;
   superseded assessments do not satisfy coverage.
   For a matching snapshot, check the reports' assigned-criteria coverage,
   including unread inputs or missing assessments.
   Give every result and partial finding to Review Sweep with its provenance.
3. Settle findings and check accepted fixes through Review Sweep. After code or
   substantive instruction fixes, refresh the full snapshot against the original
   base and start a new round. Ordinary prose and wording-only fixes use targeted
   checks instead.

Finish when the required assessments cover the final snapshot, accepted fixes
and checks are settled, and code/substantive instructions have a final round
with no fixes. Missing required coverage blocks completion. Reopen a settled
finding only with new evidence; report stalled disputes rather than repeating
equivalent rounds.

In the Orchestration handoff, map child tasks to review assignments, criteria,
models, and rounds. Include the reviewed base/snapshot, findings/dispositions,
coverage/diversity gaps, skipped additional reviews and reasons, and provider
references used or unavailable.
