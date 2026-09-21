---
name: uikit
description: UIKit interface work. Use when building, maintaining, or modernizing UIKit controllers, scenes, traits, adaptive layout, collections, or Liquid Glass; or deciding whether an existing UIKit surface should adopt SwiftUI.
---

# UIKit

Build each interface around its actual view-controller, view, window, and scene
context. Preserve the product's architecture and deployment targets while making
ownership and lifecycle explicit.

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
5. For modernization, replace a deprecated or global assumption end to end. Trace
   every caller, pass local context where needed, and preserve supported behavior
   for each active scene rather than swapping symbols mechanically.
6. Build the affected targets and exercise resizing, traits, navigation, and data
   updates relevant to the change. Use `manual-verify` for visual or interactive
   acceptance checks, `animate` for motion, and `diagnosing-bugs` for runtime
   failures or performance regressions.
