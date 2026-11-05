# Agent routing

This file owns model defaults, selection, reuse, and recovery. [Orchestration](../SKILL.md) owns
assignment, dispatch, and acceptance. T3's injected instructions and live tool descriptions own
the API, transport, permissions, task state, and workspace binding.

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
[Research](../../research/SKILL.md#source-routing) uses the YouTube and X rows, which set routing
policy, not exclusive source access. [Review Fix Loop](../../review-fix-loop/SKILL.md) owns review
coverage and assignment. Use the exact OpenCode Go IDs above to keep the subscription route.

Resolve names and effort through `orchestrator_capabilities` to exact available IDs and options.
A caller or project choice settles multiple matches; otherwise report the ambiguity. Gemini's
effort can be encoded in its model ID. Pass the complete selection using the live tool contract.

## Operate a UI

The agent already on a task operates a browser, computer, desktop app, or device UI itself as a
routine step when its tools reach it. That step needs no model match. Live host rules,
permissions, and action authorization still apply, and all other work keeps its selection.

Use a dedicated operator only for:

- Substantial UI work, such as a lengthy or difficult workflow.
- A capability the agent's tools lack.
- Required independent verification, by an operator [independent](#reuse-an-agent) of the work.
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

## Choose working selection

Explicit user selections and effort limits come first and hold through project requirements. Then
use a task-specific selection, then the first matching row:

| Assignment | Selection |
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

Mixed prose and code keeps one owner on the code's row, even inside a skill folder, at least
Standard when the prose needs judgment. Its accepted fixes stay on that row. Executable files and
tests are code.

Do the work yourself only when your model and effort match the selection or an explicit user
override. Otherwise use [selection handoff](#selection-handoff), and leave the parent's settings
unchanged. Report the selection and why.

### Raise the row

Escalate one row, or go straight to Hardest, when evidence shows the work is harder. Carry the
task, proof, partial work, and failed assumptions forward, and reconcile earlier writers first. A
product failure is a finding to diagnose or fix, not a reason to escalate until the check passes.

Document work rarely escalates. Hard or high-stakes prose stays on its row, and only repeated failed
attempts move it to Standard or Hardest. It and its fixes then keep the raised row unless a UI row
applies.

Reapply the first table when work turns out to change UI, need a dedicated operator, or edit
executable files or tests. Keep a raised row if it is higher, unless a UI row applies.

### Selection handoff

A child with delegation authority dispatches the selection, within its assigned scope.

A child without it stops at a safe checkpoint and returns a selection-change request: the row and
why, what is new since any earlier request, completed and remaining work with exact paths, checks
and failed assumptions, and active writers. This is incomplete work. The parent reconciles earlier
writers and partial changes, then dispatches the replacement.

The parent compares each request with the assignment's earlier ones. If it asks for the same or a
higher row and names no new check result, failed assumption, or artifact fact, report a blocker. A
verify-and-repair cycle that changes the artifact or check result is not a repeat.

A top-level session that cannot get its row reports that and asks.

## Reuse an agent

Prefer a retained agent when its context helps. You need not search for one. It must:

- Match the resolved model and effort exactly.
- Reach the right workspace and current revision.
- Hold current context, not stuck or anchored on failed assumptions.
- Keep that context under a continuation the host supports and permits for this work. A working
  continuation tool does not show that permission.

Otherwise use a new agent. [Recovery](#recover-work) takes precedence.

**Independence:** an agent that wrote or directed work stays out of its later independent
assessment. Pre-edit coverage follows the [coverage rule](../../review-fix-loop/SKILL.md#coverage-rule).
An earlier assessment alone does not end independence.

**Follow-up reviews and rechecks** prefer the original reviewer when it qualifies, its reports and
receipts are archived, and its context is free of same-round peer content. Otherwise, or when the
host requires a new task, give a new independent task the role's criteria and selection and the
prior evidence, and record it as a replacement. Either way, brief it under
[Review evidence](../../review/references/review-evidence.md).

**Reviewer to implementer:** a read-only reviewer can take accepted repairs once its pass is
complete, its outputs are archived, and findings are settled. Its brief lists the repairs and
explicitly replaces the read-only assignment. Already authorized implementation needs no new human
approval.

## Recover work

Keep partial results and the failure cause. A caller's failure policy, such as
[additional-review skips](../../review-fix-loop/references/review-assignments.md#handle-failures),
overrides the retry below. Use a new key for any fresh run after terminal failure.

| Failure | Action |
| --- | --- |
| Uncertain dispatch or lost response | Repeat with its existing key in the same provider session |
| Uncertain dispatch or lost response after a session change | Treat each tracked key, with or without an ID, as a pending run. Read known IDs through the host's route and collect finished results. Treat a live run as a wait timeout. If a read-only run stays unknown, apply its caller's failure policy. If any other run stays unknown, start no overlapping work and report a blocker |
| Wait timeout | The run is still live. Follow the host's next step |
| Transient terminal or provider runtime failure | May retry once per target per workflow, then treat it as unavailable |
| Quota, or an unavailable model or provider | The [listed fallback](#availability-fallback) with no retry. Otherwise report the blocker and resume when conditions change |
| Authentication failure | Stop and report it, or request the login through the host's secret route. Retry once resolved |
| Permission or policy denial | Stop the blocked action. Another model or transport does not authorize it |
| Wrong answer, failed product check, or task difficulty | Diagnose or escalate |

**Replacing work:** before a replacement overlaps earlier writers, account for pending runs and
reconcile their files. A cancellation or terminal receipt alone does not show writers stopped.

### Availability fallback

A row's fallback applies only when the row supplied the selection. If the user named the model,
report a blocker and wait unless the user authorized a substitute. Other explicit selections need
their own authorized fallback. A fallback never authorizes unlisted models, the Simple tier, or a
change to additional-review skip policy.

Record the failed selection, evidence, and fallback. Keep the assignment's scope, requirements,
verification bar, and review criteria, and the exact fallback until availability changes or the user
directs otherwise.

A review fallback runs in a new independent task and never reuses another result.

For implementation and document work, if the fallback matches a still-running owner, keep that
owner, record the failed escalation, and pass it the reassessed selection and evidence. If the run
has ended, dispatch a new fallback task with the saved handoff.
