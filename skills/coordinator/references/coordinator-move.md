# Move or take over the coordinator

Only one thread coordinates a program at a time so two coordinators never act on stale state or
clobber `program.json`.

## Check the coordinator

Before acting on any request, direction, report, event, or pasted answer, and before every record
write, read `chief` from `git -C /absolute/path show HEAD:program.json`. Before messaging that
thread, read it with `t3_thread_read`, reconcile recent direction with `next`, live owners, waits,
and `owner.route`, and apply [Orchestration's communication rule](../../orchestration/SKILL.md#communicate).

If this thread is not `chief`, forward actionable items to `chief` via `t3_thread_send` (linking
the user's source message for requests, directions, or answers), then stop. Unwatch PRs when the
coordinator asks. If `chief` is unavailable, follow Take over below; a new user request on a paused
or closed program follows resume in [lifecycle](lifecycle.md).

## Move

Only the current coordinator moves a program:

1. Turn off tap-to-answer under [hosting](hosting.md), recording final stored picks while you still
   hold the record.
2. Run `record.py move --chief <new thread link>` (updates `chief` and sets every live owner's
   `owner.route` to `t3_thread_send` to the coordinator). Do **not** publish from this thread.
3. Delete your heartbeat (`delete_scheduled_task` in T3) and message the new thread via
   `t3_thread_send`. Owners keep running.

## Take over

If `chief`'s thread cannot act, ask the user to approve a takeover (the one exception to forwarding).
With approval:

1. Delete the old thread's heartbeat and turn off its answer wake (`grant.heartbeat`, `grant.wake`),
   leaving stored picks for resume.
2. Repeat until the old thread is idle or gone (`thread_not_found`) and `chief` at `HEAD` names
   this thread: run `record.py move --chief <this thread link>` without publishing, interrupt the
   old thread, and confirm via `t3_thread_read`. If it will not settle or a call fails, stop and
   report an incomplete takeover.

## Same-thread provider switch

When this thread's model or provider changes in place (such as Claude ↔ Codex ↔ another provider
via `t3_thread_configure` or the model picker), `chief` and the bound heartbeat stay the same, so
do not run `record.py move`. Instead:

1. **Leaving Claude:** delete the old webhook wake task (`delete_scheduled_task` using the task ID
   in `grant.wake`), overwrite `grant.wake` via `record.py grant --wake "None (<reason>)"` so
   future heartbeat ticks stop looking for Claude DB picks, and tell the user Send answer on the old
   Claude artifact no longer reaches you.
2. **Entering Claude:** publish a private Claude artifact, set up tap-to-answer under
   [hosting](hosting.md), and update `grant.wake`.
3. **Publish on the new backend:** force-publish under [hosting](hosting.md), record any new URL via
   `record.py grant --hosting`, tell the user the old hosted URL is now frozen, and verify the
   existing heartbeat's `enabled` and `nextRunAt`.

## After either

The new coordinator keeps the same program folder and git history, publishes the page with its
session's backend (recording any new URL via `record.py grant --hosting` and telling the user the
old hosted URL is now frozen), sets up its own heartbeat bound to its thread (`grant.heartbeat`),
and updates `grant.wake`: on Claude, set up tap-to-answer; on any non-Claude provider, delete any
remaining old webhook task (`delete_scheduled_task`) and overwrite `grant.wake` (such as
`"None (Sites page; Copy answer only)"`) so heartbeat ticks never try to read Claude DB picks.
The rest of the grant stays unchanged. Reconcile state as on resume, send owners their updated
route, watch any delegated owner's pending PRs, and ask any remaining old thread to unwatch.
