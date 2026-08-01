# Merge

Read this reference only in merge mode, after the full delivery passes readiness checks and before any merge.

## Authorization

Bind explicit merge authorization to the reported PR set and current head SHA for each PR. A new commit, retargeted base, or changed PR set requires a new readiness check before merge.

## Single PR

Confirm the current head and base, required checks, required approvals, resolved accepted findings, and mergeability. Merge through the repository's supported method and report the merge commit or resulting base SHA.

## PR Stack

Use the stack shape and invalidation rules in `stacked-prs.md`. Merge from base to tip. After each merge, confirm the next PR's base, diff, head, reviews, and checks before continuing.

When a merge changes the next layer's base, history, diff, or check target, retarget it to the delivery base when needed, restack it, run `/review-push-and-watch`, and recheck readiness before its merge.

Stop the sequence on a conflict, new commit, missing approval, failed or missing required check, unresolved accepted finding, or changed head authorization.

## Completion

Merge mode is complete when every authorized PR is merged in order and the delivery base contains the intended change, or when the sequence stops with the exact PR, state change, owner, and required action.
