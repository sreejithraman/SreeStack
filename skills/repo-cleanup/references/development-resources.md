# Development resources

## Identify resources

Identify task-owned resources from available conversation and tool results.
Fill gaps using existing logs, handoffs, and current platform state.

For simulator/emulator resources, identify the lifecycle manager first. Use
[Simulator Lifecycle](../../simulator-lifecycle/SKILL.md) for SimLock runs and
their receipts. Keep the ownership reconstruction below for legacy resources
and retained devices; an unmanaged device is not adopted into the disposable
pool just because it appears idle.

## Clean up

Before each action, recheck the task evidence against current identity, use,
and retention. Keep resources needed for user inspection or another consumer.
Preserve uncertain targets and report missing evidence or unavailable tooling;
continue independent cleanup.

- **SimLock devices and installs:** stop and await only this run's consumers,
  export retained evidence, and release its exact lease through the acquiring
  interface. Let SimLock wipe and recycle the device. Inspect status/events for
  completion or failure. Never translate an old receipt, expiry or vanished
  owner into a raw uninstall, shutdown, erase or delete. A replacement lease
  belongs to its new run. Clean this run's disposable host outputs separately
  after their writers exit and current ownership/retention still match.
- **Mac apps and supporting processes:** quit only instances this task launched;
  preserve reused processes. Match the task's app/executable path and process
  identity, including start time or equivalent session identity, immediately
  before stopping. An app name or bundle ID alone is insufficient. Quit apps
  gracefully, preserving unsaved user work, and stop their task-owned servers
  and watchers separately.
- **Unmanaged simulator/emulator installs:** uninstall only task-installed apps and test
  runners with disposable data. Immediately before uninstall, compare the current
  build identity and install evidence against the task evidence. Preserve replaced
  or mismatched installs, or any install whose continued ownership cannot be proved.
  Use exact device and bundle/package IDs:
  `xcrun simctl uninstall <udid> <bundle-id>` or
  `adb -s <serial> uninstall <package-id>`; scope Android removal to the owning
  user when needed. Uninstalling can remove app data; Android's `-k` retains it
  ([adb docs](https://developer.android.com/tools/adb)). Confirm removal by
  re-listing installed apps on kept devices. A separate uninstall is unnecessary
  when the entire temporary device is eligible for deletion.
- **Unmanaged simulator/emulator devices:** shut down and delete a temporary device only
  when it was created solely for this task and all its data is disposable. Keep
  device definitions and data otherwise; shut down a kept device only when this
  task booted it. The shared retention and consumer check above applies to both
  shutdown and deletion. Use platform tooling scoped to the exact Simulator ID
  or Android AVD; a running Android serial alone does not identify the saved AVD
  to delete. Preserve physical devices, shared runtimes, and SDKs.
