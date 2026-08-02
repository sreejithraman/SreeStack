---
name: showroom
description: Showroom creates and verifies review surfaces after product work, adopts ambiguous projects through optional checked-in configuration, and repairs repo delivery commands that fail its contract. Use when a reviewer needs a URL, running device, artifact, command, transcript, plan, or report with lifecycle details.
---

# Showroom

Give the reviewer a surface they can use. A build or test supports the surface; it does not replace one.

## Workflow

1. Detect the repo, worktree, project, and native run or release path. If `.showroom.toml` exists, read [configuration.md](references/configuration.md). Finish when one project and target surface are clear.
2. Read [contract.md](references/contract.md). Pick the first fit: an existing project surface, a durable provider surface, a local platform surface, then evidence only. Finish when the choice and its owner are clear.
3. Run `showroom doctor [project] --json`. Use `python3 <skill-dir>/scripts/showroom` when `showroom` is not on `PATH`. If a delivery command fails, read [delivery-command.md](references/delivery-command.md), inspect the repo's current release script, and repair the smallest checked-in command plus contract tests. Finish when doctor passes without delivery side effects.
4. Start or register the surface. Keep approval needs clear for auth, public access, spend, and durable resources. Finish when one normalized record owns the exact local resources or names the external owner.
5. Verify through the closest user surface. Capture visible proof for visual work. Finish when `showroom verify <id> --json` records the current result.
6. Return the record with its location, evidence, limits, end time, and exact inspect, verify, renew, pin, unpin, and stop commands.

## Selection

- Use an iOS Simulator for routine iOS visual work. Use Device or TestFlight only when the user asks or the change needs that surface.
- Use a local web surface for active web or API work unless a useful branch surface exists or the user needs a longer-lived URL.
- Use TestFlight for a meaningful checkpoint after explicit approval. A pending Apple processing state remains pending.
- Use emulator evidence or an installable test build for Android.
- Launch desktop apps and capture visible evidence.
- Use a private endpoint for APIs when possible.
- Use a runnable example, transcript, artifact, plan, or report when no true interactive surface fits.
- Do not create an interactive surface when evidence gives a truer review.

Read [hosted-providers.md](references/hosted-providers.md) when durable hosting is needed.

Use an installed `vercel-deploy`, `netlify-deploy`, `cloudflare-deploy`, or `render-deploy` skill for provider deployment. Do not copy its commands into Showroom. Then use `showroom register` to save the result and its provider, pull-request, or Showroom owner. If the skill is missing, state that limit and use a local or evidence surface. Do not install or switch providers without approval.

## Safety

- Keep surfaces private by default.
- Never invoke Tailscale Funnel without explicit approval.
- Require approval for public access, provider deployment, persistent services, user settings, and TestFlight uploads.
- Store runtime state outside the repo. Keep host names, tokens, credentials, device IDs, and signing data out of checked-in config.
- Act only on exact Showroom-owned resources. For manual and provider delivery, stop the record and leave the external app or build unchanged.
- Do not reset Tailscale, kill by process name or port, erase normal simulators, or delete unrelated provider resources.
- Run `showroom cleanup --dry-run` before material cleanup and show exact targets when approval is needed.
- State that local surfaces fail while the host sleeps, shuts down, or loses needed access.
- Do not report success until `showroom verify <id> --json` records the result.
