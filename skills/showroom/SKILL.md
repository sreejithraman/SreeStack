---
name: showroom
description: "Use after changing what a user sees to exercise the changed UI and return the smallest useful visual proof: one checked screenshot, a flow contact sheet with full-size frames, or motion proof. For web, return the checked preview or deployment URL and disclose access limits."
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
only when the behavior needs more states. Use `verify` first when risk or
scope needs broader workflow testing; Showroom presents its visual proof rather
than choosing a second test plan.

Use the same deployment or device chosen for the task or its verification run.
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

Exercise and capture the selected deployment or preview. When the task and its
verification run leave the target open, use the project's local server through
T3's collaborative preview. Follow [web verification](../verify/references/web.md)
for host browser selection and recovery; those rules also apply when broader
Verify coverage is unnecessary.

Return the checked URL and the visual proof. State login, network, or runtime
requirements. A loopback URL or a check from this machine does not establish
access from another device. If the user asks for access away from home, use an
existing deployment or supported app sharing first; for tailnet sharing, read
[web sharing](references/web-sharing.md). Disclose unverified remote-client
access. Keep proof on the requested target and report a missing changed state
or access gap.

Keep a preview-owned server running when the user needs to inspect it. Record
its process identity, ownership, and exact stop action; reused services retain
their existing owner. Stop a local origin only when this preview started it and
its recorded identity still matches. Tailnet teardown follows
[web sharing](references/web-sharing.md), checking mapping and origin separately.

## iOS

Use the requested iOS target, or the one already used by the verification run. When
neither has selected a target, default to Simulator if it supports the flow;
otherwise use a suitable physical device. Build and launch on that target when
needed. For Simulator, use one; create one only if none is usable. Leave every
other device untouched.

Follow [iOS verification](../verify/references/ios.md) for host device routing
and driving, including the T3 Device panel and returned session flags.

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
