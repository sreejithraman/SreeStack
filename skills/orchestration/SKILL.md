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
and stay free. In T3 that means `delegate_task`. Pick its model by its job from
[the model table](references/models.md#choose-a-model), and keep your own. Keep reading, planning,
answering, and coordinating yourself. Edit yourself only when told to do it yourself, or under the
repair rule below. If you can't launch a subagent, say so and ask.

**As a child,** do your own work, whatever your model. Delegate further only when your task says
to.

**Review fixes and other repairs go to the slice's owner first,** even after its turn finished.
A slice's owner is the agent that wrote it. In T3, `t3_thread_send` to the owner's thread. T3's
"Fix small review findings yourself; start no delegate for them" bars a new delegate. Resuming the
owner starts none, so the owner still goes first.

**No owner left** means its thread is gone or can't be resumed. A finished run is not that. If
its state is unknown, use [recovery](references/reuse-and-recovery.md#recover-work). With no
owner left, that same T3 rule applies: fix a small review finding yourself, and launch any other
repair from the model table. Before a repair overlaps the owner's files, reconcile under
[Replacing work](references/reuse-and-recovery.md#recover-work).

Give independent, ready work to separate children when that adds speed or coverage. Keep
cohesive work with one owner.

## Assign

Settle the outcome and proof before you split the work. Give each slice one owner and each active
writer paths no other active writer touches. Run git, index, and other colliding work in series.
Start a dependent slice after its input is accepted.

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

**In-scope follow-up:** send it to the existing owner, whatever its model. **Scope change:** return
it to the caller with its source and reason.

**Human hold:** record its source, scope, and release condition. It survives retries, transfers,
and restarts, and only that person lifts it.

## Dispatch

Follow live host rules. Use a new task unless [reuse](references/reuse-and-recovery.md#reuse-an-agent)
fits. When a run fails or its status is unclear, use
[recovery](references/reuse-and-recovery.md#recover-work).

- **Target:** each child must support the chosen model and options. Use a generic role when
  custom ranks would override them. T3's `role` is not a model preset.
- **Slash command:** through `delegate_task`, set `role: general` and start `task` with the
  command. Other roles put text before it.
- **Separate checkout:** confirm its starting revision and supply uncommitted inputs
  explicitly.
- **Limit:** by default 12 children stay active, counting workers and reviewers together. Host
  or user limits lower this.
- **Tracking:** keep each task's request key and ID, so recovery starts no duplicate writer.

## Return

A child returns its artifact and revision, the evidence it observed, coverage gaps, blockers,
and open decision requests.

**When you are stuck, ask up.** Finish what doesn't depend on the answer, then end your turn
with the question and a partial report. If it blocks other work, raise it at once, through a
mid-run route if the host offers one.

**As the parent,** answer and resume the child for unaffected work. For a second opinion, launch
a read-only reviewer. [Replace the owner](references/reuse-and-recovery.md#replace-an-owner)
only on evidence of repeated failure.

**When a person must decide or supply something,** return a **decision request** apart from the
progress report: an ID, the exact question and its source, the affected work, options with any
recommendation, and what continues meanwhile.

A parent forwards the question, meaning intact, through the host's user-input route. The request
stays open until the person answers or withdraws it, or the parent settles it under a workflow
that authorizes that. Silence, progress, and recommendations settle nothing.

## Accept

A child's summary, a finished turn, green CI, or an open PR is input, not acceptance. Accept
only an artifact you inspected at a named revision, with evidence of the required outcome by
the specified method.

1. Mark every required slice accepted, needing repair, rejected with a reason, or blocked. A
   dropout stays required. Route each repair under [Who does the work](#who-does-the-work).
2. Verify the integrated result against the original requirements. Reuse a check while its
   revision and scope hold, and rerun the checks integration affected.
3. Use [review-fix-loop](../review-fix-loop/SKILL.md) for behavior and agent-procedure
   changes. For a change headed to a PR, leave that to [pr](../pr/SKILL.md), which runs the
   loop when no matching review evidence exists.
4. An accepted result is not a delivered one. A queued handoff with no host receipt is unknown.
   To recover a failed handoff, recheck the request, holds, and revision. Then resend only what
   is missing, to the same recipient.

Finish when every required result is accepted and integrated, or you report the exact gap.
Return each slice's disposition, artifacts, checks, open decision requests, and blockers.

Start goals and recurring work only when explicitly requested.
