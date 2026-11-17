# Setup and rollout

Use for an authorized environment setup or adoption check. Installing this
skill does not install SimLock, configure a worker, or prove host integration.
Keep this skill in SreeStack; read runtime rules from `simlock instructions`
rather than also installing a generated SimLock skill or pasting those rules
into every project.

## Establish the worker

1. Inspect existing SimLock, agent-device and host configuration. Reuse the
   established worker and device roots. Check the selected version's release
   and help; website/main features may be newer than the published package.
2. If absent and installation is in scope, install the published CLI with
   `npm install -g simlock`. Check `simlock --help`, `simlock whoami`,
   `simlock instructions`, `simlock doctor` and `simlock catalog`.
   Configure agent-device using the current SimLock and host instructions.
   Verify its capability is enabled on each selected worker and gateway; an
   installed executable alone does not establish that the bridge is available.
   Keep credentials in the approved credential path, outside run evidence.
3. For a new worker, preserve the isolated device roots and supported lease
   identity. Set an explicit capacity appropriate to the machine and concurrency.
   For example, this bounds iOS definitions to four, Android definitions to one,
   and the total running devices to four:

   ```sh
   simlock config set capacity '{"strategy":"fixed","config":{"maxRunning":4,"ios":{"maxDevices":4,"maxRunning":4},"android":{"maxDevices":1,"maxRunning":1}}}'
   ```

   These match this Mac pilot's existing 4/4/1 limits; do not change them without
   the owner's measured capacity decision. Set the supported
   idle shutdown/deletion policy and inspect warm-pool behavior; warm devices
   can be exempt from idle shutdown. SimLock 0.7 retires virtual devices on
   release; the next lease receives a new copy of a seed or named baseline.
   Reuse the active lease within one run, not a released device ID or app state.
   `lease.identity` does not restore cross-lease virtual-profile reuse.
   Changes requiring a SimLock daemon
   restart belong in a maintenance window with its consumers accounted for;
   ordinary agents do not restart a shared daemon to repair a run.
4. For T3 adoption, follow [T3 connection setup](t3.md#connection-setup).

Use the current [configuration reference](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/reference/configuration.mdx),
[capacity guidance](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/worker/capacity.mdx)
and [device roots and cleanup](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/worker/cleanup.mdx).

The installed 0.7 retirement behavior is pinned in
[virtual source/baseline semantics](https://github.com/callstackincubator/simlock/blob/392e0ac5a8d1168d19fb3d4447b908e05652d1e5/docs/internal/adr/0061-every-virtual-device-is-a-copy-of-a-source-and-a-baseline-is-a-named-source.md)
and [release dispatch](https://github.com/callstackincubator/simlock/blob/392e0ac5a8d1168d19fb3d4447b908e05652d1e5/src/core/reclaim-coordinator.ts#L103).
Saving an explicitly authorized named baseline ends its lease; future compatible
leases copy that source. It is not retention of the released virtual device.

## Migrate existing resources without adopting their data

Inventory managed and unmanaged devices separately. Keep user inspection
devices, retained data and devices with uncertain consumers outside SimLock's
disposable pool. SimLock does not automatically adopt or clean existing
unmanaged devices. Use Repo Cleanup's ownership checks for individually
authorized legacy disposal; names, age and disk pressure do not establish it.

Record the migration's measured baseline and review date. The November 1, 2026
audit reported 58 simulator definitions and about 143 GB in iPhone/iPad folders,
up 47 GB since October 26. Treat that as historical context, not a current
measurement or a deletion list.

Use `simlock status --json`, `simlock list --leases` and
`simlock cleanup --dry-run` for owners, device states and proposed cleanup.
Measure bytes for the actual managed roots, task output folders and retained
locations with filesystem disk-usage tooling. Free filesystem space and device
counts alone do not show per-resource usage. Include retained owner/reason/review
records and unresolved legacy resources in the report.

## Prove the supported path before broad use

Use disposable fixtures and the project's public run command. Record versions,
commands, receipts, observed results and evidence outside disposable outputs.
For agent-device on iOS, include [helper preparation](workflow.md#run-and-record)
before app commands.
Mark each unexercised case blocked or untested; source tests do not establish
that this machine's native integration works.

| Case | Required observation |
| --- | --- |
| Two independent agents/projects request the same model/runtime | Distinct active device IDs and leases; each installs a distinguishable build and sees its own state. |
| A second run targets an occupied device or foreign lease | Supported interface refuses access or queues; the first build and state survive. |
| Sibling agents share a requester or session | A collision never authorizes reuse, renewal, cancellation or release of the sibling's lease or queued request; isolate through a supported route or report blocked. |
| Normal completion, command failure, partial setup and cancellation | Own consumers exit; own lease ends; virtual device retirement/deletion completes or reports failure; disposable host outputs are removed. |
| Release A while B remains active | B's app/state and lease remain usable; A's cleanup does not stop B's processes. |
| Retry A's release after its device is leased to C | Every acquisition has a fresh lease ID under the chosen generated/caller-ID policy; A's old release cannot resolve to C, and C's build and state survive. |
| Acquire again after virtual release | A new lease/device copies the compatible source or baseline; the old device is retired; the configured bound holds. |
| Crash the run owner or lose renewal | Managed recovery follows the documented expiry policy; no custom cleanup acts on the cached device ID. |
| Native command hangs or cleanup fails | A bounded error names the operation and diagnostics; the device stays unavailable when cleanup is unresolved; shared services remain running. |
| Retained inspection device and evidence | Their app data and retained files survive disposable run cleanup and idle maintenance. |
| T3 inspection, when supported | Panel and returned driver show the same leased device/build; handing off and closing preserve the recorded lifetime. |

Do not declare the rollout complete until these cases pass on the chosen native
route. Run fixtures through the installed tool's lifecycle; do not simulate
success by editing its registry or deleting devices manually.
