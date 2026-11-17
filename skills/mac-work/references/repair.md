# Admission repair proposal

Status: proposed, not implemented or accepted. The current pin cannot safely
unlock the handoff layer. Keep the existing manual coordination and holds while
this gate is blocked. Do not fall back to unqueued execution silently.

## Repair upstream ownership, then wrap it

A wrapper supplying matching flags cannot repair upstream's premature releases.
Patch the pinned upstream lifecycle in a separately authorized source change,
or use a future upstream revision that passes the same probes. Keep upstream's
SQLite admission transaction and FIFO policy as the only scheduler.

1. **Make first use nondestructive.** Serialize database initialization across
   processes. Distinguish busy/locked from corruption; fail closed on uncertainty.
   `ensure_db` currently unlinks the database and WAL after any OperationalError,
   including concurrent first-use failures. Never erase live admission state
   to make initialization succeed.
2. **Keep uncertain permits.** Record owner boot identity and PID birth identity,
   task generation, child/group identity and configuration digest before work
   can escape supervision. Owner death with no child PID is an uncertain spawn,
   not permission to release. Preserve the row and mark recovery pending. Count
   terminating/quarantined rows against the same upstream capacity until closure
   is proved; never replay a command automatically after a crash.
3. **Close the whole owned lifetime before releasing.** Normal exit, cancellation,
   timeout, stale cleanup and server-replacement cleanup must all use one upstream
   close operation. Signal the group, escalate after bounded grace, and observe
   its disappearance before releasing. Preserve a terminal receipt separately
   from the admission row. A stale timer may initiate termination; it cannot by
   itself grant the next command capacity.
4. **Handle escaping descendants explicitly.** A process-group check cannot prove
   that a `setsid` descendant stopped. The detached probe demonstrates that limit.
   Automatic recovery needs a verified ownership/containment seam that survives
   daemonization and owner death. A PID scan after reparenting is insufficient.
   Until that exists, uncertain ownership must quarantine the permit. A fail-closed
   fallback can require a host reboot (verified changed boot identity) before
   reclaiming it; that preserves safety at the cost of availability. Do not claim
   arbitrary descendant safety from a foreground-only convention.
5. **Persist reconciliation.** Late reads after a crash must return the original
   interrupted/recovery-pending receipt, never unknown followed by resubmission.
   Resolve the row and receipt atomically enough that cancel/completion/restart
   races cannot release twice or lose the result.

The bounded first repair is initialization plus ordinary process-group closure
and durable quarantine for all unresolved deaths. It does not solve transparent
detached-process recovery. Decide that availability tradeoff with the parent
before building an adapter; do not grow a second scheduler to hide the gap.

The concrete source paths are `queue_core.ensure_db`, `cleanup_queue`,
`kill_process_tree`, `tq.cmd_run`/its cleanup handler, and the MCP execution,
termination, cancellation and release paths. The
[pinned source](https://github.com/block/agent-task-queue/tree/48d16da41f57801bbf9462ed2df923713978b6ae)
owns them. No upstream implementation was copied into this repository.

## Proposed operational contract after qualification

These are inputs for the next admission attempt, not shipped executable APIs.
They unlock no dependent implementation until a repaired candidate passes.

- One host config lives outside projects/providers; all clients resolve the same
  absolute runtime and SQLite state path. It records schema version, source pin,
  runtime/lock digest, configuration digest and one heavy root with capacity 1.
  Unknown schema, version or digest fails closed. Entry points cannot override
  capacity, create a second heavy root, or fall back to PATH/default `/tmp` state.
- A single CLI offers `run`, `status` and `cancel`. `run` requires an operation ID,
  owner, absolute worktree and command argv, plus separate queue-wait and execution
  limits. It snapshots revision and worktree dirtiness. Retrying an ID returns its
  original receipt or rejects differing input; status never submits.
- Receipts retain operation/upstream task IDs, owner/worktree/revision, argv,
  configured limits, queued/start/terminal timestamps, exit/result and lifecycle
  closure/recovery state. Queue deadline begins on submission; execution deadline
  begins on admission. A timed-out wait requests explicit cancellation of that
  task and waits for confirmed closure before reporting released capacity.
- Write private receipt/output files without recording secret environment values.
  Retention, output exposure and T3 presentation belong to diagnostics integration.
- Install into immutable version directories. Activate config/runtime together
  only after drain and successful qualification. Upgrade/rollback refuses unresolved
  permits. Keep the previous runtime/config until all receipts are reconciled.

T3 device_open exposes no established external admission hook. Task 2 must settle
its supported bounded-session or native integration seam separately. Admission
never takes device lifecycle ownership away from SimLock or UI driving away from
T3's exact bound driver.
