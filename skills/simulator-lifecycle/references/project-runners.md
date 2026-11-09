# Project runner integration

Use when adding or changing a project's normal simulator build/test command.
Keep implementation, tests and CI configuration in that project. The shared
skill owns the lifecycle contract; SimLock remains the device authority.

## One run boundary

Wrap the whole device-dependent operation, including installs performed by
test runners, in one acquisition/teardown scope. Reuse an existing runner hook
when it can guarantee the same behavior on success, failure and cancellation.
Discover the selected SimLock interface's current API rather than implementing
another lease registry, heartbeat protocol or device reset helper.

The runner must:

- Acquire a compatible device once, give concurrent runs independent supported
  identities, and propagate the exact grant/environment to every consumer. Apply
  the [run ownership guard](workflow.md#choose-the-route-before-acquiring) and
  [lease identity policy](workflow.md#run-and-record); a shared requester or a
  reusable task ID does not authorize another run's acquisition or teardown.
- Keep the lease renewed while builds or tests run, even when no UI commands
  occur. A one-shot detached lease needs a supported renewal owner; choosing a
  long TTL alone is insufficient. Observe lease loss and stop device-dependent
  work before any further command.
- Build into the worktree's normal DerivedData so later runs reuse it, and
  serialize builds that share it. Allocate a unique run directory for temporary
  fixtures and logs, and put Verify's
  [kept proof](../../verify/SKILL.md#keep-proof-not-runs) outside it. Record
  created paths and process identities as they are created.
- Capture PIDs at spawn and use existing ownership-checked stop tooling. Recheck
  start identity, executable/workspace and other consumers immediately before
  stopping. Await all run-owned writers, including test helpers and descendants;
  a root process exiting is insufficient if it left children running.
- Export the device's screenshots and logs that kept proof needs before
  releasing, because SimLock wipes the device. Release through the same
  interface in teardown even when acquisition only partly succeeded; reconcile
  an uncertain grant by request/run identity before requesting another device.
- Bound queued acquisition and use supported cancellation only for a request
  proven to belong to this run. Killing a waiting CLI process does not necessarily
  cancel its queued request. Reconcile whether it was cancelled or granted, and release an eventual
  grant through its original owner instead of leaving it to expire. Check the
  installed interface's cancellation support before choosing it for a runner.
- Remove disposable host paths only after writers are gone, the paths are still
  run-owned and retention is unchanged. Refuse shared caches, roots, symlink
  substitutions and uncertain ownership. Retain and report unresolved output
  instead of deleting while a writer may still use it.
- Report both the original command result and teardown result. A successful test
  with failed release or cleanup is incomplete teardown. A release reply does
  not prove the asynchronous device wipe finished.

Crash recovery reads the existing run receipt and live SimLock state. Stop only
proven surviving run-owned processes, remove only proven disposable host paths,
and let SimLock reconcile its devices. Expiry never turns a receipt into device
cleanup authority. If a process or path cannot be proved safe, retain it with
its owner, reason and review date. Keep the receipt until recovery is settled.

## Build and test target compatibility

Runners using agent-device on iOS include the
[helper preparation step](workflow.md#run-and-record) inside the lease scope,
with its own startup budget before app operations.

Read the grant's device set and environment. With isolated iOS device sets,
Xcode 27 supports `-DVTSimulatorSetLocation` alongside the granted destination.
Older tools may need a generic simulator build followed by a supported install;
that can build an app but cannot stand in for a requested native UI test suite.
See [SimLock build routing](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/using-devices/build-and-run.mdx).

Pass the exact destination and per-run output locations through the project's
existing Xcode wrapper. Inspect parallel-testing and clone settings: a test
runner that silently creates extra simulators bypasses the pool bound. Disable
that behavior through supported options or use an integration that explicitly
accounts for it. Do not claim capacity is enforced while untracked clones exist.

Wire local agent commands and CI to this same runner; document any route that
cannot yet use it. Verify two simultaneous runs and independent teardown before
switching the project default. Linking this skill alone does not enforce a
project runner that has not been integrated.
