# Authenticated verification

Use this reference when selected workflows require login or authenticated
commands. Verify owns product assertions and the verdict; agent-login owns
application sign-in and credential use, with provider mechanics in its references.

## Reuse approved setup

Identify the intended environment, designated test account, required role, and
allowed destinations from the session and project instructions. Reuse standing
authorization within that scope. Ask for missing account or destination details,
not credential values. A shared agent environment supplies configuration; its
presence does not authorize using every credential it contains.

An existing or user-established session can support authenticated feature checks.
Confirm its intended account and role without exposing private details. Record
how the session was established; it does not prove automatic login. Preserve
reused sessions unless the selected checks require and authorize changing them.

For application sign-in, use [agent-login](../../agent-login/SKILL.md).
For command or API credentials, follow agent-login’s provider guidance;
other providers need an approved private delivery procedure.

## Establish the login path

Check three separate prerequisites before retrieving values:

- **Account scope:** the designated account and destination are authorized for
  this workflow, with suitable test data and role.
- **Credential access:** the actual agent runtime can authenticate to the
  credential provider, and approved references identify the needed fields.
- **Credential delivery:** the selected browser, computer-use, device, or command
  consumer can use those fields without secret values entering chat, tool
  arguments, output, or retained artifacts.

Honor host browser and device routing. Delivery must target the actual tab or
device session and drive the selected public login flow. Follow agent-login for
UI entry and command credential delivery before resolving fields.

If a prerequisite is missing, identify whether account scope, runtime access,
or secure delivery is blocked. Give the exact setup or user-sign-in step needed
and continue independent checks.

## Assert and retain proof

For login assertions, begin from the recipe's signed-out state, drive the actual
public login form or command, and observe the expected authenticated state and
role. Injecting a session through an internal API does not prove a login form.
Select expiry, logout, or re-login checks when the requested behavior requires
them; avoid changing shared account state merely to prepare unrelated checks.

Distinguish invalid fixtures or missing setup from a product rejecting valid
credentials, preserving observed failed attempts while diagnosing the cause.
Apply Verify's assertion statuses. Report provider authentication, automatic
login, and post-login feature checks separately, so a successful token check or
user sign-in cannot stand in for an unexercised login assertion.

Retain redacted proof from the settled authenticated state, excluding credential
entry payloads and session secrets. Provider access logs or a masked password
field alone do not establish safe delivery.
