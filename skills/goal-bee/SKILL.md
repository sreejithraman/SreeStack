---
name: goal-bee
description: Use when the user explicitly requests goal-backed work, including a child goal assigned within that request. Write a measurable objective, do the work, check the result, and update the goal state.
---

# Goal bee

Run one goal until its stated checks pass or it meets the `blocked` rule. The goal stays active across turns. It does not grant new permissions or expand the request.

Require an explicit user request to create or use a goal, including when a parent
skill assigns the work. Otherwise, complete the task without creating a goal.

## Steps

1. Write the objective.

   Apply the goal check below. Use exact commands and pass conditions when they exist. Use numbers only when they measure success.

   Turn a request such as "make progress" or "work on X" into a result another agent can check. Ask one short question only when a safe choice would change the result or its proof.

2. Check goal state.

   Call `get_goal`. Resume an active goal when it matches the request. If no goal is active, call `create_goal` with one short objective. Include its proof and key scope limits. Pass a token budget only when the user gave one.

   Leave a conflicting active goal unchanged. Ask the user whether to finish it or put the new goal in its own thread.

3. Do the work.

   Complete every safe step required by the objective. Preserve user work and follow all approval rules. Use failed attempts to choose the next step while useful options remain.

   At the start of each later goal turn, call `get_goal` before resuming. Apply user changes that still fit the objective. Tell the user when a new request conflicts with it before changing course.

4. Check the result.

   Run the checks named in the objective and read their output. Keep the goal active if a required check is missing or fails. A patch or partial pass does not prove the full objective.

5. Record the final state.

   Call `update_goal` with `complete` only when the result exists, every required check passes, and no required work remains.

   Use `blocked` only when the same issue stops progress for three goal turns in a row and no useful in-scope work remains. On the first two turns, try safe options and record the exact cause. If a blocked goal resumes, start the count again.

6. Report the result.

   State the objective, final state, checks and outputs, changed files or actions, and known risks. For a completed goal with a token budget, include the final token count returned by `update_goal`.

## Goal check

Before `create_goal`, the objective must answer:

- What will be true when the work is done?
- What evidence will prove it?
- What exact pass condition marks success?
- Which scope limits and stop rules matter?

For a bug, name the reproduction and the check that must change from failing to passing when possible. For research, name the decision and the sources needed to support it. For an operation, name the healthy state, the check period when needed, and the point that requires user action.
