# SwiftUI feedback

Use `sensoryFeedback` to express the meaning of a state change. Keep the modifier
on a view that remains mounted when the event arrives. Native controls may
already provide feedback; inspect before adding a second response.

## Choose the trigger

| Event shape | Trigger | Selection rule |
| --- | --- | --- |
| Discrete selection | Selected value | Emit `.selection` for intended changes; exclude programmatic resets if they carry no meaning. |
| Entering a snap | Alignment state or snap event ID | Emit on entry, then wait for release before another snap. |
| Repeated operation outcomes | New completion event with identity and outcome | Choose `.success` or `.error` from the outcome. |

An `Equatable` trigger must change for each intended event. A Boolean set true
once misses later successes. A loading Boolean changes on both start and finish.
For one fixed response, use `sensoryFeedback(_:trigger:)`; use its condition
variant to filter transitions or its feedback-selection variant to return the
right response or `nil`.

The operation owner emits a fresh completion only after it knows the result.
The view below consumes that event; it does not infer success from a button tap.

```swift
import SwiftUI

struct SaveCompletion: Equatable {
    enum Outcome: Equatable {
        case saved
        case failed
    }

    let id = UUID()
    let outcome: Outcome
}

@MainActor
struct SaveStatus: View {
    let completion: SaveCompletion?
    let hapticsEnabled: Bool

    var body: some View {
        Text(status)
            .sensoryFeedback(trigger: completion) { _, event in
                guard hapticsEnabled, let event else { return nil }
                switch event.outcome {
                case .saved: return .success
                case .failed: return .error
                }
            }
    }

    private var status: String {
        switch completion?.outcome {
        case .saved: "Saved"
        case .failed: "Save failed. Try again."
        case nil: ""
        }
    }
}
```

On the main actor, publish `SaveCompletion(outcome: .saved)` after a committed
save or `.failed` with the failure presentation. Route cancellation separately;
it is not success. Use the app's actual error message and recovery action in
place of the example's generic status.

## Own async results and view lifetime

Keep operation lifetime with its existing state owner. If several requests can
overlap, define which result belongs to the current interaction before publishing
feedback. Discard obsolete callbacks. A task cancellation request does not prove
that a write failed or never committed; determine the real outcome first.

Attach feedback to the UI that will present that result. An event published
before the modifier mounts is not a request to replay later. Recreating the view,
recomputing its body, or restoring old state must not invent a new user event.
A preferences change alone should not replay the last result.

SwiftUI observes changes across updates; an event ID is not a playback queue.
For dense input, first decide whether every event deserves feedback. Use Core
Haptics for a designed texture or timed pattern. Use direct UIKit emission when
a discrete control event needs to bypass view update timing.

## Direct UIKit emission

Use this path for an existing UIKit control or a demonstrated need for direct
standard feedback. Keep its generator with the interaction owner, call it on
the main actor, and use the relevant view when creating a view-associated
generator such as `UIImpactFeedbackGenerator(style:view:)`.

Map the design to `selectionChanged()`, `impactOccurred()`, or
`notificationOccurred(_:)`. Keep gesture thresholds and outcome selection in
the interaction logic. Direct emission still obeys preference, cancellation,
and single-owner rules; it is not a fallback for system suppression.

Call `prepare()` during approach to a likely event. Immediate preparation and
emission provide no preparation interval. Preparation at screen load does not
keep later taps ready. Retain the generator through the interaction and let it
become idle when no longer needed; never delay an accepted event or maintain a
permanent preparation timer.

## Sources

- [Feedback types](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [Trigger modifier](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:))
- [Feedback selection](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(trigger:_:))
- [View-associated impact generator](https://developer.apple.com/documentation/uikit/uiimpactfeedbackgenerator/init(style:view:))
- [Generator preparation](https://developer.apple.com/documentation/uikit/uifeedbackgenerator/prepare())
