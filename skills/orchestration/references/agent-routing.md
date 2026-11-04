# Agent routing

T3's injected orchestration instructions and live tool descriptions own the API,
transport, permissions, task state, and workspace binding. Read those when you
dispatch.

## Model defaults

| Purpose | Provider | Model | Effort | Availability fallback | Review pool |
| --- | --- | --- | --- | --- | --- |
| UI implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Simple implementation and fixes | Codex | GPT-6.1 Sol | Medium | — | — |
| Standard implementation and fixes | Claude | Opus 5.5 | High | Codex / GPT-6.1 Sol / High | — |
| Hardest implementation and fixes | Claude | Opus 5.5 | X-High | Codex / GPT-6.1 Sol / High | — |
| Document writing and revision | Claude | Opus 5.5 | Medium | Codex / GPT-6.1 Sol / Medium | — |
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

The primary-review row also sets the model for cross-judges and single-reviewer
audits.

- **Implementation** rows cover code, builds, tests, refactoring, configuration,
  non-interactive verification, and accepted code fixes.
- **Document writing and revision** covers prose: skills, agent instructions,
  READMEs, other docs, and accepted fixes to them.
- **General research** covers source reading, comparison, and synthesis.
  [Research](../../research/SKILL.md#source-routing) uses the YouTube and X
  retrieval rows. These rows set routing policy, not exclusive source access.

Use the exact [OpenCode Go model IDs](https://opencode.ai/v2/docs/console/go/#models)
above. They keep the subscription route, so leave free or other paid endpoints out.

User instructions override these defaults. Keep explicit user choices when you
apply project requirements.

Resolve names and effort through `orchestrator_capabilities` to exact available
provider-instance and model IDs and supported options. Use a caller or project
choice to settle multiple matches. Otherwise report the ambiguity. Gemini's effort
can be encoded in its model ID. Pass the complete resolved selection, because
[T3 replaces supplied options](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1001)
rather than merging them with inherited ones.

## Choose working selection

Pick a selection for each bounded assignment before you work or dispatch. Take the
first match:

1. Operating a computer, browser, desktop app, or device UI, including verifying
   an interactive workflow, uses an [interaction row](#choose-interaction-effort).
   Split work that also builds UI, as described below.
2. Building or changing UI uses the UI implementation row, however small or hard.
   That includes a one-line CSS, SwiftUI, or UIKit fix.
3. Writing or revising prose uses the document row, however small. A doc update
   that ships with a code change stays with that change's implementer. Executable
   files and tests use implementation rows, even inside a skill folder.
4. Other implementation uses a [tier](#choose-implementation-tier).

Source review and programmatic research, including of UI, keep their named review
and research rows.

When a task is hard or an answer is poor, diagnose or escalate. Report the chosen
selection and why in the assignment or handoff.

### Choose interaction effort

- **Routine:** a well-understood, linear flow. Still check intermediate and final
  states.
- **Demanding:** branching, uncertain state, recovery, or several interacting
  assertions.
- **Complex:** complex edge cases, or a high cost of a false pass.

Escalate on
evidence of missed checks, state mismatches, or inconsistent judgments. Treat a
real product failure as a finding to diagnose or fix, not as a reason to escalate
until the check passes. An interaction row changes the model, not permissions or
action authorization.

Split work that both builds and drives. The implementation selection builds. The
interaction selection then operates and verifies, and returns product failures to
implementation for repair. Each handoff carries expected and observed states,
evidence, unresolved checks, and session or tool references.
[Selection handoff](#selection-handoff) and writer reconciliation apply.
[Verify](../../verify/SKILL.md) owns acceptance assertions and verdicts.

### Choose implementation tier

Standard is the default:

- **Simple:** only when the evidence clearly shows a small, mechanical task with
  an obvious check, such as a code typo, rename, or formatting fix.
- **Standard:** all other implementation, fixes, diagnosis, and non-interactive
  verification.
- **Hardest:** unresolved architectural tradeoffs, subtle state or concurrency
  invariants, or repeated failed approaches that require challenging shared
  assumptions.

Small size alone does not make a task Simple; a small concurrency fix can be
Hardest.

Reassess when investigation or failed checks show the work is harder. Escalate one
tier, or go straight to Hardest when the evidence warrants it. Document work rarely
escalates: hard or high-stakes prose stays on its row, and only repeated failed
attempts move it to Standard or Hardest. It and its accepted fixes then keep the
raised row unless check 1 or 2 applies. Reapply the
ordered checks when work turns out to change UI, need interactive operation, or
edit executable files or tests. Carry the task, proof, partial work, and failed
assumptions into the next assignment, and reconcile earlier writers before a
handoff.

### Selection handoff

A child with delegation authority stays within its assigned scope.

A child without that authority stops at a safe checkpoint and returns a
selection-change request to its parent. The request gives the row wanted and why,
what is new since any earlier request, completed and remaining work with exact
paths, checks and failed assumptions, and any active writers. This is incomplete
work awaiting reassignment, not a finished task. The parent reconciles earlier
writers and partial changes, then dispatches the replacement.

The parent compares each request with the assignment's earlier ones. If a request
asks for the same or a higher row and names no new check result, failed assumption,
or artifact fact, report a blocker. A verify-and-repair cycle that changes the
artifact or the check result is not a repeat.

A top-level session that cannot get the row reports that to the user and asks.

## Dispatch and track

Each child must support the resolved model and options. Use a generic role when
custom ranks would override them. The brief defines obligations; T3's broad `role`
is not a model preset.

For a native slash command through `delegate_task`, use `role: general` and start
`task` with the command. Other roles put text before the command.

Shared-checkout children need disjoint writes and one-at-a-time git and index
operations. For a separate checkout, use the host's worktree-isolated delegation.
Confirm its starting revision and supply uncommitted inputs explicitly, since they
may not be copied.

The default local ceiling is 12 active children, lowered by host or user limits.
Count workers and reviewers together. Start ready assignments as slots free. Keep
each task's request key, ID, selection, owned output, and state.

A wait timeout leaves work live, so reconcile its state before replacing it.

Before a replacement overlaps earlier writers, account for pending child runs and
reconcile their files. Cancellation or a terminal receipt alone does not show that
every later or nested writer has stopped.

### Reuse an agent

For new work, prefer a retained agent you already know of when its context would
help. You need not search for one. It must match the assignment's model and effort
exactly, reach the right workspace and current revision, and keep its context under
a continuation the host supports. Choose a new
agent when that context is stale, the agent repeats failed assumptions, or the work
needs an independent attempt. [Recover work](#recover-work) and
[availability fallback](#availability-fallback) take precedence.

A read-only reviewer can take accepted repairs after its whole review pass is
complete, its reports and receipts are archived under
[Review evidence](../../review/references/review-evidence.md), and the caller or
Review Sweep has settled the findings. Its brief lists those repairs and explicitly
replaces the read-only assignment. Already authorized implementation needs no new
human approval.

An agent that wrote or directed a change stays out of later independent assessment
of it. Its earlier pre-edit coverage follows
[carry-forward rules](../../review-fix-loop/SKILL.md#review-settle-repeat). Each
independent review or recheck is a fresh delegated task.

## Recover work

Repeat an uncertain dispatch with its existing key in the same provider session,
so it resolves to the same work
([T3 command identity](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1531)).
A fresh run after terminal failure, including a retry in the same review round,
needs a new key. Reconcile retained IDs before replacing work after a session
change or lost response.

Keep partial results and the failure cause. Then, unless the caller sets a different
failure policy:

- **Transient terminal failure:** one fresh-task retry per target per workflow.
- **Quota or unavailable model:** use a listed fallback. Otherwise report the
  blocker and resume when conditions change.
- **Authentication failure:** stop and report it, or request the login through the
  host's secret route. Retry once it is resolved.
- **Permission or policy denial:** stop the blocked action. Another model or
  transport does not authorize it.

A failed required selection with no listed fallback stays a blocker after permitted
recovery. A fallback never authorizes unlisted models or changes additional-review
skip policy.

### Availability fallback

Use a row's listed fallback automatically when the assignment uses that row's
provider and model and the selection cannot run because of quota, an unavailable
model or provider, or a provider runtime failure. A wrong answer or failed product
check is not a runtime failure. Authentication and permission failures follow the
recovery rules above. Other explicit selections need their own authorized fallback.

Record the failed selection, failure evidence, and fallback. A transient runtime
failure may use the one retry above first. Confirmed quota or unavailability needs
no retry. Reconcile partial work and earlier writers before starting a replacement.

Keep the assignment's scope, requirements, verification bar, and review criteria. A
review fallback still does that role's review in a fresh independent task. It does
not reuse the implementer's result or another assessment as its coverage.

A user choice that excludes substitution stays a blocker. If the fallback also
cannot run, report the blocker.

Keep the exact fallback model and effort for that assignment until availability
changes or the user directs otherwise. Task difficulty alone must not send the
assignment back to its unavailable selection.

If the fallback matches a still-running owner of that assignment, keep that owner
and record the failed escalation rather than starting a duplicate. Pass the reassessed selection and evidence to that owner. If the former
run has ended, dispatch a fresh fallback task with the saved handoff.

Dispatch identity and stored thread options confirm configuration, not which model
the provider ran.
