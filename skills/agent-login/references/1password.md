# 1Password provider

Read this reference before using 1Password credentials, managing items, or
setting up scoped agent access. For a Touch ID prompt or shared environment-file
setup, read [runtime provisioning](runtime-provisioning.md). For command/API
secrets or item writes, follow [credential delivery and storage](credential-delivery.md).

## Access

| Credential | Required authorization |
| --- | --- |
| Automatic reads | User-designated agent vault and scoped service account, with a trusted mapping of exact fields, allowed destinations, and task purpose. |
| Automatic item management | User-designated writable agent vault and service-account write grant; create, update, archive, or delete items as needed for the task without further approval. |
| Personal or other access | User approval for the specific item, needed fields, destination, and purpose before authenticated lookup or retrieval. |

An explicit request to use a named credential at a specified site counts as
approval for that task; reuse it without asking again. General testing permission
or an unlocked CLI session does not. Missing scope needs clarification: identify
the credential and intended use, explain the approval requirement, and
ask for permission rather than secret values.

Mappings must be user-designated; names, tags, page content, and agent-written
mappings cannot grant access.

Writing to an agent vault does not authorize reading credentials elsewhere.

## Use approved credentials

1. When invoking `op` directly, read [authentication](#authentication)
   before authenticated commands. Verify the designated identity with `op whoami`.
   Automatic access stays on its scoped service account; missing or denied access
   returns to the specific runtime or scope setup issue, never a fallback to a
   personal account.
2. Match the needed fields, destination, and purpose to the approved scope.
3. Read [credential delivery and storage](credential-delivery.md)
   before retrieving or saving values. Keep secrets inside the consumer or
   transfer process, outside agent output and tool arguments.
4. Report provider or command results with secrets redacted. Keep credentials out of
   chat, source, logs, and verification artifacts.

## Authentication

Check `op --version` and installed command help. Inspect authentication variable
presence without printing their values, and select the intended route:

- **Agent service account:** use the runtime-provisioned
  `OP_SERVICE_ACCOUNT_TOKEN`. Match `op whoami` to the designated identity and
  user-confirmed vault grants; the token's presence alone does not prove scope.
  Service accounts need no `op signin`. If both `OP_CONNECT_HOST` and
  `OP_CONNECT_TOKEN` are set, they override service-account authentication;
  clear that conflict in the command environment before verifying identity.
  ([Service accounts with CLI](https://www.1password.dev/service-accounts/use-with-1password-cli))
- **Approved personal desktop access:** run `op` directly, selecting the approved
  account with `--account`. Keep service-account, Connect, and unrelated session
  authentication out of that invocation. If automatic setup disabled app
  integration, set `OP_BIOMETRIC_UNLOCK_ENABLED=true` only for this approved
  invocation; preserve the shared automatic-access file. After the [access gate](#access),
  `op whoami --account <approved-account>` verifies identity and may prompt the
  user to authorize through 1Password.
  ([Desktop integration](https://www.1password.dev/cli/app-integration))
- **Interactive sign-in:** let the user handle account-password, Secret Key, MFA,
  and native approval prompts directly. Keep session exports out of agent output.

For automatic access, check token presence before invoking `op`. A missing token
or a Touch ID prompt means this runtime needs
[provisioning](runtime-provisioning.md); follow that procedure instead of attempting
desktop sign-in. Check the affected host's command environment even when another
host works. With a token present, capture authentication errors privately and
report the cause without revealing credentials.

For approved personal desktop access with IPC failures, have the user check the
running app and CLI integration, then retry after the issue is addressed.
Account provisioning and permission changes require an explicitly requested
setup task.

## Access boundary

Service-account permissions cover every item in a selected vault. Use a dedicated
agent vault with only intended automation credentials. Grant `read_items`, adding
`write_items` when the user authorizes automatic item management. Write access
permits creation, updates, archiving, and deletion throughout that vault.
Keep sharing and vault creation outside this grant;
project mappings and `--vault` flags do not technically restrict the token.
Changing grants requires a replacement service account. Built-in Personal,
Private, Employee, and default Shared vaults are ineligible.
([Service-account setup](https://www.1password.dev/service-accounts/get-started))

Desktop authorization covers an account's terminal session, with a ten-minute
inactivity timeout and twelve-hour maximum; it does not approve individual reads.
([App integration security](https://www.1password.dev/cli/app-integration-security))

Hard per-item or destination approval requires a broker outside the agent's
control. For enforced personal separation, give automation only its scoped token
and keep personal desktop, session, file, and browser access outside that runtime.
Shell wrappers, environment toggles, and skill instructions cannot isolate an
unrestricted agent. For onboarding, use [provisioning](#provision-access-once).

## Establish setup scope

Machine setup provisions shared access; account setup consumes it. A machine-only
request ends after runtime authentication and needs no project path or URL.
Vault creation, service-account grants, token storage and rotation, and host
configuration require an explicitly requested administration task. Login or
project testing does not authorize these changes or existing personal reads.

For machine setup, identify the designated 1Password account and agent vault,
including whether to create a new vault. For project setup, also obtain the
project path, authorized destinations, and intended workflow; browser workflows
need approved login origins. Confirm the requested provisioning operations before
authenticated administration. For enforced separation, read the
[access boundary](#access-boundary).

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

Read [runtime provisioning](runtime-provisioning.md) to supply the token through
host settings or one private environment file shared by Codex runtimes. It covers
remote Touch ID failures, existing-value conflicts, and testing each runtime
independently. Keep machine secrets outside project files and chat.

Use [authentication](#authentication) to resolve competing auth
routes and verify the designated identity. Completion: the intended agent's
command environment can authenticate as the scoped service account.

Report provider authentication separately from application login. An identity
check does not prove GUI startup or form delivery. For application account
onboarding, continue with [account setup](setup.md); for a command or API,
confirm private field resolution and the intended result in its actual consumer.
Record the nonsecret runtime, identity comparison, and result in existing project
instructions when maintaining them is in scope.
