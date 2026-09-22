---
name: web-interface
description: Build and review browser interface behavior and accessibility. Use for HTML semantics, forms, keyboard or focus behavior, status announcements, pointer or touch input, component states, and async or repeated interactions. Use ui-visual-design for visual direction and animate for motion.
---

# Web Interface

Make web components understandable and reliable across browser input and access
paths. Preserve the product's visual direction unless the request also calls
for `ui-visual-design`.

For an authorized build or fix, implement the smallest complete change. For a
plan or review, leave the product unchanged and report each affected location,
current behavior, exact proposed change, and check the implementation must pass.

## Process

1. Inspect the rendered component, semantic tree, current interaction contract,
   affected state, input methods, and nearby product patterns.
2. Prefer native HTML elements and browser behavior. When a custom component is
   justified, preserve the equivalent name, role, value, state, relationship,
   focus, and keyboard contract.
3. Associate labels, help, validation, and errors with the controls they
   describe. Keep focus visible and ordered by the task, restore or move it
   deliberately after navigation or dismissal, and avoid keyboard traps.
4. Expose visible async status, validation, and errors to assistive technology
   when focus remains elsewhere.
5. Model the component's real states, including loading, empty, disabled, error,
   overflow, cancellation, and interruption. Keep those states inside the
   component contract rather than relying on a happy-path page shell.
6. Start press feedback on pointer or key down, but commit only after a valid
   activation. Clear the pressed state when input cancels, leaves the allowed
   target, or becomes a drag.
7. Handle rapid and repeated input without stale work overwriting current
   state. Keep the control usable while work is pending when the action safely
   permits it.
8. Use `animate` when feedback moves or transitions; this skill still owns the
   action and state contract. Use `ui-visual-design` when changing hierarchy,
   styling, or visual identity.
9. Exercise the real component through affected mouse, touch, keyboard, focus,
   and assistive-technology paths. Include rapid repeat, interruption, and
   non-happy states. Use `manual-verify` when hands-on evidence would add
   confidence.

Honor increased contrast, forced colors, reduced transparency, and larger text
where the browser or operating system exposes them. When a screen-reader or
announcement check cannot run, name that evidence gap.

The work is done when every affected semantic, keyboard, focus, status, input,
and edge-state path passes on the real page, or its remaining evidence gap is
explicit.
