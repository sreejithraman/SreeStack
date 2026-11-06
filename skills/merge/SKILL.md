---
name: merge
description: Use when the user asks to merge a PR or stack, or to keep a finished change, and finish its issues and cleanup.
---

# Merge

Land a finished change. Start from a PR, a stack, or a reviewed local change the user kept.
Leave it merged and shown, with issues settled and task resources cleaned up. You are done when
GitHub reports every PR in the set merged, and each issue and cleanup target has a result.

A merge request authorizes landing the scoped work, closing fully resolved issues, and cleaning
up task-owned temporary resources. It also covers fixes that
[continue](../review-sweep/references/classification.md#continue-or-stop). Honor the user's
limits.

1. **Scope.** Identify the repository, PRs, landing branch, and evidence. Ask for the target if a
   merge request could refer to several PRs. If the work has no PR, publish it through
   [PR](../pr/SKILL.md#publish), then continue here. For stacks, use [gh-stack](../gh-stack/SKILL.md) to
   resolve the exact merge set and command target. Authorization must cover every layer. An
   already merged PR skips to step 5.

2. **Bring it to ready.** Follow PR's [watch](../pr/references/watch.md). Failures, comments,
   conflicts, and commits you didn't push all go through
   [continue or stop](../review-sweep/references/classification.md#continue-or-stop). Fixes that
   continue get one line in your report. A wake resumes this step, because the merge request
   still stands. On a stop, cancel any armed landing and confirm it's cancelled, with
   `gh pr merge --disable-auto` or, for a queue, the `dequeuePullRequest` mutation. Then leave the
   PR open and use [Show Me](../show-me/SKILL.md) to show the user what happened, including
   anything that landed first.

   A caller that keeps its own repair owner gets each failure, comment, and stop back, and resumes
   that owner. You repair nothing.

3. **Check it.** Capture what the user will want to see first, with Show Me, so this is the last
   read before you land. Run [`pr_state`](../pr/references/watch.md#read-the-state) with
   `--head <verified head>` for every PR in the set. Each must be
   [ready](../pr/references/watch.md#ready-or-blocked). Its `baseRefName` must be the landing
   branch, or for a stack layer its parent in the scoped set. A different base is a stop.

   Every PR, including docs-only changes, needs review of its current head that includes
   [Show, Don't Tell](../show-dont-tell/SKILL.md), plus required verification. Reuse matching
   evidence. A scoped rerun after a repair counts. So does review from before the base moved,
   once you've read the new base commits and they don't affect the files or behavior this change
   depends on. If evidence is missing or stale, a caller with its own repair owner gets the gap
   back. Otherwise run [PR's review step](../pr/SKILL.md#publish), publish any fixes, and go back
   to step 2.

   A head you didn't verify holds commits nobody reviewed. Read them, then go back to step 2. It
   counts as verified once the evidence above covers it.

   Closing links that would close unfinished issues block landing. After repairs or restacking,
   recheck every affected layer. Before local history changes, apply
   [Preserve local files](../pr/references/preserve-local-files.md). Land the set only when all of
   it is ready.

4. **Land.** Follow repository merge settings, protections, and queues. For one PR, use
   [gh pr merge](https://cli.github.com/manual/gh_pr_merge) with
   `--match-head-commit <verified head>`, and leave branch deletion to cleanup. For stacks, use
   `gh-stack`, with guards against unverified head changes on every layer: head preconditions,
   or enforced current-head checks and fresh approvals after pushes. Without them, report the
   blocker; see
   [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
   Confirm with `pr_state` that each PR reports `merged`. Queued work is still pending. After a
   failed or timed-out submission, read GitHub before you retry. If it reports `state: MERGED`
   with `the head moved`, commits you didn't verify landed. Read them and tell the user what
   landed before you finish any issue.

5. **Finish issues.** Check linked or task-scoped issues against their acceptance criteria and
   intended delivery branch. Confirm automatic closure, or close a fully resolved open issue as
   completed with the merged PR link. Keep partial issues, and those waiting on unmerged layers,
   open. Check existing state and comments before posting. An intermediate stack merge doesn't
   prove delivery, because
   [automatic closing links](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
   apply when work reaches the default branch.

6. **Clean up.** Use [Repo Cleanup](../repo-cleanup/SKILL.md) for confirmed merges. Pass merge
   results, proven merge-time source heads, branches and bases, worktrees, and known task
   resources, including device installs. Name resources that remaining stack layers still need.
   A failed issue update doesn't stop eligible cleanup.

Report merged and pending PRs, the fixes made along the way, issue results, cleanup results, and
blockers, and show the result. The report ends at what landed.
