# iOS Simulator preview adapter: official interfaces and safe policy

Research date: 2026-07-20

This note records the Apple-supported interfaces relevant to an iOS preview
adapter and separates them from `showroom` policy. The local first-party
command reference was inspected with Xcode 26.6 (build 17F113). No Simulator
device was created, cloned, booted, erased, modified, or deleted during this
research.

## Conclusions

- Apple supports the complete mechanical path needed for a preview:
  discover a project or workspace and scheme with `xcodebuild`, choose a
  Simulator destination, build an app, create or clone a simulated device,
  boot it, install and launch the app, open a URL, and capture a screenshot or
  recording. [Apple describes `xcodebuild` and `simctl` as Xcode-provided
  command-line tools][apple-cli]; their installed help documents the commands
  listed below. [CLI-1] [CLI-2]
- A scheme and run destination are both meaningful build inputs. A scheme
  selects targets, configuration, and launch environment; the destination
  selects simulated versus physical hardware. [Apple: Building and running an
  app][apple-build-run] [Apple: Customizing build schemes][apple-schemes]
- Build success is not proof of an interactive or visual change. The adapter
  should not claim verification until it has installed and launched the app and
  captured evidence after any configured navigation. This is a product policy,
  not an Apple API guarantee. Apple likewise treats build and run as separate
  operations and presents Simulator as an interactive testing surface.
  [Apple: Running on simulated or physical devices][apple-run-destinations]
- Simulator is useful for quick iteration but does not reproduce all device
  features or physical-device performance. A preview report must preserve this
  limitation. [Apple: Running on simulated or physical
  devices][apple-run-destinations]
- Ownership is not built into `simctl`. “Manager-owned clone,” lease, reuse,
  worktree identity, and exact-resource cleanup are `showroom` concepts. The
  registry must therefore be the authority for destructive actions.

## Source classification

Statements labeled **Official interface** come directly from current Apple web
documentation or the help shipped in Xcode. Statements labeled
**Implementation inference** are recommendations derived from those interfaces;
Apple does not promise the policy or composition itself.

The installed CLI sources used here are:

- **CLI-1:** `xcodebuild -version` and `xcodebuild -help`, Xcode 26.6
  (17F113), inspected 2026-07-20.
- **CLI-2:** `xcrun simctl help` and help for `list`, `create`, `clone`,
  `delete`, `boot`, `shutdown`, `install`, `uninstall`, `appinfo`, `listapps`,
  `get_app_container`, `install_app_data`, `launch`, `terminate`, `openurl`,
  and `io`, Xcode 26.6, inspected 2026-07-20.
- **CLI-3:** `xcrun xcresulttool help`, `help get`, `help get build-results`,
  `help get test-results`, and `help export`, xcresulttool 24757, inspected
  2026-07-20.

Apple's command-line tool reference explicitly directs developers to the
installed manual/help for these Xcode-shipped tools. [Apple: Xcode command-line
tool reference][apple-cli]

## Discovery

### Container, scheme, target, and destination

**Official interface.** `xcodebuild` accepts either `-project <path>` or
`-workspace <path>`. `xcodebuild -list` lists project targets and configurations
or workspace schemes, and `-json` requests structured output. With a scheme,
`-showdestinations` displays destinations available to that scheme.
`-showBuildSettings -json` displays resolved build settings. [CLI-1]

**Official interface.** A build scheme identifies targets to build, build
configuration, and executable environment. Xcode creates schemes for most
targets, and current Xcode shares schemes by default. [Apple: Customizing build
schemes][apple-schemes] Apple's scheme help says the Shared checkbox makes a
scheme available to other team members. [Apple: Add, delete, rename, and share
schemes][apple-share-scheme]

**Implementation inference.** Detection should:

1. Search the selected working directory for `.xcworkspace` and `.xcodeproj`
   containers while excluding build output and dependency checkouts.
2. Use a manifest override when more than one plausible container exists.
   Prefer a single workspace over its contained project only when the choice is
   unambiguous; workspaces often carry dependency integration, but Apple does
   not define this as a universal selection rule.
3. Run `xcodebuild -list -json` against the chosen container.
4. Prefer a scheme checked into
   `xcshareddata/xcschemes/<scheme>.xcscheme`. Treat filesystem inspection as a
   current Xcode project-format convention, not a stable API. If several app
   schemes remain, require a manifest selection rather than guessing.
