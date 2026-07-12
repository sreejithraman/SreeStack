---
name: goal-swarm
metadata:
  owner: sree
description: Goal swarm. Use when the user explicitly asks for parallel agents, subagents, or agent-owned goal shards.
argument-hint: "<goal or task>"
---

# Goal Swarm

A goal swarm turns explicit parallel-agent authorization into bounded shard work under one parent goal.

Use this only when the user explicitly asks for parallel agents, subagents, a swarm, or agent-owned goal shards.

## Steps

1. Create the parent goal using `references/goal-prompts.md`.

   Make the expected outcome, scope, constraints, verification target, and final deliverable concrete enough that another agent could judge whether the parent goal has been satisfied.

2. Split the work into independent shards using `references/shard-types.md`.

   Give each shard one owner, one deliverable, and responsibility that does not duplicate another shard.

3. Write a dedicated `/goal` prompt for each shard using `references/goal-prompts.md`.

   Each prompt should stand alone without extra explanation from the parent agent.

4. Dispatch all ready shards concurrently.

   Keep any unspawned work local only when there is a clear reason, such as dependency order, low value, or overlap with the parent agent's critical path.

5. Synthesize returned artifacts.

   Inspect every shard result before trusting it. Each result is incorporated, rejected with a reason, narrowed and re-dispatched, finished locally, or marked blocked.

   Give every returned artifact an explicit disposition before final synthesis starts.

6. Verify the parent goal.

   The final answer should name the agents spawned, shard ownership, evidence checked, and any residual risk.
