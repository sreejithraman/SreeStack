# Entities and queries

## Choose the value model

Use the framework's common value types when they preserve the meaning. Use an
`AppEnum` for a small, fixed set of choices with localized display names. Use an
`AppEntity` for app data that the system must identify, display, retrieve, or
pass between actions.

An entity is a system-facing projection, not a persistence model. Give it:

- a stable identifier that resolves the same logical object over time;
- a clear type display representation;
- an instance display representation that distinguishes similar results; and
- only the properties needed by the intended system experiences.

Creating a separate entity projection is often the cleaner boundary when the
app model contains mutable state, private fields, framework-specific storage, or
values that are not safe to cross concurrency boundaries.

Apple references:

- [App entities](https://developer.apple.com/documentation/appintents/app-entities)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)

## Design the query around retrieval paths

Every query must restore entities from identifiers. Add other query capabilities
only for real selection paths:

- suggested entities for a short, useful initial picker;
- string search when people know a name;
- property queries when clients need structured filtering; and
- parameter dependencies when one choice genuinely constrains another.

Resolve identifiers in batches, preserve the requested identity, and use the
same store as the app. Bound broad suggestions and searches. Return useful
defaults only when the product has a predictable default; a surprising default
can execute an action against the wrong object.

Treat shipped intent and entity identities as compatibility contracts. Saved
shortcuts and donations can outlive an app update, so preserve resolution across
renames or provide the framework's migration path and test an upgrade from the
previous release.

Inject stores and services into queries just as you do for intents. Account for
signed-out, deleted, inaccessible, and stale entities. Surface empty results as
a valid state and operational failures as errors the invoking surface can
explain.

Apple reference: [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery).

## Make entities useful beyond selection

Return entities from intents when another action could consume them. Adopt
`IndexedEntity` only for content that should appear in Spotlight and related
system experiences. Supply an appropriate open action so selecting a search
result reaches the corresponding content in the app.

Keep indexes in sync with creation, updates, deletion, access changes, and
sign-out. When donating entities directly, support reindexing through an
`IndexedEntityQuery` where the SDK requires it.

Apple reference: [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight).
