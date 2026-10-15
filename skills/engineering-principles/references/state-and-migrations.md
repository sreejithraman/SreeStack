# State, retries, and migration

## Outcome-Oriented Execution

For a planned rewrite, define the target behavior and explicit verification
boundaries. Converge on that target instead of accumulating temporary compatibility
machinery solely to preserve every private intermediate state. Temporary breakage
belongs only inside a scoped, reversible development phase; keep delivered commits,
PR layers, shared branches, and rollout stages coherent under their own checks.
Use [Sequence work into verifiable units](execution.md#sequence-work-into-verifiable-units) to choose
those boundaries and prove the complete target before declaring completion.

## Make Operations Idempotent

For a mutating command, lifecycle step, or retry loop, ask what a second run and
a crash between effects leave behind. Inspect and reconcile partial state before
repeating work. Use stable operation identity, transactional updates, deduplication,
or explicit recovery states where the effects need them. Reuse established provider
idempotency and recovery contracts rather than inventing a parallel one.

Test representative interruption points and duplicate requests through the real
operation. A restart should converge to the intended state or expose a recoverable
pending state, without silently duplicating effects. For an uncertain external
write, inspect its result before replaying it. Repetition does not grant permission.

## Migrate Callers Then Delete Legacy APIs

For an internal interface the project can migrate together, inventory its callers,
move them to the supported route, update examples and tests, and remove the obsolete
route in the same refactor wave. Leaving both available creates competing examples
for the next contributor. Preserve distinct adapters and externally required
compatibility paths. Where deployment or external consumers require staged support,
name its owner, removal condition, and verification rather than breaking them for
local simplicity.

## Separate Before Serializing Shared State

Identify concurrent writers and the facts each owns before adding a lock. Independent
facts can use independently owned files, keys, or objects and combine when read.
Separate fields in one read-modify-write file still share a write target.

When one canonical mutable object is a real invariant, enforce its owner or access
protocol structurally: a single-writer actor, transaction, lock, exclusive phase,
or compare-and-swap. Instructions alone do not coordinate concurrent writes.
Check overlaps, retries, and failure recovery at that protocol. Agent assignments
follow [orchestration](../../orchestration/SKILL.md)'s host workspace rules; this
principle does not create worktrees or authorize new top-level threads.
