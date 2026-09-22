# Toolbars

Use semantic toolbar placements and let the platform adapt the bar. When space is
constrained, decide which commands must remain visible and which can move into
overflow instead of relying on declaration order.

## Control overflow

- Apply `.visibilityPriority(_:)` to toolbar content. Higher priority stays
  visible longer. `.automatic` exists across OS 27 platforms; `.low`, `.high`,
  and relative priorities have narrower iOS and macOS availability.
- Put commands that should always live in overflow in `ToolbarOverflowMenu` or
  `.toolbarOverflowMenu { ... }`. These APIs are limited to iOS and visionOS 27.
- Use `.topBarPinnedTrailing` for critical trailing items that must stay visible.
  It is limited to iOS and visionOS 27.

See Apple's [`ToolbarOverflowMenu`](https://developer.apple.com/documentation/swiftui/toolbaroverflowmenu)
documentation and check the active SDK for the exact platform availability of
the priority used.

## Minimize while scrolling

The Xcode 27 final API is
`.toolbarMinimizationBehavior(_:for:)` with `ToolbarMinimizationBehavior`.
Use it only when hiding bar chrome during scrolling improves the content task.
The platform decides `.automatic`; iOS also exposes explicit scroll directions
and `.never`. The supported placement documented for this behavior is the
navigation bar.

Use
[Apple's API documentation](https://developer.apple.com/documentation/swiftui/view/toolbarminimizationbehavior%28_%3Afor%3A%29)
for the active platform. Earlier prerelease material used `Minimize` in these
names; do not emit that spelling against the final SDK.

Verify compact width, resized macOS windows, localization expansion, Dynamic
Type, keyboard access, and every overflow command. When minimization changes
safe-area behavior or restoration, measure the actual layout before adding the
advanced safe-area or restoration controls.
