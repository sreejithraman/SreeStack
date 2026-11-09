---
name: review-fix-loop
description: Use when asked to review and fix a branch, PR, or local diff.
---

# Review Fix Loop

The parent runs these six steps. [Orchestration](../orchestration/SKILL.md) owns
model defaults, delegation, recovery, and the general handoff.
[Review](../review/SKILL.md) assesses one snapshot;
[Review Sweep](../review-sweep/SKILL.md) validates and fixes findings.
The caller owns commits, publication, replies, and merging.

[PR](../pr/SKILL.md) calls this loop when work is ready to publish, and anyone can ask
for it. Until then, an agent proves its work and stops for the user to try it.

## 1. Establish scope and select coverage

Resolve the original base once using Review. Gather the complete snapshot,
requirements, and verification evidence with the
[review brief](../review/references/review-brief.md). Establish its workflow/pass
identity before dispatch and retain it with the findings through every pass.

Select initial discovery from the first matching row, honoring explicit user
requests:

| Change | Initial discovery |
| --- | --- |
| Ordinary prose or wording only, with no procedure change | Parent review |
| Substantial, or not clearly contained | Wave 1: Primary, Ponytail, and Thermo. Wave 2: Adversarial |
| Contained and failure-sensitive, or with a plausible material consequence still uncertain | Primary plus the fitting lens, usually Adversarial |
| Remaining contained behavior or agent-procedure change | One independent Primary |

**Failure-sensitive** behavior covers security, data integrity, persistence,
ordering, concurrency, retries, partial failure, migrations, and recovery.

**Contained** work affects one bounded behavior with no substantial trigger.
A change is **substantial**, even with a small diff, when it changes a shared
contract or ownership boundary, introduces interacting behaviors across modules
or authors, introduces or redesigns a multi-step workflow, broadly adds or
rewrites implementation or instructions, or reaches beyond one contained path
with failure-sensitive behavior. Judge the changed behavior and consequences,
rather than line count or file count alone.

Record the selection and a one-sentence reason in the brief. Apply
[review assignments](references/review-assignments.md) for the criteria, model
mapping, additional draws, provider references, and skip policy. This step is
done when scope, proof, and assignments are recorded.

### Coverage rule

Coverage counts for the final snapshot only when an assessment of it, or proof
that still applies to it, supports that angle:

- **Never covered:** a newly required angle assesses the complete current change.
- **Stale:** an angle with earlier coverage assesses changed behavior and affected
  dependencies, and whatever an edit invalidated.
- **Retained:** coverage carries forward where its source, assumptions, and proof
  still apply, with the reason recorded. Pre-edit coverage from an agent that later
  wrote or directed the work follows this rule too.

A new edit makes the proof it touches stale and routes back through step 4. When
work changes the assessed scope, update the selection, apply this rule, and return
to step 2. Substantial work still runs both waves, even when an angle assessed
an earlier snapshot. Keep the original base and complete diff for context, rather
than requiring another whole-change review by default.

## 2. Run initial discovery

Every pass gets a new brief, snapshot-bound assessments, and unique report and
receipt paths. Run each selected assessment as a **T3-owned** task through
Orchestration, excluding any agent that wrote or directed the assessed work. Await
the required assessments and all additional reviews that have not been skipped.

Substantial work runs in stages, using steps 3 and 4 between them:

1. Run wave 1, then validate and settle its findings.
2. Settle scope and design using existing triage authority, and record the results
   as accepted scope changes in the brief.
3. Route wave 1 fixes through step 4. Wave 2 satisfies any Adversarial route.
4. Run Adversarial over the complete change on the settled snapshot. It stays first
   discovery: use the brief's first-round rules plus accepted scope changes, and
   treat this loop's earlier reports as same-round peer outputs under Review
   evidence.

## 3. Validate, archive, and settle

Recheck the snapshot before accepting results. If it moved, cancel obsolete tasks,
retain useful observations as unverified claims, and rerun with refreshed inputs
covering all unreviewed changes. Superseded assessments do not satisfy coverage.

