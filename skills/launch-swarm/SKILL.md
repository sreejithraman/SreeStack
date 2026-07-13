---
name: launch-swarm
description: Launch swarm. Use when a task should become a merge-ready PR through goal-swarm, local review, and GitHub sweep.
argument-hint: "[ready|merge] <task, issue, branch, or PR>"
---

# Launch Swarm

Launch swarm turns a task into a merge-ready PR, and optionally merges it when explicitly authorized.

Use this when the user wants the work carried through implementation, review, publishing, GitHub sweep, and readiness or merge.

## Modes

- **Ready mode**: default. Stop at a merge-ready PR.
- **Merge mode**: only when the user explicitly asks to merge, land, or ship, or explicitly approves merge after the readiness report.

## Steps

1. Preflight

   Identify the repo, base branch, current branch, worktree state, task source, target PR if one exists, mode, constraints, and files or changes that must be preserved.

2. Build

   Use `/goal-swarm` when the task benefits from explicit parallel shard work. For linear work, implement locally and state why local execution fits.

   Keep ownership clear and preserve unrelated user or agent changes.

3. Local Review

   Run `/review-fix-loop` on the resulting diff.

   Continue only when verification is green, failures are evidenced as unrelated, or remaining blockers are explicit.

4. Publish

   Commit only owned changes, push the branch, and use the GitHub connector to create or update the PR. Mark it ready for review by default unless the user requested draft.

5. GitHub Sweep

   Run `/github-review-sweep` on the PR. If fixes or required-check failures change the diff, rerun `/review-fix-loop`, publish the new commit, and repeat the sweep until stable or blocked.

6. Verify Readiness

   Confirm local verification, manual verification, required PR checks, approvals, parent-owned defers, base branch, and head SHA.

   Rerun `/manual-verify` only when the final PR diff lacks manual-verification evidence, the GitHub sweep changed an exercisable surface, or previous manual verification was blocked or stale.

7. Ready Or Merge

   In ready mode, stop and report merge readiness or exact blockers.

   In merge mode, merge only after explicit authorization is present and the head SHA being merged is confirmed.

## Report

End with:

- mode: ready or merge
- branch, base branch, PR URL, and head SHA
- swarm shards used, or why none
- changed files or artifact summary
- review/fix loop result
- GitHub sweep result
- manual verification result
- ready, merged, auto-merge enabled, or exact blocker
