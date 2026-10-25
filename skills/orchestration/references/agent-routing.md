# Agent routing

Use this reference to select a model and execute a delegated assignment.
T3's injected orchestration instructions and live tool descriptions own the
API, transport, permissions, task state, and workspace binding. Read those
when dispatching; this reference owns SreeStack's defaults and execution policy.

## Model defaults

Edit this table to change the defaults.

| Purpose | Provider | Model | Effort | Alternate priority |
| --- | --- | --- | --- | --- |
| Implementation and fixes | Codex | GPT-6.1 Sol | High | — |
| General research | Codex | GPT-6.1 Sol | Medium | — |
| YouTube retrieval | Antigravity | Gemini 4 Argon | High | — |
| X retrieval | Grok | Grok 4.7 | High | — |
| Primary review | Codex | GPT-6.1 Sol | High | — |
| Alternate review | OpenCode | `opencode/deepseek-v4.1-flash-free` | Max | 1 |
| Alternate review | OpenCode | `opencode/glm-5.3-flash-free` | Max | 1 |
| Alternate review | Antigravity | Gemini 4 Argon | Medium | 2 |
| Alternate review | Antigravity | Gemini 3.8 Flash | High | 3 |

The working selection covers code, tests, refactoring, configuration,
documentation changes, verification, and accepted fixes. The General research
selection covers source reading, comparison, and synthesis.
[Research](../../research/SKILL.md#source-routing) uses the YouTube and X retrieval
rows. These specify routing policy, not exclusive source access.
Alternate rows are a review pool; lower priority numbers are preferred.
Use the exact free OpenCode IDs above
to distinguish them from paid routes for the same models.
User instructions override defaults; preserve explicit user choices when
applying project requirements. Review Fix Loop's primary fallback is permitted
for alternate assessments unless the user requires a specific model/diversity.

Resolve names and effort through `orchestrator_capabilities` to exact available
provider-instance/model IDs and supported options. Use a caller/project choice
to disambiguate multiple matches; otherwise report the ambiguity. Gemini's
effort can be encoded in its model ID. Pass the complete resolved selection:
T3 replaces supplied options rather than merging them with inherited options.
[T3 selection semantics](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1001).

Direct-work ownership follows [Orchestration](../SKILL.md). Reviewers assess;
the working selection applies accepted fixes.

## Dispatch and track

Follow T3's native-versus-app-owned routing rule. A native child must support
the exact model/options; use a generic role when custom ranks would override
those settings. Use `delegate_task` for cross-provider or explicitly T3-owned
work, including Review Fix Loop. The assignment brief defines obligations;
T3's broad `role` is not a model preset.
[T3 execution policy](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/provider/T3OrchestrationInstructions.ts#L7).

Use fresh delegated tasks for bounded assignments and independent reviews.
Carry needed context in the brief. Shared-checkout children need disjoint writes
and serialized git/index operations. For a separate checkout, use the host's
worktree-isolated delegation. Confirm its starting revision and supply relevant
uncommitted inputs explicitly; they may not be copied. Follow live host workspace
rules. Ordinary top-level threads require an explicit user request.

The default local ceiling is 12 active children, reduced by host/user limits.
Count workers and reviewers together. Start ready assignments as slots free;
retain each task's request key, ID, selection, owned output, and state.

Prefer async dispatch. Do independent parent work, then yield for T3 delivery.
Use status when a result is needed mid-turn and cancel obsolete tasks through
their owning tool. A wait timeout leaves work live; confirm terminal state before
replacement. Follow live tool discovery/recovery instructions when T3 tools
are initially absent, and report any remaining capability gap.

Before overlapping a replacement with earlier writers, account for pending
child runs and reconcile their files. Cancellation or a terminal task receipt
alone does not establish that every later or nested writer has stopped.

## Recover work

Repeat an uncertain dispatch with its existing key in the same provider session
so it resolves to the same work. A fresh execution after terminal failure,
including a retry in the same review round, needs a new key. Reconcile retained
IDs before replacing work after a session change or lost response.
[T3 command identity](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/OrchestratorMcpService.ts#L1531).

Retain partial results and the failure cause. A transient terminal failure may
have one fresh-task retry per target per workflow. Quota, auth, or unavailable
models need changed conditions or a permitted alternate selection. Permission
or policy denials stop the blocked action; another model or transport does not
authorize it. Review Fix Loop owns alternate replacement and coverage decisions.
A failed required working/primary selection remains a blocker after its permitted
recovery; it is not permission to choose an unlisted model.

Report actual completion and evidence gaps. Dispatch identity and stored thread
options can confirm configuration, not provider execution fidelity. Acceptance
belongs to the parent under Orchestration; a task summary alone is not a pass.