For a matching snapshot, check assigned-criteria coverage, including unread inputs
and missing assessments. Use [Review evidence](../review/references/review-evidence.md)
to validate task/output identity, read receipts, and source citations, then archive
the original report and receipt bytes before any repair or later writer runs.
Invalid or lost required coverage needs a new assessment under the
[failure policy](references/review-assignments.md#handle-failures).

Give every result and partial finding to Review Sweep with its provenance. It
settles findings and checks accepted fixes, carrying canonical issue IDs and their
per-issue repair/check evidence forward. Reopen a settled finding only with new
evidence; report stalled disputes rather than repeating equivalent passes. A
[stop](../review-sweep/references/classification.md#continue-or-stop) blocks
completion. Finish what doesn't depend on it, then report it to your caller with the decision
it needs.

## 4. Route repairs

Ordinary prose and wording-only fixes use targeted checks. For code or substantive
instruction fixes, start a new pass that sends each fix to a new task on the original
reviewer's model for what it changes, under Orchestration's
[review-pass rule](../orchestration/references/reuse-and-recovery.md#reuse-an-agent). The pass
runs the union of those routes over one scope, each focused on the fixes routed to it. Reviewers with
no routed fix stay out and keep their valid coverage.

| The fix changes | Reviewer |
| --- | --- |
| Correctness, requirements, tests, or other local behavior | Primary |
| Only a simplification, deletion, or reuse | Ponytail |
| An ownership boundary, guarantee, structure, or types | Thermo, plus Adversarial when it can change failure behavior |
| Failure-sensitive behavior, or a plausible material consequence still uncertain | Adversarial on the affected contracts |

Scope the pass to all changes since the last completed pass and their affected
behavior, consumers, and dependencies, with the review brief's later-round inputs,
including unresolved findings. Each reviewer checks the repair and its spillover
against the current snapshot rather than only its earlier comment, including
whether fixes invalidate earlier conclusions.

When the work crosses into another angle, the reviewer reports it and the parent
extends the route to that angle. Add a new outside perspective for a disputed
assumption or a material design or
ownership change. Expand the scope when a fix reaches further or retained coverage
cannot be justified.

When a repair cycle returns to an invariant the loop has already repaired, or a
second pass finds new issues in the same component, pause further review of it. The parent applies
[Attack the Premise](../engineering-principles/references/attack-the-premise.md),
keeps the counterexamples, and records the design decision before the next pass.
Route a changed design as an ownership or guarantee fix. This checkpoint is
diagnostic, never a round limit or a reason to ship a known defect.

Repeat steps 3 and 4 until no selected, routed, or checkpoint work remains.

## 5. Run the integrated check

With any repairs, a new task on Primary's model checks every
repair since initial discovery began on the current snapshot: their interactions,
accumulated state, branches, and layers, the requested behavior, and current
verification. A Primary assessment already scoped to every repair, with no repair
after it, is this check.

Process its results through step 3; route any repairs through step 4.

When repairs invalidate an earlier guarantee, structural conclusion, simplicity
judgment, or failure assumption, route that work back to the Thermo, Ponytail, or
Adversarial reviewer. A later code or substantive instruction fix keeps its route
and always includes Primary on that change, which carries this check forward.
Repeat the whole check only when such a fix invalidates its conclusions.

## 6. Finish

Finish when coverage holds for every required angle on the actual final snapshot,
accepted findings and checks are settled on it, and the final
code/substantive-instruction pass needs no fixes. Missing required coverage and
accepted findings block completion.

Record completion on the PR's head, because
[`pr_state`](../pr/references/watch.md#ready-or-blocked) blocks merging without it.
Confirm with `gh pr view <number> --json headRefOid` that the pushed head is the final
snapshot, then post a status on its full SHA, with a description of at most 140 characters:

```sh
gh api repos/<owner>/<repo>/statuses/<full head sha> -f state=success \
  -f context=review-fix-loop -f description="<workflow_id>: <N> passes"
```

When the final snapshot isn't pushed yet, put the command in the handoff. The caller posts it
once the PR's head is that snapshot.

In the Orchestration handoff, map child tasks to workflow/pass, review assignments,
criteria, and configured models, and state which reviewer each follow-up task
follows and the prior evidence it received. Include the reviewed base/snapshot,
findings/dispositions, coverage/diversity gaps, skipped additional reviews and
reasons, and provider references used or unavailable.
