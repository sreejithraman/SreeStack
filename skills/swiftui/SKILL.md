---
name: swiftui
description: SwiftUI interface work on Apple platforms. Use when choosing SwiftUI versus UIKit; building, reviewing, or restructuring SwiftUI views, state flow, navigation, presentation, component feedback, async or edge-state behavior, accessibility semantics, or Liquid Glass; or applying a diagnosed SwiftUI performance fix.
---

# SwiftUI

Shape the interface around SwiftUI's ownership, identity, and environment rather
than reproducing an imperative view hierarchy. Preserve the product's existing
architecture and deployment targets unless the task changes them.

For an authorized build or fix, implement and test the workflow below. For a
plan or review, leave the product unchanged and turn its implementation and test
steps into exact proposed changes, findings, and checks.

## Workflow

1. Inspect the affected scene, views, models, deployment targets, and existing
   design system. Trace each mutable value to its source of truth and each user
   action to the code that owns its effect.
2. Read only the references needed for the task:
   - [Choosing SwiftUI or UIKit](references/framework-choice.md) when the framework
     is not fixed or the work could introduce a framework boundary. If UIKit owns
     the affected surface, continue with `uikit` and end this workflow. For a
     hybrid, name the boundary and continue here only for the SwiftUI-owned side.
   - [State and data flow](references/state-and-data-flow.md) for ownership,
     Observation, bindings, environment values, or editable drafts.
   - [Composition and identity](references/composition-and-identity.md) for view
     boundaries, collection identity, update scope, or restructuring a large view.
   - [Navigation and presentation](references/navigation-and-presentation.md) for
     stacks, split views, routes, sheets, dialogs, or restoration.
   - [Materials and Liquid Glass](references/materials-and-glass.md) when adopting
     current platform materials or reviewing custom glass effects.
3. Make the source of truth and view identity explicit before changing layout.
   Give each view only the values, bindings, and actions it needs. Keep durable
   storage and business rules outside transient view state.
4. Prefer native containers and controls for the target platform. Add a UIKit or
   AppKit bridge at a deliberate boundary when SwiftUI lacks the required behavior;
   keep lifecycle and ownership on one side of that boundary.
5. For interactive components, give immediate feedback and keep loading, empty,
   disabled, error, and overflow states close to the action or content they
   describe. Prevent interrupted or repeated async work from letting an older
   result overwrite the current state. Prefer platform controls and strong
   defaults over extra options; preserve valid activation and cancellation.
6. Preserve useful accessibility semantics. Expose the control's name, value,
   state, and actions, and keep focus and announcements aligned with the task and
   reading order rather than an incidental view hierarchy. Announce visible async
   status, validation, and errors when focus does not move and the change would
   otherwise be missed.
7. Build the affected targets and exercise main, edge-state, interruption, and
   repeated-input transitions. When behavior or accessibility is in scope,
   exercise the supported touch, pointer, keyboard, focus, announcement, and
   VoiceOver reading paths. Use
   `manual-verify` for visual or interactive acceptance checks. Use `animate` for
   motion design, `ios-haptics` for tactile feedback when its iOS 26+ SwiftUI scope
   applies, `ui-visual-design` for visual hierarchy and token-system work, and
   `diagnosing-bugs` when a failure or performance regression needs investigation.

After performance diagnosis identifies the bottleneck, use the data-flow and
composition guidance here to narrow invalidation or reduce body work without
changing behavior.
