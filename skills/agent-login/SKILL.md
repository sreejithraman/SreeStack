---
name: agent-login
description: Use when signing into applications, setting up or diagnosing agent credential access, or supplying and managing approved credentials for authentication.
---

# Agent Login

Pick the route that matches the task. Each route ends at its own finish line.
A missing prerequisite ends the route as a named block.

## Rules for every route

- Read [access](references/access.md) before any authenticated operation. It
  decides who may use which credential and how to confirm the agent's identity.
- Setup or credential work does not continue into an application login
  unasked. A login that the user or a calling workflow, such as verify, asks
  for counts as a request.
- Machine setup and other administration need an explicit user request. That
  covers vault creation, service-account grants, token storage and rotation,
  and host configuration. A login or credential task creates no tokens, changes
  no grants, and reads personal credentials only as access approves.
- Keep values inside the consumer. Keep them out of chat, agent tool arguments,
  logs, source code, project files such as tracked `.env` files and fixtures,
  and verification artifacts. Apply the user's capture policy.
- Send a credential only to exact approved destinations, including identity
  providers and redirects. Use an encrypted transport for remote destinations,
  such as HTTPS for web origins. Plain HTTP is allowed only for approved
  loopback test origins.
- A login approval covers credential use, not later application actions.
- Report provider authentication, delivery, and login as separate results. Each
  needs its own proof.

## Machine or account setup

Use this route to provision unattended agent access, repair a runtime that
prompts for Touch ID, onboard an application account, or check login readiness.

- For the vault, service account, and each runtime's token, follow
  [machine setup](references/machine-setup.md). It is done when each affected
  runtime authenticates as the designated identity.
- To onboard an application account, follow
  [onboard an account](references/browser-login.md#onboard-an-account).
  Onboarding includes its proof login. It is done when that login is verified
  or a missing prerequisite other than the login itself is named.

## Credential use, storage, or item management

Use this route when a command, API, test harness, or subprocess needs a
credential, when a value must be saved, or when items in the designated
writable agent vault must be created, updated, archived, or deleted. After
[access](references/access.md), follow
[secrets for programs](references/secrets-for-programs.md).

It is done when one of these is true:

- The consumer authenticates or accepts the privately delivered credential.
  Product and test results belong to the work that asked for the credential;
  use [verify](../verify/SKILL.md) for product assertions.
- The requested item state, such as saved fields or an archived or deleted
  item, checks out in the designated vault under the scoped service account.
- The missing prerequisite is named, such as a missing runtime token or missing
  scope.

## UI login

Use this route to sign into an application in a browser or device session.

Reuse an existing authenticated session when its account and role fit the
requested work. Preserve user-established sessions. Reuse does not prove
automatic login; a login assertion starts from its required signed-out state.

1. Choose a credential-aware consumer that resolves fields privately into the
   actual browser or device session. Honor host routing. The bundled
   `agent-login` command supports only 1Password and existing local Chromium
   CDP tabs; follow [browser login](references/browser-login.md#fill-a-tab) to
   use it. Native T3/Codex browser and simulator adapters are not implemented.
   An approved project consumer can supply another supported path. Ordinary
   typing tools take literal values and cannot do private delivery. If delivery
   is unavailable, report the missing integration and continue after user
   sign-in.
2. Treat filling or submission as delivery results. Use the original session to
   confirm authenticated state and the intended account and role.

It is done when the original session shows the intended account and role and
stays open for the requested work. Use [verify](../verify/SKILL.md) for product
assertions.