5. Run `xcodebuild -showdestinations` for the selected scheme and choose an iOS
   Simulator destination compatible with the requested device and OS.
6. Run `xcodebuild -showBuildSettings -json` with that scheme and destination.
   Resolve the app product from settings such as `TARGET_BUILD_DIR`,
   `WRAPPER_NAME`, and `PRODUCT_BUNDLE_IDENTIFIER`; if multiple `.app` products
   are present, require a target/product override.

**Official interface.** `simctl list` can list devices, device types, runtimes,
or pairs; it supports JSON, an `available` filter, and a search term. `simctl
create` requires a name and device-type identifier, accepts an optional runtime
identifier, and otherwise chooses the newest compatible runtime. [CLI-2]

**Implementation inference.** Always select an explicit compatible runtime.
Implicitly taking “newest” makes an idempotent preview susceptible to changing
after an Xcode/platform update. Record the Xcode build, runtime identifier,
device-type identifier, and deployment-target setting with the preview.

### Signing policy

**Official interface.** `xcodebuild -showBuildSettings` exposes resolved project
settings, including signing settings. Apple's build-settings reference defines
`CODE_SIGN_STYLE` as the method for acquiring signing assets and warns that a
missing or invalid signing identity causes a build error. [Apple: Build settings
reference][apple-build-settings] [CLI-1]

**Official interface.** `-allowProvisioningUpdates` authorizes `xcodebuild` to
communicate with the Apple Developer website. For automatically signed targets
it may create or update profiles, App IDs, and certificates; for manually signed
targets it may download profiles. `-allowProvisioningDeviceRegistration`, when
combined with it, may register a destination device. [CLI-1]

**Implementation inference.** The Simulator adapter should preserve the
project's resolved signing policy and must not pass either provisioning flag by
default. It should never write a team, identity, profile, or other personal
signing override into the project or manifest. If a Simulator build cannot
proceed without account or signing changes, report a blocker and require an
explicitly authorized project-specific action.

## Build and result reporting

**Official interface.** `xcodebuild` accepts a scheme, a destination specifier,
a dedicated `-derivedDataPath`, and a `-resultBundlePath` where it places a
bundle describing what occurred. [CLI-1] Apple documents destination specifiers
as comma-separated key/value pairs and includes an `id` key for iOS
destinations. [Apple Technical Note TN2339][apple-tn2339]

**Official interface.** Current `xcresulttool get build-results --path <path>`
returns a high-level description of a build action, its run destination,
metadata, warnings, and issues. It can emit its JSON schema. `xcresulttool get
test-results` exposes test summaries and details; `export attachments` exports
attachments. [CLI-3]

**Implementation inference.** Give every preview/worktree its own Derived Data
directory and every build attempt a fresh result-bundle path in machine state.
This avoids cross-worktree product collisions and makes failure recovery
auditable. A representative build command is:

```sh
xcodebuild \
  -workspace "$workspace" \
  -scheme "$scheme" \
  -destination "platform=iOS Simulator,id=$simulator_udid" \
  -derivedDataPath "$derived_data" \
  -resultBundlePath "$result_bundle" \
  build
```

Use `-project` instead of `-workspace` when the selected container is a project.
Do not inject `-allowProvisioningUpdates`. Persist the process exit status,
result-bundle path, and a parsed `xcresulttool get build-results` summary.

**Implementation inference.** Derive the installable `.app` and bundle
identifier from resolved build settings, then confirm that the expected paths
exist. Do not scan all of Derived Data and choose the first `.app`; schemes can
build multiple products and test runners.

## Manager-owned Simulator lifecycle

### Supported controls

**Official interface.** `simctl create <name> <device type id> [<runtime id>]`
creates a simulated device. `simctl clone <device> <new name> [<destination
device set>]` clones a device. `simctl boot <device>` boots a device, `shutdown
<device>` shuts down one device or all devices, and `delete` accepts one or more
devices as well as the broad selectors `unavailable` and `all`. The top-level
tool also accepts `--set <path>` to select a device set. [CLI-2]

**Official interface.** Wherever `simctl` accepts a device argument, a UDID or
the special value `booted` is allowed. If multiple devices are booted,
`booted` chooses one of them. [CLI-2]

