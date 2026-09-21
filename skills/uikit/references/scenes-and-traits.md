# Scenes and Traits

## Follow scene context

A window scene represents one UI instance and can have state independent of other
windows. Keep process-wide setup in the app delegate and scene-specific windows,
restoration, and lifecycle work with the scene or scene delegate. Apple's
[`UIWindowScene`](https://developer.apple.com/documentation/uikit/uiwindowscene)
documentation defines that boundary.

Start from the object involved in the operation:

- use a view's `window?.windowScene` for its scene;
- use that scene's `screen` when display properties are needed; and
- use `effectiveGeometry.interfaceOrientation` on iOS 16 and later when code
  genuinely needs interface orientation rather than layout size or size classes.

`UIScreen.main` does not identify the display for every window, and Apple directs
apps to use a screen obtained from context. See [`UIScreen.main`](https://developer.apple.com/documentation/uikit/uiscreen/main).
Likewise, `UIWindowScene.interfaceOrientation` is deprecated in favor of
[`effectiveGeometry.interfaceOrientation`](https://developer.apple.com/documentation/uikit/uiwindowscene/interfaceorientation).
For a deployment target below iOS 16, keep an availability-guarded fallback to
the contextual window scene's `interfaceOrientation`; do not replace it with a
process-wide screen or window lookup.

When a service lacks UI context, pass the required screen, scene, geometry, or
derived value into it. A scan of connected scenes or key windows cannot establish
which scene owns an arbitrary operation.

## Respond to traits

Read traits from the nearest `UIView` or `UIViewController` environment. Use size
classes and current bounds for adaptive layout; device labels and orientation are
usually weaker proxies for the space actually available.

On iOS 18 and later, place trait-dependent work in a lifecycle method that supports
automatic trait tracking, such as `layoutSubviews`, when it naturally belongs
there. Otherwise, on iOS 17 and later, register for the specific traits or semantic
trait set that affects the result. UIKit retains registrations for the observable
object's lifetime, so retain the registration token only when it must be stopped
earlier. On older deployment targets, keep an availability-guarded
`traitCollectionDidChange(_:)` implementation and filter for the traits that
change the result. Apple's
[trait change guidance](https://developer.apple.com/documentation/uikit/adapting-your-app-when-traits-change)
describes automatic tracking and `registerForTraitChanges` as replacements for
deprecated `traitCollectionDidChange` implementations.

Initialize the trait-dependent result during setup; a change callback only handles
later changes. Use dynamic system colors and images where possible so UIKit performs
the adaptation without custom callbacks.
