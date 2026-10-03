# Web behavior and accessibility

Use this branch for browser component behavior, semantics, input, state, and
accessibility. Preserve the product's visual direction unless visual design is
also in scope.

1. Inspect the rendered component, semantic tree, interaction contract,
   affected states, supported input methods, and nearby product patterns.
2. Prefer native HTML elements and browser behavior. When a custom component is
   justified, preserve the equivalent name, role, value, state, relationship,
   focus, and keyboard contract.
3. Associate labels, help, validation, and errors with the controls they
   describe. Keep focus visible and ordered by the task. Restore or move it
   deliberately after navigation or dismissal, and prevent keyboard traps.
4. Expose visible async status, validation, and errors to assistive technology
   when focus remains elsewhere.
5. Model loading, empty, disabled, error, overflow, cancellation, and
   interruption inside the component contract rather than relying on a
   happy-path page shell.
6. Start press feedback on pointer or key down, but commit only after a valid
   activation. Clear the pressed state when input cancels, leaves the allowed
   target, or becomes a drag.
7. Handle rapid and repeated input without stale work overwriting current
   state. Keep the control usable while work is pending when the action safely
   permits it.
8. Honor increased contrast, forced colors, reduced transparency, and larger
   text where the browser or operating system exposes them.
9. Exercise affected mouse, touch, keyboard, focus, and assistive-technology
   paths on the real component. Include rapid repeat, interruption, and
   non-happy states. When an announcement or screen-reader check cannot run,
   name that evidence gap.

Use `animate` for the moving feedback's timing and interruption while keeping
the action and state contract here. Use `manual-verify` when hands-on evidence
would add confidence.

This branch is complete when every affected semantic, keyboard, focus, status,
input, and edge-state path passes on the real page, or its remaining evidence
gap is explicit.

## Content under constraint

When real data breaks a component, use `manual-verify`'s edge-data workflow to
reproduce it through the existing data boundary. Choose the display contract per
field, then fix the demonstrated cause:

- Keep identifying content and compared numbers, amounts, and dates readable.
  Wrap, clamp previews, or truncate according to the task; expose the complete
  value through a usable detail or expansion path when shortened. A hover-only
  tooltip does not cover touch or keyboard access.
- When a text column pushes siblings out of a flex row, inspect its automatic
  minimum size; `min-inline-size: 0` can let it shrink. Protect fixed-size icons
  and necessary trailing actions from unwanted shrinking. Verify the combined
  row at its real container width. See [flex automatic minimum size](https://drafts.csswg.org/css-flexbox-1/#min-size-auto).
- For identifiers that otherwise overflow, consider `overflow-wrap: anywhere`
  on that content, preserving normal breaks elsewhere. Diagnose before applying
  it globally. See [overflow wrapping](https://drafts.csswg.org/css-text-3/#overflow-wrap-property).
- Choose explicit missing-field and media fallbacks; retain enough identity to
  distinguish duplicate names. Format numbers, plurals, and time for the
  supported locale. Avoid clipping tall scripts or splitting multi-code-point
  characters when deriving initials.
- Treat a large collection as a measured usability and performance question.
  Choose pagination or virtualization when evidence and the interaction model
  warrant it, then check navigation and accessibility as well as scrolling.
