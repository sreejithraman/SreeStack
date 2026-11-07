# Models

Look up what to launch here. The table is not a rule about who may work. A thread keeps the
model the user picked, and no running agent is replaced because its model differs from a row.

## Model defaults

| Purpose | Provider | Model | Effort | Availability fallback | Review pool |
| --- | --- | --- | --- | --- | --- |
| UI implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Simple implementation and fixes | Codex | GPT-6.1 Sol | Medium | — | — |
| Standard implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Hardest implementation and fixes | Claude | Opus 5.5 | X-High | Codex / GPT-6 Astra / X-High | — |
| Document writing and revision | Claude | Opus 5.5 | Medium | Codex / GPT-6.1 Sol / Medium | — |
| Routine UI operation | Codex | GPT-6.1 Terra | Medium | — | — |
| Demanding UI operation | Codex | GPT-6.1 Terra | High | — | — |
| Complex UI operation | Codex | GPT-6.1 Terra | X-High | — | — |
| General research | Codex | GPT-6.1 Sol | Medium | — | — |
| YouTube retrieval | Antigravity | Gemini 4 Argon | High | Antigravity / Gemini 3.8 Flash / High | — |
| X retrieval | Grok | Grok 4.7 | High | — | — |
| Primary review | Codex | GPT-6.1 Sol | High | — | — |
| Ponytail review | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Thermo review | Codex | GPT-6.1 Sol | High | — | — |
| Adversarial review | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Additional review | OpenCode | `opencode-go/deepseek-v4.1-flash` | Max | — | OpenCode Go |
| Additional review | OpenCode | `opencode-go/glm-5.3-flash` | Max | — | OpenCode Go |
| Additional review | Antigravity | Gemini 4 Argon | High | — | Gemini |
| Additional review | Antigravity | Gemini 3.8 Flash | High | — | Gemini |

The primary-review row also sets the model for cross-judges, single-reviewer audits, and second
opinions. Use the exact OpenCode Go IDs above to keep the subscription route.

Resolve names and effort through `orchestrator_capabilities` to exact available IDs and options.
A caller or project choice settles multiple matches; otherwise report the ambiguity. Gemini's
effort can be encoded in its model ID. When a row's model is unavailable, use [availability fallback](reuse-and-recovery.md#availability-fallback).

## Choose a model

Explicit user choices and effort limits come first and hold through project requirements. Then
use a task-specific choice, then the first matching row.

| Job | Row |
| --- | --- |
| Source review, including of UI | Its named review row |
| Research-only source reading, comparison, synthesis, or retrieval, including of UI | General research, or the YouTube or X row |
| [Dedicated UI operation](#operate-a-ui), including verifying an interactive workflow | Routine, Demanding, or Complex UI operation |
| Building or changing UI, however small | UI implementation at any difficulty, never Simple or Hardest |
| Writing or revising prose, however small: skills, agent instructions, READMEs, other docs, and accepted fixes to them | Document writing and revision |
| Diagnosis, design decisions, other code, builds, tests, refactoring, configuration, non-interactive verification, or accepted code fixes | Simple, Standard, or Hardest implementation |

| Row | Use for |
| --- | --- |
| Simple | The evidence clearly shows a small, mechanical task with an obvious check, such as a code typo, rename, or formatting fix |
| Standard | The default. Choose it when Simple is in doubt |
| Hardest | Rare cases where evidence shows Standard is insufficient: unresolved architectural tradeoffs, subtle state or concurrency invariants, or repeated failed approaches |

Mixed prose and code keeps one owner on the code's row. Executable files and tests are code.

### Raise the row

These rules set the next launch. A running owner stays unless you
[replace it](reuse-and-recovery.md#replace-an-owner).

Raise one row, or go straight to Hardest, when evidence shows the work is harder. A product
failure is a finding to diagnose or fix, not a reason to raise the row until the check passes.
A raised row holds for the work and its fixes unless a UI row applies.

Hard or high-stakes prose stays on its row. Only repeated failed attempts raise it to Standard or
Hardest.

## Operate a UI

The agent already on a task operates a browser, computer, desktop app, or device UI itself as a
routine step when its tools reach it. Live host rules, permissions, and action authorization
still apply.

Use a dedicated operator only for:

- Substantial UI work, such as a lengthy or difficult workflow.
- A capability the agent's tools lack.
- Required independent verification, by an operator [independent](reuse-and-recovery.md#reuse-an-agent) of the work.
- Repeated operational difficulty, such as tool failures, state mismatches, or inconsistent
  judgments.

| Tier | Use for |
| --- | --- |
| Routine UI operation | A well-understood, linear flow. Still check intermediate and final states |
| Demanding UI operation | Branching, uncertain state, recovery, or several interacting assertions |
| Complex UI operation | Complex edge cases, or a high cost of a false pass |

A tier changes the model, not permissions or authorization. The handoff carries expected and
observed states, evidence, unresolved checks, and session or tool references.
[Verify](../../verify/SKILL.md) owns assertions and verdicts. A product failure is a finding for
the implementer, not a handoff trigger.
