# Choosing SwiftUI or UIKit

## Default new work to SwiftUI

Use SwiftUI for a new app, scene, screen, or component unless a concrete
requirement points elsewhere. Apple calls SwiftUI its best choice for new apps
and recommends it for new features in existing apps. SwiftUI also supports one
declarative interface across Apple platforms.

Sources: [SwiftUI apps](https://developer.apple.com/documentation/technologyoverviews/swiftui),
[Platforms State of the Union, WWDC24](https://developer.apple.com/videos/play/wwdc2024/102/).

## Keep or choose UIKit for evidence

Use UIKit for the affected surface when one or more of these conditions holds:

- The feature already has stable UIKit controller, navigation, restoration, or
  scene ownership, and the requested change does not justify replacing it.
- A required system component or behavior has no suitable SwiftUI API. Wrap or
  host that capability instead of recreating it.
- The app's minimum OS version lacks the required SwiftUI API while UIKit provides
  the supported behavior.
- Measurement shows a requirement the current SwiftUI implementation cannot meet,
  and a UIKit implementation or boundary resolves that specific problem.

UIKit remains current and interoperates in both directions with SwiftUI. A broad
preference for control or an assumed performance advantage is not evidence for
choosing it. Diagnose and measure the actual behavior first.

Sources: [UIKit](https://developer.apple.com/documentation/uikit),
[UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration),
[SwiftUI performance](https://developer.apple.com/documentation/xcode/understanding-and-improving-swiftui-performance).

## Treat hybrid as an architecture

An existing UIKit app does not need a wholesale rewrite. Add SwiftUI at a coherent
feature, screen, scene, or component boundary while the UIKit shell continues to
own its established lifecycle. In a SwiftUI app, wrap the smallest UIKit view or
view controller that owns a missing capability.

Keep one side responsible for state and lifecycle across each boundary. Pass
values and actions explicitly, and translate them in one hosting or representable
adapter. Repeatedly alternating frameworks within one feature multiplies layout,
sizing, identity, and lifecycle coordination.

Apple presents incremental adoption as a normal long-term approach and provides
`UIHostingController`, `UIHostingConfiguration`, representable protocols, and
scene bridges for it.

Sources: [Use SwiftUI with AppKit and UIKit, WWDC26](https://developer.apple.com/videos/play/wwdc2026/272/),
[Using SwiftUI with UIKit](https://developer.apple.com/documentation/uikit/using-swiftui-with-uikit),
[`UIViewControllerRepresentable`](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable).

## Decide at the feature boundary

1. List the required platforms, minimum OS versions, system components,
   interactions, restoration behavior, and measured constraints.
2. Start with SwiftUI for new work. Prove any uncertain capability with the
   smallest useful prototype or documentation check.
3. If a requirement needs UIKit, choose the smallest coherent UIKit-owned
   boundary and define its state, sizing, lifecycle, and event contract.
4. Preserve proven UIKit that the feature does not need to replace.
5. Verify the integrated result through the actual navigation, resizing,
   accessibility, restoration, and performance paths it must support.
