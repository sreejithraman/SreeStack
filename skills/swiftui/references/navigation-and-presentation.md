# Navigation and Presentation

## Model destinations

Use `NavigationStack` for linear navigation and `NavigationSplitView` when the
platform and information architecture call for columns. Put navigation state at
the scene or feature boundary that must restore, deep-link, or coordinate it.

Represent a route with a small stable value, usually an identifier plus the
minimum routing context. Resolve the current model at the destination. Passing a
large mutable model through the path turns navigation state into data transport
and makes restoration brittle.

Use a typed array when every route has one type. Use `NavigationPath` when a stack
must contain heterogeneous route values. Register each value with the destination
that knows how to render it. See Apple's
[navigation stack guidance](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
and [`NavigationStack`](https://developer.apple.com/documentation/swiftui/navigationstack).

## Own presentations

Keep sheet, popover, alert, and confirmation state with the feature that decides
to present it. Prefer item-driven presentation when the presented content has an
identity. The optional item then describes both whether the presentation exists
and what it displays.

For alerts and confirmation dialogs that act on a value, use the builder overload
whose `item` is a `Binding<T?>`. The optional value controls presentation and is
passed to the actions and message closures; it does not need to conform to
`Identifiable`. These overloads back-deploy to the original builder API versions,
so they do not need an OS 27 availability check. See Apple's
[`confirmationDialog` item overload](https://developer.apple.com/documentation/swiftui/view/confirmationdialog%28_%3Aitem%3Atitlevisibility%3Aactions%3Amessage%3A%29).

Treat dismissal as an outcome. Let the presented feature report save, cancel, or
delete through an action, then let the owner update durable state and presentation
state in a defined order. Use the environment dismiss action for a local dismissal
that needs no domain result.

## Verify state transitions

Exercise push and pop, programmatic routes, deep links, restoration if supported,
and presentation dismissal. On iPadOS and macOS, resize or change column visibility
when the changed flow uses a split view. Confirm that a repeated route reaches the
correct model and that cancelling a presentation leaves its source of truth intact.
