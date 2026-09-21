# Layout and Safe Areas

## Describe relationships

Use Auto Layout constraints and guides to express relationships inside the owning
view hierarchy. Create constraints once, then update constants or switch between
small named constraint sets when state changes. Base adaptation on container bounds,
traits, and content rather than a device model or global screen size.

Use `layoutMarginsGuide` for component spacing, `readableContentGuide` for readable
text width, and [`safeAreaLayoutGuide`](https://developer.apple.com/documentation/uikit/uiview/safearealayoutguide)
for content that must avoid bars, rounded corners, and other obscured regions.
Backgrounds can intentionally extend to the view edges while interactive and
readable content remains constrained to the appropriate guide.

## Let containers define insets

The safe area is local to a view and can change after it joins a window, after bars
appear, or while a window resizes. Read `safeAreaInsets` when the view is in its
hierarchy and respond in `safeAreaInsetsDidChange()` only when constraint guides
cannot express the behavior. A custom container can adjust a child's additional
safe area when it owns an overlay; keep that adjustment with the container.

Treat the keyboard as changing the usable region rather than as a fixed height.
Prefer UIKit's keyboard layout guide where supported. When notifications are
required by the deployment target or behavior, convert the reported frame into the
affected view's coordinate space and follow the notification's timing.

## Verify adaptation

Exercise the sizes and environments the feature supports: portrait and landscape,
split view or resizable windows, large Dynamic Type sizes, right-to-left layout,
system bars, presented controllers, and keyboard appearance where relevant. Check
for ambiguous constraints, clipped text, unreachable controls, and scroll content
hidden behind overlays.
