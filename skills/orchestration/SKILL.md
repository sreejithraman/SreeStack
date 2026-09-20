---
name: orchestration
description: Decide whether to delegate and coordinate agents for implementation, research, or verification. Use when choosing workers, splitting work, or integrating their results.
---

# Orchestration

The parent owns scope, delegation, and integration. Keep cohesive work with one
owner; delegate when independent work can start now and adds useful speed or
coverage. Difficulty alone calls for a stronger model, not more agents.
Orchestration does not require or authorize a goal.

## Steps

1. Choose the work.

   Keep tasks with the parent when a child would wait on a dependency, edit the
   same files, or save little time. Give each delegated result one owner and a
   check. Use [responsibilities](references/responsibilities.md) to clarify each
   assignment; they are not roles to fill on every task.

2. Brief and dispatch.

   Follow [agent routing](references/agent-routing.md) for role, model, effort,
   context, and reuse. Supply the result, requirements, inputs, owned paths,
   shared files to leave alone, checks, and return format. Start ready work
   within the configured limit. The parent can do separate work while waiting.

3. Integrate and verify.

   Read each result and its evidence. Accept it, send related fixes to its owner,
   finish it with the parent, reject it with a reason, or report its blocker.
   Check the integrated result against the original requirements. Reuse valid
   test evidence; rerun checks when integration changes what they tested.

   Use `/review-fix-loop` for code changes that affect behavior and docs that
   change agent behavior. It owns independent review coverage and rounds;
   child acceptance does not replace it. Reuse a completed review only while
   its scope and evidence still match the final change.

## Handoff

Report the integrated result, child dispositions, checks, and remaining risks
or blockers. Include requested agent settings and distinguish them from
confirmed runtime settings.
