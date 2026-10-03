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

## Mobile browser checks

When the changed workflow involves mobile viewport, keyboard, touch, scroll, or
browser chrome, load `ui-design`'s mobile browser behavior guidance and turn the
applicable contracts into assertions:

- Show and hide browser chrome; open and dismiss the keyboard; focus the lowest
  relevant input. Verify that content, errors, and required actions remain
  reachable, and closing the keyboard restores a usable layout.
- Check portrait and landscape where supported, including safe-area edges and
  fixed headers, bottom bars, sheets, and toasts. Test installed presentation
  separately when a PWA is a target.
- Tap, cancel a press, drag, and scroll on affected surfaces. Verify that feedback
  clears and actions commit only on valid activation; no gesture strands page
  scrolling or removes pinch zoom. Check nested scroll boundaries and short
  content as well as a long list.
- Exercise without hover and with available mixed input. Keep keyboard focus and
  full-value access usable. Confirm content remains selectable and copyable
  where users need it, and any replacement tap feedback remains visible.
- Check supported appearance changes and browser-chrome hints in the actual
  target mode. Inspect focus zoom and keyboard/input hints on relevant fields.

Record browser/version, device or simulator, orientation, display mode, and input
method. Emulation can establish layout and some input behavior but does not
establish every hardware/browser assertion. Use target hardware when available
for keyboard, chrome, safe areas, gestures, and touch feel; mark unavailable
checks `blocked` or `untested` rather than calling them passed. See [Chrome's
Device Mode limitations](https://developer.chrome.com/docs/devtools/device-mode#limitations).

## Evidence

Capture the states that establish the result: the initial condition, the outcome,
and any failure. Record the URL, viewport, and relevant console or network
evidence. Do not infer success from a screenshot when behavior required an
interaction.
