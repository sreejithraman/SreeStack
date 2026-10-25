# Make Operations Idempotent

For a mutating command, lifecycle step, or retry loop, ask what a second run and
a crash between effects leave behind. Inspect and reconcile partial state before
repeating work. Use stable operation identity, transactional updates, deduplication,
or explicit recovery states where the effects need them. Reuse established provider
idempotency and recovery contracts rather than inventing a parallel one.

For leftover locks, temporary artifacts, partial records, or claimed jobs, make
ownership and recovery decidable after every relevant interruption point.
Distinguish live work from stale work using reliable evidence before reclaiming
it; a marker's existence alone does not establish either state.

Test representative interruption points and duplicate requests through the real
operation. A restart should converge to the intended state or expose a recoverable
pending state, without silently duplicating effects. For an uncertain external
write, inspect its result before replaying it. Repetition does not grant permission.
