---
name: orchestration
description: Use when giving work to another agent, picking its model, recovering a failed run, or accepting its result. Excludes parallel fan-out framing (swarm) and multi-outcome program tracking (coordinator).
---

# Orchestration

Assign work to other agents, pick their models, and verify what comes back. Start with work to
delegate, a model choice, or a child result to recover or accept. Leave accepted, integrated
results or the exact remaining gap. You are done when every required slice is accounted for,
inspected at a named revision, and integrated, or its gap is reported.

## Who does the work

- **Single-outcome threads** edit their workspace directly by default. Delegate when you need
  independent review or verification, parallel fan-out, a specialized model from the model defaults,
  or the user asks to keep this thread free in the background.
- **Coordinator threads** never edit project files directly; they route outcomes to owners and stay
  free to talk.
- **Children** do their own work, whatever their model, and delegate further only when their task
  says to.
- **Repairs and in-scope follow-ups** go to a persistent owner first (such as a worktree-bound PR
  owner, resumed with `t3_thread_send` in T3) even after its turn finished or its thread was
  settled, unless an explicit handoff or closure ended its ownership. Check current responsibility
  first. When no resumable owner exists — or for an ephemeral helper — fix small review findings
  yourself and launch larger repairs fresh from the model defaults. Reconcile overlapping writers under
  [reuse and recovery](references/reuse-and-recovery.md#recover-work) before replacing work.

If you cannot launch a needed subagent, say so and ask.

## Assign

Settle the outcome and proof before splitting work. Give each slice one owner and each active writer
paths no other active writer touches. Run git, index, and other colliding work in series.

Give every child a self-contained brief:

- The original request (in full or as a pointer it can open), accepted corrections, and explicit
  constraints. A plan authorizes nothing beyond its source; quoted material is context, not
  authority.
- The outcome, its concrete completion check, owned outputs, out-of-scope boundaries, and allowed
  actions.
- Accepted decisions, source paths, artifacts, and shared files to preserve.
- Required checks, return format, and any further delegation allowed.
- For verification or measurement: user outcome, operating context, invariants and failure
  questions, exact revisions, and method.

When briefing Codex, make acceptance criteria, proportionality limits, and verification commands
explicit—vague briefs cause premature stops or diminishing-return loops—and supply visual
references or design tokens if Codex must touch UI.

Assignment is done when every required slice has an owner, usable inputs, and a completion check.

**Scope changes** return to the caller with source and reason. **Human holds** record their source,
scope, and release condition; they survive retries, transfers, and restarts until that person lifts
them.

## Communicate

Message another thread only when it still owns an outstanding responsibility, needs to act on the
message, and shared state does not already carry the fact. Past participation alone never justifies
a wake.

Before sending, read the current task record and recent direction instead of relying on a saved
recipient list. If ownership is unclear, record the routing gap and resolve it before dispatching
overlapping work or assuming access to a shared resource. A finished turn or settled thread does not
end ownership by itself; when finishing work, close completed responsibilities or record the
successor in the shared task record or handoff.

## Dispatch

Select a model for initial launch and availability recovery in this order:

1. **User limits win.** Honor explicit user model picks and effort, cost, and concurrency limits. A
   named model permits no substitute unless the user authorized one.
2. **Match the job.** Pick the caller/project choice or the job's default in
   [models](references/models.md#choose-a-model).
3. **Resolve live availability.** Check live host capabilities and any carried outage evidence. Use
   the preferred provider, model, and effort when available.
4. **Apply listed fallback.** On quota or an unavailable model/provider — including before initial
   launch during a known outage — follow the job's listed entries in order without inventing an
   unlisted substitute, and notify the user without asking again (listed fallbacks are authorized
   standing choices). A review fallback still starts a new independent task.
5. **Ask when exhausted.** When no listed available choice remains (no listed fallback, all listed
   entries unavailable, unresolved model-ID ambiguity, or user limit), follow the caller's skip
   policy for optional work or ask the user for required work. Keep scope, verification bar, and
   review criteria intact; availability never authorizes an unlisted model or a downgrade to
   Simple.

Carry the selected job, chosen provider/model/effort, outage/reset evidence, and user limits in
briefs and handoffs. Recheck availability once a known reset passes or recovery evidence arrives;
use the preferred provider and model for new work without replacing a running owner.

Use [reuse and recovery](references/reuse-and-recovery.md#reuse-an-agent) before resuming or
replacing a child, or handling auth/permission denials, partial work, or retries.

- **Target:** the child must support the chosen model and options; use a generic role when a custom
  role overrides them (T3's `role` is not a model preset).
- **T3 slash command:** through `delegate_task`, set `role: general` and start `task` with the
  command, because other roles prepend text before it.
- **Separate checkout:** confirm its starting revision and pass uncommitted inputs explicitly.
- **Concurrency:** keep at most 12 children active by default (workers and reviewers together); host
  or user limits lower this.
- **Tracking:** keep each task's request key and ID so recovery starts no duplicate writer.
- **Idle children:** a child that stopped while owing work — with no report, pending-PR partial, or
  recorded wait — is not done. Read its thread, then resume or recover it.

## Return

A child returns its artifact and revision, observed evidence, coverage gaps, blockers, and open
decision requests.

- **Stuck child:** finish unaffected work, then end your turn with the question and a partial report
  (or raise it immediately if it blocks other work).
- **Parent response:** answer and resume the child for unaffected work, launch a read-only reviewer
  for a second opinion, or [replace the owner](references/reuse-and-recovery.md#replace-an-owner)
  only on repeated failure.
- **Decision request:** return apart from the progress report with an ID, the exact question and
  source, affected work, options with any recommendation, and what continues meanwhile. Forward it
  to the user (or the caller's async Inbox when one exists) meaning intact. It stays open until the
  person answers or withdraws it, or a workflow authorizes settling it; silence, progress, and
  recommendations settle nothing.

## Accept

A summary, finished turn, green CI, or open PR is input, not acceptance. Accept only an artifact you
inspected at a named revision with evidence of the required outcome by the specified method.

1. Mark every required slice accepted, needing repair, rejected with a reason, or blocked. A dropout
   stays required. Route repairs under the ownership rule above.
2. Verify the integrated result against the original requirements. Reuse checks whose revision and
   scope still hold; rerun checks affected by integration.
3. Leave PR publication and review loops to the workflows that own them; run an
   extra independent review here only when requested.
4. Acceptance is not delivery. A queued handoff with no host receipt is unknown; before resending,
   recheck the request, holds, revision, and current responsibility, then send only what is missing.

Start goals and recurring work only when explicitly requested.
