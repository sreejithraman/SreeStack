---
name: app-intents
description: App Intents work on Apple platforms. Use when exposing app actions or content to Apple Intelligence, Siri, Shortcuts, Spotlight, widgets, controls, or hardware entry points; designing AppEntity queries; or diagnosing intent discovery and execution.
---

# App Intents

Expose a small, stable action layer that reflects what people want to do with
the app. Keep intents as adapters over existing domain services rather than a
second implementation of product behavior.

Use the project's supported Xcode, Swift, and OS versions as the API boundary.
App Intents changes between SDK releases, so confirm version-sensitive APIs in
the installed SDK or current Apple documentation before adopting them.

## Workflow

1. Inspect the relevant app and extension targets, deployment versions, existing
   intents, domain services, data stores, navigation, authentication, and
   entitlements. Identify which process can perform the action and which target
   must discover each declaration.
2. Describe the user action in one sentence. Choose the system surfaces where
   it is useful and decide whether it can finish in the background, needs the
   foreground immediately, or may continue there later. Read [Actions and
   execution](references/actions-and-execution.md) before implementing or
   changing an intent.
3. Model only the input and output the system needs. Use framework value types
   or an `AppEnum` for fixed choices. Read [Entities and
   queries](references/entities-and-queries.md) when app data must be selected,
   returned, searched, indexed, or shared across targets.
4. Add the smallest discovery surface that makes the action useful. Read
   [Discovery and system surfaces](references/discovery-and-system-surfaces.md)
   for App Shortcuts, Spotlight, widgets, controls, hardware entry points, and
   shared-package registration.
5. Build every target that declares or consumes the changed types. Then follow
   [Verification](references/verification.md) and exercise each requested system
   surface. Use `manual-verify` when hands-on interaction adds confidence.

The work is complete when each requested action is discoverable from its target
surface, resolves representative parameters, runs in its intended process and
foreground mode, reports a useful result or failure, and preserves the app's
authorization and domain rules.
