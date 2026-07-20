# Provider skill composition research

Researched 2026-07-20 from the current Codex manual and the official OpenAI skills catalog. This note records workflow facts, not provider credentials or machine-specific configuration.

## Findings

- Codex skills are reusable workflow instructions with optional scripts and references. They activate explicitly with `$skill-name` or implicitly from their descriptions; they are not runtime libraries with a stable callable interface. [Codex: Build skills](https://learn.chatgpt.com/docs/build-skills)
- Personal skills belong under `$HOME/.agents/skills`, while checked-in source can live elsewhere and be copied or symlinked into that location. The repository should therefore be the source of truth without assuming that every provider skill is installed. [Codex: Build skills](https://learn.chatgpt.com/docs/build-skills)
- The official curated catalog currently contains `vercel-deploy`, `netlify-deploy`, `cloudflare-deploy`, and `render-deploy`. Curated skills are installed separately and may be absent from a session. [OpenAI skills catalog](https://github.com/openai/skills)
- Provider skills differ materially. Vercel returns a preview URL and may return a claim URL; Netlify uses its CLI and returns deployment/site information; Cloudflare selects among several products before deployment; Render may use a Blueprint or MCP-backed resource creation. A common runtime deployment interface cannot be inferred from these instruction files. [Vercel skill](https://github.com/openai/skills/blob/main/skills/.curated/vercel-deploy/SKILL.md), [Netlify skill](https://github.com/openai/skills/blob/main/skills/.curated/netlify-deploy/SKILL.md), [Cloudflare skill](https://github.com/openai/skills/blob/main/skills/.curated/cloudflare-deploy/SKILL.md), [Render skill](https://github.com/openai/skills/blob/main/skills/.curated/render-deploy/SKILL.md)
- Provider actions can require authentication, prompts, repository changes, or external resource creation. Provider selection and authorization must remain visible to Codex rather than being hidden inside an unattended generic CLI call.

## Recommended seam

Keep provider dispatch in the `preview` skill:

1. Detect an existing project-native PR or branch preview before creating anything.
2. If durable hosting is requested or required, select an installed provider skill from project configuration and invoke it as an agent workflow.
3. Verify the returned surface according to the preview contract when provider policy permits.
4. Normalize the provider result into `previewctl` with a provider-neutral registration command or evidence-only record.

Keep `previewctl` responsible for project/worktree identity, local adapters, registry records, leases, normalized rendering, verification metadata, and exact cleanup. Do not put provider deployment commands, credentials, or provider-specific schemas in the CLI core.

Provider records should allow opaque fields such as `provider_resource_id`, `provider_url`, and lifecycle ownership (`previewctl`, `provider`, or `pull-request`). Cleanup should report provider-owned resources rather than deleting them unless an installed provider workflow explicitly supplies an exact, authorized deletion action.

## Installation implication

The `preview` skill may recommend installing a missing curated provider skill, but it must not silently install one. Absence of a hosted-provider skill falls through to a local platform adapter or evidence-only handoff.

## Residual uncertainty

Skill prose and outputs can evolve without a machine-readable compatibility contract. Hosted-provider dispatch therefore remains an agent-level protocol. A future stable provider tool or MCP interface could justify a real runtime adapter, but should be added only when at least two concrete implementations share a proven interface.
