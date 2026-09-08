---
name: app-store-connect
description: Use when asked to check App Store Connect builds, investigate TestFlight crashes or feedback, distribute betas, prepare or submit a release, fix App Review blockers, update store listings or pricing, manage Apple Ads, or run asc commands. Also use for signing, export, or notarization as part of app distribution. Excludes local Simulator debugging.
---

# App Store Connect usage

Use this skill when you need to run or design `asc` commands for App Store Connect.

Read only the workflow guide needed for the request; follow its supporting links when their stated condition applies. Switching guides keeps the current task, resolved IDs, and authorization.

Read app IDs, auth profiles, build selection, and release rules from the current project. Reuse its release scripts where they cover the task. These guides provide procedures, not permission for unrelated account changes or test mutations.

## Command discovery

- Check `asc version` and use the installed command’s `--help` to verify examples before running them. The guides may cover a newer CLI version.
  - `asc --help`
  - `asc builds --help`
  - `asc builds list --help`
- Use `asc search` for local, deterministic command discovery when you know the workflow but not the command path.
  - `asc search "submit app for review"`
  - `asc search --output table "upload build"`
- Use `asc schema` to inspect bundled App Store Connect endpoint schemas and request/query fields before designing API-facing commands.
  - `asc schema --pretty "GET /v1/apps"`
  - `asc schema --method POST appStoreVersions`
- Use `asc capabilities` to explain CLI-supported, partial, web-session, and public-API-limited workflow coverage.
  - `asc capabilities --area release --output table`
  - `asc capabilities --status web-session --output table`
  - `asc capabilities --status not-public-api --output markdown`

## Canonical verbs (current asc)

- Prefer `view` over legacy `get` aliases for read-only commands in docs and automation.
  - `asc apps view --id "APP_ID"`
  - `asc versions view --version-id "VERSION_ID"`
  - `asc pricing availability view --app "APP_ID"`
- Prefer `edit` for update-only availability surfaces and other canonical edit flows.
  - `asc pricing availability edit --app "APP_ID" --territory "USA,GBR" --available true`
  - `asc app-setup availability edit --app "APP_ID" --territory "USA,GBR" --available true`
  - `asc xcode version edit --build-number "42"`
- Use `asc pricing availability create` to initialize app availability before using the update-only `edit` command. If Apple rejects the public-API bootstrap, authenticate a web session and use `asc web apps availability create`, or configure Pricing and Availability in App Store Connect.
  - `asc pricing availability create --app "APP_ID" --territory "USA,GBR" --available true --available-in-new-territories true`
  - `asc web apps availability create --app "APP_ID" --territory "USA,GBR" --available-in-new-territories true`
- Keep `set` where the CLI intentionally models a higher-level replacement/configuration flow and `--help` still shows `set` as the canonical verb.

## Flag conventions

- Use explicit long flags (e.g., `--app`, `--output`).
- Prefer explicit flags in automation; some newer commands can prompt for missing fields when run interactively.
- Destructive operations require `--confirm`.
- Use `--paginate` when the user wants all pages.

## Output formats

- Output defaults are TTY-aware: `table` in interactive terminals, `json` when piped or non-interactive.
- Use `--output table` or `--output markdown` only for human-readable output.
- `--pretty` is only valid with JSON output.

## Authentication and defaults

- Prefer keychain auth via `asc auth login`.
- Fallback env vars: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY_PATH`, `ASC_PRIVATE_KEY`, `ASC_PRIVATE_KEY_B64`.
- `ASC_APP_ID` can provide a default app ID.
- When permissions are unclear, inspect exact API key role coverage with `asc web auth capabilities`.
  - This lives under the web-session auth surface.
  - It can resolve the current local auth by default, or inspect a specific key with `--key-id`.
- When API key setup is requested, create an App Store Connect team API key through a cached Apple Account web session with `asc web api-keys create`.
  - An Account Holder or Admin session is required; use `asc web auth login --apple-id "user@example.com"` first when needed.
  - The command saves the one-time P8 as `AuthKey_<KEY_ID>.p8` without printing its contents; choose an explicit private directory with `--output-dir`.
  - Example: `asc web api-keys create --name "CI uploads" --role APP_MANAGER --output-dir "./keys" --output json`.

## Timeouts

- `ASC_TIMEOUT` / `ASC_TIMEOUT_SECONDS` control request timeouts.
- `ASC_UPLOAD_TIMEOUT` / `ASC_UPLOAD_TIMEOUT_SECONDS` control upload timeouts.

## Workflow guides

| Task | Read |
| --- | --- |
| Resolve app, version, build, or group IDs | [asc-id-resolver](references/asc-id-resolver/guide.md) |
| Inspect builds, processing, or retention | [asc-build-lifecycle](references/asc-build-lifecycle/guide.md) |
| Distribute TestFlight builds and manage testers | [asc-testflight-orchestration](references/asc-testflight-orchestration/guide.md) |
| Read TestFlight crashes and feedback | [asc-crash-triage](references/asc-crash-triage/guide.md) |
| Archive or export with Xcode | [asc-xcode-build](references/asc-xcode-build/guide.md) |
| Set up certificates, profiles, and signing | [asc-signing-setup](references/asc-signing-setup/guide.md) |
| Diagnose review blockers, rejection, or stuck submissions | [asc-submission-health](references/asc-submission-health/guide.md) |
| Stage, publish, or submit a release | [asc-release-flow](references/asc-release-flow/guide.md) |
| Sync store metadata | [asc-metadata-sync](references/asc-metadata-sync/guide.md) |
| Translate store metadata | [asc-localize-metadata](references/asc-localize-metadata/guide.md) |
| Write What’s New release notes | [asc-whats-new-writer](references/asc-whats-new-writer/guide.md) |
| Capture, frame, and upload screenshots | [asc-shots-pipeline](references/asc-shots-pipeline/guide.md) |
| Resize existing screenshots | [asc-screenshot-resize](references/asc-screenshot-resize/guide.md) |
| Audit App Store search optimization | [asc-aso-audit](references/asc-aso-audit/guide.md) |
| Fetch analytics reports | [asc-analytics-reports](references/asc-analytics-reports/guide.md) |
| Localize subscriptions and in-app purchases | [asc-subscription-localization](references/asc-subscription-localization/guide.md) |
| Set prices by purchasing power | [asc-ppp-pricing](references/asc-ppp-pricing/guide.md) |
| Sync a RevenueCat product catalog | [asc-revenuecat-catalog-sync](references/asc-revenuecat-catalog-sync/guide.md) |
| Distribute ad hoc builds | [asc-ad-hoc-distribution](references/asc-ad-hoc-distribution/guide.md) |
| Notarize macOS apps | [asc-notarization](references/asc-notarization/guide.md) |
| Create an app record through the browser | [asc-app-create-ui](references/asc-app-create-ui/guide.md) |
| Define repeatable asc workflows | [asc-workflow](references/asc-workflow/guide.md) |
| Manage Apple Ads auth, campaigns, or reports | [asc-apple-ads](references/asc-apple-ads/guide.md) |
| Submit an app to the CLI project’s showcase | [asc-wall-submit](references/asc-wall-submit/guide.md) |