**Implementation inference.** Never use `booted` in the adapter. Concurrent
worktrees make it ambiguous by definition. Every operation must use the exact
registered UDID.

**Implementation inference.** A safe first implementation should:

1. Create a manager-owned template for an explicit device type/runtime, or
   select only a previously registered manager template.
2. Clone that manager-owned template for each stable project/worktree/device
   configuration. Give the clone a human-readable `showroom` prefix, but use
   its returned UDID—not its name—as identity.
3. Record `manager_owned: true`, the clone UDID, source template UDID, device
   type, runtime, Xcode build, project/worktree identity, and creation time
   before any subsequent mutation.
4. Reuse a healthy matching clone on idempotent `start`; allocate a distinct
   clone and Derived Data directory for another worktree.
5. Reconcile boot state from `simctl list devices --json` before requesting a
   boot. Treat JSON field parsing as versioned CLI integration and cover it with
   fixtures for supported Xcode versions.

**Implementation inference.** `simctl --set` makes a dedicated manager device
set technically possible, but Apple does not document how a custom device set
interacts with the current graphical Device Hub. Do not make custom device sets
the default interactive design until a real UI flow is manually verified.
Using the default set with exact registered manager UDIDs is supportable if
cleanup refuses every unregistered device.

### Ownership and cleanup invariant

The deletion gate should be conjunctive:

```text
registered exact UDID
AND manager_owned is true
AND registry project/worktree identity matches the requested preview
AND observed device type/runtime are compatible with the registry record
```

**Implementation inference.** If any check fails, leave the device untouched
and report drift. Names and prefixes are diagnostics only, never deletion
authority. `cleanup`, including dry-run, must never call `simctl delete all`,
`simctl delete unavailable`, `simctl shutdown all`, or `simctl erase`; those
broad commands can affect normal developer devices. On stop or expiry, target
only the exact bundle identifier and manager UDID, then the exact clone UDID:

```sh
xcrun simctl terminate "$simulator_udid" "$bundle_id"
xcrun simctl shutdown "$simulator_udid"
xcrun simctl delete "$simulator_udid"
```

**Official interface.** `terminate`, `shutdown`, and `delete` are individually
supported operations. [CLI-2] **Implementation inference.** Their error cases
must be normalized for idempotency: “already stopped,” “already shut down,” or
“already absent” should converge to stopped without widening the target.

## Install, launch, fixtures, and navigation

### Install and launch

**Official interface.** `simctl install <device> <path>` installs an app.
`appinfo <device> <bundle identifier>` reports information for an installed app,
and `listapps <device>` lists installed apps. `launch` accepts an exact device,
bundle identifier, and trailing application arguments. It supports
`--terminate-running-process`, stdout/stderr redirection, and console modes.
Environment variables prefixed with `SIMCTL_CHILD_` are passed into the child
environment. [CLI-2]

**Implementation inference.** After the device is observed booted, install the
resolved app path, confirm the bundle with `appinfo`, and launch by exact UDID:

```sh
xcrun simctl install "$simulator_udid" "$app_path"
xcrun simctl appinfo "$simulator_udid" "$bundle_id"
xcrun simctl launch \
  --terminate-running-process \
  --stdout="$stdout_log" \
  --stderr="$stderr_log" \
  "$simulator_udid" "$bundle_id" "${launch_args[@]}"
```

Record the launch command's exit status and returned PID. Keep environment
values out of reports and redact configured secrets from logs. Scheme Run
arguments are not automatically applied by a standalone `simctl launch`; the
manifest must explicitly supply any arguments/fixtures that the preview needs.

### Deep links and fixtures

**Official interface.** `simctl openurl <device> <URL>` asks the simulated
device to open a URL. [CLI-2] Apple documents that a registered custom URL can
launch an app in a specified context and recommends universal links when an
HTTPS association is available. Apple also warns that custom URL input must be
validated. [Apple: Defining a custom URL scheme][apple-custom-url]

**Implementation inference.** Apply a configured deep link only after install
and launch, record its redacted form, and fail navigation verification if
`openurl` fails. Never persist authorization codes, reset tokens, or other
credentials embedded in a URL.

**Official interface.** `simctl install_app_data` replaces an app's current
container contents with an `.xcappdata` package and terminates the app if it is
running. [CLI-2] Xcode schemes can also configure App Data, location, StoreKit,
launch arguments, and other run-time inputs. [Apple: Customizing build
schemes][apple-schemes]

