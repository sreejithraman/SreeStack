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
or closed program follows resume in `lifecycle.md`.

## Move

Only the current coordinator moves a program:

1. Reconcile every pending landing release (`released`, `submitted`, or `cancelling` in `landings`):
   withdraw it under `landing.md` (Withdraw a release: moving active releases to
   `cancelling` first, confirming forge cancellation, then marking `withdrawn` or `landed`).
   `record.py move` refuses while any landing release stays pending.
2. Run `record.py move --chief <new thread link>` (updates `chief` and sets every live owner's
   `owner.route` to `t3_thread_send` to the coordinator). Do **not** publish from this thread.
3. Delete your heartbeat (`delete_scheduled_task` in T3) and message the new thread via
   `t3_thread_send`. Owners keep running.

## Take over

If `chief`'s thread cannot act, ask the user to approve a takeover (the one exception to forwarding).
With approval:

1. Interrupt the old thread (`t3_thread_interrupt`) and delete its heartbeat (`grant.heartbeat`).
2. Reconcile any pending landing releases bound to the old chief in the same order as
   Withdraw a release in `landing.md`: first move each active release to `cancelling`
   (`record.py land --landing <ID> --to cancelling --note "Coordinator takeover"`), which fences
   its lander while keeping `record.py move` blocked until forge confirmation; notify/fence its
   lander, cancel any in-flight forge auto-merge or merge-queue entry, and once confirmed stopped
   mark it `withdrawn` (or `landed` if it already merged).
3. Repeat until the old thread is idle or gone (`thread_not_found`) and `chief` at `HEAD` names
   this thread: run `record.py move --chief <this thread link>` without publishing, interrupt the
   old thread, and confirm via `t3_thread_read`. If it will not settle or a call fails, stop and
   report an incomplete takeover.

## Same-thread provider switch

When this thread's model or provider changes in place (such as Claude ↔ Codex ↔ another provider
via `t3_thread_configure` or the model picker), `chief` and the bound heartbeat stay the same, so
do not run `record.py move`. Instead:

1. Force-publish the page on the new backend under `hosting.md` (updating `hosting` if the URL
   changed and telling the user the old URL is now frozen).
2. Verify the existing heartbeat's `enabled` and `nextRunAt`.

## After either

The new coordinator keeps the same program folder and git history, force-publishes the page under
`hosting.md`, and sets up its own heartbeat bound to its thread (`grant.heartbeat`). The rest of
the grant stays unchanged. Reconcile state as on resume, send owners their updated route, watch any
delegated owner's pending PRs, and ask any remaining old thread to unwatch.
