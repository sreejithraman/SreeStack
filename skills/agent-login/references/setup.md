# Set up an account login

Obtain the user's designation for the account, needed fields, destinations,
purpose, and role. Confirm the account exists in the application. Provider items
store credentials; they do not create application accounts.

When provider access needs provisioning, establish only its prerequisites.
For 1Password, use [scoped access](1password.md#provision-access-once)
and [runtime access](1password.md#supply-the-runtime), then
resume here once the service account authenticates. Login testing alone does
not authorize provider administration or reading personal credentials.

Store the approved alias in the private account file described in
[README](../../../README.md#agent-login), preserving other aliases. The current
format uses a confirmed 1Password service-account ID and exact `op://` field
references. Include the actual form origin, additional authorized submission
origins, and selectors for its empty input fields and submit control. Add only
the destinations and fields needed for the task; the CLI supports username and
password, not OTP entry or a generic provider registry.

Project instructions need only the nonsecret alias, purpose, and browser workflow.
`agent-login list` discovers configured aliases without resolving values. Keep
account IDs, references, and tokens outside shared skill instructions.

Follow [browser login](browser-login.md) in the host and environment future agents
will use. Confirm private field resolution, the intended account/role, and owner
control after the command disconnects. Record the nonsecret result in the
project's existing verification instructions when maintaining those is in scope.

Report provider authentication, delivery capability, and automatic login
separately. Mark automatic login verified only after the actual public form
succeeds. Otherwise name the missing prerequisite: approved mapping, runtime
access, skill/command discovery, supported adapter, or login verification.
