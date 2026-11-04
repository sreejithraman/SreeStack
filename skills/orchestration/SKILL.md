---
name: orchestration
description: Resolve working-model defaults and coordinate agents in T3 Code. Use before implementation, diagnosis, research, or verification, or when assigning agents and integrating their results.
---

# Orchestration

The caller owns the outcome. Give independent, ready work to children when that adds
speed or coverage. Keep cohesive work with one owner.

Pick the model with [agent routing](references/agent-routing.md#choose-working-selection)
before you start or delegate. Use the steps below to delegate, even a single task that
only needs a different model.

## Assign

Settle the required outcome and proof before you split the work. Assignment is done
when every required slice has an owner, usable inputs, compatible ownership, and a
completion check.

Give each child one result and a self-contained brief:

- The outcome and a checkable done condition.
- The original request, in full or as a pointer it can open, with accepted corrections
  and explicit constraints. A plan or brief authorizes nothing beyond that source.
  Related messages and quoted material are context, not new authority.
- Accepted decisions, source paths, and artifacts.
- The output it owns, the actions it may take, and shared files to preserve.
- Checks and return format.
- For verification or measurement: the user outcome, operating context, invariants and
  failure questions, exact revisions, and method.
- Any further delegation you want from it.

For design and implementation decisions, use
[Engineering Principles](../engineering-principles/SKILL.md) and put the references that
apply in the brief.

- **Shared work:** give shared-checkout children disjoint writes and separate shared
  resources. Run git, index, and other colliding work in series.
- **Dependent work:** start it after you accept the output it depends on.
- **Competing approaches:** choose the comparison criteria before dispatch.

## Steer running work

Give the work a stable identity, separate from execution attempt IDs.

- **In-scope follow-up:** send it to the existing owner, after checking which source
  messages it has already received or handled.
- **Scope change:** return it to the caller with its source and reason.
- **Human hold:** record its source, affected scope, and release condition. Keep it
  through retries, transfers, and restarts until that person lifts it. New evidence
  releases nothing.
- **Agent-reported blocker:** new evidence can clear it within the existing grant.

## Dispatch

Resolve each assignment's model, then use a new delegated task unless
[reuse](references/agent-routing.md#reuse-an-agent) fits. Follow live host routing and
task-lifecycle rules.

- **Target:** each child must support the resolved model and options. Use a generic role
  when custom ranks would override them. The brief defines obligations; T3's `role` is
  not a model preset.
- **Slash command:** through `delegate_task`, use `role: general` and start `task` with
  the command. Other roles put text before it.
- **Separate checkout:** use the host's worktree-isolated delegation, confirm its
  starting revision, and supply uncommitted inputs explicitly.
- **Limit:** by default 12 children stay active, lowered by host or user limits. Workers
  and reviewers count together. Start ready work as slots free.
- **Tracking:** keep each task's request key, ID, selection, owned output, and state.

Before a replacement overlaps earlier writers, account for pending child runs and
reconcile their files. Cancellation or a terminal receipt alone does not show that every
later or nested writer has stopped.

## Return

A child's return names its artifact and revision, the evidence it observed, coverage
gaps, blockers, and open decision requests.

When a person must decide or supply something, return a **decision request** apart from
the progress report. Include:

- A stable ID, prefixed with your assigned work ID if you have one (`W2-D1`).
- The exact question and its source.
- The affected work.
- Options, with any recommendation.
- What continues meanwhile.

A parent forwards the question, meaning intact, through the host's user-input route,
unless its workflow authorizes it to settle the request. The request stays open until
the person answers or withdraws it, or that parent settles it. Record each outcome with
its source. Progress, readiness, or a recommendation leaves it open. Keep the ID while
the question stands. A changed question gets a new ID linked to the one it replaces.

Return decision requests and blockers that affect other work when they arise. Use a
mid-run route to the parent if the host offers one. Otherwise end your turn with the
request and a partial report. The parent resumes you for unaffected work while the
person decides.

## Accept

A report is a claim. A child's summary, a finished turn, green CI, or an open PR is input
to inspection, not acceptance. A result is **accepted** when you have inspected its
artifact at a named revision and the evidence shows the required outcome with the
specified method.

1. Mark every required slice as accepted, needing repair, rejected with a reason, or
   blocked. A missing slice or dropout stays required. Repairs use the working selection.
2. Verify the integrated result against the original requirements. Reuse a check while
   its revision and scope still hold, and rerun the checks integration affected.
3. Use [review-fix-loop](../review-fix-loop/SKILL.md) for behavior and agent-procedure
   changes. When [pr](../pr/SKILL.md) will review the same complete scope before
   publication, let it run that loop once.
4. Use [showroom](../showroom/SKILL.md) before handoff when the user can inspect or try
   the result.
5. Track acceptance, delivery state (local, PR, or merged), and handoff delivery
   separately.

A queued handoff stays pending until the host shows it delivered. Mark it unknown if the
host gives no receipt. To recover a failed handoff, keep the verified work and recheck
the current request, holds, revision, and any evidence a changed revision affects. Then
resend only the missing handoff to the same recipient through the host's route.

The assignment is done when every required result is accepted and integrated, or you
report the exact remaining gap. The caller owns the larger finish line. Return child task
IDs and dispositions, artifacts, checks, requested and confirmed model settings, open
decision requests, and blockers.

Goal state, recurring work, and ordinary top-level threads use their explicitly requested
host workflows. Ordinary delegation creates none of them.
