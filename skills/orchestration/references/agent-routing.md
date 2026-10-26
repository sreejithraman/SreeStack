# Agent routing

Use this reference to select a model and execute a delegated assignment.
T3's injected orchestration instructions and live tool descriptions own the
API, transport, permissions, task state, and workspace binding. Read those
when dispatching; this reference owns SreeStack's defaults and execution policy.

## Model defaults

Edit this table to change the defaults.

| Purpose | Provider | Model | Effort | Review pool |
| --- | --- | --- | --- | --- |
| Implementation and fixes | Codex | GPT-6.1 Sol | High | — |
| General research | Codex | GPT-6.1 Sol | Medium | — |
| YouTube retrieval | Antigravity | Gemini 4 Argon | High | — |
| X retrieval | Grok | Grok 4.7 | High | — |
| Required review | Codex | GPT-6.1 Sol | High | — |
| Additional review | OpenCode | `opencode-go/deepseek-v4.1-flash` | Max | OpenCode Go |
| Additional review | OpenCode | `opencode-go/glm-5.3-flash` | Max | OpenCode Go |
| Additional review | Antigravity | Gemini 4 Argon | High | Gemini |
| Additional review | Antigravity | Gemini 3.8 Flash | High | Gemini |

The required-review row is also the primary review selection used by
cross-judges and single-reviewer audits.

The working selection covers code, tests, refactoring, configuration,
documentation changes, verification, and accepted fixes. The General research
selection covers source reading, comparison, and synthesis.
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

## Dispatch and track

Follow live host routing and task-lifecycle rules. Each child must support the
resolved model/options; use a generic role when custom ranks would override
them. The assignment brief defines obligations; T3's broad `role` is not a model
preset.

For a native slash command through `delegate_task`, use `role: general` and
start `task` with the command. Other roles prepend text before the command.

Use fresh delegated tasks for bounded assignments and independent reviews.
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

## Recover work

Repeat an uncertain dispatch with its existing key in the same provider session
so it resolves to the same work. A fresh execution after terminal failure,
including a retry in the same review round, needs a new key. Reconcile retained
IDs before replacing work after a session change or lost response.
[T3 command identity](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1531).

Retain partial results and the failure cause. Unless the caller defines a
different failure policy, a transient terminal failure may have one fresh-task
retry per target per workflow. Quota, auth, or unavailable models need changed
conditions or a permitted alternate selection. Permission or policy denials
stop the blocked action; another model or transport does not authorize it.
A failed required selection remains a blocker after permitted recovery;
it is not permission to choose an unlisted model.

Dispatch identity and stored thread options can confirm configuration, not
provider execution fidelity.
