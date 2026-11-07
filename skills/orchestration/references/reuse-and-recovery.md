# Reuse and recovery

## Reuse an agent

For a new assignment, reuse a retained agent when its context helps and it runs the row's model and
effort, reaches the right workspace and current revision, isn't stuck on failed assumptions, and
the host permits continuing it for this work. Otherwise use a new agent.

A repair to its [owner](../SKILL.md#who-does-the-work) needs no model match or continuation
permission. First confirm the owner can reach the revision under repair, or give it that revision.

**Independence:** an agent that wrote or directed work stays out of its later independent
assessment.

**Review passes:** the first pass uses fresh agents on the [review rows](models.md#model-defaults).
Each later pass and recheck uses a new task on the same model and effort as that reviewer, because
T3 requires a new task for each re-check. Archive that reviewer's reports and receipts first. Give
the new task the role's criteria and the prior evidence, keep same-round peer content out of it,
and record which reviewer it follows. Brief every pass under
[Review evidence](../../review/references/review-evidence.md).

## Replace an owner

Replace an owner only on evidence of repeated failure: fixes that keep failing the same check, or
the same assumption proving wrong. A model that differs from the table is not evidence, and
neither is one failed check or a stuck child, who [asks up](../SKILL.md#return). A lost owner
follows [recovery](#recover-work), not this test.

Before you replace one, reconcile under [Replacing work](#recover-work). Carry forward the task,
proof, partial work with exact paths, checks, and failed assumptions.

If a further replacement would name no new check result, failed assumption, or artifact fact,
report a blocker.

## Recover work

Keep partial results and the failure cause. A caller's failure policy, such as
[additional-review skips](../../review-fix-loop/references/review-assignments.md#handle-failures),
overrides the retry below. Use a new key for any fresh run after terminal failure.

| Failure | Action |
| --- | --- |
| Uncertain dispatch or lost response, including a failed send to an owner | Repeat with its existing key in the same provider session |
| Uncertain dispatch or lost response after a session change | Treat each tracked key, with or without an ID, as a pending run. Read known IDs through the host's route and collect finished results. Treat a live run as a wait timeout. If a read-only run stays unknown, apply its caller's failure policy. If any other run stays unknown, start no overlapping work and report a blocker |
| Wait timeout | The run is still live. Follow the host's next step |
| Transient terminal or provider runtime failure | May retry once per target per workflow, then treat it as unavailable |
| Quota, or an unavailable model or provider | The [listed fallback](#availability-fallback) with no retry. Otherwise report the blocker and resume when conditions change |
| Authentication failure | Stop and report it, or request the login through the host's secret route. Retry once resolved |
| Permission or policy denial | Stop the blocked action. Another model or transport does not authorize it |
| Wrong answer, failed product check, or task difficulty | Diagnose, [ask up](../SKILL.md#return), or [replace the owner](#replace-an-owner) on repeated failure |

**Replacing work:** before a replacement overlaps earlier writers, account for pending runs and
reconcile their files. A cancellation or terminal receipt alone does not show writers stopped.

### Availability fallback

A listed fallback is the user's standing permission to switch, so the switch is asked for, even
where the host says never to switch unasked. It applies only when the row supplied the model. If
the user named the model, report a blocker and wait unless the user authorized a substitute. A
fallback never authorizes unlisted models, the Simple tier, or a change to additional-review skip
policy.

Keep the assignment's scope, requirements, verification bar, and review criteria, and the exact
fallback until availability changes or the user directs otherwise.

A review fallback runs in a new independent task and never reuses another result.
