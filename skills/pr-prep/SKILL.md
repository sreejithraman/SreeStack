---
name: pr-prep
description: Use when the user asks to prepare, publish, or merge a single PR, or handle its CI or review feedback.
---

# PR Prep

Bring one branch or PR to readiness. By default, publish it as ready for review
and leave merging to the caller. Honor an explicit request to keep it in draft.
Stack management stays with the caller.

An unambiguous request to merge the scoped PR, including `/pr-prep yolo` or a
later “merge” in that PR’s context, authorizes merging once it meets the repo’s
requirements, including after fixes made during this run. No further merge
confirmation is needed. An explicit request to keep the PR in draft takes
precedence over a merge request.

1. **Scope.** Resolve the branch, immediate base, intended changes, existing PR,
   and whether draft or merge was requested. If more than one PR could be the
   merge target, ask which one before merging. Preserve unrelated work.

2. **Review.** Run `/review-fix-loop <immediate-base>` over the complete PR diff.
   Continue when review and verification pass; report blockers.

3. **Publish.** Read [publish.md](references/publish.md). Commit the task’s
   changes, push, and create or update the PR. Record the remote head and base.

4. **Watch.** Read [ci.md](references/ci.md) for checks and
   [pr-feedback.md](references/pr-feedback.md) when feedback exists. Watch the
   current pushed head and triage findings through `/review-sweep`. Hold replies
   claiming a fix and thread resolution until that fix is pushed.

5. **Repeat or finish.** If you make fixes, return to step 3. After publishing,
   post held replies and resolve eligible threads, then check CI and feedback
   again. Finish when the current published changes pass the needed checks and
   have no outstanding accepted fixes. Account for missing checks and open
   threads; report pending human approval or other blockers. For a draft, use
   the draft completion rules in the references.

6. **Hand off when merging is requested.** Otherwise, stop at readiness. Invoke
   [merge](../merge/SKILL.md) with the PR, verified head/base, readiness evidence,
   related issues, and task resources, including worktrees and device installs.
   If it returns a readiness blocker, resume the applicable prep step; report
   blockers that require someone else's action.

Report the PR link, current head, verification results, readiness or merge
result, issue completion and cleanup results when merging, and anything still needed.
