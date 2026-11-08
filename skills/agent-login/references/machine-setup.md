# Machine setup

Use this for a requested machine setup: a dedicated vault and service account,
the token in each agent runtime, or a runtime that prompts for Touch ID during
automatic access. Machine setup provisions shared access; account onboarding
consumes it. A machine-only request needs no project path or URL.

## Settle the scope

Identify the designated 1Password account and agent vault, including whether to
create a new vault. Confirm the requested provisioning operations before any
authenticated administration. For enforced separation, read the
[access boundary](access.md#access-boundary).

Make the skill available to each host from a stable source checkout, not a
temporary worktree. Confirm discovery in a new agent session and `op` on `PATH`.

## Create the vault and service account

Create the dedicated vault and service account the
[access boundary](access.md#access-boundary) describes, with the grants the user
requested. Typical vault contents are test logins or sandbox API keys.

The agent can create the vault and service account with `op` when that
administration is authorized. Check installed help first. Service-account
creation returns the token once: save it through a protected path that keeps it
out of tool output and arguments. If no such path exists, have the user run the
creation wizard and save the token privately in 1Password, outside the
automation vault.
([Service-account creation](https://www.1password.dev/service-accounts/get-started))

This step is done when the vault, service-account identity, and selected grants
are confirmed and the token is saved privately. The vault can start empty.

## Find the affected runtime

Check `OP_SERVICE_ACCOUNT_TOKEN` presence inside the agent's command environment,
printing only a boolean. A working T3 session does not establish access in the
Codex desktop app. GUI apps may not inherit terminal exports, and existing
processes keep their earlier environment.

A desktop authorization prompt on the
[service-account route](access.md#authenticate) is a provisioning failure.
Repair the affected runtime instead of asking a remote user to touch the Mac.

## Choose the token source

Use the host's secret facility when available. In T3 versions with provider
Environment/Variables settings, a sensitive `OP_SERVICE_ACCOUNT_TOKEN` entry
supplies the provider process. The value is literal: entering a filename or shell
expression does not load an environment file. Check installed storage behavior;
masking is not isolation, and other projects using that provider inherit access.
([Environment UI](https://github.com/pingdotgg/t3code/blob/2cbc24fcae2b5649d7b60b68da72053a37fa82d5/apps/web/src/components/settings/ProviderInstanceCard.tsx),
[provider environment merge](https://github.com/pingdotgg/t3code/blob/2cbc24fcae2b5649d7b60b68da72053a37fa82d5/apps/server/src/provider/ProviderInstanceEnvironment.ts))

For a shared local file, Codex loads `.env` from its `CODEX_HOME` (default
`~/.codex`) at startup, following symlinks. It ignores `CODEX_*` keys in that
file. Restart the app or CLI after a change; a running process keeps its earlier
environment. This does not establish environment-file support for other T3
providers.
([Desktop environment setup](https://learn.chatgpt.com/docs/amazon-bedrock#desktop-app-and-ide-extension),
[Codex `.env` loading](https://github.com/openai/codex/blob/d960b366941bf062adb4d43111e81b64507e8879/codex-rs/arg0/src/lib.rs#L272-L284))

A reusable layout is:

```text
~/.config/agents/shared.env   # canonical private agent environment
~/.codex/.env                # symlink to that file
<T3 Codex home>/.env         # symlink to that file
```

Discover the effective homes; keep their configs and sessions separate. The
shared file can hold credentials and configuration meant for every linked agent
runtime; 1Password is one section. When provisioning or rotating 1Password,
update only its variables and preserve other entries. Keep variables specific to
one runtime in that host's separate configuration. Treat the shared file as
plaintext secrets: keep the parent directory owner-only (`0700`) and the
canonical file owner-readable/writable (`0600`), outside repositories.

Provision `OP_SERVICE_ACCOUNT_TOKEN` and `OP_BIOMETRIC_UNLOCK_ENABLED=false`
inside the transfer process, using an existing authorized environment or private
source. Capture outputs and exceptions; neither file contents nor secret values
belong in a tool argument. Use valid dotenv encoding, not executable shell code.
Reading the token from the user's personal vault is personal access: get the
user's approval for that item under [access](access.md#who-may-use-which-credential),
or have the user enter the token privately. Have the user enter it privately
too if no protected transfer path exists.
The biometric setting disables desktop integration for automatic access;
approved personal access sets its own invocation environment.
([Desktop integration toggle](https://www.1password.dev/cli/app-integration#optional-set-the-biometric-unlock-environment-variable))

Inspect existing `.env` paths and symlink targets before changing them. Preserve
unrelated settings; reconcile existing files privately instead of overwriting
them. To migrate a token-only file, verify its replacement privately, keep it
recoverable during migration, and remove the old destination before creating
the link. Account for any retained secret copies during rotation.

When an existing `.env` needs runtime-specific settings, keep it. Use a
host-supported launcher to load the shared environment file if available;
otherwise keep that host's separate provisioning and report shared-file setup as
incomplete. Moving all runtime settings into the shared file would supply them
to every linked runtime. Create links only at absent destinations, and keep the
canonical path stable through worktree cleanup.

An existing provider environment value can compete with file loading. Keep a
working configuration during the trial. Test the file with the parent token
removed, then reconcile duplicate entries through the host's supported settings
interface before claiming one active source. Rotation must account for remaining
copies and already-running processes.

For Codex, inspect the effective `shell_environment_policy` if a parent token
does not reach commands. Resolve the specific inheritance or filter conflict
while preserving unrelated settings; keep token values out of `config.toml`.
([Command environment](https://learn.chatgpt.com/docs/config-file/config-advanced#shell-environment-policy))

## Verify each runtime

For **shared-file provisioning**, before transferring a token, use a harmless
marker in an isolated Codex home to test `.env` loading into command subprocesses.
Then start each installed runtime with `OP_SERVICE_ACCOUNT_TOKEN`, Connect
variables, and `OP_SESSION_*` removed from its parent environment, using its
actual Codex home. Check token presence without printing the value; inherited
access can otherwise hide a broken file setup.

For **every provisioning source**:

1. From the affected runtime's command environment, check token presence and
   capture `op whoami --format=json` privately. Compare its service-account
   identity with the designated identity. Check the exit status before parsing
   JSON; retry an unexplained empty failure once in a fresh subprocess, then
   diagnose a persistent failure from privately captured errors. Output only the
   identity comparison result. Confirm `OP_BIOMETRIC_UNLOCK_ENABLED=false` in
   the subprocess environment and successful authentication without a desktop
   authorization prompt.
2. Restart the affected GUI/provider as needed without interrupting other work,
   then repeat the identity check from a fresh agent session. An app-server
   subprocess probe establishes runtime loading, not a completed GUI restart.

Record the runtime/version, effective home, token source path or setting name,
expected identity, and completed checks without secret values, in existing
project instructions when maintaining them is in scope. Report partial coverage
explicitly. Machine setup ends here.
