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
  valid readiness and merge gate; host PR tools (`pull_request_read`, `pull_request_merge`, or a
  GitHub connector) do not run or replace it because they do not check `review-fix-loop`,
  `## Provisional`, or complete paginated readiness.
- **Caller-owned repair mode:** if the caller keeps its own repair owner, handle any stop below
  first, then repair nothing—return every failure, comment, missing review or verification gap,
  and stop to the caller so it can resume that owner.

## Steps

1. **Scope.** Identify the repository, PRs, landing branch, and evidence. Ask for the target if a
   merge request could refer to several PRs. If the work has no PR, publish it through
   [PR](../pr/SKILL.md#publish), then continue here. For stacks, use
   [gh-stack](../gh-stack/SKILL.md) to resolve the exact merge set and command target.
   Authorization must cover every layer. An already merged PR skips to step 4.

2. **Bring to ready.** Follow PR's [watch](../pr/references/watch.md). Classify every state read
   before dispatching repairs or returning control: failures, comments, conflicts, and commits you
   didn't push go through continue or stop; fixes that continue get one line in your report. A
   wake resumes this step, because the merge request still stands.

   **Handle stops first.** An open `## Provisional` section (`pr_state` blocker) is a stop; a
   merge request alone never clears it. On any stop (including a base mismatch or `## Provisional`
   blocker found on the final read), cancel any armed landing and confirm cancellation (`gh pr
   merge --disable-auto`, or for a queue the `dequeuePullRequest` mutation), leave the PR open,
   use [Show Me](../show-me/SKILL.md) to show the user what happened (including anything that
   landed first), and stop without repairing or landing.

   **Route repairable gaps** (when no stop and no caller-owned repair mode apply). `pr_state` blocks any head
   without a passing `review-fix-loop` status, including after a base update or restack. Read any
   unverified head commits first. Take missing review, missing or stale verification, or
   unverified head commits through PR's Prepare and Review steps, using
   [Review Fix Loop's repair routing](../review-fix-loop/SKILL.md#route-repairs) for a new head of
   reviewed work (clean disjoint rebases carry forward coverage onto the new pushed SHA; edits or
   interacting base changes run a repair pass). Publish any fixes, post the `review-fix-loop`
   status, and recheck every affected layer. Before local history changes, apply
   [Preserve local files](../gh-stack/references/preserve-local-files.md).

3. **Land.** Capture what the user will want to see first with Show Me so `pr_state` is the last
   read before landing.

   **Pre-merge gate:** before submitting any merge (`pull_request_merge`, `gh pr merge`,
   `gh stack merge`, or a GitHub connector), run
   `python3 <pr skill folder>/scripts/pr_state.py <number or URL> --head <verified head>`
   (outside the sandbox, per `watch.md`) on every PR in the set and verify all of the following
   for the whole set:
   - The PR is [ready](../pr/references/watch.md#ready-or-blocked) under that `pr_state` read:
     every `to_settle` item and feedback is settled (including newly arrived items), there is no
     `## Provisional` blocker, and `status` is `ready` (or non-`ready` only from
     `watch.md`-permitted current-head CI dismissals or a user-approved unanswered review
     request).
   - That exact `<verified head>` SHA carries a passing `review-fix-loop` status—required for
     every PR, including docs-only changes, recording current-head review and
     [Show, Don't Tell](../show-dont-tell/SKILL.md).
   - Required verification covers that exact head, and no commits on it are unverified.
   - `baseRefName` is the landing branch, or for a stack layer its parent in the scoped set (any
     other base is a stop).
   - No closing link would close an unfinished issue.

   Name each PR's exact `<verified head>` SHA and passing `review-fix-loop` status before
   submitting the merge. If any PR fails the gate, do not merge—on any stop, handle it per step 2
   and stop; otherwise return the gap to step 2. Land the set only when all of it is ready.

   **Execute and confirm:** follow repository merge settings, protections, and queues. For one PR,
   merge directly with an exact-head guard (`pull_request_merge` with
   `expectedHeadSha: <verified head>` and without `auto: true` when host PR tools are available,
   or `gh pr merge --match-head-commit <verified head>` otherwise), and leave branch deletion to
   cleanup. Do not arm `auto: true` or `--auto` on a single PR; if a direct merge fails, read
   GitHub and return to step 2. If the repository requires a merge queue, queue only when branch
   protections or queue rules enforce current-head review on any later push (otherwise report the
   blocker). For stacks, use `gh-stack` (which owns stack set selection and queue handling; never
   `pull_request_merge` with `stack: true`). Because neither `gh stack merge` nor
   `pull_request_merge` enforces per-layer head preconditions at submission (and earlier
   `pr_state` reads do not guard against pushes before merge), land a stack only when branch
   protections enforce current-head review on every layer (for example, required
   `review-fix-loop` status or required approvals dismissed on new pushes); otherwise report the
   blocker.

   Confirm with `python3 <pr skill folder>/scripts/pr_state.py <number or URL> --head <verified head>`
   that each PR reports `merged`. Queued work is still pending. After a failed or timed-out
   submission, read GitHub before you retry. If it reports `state: MERGED` with `the head moved`,
   commits you didn't verify landed; read them and tell the user what landed before you finish
   any issue.

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
