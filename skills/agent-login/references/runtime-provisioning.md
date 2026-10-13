# Provision the agent runtime

Use this reference during authorized machine setup, or to diagnose a runtime
that prompts for Touch ID during automatic access. Project testing consumes
existing setup; it does not authorize creating tokens or changing vault grants.

## Identify the affected process

Check `OP_SERVICE_ACCOUNT_TOKEN` presence inside the agent's command environment,
printing only a boolean. A working T3 session does not establish access in the
Codex desktop app. GUI apps may not inherit terminal exports, and existing
processes keep their earlier environment.

Service-account authentication needs the token and no `op signin`.
A desktop authorization prompt on this path is a provisioning failure;
repair the affected runtime rather than asking a remote user to touch the Mac.
([CLI service-account authentication](https://www.1password.dev/service-accounts/use-with-1password-cli))

## Choose the token source

Use the host's secret facility when available. In T3 versions with provider
Environment/Variables settings, a sensitive `OP_SERVICE_ACCOUNT_TOKEN` entry
supplies the provider process. The value is literal: entering a filename or shell
expression does not load an environment file. Check installed storage behavior;
masking is not isolation, and other projects using that provider inherit access.
([Environment UI](https://github.com/pingdotgg/t3code/blob/2cbc24fcae2b5649d7b60b68da72053a37fa82d5/apps/web/src/components/settings/ProviderInstanceCard.tsx),
[provider environment merge](https://github.com/pingdotgg/t3code/blob/2cbc24fcae2b5649d7b60b68da72053a37fa82d5/apps/server/src/provider/ProviderInstanceEnvironment.ts))

For a shared local file, Codex supports `~/.codex/.env` followed by an app restart.
In a live check with Codex CLI 0.160.0, both the desktop app's bundled CLI and
T3's installed CLI also loaded `.env` from their respective `CODEX_HOME`,
including symlinks. Recheck installed versions and each host; this does not
establish environment-file support for other T3 providers.
([Desktop environment setup](https://learn.chatgpt.com/docs/amazon-bedrock#desktop-app-and-ide-extension))

A reusable layout is:

```text
~/.config/agents/shared.env   # canonical private agent environment
~/.codex/.env                # symlink to that file
<T3 Codex home>/.env         # symlink to that file
```

Discover the effective homes; keep their configs and sessions separate. The
shared file can contain credentials and configuration intended for every linked
agent runtime; 1Password is one section. When provisioning or rotating 1Password,
update only its variables and preserve other entries. Keep variables specific to
one runtime in that host's separate configuration. Treat the shared file as
plaintext secrets: keep the parent directory owner-only (`0700`)
and the canonical file owner-readable/writable (`0600`), outside repositories.
Provision `OP_SERVICE_ACCOUNT_TOKEN` and `OP_BIOMETRIC_UNLOCK_ENABLED=false`
inside the transfer process, using an existing authorized environment or private
source. Capture outputs and exceptions; neither file contents nor secret values
belong in a tool argument. Use valid dotenv encoding, not executable shell code.
Have the user enter the token privately if no protected transfer path exists.
The biometric setting disables desktop integration for automatic access;
approved personal access selects its own invocation environment.
([Desktop integration toggle](https://www.1password.dev/cli/app-integration#optional-set-the-biometric-unlock-environment-variable))

Inspect existing `.env` paths and symlink targets before changing them. Preserve
unrelated settings; reconcile existing files privately rather than overwriting
them. To migrate a token-only file, verify its replacement privately, preserve
recoverability during migration, and remove the old destination before creating
the link. Account for any retained secret copies during rotation.

When an existing `.env` needs runtime-specific settings, retain it. Use a
host-supported launcher to load the shared environment file if available; otherwise
retain that host's separate provisioning and report shared-file setup as
incomplete. Moving all runtime settings into the shared file would supply them
to every linked runtime. Create links only at absent destinations, and keep the
canonical path stable through worktree cleanup.

An existing provider environment value can compete with file loading. Retain a
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
   identity with the designated identity. Check the exit status
   before parsing JSON; retry an unexplained empty failure once in a fresh
   subprocess, then diagnose a persistent failure from privately captured errors.
   Output only the identity comparison result. Confirm
   `OP_BIOMETRIC_UNLOCK_ENABLED=false` in the subprocess environment and successful
   authentication without a desktop authorization prompt.
2. Restart the affected GUI/provider as needed without interrupting other work,
   then repeat the identity check from a fresh agent session. An app-server
   subprocess probe establishes runtime loading, not a completed GUI restart.

Record the runtime/version, effective home, token source path or setting name,
expected identity, and completed checks without secret values. Report partial
coverage explicitly. Machine authentication ends here.
