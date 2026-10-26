---
name: pr
description: Draft PR text, prepare or publish a PR, fix review feedback, babysit CI and reviews, or merge when requested.
---

# PR

Resolve the target PR or branch, its immediate base, intended changes, and
requested outcome. Exclude unrelated local work from review inputs and fixes.

- **Title/body:** inspect the diff and evidence, then use [PR body](references/pr-body.md).
  Return text locally unless asked to update the remote description. This route
  does not commit, push, or run the delivery workflow.
- **Watch/babysit/feedback:** start with [CI and reviews](references/ci.md).
  For comments and threads, read [PR feedback](references/pr-feedback.md).
  An unchanged PR needs no local review or publication.
- **Prepare/publish:** use the delivery workflow below.
- **Merge:** reuse applicable delivery evidence; complete missing preparation
  below, then hand off to [merge](../merge/SKILL.md).

Publish ready for review unless the user requests a draft. Merge only when
requested; `/pr yolo` or a later “merge” for this PR authorizes landing after
required fixes and checks. A draft request takes precedence. Ask for the target
if a merge request could refer to several PRs. Stack operations belong to
[gh-stack](../gh-stack/SKILL.md).

## Thread registration

In T3, call `link_pull_request` immediately for each PR taken over, created, or
pushed, including every stack layer. Follow live host rules for registration;
background mentions and read-only reviews need no link. Report registration
failures separately from publication.

## Deliver changes

1. Invoke [Show, Don't Tell](../show-dont-tell/SKILL.md) on the complete PR diff
   against the immediate base, including docs-only changes. Then run
   [review-fix-loop](../review-fix-loop/SKILL.md) over the resulting complete diff.
   Reuse matching preparation and review evidence. Record that review included
   this pass and tie readiness evidence to the published head/base.
   Continue after review and verification pass.
2. [Publish](references/publish.md) the owned changes and record the remote head
   and base.
3. Follow [CI and reviews](references/ci.md) through fixes, waiting, and readiness.

At readiness, hand off unless merging was requested. For preparation requested
by Merge, return the PR, verified head/base, readiness evidence, related issues,
and task resources to that original caller; it retains the full merge set and
landing responsibility. For a direct PR merge request, pass the same evidence
and resources to `merge`; it owns landing, issue completion, and cleanup.

Report the PR link, current head, verification, readiness or merge result, and
remaining blockers. Include issue and cleanup results when merging.
