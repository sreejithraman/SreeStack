---
name: review-push-and-watch
description: Use when one branch or GitHub PR must be reviewed locally, pushed, watched through CI and review feedback, and fixed until ready or blocked.
---

# Review, Push, And Watch

This skill owns one head branch, its immediate base, and one GitHub PR. Stack-wide branch changes and merges stay with the caller.

## Modes

- **Ready mode**: default. Publish the PR as ready for review and stop when it is merge-ready, waiting for human action, or blocked.
- **Draft mode**: keep the PR in draft and stop when its current head is locally sound, pushed, and clear of current actionable feedback and CI failures.

## Steps

1. Scope one PR.

   Resolve the repo, owned worktree changes, head branch, immediate base, existing PR if any, intended diff, mode, and checks used by the repository.

   Finish this step when one writable head, one base, one owned diff, and at most one PR are resolved, or return an exact blocker.

2. Run the local review.

   Run `/review-fix-loop <immediate-base>` over the complete PR diff.

   Finish this step when the local review and verification are current and green, or return its explicit blocker.

3. Publish the current head.

   Before staging or pushing, read `references/publish.md` fully. Commit only owned changes, push the head branch, and create or update the PR in the requested mode.

   Record the pushed head SHA and the PR's current check target. Finish this step when the remote branch and PR both point at the published change.

4. Watch the PR.

   Before inspecting checks, read `references/ci.md` fully and watch the current PR check set to a terminal state.

   When comments, reviews, or unresolved threads exist, read `references/pr-feedback.md` fully before editing code or replying. Combine technical claims from PR feedback and code-caused CI failures into one `/review-sweep` pass. Keep operational CI states with the CI rules. Hold fixed replies and thread resolution until the reviewed fix reaches the remote PR head.

   Finish this step when every current feedback item has a disposition and every expected check is accounted for under the mode-specific completion rules in `references/ci.md` or has an exact blocker.

5. Publish fixes and repeat.

   When step 4 changes the local diff, rerun `/review-fix-loop <immediate-base>`, commit every owned edit, push it, and record the new head and check target. Then post the held replies, resolve eligible threads against that published head, and return to step 4.

   In ready mode, stop when the current published state has no unblocked accepted findings, local verification is current, required checks pass, expected checks are accounted for, and review threads are handled. Report missing human approval as waiting for human action.

   In draft mode, stop at draft-stable when the current head is locally sound and pushed, current actionable feedback is handled, every started check has a terminal disposition, no code-caused check failure remains, and checks absent under draft policy are recorded.

## Report

End with:

- mode
- branch and immediate base
- PR URL and current head SHA
- review/fix loop result
- commits and pushes made
- comments, reviews, replies, and thread state
- required and expected CI results
- ready, draft-stable, waiting for human action, or exact blocker
