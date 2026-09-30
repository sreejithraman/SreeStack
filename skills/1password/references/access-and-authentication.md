# Authentication

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
  authentication out of that invocation. After the skill's access gate,
  `op whoami --account <approved-account>` verifies identity and may prompt the
  user to authorize through 1Password.
  ([Desktop integration](https://www.1password.dev/cli/app-integration))
- **Interactive sign-in:** let the user handle account-password, Secret Key, MFA,
  and native approval prompts directly. Keep session exports out of agent output.

If authentication fails, report the missing setup. For desktop IPC failures,
have the user check the running app and CLI integration, then retry after the
issue is addressed. Have the user provision missing tokens; account provisioning
and permission changes require an explicitly requested setup task.

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
unrestricted agent. For onboarding, use [setup](setup.md).
