# Foreground command pilot

The user selected **Foreground commands** for the pilot. Commands must wait for
all their heavy work and keep it in the launched process group. Detached sessions,
background build services and shared daemons are outside this contract. This is
cooperative routing, not OS containment or raw-shell prevention. Qualify the exact
invocation's normal completion, cancellation and owner failure before routing it.
A foreground option alone does not prove group ownership or closure. Do not
blindly kill a shared build daemon.

## Create a task-owned Try install

From this repository root:

```sh
python3 -I -B skills/mac-work/scripts/mac_work.py install \
  --root /absolute/private/mac-work-try --release try-1 --json
/absolute/private/mac-work-try/bin/mac-work run \
  --id example-1 --owner my-thread --worktree "$PWD" \
  --queue-seconds 60 --execution-seconds 10 --wait-seconds 10 \
  --json -- /usr/bin/true
/absolute/private/mac-work-try/bin/mac-work status --id example-1 --json
/absolute/private/mac-work-try/bin/mac-work cancel --id example-1 --json
```

The installation owner records the selected root and exact runnable command.
No live profiles or existing holds are changed by these examples. Installation
requires `uv` and downloads only the pinned Python/dependency/source artifacts.
`--archive PATH` reuses the verified upstream archive. `--help` owns remaining
flags. Without an explicit root, the standard private host root is
`~/Library/Application Support/mac-work`. Use one root across projects/providers;
extra roots are for disposable tests, not independent project admission pools.

The root contains `current.json`, immutable named `versions/`, a root-bound
`bin/mac-work`, and shared `state/queue.db`. The active pointer binds an immutable
config by digest. The durable SQLite baseline is `heavy=1` with
`ownership_contract=process-group`.
The config also binds the runtime interpreter, candidate source/patch/dependency pins, and
bundled runner code. CLI/MCP clients cannot select another queue or cap. Runtime,
source, patch, code, config or policy drift refuses execution; there is no direct
shell fallback. A missing database in an active root refuses requests/activation;
restore state instead of silently starting an empty queue and losing operation IDs.
Version directories are never overwritten by the installer. Trusted launcher,
controller, worker and gate Python imports are isolated from caller overrides;
requested commands retain their environment. Active opens validate existing schema
and policy before mutation; empty/truncated state is not fresh bootstrap.

