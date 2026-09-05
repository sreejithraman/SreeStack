---
name: post-merge-cleanup
description: Clean up task-owned branches, review surfaces, development apps, slots, and build output after a confirmed merge.
---

# Post-merge cleanup

Remove only temporary resources owned by the merged task. Preserve source changes, app data, shared caches, and unrelated work.

## Scope the task

1. Resolve the repository, worktree, source branch, base branch, pull request, and merge commit with read-only checks.
2. Inventory task-owned review surfaces, development apps, slot claims, runtime files, and build folders. Prefer project cleanup commands over hand-written deletion.
3. If more than one pull request, surface, slot, or path could match, stop and ask for the exact target.

Finish this step when every proposed target has direct ownership evidence.

## Check the gates

- Confirm the pull request is merged. Stop if it is open, closed without merge, or unknown.
- Check the worktree for staged, unstaged, and untracked files. Preserve all user changes. Skip branch switching or deletion when it could disturb them.
- Resolve each delete target to an explicit path. Reject roots, home folders, workspace roots, unresolved variables, globs, symlinks, and shared paths without proven ownership.
- Treat explicit invocation or a handoff from `pr-prep` after its authorized merge as approval for task-owned cleanup in that scope. Ask before removing shared caches, user data, release artifacts, or anything not clearly owned by the task. Tool and host approval rules still apply.

Finish this step when the merge and every mutation are safe to verify.

## Clean up

Use this order so later checks see stable state:

1. Stop exact temporary review surfaces and development apps. When Showroom is available, use its skill and stop only records tied to this worktree or pull request; do not run a global cleanup.
2. Run the repository's cleanup or slot-release command when one exists.
3. Measure and remove exact task-owned build folders. Keep app data. Remove a shared build cache only when no build is active and no other worktree can be using it.
4. Remove the remote source branch if it still exists, then fetch with pruning.
5. Move a clean current worktree to the updated remote base. If the base branch is checked out in another worktree, detach at `origin/<base>`.
6. Delete the local source branch only after recording its head and confirming it matches the merged pull request. A squash merge may require forced local deletion after this check.

Leave the current worktree in place. Codex owns its lifecycle.

## Verify and report

Verify that:

- the pull request remains merged;
- task-owned review surfaces and apps are stopped;
- slot claims and build folders are gone;
- source branch refs are gone;
- the worktree is clean at the remote base or was left unchanged to protect user work.

Report the pull request, merge commit, removed resources, bytes freed, retained data, skipped items, and recovery details such as the recorded branch head or reflog. State partial cleanup plainly.
