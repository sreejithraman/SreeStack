# SDK 27 Migration

Treat SDK migration as a source-compatibility task. Confirm the selected Xcode,
Swift language mode, deployment targets, and failing destination before changing
code. A symbol introduced by the SDK can still require runtime availability,
while a compiler transformation such as the `@State` macro follows the build
toolchain.

## Migrate `@State`

Xcode 27 expands `@State` as an attached macro. Apply the matching fix when this
causes a source error:

- When an initializer supplies initial state, omit an inline default, initialize
  ordinary stored properties first, and then assign the state property. An inline
  default wins when SwiftUI creates the state storage, so merely reordering the
  assignments can compile with the wrong initial value.
- Remove another property wrapper composed with `@State`. Both transformations
  can synthesize the same underscore-prefixed storage.
- Declare a private memberwise initializer explicitly when an extension formerly
  delegated to one synthesized for a view containing `@State`.

```swift
struct CounterView: View {
    let name: String
    @State private var count: Int

    init(name: String, initialCount: Int) {
        self.name = name
        self.count = initialCount
    }

    var body: some View { Text("\(name): \(count)") }
}
```

Apple documents the supported transformations in
[TN3211: Resolving SwiftUI source incompatibilities](https://developer.apple.com/documentation/technotes/tn3211-resolving-swiftui-source-incompatibilities-for-state-and-contentbuilder).

## Resolve content-builder incompatibilities

Xcode 27 unifies SwiftUI builders through `ContentBuilder`. Use the compiler
diagnostic and the smallest applicable repair:

- Change an ambiguous direct `overlay` or `background` style expression to the
  trailing-closure form.
- Qualify a SwiftUI type, such as `SwiftUI.Color`, when another imported module
  declares the same name or member.
- Avoid spelling concrete result-builder output types. For OS 27-only code that
  truly requires one, use `TupleContent`. For an earlier deployment target,
  retain `TupleView` and construct it explicitly inside the builder.
- Put `EmptyContent()` or `EmptyView()` in an otherwise empty nested builder when
  MapKit causes the empty result to resolve as map content.
- If a deeply branching, back-deployed Swift Charts builder times out during type
  checking, extract the branch into a focused `@ChartContentBuilder` function.

Do not apply these as general style rewrites. They address specific SDK 27 source
incompatibilities described by TN3211.

## Replace deprecated previews

SDK 27 deprecates the legacy `PreviewProvider` family and preview modifiers such
as `previewDevice`, `previewLayout`, and `previewDisplayName`. Prefer `#Preview`,
preview traits, or the Xcode canvas device picker when they preserve the preview's
behavior. Keep a provider when preview macros cannot express the required case.
Apple's
[deprecated previews index](https://developer.apple.com/documentation/swiftui/previews-deprecated)
lists the affected surface.

Use the installed SDK diagnostic as the final authority. For example,
`statusBarHidden(_:)` is not an SDK 27 hard deprecation on visionOS even though it
has no effect there.
