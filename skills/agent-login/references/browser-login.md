# Browser login

The `agent-login` command fills an existing local Chromium tab from an approved
account alias. Values are resolved and entered inside the command; its arguments
and JSON output contain no credential values. Codex and T3 agents can invoke the
same installed command and private account mappings.

## Onboard an account

Get the user's designation for the account, needed fields, project path,
authorized destinations including the login origin, purpose, role, and intended
workflow. Confirm the account exists in the application; a 1Password Login item
does not create an application account.

The command needs `op` on `PATH` and a runtime that authenticates as the scoped
service account. If it does not, name that block. When the user's setup request
also covers the machine, do only those prerequisites with
[machine setup](machine-setup.md), then resume here.

[Install the command](#install-the-command) if needed and
[add the alias](#configure-approved-aliases). Project instructions need only the
nonsecret alias, purpose, and browser workflow. `agent-login list` discovers
configured aliases without resolving values. Keep account IDs, references, and
tokens out of shared skill instructions.

Prove the login by [filling a tab](#fill-a-tab) in the host and environment
future agents will use. Confirm private field resolution, the intended
account and role, and owner control after the command disconnects. Mark
automatic login verified only after the actual form succeeds. Otherwise name
the missing prerequisite: approved mapping, runtime access, skill or command
discovery, supported adapter, or login verification. Record the nonsecret result
in the project's existing verification instructions when maintaining those is in
scope.

## Install the command

Install with Node 22 or newer and npm from the SreeStack repository root:

```sh
npm install --global --install-links ./skills/agent-login/scripts
agent-login --help
```

From a standalone skill folder, use that folder's absolute `scripts` path in
place of `./skills/agent-login/scripts`.

`--install-links` installs a copy that survives worktree removal. Linking the
skill does not configure 1Password or restrict shell access. The package uses
`playwright-core` without installing a browser. Use a host-supported CDP
endpoint or a dedicated Chromium automation profile; recent Chrome requires a
nondefault data directory for remote debugging.
([Chrome debugging profiles](https://developer.chrome.com/blog/remote-debugging-port),
[Playwright CDP](https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp))

## Configure approved aliases

Keep user-specific aliases in `~/.config/agents/accounts.json`, owned by the user
with mode `0600` inside a `0700` directory. Store only references, never
passwords or the service-account token. Preserve other accounts when adding an
alias:

```json
{
  "version": 1,
  "serviceAccountId": "<confirmed service-account ID>",
  "accounts": {
    "staging-buyer": {
      "origin": "https://staging.example.com",
      "allowedOrigins": ["https://auth.example.com"],
      "username": "op://<vault ID>/<item ID>/username",
      "password": "op://<vault ID>/<item ID>/password",
      "selectors": {
        "username": "input[autocomplete='username']",
        "password": "input[autocomplete='current-password']",
        "submit": "button[type='submit']"
      },
      "purpose": "Test login and dashboard verification",
      "role": "BUYER"
    }
  }
}
```

Replace placeholders with confirmed 26-character IDs and selectors for the
approved form. The login origin is always allowed. `allowedOrigins` adds the
exact origins needed during entry and submission, including redirects and
identity providers. Add only the destinations and fields the task needs. The
command supports username and password, not OTP entry or other providers. Input
fields must be empty, unique, and in the main document.

## Fill a tab

1. Run `agent-login list`. Match the alias, destination, purpose, and role to
   the task's [approved scope](access.md#who-may-use-which-credential).
2. Follow the host's browser routing. Get its documented loopback CDP endpoint
   and run `agent-login tabs --cdp http://127.0.0.1:PORT`. Choose the exact
   target; origins alone cannot tell two tabs apart. CDP target IDs differ from
   host tab IDs. The command attaches to existing tabs and never launches a
   browser. Native T3 preview and Codex browser target IDs are not CDP
   endpoints, and other browser engines are unsupported.
3. Navigate that tab to the mapped origin and show its password form. Confirm
   the mapped fields are empty and uniquely identified. Keep other automation
   idle during filling. Run:

   ```sh
   agent-login fill ALIAS --cdp http://127.0.0.1:PORT --target TARGET_ID --submit
   ```

   Omit `--submit` to fill only. The command checks the service-account
   identity, origin, and bound fields before entering values.
4. Read the result. `filled` and `submitted` report delivery. `blockedRequests`
   counts unapproved background requests blocked during delivery. The command
   disconnects and leaves the tab with its original owner.

## Limits and recovery

The browser still receives plaintext inputs. The command cannot redact host
snapshots, traces, or recordings; pause captures when values must stay out of
them. Use a trusted test site and a dedicated browser profile, with its
debugging endpoint reachable only locally. The command is a private consumer,
not an isolation boundary against same-user processes or page scripts.
Service-worker-controlled pages are unsupported. The destination guard covers
interceptable requests from the selected page during this bounded operation.
Popups, workers, existing WebSockets, and scripts that send retained values
later are outside that scope.

On an error, use its controlled `code` and `inputMayHaveOccurred` flag. Inspect
the original tab and authentication state before retrying; a failed submission
may already have reached an allowed destination. Cleanup clears only unchanged
values in the original fields. A crash can leave a target lease in
`.agent-login-leases` beside the account file. Each lease records its
`targetId`, `pid`, and `startedAt`: identify the exact target, confirm the
recorded process has stopped and the tab is idle, then remove only that file.
Preserve other leases. Do not broaden `allowedOrigins` to silence a denial;
confirm the required destination and authorization first.

## Development checks

From the SreeStack repository root, install dependencies with
`npm ci --prefix skills/agent-login/scripts` and run
`TEST_BROWSER_EXECUTABLE=/path/to/chromium npm test --prefix skills/agent-login/scripts`.
Tests use dummy credentials and a dedicated temporary browser profile.
