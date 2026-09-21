# View Controllers and Collections

## Keep controller ownership explicit

A view controller coordinates one screen or one coherent region. Let model and
service types own business rules and persistence. Let the controller translate
state into UIKit updates and route user actions to the owner of their effects.

Use `UINavigationController`, `UITabBarController`, and `UISplitViewController`
when their behavior matches the product. For a custom container, keep the parent
and child relationship synchronized with the view hierarchy:

1. Call `addChild(_:)`.
2. Add the child's root view and establish its frame or constraints.
3. Call `didMove(toParent:)` on the child.

For removal, call `willMove(toParent: nil)`, remove the child's constraints and
view, then call `removeFromParent()`. Forward appearance and rotation decisions
deliberately when the default forwarding does not fit. Apple's
[custom container guide](https://developer.apple.com/documentation/uikit/creating-a-custom-container-view-controller)
describes the lifecycle contract.

Keep each observer, task, and callback tied to an owner with a defined lifetime.
Capture controllers weakly in escaping callbacks when the callback owner could
otherwise retain the controller. Cancel work when its result no longer belongs to
the visible feature or current request.

## Give collection items stable identity

Prefer diffable data sources for table and collection state that changes over
time. Build snapshots from domain section and item identifiers that remain stable
through sorting, filtering, and refresh. Treat an index path as a current location,
not an item's identity.

Apply one coherent snapshot for a model transition. Configure a cell from the
identifier's current model and make asynchronous image or content work verify that
the cell still represents that identifier before applying its result. Apple's
[diffable data source example](https://developer.apple.com/documentation/uikit/updating-collection-views-using-diffable-data-sources)
shows the identifier-based update model.
