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

For interactive Simulator checks in T3 Code, use `device_list`, then `device_open`
so the user can watch the selected device. Drive it with the exact `agent-device`
launcher, host configuration, and session flags returned by `device_open`, keeping
those flags on every command. Prefer current snapshot refs and use
`device_screenshot` for visual inspection. Follow the live host device contract
and report an unavailable platform.
See the [T3 device contract](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/toolkits/device/handlers.ts#L28).

Run repository regression suites as project test operations. Use the host's
device driver for interactive work and honor host restrictions on suite execution.
Serialize suite runs and interactive work sharing a device, app data, or backend
fixtures. Outside a host-managed device runtime, use available device tooling
that exposes the required interaction and result.

Use platform tools for builds, logs, or other operations the device driver does
not cover. Outside that device runtime, choose the shortest available path that
can observe the required result: Xcode's MCP tools can build, run, interact with the Simulator,
and capture screenshots; `xcodebuild` and `xcrun simctl` cover build, install,
and launch; Simulator or computer-use tools can provide the remaining
interaction. Check the connected tool's capabilities before relying on it.
Xcode 27 adds Simulator interaction to its MCP server
([Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)); external agents connect through
[`xcrun mcpbridge`](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode).
Before using those MCP tools, open the target project or workspace in Xcode. If
Xcode's headless MCP server is enabled, `xcrun mcp-server open <project-or-workspace>`
can open it instead; check `xcrun mcp-server status` when discovery fails.
For physical-device checks, choose the device as Xcode's run destination or use
[`xcrun devicectl`](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference)
for available device operations. Interact through the device or connected
interface tooling; check its capabilities before relying on it.

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
that the runner uses it. Use the project's Xcode or `xcodebuild` workflow;
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
Verify's main procedure. Retain the runner's exit status and result bundle,
including screenshots, attachments, logs, and every attempt needed for the verdict.

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

Record the command and toolchain, scheme/test plan, build and target identity,
fixture state, selected tests, per-assertion outcomes, and artifact locations.
Capture the workflow states needed to support visual claims. Use
[interface review](interface-review.md) for relevant visual, Dynamic Type,
keyboard, focus, touch-target, and assistive-technology checks. Exercise VoiceOver
usability and hardware-dependent behavior through suitable checks on the required
target; accessibility identifiers supply selectors for automation.

For reusable setup, follow [project maps](project-map.md): link executable tests
to workflow assertions and document the method for exercising remaining checks.
Keep run evidence separate from the map.
