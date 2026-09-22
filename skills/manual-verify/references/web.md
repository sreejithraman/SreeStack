# Web Verification

Use the requested deployment and the browser environment already attached to
the task when possible. For a local change, start or locate the development
server; for a live site, open its URL.
Reach the exact route or state under test and record the URL, viewport, or
device mode when they affect the result.

## Observe and interact

- Capture a browser snapshot or inspect the DOM and accessibility tree before
  interacting. Pair semantic inspection with a screenshot when appearance matters.
- Target elements by role, accessible name, label, or another stable locator.
  Reinspect the page after navigation, re-rendering, or layout changes before
  reusing a target.
- Exercise pointer, keyboard, focus, scrolling, and responsive behavior when the
  change affects them. Test only the viewports and input methods relevant to the
  requested workflow and likely regression risk.
- Wait for visible loading to settle. If an action produces no clear result,
  inspect the console and failed network requests before deciding whether the
  product or the environment failed.

## Evidence

Capture the states that establish the result: the initial condition, the outcome,
and any failure. Record the URL, viewport, and relevant console or network
evidence. Do not infer success from a screenshot when behavior required an
interaction.
