---
name: goal-swarm
description: Split work across agents when the user explicitly requests goal-backed work and the user, applicable instructions, or a parent skill requests delegation.
---

# Goal swarm

Use parallel agents to complete one parent goal. Follow `/goal-bee` for the parent goal. Each child gets one bounded goal.

Require both an explicit user request to create or use a goal and authority to
delegate from the user, applicable instructions, or a parent skill. An ordinary
task request does not request a goal. For delegation without a goal, read
[agent routing](references/agent-routing.md) without opening a goal.

## Steps

1. Open the parent goal.

   Keep it active until you have added every accepted child result and the parent checks pass.

2. Split the work into independent shards using `references/shard-types.md`.

   Give each shard one owner, one result, and work that does not overlap another shard. Keep work with the parent when another agent would wait on a dependency, edit the same files, or save little time.

3. Give each child one `/goal-bee` request.

   Write each request so the child needs no extra context. State the result, proof, owned work, inputs, limits, checks, and return form. Name shared files and paths the child must leave alone.

   Read [agent routing](references/agent-routing.md) to choose a role and apply
   its model, effort, and context settings. Keep child goals within the parent
   goal the user requested.

4. Start the ready shards.

   Start ready shards within the configured concurrency limit. Wait to start
   work whose inputs are missing. The parent may join finished work or take a
   separate task that does not conflict with a child.

5. Review every child result.

   Read the evidence, then accept the result, reject it with a reason, send back a narrower request, finish it with the parent, or record its blocker. Make this choice for every child before you prepare the report.

6. Check and close the parent.

   For meaningful code changes, run `/review-fix-loop` on the complete integrated
   diff. Child acceptance does not replace that review. Reuse a completed review
   only while its scope and evidence still match the final change.

   Add the accepted work and run the parent checks. Close it only when every required check passes.

## Report

Name the parent goal and state. List the agents, their roles and requested
settings, their work, the choice made for each result, the checks run, and known
risks. Distinguish confirmed settings from unverified requests.
