# Hosted provider dispatch

Use hosted deployment only for durable availability or an existing project-native preview lifecycle.

## Dispatch

1. Detect existing repository configuration and PR/branch previews.
2. Respect `.preview.toml` `hosted_provider`; do not substitute another provider silently.
3. Confirm that the matching skill is installed and available.
4. Invoke that skill explicitly and follow its authorization, authentication, configuration, and verification rules.
5. Register its returned URL/resource identifier with `previewctl register`.
6. Set lifecycle ownership accurately:
   - `pull-request` when the native PR lifecycle owns it.
   - `provider` when the provider owns expiry or cleanup.
   - `previewctl` only when an exact authorized cleanup action is available.
7. Record provider limitations and management commands or dashboard links.

Provider workflows are not runtime libraries and do not share a stable machine-readable result. Keep normalization in the agent workflow and keep provider-specific deployment logic out of `previewctl`.

Never delete or renew a hosted resource merely because its local registry record expired. Require an exact provider resource identity and use the relevant provider workflow.
