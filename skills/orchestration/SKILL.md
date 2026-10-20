---
name: orchestration
description: Resolve working-model defaults and coordinate agents in T3 Code. Use before implementation, diagnosis, research, or verification, or when assigning agents and integrating their results.
---

# Orchestration

The parent owns the outcome. Give independent, ready work to children when it
improves speed or coverage; keep cohesive work with one owner. Use the applicable
selection in [agent routing](references/agent-routing.md#model-defaults),
including when working directly. The working selection applies unless a
task-specific selection or explicit user override covers the assignment.

Resolve that selection before doing the work. Continue directly only when this
agent's effective model and effort match it or an explicit user override.
Otherwise delegate the task with that selection, preserving the parent's
configuration. Use the steps below for delegation, including a single cohesive
task that needs the working model.

## Assign

For design and implementation decisions, use
[Engineering Principles](../engineering-principles/SKILL.md) where its guidance
helps the task. Include applicable references in implementation briefs.

Resolve the required outcome and proof before splitting it. Each child owns
one result and a checkable completion condition. Separate writable paths and
shared resources; serialize work that would collide. For competing approaches,
choose the comparison criteria before dispatch. For tickets with blocking
relationships, use [task graphs](references/task-graphs.md).

Give each child a self-contained brief: requirements and accepted decisions,
source paths and artifacts, owned output, permitted actions, shared files to
preserve, checks, and return format. For verification or measurement, include
exact revisions and the method. Assign further delegation explicitly when needed.

Finish assignment when every required slice has an owner, usable inputs,
compatible ownership, and a completion check. Then follow agent routing to
resolve the model and start ready work within the concurrency ceiling.

## Accept

Inspect each result and its evidence. Account for every required slice as
accepted, needing repair, rejected with a reason, or blocked. A completed child
turn, a missing slice, or a mismatched verification revision/method is not
proof of the parent outcome. Repair through the working model selection.

Verify the integrated result against the original requirements. Reuse checks
while their revision and scope remain valid; rerun those affected by integration.
Use [review-fix-loop](../review-fix-loop/SKILL.md) for behavior and agent-procedure
changes. When [pr](../pr/SKILL.md) will review the same complete scope before
publication, let it own that loop once.

Use [showroom](../showroom/SKILL.md) before handoff when the integrated result
is something the user can inspect or try. It chooses demonstrations and access;
reuse applicable verification evidence.

Finish when every required result is integrated and its checks pass, or report
the precise remaining gap. Return child dispositions, artifacts, checks,
requested/confirmed model settings, and blockers. Goal state, recurring work,
and ordinary top-level threads use their explicitly requested host workflows;
ordinary delegation creates none of them.
