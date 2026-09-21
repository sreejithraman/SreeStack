# Discovery and system surfaces

## App Shortcuts, Siri, and Spotlight actions

Use the app's single `AppShortcutsProvider` to promote the small set of actions
people should find without first building a shortcut. Give each shortcut a
concrete title, symbol, and a few short phrases grounded in the product
vocabulary. Include the application-name token where the supported API requires
it. Localize metadata and refresh shortcut parameters when their display values
change.

A complete parameter summary improves editing in Shortcuts. On supported macOS
versions, an intent whose summary includes all required parameters can also run
as an action from Spotlight. Test discovery separately from execution because
build-time metadata extraction can succeed while runtime dependencies or routing
still fail.

Apple references:

- [AppShortcutsProvider](https://developer.apple.com/documentation/appintents/appshortcutsprovider)
- [Get to know App Intents](https://developer.apple.com/videos/play/wwdc2025/244/)

## Content in Spotlight

Use app entities for content the system should understand. For searchable
content, conform the system-facing model to `IndexedEntity`, mark useful entity
properties, donate current entities to the appropriate Spotlight index, and
provide an open intent that routes a selected entity into the app. Keep semantic
search, privacy, account scope, and deletion behavior aligned with the app's own
search and access rules.

Apple reference: [Spotlight integration](https://developer.apple.com/documentation/appintents/spotlight).

## Apple Intelligence and Siri

When the task includes Apple Intelligence or richer Siri integration, use an
available app schema for each well-known action, entity, and fixed choice. Make
relevant entities searchable, choose transferable representations for content
that can move between apps, associate visible content with its entity, and
donate actions initiated in the app when those signals improve discovery.

Treat onscreen context, cross-app transfer, and Visual Intelligence as separate
branches with their own SDK requirements. Load the current Apple documentation
for the requested branch before selecting protocols or annotations; these APIs
are version sensitive.

When a schema macro is newer than the minimum OS, availability-gate the schema
declaration and retain an older compatible intent surface if the action must
remain usable there. Both paths call the same domain service. Keep shipped
intent and entity identities compatible. If separate declarations are required,
use the supported SDK's discovery and deprecation mechanisms so a fresh install
exposes one public action per OS version while saved legacy shortcuts remain
runnable after an upgrade. Build and exercise both the oldest supported OS and
a schema-capable OS.

Apple references:

- [Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [Donations and discovery](https://developer.apple.com/documentation/appintents/donations-and-discovery)

## Widgets, controls, and hardware entry points

Reuse the same verbs, entities, and services when an action also belongs in a
widget, control, Live Activity, Action button, or other hardware entry point.
Choose the surface-specific intent protocol and result shape required by the
supported SDK. Keep configuration entities compact and make dependent pickers
respond to the earlier selections.

Each surface has its own time, UI, process, and entitlement constraints. Inspect
that surface's current Apple documentation before implementation; sharing the
domain operation does not make every intent type interchangeable.

## Shared declarations and targets

App Intents metadata is extracted per build target. Keep declarations in the
target that owns them, and confirm membership for every app or extension that
uses them. When declarations live in a framework, static library, or Swift
package, define an `AppIntentsPackage` there and include it from each consuming
target as required by the supported SDK.

Use an App Intents extension when an action must remain available without the
main app process. Choose placement from execution and reuse requirements rather
than creating a dedicated target by default. When the installed SDK provides
execution-target selection, check its availability before using it.

Titles and other build-time metadata must use values the extractor can evaluate;
prefer literal localized resources over computed values. Keep shared entity and
intent types independent of app-only UI state.

Apple reference: [AppIntentsPackage](https://developer.apple.com/documentation/appintents/appintentspackage).
