---
name: goal-swarm
description: Split work into child goals when the user requests goal-backed parallel work or child goals.
---

# Goal swarm

Add child goals to `/orchestration` when the user requests goal-backed parallel
work or child goals. Bounded help on a single goal uses orchestration alone.

1. Follow `/goal-bee` to open or resume the parent goal.

2. Use `/orchestration` to choose, dispatch, and integrate independent work.
   Give each child one `/goal-bee` request with the user’s goal authorization,
   a bounded objective, and proof within the parent scope. Keep one goal owner
   when no useful split exists. Orchestration owns briefs, routing, reuse, and
   verification.

3. Close the parent through `/goal-bee` after required child results are accepted
   and integrated checks pass. Include parent and child goal states in the
   orchestration handoff; report any required result that remains blocked.
