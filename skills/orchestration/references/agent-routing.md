# Agent routing

Use this reference to select a model and execute a delegated assignment.
T3's injected orchestration instructions and live tool descriptions own the
API, transport, permissions, task state, and workspace binding. Read those
when dispatching; this reference owns SreeStack's defaults and execution policy.

## Model defaults

Edit this table to change the defaults.

| Purpose | Provider | Model | Effort | Availability fallback | Review pool |
| --- | --- | --- | --- | --- | --- |
| UI implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Simple implementation and fixes | Codex | GPT-6.1 Sol | Medium | — | — |
| Standard implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Hardest implementation and fixes | Claude | Opus 5.5 | X-High | Codex / GPT-6.1 Sol / High | — |
| Routine interaction | Codex | GPT-6.1 Terra | Medium | — | — |
| Demanding interaction | Codex | GPT-6.1 Terra | High | — | — |
| Complex interaction | Codex | GPT-6.1 Terra | X-High | — | — |
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
single-reviewer audits.

Implementation selections cover code, builds, tests, refactoring, configuration,
documentation changes, non-interactive verification, and accepted fixes. Interaction selections cover
operating a computer, browser, desktop app, or device UI, including verifying
interactive workflows. The General research selection covers source reading,
comparison, and synthesis.
[Research](../../research/SKILL.md#source-routing) uses the YouTube and X retrieval
rows. These specify routing policy, not exclusive source access.
[Review Fix Loop](../../review-fix-loop/SKILL.md) owns review coverage, assignment
selection, harness review, and optional-failure policy.
Use the exact OpenCode Go IDs above, preserving the subscription route rather
than substituting free or other paid endpoints.
[OpenCode Go model IDs](https://opencode.ai/v2/docs/console/go/#models).
User instructions override defaults; preserve explicit user choices when
applying project requirements.

Resolve names and effort through `orchestrator_capabilities` to exact available
provider-instance/model IDs and supported options. Use a caller/project choice
to disambiguate multiple matches; otherwise report the ambiguity. Gemini's
effort can be encoded in its model ID. Pass the complete resolved selection:
T3 replaces supplied options rather than merging them with inherited options.
[T3 selection semantics](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1001).

## Choose working selection

Choose the selection automatically for each bounded assignment before direct
work or dispatch, checking in this order:

1. Operating a computer, browser, desktop app, or device UI, including verifying
   an interactive workflow, uses an [interaction row](#choose-interaction-effort).
   Split assignments that also build UI as described below.
2. Building or changing UI uses the UI implementation row, however small,
   including a one-line CSS, SwiftUI, or UIKit fix. UI work never uses Simple.
   UI work stays at this row regardless of difficulty; it does not use Hardest.
3. Other implementation uses a tier below.

Source review and programmatic research, including of UI, keep their named
review and research rows. Builds, unit tests, and other checks that need no
interactive operation keep the implementation selection.

Task difficulty or an unsatisfactory answer calls for diagnosis or escalation,
not an availability fallback. Honor explicit user selections and effort limits.
Report the chosen selection and its concrete reason in the assignment or handoff.

### Choose interaction effort

- **Routine:** a well-understood, linear flow. Still check intermediate and
  final states.
- **Demanding:** branching, uncertain state, recovery, or several interacting
  assertions.
- **Complex:** complex edge cases, or a high cost of a false pass.

Choose a higher row upfront when known complexity warrants it. Escalate on
evidence of missed checks, state mismatches, or inconsistent judgments. A real
product failure is a finding to diagnose or fix, not by itself a reason to
escalate until the check passes. An interaction row changes the model, not
permissions or action authorization.

Split work that both builds and drives. The implementation selection builds;
the interaction selection then operates and verifies, and returns product
failures to implementation for repair. Each handoff carries expected and
observed states, evidence, unresolved checks, and relevant session or tool
references. [Selection handoff](#selection-handoff) and writer reconciliation
apply. [Verify](../../verify/SKILL.md) owns acceptance assertions and verdicts.

### Choose implementation tier

Standard is the default:

- **Simple:** only when the evidence clearly shows a small, routine, mechanical
  task that needs little judgment, such as a typo, rename, or formatting fix
  with an obvious check.
- **Standard:** all other implementation, fixes, diagnosis, and non-interactive
  verification, including substantive work with clear requirements or
  established patterns.
- **Hardest:** unresolved architectural tradeoffs, subtle state or concurrency
  invariants, or repeated failed approaches that require challenging shared
  assumptions. Choose this tier when the depth of uncertainty and judgment
  warrants its configured effort.

Choose Standard when Simple is in doubt. Small size alone does not make a task
Simple; a small concurrency fix can be Hardest.

Reassess when investigation or failed checks expose greater difficulty. Escalate
Simple to Standard, or Standard to Hardest, as needed; choose Hardest directly
when the evidence already warrants it. Reapply the ordered checks when work
turns out to change UI or need interactive operation. Carry the task,
proof, partial work, and failed assumptions into the next assignment. Reconcile
earlier writers before a handoff.

### Selection handoff

Follow the host's delegation authority for both initial selection mismatches and
later escalation. A child without permission to delegate stops work
at a safe checkpoint and returns a selection-change request to its parent.
Include the requested row and reason, completed and remaining work with exact
paths, checks and failed assumptions, and any active writers. This is incomplete
work awaiting reassignment, not a completed task. The parent reconciles earlier
writers and partial changes, then dispatches the selected replacement. A child
with delegation authority stays within its assigned scope.

## Dispatch and track

Follow live host routing and task-lifecycle rules. Each child must support the
resolved model/options; use a generic role when custom ranks would override
them. The assignment brief defines obligations; T3's broad `role` is not a model
preset.

For a native slash command through `delegate_task`, use `role: general` and
start `task` with the command. Other roles prepend text before the command.

Use fresh delegated tasks for independent reviews, and for other bounded
assignments unless [reuse](#reuse-an-agent) fits.
Carry needed context in the brief. Shared-checkout children need disjoint writes
and serialized git/index operations. For a separate checkout, use the host's
worktree-isolated delegation. Confirm its starting revision and supply relevant
uncommitted inputs explicitly; they may not be copied.

The default local ceiling is 12 active children, reduced by host/user limits.
Count workers and reviewers together. Start ready assignments as slots free;
retain each task's request key, ID, selection, owned output, and state.

Prefer async dispatch and follow the returned next action. A wait timeout leaves
work live; reconcile its state before replacement.

Before overlapping a replacement with earlier writers, account for pending
child runs and reconcile their files. Cancellation or a terminal task receipt
alone does not establish that every later or nested writer has stopped.

### Reuse an agent

For new work, prefer a retained agent you already know of when its context would
help; finding one needs no search. It must match the assignment's resolved model
and effort exactly, reach the correct workspace and current revision, and keep
that context under a continuation the host supports. Normal assignment rules
still apply. Choose a new agent when that context is stale, the agent repeats
failed assumptions, or the work needs an independent attempt.
[Recover work](#recover-work) and [availability fallback](#availability-fallback)
take precedence.

A read-only reviewer can take accepted repairs once its whole review pass is
complete, reports and receipts are archived under
[Review evidence](../../review/references/review-evidence.md), and the caller or
Review Sweep has settled the findings. Its brief lists those repairs and
explicitly supersedes the read-only assignment. Implementation already
authorized needs no new human approval.

An agent that wrote or directed a change is excluded from later independent
assessment of that change. Its earlier pre-edit coverage follows
[carry-forward rules](../../review-fix-loop/SKILL.md#review-settle-repeat). Each
independent review or recheck is a fresh delegated task.

## Recover work

Repeat an uncertain dispatch with its existing key in the same provider session
so it resolves to the same work. A fresh execution after terminal failure,
including a retry in the same review round, needs a new key. Reconcile retained
IDs before replacing work after a session change or lost response.
[T3 command identity](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1531).

Retain partial results and the failure cause. Unless the caller defines a
different failure policy, a transient terminal failure may have one fresh-task
retry per target per workflow. Quota or unavailable models need changed conditions
or a listed fallback. Authentication failures need resolved authentication.
Permission or policy denials
stop the blocked action; another model or transport does not authorize it.

Failed required selections without a listed fallback remain blockers after
permitted recovery. A fallback never authorizes unlisted models or changes
additional-review skip policy.

### Availability fallback

When an assignment uses its row's configured provider and model, that row lists
a fallback, and the selection cannot run because of quota, an unavailable
model/provider, or a provider runtime failure, use that fallback automatically.
A wrong answer or failed product check is not a runtime failure, and
authentication or permission failures follow the recovery rules above.
Other explicit selections require their own authorized fallback. Record the failed
selection, failure evidence, and fallback. A transient runtime failure may use
the one retry above before fallback; confirmed quota or unavailability needs no
retry. Reconcile partial work and earlier writers before starting a replacement.

Preserve the assignment's scope, requirements, verification bar, and review
criteria. A review fallback still performs that role's review in a fresh
independent review task; it does not reuse the implementer's result or another
assessment as its coverage. An explicit user selection without substitution
takes precedence. If the fallback also cannot run, report the blocker. A
fallback is the row's listed selection, never the Simple tier. Keep the exact
fallback model and effort for that assignment until availability changes or the
user directs otherwise; task difficulty alone must not cycle the assignment back
to its unavailable selection. For implementation, if the
fallback matches a still-running owner of that assignment, keep that owner and
record the failed escalation rather than starting a duplicate replacement.
Pass the reassessed selection and evidence to that owner. If the former run has ended,
dispatch a fresh fallback task with the saved handoff instead.

Dispatch identity and stored thread options can confirm configuration, not
provider execution fidelity.