**Implementation inference.** Install configured app-data fixtures before
launch and only on a registered manager clone. Because the command replaces
container state, it must never target an ordinary developer Simulator.

### UI-test navigation

**Official interface.** `xcodebuild test -scheme <scheme>` runs configured
tests, and `-only-testing` can select a test identifier. Command-line test runs
produce an Xcode test-results bundle containing results and logs. [Apple:
Running tests and interpreting results][apple-test-results] [CLI-1]

**Official interface.** `XCUIApplication` can launch, monitor, and terminate an
app, wait for an expected state, pass launch arguments/environment, and open a
URL. Its synchronous `launch()` returns after the app is ready to handle events
or records a test failure. [Apple: XCUIApplication][apple-xcuiapp] [Apple:
XCUIApplication launch][apple-xcui-launch]

**Implementation inference.** When a project supplies a preview-navigation UI
test, run it against the exact destination UDID with a result bundle and retain
the selected test identifier. Prefer a small, deterministic navigation test
over encoding app-specific UI logic in `showroom`. Treat its assertions and
`XCUIApplication` state as stronger interactive verification than a bare
`simctl launch`.

## Screenshots and recordings

**Official interface.** `simctl io <device> screenshot <file-or-url>` captures a
screenshot; PNG is the default and other listed image formats are available.
`simctl io <device> recordVideo <file-or-url>` records a QuickTime movie using
HEVC by default or H.264 when selected. `recordVideo` writes “Recording started”
to stderr after the first processed frame; sending SIGINT stops recording, and
the process exits after in-flight frames are finalized. [CLI-2]

**Official interface.** Device Hub also captures full-resolution Simulator
screenshots and recordings. Apple presents these artifacts as useful for team
review, bug/design explanation, accessibility, and localization review.
[Apple: Capturing screenshots and videos][apple-capture]

**Implementation inference.** Capture at least one screenshot after successful
launch and configured navigation for any visual or interactive change:

```sh
xcrun simctl io "$simulator_udid" screenshot "$screenshot_path"
```

For a recording, supervise `simctl io ... recordVideo` as its own exact process,
wait for the documented started message, and stop it with SIGINT so the movie is
finalized. Do not infer success from file creation alone; require a zero exit,
nonempty artifact, and readable media metadata. Never use a broad process-name
kill.

**Official interface.** UI tests can capture screen/window screenshots as
`XCTAttachment`s, and setting attachment lifetime to keep-always retains them
after successful tests. [Apple: Adding test attachments][apple-attachments]

**Implementation inference.** If a project already has a preview-navigation UI
test, prefer its semantic assertions and retained screenshot attachments, then
optionally add a `simctl io` screenshot as a simple handoff artifact.

## Verification model

The adapter should report checks separately instead of collapsing them into a
premature Boolean:

| Check | Evidence | Claim allowed |
| --- | --- | --- |
| Discovery | selected container, shared scheme, target/product, destination | configuration resolved |
| Build | `xcodebuild` exit plus `.xcresult` build summary | build succeeded |
| Install | `simctl install` exit plus `appinfo` | app installed on exact clone |
| Launch | `simctl launch` exit, returned PID, captured logs | launch request succeeded |
| Navigation | successful `openurl`, fixture application, or configured UI test | configured state reached at the mechanism's confidence level |
| Visual evidence | readable screenshot/video captured after navigation | review artifact captured |
| UI assertion | passing UI test, `XCUIApplication` expected state, retained attachments | interactive behavior verified by the project test |

**Implementation inference.** A bare launch does not expose a stable,
documented general-purpose foreground-state assertion in the inspected
`simctl` interface. Without a UI test, say “launch succeeded and evidence was
captured,” not “app state was asserted.” A screenshot proves what was rendered
at capture time but does not by itself prove a workflow is interactive.

Preserve these evidence paths in the common handoff:

- build `.xcresult` and parsed build summary;
- app stdout/stderr logs;
- navigation/UI-test `.xcresult`, when used;
- screenshots and recordings;
- a redacted command transcript;
- device metadata: manager UDID, name, type, runtime, and Xcode build.

## Recommended adapter sequence

The following composes official commands with inferred lifecycle policy:

1. Detect a unique container, checked-in shared scheme, app product, deployment
   target, and signing posture; stop on ambiguity.
