---
name: pr
description: Use when asked to write a PR title or body, prepare or publish a PR, or watch or babysit a PR's checks and reviews.
---

# PR

Publish a change as a PR and watch it to ready. Start from a change or an existing PR.
Leave one PR at a verified head, with its checks and feedback accounted for. You are done
when the PR is [ready or a finished draft](references/watch.md#ready-or-blocked), or you have
named exactly what blocks it. A request for text alone is done when you return the text.

[Review Sweep](../review-sweep/SKILL.md) fixes findings. [Merge](../merge/SKILL.md) lands
PRs, so send a merge request there, including `/pr yolo`. A draft request wins over `/pr
yolo`. [gh-stack](../gh-stack/SKILL.md) owns stack operations.

Resolve the PR or branch, its immediate base, and what was asked. Leave unrelated local
work out of commits, review inputs, and fixes.

## Write the title and body

Use [PR body](references/pr-body.md). Return the text locally unless asked to update the
remote description. Writing text commits and pushes nothing.

## Publish

Watching an existing PR starts at step 4.

1. **Commit it.** Follow [commit](references/publish.md#commit), so review sees a committed
   head.
2. **Get it reviewed.** Reuse review evidence that matches the complete diff against the
   immediate base and included [Show, Don't Tell](../show-dont-tell/SKILL.md). Otherwise run
   Show, Don't Tell on that diff, including docs-only changes, then
   [Review Fix Loop](../review-fix-loop/SKILL.md) on the result. Continue once review and
   verification pass.
3. **Publish it.** Follow [publish](references/publish.md#push). Publish ready for review
   unless the user asks for a draft. In T3, link each PR you create, push to, or take over,
   including every stack layer.
4. **Watch it.** Follow [watch](references/watch.md).

## Report

Give the PR link, head and base, verification, readiness, and blockers. A caller gets the same
evidence plus related issues and task resources.
