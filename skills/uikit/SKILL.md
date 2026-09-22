---
name: uikit
description: UIKit interface work. Use when building, reviewing, maintaining, or modernizing UIKit controllers, scenes, traits, adaptive layout, collections, component feedback, async or edge-state behavior, accessibility semantics, or Liquid Glass; or deciding whether an existing UIKit surface should adopt SwiftUI.
---

# UIKit

Build each interface around its actual view-controller, view, window, and scene
context. Preserve the product's architecture and deployment targets while making
ownership and lifecycle explicit.

For an authorized build or fix, implement and test the workflow below. For a
plan or review, leave the product unchanged and turn its implementation and test
steps into exact proposed changes, findings, and checks.

## Workflow

1. Inspect the affected controller hierarchy, scene configuration, layout system,
   data source, deployment targets, and user-visible behavior. Identify which
   object owns the window, content, navigation, and mutable state.
2. Read only the references needed for the task:
   - [Choosing SwiftUI or UIKit](../swiftui/references/framework-choice.md) when the
     framework is not fixed or the work could introduce a framework boundary. If
     SwiftUI owns the affected surface, continue with `swiftui` and end this
     workflow. For a hybrid, name the boundary and continue here only for the
     UIKit-owned side.
   - [View controllers and collections](references/view-controllers-and-collections.md)
     for containment, lifecycle ownership, lists, or stable item identity.
   - [Scenes and traits](references/scenes-and-traits.md) for windows, screens,
     geometry, orientation, environment changes, or deprecated global lookups.
   - [Layout and safe areas](references/layout-and-safe-areas.md) for constraints,
     margins, bars, keyboard interaction, or resizable interfaces.
   - [Materials and Liquid Glass](references/materials-and-glass.md) when adopting
     current UIKit materials or reviewing custom glass effects.
3. Choose the nearest valid context. UI code should normally derive environment
   from its view or controller; non-UI code should receive the specific value or
   capability it needs.
4. Use standard controls and containers where they express the behavior. If a
   SwiftUI island is appropriate, place `UIHostingController` at an explicit
   containment boundary and keep one owner for state and lifecycle.
5. For interactive components, give immediate feedback and keep loading, empty,
   disabled, error, and overflow states close to the action or content they
   describe. Cancel or identify interrupted and repeated async work so an older
   callback cannot overwrite the current state. Prefer platform controls and
   strong defaults over extra options; preserve valid activation and cancellation.
6. Preserve useful accessibility semantics. Expose the control's name, value,
   state, and actions, and keep focus and announcements aligned with the task and
   reading order rather than an incidental view hierarchy. Announce visible async
   status, validation, and errors when focus does not move and the change would
   otherwise be missed.
7. For modernization, replace a deprecated or global assumption end to end. Trace
   every caller, pass local context where needed, and preserve supported behavior
   for each active scene rather than swapping symbols mechanically.
8. Build the affected targets and exercise resizing, traits, navigation, data
   updates, edge states, interruption, and repeated input relevant to the change.
   When behavior or accessibility is in scope, exercise the supported touch,
   pointer, keyboard, focus, announcement, and VoiceOver reading paths.
   Use `manual-verify` for visual or interactive
   acceptance checks, `animate` for motion, `ui-design` for visual hierarchy
   and token-system work, and `diagnosing-bugs` for runtime failures or performance
   regressions.
