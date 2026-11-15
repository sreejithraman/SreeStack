# Move or take over the coordinator

One thread is the program's coordinator at a time. These steps keep a second coordinator
from acting on stale state or writing over the record.

## Check the coordinator

Before acting on a request, direction, event, report, or pasted answer, and
before each record write, read `chief` from
`git -C /absolute/path show HEAD:program.json`. A thread that is not the coordinator
reads the coordinator's thread, forwards the item with `t3_thread_send`, linking the
user's message for requests, directions, and answers, and stops. It unwatches
its PRs when the coordinator asks. A user item that arrives through `t3_thread_send`
counts under [record an answer](decisions.md#record-an-answer).

## Move

Only the coordinator moves the program to a new thread. First it
[turns off](hosting.md#turn-off) tap-to-answer, recording the last stored picks
while it still holds the record. Then in one
[record write](program-state.md#write-the-record) it names the new coordinator in
`chief` and each live owner's new return route in its `owner.route`, which is
`t3_thread_send` to that coordinator even for an owner that used to end its turn.
Right after the commit, and without publishing, it deletes its heartbeat and
tells the new thread with `t3_thread_send`. Owners keep running.

## Take over

If the coordinator's thread cannot act, offer the user a takeover instead of
forwarding; this is the one exception to the check above. With approval, delete
the old thread's heartbeat and [turn off](hosting.md#turn-off) its answer wake,
whose task IDs are in `grant.heartbeat` and `grant.wake`, leaving the stored
picks for the resume below. Then repeat
until the old thread is idle or gone (`thread_not_found`) and `chief` at `HEAD`
names this thread: [write](program-state.md#write-the-record) this thread as
coordinator with the new return routes, without publishing, interrupt the old
thread, and confirm its state with `t3_thread_read`. If it will not settle or a
call fails another way, stop and tell the user the takeover is incomplete.

## After either

The new coordinator takes over the program folder as it stands, keeping its single
record and git history. It [publishes the page](hosting.md) with its session's
backend, reusing that backend's target or recording the new URL after success.
It sets up its own [heartbeat](../SKILL.md#heartbeat) and
[answer wake](hosting.md#tap-to-answer), bound to its thread, and records the
new task IDs in `grant.heartbeat` and `grant.wake`; the grant is otherwise
unchanged.
The move or takeover completes after successful publication and any link write.
It reconciles state as on resume, sends owners their route, watches any
delegated owner's pending PRs, and asks any remaining old thread to unwatch.
