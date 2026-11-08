# Secrets for programs

Use this after [access](access.md) has confirmed the service-account identity.
It covers delivering a credential to a command, API client, or test harness, and
creating, updating, archiving, or deleting items in the designated writable
agent vault.

## Find the field

Prefer exact vault and item IDs and field references. If locating an approved
item requires metadata discovery, limit it to the authorized vault; a field read
needs no whole-item export. Consult installed `op read --help` and
[secret reference syntax](https://www.1password.dev/cli/secret-reference-syntax)
for field and OTP references. Retrieve approved OTPs immediately before use.

## Deliver to a command

With the scoped token already provisioned, pass exact references to the
existing consumer. For a POSIX shell:

```sh
TEST_LOGIN_USERNAME='op://VAULT_ID/ITEM_ID/username' \
TEST_LOGIN_PASSWORD='op://VAULT_ID/ITEM_ID/password' \
op run -- env -u OP_SERVICE_ACCOUNT_TOKEN node ./scripts/verify-login.mjs
```

Substitute approved references and the actual project runner. The runner reads
values inside its process. Remove unrelated inherited `op://` references before
`op run`; it resolves those too. Review each reference and interpolation when
using `--env-file`.

Keep output masking on and shell tracing off. Masking does not protect
transformed output, files, or browser artifacts, and same-user processes may read
process environments. Dropping the service token from a consumer that does not
need `op` reduces propagation; it does not sandbox that consumer.
([Environment injection](https://www.1password.dev/cli/secrets-environment-variables),
[run reference](https://www.1password.dev/cli/reference/commands/run))

If `op run` cannot serve an authorized consumer, capture `op read` inside that
process instead of displaying it. Use private temporary files with restrictive
permissions and cleanup only when file input is unavoidable. Real reference
names and IDs can be private metadata; keep project mappings scoped to the
project that needs them.

## Manage items

Use the scoped service account for writes in the user-designated writable agent
vault. Confirm the destination vault and account identity before writing, and
match an existing item's identity before updating, archiving, or deleting it.

To save or update, capture newly generated or already-authorized source
credentials inside the transfer process and pass an item JSON template to
`op item create` or `op item edit` over stdin. Capture their responses too; they
can contain secrets. Verify saved fields inside the process without displaying
them. Preserve unrelated fields. JSON edits can overwrite passkeys; use a
supported path that preserves them or stop.
([Item creation](https://www.1password.dev/cli/reference/management-commands/item#item-create),
[item editing](https://www.1password.dev/cli/reference/management-commands/item#item-edit))

`op item delete --archive` moves an item to the Archive. Plain `op item delete`
puts it in Recently Deleted for 30 days. Check installed help for the current
behavior.
([Item deletion](https://www.1password.dev/cli/reference/management-commands/item#item-delete))
