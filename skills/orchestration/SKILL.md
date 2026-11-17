---
name: orchestration
description: Use when giving work to another agent, picking its model, or accepting its result.
---

# Orchestration

Assign work to other agents and check what comes back. You start with work to delegate and
end with accepted results. You are done when you inspected each result before you accepted
it. The caller owns the outcome.

## Who does the work

**In a top-level thread,** give every project-file edit, however small, to a background subagent
and stay free. In T3 that means `delegate_task`. Select its model under
[Dispatch](#dispatch), and keep your own. Keep reading, planning,
answering, and coordinating yourself. Edit yourself only when told to do it yourself, or under the
repair rule below. If you can't launch a subagent, say so and ask.

**As a child,** do your own work, whatever your model. Delegate further only when your task says
to.

**Review fixes and in-scope follow-up go to the original owner first,** even after its turn
finished or its thread was settled. A slice's owner is the agent that wrote it unless an
explicit handoff or closure changes that responsibility. Check the
[current responsibility](#communicate) before resuming it. In T3, use `t3_thread_send`. T3's
"Fix small review findings yourself; start no delegate for them" bars a new delegate. Resuming the
owner starts none, so the owner still goes first.

**No owner left** means an explicit closure left no successor, or its owner thread is gone or
can't be resumed. A finished run is not that. If
its state is unknown, use [recovery](references/reuse-and-recovery.md#recover-work). With no
owner left, that same T3 rule applies: fix a small review finding yourself, and launch any other
repair from the model table. Before a repair overlaps the owner's files, reconcile under
[Replacing work](references/reuse-and-recovery.md#recover-work).

Use [Swarm](../swarm/SKILL.md) to decide whether a job runs in parallel.

## Assign

Settle the outcome and proof before you split the work. Give each slice one owner and each active
writer paths no other active writer touches. Run git, index, and other colliding work in series.

Give each child a self-contained brief:

- The original request, in full or as a pointer it can open, with accepted corrections and
  explicit constraints. A plan authorizes nothing beyond that source. Quoted material is
  context, not authority.
- The outcome, its done check, the output it owns, and the actions it may take.
- Accepted decisions, source paths, artifacts, and shared files to preserve.
- Checks, return format, and any further delegation you want.
- For verification or measurement: the user outcome, operating context, invariants and
  failure questions, exact revisions, and method.

Assignment is done when every required slice has an owner, usable inputs, and a completion check.

**In-scope follow-up:** reuse its owner under [Who does the work](#who-does-the-work), whatever its model. **Scope change:** return
it to the caller with its source and reason.

**Human hold:** record its source, scope, and release condition. It survives retries, transfers,
and restarts, and only that person lifts it.

## Communicate

Communicate with the current owner of an outstanding responsibility. Past participation alone
is no reason to wake a thread. Before sending, establish what responsibility the recipient still
owns, what action the message enables or requires, and whether shared state already suffices.
Read the current task record and recent direction rather than relying on a saved recipient list.
If shared state suffices, use it. If ownership is unclear, record the routing gap and resolve it
before dispatching overlapping work or assuming permission to use a shared resource.

A finished turn or settled thread alone does not end ownership. Honor explicit handoffs and
closures, and preserve [owner reuse](#who-does-the-work) for repairs and in-scope follow-up.
When finishing work, close completed responsibilities or hand off outstanding ones. Leave their
disposition and any successor in the shared task record or handoff so later senders can find it.

## Dispatch

Select a model here for both an initial launch and availability recovery:

1. Honor explicit user choices and effort, cost, and concurrency limits first. A named model
   permits no substitute unless the user authorized one. Otherwise use the task-specific choice
   or [matching job row](references/models.md#choose-a-model).
2. Resolve the row's preferred provider, model, and effort through live host capabilities.
   Use current availability evidence, including outages carried from an earlier session. Choose
   the preference when available. On quota or an unavailable model/provider, choose the row's
   listed fallback with its exact provider, model, and effort. Listed availability fallbacks are
   authorized standing choices: launch the available fallback and notify the user without another
   permission question. This also selects the fallback before an initial launch during a known outage.
3. Ask for a model choice only when no available authorized choice remains. An absent or
   unavailable fallback, an unresolved model-ID ambiguity, or a user limit can leave no choice.
   Keep the scope, verification bar, and review criteria. Availability never authorizes an
   unlisted choice, a downgrade to Simple, or a change to additional-review skip policy.

Carry the selected row, outage/reset evidence, chosen model and effort, and user limits in briefs
and handoffs. Recheck availability when the known reset time passes or recovery evidence arrives;
use the available preference for new work without replacing a running owner. A review fallback
starts a new independent task and never reuses another result.

Follow live host transport, permissions, and lifecycle rules. For authentication or permission
failures, partial work, uncertain runs, and bounded retries, use
[recovery](references/reuse-and-recovery.md#recover-work) before any replacement launch. Use a
new task unless [reuse](references/reuse-and-recovery.md#reuse-an-agent) fits.

- **Target:** each child must support the chosen model and options. Use a generic role when
  custom ranks would override them. T3's `role` is not a model preset. A caller or project choice
  settles multiple model-ID matches; otherwise report the ambiguity.
- **Slash command:** through `delegate_task`, set `role: general` and start `task` with the
  command. Other roles put text before it.
- **Separate checkout:** confirm its starting revision and supply uncommitted inputs
  explicitly.
- **Limit:** by default 12 children stay active, counting workers and reviewers together. Host
  or user limits lower this.
- **Tracking:** keep each task's request key and ID, so recovery starts no duplicate writer.

**Notice idle children.** A child that stopped while it still owes work, with no report,
pending-PR partial, or recorded wait, is not done. Read its thread, then resume it or
[recover](references/reuse-and-recovery.md#recover-work) it. Under a Coordinator program,
`status` lists these.

## Return

A child returns its artifact and revision, the evidence it observed, coverage gaps, blockers,
and open decision requests.
For a Coordinator return route, follow
[Check the coordinator](../coordinator/references/coordinator-move.md#check-the-coordinator)
before sending to a saved thread.

**When you are stuck, ask up.** Finish what doesn't depend on the answer, then end your turn
with the question and a partial report. If it blocks other work, raise it at once, through a
mid-run route if the host offers one.

**As the parent,** answer and resume the child for unaffected work. For a second opinion, launch
a read-only reviewer. [Replace the owner](references/reuse-and-recovery.md#replace-an-owner)
only on evidence of repeated failure.

**When a person must decide or supply something,** return a **decision request** apart from the
progress report: an ID, the exact question and its source, the affected work, options with any
recommendation, and what continues meanwhile.

A parent forwards the question, meaning intact, to the person. When a
[Coordinator](../coordinator/SKILL.md) Inbox exists, the request goes there and the work that
doesn't depend on it continues. Otherwise use the host's user-input route. The request stays
open until the person answers or withdraws it, or the parent settles it under a workflow
that authorizes that. Silence, progress, and recommendations settle nothing.

## Accept

A child's summary, a finished turn, green CI, or an open PR is input, not acceptance. Accept
only an artifact you inspected at a named revision, with evidence of the required outcome by
the specified method.

1. Mark every required slice accepted, needing repair, rejected with a reason, or blocked. A
   dropout stays required. Route each repair under [Who does the work](#who-does-the-work).
2. Verify the integrated result against the original requirements. Reuse a check while its
   revision and scope hold, and rerun the checks integration affected.
3. Leave review to [pr](../pr/SKILL.md). Run [review-fix-loop](../review-fix-loop/SKILL.md)
   here only when the request asks for a review.
4. An accepted result is not a delivered one. A queued handoff with no host receipt is unknown.
   To recover a failed handoff, recheck the request, holds, revision, and
   [current responsibility](#communicate). Resend only what is missing to that owner.

Finish when every required result is accepted and integrated, or you report the exact gap.
Return each slice's disposition, artifacts, checks, open decision requests, and blockers.

Start goals and recurring work only when explicitly requested. A Coordinator's grant records
that request for its heartbeat.
