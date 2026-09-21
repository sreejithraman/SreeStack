# Materials and Liquid Glass

Treat current platform materials as part of the system component hierarchy. An
app built with current SDKs often receives the current appearance through standard
navigation, toolbar, tab, menu, control, and presentation APIs. Start there, then
add a custom effect only when the design calls for a custom functional surface.
Apple's [adoption guidance](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
covers the system components and accessibility behavior.

## Custom SwiftUI glass

The current custom glass APIs require the current SDK and version 26 or later on
iOS, iPadOS, macOS, tvOS, and watchOS; they are unavailable on visionOS. Confirm
the boundary in the active SDK because it can change. In shared multiplatform
source, put the visionOS fallback in a compile-time `#if os(visionOS)` branch and
keep glass types and modifiers outside that branch. On supported platforms, put
custom glass behind a version availability check. Keep a fallback with the same
structure, actions, legibility, and interaction.

- Apply `glassEffect(_:in:)` after modifiers that establish the view's appearance
  and shape.
- Group related effects in one `GlassEffectContainer`. Its spacing controls when
  neighboring shapes begin to blend, and the shared container reduces rendering
  work.
- Add `interactive()` only to an element that actually responds to interaction.
- Use stable glass effect identifiers when shapes merge or transition. Coordinate
  the state change with `animate`; the visual effect does not define the product's
  motion behavior by itself.
- Use custom glass sparingly on the most important functional elements. Let the
  content remain the visual focus.

Apple documents modifier order, containers, unions, and transitions in
[Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views).

## Verify adaptations

Check the result over representative light and dark content, with increased
contrast, reduced transparency, and reduced motion. System components adapt to
these settings; confirm that custom colors, effects, and transitions still keep
text and controls clear. Verify hit targets and focus independently of the glass
shape, and profile screens with several custom effects when rendering cost is a
concern.
