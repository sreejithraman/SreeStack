# macOS Verification

Build and launch the intended app configuration. Record the macOS version, app
build or revision, and any fixture or account state that affects the check. Use
the host's native app or computer-use tooling, with accessibility inspection when
it is available.

## Observe and interact

- Confirm that the expected app and window are active before interacting. Inspect
  the rendered interface and accessibility hierarchy when the tooling exposes it.
- Target controls by accessibility role, label, or identifier when supported.
  With rendered-state tooling, recapture after each action and report semantic or
  accessibility coverage as untested.
- Exercise menus, keyboard shortcuts, focus, window resizing, sheets, popovers,
  multiple windows, and full-screen behavior when they belong to the selected
  workflow. Give multiple windows distinct observable states, confirm which one
  is active, then inspect both the active window's expected change and the
  inactive window's unchanged state.
- For open, save, import, export, or drag-and-drop workflows, use disposable
  copies while preserving the source fixtures. Record the paths and expected
  changes. To verify an explicit save action, capture an independent on-disk
  baseline and the document's dirty state immediately before invoking it, then
  observe the command-specific state transition and inspect the on-disk result.
  If autosave removes the dirty precondition before the command or makes
  attribution impossible, report persistence separately and mark the save-action
  assertion `blocked`. Mark it `untested` when the command was not exercised. If
  the document was dirty, the command was exercised, and neither the expected
  transition nor persisted output appears after settling, mark it `failed`.
  Closing and reopening the recorded path can provide additional persistence
  evidence. Record the persisted value observed.
- Treat permission prompts and other system UI as part of the workflow. Record
  any permission state that a later run would need to reproduce. A controlled
  denial requested by the workflow is a test precondition: keep it denied unless
  the task authorizes changing it, then check the app's error or fallback behavior
  and confirm that it did not produce restricted output.
- Capture application logs or crash reports when the app exits, hangs, or behaves
  differently from the visible state.

When the verifier cannot establish or observe a required state because hardware,
services, entitlements, permissions, or system configuration are unavailable,
exercise the supported portion and mark only the affected assertions blocked.

## Evidence

Record the macOS version, app build or revision, workflow states, affected and
unaffected windows, and relevant screenshots, inspected output files, or logs. A
successful build proves that the app compiled; the interaction and resulting
state prove whether the workflow worked.
