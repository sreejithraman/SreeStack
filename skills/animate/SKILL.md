---
name: animate
description: "Design, implement, and tune web, SwiftUI, and UIKit interface motion. Use for motion on those platforms when deciding whether to animate, building or reviewing transitions, shaping gesture-driven motion, or honoring reduced-motion preferences."
---

# Animate

Build the requested motion on its real platform. An instant state change is a valid result when motion would add delay without meaning.

For an authorized build or fix, implement and test the workflow below. For a
plan or review, leave the product unchanged and report the proposed motion or
instant alternative, exact changes, and checks the implementation must pass.

## Process

1. Inspect the real interaction, nearby motion, design tokens, target platform and supported versions, input methods, use rate, state changes, and runnable surface. Finish when every animated element in scope has this evidence.
2. Apply the motion gate below. Name the purpose and frequency tier. If motion fails the gate, keep the state change instant and test that state on the real surface.
3. Read the platform branch before choosing APIs or timing:
   - For websites and web apps, read [web motion](references/web.md). Read only the pattern guides that match the interaction.
   - For SwiftUI or UIKit, read [Apple-platform motion](references/apple-platforms.md).
4. Choose the smallest mechanism that fits the interaction. Use the product's current components, motion system, and tokens before adding another abstraction or dependency.
5. Implement the reduced-motion path with the primary behavior. Preserve useful feedback and the final state when movement is reduced or removed.
6. Test entry, exit, rapid repeat, interruption, affected input methods, and reduced motion on the target platform. Slow playback or frame-step when timing and coordination need closer study.

When motion passes the gate, the work is done when it has a stated purpose, follows the product and platform conventions, survives interruption, and passes the affected input and reduced-motion paths. When motion fails the gate, the work is done when the instant or static state passes those same affected paths.

## Motion gate

| Use rate | Default |
| --- | --- |
| Very frequent or keyboard-led | Instant |
| Frequent, such as hover or list movement | None or very short |
| Occasional, such as a modal, drawer, or toast | Standard interface motion |
| Rare, explanatory, or celebratory | More room for delight |

Motion needs one job:

- Confirm input.
- Explain spatial origin or destination.
- Mark a state change.
- Bridge a change that would otherwise feel abrupt.
- Teach a rare flow.
- Add delight to a rare moment without blocking the task.

Keep content steady while someone reads or acts on it. Decorative motion must not move useful data or its controls. If none of the jobs applies, stop at the gate.

## Shared behavior

- Prefer the platform's standard components and transitions. Add custom motion only when it communicates something the system behavior does not.
- Make feedback immediate, brief, and proportional to the state change. Frequent actions should feel faster and quieter than rare ones.
- Preserve spatial meaning between entry and exit. Tune them separately when the system response should be faster on dismissal.
- Start interrupted motion from its live value. Gesture-driven motion should track input directly, preserve the grab point, and settle from the release state rather than restart from an old target.
- Keep controls usable while decorative motion runs. Important information needs a non-motion cue.
- Treat durations, curves, and spring values as test points. Geometry, content, input, platform, and product tone determine what feels right.

## Handoff

For a build, deliver the implemented result first. When the gate rejects motion,
deliver the instant or static alternative instead. For a plan or review, deliver
the proposal or findings without editing the product. Then state:

- The motion gate result and purpose.
- The platform mechanism and reduced-motion behavior.
- Any feel check that still needs slow motion, frame stepping, Simulator, or device testing.

Keep the note brief; the tested interaction is the result.
