# Merge

Use only when `pr-prep` was invoked with `yolo` and the PR is ready.

Before merging, recheck the PR’s current head and base, required checks,
required approvals, unresolved review threads, and mergeability. Use results
for the current PR state. If the head or base changed since verification,
return to the prep loop before merging.

Merge only the scoped PR through the repo’s supported method, matching the
verified head so a concurrent push cannot merge unreviewed changes. Respect
branch protection and the repo’s merge queue; do not bypass either. Leave
stack changes and other PRs to the caller.

If approval, conflicts, or another requirement blocks merging, report what is
needed. If the repo queues the merge, watch its result and report any blocker.
Confirm GitHub reports the PR as merged before claiming completion; include
the merge commit or resulting base SHA. A queued merge is still pending.
