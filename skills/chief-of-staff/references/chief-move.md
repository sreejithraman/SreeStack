# Move or take over the chief

One thread is the program's chief at a time. These steps keep a second chief
from acting on stale state or writing over the record.

## Check the chief

Before acting on a request, direction, event, report, or pasted answer, and
before each record write, read `record.chief` in `program.json`. A thread that
is not the chief reads the chief's thread, forwards the item with
`t3_thread_send`, linking the user's message for requests, directions, and
answers, and stops. It unwatches its PRs when the chief asks. A user item that arrives through
`t3_thread_send` counts under [record an answer](decisions.md#record-an-answer).

When `program.json` fails `--check`, only the thread whose own last write named
it chief writes: it repairs the file through
[write the record](program-state.md#write-the-record), then resumes the check.
Any other thread reports the break to the user and writes nothing.

## Move

Only the chief moves the program to a new thread. In one record write it names
the new chief in `record.chief` and each live owner's new return route in
`record.owners`, which is `t3_thread_send` to that chief even for an owner that
used to end its turn. It then tells the new thread with `t3_thread_send`.
Owners keep running.

## Take over

If the chief's thread cannot act, offer the user a takeover instead of
forwarding; this is the one exception to the check above. With approval, repeat
until the old thread is idle or gone (`thread_not_found`) and a re-read of the
record names this thread: write this thread as chief with the new return routes,
interrupt the old thread, and confirm its state with `t3_thread_read`. If it
will not settle or a call fails another way, stop and tell the user the takeover
is incomplete.

## After either

The new chief takes over `program.json` and the running dashboard server as they
stand; the server needs no restart. It reconciles state as on resume, sends
owners their route, watches any delegated owner's pending PRs, and asks any
remaining old thread to unwatch.
