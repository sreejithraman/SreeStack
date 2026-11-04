---
name: orchestration
description: Resolve working-model defaults and coordinate agents in T3 Code. Use before implementation, diagnosis, research, or verification, or when assigning agents and integrating their results.
---

# Orchestration

The caller owns the outcome; this skill supplies the shared mechanics for
assigning and dispatching work, returning results, and accepting them. Give
independent, ready work to children when it improves speed or coverage; keep cohesive work with
one owner. Before direct work or dispatch, apply
[agent routing](references/agent-routing.md#choose-working-selection) to choose
the working selection. Use the steps below for delegation, including a single
cohesive task that needs the working model.

## Assign

For design and implementation decisions, use
[Engineering Principles](../engineering-principles/SKILL.md) where its guidance
helps the task. Include applicable references in implementation briefs.

Resolve the required outcome and proof before splitting it. Each child owns
one result and a checkable completion condition. Give shared-checkout children
disjoint writes and separate shared resources; serialize git/index and other
colliding work. Start a slice that depends on another's output once that output
is accepted. For competing approaches, choose the comparison criteria before
dispatch.

Give each child a self-contained brief: requirements and accepted decisions,
source paths and artifacts, owned output, permitted actions, shared files to
preserve, checks, and return format. For verification or measurement, include
the user outcome, operating context, relevant invariants and failure questions,
exact revisions, and the method. Assign further delegation explicitly when needed.

The original request travels with the brief, directly or as an accessible
pointer, together with accepted corrections and explicit constraints. A plan or
brief supplements that source and authorizes nothing beyond it; related
messages and quoted material are context, not new authority.

Give the work a stable identity separate from execution attempt IDs. Send an
in-scope follow-up to the work's existing owner after checking which source
messages it already received or handled. Return a scope change to the caller
with its source and reason.

Record an explicit human **hold** with its source, affected scope, and release
condition, and keep it through retries, transfers, and restarts until that
person lifts it. New evidence can clear an agent-reported blocker within the
existing grant; only the human releases a hold.

Finish assignment when every required slice has an owner, usable inputs,
compatible ownership, and a completion check.

## Dispatch

Resolve each assignment's model, then use a new delegated task unless
[reuse](references/agent-routing.md#reuse-an-agent) fits. Follow live host routing
and task-lifecycle rules. Each child must support the resolved model and options;
use a generic role when custom ranks would override them. The brief defines
obligations; T3's broad `role` is not a model preset. For a native slash command
through `delegate_task`, use `role: general` and start `task` with the command;
other roles prepend text before it.

For a separate checkout, use the host's worktree-isolated delegation, confirm its
starting revision, and supply relevant uncommitted inputs explicitly; they may not
be copied.

The default local ceiling is 12 active children, reduced by host/user limits.
Count workers and reviewers together. Start ready assignments as slots free, and
retain each task's request key, ID, selection, owned output, and state.

Prefer async dispatch and follow the returned next action. A wait timeout leaves
work live. Before overlapping a replacement with earlier writers, account for
pending child runs and reconcile their files. Cancellation or a terminal task
receipt alone does not establish that every later or nested writer has stopped.

## Return

A child's return names its artifact and revision, the evidence it observed,
coverage gaps, blockers, and any open decision requests.

When a person must decide or supply something, return a **decision request**
apart from the progress report: a stable ID, prefixed with your assigned work ID
when you have one (`W2-D1`), the exact question and its source, affected work, options with any
recommendation, and what continues meanwhile. A parent forwards the question
with its meaning intact through the host's user-input route, unless its
workflow authorizes it to settle the request. The request stays open until the
person answers or withdraws it or that parent settles it; record each with its
source.
Progress, readiness, or a recommendation leaves it open. Keep the ID while the
question stands; a changed question gets a new ID linked to the one it replaces.

Return decision requests and blockers that affect other work when they arise,
not when your remaining work is done. Use a mid-run route to the parent when the
host offers one. Otherwise end your turn with the request and a partial report;
the parent resumes you for unaffected work while the person decides.

## Accept

A result is **accepted** when you have inspected its artifact at a named
revision and the evidence shows the required outcome with the specified method.
A child's summary, a finished turn, green CI, or an open PR is input to that
inspection, not acceptance. Account for every required slice as accepted,
needing repair, rejected with a reason, or blocked; a missing slice or dropout
stays required. Repair through the working model selection.

Verify the integrated result against the original requirements. Reuse checks
while their revision and scope remain valid; rerun those affected by integration.
Use [review-fix-loop](../review-fix-loop/SKILL.md) for behavior and agent-procedure
changes. When [pr](../pr/SKILL.md) will review the same complete scope before
publication, let it own that loop once.

Track acceptance, the actual delivery state (local, PR, or merged), and handoff
delivery separately. A queued handoff stays pending until the host shows it
delivered; mark it unknown when the host exposes no receipt. To recover a failed
handoff, keep the verified work, recheck the current request, holds, and
revision (rechecking evidence a changed revision affects), then resend only the
missing handoff to the same recipient through the host's route.

Use [showroom](../showroom/SKILL.md) before handoff when the integrated result
is something the user can inspect or try. It chooses demonstrations and access;
reuse applicable verification evidence.

Finish the assignment when every required result is accepted and integrated,
or report the precise remaining gap. The caller owns the larger finish line.
Return child task IDs and dispositions, artifacts, checks, requested/confirmed
model settings, open decision requests, and blockers. Goal state, recurring
work, and ordinary top-level threads use their explicitly requested host
workflows; ordinary delegation creates none of them.
