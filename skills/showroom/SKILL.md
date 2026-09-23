---
name: showroom
description: "Use after changing what a user sees to exercise the changed UI and return the smallest useful visual proof: one checked screenshot, a flow contact sheet with full-size frames, or motion proof. For web, also provide a checked URL for access away from home and disclose unverified remote access."
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

Use the same deployment or device chosen for the task or by `manual-verify`.
Reuse checked captures from that run when they show the change; do not switch
targets just to make proof easier.

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

Exercise and capture the changed state or flow at the selected target. When
neither the task nor `manual-verify` selects a web target, use a local preview.
Return a checked URL for access away from home.

For a deployed target, confirm that its URL shows the changed UI. State any
login or network requirements. If the change is absent or remote access cannot
be established, name that gap; keep proof on the selected target rather than
switching to a local build.

For a local preview:

1. Start or locate the repo's existing `dev` or `start` server bound to
   `127.0.0.1`. Record its process identity, including command and start time or
   controlled session, whether this preview started it or reused it.
2. Check the current Serve configuration. Choose an unused high port other
   than 443, 8443, or 10000, then publish with Tailscale Serve:
   `tailscale serve --bg --https=<port> http://127.0.0.1:<origin>`. Never Funnel.
   Keep any origin process started for this preview running after the command
   returns.
3. Exercise and capture the changed route or state through the returned URL.
   If no browser tool is available, check that route with `curl` or another
   read-only request and name the remaining remote visual-proof gap.

When available, check the URL from an off-home client too (on the tailnet for
Tailscale Serve). Otherwise report remote-client access as unverified; a check
from this Mac alone does not establish it.

Return the URL and say that access requires this Mac awake and on Tailscale,
and the user's device on the tailnet. Include the Serve mapping and the exact
`tailscale serve --https=<port> off` command. If this preview started the origin,
include its exact stop command or session action too; otherwise say the reused
origin will remain running after take-down.

When asked to take the preview down, compare the current Serve mapping and
origin process identity with the recorded ones. Stop Serve if its mapping still
belongs to this preview, even if the origin has changed. Stop the origin only
if this preview started it and its identity still matches. Report any mismatch
or uncertainty and leave that service running. Do not run
`tailscale serve reset`. Do not kill by process name or port.

## iOS

Use the requested iOS target, or the one already used by `manual-verify`. When
neither has selected a target, default to Simulator if it supports the flow;
otherwise use a suitable physical device. Build and launch on that target when
needed. For Simulator, use one; create one only if none is usable. Leave every
other device untouched.

Exercise and capture the changed state or flow in the running app, not the home
screen. If the chosen target cannot be exercised or captured with available
tooling, name the proof gap rather than substituting another target. Put the
screenshot, contact sheet, or recording in the reply with its absolute path so
the coding app renders it.

## Handoff

Show the screenshot, contact sheet, or recording in the reply. State the path
exercised, what the proof shows, and any failed or untested state. For any
contact or timed frame sheet, include the ordered absolute paths to every
full-size frame so the user or an AI reviewer can inspect a cell in detail.
