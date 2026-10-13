# Fill an existing browser tab

Use `agent-login` when an approved account alias and an existing local Chromium
CDP session are available. Installation and the private mapping format are in
[README](../../../README.md#agent-login).

1. Run `agent-login list`. Match the alias, destination, purpose, and role to the
   user's approved task. A local mapping records authorization; creating a
   mapping does not grant it. Resolve missing scope through the [1Password access gate](1password.md#access).
2. Follow the host's browser routing. Obtain its documented loopback CDP endpoint
   and run `agent-login tabs --cdp http://127.0.0.1:PORT`. Choose the exact target;
   origins alone cannot distinguish two tabs. CDP target IDs differ from host
   tab IDs. The command attaches to existing tabs and never launches a browser.
3. Navigate that tab to the mapped origin and display its password form. Confirm
   the mapped fields are empty and uniquely identified. Keep other automation
   idle during filling. Run:

   ```sh
   agent-login fill ALIAS --cdp http://127.0.0.1:PORT --target TARGET_ID --submit
   ```

   Omit `--submit` for filling only. Values are resolved and entered inside the
   command; arguments and JSON output contain no credential values. It checks
   the service-account identity, origin, and bound fields before entering them.
4. Treat `filled` and `submitted` as delivery results. `blockedRequests` counts
   unapproved background requests that were blocked during delivery. Use the original browser
   owner to verify authenticated state, intended account/role, and the requested
   workflow. The command disconnects and leaves the existing tab open.

Native T3 preview and Codex browser target IDs are not CDP endpoints. Their
credential-fill adapters, other browser engines, and simulator/computer-use
delivery are not implemented. If the required host lacks a documented endpoint,
report that missing adapter and continue after user sign-in.

## Limits and recovery

The browser still receives plaintext inputs. The command cannot redact host
snapshots, traces, or recordings. Apply the user's capture policy; pause captures
when values must stay out of them. Use a trusted test site and dedicated browser
profile, with its debugging endpoint accessible only locally. The helper is a
private consumer, not an isolation boundary against same-user processes or page
scripts. Service-worker-controlled pages are unsupported.
The destination guard covers interceptable requests from the selected page
during this bounded operation. Popups, workers, existing WebSockets, and scripts
that send retained values later are outside that scope.

On an error, use its controlled `code` and `inputMayHaveOccurred` flag. Inspect
the original tab and authentication state before retrying; a failed submission
may already have reached an allowed destination. Cleanup clears only unchanged
values in the original fields. A crash can leave a target lease in
`.agent-login-leases` beside the account file. Each lease records its `targetId`,
`pid`, and `startedAt`: identify the exact target, confirm the recorded process
has stopped and the tab is idle, then remove only that file. Preserve other leases.
Do not broaden `allowedOrigins` to silence a denial; confirm the required
destination and authorization first.
