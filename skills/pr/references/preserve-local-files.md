# Preserve local files during history changes

Before a rebase, restack, sync, or checkout that can replay tracking deletions,
inspect the affected commits and worktrees for retained local files. A clean
`git status` does not account for ignored files, and a file can still be tracked
even when an ignore rule matches its path. Include retained files whose paths
are deleted from tracking anywhere in the replayed commits, even if those paths
reappear in the final tree.

For each affected worktree:

1. Record the exact retained paths and hash their current local bytes. Copy them
   outside every checkout the operation can change. Verify backup hashes before
   starting; preserve local edits even when committed blobs are available.
2. Perform the scoped history operation. Keep the backups through conflicts,
   retries, and aborts. A failed operation can still have changed local files.
3. Inspect each retained path after the operation. Restore missing files from
   the verified backup. If the operation left different content, preserve both
   versions and reconcile the intended result before overwriting either.
4. Compare restored bytes with the recorded hashes, and verify intended tracking
   and ignore state. Check every affected worktree after success or recovery.
   Retain backup paths and unresolved differences at handoff; preservation is
   complete only when every retained file is accounted for.

Use exact paths and keep backup data out of commits and review packets. Git blobs
are a recovery source only when their bytes match the recorded local hashes.
Let the caller's existing authorization govern the history operation.
