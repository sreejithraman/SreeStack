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

1. Reconcile every active landing release (`released` or `submitted` in `landings`): withdraw it
   under [landing](landing.md#withdraw-a-release) and confirm any forge auto-merge or queue entry
   stopped (or already merged). `record.py move` refuses while a landing release stays pending.
2. Turn off tap-to-answer under [hosting](hosting.md), recording final stored picks while you still
   hold the record.
3. Run `record.py move --chief <new thread link>` (updates `chief` and sets every live owner's
   `owner.route` to `t3_thread_send` to the coordinator). Do **not** publish from this thread.
4. Delete your heartbeat (`delete_scheduled_task` in T3) and message the new thread via
   `t3_thread_send`. Owners keep running.

## Take over

If `chief`'s thread cannot act, ask the user to approve a takeover (the one exception to forwarding).
With approval:

1. Delete the old thread's heartbeat and turn off its answer wake (`grant.heartbeat`, `grant.wake`),
   leaving stored picks for resume.
2. Reconcile any pending landing releases bound to the old chief: cancel any in-flight forge
   auto-merge or queue entry, confirm its terminal state, and withdraw or mark landed via
   `record.py land` before transferring `chief`.
3. Repeat until the old thread is idle or gone (`thread_not_found`) and `chief` at `HEAD` names
   this thread: run `record.py move --chief <this thread link>` without publishing, interrupt the
   old thread, and confirm via `t3_thread_read`. If it will not settle or a call fails, stop and
   report an incomplete takeover.

## Same-thread provider switch

When this thread's model or provider changes in place (such as Claude ↔ Codex ↔ another provider
via `t3_thread_configure` or the model picker), `chief` and the bound heartbeat stay the same, so
do not run `record.py move`. Instead:

1. Run the single backend and wake transition + forced publish under [hosting](hosting.md) (which
   drains/turns off any old Claude wake, publishes once on the new backend, sets up tap-to-answer
   once if entering Claude, and updates `grant.hosting` and `grant.wake`).
2. Verify the existing heartbeat's `enabled` and `nextRunAt`.

## After either

The new coordinator keeps the same program folder and git history, runs the single backend and wake
transition + forced publish under [hosting](hosting.md), and sets up its own heartbeat bound to its
thread (`grant.heartbeat`). The rest of the grant stays unchanged. Reconcile state as on resume,
send owners their updated route, watch any delegated owner's pending PRs, and ask any remaining old
thread to unwatch.
