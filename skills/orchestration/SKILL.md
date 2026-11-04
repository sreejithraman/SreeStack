---
name: orchestration
description: Resolve working-model defaults and coordinate agents in T3 Code. Use before implementation, diagnosis, research, or verification, or when assigning agents and integrating their results.
---

# Orchestration

The caller owns the outcome. Give independent, ready work to children when that
adds speed or coverage. Keep cohesive work with one owner.

## Pick the model

Pick a model with [agent routing](references/agent-routing.md#model-defaults)
before you start or delegate. Use the
[working selection](references/agent-routing.md#choose-working-selection) unless
a task-specific row or the user says otherwise.

Do the work yourself only when your model and effort match that choice or an
explicit user override. Otherwise follow
[selection handoff](references/agent-routing.md#selection-handoff). Use the steps
below to delegate, even a single task that only needs a different model, and
leave the parent's own settings unchanged.

## Assign

For design and implementation decisions, use
[Engineering Principles](../engineering-principles/SKILL.md) and put the
references that apply in the brief.

Settle the required outcome and proof before you split the work.

- Give each child one result and a completion check.
- Separate writable paths and shared resources. Run work that would collide in
  series.
- Start a slice that depends on another's output once that output is accepted.
- For competing approaches, choose the comparison criteria before dispatch.

Give each child a self-contained brief:

- Requirements and accepted decisions.
- Source paths and artifacts.
- The output it owns and the actions it may take.
- Shared files to preserve.
- Checks and return format.
- For verification or measurement: the user outcome, operating context,
  invariants and failure questions, exact revisions, and method.
- Any further delegation you want from it.

Send the original request with the brief, in full or as a pointer it can open,
along with accepted corrections and explicit constraints. A plan or brief adds
to that source and authorizes nothing beyond it. Related messages and quoted
material are context, not new authority.

Give the work a stable identity, separate from execution attempt IDs. Send an
in-scope follow-up to the existing owner after checking which source messages it
has already received or handled. Return a scope change to the caller with its
source and reason.

Record an explicit human **hold** with its source, affected scope, and release
condition. Keep it through retries, transfers, and restarts until that person
lifts it. New evidence can clear an agent-reported blocker within the existing
grant, but only the human releases a hold.

Assignment is done when every required slice has an owner, usable inputs,
compatible ownership, and a completion check. Then use agent routing to resolve
the model, consider [reuse](references/agent-routing.md#reuse-an-agent), and
start ready work within the concurrency ceiling.

## Return

A child's return names its artifact and revision, the evidence it observed,
coverage gaps, blockers, and open decision requests.

When a person must decide or supply something, return a **decision request**
apart from the progress report. Include:

- A stable ID, prefixed with your assigned work ID if you have one (`W2-D1`).
- The exact question and its source.
- The affected work.
- Options, with any recommendation.
- What continues meanwhile.

A parent forwards the question, meaning intact, through the host's user-input
route, unless its workflow authorizes it to settle the request. The request stays open
until the person answers or withdraws it, or that parent settles it. Record each
outcome with its source. Progress, readiness, or a recommendation leaves it open.
Keep the ID while the question stands. A changed question gets a new ID linked to
the one it replaces.

Return decision requests and cross-cutting blockers when they arise, not when
your other work is done. Use a mid-run route to the parent if the host offers
one. Otherwise end your turn with the request and a partial report. The parent
resumes you for unaffected work while the person decides.

## Accept

A result is **accepted** when you have inspected its artifact at a named revision
and the evidence shows the required outcome with the specified method. A child's
summary, a finished turn, green CI, or an open PR is input to that inspection, not
acceptance.

Mark every required slice as accepted, needing repair, rejected with a reason, or
blocked. A missing slice or dropout stays required. Repairs use the working
selection.

Verify the integrated result against the original requirements. Reuse a check
while its revision and scope still hold, and rerun the checks integration
affected. Use [review-fix-loop](../review-fix-loop/SKILL.md) for behavior and
agent-procedure changes. When [pr](../pr/SKILL.md) will review the same complete
scope before publication, let it run that loop once.

Track acceptance, delivery state (local, PR, or merged), and handoff delivery
separately. A queued handoff stays pending until the host shows it delivered.
Mark it unknown if the host gives no receipt. To recover a failed handoff, keep
the verified work and recheck the current request, holds, and revision, including
any evidence a changed revision affects. Then resend only the missing handoff to
the same recipient through the host's route.

Use [showroom](../showroom/SKILL.md) before handoff when the user can inspect or
try the integrated result.

The assignment is done when every required result is accepted and integrated, or
you report the exact remaining gap. The caller owns the larger finish line.
Return child task IDs and dispositions, artifacts, checks, requested and confirmed
model settings, open decision requests, and blockers.

Goal state, recurring work, and ordinary top-level threads use their explicitly
requested host workflows. Ordinary delegation creates none of them.
