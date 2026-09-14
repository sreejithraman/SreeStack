# Implementation checks

Read the full selected pattern, then implement it within the project’s component and motion system. The examples show motion mechanics; complete the component lifecycle and affected input paths as part of the change.

## Components and state

- Use the project's accessible component and lifecycle hooks. Example HTML and class toggles supply motion only. Preserve focus entry and return, Escape handling, labels, keyboard navigation, and hidden-state semantics where the component needs them. Opacity and `pointer-events: none` alone do not remove hidden controls from keyboard focus or the accessibility tree.
- Map selectors and state attributes together. Keep enter, exit, and cleanup phases intact; retain an exiting surface until its exit finishes, except when motion is disabled.
- Scope queries and mutable state to each component instance. Cancel timers, animation frames, and listeners on teardown. Handle rapid reopen, repeat, and interruption so old callbacks cannot overwrite the new state. Use the live value when retargeting.
- Code examples that read durations with `parseFloat` assume the stated units. Resolve tokens to usable values and handle `s` versus `ms` when using the project's tokens. Keep JavaScript waits aligned with actual CSS timing and the reduced-motion path.

## Tokens and rendering

- Each pattern includes its variables. Map them to existing project tokens and keep theme overrides. Add only the values the interaction needs. Scope tokens to avoid collisions across patterns.
- Preserve required structure when adapting selectors. Measure size when a pattern depends on height or width; recheck after content or font changes.
- Measure layout, paint, blur, masks, and large surfaces on target browsers. CSS or WAAPI alone does not guarantee compositor execution. Keep `will-change` only where measurement supports it; remove permanent hints when they do not help.
- Treat library-specific hooks, including Base UI state attributes and Motion options, as examples. Check the installed API before use.

## Access and input

- Keep the reference's reduced-motion behavior and complete any gaps. CSS guards do not stop JavaScript timers or loops. Stop needless work and expose the final useful state; ensure text, controls, and status remain available without motion. Check changes to the preference while mounted.
- Gate hover motion for a fine pointer with hover support. Keep keyboard focus behavior usable and touch actions direct.
- For gestures, follow [drag-to-dismiss](patterns/drag-to-dismiss.md) for pointer ownership, cancellation, release velocity, and bounds.
- Treat cloned text, tab copies, particles, and other duplicate visuals as decorative. Keep one accessible source of content and one set of focusable controls.
- Streaming and status examples must reflect real application state. Decorative timing must not delay available content, erase a useful error, imply progress that has not occurred, or loop a completed operation.
