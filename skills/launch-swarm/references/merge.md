# Merge

Read this reference only in merge mode, after the full delivery passes readiness checks and before any merge.

## Authorization

Bind explicit merge authorization to the reported PR set and current head SHA for each PR. A new commit, retargeted base, or changed PR set requires a new readiness check before merge.

## Delivery Order

Treat the current PR set as a dependency graph. Independent PRs may merge in any safe order. Dependent PRs merge from base to tip. Before each merge, confirm the current head and base, required checks, required approvals, resolved accepted findings, and mergeability.

Merge through the repository's supported method and report the merge commit or resulting base SHA.

## Dependent PRs

Use the stack shape and invalidation rules in `stacked-prs.md`. Merge from base to tip. After each merge, confirm the next PR's base, diff, head, reviews, and checks before continuing.

When a merge changes a descendant's base, history, diff, or check target, retarget it to the delivery base when needed, restack it, run `/review-push-and-watch`, and recheck readiness before its merge.

After every merge, recheck the remaining PR graph. A merged independent PR may still change another PR's test merge, conflict state, or expected checks.

Stop the sequence on a conflict, new commit, missing approval, failed or missing required check, unresolved accepted finding, or changed head authorization.

## Completion

For ticketed delivery, follow the repository's issue-closing rule and verify every landed ticket against its merged PR.

Merge mode is complete when GitHub reports every authorized PR as merged in a safe order, the delivery base contains the intended change, and the tracker reports every in-scope ticket as landed, or when the sequence stops with the exact PR, state change, owner, and required action.
