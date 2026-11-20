---
name: cleanup
description: Use when asked to clean up finished or abandoned work, git worktrees, branches, Xcode DerivedData, task-owned dev apps/servers, simulators/emulators, disposable task folders, or run housekeeping. Excludes active work and unmerged stack layers still needed by another task.
---

# Cleanup

Remove verified, disposable resources left behind by merged or explicitly abandoned work, and run
safe housekeeping across git state and local development resources. Start from a merge handoff,
an explicit abandonment/cleanup request, or a housekeeping scope. You are done when every in-scope
eligible resource is verified removed or stopped, the local default branch is refreshed (or its
skip reason recorded) when a repository is in scope, and the report lists removals, bytes freed
when measured, retained or skipped targets with reasons, and recovery details (recorded branch
heads or reflogs).

## Guardrails

- **Proven ownership and disposal reason only:** age or a stale-looking name never makes a
  resource disposable. Preserve user changes, ignored user data, retained app data, shared caches,
  unrelated work, explicit retention requests, and resources needed by an unmerged stack layer or
  active task.
- **Explicit paths only:** resolve deletion paths to concrete locations; reject roots, home
  folders, workspace roots, unresolved variables, globs, symlinks, and shared paths without
  proven ownership. Ask before removing retained user data, shared caches, release artifacts,
  or uncertain resources.
- **Scope:** an explicit cleanup request or a handoff from [merge](../merge/SKILL.md) after an
  authorized merge covers verified task-owned temporary resources (worktrees, branches, dev
  processes, simulator/emulator installs, temporary devices, disposable test data, and explicitly
  scoped disposable task directories). It never authorizes unrelated or uncertain targets.

## 1. Inventory

When a repository is in scope, resolve the repository, worktrees, default and task branches,
relevant pull requests, and local or remote refs; refresh remote refs before judging branch tips.
Also inventory applicable candidate resources: explicitly scoped task directories, review surfaces,
development apps and servers/watchers, simulator/emulator devices and installs, slot claims,
runtime/state files, build folders, and Xcode DerivedData. For Mac apps, processes,
simulators/emulators, or Xcode DerivedData, read
[development resources](references/development-resources.md#identify-resources).

Prefer project cleanup or slot-release commands over hand-written deletion (inspect their effects
and arguments first; use them only when scoped to verified targets). Record each candidate's exact
target, owner, current tip if it is a ref, and disposal evidence. For a merged PR, obtain the
merge-time source head from the handoff or another immutable record; the branch's current tip is
not that evidence. Ask for clarification only when ownership or scope is ambiguous; assess
multiple clear candidates separately.

## 2. Check eligibility

Inspect staged, unstaged, and untracked files in affected worktrees. For an explicitly scoped task
directory, inspect its contents, ownership, retained or ignored user data, nested checkouts, and
active consumers before treating the directory as disposable. A merged PR establishes completion
only for its verified merge-time source head; a branch tip reachable from its intended base is also
complete. An explicit abandonment request establishes abandonment only for its identified commits
and task-owned changes. For housekeeping, verify completion or abandonment separately for each
branch, folder, or task; preserve unique commits unless explicitly abandoned or authorized.

## 3. Clean eligible resources

- **Review surfaces, dev processes, Mac apps, simulators/emulators, and Xcode DerivedData:**
  stop only matching review surfaces (following [Show Me](../show-me/SKILL.md) when available)
  and task-owned processes, and follow
  [development resource cleanup](references/development-resources.md#clean-up).
- **Build folders and explicitly scoped task directories:** measure and remove exact task-owned
  build folders or proven-disposable task directories while keeping retained app data and ignored
  user data. Remove a shared build cache only after user approval, when no build is active and no
  other worktree can use it.
- **Worktrees:** identify each exact inactive worktree and inspect its status, ignored files,
  `HEAD`, branch, and host ownership. Preserve active worktrees and user data; leave the current
  worktree in place for Codex. A clean detached worktree can still hold unique commits — remove
  it only when `HEAD` is reachable from a retained ref or intended base, or the user explicitly
  abandoned those commits. Inspect any host cleanup command before using it; otherwise remove
  only a worktree that is clean or contains solely identified, explicitly abandoned task changes
  with no retained ignored data. When removing a worktree on macOS/Xcode, also clean its
  DerivedData under [development resource cleanup](references/development-resources.md#clean-up).
- **Branches and refs:** recheck each tip and worktree use immediately before deleting. For
  merged work (including squash merges), the tip must still equal the verified merge-time source
  head or be reachable from the intended base. Retain and report any branch that advanced beyond
  completed or explicitly abandoned work (or whose eligibility cannot be proved). Retain any
  remote branch used as an open PR's head or base. Delete a remote branch only when eligible and
  in scope (merged task, explicitly abandoned task, or explicit request for that remote branch),
  using an expected-tip lease so a concurrent push fails the delete (see
  [git-push](https://git-scm.com/docs/git-push)). If a clean current worktree holds a branch
  being deleted, detach it at the appropriate base first; otherwise leave the worktree and branch
  in place. Delete a local branch only when no worktree holds it, using an atomic
  expected-old-tip check (see [git-update-ref](https://git-scm.com/docs/git-update-ref)). Remove
  branch-specific Git config afterward only if the branch name remains absent; retain and report
  the config if recreated.

## 4. Refresh the local default branch

When a repository is in scope (skip for directory-only cleanup), fetch the default branch's
configured upstream (or established authoritative remote ref) and compare tips. If local is behind,
fast-forward it in its existing worktree only when clean; if not checked out, confirm ancestry and
use an atomic expected-old-tip ref update. Leave it unchanged and report why if ahead, diverged,
dirty, or lacking a usable remote. Never switch another worktree to it, reset it, or force-move it.

## 5. Verify and report

Confirm stopped processes have exited, kept devices have the expected power/install state, deleted
temporary devices are absent from inventory, and removed folders or resources are absent on disk.
When a repository is in scope, recheck changed refs, affected worktrees, and the local default
branch against its upstream. Report the outcomes required above and state partial cleanup plainly.
