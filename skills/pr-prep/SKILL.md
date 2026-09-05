---
name: pr-prep
description: Prepare one branch or PR for review, handle CI and feedback, and optionally merge when invoked with yolo.
---

# PR Prep

Bring one branch or PR to readiness. By default, publish it as ready for review
and leave merging to the caller. Honor an explicit request to keep it in draft.
Stack management stays with the caller.

`/pr-prep yolo` authorizes merging this PR once it meets the repo’s merge
requirements, including after fixes made during this run. No further merge
confirmation is needed. An explicit request to keep the PR in draft takes
precedence over `yolo`.

1. **Scope.** Resolve the branch, immediate base, intended changes, existing PR,
   and whether draft or `yolo` was requested. Preserve unrelated work.

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

6. **Merge with `yolo`.** Once ready, read [merge.md](references/merge.md) and
   merge the PR. After GitHub confirms the merge, run `/post-merge-cleanup`
   with the PR, merge commit, branch, base, worktree, and known task-owned
   resources. Without `yolo`, stop at readiness.

Report the PR link, current head, verification results, readiness or merge
result, cleanup result, and anything still needed.
