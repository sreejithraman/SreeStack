# Models

The table sets defaults for new launches and availability recovery; it never replaces a running
agent or overrides the model the user picked for a thread.

## Model defaults

| Purpose | Provider | Model | Effort | Availability fallback | Review pool |
| --- | --- | --- | --- | --- | --- |
| Coordinator | Claude | Opus 5.5 | High | Codex / GPT-6.2 Sol / High | — |
| UI implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.2 Sol / High | — |
| Simple implementation and fixes | Codex | GPT-6.2 Sol | Medium | — | — |
| Standard implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.2 Sol / High | — |
| Hardest implementation and fixes | Claude | Opus 5.5 | X-High | Codex / GPT-6.2 Astra / X-High | — |
| Document writing and revision | Claude | Opus 5.5 | Medium | Codex / GPT-6.2 Sol / Medium | — |
| Routine UI operation | Codex | GPT-6.1 Terra | Medium | — | — |
| Demanding UI operation | Codex | GPT-6.1 Terra | High | — | — |
| Complex UI operation | Codex | GPT-6.1 Terra | X-High | — | — |
| General research | Codex | GPT-6.2 Sol | Medium | — | — |
| YouTube retrieval | Antigravity | Gemini 4 Hydrogen High | High | — | — |
| X retrieval | Grok | Grok 4.7 | High | — | — |
| Primary review | Codex | GPT-6.2 Sol | High | — | — |
| Ponytail review | Claude | Opus 5.5 | High | Codex / GPT-6.2 Sol / High | — |
| Thermo review | Codex | GPT-6.2 Sol | High | — | — |
| Adversarial review | Claude | Opus 5.5 | High | Codex / GPT-6.2 Sol / High | — |
| Additional review | Antigravity | Gemini 4 Hydrogen High | High | — | Gemini |

The Primary review row also sets the model for cross-judges, single-reviewer audits, and second
opinions. Some providers (such as Gemini) encode effort in the model ID; resolve the exact ID from
live host capabilities.

## Choose a model

| Job | Row |
| --- | --- |
| Running a multi-outcome coordinator or its program | Coordinator |
| Source review, including of UI | Its named review row |
| Research-only source reading, comparison, synthesis, or retrieval, including of UI | General research, or the YouTube or X row |
| Dedicated UI operation (see below), including verifying an interactive workflow | Routine, Demanding, or Complex UI operation |
| Building or changing UI, however small | UI implementation at any difficulty, never Simple or Hardest |
| Writing or revising prose, however small (skills, agent instructions, READMEs, docs, and their fixes) | Document writing and revision |
| Diagnosis, design decisions, other code, builds, tests, refactoring, config, non-interactive verification, or code fixes | Simple, Standard, or Hardest implementation |

| Difficulty row | Use for |
| --- | --- |
| Simple | Evidence clearly shows a small, mechanical task with an obvious check (typo, rename, formatting) |
| Standard | Default; choose whenever Simple is in doubt |
| Hardest | Rare cases where evidence shows Standard is insufficient: unresolved architectural tradeoffs, subtle state or concurrency invariants, or repeated failed approaches |

Mixed prose and code keeps one owner on the code's row. Executable files and tests are code.

### Raise the row

Applies to the next launch; a running owner stays unless replaced.

Raise one row (or straight to Hardest) when evidence shows the work is harder. A product failure is
a finding to diagnose or fix, not a reason to raise the row. A raised row holds for the work and its
fixes unless a UI row applies. High-stakes prose stays on Document writing and revision; only
repeated failed attempts raise it to Standard or Hardest.

## Operate a UI

The agent already on a task operates a browser, desktop app, or device UI itself as a routine step
when its tools reach it.

Use a dedicated UI operator only for:

- Substantial UI work (a lengthy or difficult workflow).
- A capability the agent's tools lack.
- Required independent verification, by an operator independent of the work.
- Repeated operational difficulty (tool failures, state mismatches, inconsistent judgments).

| Tier | Use for |
| --- | --- |
| Routine UI operation | Well-understood linear flow; still check intermediate and final states |
| Demanding UI operation | Branching, uncertain state, recovery, or several interacting assertions |
| Complex UI operation | Complex edge cases, or high cost of a false pass |

A tier changes the model, not permissions or authorization. Pass expected and observed states,
evidence, unresolved checks, and session/tool references in the handoff.
The verification caller owns assertions and verdicts; a product failure goes to the
implementer, not a UI operator.
