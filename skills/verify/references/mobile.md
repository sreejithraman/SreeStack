# Mobile verification

Use this reference for iOS and Android app workflows. For websites in mobile
browsers, use [web](web.md). Choose the target and
interaction method from the required assertions. Use interactive driving for
exploration, reproduction, and interface inspection; use project suites for
repeatable regression checks. Combine them when the selected coverage needs both.
Verify's main procedure owns coverage, state, verdicts, and cleanup for either path.

## Target and tooling

Preserve a requested platform, OS, and Simulator, emulator, or physical-device
target. Otherwise use a Simulator or emulator when it can exercise the selected
workflow; choose suitable hardware for device-dependent assertions. Record the
app/build revision, bundle or package identifier, target ID, model, and OS version.
For Apple build and device setup, read [iOS](ios.md). For Android, discover the
project's build variant, APK/install command, and required SDK/device setup.
Platform CLIs can build, install, launch, and collect logs.

For interactive Simulator or Android Emulator checks in T3 Code, use
`device_list`, then `device_open` so the user can watch the selected device.
Drive it with the exact `agent-device` launcher, host configuration, and session
flags returned by `device_open`, keeping those flags on every command. Prefer
current snapshot refs and use `device_screenshot` for visual inspection.
Follow the live host device contract and report an unavailable platform.
See the [T3 device contract](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/toolkits/device/handlers.ts#L28).

Run an existing repository regression suite as a project test operation, separate
from interactive driving. Honor any host restrictions on suite execution;
Maestro Studio or MCP does not replace the host's interactive driver. Serialize
suite runs and interactive work sharing a device, app data, or backend fixtures.
Outside a host-managed device runtime, use available device tooling that exposes
the required interaction and result.

## Choose a regression harness

Reuse an established project harness, including native UI tests. For new
repeatable mobile workflow automation, prefer Maestro when its target support
and observable controls fit. A one-off check can stay interactive; ordinary
verification does not require introducing a suite. Add or change executable
tests when the active task includes implementation, harness repair, or reusable
verification setup. Keep project flows and CI configuration in the product repo.

Maestro drives public UI interactions through YAML flows. Its supported mobile
targets are:

| Target | Maestro support |
| --- | --- |
| iOS Simulator | Supported; use a Simulator build. |
| Physical iPhone/iPad | Unsupported; use suitable native/device tooling. |
| Android Emulator | Supported; install the intended app first. |
| Physical Android device | Supported through ADB; requires device debugging access. |

Sources: [iOS support](https://docs.maestro.dev/get-started/supported-platform/ios/uikit),
[Android support](https://docs.maestro.dev/get-started/supported-platform/android),
and [flow model](https://docs.maestro.dev/maestro-flows).
Simulator or emulator results establish only the assertions exercised there.
Keep hardware-dependent assertions blocked when the required device is unavailable.

## Prepare and run Maestro

Discover the project's installed/pinned Maestro version, flow paths, wrapper
command, and CI configuration. Check `maestro --version` and relevant `--help`
against the [CLI reference](https://docs.maestro.dev/maestro-cli/maestro-cli-commands-and-options)
before relying on version-dependent options. A skill link does not install Maestro.
If it is unavailable, use another suitable method for the selected assertions or
report the exact suite blocker; do not infer a product failure from a missing CLI.

Identify the installed build on the explicit test target before running. Use
the project's wrapper or Maestro's global `--device` option to select it; check
that the wrapper forwards the selection. Prepare fixtures, permissions, locale,
and authentication required by the selected flows. Inspect launch/reset commands
and hooks before execution: clearing app data or reinstalling must fit the run's
state assumptions and disposable target. Keep credentials in the approved runtime
delivery path described by [authenticated verification](authenticated-verification.md).

Connect selected flow checks to required workflow assertions before execution.
Inspect tags, conditions, subflows, optional commands, and retry configuration;
confirm required checks actually execute and fail the run on a mismatch. Use the
project's command to run the selected scope, retaining its exit status, reports,
and artifacts outside disposable state. Account for native tests or interactive
checks needed for assertions outside that scope.

When establishing a new harness, prove a representative flow against the actual
build and target. In a disposable copy, introduce a known assertion mismatch and
confirm the run fails with useful retained evidence. Keep the real assertion and
its observed product verdict separate from this check of failure detection.

## Write maintainable flows

- Pair meaningful actions with explicit outcome assertions. A successful tap,
  launch, or spinner disappearance alone does not prove a save completed.
  Persistence checks need Verify's fresh read of durable state.
- Prefer stable IDs and meaningful labels to coordinates. Maestro maps IDs to
  iOS accessibility identifiers and Android resource IDs; text and ID selectors
  use regex, so account for metacharacters in literal fixture values. Check the
  rendered hierarchy and framework-specific exposure when controls cannot be
  found. See [selectors](https://docs.maestro.dev/reference/selectors/core-selectors).
- Use `assertVisible` or `assertNotVisible` for normal state waits, and
  `extendedWaitUntil` with a justified deadline for longer operations. Animation
  settling establishes UI stability, not backend completion. See
  [wait strategies](https://docs.maestro.dev/maestro-flows/flow-control-and-logic/wait-commands).
- Keep fixtures isolated and repeatable. Each standalone flow establishes its
  starting state rather than depending on an earlier flow's leftovers. Reuse
  coherent subflows without hiding required assertions or cleanup.
- Preserve failed attempts and bound retries according to Verify's procedure.
  Polling for a state is different from repeating a state-changing action;
  automatic action retries can duplicate external effects.

Use deterministic assertions for required regression gates. Maestro's experimental
[`assertWithAI`](https://docs.maestro.dev/reference/commands-available/assertwithai)
uploads screenshots and defaults to optional/non-blocking. If an authorized run
uses it, inspect the evidence and configure required failure behavior explicitly;
its default cannot establish a required assertion passed.

## Evidence and remaining checks

Record the command, CLI version, build/target identity, fixture state, selected
flows, and per-assertion outcomes. Maestro supports JUnit and HTML reports through
`--format` and `--output`; report paths are separate from the test artifact output
directory. Check installed-version options and inspect the files actually
produced. Normal passing runs do not automatically capture every step; request
screenshots at states needed for visual claims. Retain failure evidence and
earlier failed attempts alongside a later successful run. See
[reports and artifacts](https://docs.maestro.dev/maestro-flows/workspace-management/test-reports-and-artifacts).

[`assertScreenshot`](https://docs.maestro.dev/reference/commands-available/assertscreenshot)
can compare selected states with reviewed baselines on controlled targets.
Baseline approval requires judging the intended appearance; a comparison alone
does not establish layout quality. Use [interface review](interface-review.md)
for the relevant visual, Dynamic Type/font scaling, keyboard, focus, touch-target,
and assistive-technology checks. Accessibility selectors do not prove VoiceOver
or TalkBack usability. Keep native logic/concurrency tests and hardware checks
where those supply the required evidence.

For reusable setup, follow [project maps](project-map.md): link executable flow
files and map their checks to workflow assertions. Document uncovered assertions
and the method for exercising them. Keep run evidence separate from the map.
