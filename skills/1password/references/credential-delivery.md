# Credential delivery

Prefer exact vault/item IDs and field references. If locating an approved item
requires metadata discovery, limit it to the authorized vault; whole-item exports
are unnecessary for a field read. Consult installed `op read --help` and
[secret reference syntax](https://www.1password.dev/cli/secret-reference-syntax)
for field and OTP references. Retrieve approved OTPs immediately before use.

For login, compare the actual scheme, host, and port with the approved origin.
Subdomains and redirect targets need their own authorization. Use HTTPS remotely;
HTTP is acceptable for an explicitly allowed loopback test origin.

## Browser login

Use a credential-aware browser integration when available for the selected access
path, honoring its approval prompts and documented guarantees. Otherwise use an
existing project login harness with environment injection below. Follow the host's
browser routing rules; a missing credential feature does not justify changing
browsers. Ordinary typing tools accept literal values, not `op://` references.

Before injecting, check that the consumer submits only to approved origins and
keeps credential payloads out of traces, screenshots, reports, and saved browser
state. A login approval covers credential use, not subsequent site actions.

## Commands and test harnesses

With the scoped token already provisioned, supply exact references to an existing
consumer. For a POSIX shell:

```sh
TEST_LOGIN_USERNAME='op://VAULT_ID/ITEM_ID/username' \
TEST_LOGIN_PASSWORD='op://VAULT_ID/ITEM_ID/password' \
op run -- env -u OP_SERVICE_ACCOUNT_TOKEN node ./scripts/verify-login.mjs
```

Substitute approved references and the actual project runner; none is bundled.
The runner reads values inside its process. Remove unrelated inherited `op://`
references before `op run`; it resolves those too. Review each reference and
interpolation when using `--env-file`.

Keep output masking enabled and shell tracing off. Masking does not protect
transformed output, files, or browser artifacts, and same-user processes may read
process environments. Dropping the service token from a consumer that does not
need `op` reduces propagation; it does not sandbox that consumer.
([Environment injection](https://www.1password.dev/cli/secrets-environment-variables),
[run reference](https://www.1password.dev/cli/reference/commands/run))

If `op run` cannot serve an authorized consumer, capture `op read` inside that
process instead of displaying it. Use private temporary files with restrictive
permissions and cleanup only when file input is unavoidable. Real reference
names and IDs can be private metadata; keep project mappings appropriately scoped.

## Credential storage

Use the scoped service account for saves and updates in a user-designated writable
agent vault. Capture newly generated or already-authorized source credentials
inside the transfer process and pass an item JSON template to `op item create` or
`op item edit` over stdin. Capture their responses too; they can contain secrets.
Confirm the destination vault and account identity before writing, match an
existing item's identity before updating it, and verify saved fields inside the
process without displaying them. Preserve unrelated fields. JSON edits can
overwrite passkeys; use a supported path that preserves them or stop.
([Item creation](https://www.1password.dev/cli/reference/management-commands/item#item-create),
[item editing](https://www.1password.dev/cli/reference/management-commands/item#item-edit))
