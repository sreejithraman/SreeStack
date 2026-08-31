# SreeStack

A curated stack of agent skills by Sree.

SreeStack collects practical skills for implementation, review, verification, multi-agent execution, and expressive web design. Each skill is a self-contained folder whose `SKILL.md` defines when it runs and how it reaches completion.

## Skills

| Skill | Purpose |
|---|---|
| `animate` | Decide, implement, and test focused interface animation. |
| `design-eng` | Plan, build, and review interface behavior, motion, hierarchy, materials, typography, and accessibility. |
| `forever-components-inspo` | Search the Forever Components manifest for UI references. |
| `gemini-review` | Send the current diff through a guarded, read-only Gemini review runner. |
| `goal-swarm` | Split user- or parent-authorized work into bounded parallel-agent shards. |
| `kinetics-inspo` | Search Kinetics for interface motion patterns and implementation ideas. |
| `launch-swarm` | Build a direct task or spec-rooted ticket set and deliver merge-ready PRs, stacked where needed. |
| `manual-verify` | Exercise changed behavior through its closest real surface and report evidence. |
| `ponytail-review` | Find code a repo or diff can delete, reuse, inline, or replace. |
| `showroom` | Create, verify, lease, and hand off review surfaces, with shared local Apple delivery profiles. |
| `review-fix-loop` | Repeat local and external review, accepted fixes, and verification until stable. |
| `review-push-and-watch` | Review, publish, watch, and fix one GitHub PR until ready or blocked. |
| `review-sweep` | Normalize findings, verify claims, fix accepted issues, and return owned defers. |

## Install

Install one skill:

```bash
cp -R skills/manual-verify ~/.agents/skills/manual-verify
```

Install the full collection:

```bash
mkdir -p ~/.agents/skills
cp -R skills/* ~/.agents/skills/
```

Restart or refresh the agent host after installation if it caches skill discovery.

## Dependencies

Some skills compose other installed skills:

- `review-fix-loop` uses `ponytail-review`, `code-review`, `gemini-review`, `review-sweep`, and `manual-verify`.
- `review-push-and-watch` uses `review-fix-loop` and `review-sweep`.
- `launch-swarm` uses `goal-swarm` and `review-push-and-watch`.
- `showroom` bundles a Python 3.11 CLI of the same name. Local web surfaces use Tailscale Serve and macOS `launchd`; iOS surfaces require Xcode. Durable hosted surfaces compose separately installed provider deployment skills.

Host capabilities remain host-specific. In particular, GitHub workflows require authenticated GitHub tooling, browser verification requires a supported browser-control surface, parallel work requires subagent support, and `gemini-review` requires Node.js plus the local `agy` CLI.

`ponytail-review` adapts the Ponytail review rules by Dietrich Gebert under the MIT License. See `skills/ponytail-review/LICENSE.txt`.

## Repository layout

```text
SreeStack/
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml  # Codex UI metadata and invocation policy
        ├── references/   # optional disclosed reference
        ├── scripts/      # optional deterministic tooling
        └── assets/       # optional reusable assets
```

## Publishing status

The collection is prepared for local use and public-source review. A public license has not been selected yet; choose one before publishing or accepting contributions.
