# Collection Interactions

Keep collection identity stable and mutate the owning model. The view modifiers
coordinate interaction; they do not move or delete domain data for the app.

## Reorder any container

On iOS, macOS, watchOS, and visionOS 27, apply `.reorderable()` to the `ForEach`
or other `DynamicViewContent`, then apply
`.reorderContainer(for:isEnabled:move:)` to its enclosing list, stack, grid, or
custom layout. The callback receives a `ReorderDifference` whose ordered sources
and destination describe the requested move. Apply that difference to the source
of truth and test moves toward the beginning, middle, and end.

For sections or multiple collections, give each dynamic collection a stable
collection identifier and use the container overload with `in:`. For models that
are not `Identifiable`, use the overload whose final SDK label is `itemID:`.
There is no system `ReorderDifference.apply(to:)`; any application helper belongs
to the app and needs its own tests.

See Apple's [`reorderable()`](https://developer.apple.com/documentation/swiftui/dynamicviewcontent/reorderable%28%29)
and [`reorderContainer`](https://developer.apple.com/documentation/swiftui/view/reordercontainer%28for%3Aitemid%3Aisenabled%3Amove%3A%29)
documentation. The APIs are unavailable on tvOS.

## Add swipe actions outside `List`

Keep `.swipeActions(...)` on each row. On iOS, macOS, watchOS, and visionOS 27,
add `.swipeActionsContainer()` to the custom scrolling or collection ancestor.
The container coordinates the open row and dismisses actions during scrolling or
outside interaction; applying it to `List` has no effect because `List` already
provides that coordination.

Use the `onPresentationChanged` overload only when the feature needs to react to
the revealed state. Avoid duplicating the presentation state merely to render the
row. See Apple's [`swipeActionsContainer`](https://developer.apple.com/documentation/swiftui/view/swipeactionscontainer%28%29)
documentation. The new container and callback are unavailable on tvOS.

Exercise drag and swipe gestures on each supported input surface. Verify full
swipe behavior, cancellation, scrolling dismissal, focus, and accessibility
actions with `manual-verify` when these interactions affect the requested flow.
