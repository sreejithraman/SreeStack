# Apple motion pitfalls

Use this reference for motion the system component does not supply. Keep the
app's existing framework and deployment target; check SDK availability and retain
a functional fallback for unsupported APIs.

## State and lifecycle

- Scope animation to the state and views that need it so unrelated changes stay
  unaffected. Tie lifecycle work to state and completion APIs rather than guessed
  delays. See [SwiftUI animation](https://developer.apple.com/documentation/swiftui/animations)
  and [transactions](https://developer.apple.com/documentation/swiftui/transaction).
- Preserve spatial meaning between entry and exit; retarget interrupted motion
  from its live value. Custom gestures should track input directly, preserve the
  grab point, and settle from the release state.
  Keep transient gesture state separate from durable model state; SwiftUI's
  [`GestureState`](https://developer.apple.com/documentation/swiftui/gesturestate)
  resets when the gesture ends.
- For custom UIKit motion that needs scrubbing, reversal, or pausing,
  [`UIViewPropertyAnimator`](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator)
  supplies playback control. Give its lifecycle one owner and finish or cancel
  it when the interaction ends.

Cancel owned decorative motion and scheduled work when its owner ends.

For custom glass surfaces, use the framework's
[SwiftUI](../../swiftui/references/materials-and-glass.md) or
[UIKit](../../uikit/references/materials-and-glass.md) guide for native effects,
setup, availability, and fallbacks. Check Reduce Transparency and Increase
Contrast alongside Reduce Motion.

## Reduce Motion

For app-owned effects, read SwiftUI's
[`accessibilityReduceMotion`](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion).
In UIKit, read `UIAccessibility.isReduceMotionEnabled` and observe
`UIAccessibility.reduceMotionStatusDidChangeNotification` while the effect's
owner is active; remove the observation when it ends.

When Reduce Motion is enabled, including at initial presentation, stop decorative
loops and replace large travel, zoom, parallax, depth, spinning, or repeated
movement with restrained feedback or an instant update. Expose the useful final
state. On preference changes, read the new value and apply it to active effects
and later transitions. Keep important feedback available through a non-motion
cue. Apple's
[evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria)
cover the expected adaptations.

For custom gestures, verify cancellation, release velocity, and settling. Check
geometry changes from text scaling, rotation, safe areas, and changing content.
Use slow playback or a recording when the path or coordination needs inspection.
Profile rendering when the real interaction shows a measurable problem.
