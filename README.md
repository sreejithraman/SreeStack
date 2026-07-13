# SreeStack

A curated stack of agent skills by Sree.

SreeStack collects practical skills for implementation, review, verification, multi-agent execution, and expressive web design. Each skill is a self-contained folder whose `SKILL.md` defines when it runs and how it reaches completion.

## Skills

| Skill | Purpose |
|---|---|
| `forever-components-inspo` | Search the Forever Components manifest for UI references. |
| `gemini-review` | Send the current diff through a guarded, read-only Gemini review runner. |
| `github-review-sweep` | Triage, fix, reply to, and resolve GitHub PR review feedback. |
| `goal-swarm` | Split explicitly authorized work into bounded parallel-agent shards. |
| `launch-swarm` | Carry work through implementation, review, publishing, and PR readiness. |
| `manual-verify` | Exercise changed behavior through its closest real surface and report evidence. |
| `motion-websites` | Art-direct, motion-score, build, and verify expressive websites. |
| `review-fix-loop` | Repeat local and external review, accepted fixes, and verification until stable. |
| `review-sweep` | Normalize findings, verify claims, fix accepted issues, and return owned defers. |

## Install

SreeStack follows the Agent Skills repository convention: authored skills live as complete directories under `skills/`. The root `caddie.json` composes those skills with selected skills from Caddie, Matt Pocock's skills repository, and Cursor's plugins repository. `caddie.lock` pins every Git source to an exact commit.

Use Caddie to inspect and reconcile the manifest. User Skills are materialized as complete directories under `~/.agents/skills`; Claude compatibility is provided through individual links under `~/.claude/skills`.

Restart or refresh the agent host after installation if it caches skill discovery.

## Dependencies

Some skills compose other skills in this collection:

- `github-review-sweep` uses `review-sweep`.
- `review-fix-loop` uses `gemini-review`, `review-sweep`, and `manual-verify`.
- `launch-swarm` uses `goal-swarm`, `review-fix-loop`, `github-review-sweep`, and `manual-verify`.
- `motion-websites` uses `manual-verify` and can hand site work to the host's Sites capability when available.

Host capabilities remain host-specific. In particular, GitHub workflows require authenticated GitHub tooling, browser verification requires a supported browser-control surface, parallel work requires subagent support, and `gemini-review` requires Node.js plus the local `agy` CLI.

## Repository layout

```text
SreeStack/
├── README.md
├── caddie.json       # User Skills manifest
├── caddie.lock       # exact Git source revisions
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── references/   # optional disclosed reference
        ├── scripts/      # optional deterministic tooling
        └── assets/       # optional reusable assets
```

## Publishing status

The collection is prepared for local use and public-source review. A public license has not been selected yet; choose one before publishing or accepting contributions.
