# Agent routing

This reference owns SreeStack's model defaults, selection, reuse, and recovery policy.
[Orchestration](../SKILL.md) owns assignment, dispatch, and acceptance. T3's injected
instructions and live tool descriptions own the API, transport, permissions, task state,
and workspace binding.

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

The primary-review row also sets the model for cross-judges and single-reviewer audits.
[Research](../../research/SKILL.md#source-routing) uses the YouTube and X retrieval rows.
These rows set routing policy, not exclusive source access.
[Review Fix Loop](../../review-fix-loop/SKILL.md) owns review coverage, assignment
selection, harness review, and optional-failure policy.

Use the exact OpenCode Go IDs above. They keep the subscription route, so leave free or
other paid endpoints out.

Resolve names and effort through `orchestrator_capabilities` to exact available
provider-instance and model IDs and supported options. Use a caller or project choice to
settle multiple matches. Otherwise report the ambiguity. Gemini's effort can be encoded
in its model ID. Pass the complete resolved selection and intended options using the live
tool contract.

## Operate a UI

The agent already on a task operates a browser, computer, desktop app, or device UI itself
as a routine step when its tools reach the target. That step needs no model match or new
selection. This covers UI operation only. Live host rules, permissions, and action
authorization still apply, and all other work keeps its
[working selection](#choose-working-selection), including UI code changes.

Use a dedicated operator only for:

- Substantial UI work, such as a lengthy or difficult workflow.
- A specialized capability the agent's tools lack.
- Required independent verification, using an operator [independent](#reuse-an-agent) of
  the assessed work.
- Repeated operational difficulty, such as tool failures, state mismatches, or
  inconsistent judgments. A product failure is a finding for the implementer, not a
  handoff trigger.

Choose a tier only for a dedicated operator. It changes the model, not permissions or
action authorization:

| Tier | Use for |
| --- | --- |
| Routine UI operation | A well-understood, linear flow. Still check intermediate and final states |
| Demanding UI operation | Branching, uncertain state, recovery, or several interacting assertions |
| Complex UI operation | Complex edge cases, or a high cost of a false pass |

The handoff carries expected and observed states, evidence, unresolved checks, and session
or tool references, under [selection handoff](#selection-handoff).
[Verify](../../verify/SKILL.md) owns acceptance assertions and verdicts.

## Choose working selection

Pick a row for each bounded assignment before you work or dispatch. Explicit user
selections and effort limits come first and hold through project requirements. Then use a
task-specific selection, then the first matching row:

| Assignment | Selection |
| --- | --- |
| Source review, including of UI | Its named review row |
| Research-only source reading, comparison, synthesis, or retrieval, including of UI | General research, or the YouTube or X row |
| [Dedicated UI operation](#operate-a-ui), including verifying an interactive workflow | Routine, Demanding, or Complex UI operation |
| Building or changing UI, however small | UI implementation at any difficulty, never Simple or Hardest |
| Writing or revising prose, however small: skills, agent instructions, READMEs, other docs, and accepted fixes to them | Document writing and revision |
| Diagnosis, design decisions, other code, builds, tests, refactoring, configuration, non-interactive verification, or accepted code fixes | Simple, Standard, or Hardest implementation |

Mixed prose and code keeps one owner on the code's row, even inside a skill folder. Use at
least Standard when the prose needs judgment. Its accepted fixes stay on that row.

| Row | Use for |
| --- | --- |
| Simple | The evidence clearly shows a small, routine, mechanical task with an obvious check, such as a code typo, rename, or formatting fix |
| Standard | The default, including diagnosis and substantive work with clear requirements or established patterns |
| Hardest | Rare cases where evidence shows Standard is insufficient: unresolved architectural tradeoffs, subtle state or concurrency invariants, or repeated failed approaches that require challenging shared assumptions |

Choose Standard when Simple is in doubt. Small size alone does not make a task Simple; a
small concurrency fix can be Hardest.

Do the work yourself only when your model and effort match the selection or an explicit
user override. Otherwise use [selection handoff](#selection-handoff), and leave the
parent's own settings unchanged. Report the chosen selection and why in the assignment or
handoff.

### Raise the row

Reassess when investigation, failed checks, missed checks, state mismatches, or
inconsistent judgments show the work is harder. Escalate one row, or go straight to Hardest
when the evidence warrants it. Carry the task, proof, partial work, and failed assumptions
forward, and reconcile earlier writers first. A real product failure is a finding to
diagnose or fix, not a reason to escalate until the check passes.

Document work rarely escalates. Hard or high-stakes prose stays on its row, and only
repeated failed attempts move it to Standard or Hardest. It and its accepted fixes then keep
the raised row unless a UI row applies.

Reapply the first table when work turns out to change UI, need a dedicated operator, or edit
executable files or tests. Keep a raised row if it is higher, unless a UI row applies.

### Selection handoff

A child with delegation authority stays within its assigned scope.

A child without that authority stops at a safe checkpoint and returns a selection-change
request: the row wanted and why, what is new since any earlier request, completed and
remaining work with exact paths, checks and failed assumptions, and active writers. This is
incomplete work awaiting reassignment. The parent reconciles earlier writers and partial
changes, then dispatches the replacement.

The parent compares each request with the assignment's earlier ones. If it asks for the same
or a higher row and names no new check result, failed assumption, or artifact fact, report a
blocker. A verify-and-repair cycle that changes the artifact or the check result is not a
repeat.

A top-level session that cannot get the row reports that to the user and asks.

## Reuse an agent

Prefer a retained agent you already know of when its context would help. You need not search
for one. It qualifies when it:

- Matches the assignment's resolved model and effort exactly.
- Reaches the correct workspace and current revision.
- Holds useful context that is current, not stuck, and not anchored on failed assumptions.
- Keeps that context under a continuation the host both supports and permits for this work.
  A working continuation tool does not show that permission.

Otherwise use a new agent, as with an unavailable or deleted agent or work that needs an
independent attempt. [Recovery](#recover-work) takes precedence.

**Independence** means separation from writing or directing the assessed work. An agent that
did either stays out of later independent assessment of that work. Its pre-edit coverage
follows the loop's [coverage rule](../../review-fix-loop/SKILL.md#coverage-rule). An earlier
assessment alone does not end independence.

**Follow-up reviews and rechecks** prefer the role's original reviewer when it qualifies, its
reports and receipts are archived, and its context is free of same-round peer content.
Otherwise, or when the host requires a new task for reviews or rechecks, start a new
independent task with the role's criteria and selection, and supply the prior reports,
receipts, and dispositions. Record it as a replacement with prior evidence, not as
continuation. Either way, brief it under
[Review evidence](../../review/references/review-evidence.md).

**Reviewer to implementer.** A read-only reviewer can take accepted repairs once its whole
pass is complete, its reports and receipts are archived, and the caller or Review Sweep has
settled the findings. Its brief lists those repairs and explicitly replaces the read-only
assignment. Already authorized implementation needs no new human approval.

## Recover work

Keep partial results and the failure cause. A caller's failure policy, such as
[additional-review skips](../../review-fix-loop/references/review-assignments.md#handle-failures),
overrides the retry below. Use a new key for any fresh run after terminal failure. Before
replacing work, reconcile retained IDs and [earlier writers](../SKILL.md#dispatch).

| Failure | Action |
| --- | --- |
| Uncertain dispatch or lost response | Repeat with its existing key in the same provider session, so it resolves to the same work |
| Transient terminal or provider runtime failure | May retry once per target per workflow, including within a review round, before the listed fallback |
| Quota, or an unavailable model or provider | The [listed fallback](#availability-fallback) with no retry. Otherwise report the blocker and resume when conditions change |
| Authentication failure | Stop and report it, or request the login through the host's secret route. Retry once it is resolved |
| Permission or policy denial | Stop the blocked action. Another model or transport does not authorize it |
| Wrong answer, failed product check, or task difficulty | Diagnose or escalate |

A required selection without a usable fallback stays a blocker after permitted recovery.

### Availability fallback

A row's fallback applies when the row supplied the selection. An explicit user selection
needs a substitute the user authorized, and any other explicit selection needs its own
authorized fallback. Otherwise it stays a blocker. Use the exact listed model and effort.
A fallback never authorizes unlisted models, the Simple tier, or a change
to additional-review skip policy.

Record the failed selection, failure evidence, and fallback. Keep the assignment's scope,
requirements, verification bar, and review criteria. A review fallback does that role's
review in a new independent task. It does not use the implementer's result or another
assessment as its coverage.

Keep the fallback for that assignment until availability changes or the user directs
otherwise. Task difficulty alone never sends it back to the unavailable selection.

For implementation and document work, if the fallback matches a still-running owner, keep
that owner, record the failed escalation, and pass it the reassessed selection and evidence. If the former run has ended, dispatch a new
fallback task with the saved handoff.

Dispatch identity and stored thread options confirm configuration, not which model the
provider ran.
