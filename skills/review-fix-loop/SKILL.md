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
[review brief](../review/references/review-brief.md). Establish its workflow/pass
identity before dispatch and retain it with the findings through fix passes.

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
assessment angles through fix rounds; expand them if fixes introduce a new
trigger. When a plausible material consequence remains uncertain, include
Adversarial.

Apply [review assignments](references/review-assignments.md) for the criteria,
model mapping, additional draws, provider references, and skip policy. Finish
preparation when scope, proof, and assignments are recorded.

## Review, settle, repeat

1. Run each selected assessment as a **T3-owned** task through Orchestration,
   using the shared review brief. Await the required assessments and all
   additional reviews that have not been skipped.
2. Recheck the snapshot before accepting results. If it moved, cancel obsolete
   tasks, retain useful observations as unverified claims, and return to step 1
   with refreshed inputs covering all unreviewed changes. End this step there;
   superseded assessments do not satisfy coverage.
   For a matching snapshot, check the reports' assigned-criteria coverage,
   including unread inputs or missing assessments.
   Use [Review evidence](../review/references/review-evidence.md) to validate
   task/output identity, read receipts, and source citations, then archive the
   original report and receipt bytes before later writers run. Invalid or lost
   required coverage needs a fresh assessment under the selected failure policy.
   Give every result and partial finding to Review Sweep with its provenance.
3. Settle findings and check accepted fixes through Review Sweep, carrying
   canonical issue IDs and their per-issue repair/check evidence forward. After
   code or substantive instruction fixes, start a fresh pass with the same selected
   assessment angles, subject to the existing optional-skip policy. Bound its
   scope to all changes since the last completed pass, affected behavior and
   dependencies, prior findings and dispositions, and relevant verification.
   Each angle reassesses that scope against the updated work, including whether
   fixes invalidate earlier conclusions. Carry forward coverage only where the
   source, assumptions, and proof still apply; record the reason. Expand the
   scope when a fix reaches further or retained coverage cannot be justified.
   Keep the original base and complete diff for context, rather than requiring
   another whole-change review by default. Ordinary prose and wording-only
   fixes use targeted checks instead.

Finish when retained coverage and fresh assessments together cover the final
snapshot for every required angle, accepted fixes and checks are settled, and
the final code/substantive-instruction pass needs no fixes. Missing required
coverage blocks completion. Reopen a settled finding only with new evidence;
report stalled disputes rather than repeating equivalent rounds.

In the Orchestration handoff, map child tasks to workflow/pass, review assignments,
criteria, and configured models. Include the reviewed base/snapshot,
findings/dispositions, coverage/diversity gaps, skipped additional reviews and
reasons, and provider references used or unavailable.
