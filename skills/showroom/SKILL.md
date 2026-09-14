---
name: showroom
description: "Use after changing what a user sees to exercise the changed UI and return the smallest useful visual proof: one checked screenshot, a flow contact sheet with full-size frames, or motion proof, plus a checked live Tailscale URL for web."
---

# Showroom

After UI work, show what changed through the real interface. A build or test does
not replace visual proof. If the change has no user-visible UI, skip. If the UI
cannot run, name the blocker.

## Choose the proof

Use the smallest form that proves the change:

- **State:** one full-size screenshot when one state proves the change.
- **Flow:** ordered screenshots plus a labeled contact sheet when the change
  spans linked states. Capture meaningful checkpoints, not every input.
- **Motion:** a recording or timed frame sheet with elapsed-time labels when
  timing, transition, or animation quality matters.

Follow a format the user requests. Otherwise prefer one screenshot, and expand
only when the behavior needs more states. Use `manual-verify` first when risk or
scope needs broader workflow testing; Showroom presents its visual proof rather
than choosing a second test plan.

## Exercise and inspect

1. Reach each state through the interface a user would use. For a flow, keep the
   same device and viewport and order frames from start to result. Mix viewport
   sizes only for an intentional responsive comparison, and state why.
2. Save all run artifacts outside the repository unless the user asks for
   committed proof. Use numbered, state-based frame names such as
   `01-start.png` and `02-validation-error.png`.
3. Inspect every saved frame. Retake a wrong, cropped, loading, unstable, or
   private state. Check behavior with structured UI state where available;
   screenshots support visual claims, not hidden state or full accessibility.
4. For several frames, use an available image tool to build one labeled sheet.
   Keep its full-size source frames. Scan the sheet first, then inspect any dense
   or suspect frame at full size.

Prefer a compact sheet whose cells stay legible. Split a long flow at a natural
task boundary. Put labels outside the captured UI.

## Web

1. Start the repo's existing `dev` or `start` script bound to `127.0.0.1`. Keep
   that process running after this command returns.
2. Exercise and capture the changed state or flow in a browser.
3. Publish it with Tailscale Serve:
   `tailscale serve --bg --https=<port> http://127.0.0.1:<origin>`. Use a high
   Serve port; do not use 443, 8443, or 10000. Never Funnel.
4. Open the `https://…ts.net…` URL in a browser and confirm it loads. If no
   browser tool is available, check it with `curl` or another read-only request.
   If neither check works, name the blocker.

Return the visual proof and URL. Say that the URL needs this Mac awake and on
Tailscale. Include the exact `tailscale serve --https=<port> off` command and
the exact command or session action that stops the origin process this run
started.

When asked to take the page down, run those exact commands. Do not run `tailscale serve reset`. Do not kill by process name or port.

## iOS

1. Build for Simulator and launch the app.
2. Use one simulator. Create one only if none is usable. Leave every other
   device untouched.
3. Exercise and capture the changed state or flow in the running app, not the
   home screen.
4. Put the screenshot, contact sheet, or recording in the reply with its
   absolute path so the coding app renders it.

## Handoff

Show the screenshot, contact sheet, or recording in the reply. State the path
exercised, what the proof shows, and any failed or untested state. For any
contact or timed frame sheet, include the ordered absolute paths to every
full-size frame so the user or an AI reviewer can inspect a cell in detail.
