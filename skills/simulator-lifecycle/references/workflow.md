# Run and handoff conventions

Use SimLock for disposable agent devices across projects. SimLock owns allocation,
leases, wiping and reuse; project runners own build processes and host output.
Keep user inspection devices and valuable app data outside the disposable pool.

## Choose the route before acquiring

Read the host's live device contract and the project's test command. Identify
whether the requested target is disposable or a retained inspection device.
Preserve an explicitly requested device and its data.

The entrypoint's installed-version rules govern disposable work. If SimLock
is unavailable, continue independent build or code work and report the missing
prerequisite. Environment setup and adoption checks use
[setup and rollout](setup.md).

In T3, use `device_list`, then `device_open`, so the user can watch the device, and keep
the exact `agent-device` launcher, host configuration, and session flags it returns on
every command. Prefer current snapshot refs. Report an unavailable platform. See the
[T3 device contract](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/toolkits/device/handlers.ts#L28). Confirm
that the host's documented SimLock integration acquires and drives the same
underlying lease. A regular `device_open` session alone does not establish a
SimLock lease. A device from a `simlock-` host in `device_list` is that integration. If it
is unavailable, report interactive disposable
verification blocked; do not combine an unrelated CLI lease with a panel session
or substitute another driver. Project test suites may use their supported
SimLock route independently of interactive panel support.

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
Prefer reusable devices within the configured capacity. SimLock handles device
creation and resetting.

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
deadline, host and exact device ID, runtime/model/device set, installed bundle IDs
and build revisions or hashes, spawned process identities, and exact temporary
output paths. Update it as effects happen, including failed installs and partial
setup. This is evidence for recovery, not a second device ownership registry.
Keep tokens and connection secrets out of the receipt.

## When a session fails

Keep the exact command, error/code, deadline, request or diagnostic ID and log
paths with the run receipt's versions, workspace, session and lease/device
identities. Separate device-tool failure from app failure; a passing build or
generic doctor check does not prove runner readiness.

In T3, quote the error and follow its recovery advice once through its supported
tools and returned driver, including any requested diagnostic. If that still fails, report the
blocker and stop device work, unless a failure before a grant applies below. Preserve T3's connection, session and install
directory; the skill does not authorize a second lease or an alternate driver.
If a diagnostic is unavailable through that route, record that limit.

- **Failed before a grant:** no lease exists, so ended-lease recovery does not apply.
  Check `simlock status --json` for your own queued request or late grant. If you find
  one, apply the [run ownership guard](#choose-the-route-before-acquiring) and don't
  retry. Otherwise retry once, counting any retry the host's error advised, then try one
  other model from `device_list`, unless the user named the target. If that model boots,
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
sessions and services. Export required evidence before release: SimLock wipes
apps, files and settings. Release acknowledgement ends the lease; it does not
prove the background wipe finished. Check status/events for reuse readiness,
quarantine or cleanup failure before declaring teardown complete.

Remove only the runner's disposable host outputs after its writers have exited
and current path ownership and retention still match. Use
[development resource cleanup](../../repo-cleanup/references/development-resources.md#clean-up)
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

SimLock intentionally wipes disposable devices after release or expiry; it is
not a guarantee that arbitrary external consumers have stopped. Work requiring
preservation after a missed renewal belongs outside that pool.
See [lease lifecycle](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/using-devices/lease-lifecycle.mdx).
