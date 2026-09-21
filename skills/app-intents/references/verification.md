# Verification

## Build and metadata

1. Build every app, extension, widget, control, framework, or package target that
   declares or consumes the changed types. Treat metadata extraction warnings
   and concurrency diagnostics as failures to investigate.
2. Confirm deployment availability, target membership, package inclusion,
   localization, and required entitlements. Install or relaunch a fresh build
   after metadata changes so cached system discovery does not mask the result.
3. If an action is absent, first reduce the problem to metadata discovery: use a
   constant title, confirm the type is discoverable, confirm its target is in the
   installed product, and verify any `AppIntentsPackage` chain.

When the supported toolchain includes App Intents Testing, use it for meaningful
out-of-process coverage of definitions, queries, or execution. Treat it as an
additional integration layer while the API is beta; keep domain tests and real
surface checks.

## Exercise each requested surface

For each surface named in the task, verify the user-visible path rather than only
calling `perform()` in a test:

- find and run promoted actions in Shortcuts, Siri, or Spotlight;
- edit every required parameter and inspect its summary;
- search, disambiguate, and reopen representative entities;
- configure and activate the widget, control, or hardware entry point; and
- verify the intended window, scene, and destination for foreground handoff.

Cover one normal case plus the relevant signed-out, locked-device,
authorization-denied, missing-entity, cancellation, and service-failure paths.
Confirm consequential actions request confirmation at the intended point and do
not partially mutate data when the flow stops.

## Check execution behavior

Run background actions while the app is not active. Run foreground and deferred
actions from the external surface that triggers them. Check that dependencies
are registered before execution, UI state changes on its owning actor, repeated
invocation is safe, and multiwindow routing reaches the correct scene.

When an intent returns a value, chain it into another shortcut action. When it
returns dialog or a snippet, inspect the result in both visual and voice-oriented
contexts that matter to the task. Confirm errors are actionable and do not expose
private implementation details.

Record the targets built, surfaces exercised, OS versions or simulator/device
used, successful paths, and any system surface that could not be tested.

For a shipped intent or entity migration, install the previous app version,
create representative shortcuts and donations, upgrade, and run them again.
Exercise supported localizations because titles, summaries, displays, phrases,
dialogs, and errors appear as system UI.

When a current schema or system-surface API is availability gated, repeat the
relevant discovery and execution checks on the oldest supported OS and on an OS
that takes the new path. On the newer OS, check a fresh install for duplicate
actions and an upgrade for execution of a saved legacy shortcut.
