---
name: swarm-and-push
description: Use when a direct task, or a spec with child tickets, should be built and delivered as one or more merge-ready PRs, including stacked PRs or an explicitly authorized merge.
---

# Swarm and Push

Swarm and push turns a direct task or spec-rooted ticket set into merge-ready PRs, and optionally merges them when explicitly authorized. It works the ticket frontier and forms PRs as reviewable boundaries become clear.

Use this when the user wants the work carried through implementation, PR handling, readiness, and optional merge.

## Modes

- **Ready mode**: default. Stop when every in-scope PR is merge-ready.
- **Merge mode**: only when the user explicitly asks to merge, land, or ship, or explicitly approves merge after the readiness report.

## Steps

1. Preflight

   Identify the repo, target base, current branch, worktree state, task source, target PRs if any, mode, constraints, and changes that must be preserved.

   When the task source is a spec issue with child tickets, read `references/ticketed-delivery.md` fully and resolve the spec-rooted ticket graph before building. For a direct task, resolve one owned change without creating a ticket graph.

   Finish preflight when the source, mode, target base, owned scope, and either the direct task or current ticket frontier are explicit.

2. Select And Assign Work

   Invocation of swarm and push authorizes `/goal-swarm` when independent shards will shorten the build. For ticketed delivery, give each selected ticket one agent-owned shard. For linear work, implement locally.

   Make only the current delivery units concrete. Keep later work in the ticket graph until its PR boundary becomes clear. Finish this step when each current ticket or direct task has one owner, one intended result, and a known base for its current work.

3. Build And Integrate

   Build the current work, keep ownership clear, and preserve unrelated user or agent changes. Inspect every shard result and give it an explicit disposition.

   For ticketed delivery, check each ticket's acceptance criteria and update the in-memory ticket state. Finish this step when the current behavior exists, the owned changes are integrated, and the work meets every current ticket's acceptance criteria or has an exact blocker.

4. Form Current PRs

   For ticketed delivery, apply the boundary rules in `references/ticketed-delivery.md`. Put work in the same PR, an independent PR, or a dependent PR based on its review purpose and code dependency.

   When a current PR depends on another current PR, read `references/stacked-prs.md` fully before creating its branch. Agent shards and tickets define work ownership; they define PR boundaries only when the review and code dependencies match.

   Finish this step when every current owned change belongs to exactly one PR, each current PR has one reviewable purpose, and each head and immediate base are explicit.

5. Prepare PRs

   For each current PR, pass `/pr-prep` an exact handoff: repo and worktree, head branch, immediate base, existing PR if any, owned paths and commits, and whether this skill restacked its history. Use `/pr-prep` without `yolo` for both delivery modes; this skill owns merging.

   Independent PRs may run in parallel. Process dependent PRs from base to tip. When a lower PR changes, restack every affected descendant and rerun `/pr-prep` as required by `references/stacked-prs.md`.

   Finish this step when every current PR head is stable or has an exact blocker.

6. Advance The Frontier

   For ticketed delivery, advance under `references/ticketed-delivery.md`.

   When that reference yields a new frontier, return to step 2. A stable published lower PR can support later work while it waits for human approval. Finish this step when every in-scope ticket maps to a current PR, has landed, or has an exact blocker.

7. Verify Readiness

   Confirm each `/pr-prep` result against the current branch, base, PR URL, and head SHA. Confirm every dependent base link and that no descendant remains invalidated.

   Confirm ticket acceptance criteria, local verification, manual verification, required PR checks, review state, parent-owned defers, and delivery-wide blockers. Finish this step only when the full in-scope delivery is ready or its blockers are complete.

8. Ready Or Merge

   In ready mode, stop and report merge readiness or exact blockers.

   In merge mode, read `references/merge.md` fully after readiness passes and before any merge.

## Report

End with:

- mode: ready or merge
- spec and in-scope tickets, or direct task
- delivery shape and target base
- ticket-to-PR mapping when ticketed
- each branch, immediate base, PR URL, and head SHA
- swarm shards used, or why none
- changed files or artifact summary
- each pr-prep result
- manual verification result
- ready, merged, auto-merge enabled, or exact blocker
