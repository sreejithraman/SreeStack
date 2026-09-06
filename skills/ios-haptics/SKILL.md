---
name: ios-haptics
description: Design, implement, and tune haptics for SwiftUI apps targeting iOS 26+. Use for system feedback, custom Core Haptics or AHAP patterns, matching touch with sound and motion, and diagnosing missing, repeated, or mistimed feedback.
---

# iOS haptics

Build feedback for SwiftUI apps with an iOS 26 minimum deployment target.
Use `sensoryFeedback` for standard interactions and Core Haptics when the design
needs an authored pattern. Hardware support and user preferences still matter.

## Design the interaction first

Inspect the affected flow, its state owner, and any existing feedback. Check
native controls before adding feedback they may already provide. For a bug fix,
keep the intended design unless the evidence calls for a change.

Name what the user should learn through touch. Apply Apple's design principles
to the proposed event:

| Principle | Question to settle | Example |
| --- | --- | --- |
| Causality | What causes the feedback, and when does it become true? | Save success follows the completed save. A snap coincides with entering alignment. |
| Harmony | Do touch, motion, and any sound describe the same event? | A brief contact gets a brief response; a gradual expansion may justify a rising sensation. |
| Utility | Does feeling this help the user? | Selection feedback can guide precise adjustment. Routine navigation may need none. |

Separate press, acceptance, and completion. Give each feedback event one meaning
and one owner. Keep the same meaning consistent across the feature. Prefer a
small set of distinct responses over a different pattern for every control.

For each chosen event, settle its trigger, visual landmark, desired feel, and
cancellation or stop condition. Include sound when it belongs to the requested
experience. A sentence is enough for one event; use a table for a larger flow.

## Choose the feel and the playback path

Read [Designing touch, sound, and motion](references/design.md) when choosing or
tuning feedback. It covers system meanings, pattern controls, shared timing, and
worked designs. Choose rhythm and duration before strength; stronger feedback
cannot repair the wrong trigger.

Start with SwiftUI feedback:

- `.selection` for discrete changes.
- `.impact` with suitable weight or flexibility for contact and snapping.
- `.success`, `.warning`, or `.error` for a meaningful outcome.

Read [SwiftUI feedback](references/swiftui-feedback.md) when implementing these
choices. Keep triggers tied to real state transitions or explicit events. This
reference also covers direct UIKit emission when an existing UIKit control or
an event that must bypass SwiftUI update timing calls for it.

Use Core Haptics when the design needs a distinct rhythm, an intensity envelope,
a sustained texture, or authored audio and touch on one timeline. Read
[Custom playback](references/core-haptics.md) for pattern construction, AHAP,
engine ownership, and recovery. A custom animation alone does not justify a
custom haptic engine.

These paths share the same event design and preferences. Select one owner for
each event; do not emit through both paths for the same result. Reuse the app's
feedback infrastructure when it fits. A single modifier needs no global service.

## Keep feedback optional and current

Honor the app's existing haptics preference and system suppression. Preserve
visible and accessible confirmation when touch or sound is absent. Use hardware
capabilities for custom playback, not a list of device names.

Tie feedback to the UI the user actually sees. A cancelled action must not emit
completion. An old async result must not produce feedback for a new interaction.
If an operation outlives its screen, let the remaining UI decide whether feedback
still belongs there. When reduced motion changes the visual sequence, align the
haptic with the new event timing rather than an old animation delay.

## Verify behavior, then tune on a device

Compile examples and changes for iOS 26 using the project's Swift concurrency
settings. Check ordinary use, repeated outcomes, failure, cancellation, and
preferences. Add tests for meaningful event-selection or lifecycle branches;
a mock proves requests, not sensations.

Compare the proposed feel on supported physical hardware in the real flow:

1. Fix onset against the visible event.
2. Adjust duration and rhythm at normal and rapid interaction speeds.
3. Tune strength and sharpness without changing both at once.
4. Compare touch and sound separately, then with motion together.

For custom playback, also check first use, background return, interruptions, and
stopping sustained effects. Record device and OS details. Treat power state and
settings as test conditions rather than presumed explanations for failure.

For missing feedback, inspect the event, preference, hardware, owner lifetime,
and playback errors. For late or repeated feedback, inspect state changes,
duplicate emission, queued work, and stale callbacks before altering intensity.

Deliver the event choices, their design reasons, and the checks that ran. Include
custom assets and stop/recovery behavior where used. A simulator or recording
cannot establish tactile quality; explicitly name any device tuning still needed.

Design basis: [Apple's haptic design principles](https://developer.apple.com/videos/play/wwdc2021/10278/).