2. Reconcile a matching registered clone, or create/reuse a manager template
   and allocate one exact clone for this project/worktree/device tuple.
3. Select the exact UDID as the `xcodebuild` destination and build into
   preview-owned Derived Data with a fresh result bundle.
4. Parse build results and resolved product metadata. Do not continue on build
   failure.
5. Boot or reconcile the exact clone; wait until operations against that UDID
   are accepted.
6. Apply an optional app-data fixture, install the app, verify installation,
   and launch with explicit configured arguments/environment.
7. Apply a deep link or run a project-supplied UI navigation test.
8. Capture required screenshot/video evidence and validate the artifacts.
9. Report the exact device, app/build state, evidence, lease, limitations, and
   exact inspect/renew/pin/stop commands.
10. On stop/expiry, terminate and remove only exact registered resources.
    Preserve drifted or ambiguous resources for manual inspection.

## Open validation work and residual risks

- **Graphical custom device sets:** `simctl --set` and clone destination sets
  are documented in CLI help, but their integration with Xcode 26 Device Hub is
  not documented. Manually test before choosing a custom set over exact
  manager-owned devices in the default set.
- **Boot readiness:** the inspected Xcode 26.6 help does not list the historical
  `bootstatus` subcommand. Implement bounded reconciliation using supported
  list/install behavior and test it against the actual supported Xcode matrix;
  do not assume an undocumented readiness signal.
- **JSON compatibility:** `simctl list --json` is supported, but its schema is
  not published in the inspected help. Version fixtures and reject unknown
  shapes conservatively.
- **Clone semantics:** `simctl clone` is supported, but Apple does not state in
  help which runtime/device states are safe to clone or promise app/data
  equivalence. Prefer a shut-down, empty manager-owned template and verify the
  resulting clone.
- **Multiple products:** extensions, watch companions, test hosts, and schemes
  with several app products make automatic product selection unsafe. Require a
  manifest override when resolved settings do not identify one installable app.
- **Capabilities:** Simulator does not implement every hardware-backed feature.
  Report capability limitations and route physical-device-only behavior to a
  different review surface. [Apple: Running on simulated or physical
  devices][apple-run-destinations]
- **Manual verification:** no build/install/launch flow was exercised for this
  research because the shard was explicitly read-only. The implementation must
  manually verify one representative web-independent iOS app flow before the
  adapter is declared complete.

## Official sources

- [Xcode command-line tool reference][apple-cli]
- [Building and running an app][apple-build-run]
- [Running your app on simulated or physical devices][apple-run-destinations]
- [Customizing the build schemes for a project][apple-schemes]
- [Add, delete, rename, and share schemes][apple-share-scheme]
- [Technical Note TN2339: Building from the Command Line with Xcode
  FAQ][apple-tn2339]
- [Build settings reference][apple-build-settings]
- [Installing your app in many Simulator platforms and
  versions][apple-install-many]
- [Defining a custom URL scheme for your app][apple-custom-url]
- [Capturing screenshots and videos from devices][apple-capture]
- [Running tests and interpreting results][apple-test-results]
- [XCUIApplication][apple-xcuiapp]
- [XCUIApplication launch][apple-xcui-launch]
- [Adding attachments to tests, activities, and issues][apple-attachments]

[apple-cli]: https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference
[apple-build-run]: https://developer.apple.com/documentation/xcode/building-and-running-an-app
[apple-run-destinations]: https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices
[apple-schemes]: https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project
[apple-share-scheme]: https://help.apple.com/xcode/mac/current/en.lproj/dev5426ddfcf.html
[apple-tn2339]: https://developer.apple.com/library/archive/technotes/tn2339/_index.html
[apple-build-settings]: https://developer.apple.com/documentation/xcode/build-settings-reference
[apple-install-many]: https://developer.apple.com/documentation/xcode/installing-your-app-in-many-simulator-platforms-and-versions
[apple-custom-url]: https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app
[apple-capture]: https://developer.apple.com/documentation/xcode/capturing-screenshots-and-videos-from-devices
[apple-test-results]: https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results
[apple-xcuiapp]: https://developer.apple.com/documentation/xcuiautomation/xcuiapplication
[apple-xcui-launch]: https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/launch%28%29
[apple-attachments]: https://developer.apple.com/documentation/xctest/adding-attachments-to-tests-activities-and-issues
