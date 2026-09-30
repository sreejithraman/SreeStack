# Set up automatic agent access

Read the skill's access gate before onboarding. Machine setup provisions shared
access; project setup consumes it. A machine-only request needs no project path
or URL and ends after runtime authentication is verified.

Vault creation, service-account grants, token storage and rotation, and host
configuration belong to explicitly requested machine administration. Project
agents use the provisioned account within its confirmed grants and maintain approved credential
references and login workflows. Missing access returns to machine setup; a
project testing request does not authorize provisioning or permission changes.

## Establish scope

For machine setup, identify the designated 1Password account and agent vault,
including whether to create a new vault. For project setup, also obtain the
project path, authorized destinations, and intended workflow; browser workflows
need approved login origins. Confirm which provisioning
operations are requested before authenticated administration. A setup request
does not authorize reading existing personal credentials. For enforced separation, read the
[access boundary](access-and-authentication.md#access-boundary).

Ensure the skill is available to the host from a stable source checkout, not a
temporary worktree. Confirm discovery in a new agent session and `op` on `PATH`.

## Provision access once

Use a custom vault containing only credentials intended for agent use, such as
test logins or sandbox API keys, and a service account
with `read_items` for that vault. Add `write_items` when the user requests
automatic item management, including deletion. Confirm its identity and grants; keep sharing and
vault creation outside the service account's scope.
Test users must also exist in the target application; a 1Password Login item
does not create an application account.

The agent can create the vault and service account through `op` when the scoped
administration is authorized. Check installed help first. Service-account
creation returns a token once: use a protected delivery path that saves it
without returning it in tool output or arguments. If that path is unavailable,
have the user use the creation wizard and save the token privately in 1Password,
outside the automation vault.
([Service-account creation](https://www.1password.dev/service-accounts/get-started))

Completion: the dedicated vault, service-account identity, and selected grants
are confirmed; the token has been saved privately. The vault can start empty;
add designated credentials when onboarding projects or tasks.

## Supply the runtime

Provision `OP_SERVICE_ACCOUNT_TOKEN` to the process that launches the agent, using
the host's secret facility or a user-controlled launcher. Keep the value out of
project files and agent chat. An export in another terminal does not update an
already-running GUI or remote agent. Restart or reconnect as the host requires,
then check variable presence from the agent's own command environment.
([Service accounts with CLI](https://www.1password.dev/service-accounts/use-with-1password-cli))

For T3 Code versions with provider Environment/Variables settings, use a dedicated
agent provider instance and mark the token sensitive. Verify the installed host's
storage behavior before choosing it; masked settings are not runtime isolation.
Other projects using that provider can inherit the same vault access.
([T3 provider environment UI](https://github.com/pingdotgg/t3code/blob/2cbc24fcae2b5649d7b60b68da72053a37fa82d5/apps/web/src/components/settings/ProviderInstanceCard.tsx),
[provider environment merge](https://github.com/pingdotgg/t3code/blob/2cbc24fcae2b5649d7b60b68da72053a37fa82d5/apps/server/src/provider/ProviderInstanceEnvironment.ts))

For Codex, also check the effective `shell_environment_policy`: filters and
inheritance can remove a token supplied to the parent process. Resolve the
specific policy conflict while preserving unrelated exclusions; keep real token
values out of `config.toml`.
([Command environment](https://learn.chatgpt.com/docs/config-file/config-advanced#shell-environment-policy))

Use [authentication](access-and-authentication.md) to resolve competing auth
routes and verify the designated identity. Completion: the intended agent's
command environment can authenticate as the scoped service account.

## Bootstrap each project

Prepare a mapping in the project's existing agent instructions, then obtain the
user's designation before treating it as automatic-access permission. For example:

```markdown
Automatic agent access:
- Service account ID: <confirmed ID>
- Vault ID: <confirmed ID>
- Login origin: https://staging.example.com
- Username: op://<vault ID>/<item ID>/username
- Password: op://<vault ID>/<item ID>/password
- Purpose: test login, dashboard, and logout.
```

Add identity-provider origins or OTP fields only when needed and authorized.
Prepare reference-only environment mappings and adapt the existing project login
runner or credential-aware browser integration using
[credential delivery](credential-delivery.md). Keep launch and test commands in
the project's existing scripts or verification instructions.

## Verify readiness

For project readiness, run the approved credential workflow from the same host,
provider, and project future agents will use. Confirm field retrieval inside the
consumer, the intended login or command result, and credential-free output and
artifacts.

Report **verified** only after this live check passes. Otherwise report the exact
remaining step: token provisioning, skill discovery, approved mapping, supported
delivery, or login verification. A missing delivery integration can still support
testing after user sign-in, but automatic login remains unverified. Record
nonsecret setup details and the verification result where future project agents
will find them.
