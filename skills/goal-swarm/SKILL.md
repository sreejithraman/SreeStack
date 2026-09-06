---
name: goal-swarm
description: Use when the user explicitly asks for parallel agents, subagents, or agent-owned goal shards, or when a parent skill delegates independent shards.
---

# Goal swarm

Use parallel agents to complete one parent goal. Follow `/goal-bee` for the parent goal. Each child gets one bounded goal.

The user or a parent skill must grant parallel-agent authority before this skill runs.

## Steps

1. Open the parent goal.

   Keep it active until you have added every accepted child result and the parent checks pass.

2. Split the work into independent shards using `references/shard-types.md`.

   Give each shard one owner, one result, and work that does not overlap another shard. Keep work with the parent when another agent would wait on a dependency, edit the same files, or save little time.

3. Give each child one `/goal-bee` request.

   Write each request so the child needs no extra context. State the result, proof, owned work, inputs, limits, checks, and return form. Name shared files and paths the child must leave alone.

4. Start the ready shards.

   Start every shard whose inputs exist. Wait to start the rest. The parent may join finished work or take a separate task that does not conflict with a child.

5. Review every child result.

   Read the evidence, then accept the result, reject it with a reason, send back a narrower request, finish it with the parent, or record its blocker. Make this choice for every child before you prepare the report.

6. Check and close the parent.

   Add the accepted work and run the parent checks. Close it only when every required check passes.

## Report

Name the parent goal and state. List the agents, their work, the choice made for each result, the checks run, and known risks.
