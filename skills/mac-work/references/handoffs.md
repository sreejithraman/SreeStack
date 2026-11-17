# Build before device acquisition

Finish a device-independent, eligible foreground build before acquiring an
interactive device. Check its canonical receipt: success, program exit code 0,
capacity_held=false and closed lifecycle. Seal the exact install/test artifacts:

```sh
MAC_WORK_ROOT/bin/mac-work handoff --id BUILD_ID \
  --artifact /absolute/build/App.app --artifact /absolute/build/tests --json
```

Use the returned manifest paths and hashes in the run evidence. The manifest
binds producer owner/task/operation, worktree/revision, config digest and artifact
contents. Repeating identical evidence returns the same manifest; changed evidence
conflicts. Internal artifact symlinks are recorded, external links and special
files refuse. Inspection is bounded to 10,000 entries, 2 GiB and 30 seconds total;
choose the needed outputs, not an entire build/cache directory. The manifest is
evidence, not a filesystem snapshot: keep those outputs stable through consumption.

## Choose the consumer

For interactive work, follow [Simulator Lifecycle](../../simulator-lifecycle/SKILL.md)
and its [T3 route](../../simulator-lifecycle/references/t3.md). Acquire after the
build gate, consume the exact artifacts, and group the device-dependent checks
in one bounded, renewed lease. Keep the exact driver/session returned by
device_open. Record the manifest plus actual run/request/lease/device/host IDs
and both command and teardown outcomes in the existing project run evidence.
Use status to read late command results; do not replay a build to retrieve them.

**Automatic T3 boot admission remains unsupported.** The inspected device_open
schema has hostId/deviceId/platform and directly calls DeviceService.open;
there is no established external queue hook or t3 device CLI. SimLock still
governs leases/boots under the existing global4/iOS4/Android1 limits. A build
receipt does not prove boot admission, boot cancellation or T3 session teardown.
Do not wrap native device calls in a timed shell reservation or invent heartbeat,
RPC or resource-registry support. A native integration seam remains a follow-up.

For an existing foreground project runner whose supported acquisition, renewal,
queued-cancel/late-grant reconciliation, consumer stop and teardown are already
bounded and ownership-checked, preserve its original interface:

```sh
MAC_WORK_ROOT/bin/mac-work run --id CHECK_ID --owner THREAD \
  --worktree /absolute/project --handoff BUILD_ID \
  --queue-seconds 120 --execution-seconds 300 --json -- \
  ./existing-project-runner --artifact /absolute/build/App.app
```

The runner rechecks manifest/artifact hashes after admission, before spawning the
command. Drift fails before that command can acquire. The manifest digest joins
the immutable request in the same upstream operation row. Late identical
submission returns its result even after outputs are removed, without executing
again. No args, lifecycle flags, leases or renewal loops are inserted into the
project command. Follow the existing runner's exact artifact interface and
[lifecycle contract](../../simulator-lifecycle/references/project-runners.md).
Report command result separately from release/cleanup failure; a passing test
with failed teardown is incomplete. Capacity release proves command-group closure,
not asynchronous SimLock retirement or absence of uncertain device consumers.

The MCP equivalents are build_handoff(operation_id, artifacts) and the optional
handoff_id on run_command. They use the same installed root and evidence.

## Eligibility and proof limits

Foreground appearance alone does not qualify a tool. Keep heavy work in the
launched process group and wait for it. Swift 6.4.2's ordinary universal build
was observed spawning compiler/clang/frontend/dsymutil processes in distinct
groups while waiting for them. A direct graceful SIGTERM left no observed
descendants, but that is not canonical cancellation/crash qualification. Swift
and xcodebuild are not qualified examples here. The command qualification owner
maintains lifecycle proof; do not weaken the contract or kill shared build services to fit it.
The [qualification record](plan.md#real-command-eligibility-evidence) records
the installed Node + JS pnpm invocation of SimLock
`run build:daemon:run` staying in one group for a 2.371s build. Native pnpm12/Turbo
spawned other groups and is unqualified. Eligibility attaches to the exact
qualified invocation/toolchain, not to a generic command name.

`handoff_fitness.py --root ROOT --output NEW_DIR` proves the public CLI/MCP seams
using actual pinned admission plus controlled foreground runner fixtures. It
checks exact artifacts, build failure before acquisition, queued/running cancel,
drift before launch, late no-replay, command/release/cleanup failures and untouched
foreign fixture identity. Fixture leases are not SimLock or hardware proof.
Original arbitrary-detach counterexamples remain outside the user-approved
process-group boundary, not relabelled as passing.
