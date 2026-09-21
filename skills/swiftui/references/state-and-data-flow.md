# State and Data Flow

## Assign ownership

Give every mutable value one source of truth at the lowest common ancestor that
needs to own it.

- Use an immutable property for input the view only reads.
- Use private `@State` for transient state the view creates and owns. Its lifetime
  follows the view's identity, so it is not durable storage.
- Pass `@Binding` only when a child must mutate state owned elsewhere. Pass a value
  and an action when the child only reports an event.
- On supported deployment targets, use `@Observable` for reference models and
  keep a view-owned instance in `@State`. Use `@Bindable` when a view needs bindings
  to that model's mutable properties.
- Put a model or dependency in the environment when descendants share it as part
  of their surrounding context. Pass feature-local requirements explicitly.

These choices follow Apple's [model data](https://developer.apple.com/documentation/swiftui/model-data)
and [UI state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state/)
guidance.

Keep older `ObservableObject`, `@StateObject`, and `@ObservedObject` code when the
deployment target or existing architecture requires it. Modernize Observation as
a coherent ownership change rather than wrapper-by-wrapper substitution.

## Keep one truth

Copy an input into local state only when the local value is intentionally an
independent draft or snapshot. Define when it is created, committed, reset, and
reconciled with upstream changes. Derived display values should remain derived.

Place asynchronous loading and mutations with the feature owner. Start work from
a lifecycle-aware hook such as `task`, cancel or supersede stale requests, and
publish UI-observed mutations on the appropriate actor. Model loading, empty,
content, and failure as distinct states when they lead to distinct interfaces.

## Narrow dependencies

Read observable properties near the view that renders them. Passing a large model
through a broad subtree can make unrelated views depend on it. Extract a semantic
child view when doing so gives that child a smaller input surface and a stable
identity; avoid extraction performed only to shorten a file.
