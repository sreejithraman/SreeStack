---
name: gemini-review
description: Use when a local diff needs an external, read-only review through Gemini or the Antigravity CLI.
---

Use the deterministic runner as the single review path; it owns prompt construction, safety checks, and Antigravity transport.

```bash
/Users/sree/.agents/skills/gemini-review/scripts/review-current.mjs
```

In Codex, invoke that executable path directly. Do not prepend `env`, assign
`PATH` or `CODEX_REVIEW_BASE`, invoke it through `node`, or wrap it in a shell.
Those forms change the command prefix and bypass the narrowly scoped approval
rule. Pass configuration as runner arguments instead, especially
`--base <ref>`.

The runner reviews current changes against the parent branch, includes untracked files by default, prints scope, blocks obvious secret-bearing paths/content, checks `agy` is installed, and invokes only `agy --sandbox --print`.

Base resolution (Codex must use `--base`; the environment fallback is for
direct terminal use only):

1. `--base <ref>`
2. `CODEX_REVIEW_BASE`
3. `codex.reviewBase`
4. `branch.<name>.codex-review-base`
5. `branch.<name>.vscode-merge-base`
6. non-self branch upstream
7. `origin/main`

Options:

- `--base <ref>`: review against an explicit parent branch/ref.
- `--tracked-only`: exclude untracked files from the review diff.
- `--max-bytes <n>`: raise or lower the maximum prompt size.
- `--dry-run`: resolve scope and run safety checks without invoking Antigravity/Gemini.

Invocation means the user authorizes this review flow, including sending the
selected diff to Antigravity/Gemini. In Codex, run the exact executable command
above directly; its deterministic runner prefix is pre-approved. If the active
execution policy still requests approval, explain what will be sent and request
approval normally.

## Codex Approval Behavior

If approval is rejected:

1. Treat the rejection as final for external review in this turn.
2. Run the same script with `--dry-run` to verify and report the resolved scope without sending data.
3. Tell the user that no diff was sent externally.
4. Give the user the direct-terminal command to run outside Codex from the repo root:

```bash
/Users/sree/.agents/skills/gemini-review/scripts/review-current.mjs
```

5. Ask the user to paste the output back into Codex for triage.

If Antigravity prints an authentication URL, stop and tell the user to complete OAuth, then continue through the same runner.

Validate output before reporting it. Treat it as advisory: drop weak, speculative, duplicate, or line-impossible findings. Present plausible findings first in code-review style, then mention reviewed scope and residual uncertainty.
