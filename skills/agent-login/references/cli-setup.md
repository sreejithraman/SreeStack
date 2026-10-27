# Set up the agent-login command

## Prerequisites and supported sessions

1Password is a provider reference within this skill. Its
[access and setup guide](1password.md) covers scoped
provider access, item management, and command/API secrets. It requires `op` on
`PATH`, a dedicated agent vault, a scoped service account, runtime token
provisioning, and an approved credential mapping. Linking the skill does not
configure 1Password or restrict shell access.

Codex runtimes on one Mac can share a private environment file while keeping
separate Codex homes. A general file such as `~/.config/agents/shared.env` can hold
1Password variables alongside other credentials and configuration intended for
both runtimes. The [runtime setup](runtime-provisioning.md)
covers that option and host-specific verification.

The bundled `agent-login` command currently supports only 1Password credentials
and existing local Chromium tabs exposed through a loopback CDP endpoint.
Both Codex and T3 agents can invoke the same
installed command and private account mappings. Native T3/Codex browser adapters
and simulator delivery remain separate work; their tab IDs cannot be passed to
this adapter. The command disconnects after filling, leaving the tab with its
original owner for verification. It does not redact browser snapshots.

## Install the command

Install with Node 22 or newer and npm from the SreeStack repository root:

```sh
npm install --global --install-links ./skills/agent-login/scripts
agent-login --help
```

When using a standalone skill folder, run the same installation command with
that folder's absolute `scripts` path in place of `./skills/agent-login/scripts`.

`--install-links` installs a copy that survives worktree removal. The package
uses `playwright-core` without installing a browser. Use a host-supported CDP
endpoint or a dedicated Chromium automation profile; recent Chrome requires a
nondefault data directory for remote debugging.
([Chrome debugging profiles](https://developer.chrome.com/blog/remote-debugging-port),
[Playwright CDP](https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp))

## Configure approved aliases

Keep user-specific aliases in `~/.config/agents/accounts.json`, owned by the user
with mode `0600` inside a `0700` directory. Store only references, never passwords
or the service-account token. Preserve other accounts when adding an alias:

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
approved form. The login origin is always allowed; `allowedOrigins` adds exact
origins needed during credential entry and submission, including redirects and
identity providers. Remote origins require HTTPS; explicitly approved loopback
test origins can use HTTP. Input fields must be empty, unique, and in the main
document. See the [browser procedure](browser-login.md)
for selecting a target, checking outcomes, and recovering from errors.

## Development checks

From the SreeStack repository root, install dependencies with `npm ci --prefix skills/agent-login/scripts`
and run `TEST_BROWSER_EXECUTABLE=/path/to/chromium npm test --prefix skills/agent-login/scripts`.
Tests use dummy credentials and a dedicated temporary browser profile.
