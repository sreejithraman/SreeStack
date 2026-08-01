---
name: launch-swarm
description: Launch swarm. Use when a task should be built and delivered as one merge-ready PR or an ordered PR stack through goal-swarm and review-push-and-watch, with optional merge after explicit authorization.
---

# Launch Swarm

Launch swarm turns a task into one merge-ready PR or an ordered PR stack, and optionally merges it when explicitly authorized.

Use this when the user wants the work carried through implementation, PR handling, readiness, and optional merge.

## Modes

- **Ready mode**: default. Stop when the full one-PR or stacked-PR delivery is merge-ready.
- **Merge mode**: only when the user explicitly asks to merge, land, or ship, or explicitly approves merge after the readiness report.

## Steps

1. Preflight

   Identify the repo, target base, current branch, worktree state, task source, target PRs if any, mode, delivery shape, constraints, and changes that must be preserved.

   When delivery needs two or more dependent PRs, read `references/stacked-prs.md` fully before creating the first branch or PR. Finish preflight when the task, mode, delivery shape, ownership, and target base are explicit.

2. Build

   Invocation of launch swarm authorizes `/goal-swarm` when independent shards will shorten the build. For linear work, implement locally.

   Keep ownership clear and preserve unrelated user or agent changes.

   Finish the build when the requested behavior exists, shard results have explicit dispositions, and the complete owned change is ready to shape into delivery.

3. Shape Delivery

   For one PR, resolve its head branch and immediate base.

   For a stack, apply `references/stacked-prs.md` to define each layer's purpose, branch, immediate base, commit range, and dependency order. Agent shards do not define PR layers unless their code dependencies and review order also match.

   Finish this step when every owned change belongs to exactly one delivery layer and every layer has one reviewable diff.

4. Review, Push, And Watch

   For each layer, pass `/review-push-and-watch` an exact handoff: repo and worktree, head branch, immediate base, existing PR if any, owned paths and commits, and whether launch restacked its history. Use review-push-and-watch ready mode for both launch modes; merge remains launch work.

   For one PR, run `/review-push-and-watch` once with that handoff.

   For a stack, run `/review-push-and-watch` from the base layer upward. When a lower layer changes, restack every affected descendant and rerun `/review-push-and-watch` for each invalidated layer as required by `references/stacked-prs.md`.

   Finish this step when every current PR head is stable or has an exact blocker.

5. Verify Readiness

   Confirm each `/review-push-and-watch` result against the current branch, base, PR URL, and head SHA. For a stack, also confirm the ordered base links and that no descendant remains invalidated.

   Confirm local verification, manual verification, required PR checks, review state, parent-owned defers, and delivery-wide blockers. Finish this step only when the full delivery is ready or its blockers are complete.

6. Ready Or Merge

   In ready mode, stop and report merge readiness or exact blockers.

   In merge mode, read `references/merge.md` fully after readiness passes and before any merge.

## Report

End with:

- mode: ready or merge
- delivery shape and target base
- each branch, immediate base, PR URL, and head SHA
- swarm shards used, or why none
- changed files or artifact summary
- each review-push-and-watch result
- manual verification result
- ready, merged, auto-merge enabled, or exact blocker