Install with `--adaptive-capacity` to allow a second heavy job. Omit the flag for
fixed one-slot admission. Adaptive workers take one short sample of both kernel
signals per admission attempt. Two slots require pressure level
`kern.memorystatus_vm_pressure_level=1` and a memory availability estimate
`kern.memorystatus_level` of 40–100. [Apple XNU calculation](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/osfmk/vm/vm_pageout.c#L4733-L4738)

During warning or critical pressure, admission uses one slot. Unavailable,
malformed or expired samples also allow one slot. The oldest waiter goes first.
A second slot requires a sample younger than 100 ms at the admission commit
check. The elapsed clock includes system sleep.
[Apple clock documentation](https://developer.apple.com/documentation/kernel/1646199-mach_continuous_time)

When the cap falls, running jobs keep their slots until normal closure. The
setting lives in the release config. Upgrade and rollback keep the same SQLite policy and
operation history. Use `report` to see the active mode and configured maximum.

## Verified runtime boundary

Use the bound `bin/mac-work` for normal calls. It starts the fixed macOS
`/usr/bin/python3` (3.9+) through `/usr/bin/env -S`, with `-I -B -S`, and uses only
that trusted host standard library to verify the bundle and complete installed
runtime inventory before candidate Python runs. Caller PATH cannot select the
bootstrap interpreter. Host OS/system Python, the reviewed initial source/build
recipe and uv are trusted prerequisites; this is not a compromised-host defense.

The private version contains copied CPython and venv trees. Its config binds the
build receipt, which binds every code file, directory, mode and symlink. Dependency
bodies, startup files, extra distributions and bytecode are covered. Escaping
links, shared hardlinks and special files refuse. Code directories are read-only
so normal Python imports cannot add caches; requested command environments are
preserved. Active/prelaunch checks reuse the same verifier without running a
candidate probe. Full byte verification has I/O cost; set queue/execution budgets
for the qualified workload, including verification, and measure before capacity
changes. Restoring an exact task-owned byte/mode snapshot is recovery; it is not a
force-clear for permits.

This manifest/bootstrap protocol requires a fresh task-private root. Older
parent-owned roots remain unchanged. Within this protocol, idle version upgrades
and rollback keep the shared operation database and receipts. Do not relocate a
version or edit its inventories/configuration to accommodate drift.

## Stable operations and receipts

`run` requires a caller operation ID, owner, exact argv and absolute Git worktree
root. It records the commit revision and dirty flag; it does not freeze worktree
bytes. Keep the worktree stable while queued/running. Revision changes before
launch fail the operation instead of running another revision.

Operation inputs include argv, owner, worktree/revision/dirty snapshot and both
deadline limits. Same ID/input returns the original upstream task or result;
changed input conflicts. Use `status` to read an old operation after changing its
worktree. Registration and the operation association commit together inside the
existing upstream database. Only one worker can claim that task. A crash does not
make its operation ID retryable or replay its command. A new ID is an explicit new
operation, not recovery of the old one.

Acceptance waits for durable worker ownership. The worker survives CLI/MCP client
exit and owns the command's group. If that worker dies, a later status reconciles
its exact birth/group identities and retains either an interrupted receipt or
recovery-pending capacity. Submission interrupted before worker ownership may end
without execution; the same ID still returns its recorded result, never a replay.

Queue time begins on registration and stops at upstream admission. The same atomic
transition records `admitted_at` and starts the execution deadline. Runtime/Git/artifact
preflight consumes this budget; expired preflight cannot launch, and the command
receives only the remaining time. `started_at` means admission, while
`lifecycle.launched_at` records child registration. Failed preflight still records
the admitted interval.
`--wait-seconds 0..30` bounds only observation; expiration does not cancel or shorten
a task's deadlines. Cancel an exact ID explicitly. Eligible foreground completion
normally reports `success`/`failed`; deadline outcomes are `queue-timeout` and
`timeout`. Pending operations report `queued`/`running`. Uncertain closure reports
`recovery-pending` with `capacity_held=true`. Do not force-clear it or change policy
to release it. Later status releases only after verified closure (or a real changed
boot). The original lingering-success cases are now explicit negative-contract
checks: retained capacity while a group lives, then reconciliation after closure;
the old eight-second harness window was not an implementation lifetime promise.

Schema-1 JSON responses include operation/task IDs, request snapshot, queued/start
timestamps, deadline timestamps, runtime configuration
digest, lifecycle/worker identities, result, `capacity_held`, `receipt_path` and
`log_path`. Readable output shows status and those paths for T3. SQLite task/results
remain authoritative; receipt files are serialized exports refreshed by status.
CLI exit 0 means the operation was accepted/read; exit 2 means refusal. Inspect
`status` and the recorded program `exit_code`, not the CLI exit alone, for a build
result. Logs contain verbatim command output. Environment values are not dumped or used as
stored request fields, but arbitrary program output/argv can contain secrets;
this runner does not redact them. Supply credentials through the normal environment
and avoid printing them. Idempotency does not fingerprint environment changes.

## Codex and Claude consumers

Installation generates `providers/codex.toml` and `providers/claude.mcp.json` under
the private root. They point to the same bound launcher with argument `mcp`; no
provider override can pick a root queue or capacity. The stdio tools are:

- `run_command(operation_id, owner, argv, worktree, queue_seconds, execution_seconds, handoff_id=None)`
- `command_status(operation_id)`
- `cancel_command(operation_id)`
- `build_handoff(operation_id, artifacts)`
- `work_report(limit, operation_ids, sample, simlock, lease_ids)`

For artifact sealing and dependent command inputs, use `handoffs.md`.
For job reconciliation, the admission mode and observation-only pressure sampling, use
`diagnostics.md`.

The response schema and operation semantics match the CLI. The facade does not own
or cancel commands merely because its connection exits. Restart the consumer after
activation; a stale MCP process refuses new operations under an old active config.

The generated formats follow the official
[Codex stdio configuration](https://developers.openai.com/codex/mcp/) and
[Claude Code MCP configuration](https://code.claude.com/docs/en/mcp).
They are mergeable templates, not live profile edits. The installation owner
coordinates adoption with the owners of existing holds.

## Upgrade and rollback

```sh
python3 -I -B skills/mac-work/scripts/mac_work.py install \
  --root /absolute/private/mac-work-try --release try-2 --adaptive-capacity --json
/absolute/private/mac-work-try/bin/mac-work activate \
  --root /absolute/private/mac-work-try --release try-1 --json
```

Both operations refuse an active consumer/worker lock or any queued/running/
unresolved row. They also refuse an existing uncontained policy; this pilot never
reinterprets or migrates those holds. Observe/reconcile a known operation before
retrying maintenance; there is no force option. Activation verifies the target
release and switches `current.json` atomically. Old versions and all operation
receipts stay available. The database is not rolled back with code.

Installation checks idle state before building and again before activation.
A new submission during the build can prevent activation; the completed inactive
version remains inspectable and can be activated later when idle. Interrupted or
incomplete version directories are never reused. Install under a new release name
to retry; arbitrary older schema migrations/bootstrap protocol changes are outside
this first pilot. The pre-isolation reviewed launcher has a different bootstrap
hash and cannot be upgraded in place; keep its root/proof and create a fresh private
Try root for the repaired release. Supported artifact handoffs and job/pressure
reports use the contracts above. Installation and device owners coordinate host
profile activation, broader tool/device qualification, pressure policy and capacity
decisions through `plan.md`.

## Prove it privately

`runner_fitness.py --root ROOT --output NEW_PROOF_DIR` drives independent CLI/MCP
clients and harmless marker processes. Run it from the source worktree with a
disposable fixed-capacity root. The harness uses that root for all queue state.
`--case` selects a diagnostic case, not a full qualification. Keep the raw events,
verdicts, transcripts, build/config hashes and committed artifact identity.
`runner_regressions.py --root ROOT --output NEW_PROOF_DIR --case CASE` adds
boundary faults in isolated worker processes using the installed bundle. It never
edits runtime files. Keep its raw worker snapshots as well as verdicts. The
`active-state-replay` case creates separate disposable installs and retains their
damaged database bytes. Use a disposable adaptive root for `adaptive-fifo` and
`adaptive-expiry`. Use a disposable fixed root for the other cases.

The original counterexample in `fitness.md` for arbitrary escapes remains known
unsupported behavior; it is not silently counted as a passing foreground test.
