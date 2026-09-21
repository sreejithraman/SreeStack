# Apple-platform motion

Use this branch for SwiftUI and UIKit. Prefer the app's existing framework, system components, navigation, transitions, and animation tokens. System components already provide familiar motion and can adapt to accessibility settings and input methods; custom motion must earn the extra behavior. See Apple's [Motion](https://developer.apple.com/design/human-interface-guidelines/motion) guidance.

## SwiftUI

Check the project's deployment target and installed SDK before choosing an API. Use an availability-compatible transition or state lifecycle instead of raising the deployment target for motion alone.

Model motion as a state change:

- Use `withAnimation` when one action should animate the state changes it performs.
- Use `animation(_:value:)` when one view should animate in response to one explicit value. Keep the modifier close to the affected view so unrelated changes do not inherit the animation.
- Use `transition(_:)` for insertion and removal, and `contentTransition(_:)` when existing content changes in place.
- Use `Transaction` when a subtree needs a different animation, no animation, or an animation completion. Keep lifecycle work tied to state and completion APIs rather than guessed delays.
- Reach for custom `Animatable` data only when built-in animatable modifiers and transitions cannot express the interpolation.

These choices follow Apple's [SwiftUI animation overview](https://developer.apple.com/documentation/swiftui/animations), [`animation(_:value:)`](https://developer.apple.com/documentation/swiftui/view/animation(_:value:)), and [`Transaction`](https://developer.apple.com/documentation/swiftui/transaction) documentation.

For gesture-driven motion, keep transient gesture state separate from durable model state. Let direct manipulation track the gesture without lag, then animate only the settle or dismissal after release. `GestureState` resets when the gesture ends and is suitable for transient interaction state; see [Adding interactivity with gestures](https://developer.apple.com/documentation/swiftui/adding-interactivity-with-gestures) and [`GestureState`](https://developer.apple.com/documentation/swiftui/gesturestate).

## UIKit

Use the app's established transition and animation APIs for ordinary state changes. Use `UIViewPropertyAnimator` when the interaction must pause, reverse, scrub, or continue from a partially completed state. Keep one owner for the animator lifecycle and finish or cancel it when the owning interaction ends. See [`UIViewPropertyAnimator`](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator).

## Reduce Motion

In SwiftUI, read the `accessibilityReduceMotion` environment value. In UIKit, read `UIAccessibility.isReduceMotionEnabled` and observe `UIAccessibility.reduceMotionStatusDidChangeNotification` through a lifecycle-owned `NotificationCenter` observation. When notified, read the value again, replace or finish disallowed active motion without delaying useful content, expose the final state, and apply the new preference to later transitions. Remove the observation and cancel owned decorative motion when its owner ends.

When Reduce Motion is enabled:

- Remove or replace large travel, zoom, parallax, depth simulation, spinning, and repeated movement.
- Prefer a restrained fade, color or material change, symbol change, or instant state update when it preserves meaning.
- Stop decorative loops and autoplaying motion. Do not make useful content wait on a disabled animation.
- Preserve the final state and communicate important feedback through text, shape, color with sufficient contrast, haptics, or audio as appropriate; motion cannot be the only cue.

Apple specifically calls out large and three-dimensional movement in [`accessibilityReduceMotion`](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion) and provides broader evaluation criteria in [Reduced Motion evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria).

## Verification

Run the real interaction in Simulator or on device. Check:

- Initial presentation and dismissal.
- Rapid repeat, reversal, and interruption.
- Drag tracking, cancellation, release velocity, and settling when gestures apply.
- Touch plus any supported pointer, keyboard, VoiceOver, or Switch Control path affected by the change.
- Reduce Motion both enabled and disabled, including a preference change while the screen is present.
- Text scaling, rotation, safe areas, and content changes that alter the animated geometry.

Use slow animations or a recording to inspect origin, path, clipping, unexpected layout changes, and competing animations. Profile only when the real interaction drops frames, performs expensive redraws, or shows a measurable rendering problem.
