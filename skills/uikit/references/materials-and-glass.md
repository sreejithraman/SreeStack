# Materials and Liquid Glass

Build with the current SDK and inspect the interface with standard UIKit
navigation, bars, controls, and presentations before adding custom effects. These
components adopt the current system appearance and accessibility adaptations
automatically. Apple's [adoption guidance](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
describes the UIKit components that receive the design.

## Custom UIKit glass

The current `UIGlassEffect` and `UIGlassContainerEffect` APIs require iOS,
iPadOS, Mac Catalyst, or tvOS 26 or later and are unavailable on visionOS and
watchOS. Confirm the boundary in the active SDK. Keep unavailable types outside
compile-time branches for unsupported platforms, then use a version availability
check on supported platforms. Preserve the same structure, actions, legibility,
and interaction in the fallback.

- Put `UIGlassEffect` in a `UIVisualEffectView`; add the element's content to the
  effect view's `contentView`.
- Set `isInteractive` only for a control that responds to interaction. Use
  `tintColor` to communicate prominence without obscuring content.
- When several glass elements should render and merge together, put their glass
  effect views inside the `contentView` of a `UIVisualEffectView` configured with
  `UIGlassContainerEffect`. Its `spacing` defines when neighboring elements begin
  to merge.
- Keep custom glass on the functional layer above content and use it sparingly.

Apple documents the effect types in [`UIGlassEffect`](https://developer.apple.com/documentation/uikit/uiglasseffect)
and [UIKit appearance customization](https://developer.apple.com/documentation/uikit/appearance-customization).

## Verify adaptations

Check custom effects over representative light and dark content, with increased
contrast, reduced transparency, and reduced motion. Confirm that labels, icons,
focus, and hit targets remain clear when the system reduces or changes the visual
effect. Profile screens with several custom effects when rendering cost is a
concern.
