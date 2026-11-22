---
name: merge
description: Use when the user asks to merge a PR or stack, or to keep a finished change, and finish its issues and cleanup.
---

# Merge

Land a finished change. Start from a PR, a stack, or a local change the user kept.
Leave it merged and shown, with issues settled and task resources cleaned up. You are done when
GitHub reports every PR in the set merged, and each issue and cleanup target has a result.

A workflow's **Land** finish line, picked under its policy, is a merge request too. A merge
request authorizes landing the scoped work, closing fully resolved issues, and cleaning up
task-owned temporary resources. It also covers fixes that
[continue](../review-sweep/references/classification.md#continue-or-stop). Honor the user's
limits.

## Shared rules

- **Sole readiness gate:** [`pr_state`](../pr/references/watch.md#read-the-state) is the only
  valid readiness and merge gate. Host PR tools (`pull_request_read`, `pull_request_merge`, or a
  GitHub connector) skip `pr_state` and do not check `review-fix-loop`, `## Provisional`, or
  complete paginated readiness, so never use them to bypass `pr_state`.
- **Caller-owned repair mode:** if the caller keeps its own repair owner, repair nothing—return
  every failure, comment, missing review or verification gap, and stop to the caller so it can
  resume that owner.

## Steps

1. **Scope.** Identify the repository, PRs, landing branch, and evidence. Ask for the target if a
   merge request could refer to several PRs. If the work has no PR, publish it through
   [PR](../pr/SKILL.md#publish), then continue here. For stacks, use
   [gh-stack](../gh-stack/SKILL.md) to resolve the exact merge set and command target.
   Authorization must cover every layer. An already merged PR skips to step 4.

2. **Bring to ready.** Follow PR's [watch](../pr/references/watch.md). Failures, comments,
   conflicts, and commits you didn't push go through continue or stop; fixes that continue get one
   line in your report. A wake resumes this step, because the merge request still stands.

   `pr_state` blocks any head without a passing `review-fix-loop` status (including after a base
   update or restack). Take missing review, stale verification, or unverified head commits (read
   them first) through PR's Prepare and Review steps—following
   [Review Fix Loop's repair routing](../review-fix-loop/SKILL.md#route-repairs) (clean disjoint
   rebases carry forward coverage onto the new pushed SHA; edits or interacting base changes run a
   repair pass)—publish any fixes, and recheck every affected layer. Before local history changes,
   apply [Preserve local files](../gh-stack/references/preserve-local-files.md).

   An open `## Provisional` section (`pr_state` blocker) is a stop; a merge request alone never
   clears it. On any stop, cancel any armed landing and confirm cancellation (`gh pr merge
   --disable-auto`, or for a queue the `dequeuePullRequest` mutation), leave the PR open, and use
   [Show Me](../show-me/SKILL.md) to show the user what happened, including anything that landed
   first.

3. **Land.** Capture what the user will want to see first with Show Me so `pr_state` is the last
   read before landing.

   **Pre-merge gate:** before any merge call (`pull_request_merge`, `gh pr merge`,
   `gh stack merge`, or a GitHub connector), run `pr_state --head <verified head>` on every PR in
   the set and verify all of the following for the whole set:
   - `pr_state` returned [ready](../pr/references/watch.md#ready-or-blocked) (`exit 0`) with a
     passing `review-fix-loop` status on that exact `<verified head>` SHA—required for every PR,
     including docs-only changes, recording current-head review and
     [Show, Don't Tell](../show-dont-tell/SKILL.md).
   - Required verification covers that exact head, and no commits on it are unverified.
   - `baseRefName` is the landing branch, or for a stack layer its parent in the scoped set (any
     other base is a stop).
   - No closing link would close an unfinished issue.

   Name each PR's exact `<verified head>` SHA and passing `review-fix-loop` status before calling
   merge. If any PR fails the gate, do not merge—return to step 2 (or return the gap to the
   caller's repair owner). Land the set only when all of it is ready.

   **Execute and confirm:** follow repository merge settings, protections, and queues. For one PR,
   merge with an exact-head guard (`pull_request_merge` with `expectedHeadSha: <verified head>`
   when host PR tools are available, or `gh pr merge --match-head-commit <verified head>`
   otherwise), and leave branch deletion to cleanup. For stacks, use `gh-stack`, with guards
   against unverified head changes on every layer: head preconditions, or enforced current-head
   checks and fresh approvals after pushes. Without them, report the blocker (branch protection
   must prevent unverified head changes).

   Confirm with `pr_state` that each PR reports `merged`. Queued work is still pending. After a
   failed or timed-out submission, read GitHub before you retry. If it reports `state: MERGED`
   with `the head moved`, commits you didn't verify landed; read them and tell the user what
   landed before you finish any issue.

4. **Finish issues.** Check linked or task-scoped issues against their acceptance criteria and
   intended delivery branch. Confirm automatic closure, or close a fully resolved open issue as
   completed with the merged PR link. Keep partial issues, and those waiting on unmerged layers,
   open. Check existing state and comments before posting. An intermediate stack merge doesn't
   prove delivery, because automatic closing links apply only when work reaches the default
   branch.

5. **Clean up.** Use [Cleanup](../cleanup/SKILL.md) for confirmed merges. Pass merge results,
   proven merge-time source heads, branches and bases, worktrees, and known task resources,
   including device installs. Name resources that remaining stack layers still need. A failed issue
   update doesn't stop eligible cleanup.

Report merged and pending PRs, the fixes made along the way, any `Deferred` findings and `Stops`
returned by PR or review steps, issue results, cleanup results, and blockers, and show the result.
The report ends at what landed.
