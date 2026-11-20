# Reuse and recovery

## Reuse an agent

Split reuse by thread kind:

- **Persistent owners** (such as a worktree-bound PR/outcome owner): resume the original owner first
  for repairs and in-scope follow-ups — no model match or continuation permission is required — once
  you confirm it can reach the revision under repair (or give it that revision). Replace it instead
  if it shows repeated failure, stale assumptions, or dropped directives across interrupts.
- **Ephemeral helpers, research, and new assignments:** launch a fresh agent with consolidated scope
  by default. Reuse a retained helper only when it holds costly live state (uncommitted work, a
  running dev server or simulator) or directly helpful context, matches the row's model and effort,
  reaches the right workspace and revision, is not stuck on failed assumptions, and the host permits
  continuing it.

**Independence:** an agent that wrote or directed work stays out of its later independent
assessment.

**Review passes:** the first pass uses fresh agents on the review rows in
[models](models.md#model-defaults). Every later pass or recheck uses a **new task** on the same
model and effort as that reviewer (never resuming the prior reviewer thread). Preserve its prior
report, pass the role's criteria and prior evidence, keep same-round peer content out, and record
which reviewer it follows. Brief every pass with the exact snapshot, criteria, and prior report
path per the review skill's evidence rules.

## Replace an owner

Replace a persistent owner only on evidence of repeated failure (fixes keep failing the same check,
the same assumption proves wrong, or resumed turns keep dropping directives). A model that differs
from the table, a single failed check, or a stuck child asking up is not evidence. A lost owner
follows recovery below, not this test.

Before replacing, reconcile writers under Replacing work below, and carry forward the task, proof,
partial work with exact paths, checks, and failed assumptions. If another replacement would add no
new check result, failed assumption, or artifact fact, report a blocker instead.

## Recover work

Preserve partial results and the failure cause. A caller's failure policy (such as
skipping optional reviewers instead of retrying) overrides the retry rules below.
Use a new request key for any fresh run after terminal failure.

| Failure | Action |
| --- | --- |
| Uncertain dispatch or lost response (including failed send to an owner) in the same session | Repeat with its existing request key |
| Uncertain dispatch or lost response after a session change | Treat each tracked key (with or without an ID) as pending. Read known IDs through the host and collect finished results; treat live runs as wait timeouts. For an unknown read-only run, apply the caller's failure policy; for any other unknown run, start no overlapping work and report a blocker |
| Wait timeout | The run is still live; follow the host's next step without polling |
| Transient terminal or provider runtime failure | Retry at most once per target per workflow, then feed availability evidence back to Dispatch |
| Quota, or unavailable model/provider | Preserve results and failure evidence, reconcile writers below, then select the listed fallback in Dispatch without retrying the unavailable target |
| Authentication failure | Stop and report it, or request login through the host's secret route; retry once resolved |
| Permission or policy denial | Stop the blocked action; another model or transport never authorizes it |
| Wrong answer, failed product check, or task difficulty | Diagnose, ask up, or replace the owner on repeated failure |

**Replacing work:** before a replacement overlaps earlier writers, account for all pending runs and
reconcile their files. A cancellation or terminal receipt alone does not prove writers have stopped.
