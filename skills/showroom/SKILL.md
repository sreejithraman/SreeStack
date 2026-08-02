---
name: showroom
description: Showroom creates, verifies, and hands off the best available review surface after Codex changes product behavior. Use for web, mobile, desktop, API, CLI, library, infrastructure, and data projects when a reviewer needs a URL, running device, artifact, command, transcript, plan, or report with lifecycle details.
---

# Showroom

Produce evidence that a reviewer can actually use. Treat a build or passing test as supporting evidence, not automatically as the review surface.

## Workflow

1. Detect the repository, worktree, project kind, and its native run or release paths. Showroom owns no project file.
2. Read [contract.md](references/contract.md) before selecting or reporting a surface.
3. Select the first suitable surface:
   1. Existing project-native PR or branch review surface.
   2. Configured hosted provider when durable availability is required.
   3. Local platform surface for active or uncommitted work.
   4. Evidence-only surface when no interactive surface exists.
4. Run `showroom doctor --json` before creating local resources. Invoke the bundled CLI as `python3 <skill-dir>/scripts/showroom` when it is not installed on `PATH`.
5. Start or register the selected surface. Keep provider selection visible; never hide authentication, public exposure, spending, or durable resource creation inside an unattended command.
6. Verify through the closest real user surface. For visual or interactive work, capture visible evidence after launching the product.
7. Return the normalized record and lifecycle commands in the final handoff.

## Selection rules

- Choose a local web surface for active web/API work unless the project already provides a usable branch surface or the user needs durable access.
- Choose an iOS Simulator run for iOS interaction or visual work. A build alone is insufficient; launch the app and capture configured evidence.
- Treat TestFlight as an optional durable distribution workflow for meaningful checkpoints, never as the per-edit default. Require explicit authorization and use the project's existing release tooling.
- Choose emulator evidence or an installable testing build for Android.
- Launch desktop applications and capture visible evidence.
- Choose a private endpoint for APIs when possible.
- Choose a runnable example, transcript, generated artifact, plan, or report for CLI, library, infrastructure, and data projects.
- Do not manufacture an interactive surface when an evidence-only handoff is more faithful.

## Hosted providers

Read [hosted-providers.md](references/hosted-providers.md) when a durable surface is required.

Invoke an installed `vercel-deploy`, `netlify-deploy`, `cloudflare-deploy`, or `render-deploy` skill as a workflow. Do not reproduce its deployment commands inside this skill or `showroom`. After deployment, normalize the provider result with `showroom register` and record whether the provider, pull request, or `showroom` owns cleanup.

If the configured provider skill is unavailable, report that limitation and fall through to a local or evidence-only surface. Do not silently install a skill or switch providers.

## Safety

- Never create public exposure by default. Never invoke Tailscale Funnel implicitly.
- Require explicit authorization before public exposure, provider deployment with meaningful external effects, persistent service installation, or user-level configuration changes.
- Keep origins and local endpoints private by default.
- Store runtime state outside repositories. Never commit hostnames, tokens, credentials, generated state, Simulator IDs, or personal signing configuration.
- Act only on exact resources registered as Showroom-owned. Never broadly reset Tailscale, kill by process name or port, erase ordinary simulators, or delete unrelated deployments or files.
- Run `showroom cleanup --dry-run` before material cleanup and present the exact targets when authorization is required.
- State that local surfaces are unavailable while the host sleeps, is off, or loses required connectivity.

## Completion

Do not report success until `showroom verify <id> --json` or equivalent platform verification records a result. Include limitations even when verification passes.

Use the common handoff shape in [contract.md](references/contract.md). Include evidence paths and the exact commands to inspect, renew, pin, stop, and clean up the surface.
