---
name: goal-swarm
description: Run explicitly requested goal-backed work. Decide whether to work solo or assign bounded goals to agents, verify the result, and update the goal state.
---

# Goal Swarm

Own one parent goal through its requested finish line. Choose one agent when the
work is cohesive; use child goals when independent outcomes make parallel work
useful. The parent owns integration and acceptance. Goal state does not expand
the user's scope or authorize external actions.

Create or use goals only when the user explicitly requests goal-backed work.
Within that request, assign bounded child goals when useful and honor any user
limit on agents or goals. Ordinary delegation outside a goal uses
`/orchestration` without creating goals.

## Workflow

1. **Frame the parent goal.** Write a short objective with a checkable result,
   proof, pass condition, and scope limits. Name the requested finish line: a
   verified local result, a PR ready for review, a merged PR, or another
   concrete outcome. Use exact commands when they exist and numbers only when
   they measure success. Ask one short question only when an unknown changes
   the safe result or its proof.

2. **Check goal state.** Call `get_goal`. Resume a matching active goal. If none
   exists, call `create_goal` with the objective, proof, and key limits. Pass a
   token budget only when the user gave one. Leave a conflicting active goal
   unchanged and ask whether to finish it or use another thread.

3. **Choose the execution mode.** Use `/orchestration` to assess whether
   independent work can start now and improve speed or coverage. Work solo
   when a split would wait on dependencies, collide in shared state, or cost
   more coordination than it saves.

   For parallel work, partition required outcomes into owned slices or compare
   independent approaches. State every required slice; for a comparison,
   declare the selection rule before dispatch. Give an agent a child goal when
   it owns a bounded, checkable outcome. Give short exploration or review work
   a bounded task. A comparison child can complete by evaluating its approach
   with evidence, whether or not that approach is selected.

   Use `/orchestration` for agent routing, briefs, concurrency, and integration.
   Pass each child the user's goal authorization, its objective and proof,
   parent scope, owned files or resources, and a single-owner instruction.
   The child uses `$goal-swarm` in its own thread and reports its goal state,
   evidence, and artifacts. Subdivide a child goal only when the parent brief
   explicitly permits it.

4. **Do and integrate the work.** Complete every safe step needed for the parent
   objective. At the start of each later goal turn, call `get_goal` and apply
   user changes that still fit it. Inspect each child result and its evidence.
   Repair or reassign gaps when useful; a child reporting completion does not
   prove the integrated parent result. Keep every required slice accounted for.

5. **Deliver and verify.** For a PR finish line, use `/pr-prep` after
   implementation. It owns review, publication, CI, feedback, and resulting
   fixes. Use `pr-prep yolo` only when the user explicitly requested a merge.
   For a local code change or agent instruction change, use `/review-fix-loop`
   when its trigger applies. Run the checks named in the parent objective and
   read their output. Keep the goal active while a required result or check is
   missing or failing.

6. **Record and report the state.** Call `update_goal` with `complete` only when
   the finish line is reached, all required evidence and integrated checks
   pass, and no required work remains. Use `blocked` only after the same issue
   stops progress for three consecutive goal turns and no useful in-scope work
   remains; a resumed blocked goal starts a fresh count. If the user asks to
   pause, call `update_goal` with `paused`, report its returned state, and stop
   goal work.

   Report the objective, parent and child goal states, accepted results and
   gaps, checks and outputs, changed artifacts, delivery state, and known risks.
   For a completed goal with a token budget, include the final token count
   returned by `update_goal`.

## Goal check

Before `create_goal`, the objective must answer:

- What will be true when the work is done?
- What evidence will prove it?
- What exact pass condition marks success?
- Which scope limits and stop rules matter?

For a bug, name the reproduction and the check that must change from failing
to passing when possible. For research, name the decision and sources needed
to support it. For an operation, name the healthy state, check period when
needed, and the point that requires user action.
