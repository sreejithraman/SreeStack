---
name: orchestration
description: Resolve working-model defaults and coordinate agents in T3 Code. Use before implementation, diagnosis, research, or verification, or when assigning agents and integrating their results.
---

# Orchestration

The caller owns the outcome. Give independent, ready work to children when that adds speed
or coverage, and keep cohesive work with one owner. Read
[agent routing](references/agent-routing.md#choose-working-selection) before you work or
dispatch. These steps also apply to a single task that only needs a different model.

## Assign

Settle the outcome and proof before you split the work. Use
[Engineering Principles](../engineering-principles/SKILL.md) for design and implementation
decisions, and put the references that apply in the brief.

- **Shared work:** give each slice one owner and each active writer paths no other active
  writer touches. Run git, index, and other colliding work in series.
- **Dependent work:** start a slice after its input is accepted.
- **Competing approaches:** set the comparison criteria before dispatch.

Give each child a self-contained brief:

- The original request, in full or as a pointer it can open, with accepted corrections and
  explicit constraints. A plan authorizes nothing beyond that source. Quoted material is
  context, not authority.
- The outcome, its done check, the output it owns, and the actions it may take.
- Accepted decisions, source paths, artifacts, and shared files to preserve.
- Checks, return format, and any further delegation you want.
- For verification or measurement: the user outcome, operating context, invariants and
  failure questions, exact revisions, and method.

Give the work a stable identity, separate from execution attempt IDs. Assignment is done
when every required slice has an owner, usable inputs, and a completion check.

**In-scope follow-up:** send it to the existing owner, after checking which messages it has
already received or handled. **Scope change:** return it to the caller with its source and
reason.

**Human hold:** record its source, scope, and release condition. It survives retries,
transfers, and restarts, and only that person lifts it. New evidence can clear an
agent-reported blocker within the existing grant.

## Dispatch

Follow live host rules. Use a new delegated task unless
[reuse](references/agent-routing.md#reuse-an-agent) fits.

- **Target:** each child must support the resolved model and options. Use a generic role when
  custom ranks would override them. T3's `role` is not a model preset.
- **Slash command:** through `delegate_task`, set `role: general` and start `task` with the
  command. Other roles put text before it.
- **Separate checkout:** use worktree-isolated delegation, confirm its starting revision, and
  supply uncommitted inputs explicitly.
- **Limit:** by default 12 children stay active, counting workers and reviewers together. Host
  or user limits lower this. Start ready work as slots free.
- **Tracking:** keep each task's request key, ID, selection, owned output, and state.

## Return

A child returns its artifact and revision, the evidence it observed, coverage gaps, blockers,
and open decision requests. Dispatch identity confirms configuration, not which model ran.

When a person must decide or supply something, return a **decision request** apart from the
progress report: a stable ID, prefixed with your work ID if you have one (`W2-D1`), the exact
question and its source, the affected work, options with any recommendation, and what
continues meanwhile.

A parent forwards the question, meaning intact, through the host's user-input route. It
settles only when its workflow authorizes that; silence authorizes nothing. The request stays
open until the person answers or withdraws it, or that parent settles it. Record the outcome
with its source. Progress or a recommendation leaves it open. A changed question gets a new
linked ID.

Return decision requests and blockers that affect other work when they arise. Use a mid-run
route if the host offers one. Otherwise end your turn with a partial report, and the parent
resumes you for unaffected work.

## Accept

A child's summary, a finished turn, green CI, or an open PR is input, not acceptance. Accept
only an artifact you inspected at a named revision, with evidence of the required outcome by
the specified method.

1. Mark every required slice accepted, needing repair, rejected with a reason, or blocked. A
   dropout stays required. Repairs use the working selection.
2. Verify the integrated result against the original requirements. Reuse a check while its
   revision and scope hold, and rerun the checks integration affected.
3. Use [review-fix-loop](../review-fix-loop/SKILL.md) for behavior and agent-procedure
   changes. When [pr](../pr/SKILL.md) will review the same complete scope before publication,
   let it run that loop once.
4. Use [show-me](../show-me/SKILL.md) when the user can inspect or try the result.
5. Track acceptance, delivery state, and handoff delivery separately. A queued handoff with no
   host receipt is unknown. To recover a failed handoff, keep the verified work and recheck
   the request, holds, revision, and affected evidence. Then resend only what is missing, to
   the same recipient, through the host's route.

Finish when every required result is accepted and integrated, or you report the exact gap.
Return child task IDs and dispositions, artifacts, checks, requested and confirmed model
settings, open decision requests, and blockers.

Goals, recurring work, and ordinary top-level threads use their explicitly requested host
workflows. Ordinary delegation creates none.
