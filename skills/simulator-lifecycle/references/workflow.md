# Run and handoff conventions

Use SimLock for disposable agent devices across projects. SimLock owns allocation,
leases and device retirement/recovery; project runners own build processes and host output.
Keep user inspection devices and valuable app data outside the disposable pool.

## Choose the route before acquiring

Read the host's live device contract and the project's test command. Identify
whether the requested target is disposable or a retained inspection device.
Preserve an explicitly requested device and its data.

The entrypoint's installed-version rules govern disposable work. If SimLock
is unavailable, continue independent build or code work and report the missing
prerequisite. Environment setup and adoption checks use
[setup and rollout](setup.md).

For T3 acquisition and interaction, follow [T3 device routing](t3.md).
Prepare device-independent artifacts first through
[Mac Work handoffs](../../mac-work/references/handoffs.md). Acquire only after
the build receipt reports success, exit code 0 and verified closure. The command
queue does not automatically admit T3 device boots; SimLock retains that boundary.
Project test suites may use their supported SimLock route independently of
interactive panel support. A panel or metadata failure blocks only work that
depends on it; authorized independent build/test paths may continue under the
same ownership rules. Runner success does not prove panel recovery or replace
required visual proof. Honor explicit holds by their stated scope and release
condition, including holds on native suites or all device work.

Outside a host-owned device route, choose one of SimLock's supported allocation
interfaces for the run: its CLI, MCP, or agent-device bridge. With the bridge,
`agent-device open` acquires and `close` releases; do not acquire a second CLI
lease for it. Give each concurrent agent/run the distinct identity or session
required by the chosen interface. Check the identity actually reported rather
than assuming subagents have independent identities.

A shared requester or session does not establish run ownership. On
`REQUESTER_ALREADY_LEASED`, reconcile the live lease/device with this run's
recorded acquisition before reusing, renewing or releasing it. Apply the same
guard to queued requests, cancellation and late grants. Leave a sibling's or
uncertain resource untouched; use a supported isolated requester/session or
report the route blocked. Upstream advice to use or release a held lease applies
only after this run's ownership is established.

See [agent connection](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/getting-started/connect-your-agent.mdx)
and [agent-device integration](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/using-devices/agent-device.mdx).

## Drive the device

