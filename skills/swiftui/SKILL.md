---
name: swiftui
description: Build, review, or restructure SwiftUI interfaces for Apple platforms, or choose SwiftUI versus UIKit for new Apple UI. Use for state ownership and data flow, view composition and identity, navigation and presentation, or platform materials including Liquid Glass.
---

# SwiftUI

Shape the interface around SwiftUI's ownership, identity, and environment rather
than reproducing an imperative view hierarchy. Preserve the product's existing
architecture and deployment targets unless the task changes them.

## Workflow

1. Inspect the affected scene, views, models, deployment targets, and existing
   design system. Trace each mutable value to its source of truth and each user
   action to the code that owns its effect.
2. Read only the references needed for the task:
   - [Choosing SwiftUI or UIKit](references/framework-choice.md) when the framework
     is not fixed or the work could introduce a framework boundary.
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
5. Build the affected targets and exercise the changed state transitions. Use
   `manual-verify` for visual or interactive acceptance checks. Use `animate` for
   motion design, `ios-haptics` for tactile feedback when its iOS 26+ SwiftUI scope
   applies, and `diagnosing-bugs` when a failure or performance regression needs
   investigation.

After performance diagnosis identifies the bottleneck, use the data-flow and
composition guidance here to narrow invalidation or reduce body work without
changing behavior.
