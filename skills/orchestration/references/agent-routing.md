# Agent routing

This reference owns SreeStack's model defaults, selection, reuse, and recovery
policy. [Orchestration](../SKILL.md) owns assignment, dispatch, and acceptance.
T3's injected instructions and live tool descriptions own the API, transport,
permissions, task state, and workspace binding.

## Model defaults

Edit this table to change the defaults.

| Purpose | Provider | Model | Effort | Availability fallback | Review pool |
| --- | --- | --- | --- | --- | --- |
| UI implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Simple implementation and fixes | Codex | GPT-6.1 Sol | Medium | — | — |
| Standard implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Hardest implementation and fixes | Claude | Opus 5.5 | X-High | Codex / GPT-6 Astra / X-High | — |
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

The primary-review row also supplies the selection used by cross-judges and
single-reviewer audits. [Research](../../research/SKILL.md#source-routing) uses
the YouTube and X retrieval rows; these specify routing policy, not exclusive
source access. [Review Fix Loop](../../review-fix-loop/SKILL.md) owns review
coverage, assignment selection, harness review, and optional-failure policy.

Use the exact OpenCode Go IDs above, preserving the subscription route rather
than substituting free or other paid endpoints.

Resolve names and effort through `orchestrator_capabilities` to exact available
provider-instance/model IDs and supported options. Use a caller/project choice
to disambiguate multiple matches; otherwise report the ambiguity. Gemini's
effort can be encoded in its model ID. Pass the complete resolved selection and
intended options using the live tool contract.

## Operate a UI

The agent already on a task operates a browser, computer, desktop app, or device
UI itself as a routine step when its tools reach the target. That step needs no
model match or new selection. This covers UI operation only: live host rules,
permissions, and action authorization still apply, and all other work keeps its
[working selection](#choose-working-selection), including UI code changes.

Use a dedicated operator only for:

- substantial UI work, such as a lengthy or difficult workflow;
- a specialized capability the agent's tools lack;
- required independent verification, using an operator
  [independent](#reuse-an-agent) of the assessed work;
- repeated operational difficulty, such as tool failures, state mismatches, or
  inconsistent judgments. A product failure is a finding for the implementer,
  not a handoff trigger.

Choose a tier only for a dedicated operator. It changes the model, not
permissions or action authorization:

| Tier | Use for |
| --- | --- |
| Routine UI operation | A well-understood, linear flow. Still check intermediate and final states |
| Demanding UI operation | Branching, uncertain state, recovery, or several interacting assertions |
| Complex UI operation | Complex edge cases, or a high cost of a false pass |

The handoff carries expected and observed states, evidence, unresolved checks, and
relevant session or tool references, under the
[selection handoff](#selection-handoff). The operator returns product failures to
the implementer for repair. [Verify](../../verify/SKILL.md) owns acceptance
assertions and verdicts.

## Choose working selection

Choose automatically for each bounded assignment before direct work or dispatch.
Explicit user selections and effort limits come first and hold through project
requirements, then a task-specific selection, then the first matching row:

| Assignment | Selection |
| --- | --- |
| Source review, including of UI | Its named review row |
| Research-only source reading, comparison, synthesis, or retrieval, including of UI | General research, or the YouTube or X row |
| [Dedicated UI operation](#operate-a-ui), including verifying an interactive workflow | Routine, Demanding, or Complex UI operation |
| Building or changing UI, however small | UI implementation at any difficulty, never Simple or Hardest |
| Diagnosis, design decisions, other code, builds, tests, refactoring, configuration, documentation, non-interactive verification, or accepted fixes | Simple, Standard, or Hardest implementation |

| Row | Use for |
| --- | --- |
| Simple | Evidence clearly shows a small, routine, mechanical task with an obvious check, such as a typo, rename, or formatting fix |
| Standard | The default, including diagnosis and substantive work with clear requirements or established patterns |
| Hardest | Rare cases where evidence shows Standard is insufficient: unresolved architectural tradeoffs, subtle state or concurrency invariants, or repeated failed approaches that require challenging shared assumptions |

Choose Standard when Simple is in doubt. Small size alone does not make a task
Simple; a small concurrency fix can be Hardest.

Continue directly only when this agent's effective model and effort match the
selection or an explicit user override. Otherwise use the
[selection handoff](#selection-handoff), preserving the parent's configuration.
Report the chosen selection and its concrete reason in the assignment or handoff.

**Reassess** when investigation, failed checks, missed checks, state mismatches,
or inconsistent judgments expose greater difficulty, and reapply the first table
when work turns out to change UI or need a dedicated operator. Escalate one row, or
directly to Hardest when the evidence warrants it. Carry the task, proof,
partial work, and failed assumptions into the next assignment, and reconcile
earlier writers first. A real product failure is a finding to diagnose or fix,
not by itself a reason to escalate until the check passes.

### Selection handoff

Follow the host's delegation authority for initial mismatches and later
escalation. A child with authority stays within its assigned scope. A child
without it stops at a safe checkpoint and returns a selection-change request:
the requested row and reason, completed and remaining work with exact paths,
checks and failed assumptions, and any active writers. This is incomplete work
awaiting reassignment. The parent reconciles earlier writers and partial changes,
then dispatches the selected replacement.

## Reuse an agent

Prefer a retained agent you already know of when its context would help; finding
one needs no search. It qualifies when it:

- matches the assignment's resolved model and effort exactly;
- reaches the correct workspace and current revision;
- holds useful context that is current, not stuck, and not anchored on failed
  assumptions;
- keeps that context under a continuation the host both supports and permits for
  this work. A working continuation tool does not establish that permission.

Otherwise use a new agent, as with an unavailable or deleted agent or work that
needs an independent attempt. Normal assignment rules still apply, and
[recovery](#recover-work) takes precedence.

**Independence** means separation from writing or directing the assessed work. An
agent that did either is excluded from later independent assessment of that work;
its pre-edit coverage follows the loop's
[coverage rule](../../review-fix-loop/SKILL.md#coverage-rule). An earlier
assessment alone does not end independence.

**Follow-up reviews and rechecks** prefer the role's original reviewer when it
qualifies, its reports and receipts are archived, and its context is free of
same-round peer content. Otherwise, or when the host requires a new task for
reviews or rechecks, start a new independent task with the role's criteria and
selection and supply the prior reports, receipts, and dispositions. Record it as a
replacement with prior evidence, not as continuation.

Either way the assessment is a new assignment with its own snapshot-bound brief,
output paths, and read proof under
[Review evidence](../../review/references/review-evidence.md). Earlier context
guides navigation; reads of the current snapshot supply the proof.

**Reviewer to implementer.** A read-only reviewer can take accepted repairs once
its whole pass is complete, its reports and receipts are archived, and the caller
or Review Sweep has settled the findings. Its brief lists those repairs and
explicitly supersedes the read-only assignment. Implementation already authorized
needs no new human approval.

## Recover work

Retain partial results and the failure cause. A caller's failure policy, such as
[additional-review skips](../../review-fix-loop/references/review-assignments.md#handle-failures),
overrides the retry below. Use a new key for any fresh execution after terminal
failure. Before replacing work, reconcile retained IDs and
[earlier writers](../SKILL.md#dispatch).

| Failure | Action |
| --- | --- |
| Uncertain dispatch or lost response | Repeat with its existing key in the same provider session so it resolves to the same work |
| Transient terminal or provider runtime failure | May retry once per target per workflow, including within a review round, before the listed fallback |
| Quota, or an unavailable model or provider | The [listed fallback](#availability-fallback) with no retry, otherwise wait for changed conditions |
| Authentication failure | Resolve authentication |
| Permission or policy denial | Stop the blocked action; another model or transport does not authorize it |
| Wrong answer, failed product check, or task difficulty | Diagnose or escalate |

A required selection without a usable fallback remains a blocker after permitted
recovery.

### Availability fallback

A row's fallback applies when the assignment uses that row's configured provider
and model. Other explicit selections need their own authorized fallback, and an
explicit user selection without substitution takes precedence. Use the exact
listed model and effort, and report a blocker if it also cannot run. A fallback
never authorizes unlisted models, the Simple tier, or a change to additional-review
skip policy.

Record the failed selection, failure evidence, and fallback. Preserve the
assignment's scope, requirements, verification bar, and review criteria. A review
fallback performs that role's review in a new independent task, rather than using
the implementer's result or another assessment as its coverage.

Keep the fallback for that assignment until availability changes or the user
directs otherwise; task difficulty alone never cycles it back to the unavailable
selection. For implementation, if the fallback matches a still-running owner,
keep that owner, record the failed escalation, and pass it the reassessed selection
and evidence. If the former run has ended, dispatch a new fallback task with the
saved handoff.

Dispatch identity and stored thread options can confirm configuration, not
provider execution fidelity.
