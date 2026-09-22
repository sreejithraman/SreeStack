# Apple runtime diagnosis

Use this branch for local iOS, iPadOS, visionOS, tvOS, watchOS, or macOS
runtime behavior, crashes, and hangs. Keep the parent skill's feedback loop,
minimal repro, and ranked hypotheses as the controlling workflow.

## Choose and record the target

Record the scheme, configuration, commit, app version/build, destination,
OS version, arguments, environment, and install state. A result without this
identity is hard to reproduce or compare.

Start with Simulator when it reproduces ordinary app logic or UI behavior and
gives a tighter loop. Use relevant hardware for device-only behavior,
hardware-backed services, release-only symptoms, thermal or memory pressure,
and performance conclusions. Simulator does not reproduce every device feature
or its performance characteristics. See Apple's guidance on
[running on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices).

Prefer the project's documented build and run path. When a command-line
Simulator loop would be tighter, inspect the active toolchain before composing
commands:

```bash
xcodebuild -version
xcrun simctl help
xcrun simctl list devices available
xcrun simctl help launch
```

Treat the locally reported options as the source of truth. Use the exact bundle
identifier and artifact produced by the selected scheme. Capture launch output
only when it distinguishes a hypothesis.

Done when one recorded target and build reproduce the exact symptom with a
bounded pass/fail signal.

## Capture the smallest useful evidence

For interactive diagnosis, run under Xcode so breakpoints, the debug area, and
view inspection are available. Prefer a breakpoint or a narrow `Logger`
category over broad logging. Record the triggering action and timestamp, then
retain only the log window that crosses the failure.

For a local crash, use the debugger stack or collect the local crash report
with its matching executable and dSYM. For a distributed build, retain the
matching archive or downloaded distribution symbols. Check binary and dSYM
UUIDs with `dwarfdump --uuid`; draw source-level conclusions only from
symbolicated app frames. A jetsam report is evidence of memory-pressure
termination and does not provide the executing-thread stack of a normal crash.
Apple explains the artifact types in
[Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs)
and the symbolication requirements in
[Adding identifiable symbol names to a crash report](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report).

For a suspected hang, preserve both the input event and the delayed response.
Profile enough of the interval to distinguish a busy main thread from one
blocked on a resource. Use the Hangs instrument or the applicable device report
described in Apple's
[responsiveness guidance](https://developer.apple.com/documentation/xcode/improving-app-responsiveness).

Use a broad Simulator diagnostic bundle only when focused evidence is
insufficient. Inspect `xcrun simctl help diagnose` first and omit app data
containers unless they are required for the hypothesis.

Done when each retained artifact answers a named hypothesis and its app, build,
target, and time window are known.

## Protect diagnostic data

Logs, screenshots, recordings, crash reports, memory graphs, diagnostic
bundles, and app containers may contain tokens, paths, request bodies, account
data, or private user content. Minimize the capture, keep it in a task-specific
location, redact it before sharing, and follow the project's retention policy.
Use unified logging privacy controls for dynamic values; see
[`OSLogPrivacy`](https://developer.apple.com/documentation/os/oslogprivacy).

For TestFlight or App Store crash intake, release artifacts, and field
diagnostics, use `app-store-connect`. Return here once there is a local repro or
a concrete hypothesis to test.
