---
name: merge
description: Use when the user asks to merge a ready PR or stack and finish its issues and cleanup.
---

# Merge

A merge request authorizes landing the scoped work, closing fully resolved
issues, and cleanup of task-owned temporary resources. Honor the user's limits.
Return readiness blockers to the caller; fixes belong to `pr-prep` or the caller.

1. **Scope.** Identify the repository, target PRs, landing branch, and readiness
   evidence. If the scoped work has no PR, invoke [pr-prep](../pr-prep/SKILL.md)
   to prepare and publish it, carrying the merge request through its handoff.
   For stacks, use [gh-stack](../gh-stack/SKILL.md) to resolve the exact
   merge set and command target; authorization must cover every included layer.
   Already merged PRs proceed directly to issue completion and cleanup.

2. **Check readiness.** Read current GitHub state and reuse applicable handoff
   evidence. Verify head/base commits, checks, approvals, review threads,
   accepted fixes, and mergeability. Stale or missing verification and unmet
   requirements block landing. So do closing links that would close unfinished
   issues; return them to the caller for correction.

3. **Land.** Follow repository merge settings, protections, and queues. For a
   single PR, use [gh pr merge](https://cli.github.com/manual/gh_pr_merge) with
   `--match-head-commit <verified-head>`; leave branch deletion to cleanup.
   For stacks, use `gh-stack` and require guards against unverified head changes
   on every layer: head preconditions or enforced current-head checks and fresh
   approvals after pushes. If unavailable, report the blocker; see
   [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
   Confirm GitHub reports each PR merged; queued work remains pending. After a
   failed or timed-out submission, check GitHub state before retrying.

4. **Finish issues.** Check linked or task-scoped issues against their acceptance
   criteria and intended delivery branch. Confirm automatic closure or close a
   fully resolved open issue as completed with the merged PR link. Keep partial
   issues and those depending on unmerged layers open. Check existing state and
   comments before posting. An intermediate stack merge does not prove delivery;
   [automatic closing links](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
   apply when work reaches the default branch.

5. **Clean up.** Use [repo-cleanup](../repo-cleanup/SKILL.md) for confirmed merges,
   passing merge results, proven merge-time source heads, branches/bases,
   worktrees, and known task resources, including device installs. Identify
   resources needed by remaining stack layers. Issue-update failures do not
   prevent eligible cleanup.

Report merged and pending PRs, issue results, cleanup results, and blockers.
