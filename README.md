# SreeStack

A curated stack of agent skills by Sree.

SreeStack collects practical skills for implementation, review, verification, multi-agent execution, and expressive web design. Each skill is a self-contained folder whose `SKILL.md` defines when it runs and how it reaches completion.

## Skills

| Skill | Purpose |
|---|---|
| `toolcraft-brainstorming` | Define Toolcraft product behavior and app contracts before implementation. |
| `toolcraft-browser` | Verify generated Toolcraft apps through their visible browser surface. |
| `design-eng` | Plan, build, and review interface behavior, motion, hierarchy, materials, typography, and accessibility. |
| `forever-components-inspo` | Search the Forever Components manifest for UI references. |
| `gemini-review` | Send the current diff through a guarded, read-only Gemini review runner. |
| `goal-swarm` | Split user- or parent-authorized work into bounded parallel-agent shards. |
| `launch-swarm` | Build a direct task or spec-rooted ticket set and deliver merge-ready PRs, stacked where needed. |
| `manual-verify` | Exercise changed behavior through its closest real surface and report evidence. |
| `motion-websites` | Art-direct, motion-score, build, and verify expressive websites. |
| `showroom` | Create, verify, lease, and hand off review surfaces, with shared local Apple delivery profiles. |
| `review-fix-loop` | Repeat local and external review, accepted fixes, and verification until stable. |
| `review-push-and-watch` | Review, publish, watch, and fix one GitHub PR until ready or blocked. |
| `review-sweep` | Normalize findings, verify claims, fix accepted issues, and return owned defers. |
| `toolcraft-systematic-debugging` | Diagnose Toolcraft controls, tests, builds, exports, and runtime failures. |
| `toolcraft-writing-plans` | Plan Toolcraft app changes and their required verification. |
| `writing-great-skills` | Guide predictable skill authoring, invocation, structure, and pruning. |

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

- `review-fix-loop` uses `code-review`, `gemini-review`, `review-sweep`, and `manual-verify`.
- `review-push-and-watch` uses `review-fix-loop` and `review-sweep`.
- `launch-swarm` uses `goal-swarm` and `review-push-and-watch`.
- `motion-websites` uses `manual-verify` and can hand site work to the host's Sites capability when available.
- `showroom` bundles a Python 3.11 CLI of the same name. Local web surfaces use Tailscale Serve and macOS `launchd`; iOS surfaces require Xcode. Durable hosted surfaces compose separately installed provider deployment skills.

Host capabilities remain host-specific. In particular, GitHub workflows require authenticated GitHub tooling, browser verification requires a supported browser-control surface, parallel work requires subagent support, and `gemini-review` requires Node.js plus the local `agy` CLI.

The four Toolcraft workflow skills are adapted from `@pixel-point/toolcraft@0.0.12` and remain subject to Pixel Point's Toolcraft Designer License. Their names are prefixed to avoid overriding general-purpose skills. See `third-party/toolcraft-0.0.12/LICENSE.md`. Toolcraft's CLI and app runtime are not vendored here; run the published generator with `npx @pixel-point/toolcraft create` when creating an app.

## Repository layout

```text
SreeStack/
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── references/   # optional disclosed reference
        ├── scripts/      # optional deterministic tooling
        └── assets/       # optional reusable assets
```

## Publishing status

The collection is prepared for local use and public-source review. A public license has not been selected yet; choose one before publishing or accepting contributions.
