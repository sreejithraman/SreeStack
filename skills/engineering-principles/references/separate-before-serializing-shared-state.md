# Separate Before Serializing Shared State

Identify concurrent writers and the facts each owns before adding a lock. Independent
facts can use independently owned files, keys, or objects and combine when read.
Separate fields in one read-modify-write file still share a write target.

When one canonical mutable object is a real invariant, enforce its owner or access
protocol structurally: a single-writer actor, transaction, lock, exclusive phase,
or compare-and-swap. Instructions alone do not coordinate concurrent writes.
Check overlaps, retries, and failure recovery at that protocol. Agent assignments
follow [orchestration](../../orchestration/SKILL.md)'s host workspace rules; this
principle does not create worktrees or authorize new top-level threads.
