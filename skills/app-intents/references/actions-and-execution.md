# Actions and execution

## Shape the action

Start with a verb a person recognizes from the product: create a task, open a
project, start a workout, or mark an item complete. Prefer a few high-value
actions that work outside the app over a catalog of screens or implementation
operations.

Use an `AppIntent` specialization or an App Intent domain schema when it already
expresses the action. Schemas are the system contract for well-known actions and
content used by Apple Intelligence, Siri, and other clients. A semantic type
such as `OpenIntent` likewise communicates more than a generic custom action.
Check availability against the project's SDK and deployment targets before
choosing one.

Give the intent a constant, localized title and a concise description. Add a
parameter summary that reads as a natural action and includes every required
parameter. Keep parameters sufficient for the action while leaving product
state and business rules in the domain layer. Return values when they can feed a
later shortcut action; return dialog or a snippet when the invoking surface
needs a visible or spoken result.

Apple references:

- [App intents](https://developer.apple.com/documentation/appintents/app-intents)
- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Creating your first app intent](https://developer.apple.com/documentation/appintents/creating-your-first-app-intent)

## Choose the execution mode

Choose execution from the action's actual needs:

- Run in the background when services can complete the work without app UI.
- Enter the foreground immediately when the action is inherently visual.
- Start in the background and continue in the foreground when input or state
  determines whether UI is needed.

On SDKs that provide `supportedModes`, use it with `systemContext` and the
foreground-continuation APIs. Treat `openAppWhenRun` as a compatibility API: it
is deprecated in current SDK documentation. Keep older syntax only when the
project's supported toolchain requires it.

When foreground work navigates the app, hand off one typed route or payload to
the scene's existing navigation owner. Make repeated delivery safe and preserve
multiwindow behavior; avoid a global side channel that assumes one active scene.

For an open action in a scene-based or multiwindow app, check whether the
supported SDK's `TargetContentProvidingIntent` fits the navigation flow. UIKit
apps can use the more specific `UISceneAppIntent` and its scene callbacks. Route
the resolved target into the scene the system selects, then verify both reusing
an existing window and creating or selecting another window as the product
requires.

Apple references:

- [supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [TargetContentProvidingIntent](https://developer.apple.com/documentation/appintents/targetcontentprovidingintent)
- [UISceneAppIntent](https://developer.apple.com/documentation/appintents/uisceneappintent)

## Preserve authorization and intent

Set the intent's authentication policy to match the sensitivity of the action.
Check app-level authorization and account state inside the same domain service
used by the UI. Ask for confirmation before destructive, costly, public, or
otherwise consequential work when the invoking surface does not already make
the consequence clear.

Do not rely on the default authentication policy for sensitive work: current
Apple documentation says the default permits execution while the device is
locked. Choose the policy deliberately, then enforce account and object-level
authorization in the domain service.

Use system requests for missing values, disambiguation, and confirmation so the
flow works in voice and visual clients. Write dialogs for the decision at hand;
avoid instructions that assume a particular surface.

## Keep execution testable

Let `perform()` translate resolved parameters into one domain operation and
translate its outcome into an intent result. Register required services early
through `AppDependencyManager`; inject dependencies into intents and queries
instead of reaching through UI singletons. Dependencies and values crossing
execution boundaries must satisfy the SDK's concurrency requirements.

Return success only after the operation completes. Map expected failures to
localized, actionable intent errors; a success-shaped result with an error
dialog breaks automation because clients may continue the workflow.

For tests, create a standalone dependency manager or inject test services using
the facilities available in the supported SDK. Cover domain behavior at the
service boundary, then add focused checks for parameter translation, execution
mode, result, and error mapping.

Apple references:

- [AppDependency](https://developer.apple.com/documentation/appintents/appdependency)
- [AppDependencyManager](https://developer.apple.com/documentation/appintents/appdependencymanager)
