# Experimental lifecycle repair

The maintained [patch](../patches/lifecycle.patch) and hash-checked build recipe
are implemented. Production admission remains blocked: macOS has no established
seam here that proves arbitrary detached descendants absent. No canonical
heavy-command launcher or host activation is provided. The parent must settle
a usable workload boundary before the handoff layer starts.

## Implemented behavior

The patched dependency keeps upstream's SQLite transaction, root capacity and
FIFO checks authoritative. A quarantined task retains its upstream `running`
row, so the existing capacity calculation includes it.

- A shared initialization lock serializes schema setup. Missing, busy or corrupt
  databases never trigger deletion of queue/WAL files. Corruption fails closed.
- A private launch pipe gates command execution until boot identity, PID birth,
  group identity, generation and execution deadline are committed. Owner death
  before that receipt leaves an unresolved row rather than replaying the command.
- CLI/MCP completion, cancellation, timeout and orphan/server-replacement cleanup
  use one lifecycle close operation. It records the intended result before effects,
  verifies group identity before signals, and persists a recovery-pending receipt
  when closure remains uncertain. A missing root or stale timer cannot release
  capacity by itself. Unknown identity prevents signalling.
- Receipts survive queue-row deletion. Late reads return the original terminal
  or recovery-pending task; they do not submit. CLI `clear` is disabled.
- The first configured capacities and ownership contract live in SQLite. Every
  submitting entrypoint must match them. Tasks retain the configuration digest.
  Queue deadlines and execution deadlines have separate starts and limits.

| Lifecycle observation | Capacity and result |
| --- | --- |
| Waiting task cancelled or queue deadline expires | Cancel/error receipt; no command starts. |
| Admitted work has a verified closed group under the limited group contract | Terminal receipt; row released. |
| Ownership or closure uncertain | `recovery-pending`, `capacity_held=true`; row remains running. |
| Later read verifies that the limited group has no active members | Resolve its retained intended result and release. |
| Persisted boot identity differs from the real current boot | Old work cannot survive; resolve without signalling reused PIDs. |

The boot identity comes from `kern.bootsessionuuid`. PID birth and group metadata
come from the local SDK's `proc_pidinfo`/`proc_bsdinfo`; group enumeration uses
`ps`. These establish the stated group boundary, not arbitrary descendant lineage.

## Two distinct experimental contracts

`uncontained` is the default. An empty group does not prove that no descendant
escaped it. Admitted commands therefore retain capacity, even after ordinary
foreground success. A changed real boot can establish closure. There is no force
clear, boot-identity override, automatic reboot or approval shortcut.

`process-group` is a deliberately narrower qualification contract. It can finish
ordinary foreground jobs and close verified members of their original group.
A reaped root with unverified remaining members quarantines until the group is
observably empty. A descendant that changes group/session is outside this
contract. The original detached-descendant safety test still fails when this
mode is judged against the universal requirement; it has not been weakened.
Persisted policy prevents changing an existing uncontained queue to this mode.

The Mac probe registered `NOTE_TRACK` and received `Operation not supported`.
Without that flag, the root fork notification did not identify or follow the
`setsid` child. After root exit, that child survived with parent PID 1. The local SDK and
[Apple's header](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event.h)
say NOTE_TRACK/NOTE_TRACKERR/NOTE_CHILD have been unsupported since 10.5.
An environment marker, inherited descriptor or PID scan is not an absence proof
when an arbitrary daemon may clear/close it and reparent.

This is the unresolved contradiction: universal descendant safety requires
quarantine, while routine automatic completion requires a narrower enforceable
workload or containment contract. Do not present a permanently quarantining
launcher as the requested usable route. The patch advances independent repairs;
it does not settle that boundary.

## Actual private CLI and receipt surface

These are repaired upstream qualification APIs, not the proposed canonical host CLI:

```sh
"$runtime/bin/tq" --data-dir "$state" --queue-capacity heavy=1 \
  --ownership-contract process-group run -q heavy/client \
  --queue-timeout 5 -t 5 /usr/bin/true
"$runtime/bin/tq" --data-dir "$state" status 1 --json
"$runtime/bin/tq" --data-dir "$state" cancel 1 --json
"$runtime/bin/tq" --data-dir "$state" list --json
```

Use new task-private state only. Obtain the task ID from the run output or list;
the example ID is valid only in a fresh fixture. Every submitting CLI/MCP process
must use the same `--queue-capacity` and `--ownership-contract`. The MCP server
accepts those same startup flags. Its `run_task` additionally accepts
`queue_timeout_seconds`; `timeout_seconds` covers execution. Existing
`task_status` and `cancel_task` return the durable result.

A receipt includes task ID/command, worktree/directory, agent label, creation time,
configuration digest, revision when Git provides it, generation, owner and child
birth/group/boot identities, independent deadline limits, intended result and
`capacity_held`. Recovery-pending is not terminal availability. CLI exit 125
marks normal completion with retained capacity; a timeout/signal exit alone is
not proof that capacity was released. Read the receipt. No environment values
are dumped into receipts.

## Still proposed

The canonical host config/runtime/state location, idempotent operation-ID
submission, provider adapters, managed activation/upgrade/rollback and T3 result
presentation remain unimplemented. T3 device_open still has no established
external admission hook. See the [task record](plan.md). The source/patch/build
contract is fixed in [candidate.json](../candidate.json); the operational boundary
is not accepted. Reproduce the [qualification](lifecycle.md) before changing it.
