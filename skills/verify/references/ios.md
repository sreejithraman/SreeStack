# iOS Verification

Use this reference for iOS app workflows. Choose interactive driving for
exploration, reproduction, and interface inspection; use project suites for
repeatable regression checks. Combine them when the selected coverage needs both.
Verify's main procedure owns coverage, state, verdicts, and cleanup for either path.

## Target and tooling

Preserve the requested OS and Simulator or physical-device target. Otherwise use
a Simulator when it can exercise the selected workflow; choose suitable hardware
for device-dependent assertions. Identify the project or workspace, scheme, and
build configuration. Record the app/build revision, bundle identifier, target ID,
model, and OS version or Simulator runtime supporting the deployment target.

Reach and drive simulators through [Simulator Lifecycle](../../simulator-lifecycle/SKILL.md).
For a physical device, choose it as Xcode's run destination or use
[`xcrun devicectl`](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference)
for available device operations. Interact through the device or connected interface
tooling, and check its capabilities first. If no tool can drive it, ask the user to
do the steps.

## Choose a regression harness

Reuse the project's established harness. For new iOS UI workflow tests, prefer
XCTest with XCUIAutomation (XCUITest). For new Swift unit tests, prefer Swift
Testing; use XCTest for performance tests. Follow the project's supported
toolchain and keep existing test coverage useful during incremental adoption.
See [Apple's testing guidance](https://developer.apple.com/documentation/xctest).

Keep one-off checks interactive when they supply the selected evidence. Add or
change executable tests when the active task includes implementation, harness
repair, or reusable verification setup. Keep test files, test plans, fixtures,
and CI configuration in the product repo.

## Prepare and run native UI tests

Discover the project's UI test target, scheme, test plan, wrapper command, and
CI configuration. Select the explicit Simulator or device destination and check
that the runner uses it. For a Simulator, check its clone settings too, using
[build and test target compatibility](../../simulator-lifecycle/references/project-runners.md#build-and-test-target-compatibility). Use the project's Xcode or `xcodebuild` workflow;
confirm toolchain-dependent options through installed help and
[Apple's test-running guidance](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results).

Prepare the build, signing and device access where required, fixtures,
permissions, locale, and authentication. Inspect test setup, launch arguments,
reset hooks, and teardown so state changes fit the disposable target and the
workflow's starting assumptions. Keep credentials in the approved runtime
delivery path from [authenticated verification](authenticated-verification.md).

Map selected test methods to required workflow assertions. Inspect test-plan
configurations, selection filters, disabled tests, skips, expected failures, and
retries. Reconcile the tests actually executed with the selected assertions under
Verify's main procedure. Record the runner's exit status. Export the screenshots,
attachments, and log excerpts a verdict cites from the result bundle into
[kept proof](../SKILL.md#keep-proof-not-runs); the bundle itself is run scratch.

Pair public UI actions with explicit outcome assertions. Prefer accessibility
identifiers and meaningful labels. Wait for observable states with bounded
deadlines; assert the result of an operation as well as readiness to interact.
Give each standalone test a known starting state and isolated fixtures. Use the
fresh read required by Verify for persistence assertions.

When establishing a new harness, run a representative workflow against the
actual build and target. In a disposable copy, introduce a known assertion
mismatch and confirm that the runner fails with useful retained evidence. Keep
this failure-detection check separate from the real product verdict.

## Build and launch

- Build and run the intended scheme. Rerun against the changed revision after an
  authorized code fix.
- After launch, confirm that the expected app and screen are visible. Capture a
  screenshot and inspect the accessibility hierarchy when the available tooling
  exposes it.
- Preserve the workflow's data assumptions. Reset, reinstall, seed, or relaunch
  only when the required starting state calls for it, and report material setup.

## Observe and interact

- Target controls by accessibility identifier or label when supported. When the
  available tooling exposes only rendered state, interact from the current view,
  recapture after every action, and report semantic or accessibility coverage as
  untested. Derive coordinate targets from current hierarchy or bounds when they
  are available rather than from a stale screenshot.
- Recapture the hierarchy after navigation, presentation, rotation, animation, or
  any interaction that may move the target.
- Exercise text input, gestures, scrolling, orientation, permissions, and
  background or foreground transitions when they belong to the selected workflow.
- When a save or update should persist, verify it through a fresh read path by
  relaunching and refetching, inspecting the stored value through an independent
  interface, or reopening through a path known to create a new model and reload
  durable storage. Record the persisted value observed.
- Check both function and presentation: hit targets, clipping, Dynamic Type where
  relevant, safe areas, keyboard avoidance, and expected system dialogs.
- Capture application logs when the app crashes, exits, hangs, or behaves
  differently from the visible state. Use the process and bundle identifier to
  separate app output from unrelated system noise.

Keep an explicitly requested Simulator check in Simulator. Exercise the portions
the Simulator supports and name the exact device-only step that remains unverified.
For physical-device checks, use available Xcode and device controls; if suitable
hardware is unavailable, report the device-specific assertions as blocked.

## Evidence

Record the command and toolchain, scheme/test plan, build identity, target
identity, fixture state, selected tests, and per-assertion outcomes in
[kept proof](../SKILL.md#keep-proof-not-runs).
Capture the workflow states needed to support visual claims. Use
[interface review](interface-review.md) for relevant visual, Dynamic Type,
keyboard, focus, touch-target, and assistive-technology checks. Exercise VoiceOver
usability and hardware-dependent behavior through suitable checks on the required
target; accessibility identifiers supply selectors for automation.
