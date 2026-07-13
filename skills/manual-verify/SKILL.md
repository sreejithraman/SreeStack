---
name: manual-verify
description: Manual verify. Use when changed behavior can be exercised through browser, CLI, API, file, or workflow.
---

# Manual Verify

Manual verification exercises changed behavior through the closest real surface and reports evidence, not inference from the code diff.

## Steps

1. Pick the surface.

   Choose the closest real surface: browser, CLI command, API endpoint, generated file, or user/operator workflow.

   Prefer `browser:control-in-app-browser` for browser verification, including local development servers, file-backed previews, public pages, visual checks, and Developer mode/CDP inspection.

   Developer mode/CDP works in the built-in browser. Use it there for console output, network traffic, DOM, applied styles, page state, performance traces, or live-browser diagnostics.

   Use `chrome:control-chrome` only when the task explicitly asks for Chrome or needs an existing Chrome tab, the user's regular Chrome profile, logged-in Chrome session, or Chrome extension behavior.

   Use CLI/API/file/workflow verification for non-browser surfaces.

   If verification is blocked, name the missing runnable target, route, credentials, fixture data, environment, or other concrete blocker.

2. Exercise the behavior.

   Drive the changed behavior like a user or operator would: navigate, click, type, submit, inspect visible state, call the endpoint, run the command, or open the generated file.

   Exercise the behavior through the chosen surface rather than inferring from implementation.

3. Capture evidence.

   Report enough evidence that another agent can tell whether the change worked, failed, or was blocked.

   Include:

   - surface used: URL, command, endpoint, file, or workflow
   - browser surface used, if applicable: built-in browser, built-in browser with Developer mode/CDP, or Chrome
   - actions taken
   - expected result
   - observed result
   - screenshot or visible-state evidence when using a browser
   - blocker, when verification is blocked
