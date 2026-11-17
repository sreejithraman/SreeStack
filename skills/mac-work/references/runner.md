# Foreground command pilot

The user selected **Foreground commands** for the pilot. Commands must wait for
all their heavy work and keep it in the launched process group. Detached sessions,
background build services and shared daemons are outside this contract. This is
cooperative routing, not OS containment or raw-shell prevention. For example,
use Gradle's `--no-daemon` mode or a project wrapper whose foreground lifetime is
verified. Do not blindly kill a shared build daemon.

## Create a task-owned Try install

From this repository root:

```sh
python3 skills/mac-work/scripts/mac_work.py install \
  --root /absolute/private/mac-work-try --release try-1 --json
/absolute/private/mac-work-try/bin/mac-work run \
  --id example-1 --owner my-thread --worktree "$PWD" \
  --queue-seconds 60 --execution-seconds 10 --wait-seconds 10 \
  --json -- /usr/bin/true
/absolute/private/mac-work-try/bin/mac-work status --id example-1 --json
/absolute/private/mac-work-try/bin/mac-work cancel --id example-1 --json
```

The parent keeps the final Try root and exact runnable command in the owner report.
No live profiles or existing holds are changed by these examples. Installation
requires `uv` and downloads only the pinned Python/dependency/source artifacts.
`--archive PATH` reuses the verified upstream archive. `--help` owns remaining
flags. Without an explicit root, the standard private host root is
`~/Library/Application Support/mac-work`. Use one root across projects/providers;
extra roots are for disposable tests, not independent project admission pools.

The root contains `current.json`, immutable named `versions/`, a root-bound
`bin/mac-work`, and shared `state/queue.db`. The active pointer binds an immutable
config by digest. Config fixes root `heavy=1` and `ownership_contract=process-group`.
It binds the runtime interpreter, candidate source/patch/dependency pins, and
bundled runner code. CLI/MCP clients cannot select another queue or cap. Runtime,
source, patch, code, config or policy drift refuses execution; there is no direct
shell fallback. Version directories are never overwritten by the installer.

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

Queue time begins on registration. Execution time begins after upstream admission.
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

- `run_command(operation_id, owner, argv, worktree, queue_seconds, execution_seconds)`
- `command_status(operation_id)`
- `cancel_command(operation_id)`

The response schema and operation semantics match the CLI. The facade does not own
or cancel commands merely because its connection exits. Restart the consumer after
activation; a stale MCP process refuses new operations under an old active config.

The generated formats follow the official
[Codex stdio configuration](https://developers.openai.com/codex/mcp/) and
[Claude Code MCP configuration](https://code.claude.com/docs/en/mcp).
They are mergeable templates, not live profile edits. The parent owns adoption of
those templates and the existing hold inventory.

## Upgrade and rollback

```sh
/absolute/private/mac-work-try/bin/mac-work install \
  --root /absolute/private/mac-work-try --release try-2 --json
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
this first pilot. Host profile activation, project handoffs, devices, pressure
policy and capacity increases remain parent-owned later tasks in the [plan](plan.md).

## Prove it privately

`runner_fitness.py --root ROOT --output NEW_PROOF_DIR` drives independent CLI/MCP
clients and harmless marker processes. Run it from the source worktree. It never
accepts a live state directory separately from the explicit installed root.
`--case` selects a diagnostic case, not a full qualification. Keep the raw events,
verdicts, transcripts, build/config hashes and committed artifact identity.
The [original counterexample](fitness.md) for arbitrary escapes remains known
unsupported behavior; it is not silently counted as a passing foreground test.
