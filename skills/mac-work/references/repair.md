# Upstream ownership and operation seam

The user approved a foreground process-group pilot. The canonical
[runner](runner.md) is implemented on the maintained dependency patch; arbitrary
escaping descendants remain unsupported, not a pending scope decision.
Original counterexamples and the earlier universal-ownership contradiction remain
in the earlier layer's [findings](fitness.md) and proof.

## One admission owner

The patched dependency retains upstream's SQLite `BEGIN IMMEDIATE`, FIFO checks
and root-capacity calculation. `recovery-pending` tasks keep their upstream
`running` row, so existing capacity accounting includes them. There is no second
scheduler or provider-specific capacity registry.

Initialization is serialized and nondestructive. Busy/missing/corrupt state never
authorizes database/WAL deletion. Fresh bootstrap is explicit; active opens
validate existing schema and policy before mutation. A launch pipe permits command execution only
after birth/group/boot identity is committed. CLI/MCP completion, cancellation,
timeouts and orphan cleanup use one durable close operation. Verified group
members are signalled only under their recorded identity; uncertain identity or
closure retains capacity. A missing root, stale timer or dead owner alone cannot
release it. The atomic admission clock starts execution, including preflight, and stops
queue wait. Registration and gate release serialize with cancellation. Expired
preflight cannot launch. Trusted Python startup ignores caller import overrides,
while the requested command retains its environment. Execution deadlines come from the recorded limit; a cleanup timer
cannot substitute another execution allowance.

The runner revision adds `task_operations` inside the same upstream database:
operation ID, immutable request/hash, upstream task ID, config digest and one
worker claim. Operation binding and task insertion commit atomically. Claiming
never becomes retryable after a crash. The associated upstream task/result remains
authoritative; exported receipt files are serialized derived views, not a parallel
state machine. The runner's root lock protects activation from concurrent producers
and workers; it does not admit or schedule jobs.

Acceptance includes worker ownership, not merely process creation. This matters
because an exited submitter must not be mistaken for a dead worker before handoff.
A failed/interrupted start retains its original association and result instead of
replaying. A live worker can close a proven pre-launch abort through the same
lifecycle operation; a crashed owner's unknown spawn window still quarantines.

| Observation | Result |
| --- | --- |
| Waiting task cancelled or queue deadline expires | Durable outcome; command does not start. |
| Foreground group verifiably stops | Terminal receipt and released upstream row. |
| Owner/group identity or closure uncertain | Recovery-pending receipt; running row retains capacity. |
| Later status observes group closure | Resolve the original intended result; no replay. |
| Real boot identity changes | Prior work cannot survive; reconcile without signalling reused PIDs. |

Canonical policy is `heavy=1`, `process-group`. Persisted policy mismatch refuses
submission/activation. An existing uncontained queue is never silently converted;
its unresolved permits remain outside this pilot's migration scope. Bulk clear
is disabled and no approval/force shortcut frees capacity.

## Supported boundary and retained evidence

Commands must wait for all heavy work in the launched group. Shared daemons,
background services and `setsid`/other group escapes are unsupported. This is
cooperative foreground routing, not detection or containment of arbitrary escapes.
The original detached test still reproduces that limitation under the narrower
contract; it is not relabelled as a passing automatic-cleanup test.

The prior lingering-success automatic tests used an eight-second observation
window around a twenty-second fixture. Their earlier blocked verdicts remain.
The foreground pilot now checks the appropriate negative behavior separately:
hold capacity while a remaining group lives, then reconcile only after observed
closure. That is not an eight-second implementation deadline or blind release
on root exit.

The local SDK and [Apple's header](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event.h)
mark NOTE_TRACK/NOTE_TRACKERR/NOTE_CHILD unsupported since10.5. The bounded probe
returned errno45 for NOTE_TRACK; a detached child survived root exit with parent
PID1 and no tracked child identity. Environment markers, descriptors and PID scans
cannot establish arbitrary detached absence. The user resolved that broader
requirement by selecting foreground commands, not by asking for a speculative
supervisor.

The raw upstream `uncontained` mode remains in dependency qualification to preserve
that history and avoid policy reinterpretation. Canonical clients expose no mode,
queue or capacity override. Source/patch/dependency digests are fixed in
[candidate.json](../candidate.json), and [notices](../NOTICE.md) accompany builds.
No host skill/profile activation, device work or heavy compiler proof occurred in
this layer. Parent owns the [remaining integration and workload tasks](plan.md).

Reconciliation uses the recorded execution deadline when present. Only compatible
legacy rows without that deadline use the cleanup-age fallback. A matching zombie
birth is dead ownership; existing exact-group cleanup/quarantine still decides
release. Unknown unrecorded spawn windows remain held.