Run repository test suites as project test operations, and honor the host's limits on
them. Before you run a native suite, even an existing one, check its destination, device
set, and clone settings against
[build and test target compatibility](project-runners.md#build-and-test-target-compatibility).
Serialize suites and interactive work that share a device, app data, or backend
fixtures, unless each run isolates them. Independent disposable runs need independent
leases.

Use platform tools for builds, logs, and what the device driver doesn't cover, while
SimLock owns the target. Outside a host device runtime, take the shortest path that shows
the result:

- Xcode's MCP tools can build, run, drive the Simulator, and take screenshots. Open the
  project or workspace in Xcode first. With the headless server enabled,
  `xcrun mcp-server open <project-or-workspace>` can open it, and `xcrun mcp-server status`
  helps when discovery fails. External agents connect through
  [`xcrun mcpbridge`](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode).
  Simulator interaction arrived in
  [Xcode 27](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes).
- `xcodebuild` and `xcrun simctl` cover build, install, and launch on targets you're
  authorized to control.
- Simulator or computer-use tools can supply the remaining interaction.

Check a tool's capabilities before you rely on it.

## Run and record

Use a compatible model/runtime from the catalog and keep the exact granted
device ID, host, device set and lease identity through build, install and test.
Reuse this run's active lease for its device-dependent checks. The qualified
maintained local build retires released virtual devices and supplies new copies
from seeds or named baselines;
do not expect the next lease to preserve that device ID or run data. See
[installed source/baseline semantics](setup.md#establish-the-worker).

### iOS mode

Check the iOS lease's reported mode. A `slim` device turns off background
services an app run rarely needs. When the work under test needs one, request
`--mode full`, or keep its categories running with `--except <category,...>`
(`deviceExcept` through agent-device):

| Feature | Category |
| --- | --- |
| Push notifications, StoreKit testing | `store` |
| Universal links | `web` |
| Spotlight | `search` |
| App Clips | `other` |
| Device management | `mdm` |
| Photos picker | `photos` |
| Contacts and Calendar pickers | `pim` |

On a slim device, rerun a misbehaving feature on a full one before calling it
an app bug. See
[slim categories](https://github.com/MobAI-App/simslim/blob/ab8ce9f01951c1b13fed92bedea7919d8942f841/profiles.go) and
[slim lease exceptions](https://github.com/callstackincubator/simlock/blob/d30c24d8596dc27ce2f7bf4361199db1968f8a34/docs/internal/adr/0066-a-slim-lease-may-keep-named-categories-running.md).

### Android mode

Keep this Mac pilot's configured slim default and record the grant's actual mode.
The maintained local build's Android slim applies lower guest RAM and a verified
guest policy, including animation changes. Use an explicit full lease for fidelity checks; full/slim use
separate sources and a baseline must match its saved mode. Android has no iOS
`except` categories. Guest RAM is not host memory overhead. This qualifies the
maintained local build, not native Android slim in stock upstream 0.7. The local
source path is `docs/internal/adr/0078-android-slim-is-a-native-source-and-guest-policy.md`
at the unpublished full SHA in [local build qualification](setup.md#establish-the-worker).

### Run identity and helper

For iOS work through agent-device, prepare its XCTest helper after acquiring
the lease and before app commands. Discover the installed driver's
`help prepare`; where supported, run `prepare ios-runner --platform ios` through
the host-pinned driver with a bounded startup timeout, such as `--timeout 300000`.
Cold helper builds can exceed an ordinary app-launch deadline. Keep the lease
renewed during preparation, record its result, and stop app work if it fails.

Keep requester/run identity separate from lease identity. Prefer manager-generated
lease IDs; if choosing one, mint a fresh, never-reused ID for every new acquisition,
including across retries and restarts. Reconcile an uncertain operation before
starting another acquisition; do not recycle an ended lease ID.

Use the project's normal runner with acquisition and teardown around the whole
device-dependent run. Follow [project runner integration](project-runners.md)
when adding or repairing that command. Keep the lease renewed during builds,
test waits and inspection, including time with no agent-device commands. Stop
device-dependent work on lease loss; a cached UDID does not authorize another
operation. Report a hung command with its identity, deadline and logs. Leave
shared Simulator, CoreSimulator and adb services running.

Keep one run receipt beside the project's existing run evidence. Record the
project/worktree and task/run owner, chosen interface/session, lease ID and
deadline, host and exact device ID, runtime/model/device set, lease mode and kept categories, installed bundle IDs
and build revisions or hashes, spawned process identities, and exact temporary
output paths. Update it as effects happen, including failed installs and partial
setup. This is evidence for recovery, not a second device ownership registry.
Keep tokens and connection secrets out of the receipt.

## When a session fails

Keep the exact command, error/code, deadline, request or diagnostic ID and log
paths with the run receipt's versions, workspace, session and lease/device
identities. Separate device-tool failure from app failure; a passing build or
generic doctor check does not prove runner readiness.

For T3 failures, apply [T3 recovery and stop rules](t3.md#recovery-and-stop)
before the cases below. Host and task limits constrain retries and substitutions;
these cases do not authorize an attempt they prohibit.

- **Failed before a grant:** no lease exists, so ended-lease recovery does not apply.
  Check `simlock status --json` for your own queued request or late grant. If you find
  one, apply the [run ownership guard](#choose-the-route-before-acquiring) and don't
  retry. Otherwise retry once, counting any retry the host's error advised, then try one
  other model from the host's supported catalog, unless the user named the target. If that model boots,
  use it and label the substitution. If the same boot failure repeats on iOS on this Mac,
  check [break glass](break-glass.md). Otherwise stop device work and report the blocker.
- **Lease ended or target missing:** stop using the old target. Reconcile the
  lease through its original interface. Reopen only through the host's supported
  recovery path, recording the new grant; the old app state may have been wiped.
  A missing Xcode destination alone does not establish that a device was deleted.
- **Ownership conflict:** compare the reported owner and workspace with this
  run's acquisition evidence. Even `DEVICE_IN_USE` naming the expected session
  does not authorize clearing a claim or taking over the device. Preserve an
  unresolved mismatch for the integration owner.
- **Timeout or runner startup failure after a grant:** retain the bounded attempt's logs and
  result. Keep shared services running and leave device recovery to SimLock.
  Report persistent failures rather than cycling devices or increasing timeouts
  until a command happens to pass.

Report the original failure, recovery/diagnostic result and unverified work.
Use [finish or retain](#finish-or-retain) for this run's teardown, recording any
resources whose release or cleanup remains uncertain. A later successful run
does not establish that an intermittent failure was fixed.

## Finish or retain

On success, failure or cancellation, stop and await the run's device consumers
before releasing its lease through the acquiring interface. Preserve other
sessions and services. Export required evidence before release: virtual devices
and their run data are retired/deleted; physical devices follow their purge
policy. Release acknowledgement ends the lease; it does not prove asynchronous
deletion/purge finished. Check status/events for completion, quarantine or cleanup
failure before declaring teardown complete. New virtual leases copy a source;
they do not reuse the released profile.

Remove only the runner's disposable host outputs after its writers have exited
and current path ownership and retention still match. Use
[development resource cleanup](../../cleanup/references/development-resources.md#clean-up)
only for this run's ownership-checked process and host resource disposal; routine
teardown does not invoke repository housekeeping. An old receipt, expired lease
or missing renewal never
authorizes an agent to erase, delete, shut down or uninstall from a device.
Leave device recovery to SimLock; diagnose uncertain state rather than replaying
cleanup against a device ID that may now belong to another run.

For a user inspection handoff, use [Show Me](../../show-me/SKILL.md). A pooled
device is a temporary viewing surface only while its lease is renewed. For data
that must survive lease loss, use an explicitly designated inspection device
outside the pool, or export a supported durable artifact before release. Record
what is kept, why, for whom, its location, who maintains any live lease, and a
review date, outside disposable output. A retention note cannot suspend SimLock's expiry or wipe policy.

SimLock intentionally disposes of virtual run data after release or expiry; it is
not a guarantee that arbitrary external consumers have stopped. Work requiring
preservation after a missed renewal belongs outside that pool.
See [lease lifecycle](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/using-devices/lease-lifecycle.mdx).
