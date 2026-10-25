---
name: repo-cleanup
description: Use when the user asks to clean up finished or abandoned work, worktrees, task-owned dev apps or simulators/emulators, or other repository housekeeping.
---

# Repository cleanup

Clean up only resources whose owner and disposal reason are established. A merged task, an explicitly abandoned task, and routine housekeeping use the same process; age or a stale-looking name alone does not make something disposable. Preserve user changes, retained app data, shared caches, and unrelated work. Cleanup includes task-owned development processes, simulator/emulator installs, and temporary devices created for the task; honor explicit retention requests.

1. **Inventory.** Resolve the repository, worktrees, default and task branches,
   relevant pull requests, and candidate resources. Include review surfaces,
   development apps and their servers/watchers, simulator/emulator devices and
   installs, slot claims, runtime files, build folders, and local or remote refs
   as applicable. Follow [development resource discovery](references/development-resources.md#identify-resources)
   for apps, processes, simulator/emulator devices, and installs.
   Refresh remote refs before judging branch tips.
   Prefer project cleanup commands over hand-written deletion. For each candidate,
   record its exact target, owner, current tip if it is a ref, and disposal
   evidence. For a merged PR, obtain the source head verified at merge time
   from the handoff or another immutable record; the branch's current tip is
   not that evidence. Ask for clarification only when a candidate's owner or intended
   scope is ambiguous; assess multiple clear candidates separately.

2. **Check eligibility.** Inspect staged, unstaged, and untracked files in
   affected worktrees. A merged pull request establishes completion only for its
   merge-time source head; a branch tip reachable from its intended base is also complete.
   An explicit request to abandon work establishes abandonment for its identified
   commits and task-owned staged, unstaged, or untracked changes. Preserve
   unrelated changes, ignored user data, and anything whose ownership is uncertain.
   For housekeeping, verify completion or abandonment separately for each
   branch or task. Preserve unique commits unless the user explicitly abandoned
   them or authorized their removal. Resolve deletion paths to explicit
   locations; reject roots, home folders, workspace roots, unresolved variables,
   globs, symlinks, and shared paths without proven ownership. Ask before
   removing retained user data, shared caches, release artifacts, or uncertain resources.
   Preserve resources still needed by an unmerged stack layer or another active task.

3. **Clean eligible resources.** Stop only matching review surfaces and
   development processes; when Showroom is available, follow its skill for surfaces
   tied to this task or worktree. Inspect a repository cleanup or slot-release
   command's effects and arguments before running it; use it only when it can be
   scoped to verified targets. For Mac development apps, supporting processes,
   and simulator/emulator installs and devices, follow
   [development resource cleanup](references/development-resources.md#clean-up).
   Measure and remove exact task-owned build folders, keeping retained app data.
   Remove a shared build cache only after approval,
   when no build is active and no other worktree can use it.

   When worktree removal is in scope, identify an exact inactive worktree and
   inspect its status, ignored files, HEAD, branch, and host ownership. Preserve
   active worktrees and user data. A clean detached worktree can still hold
   unique commits; remove it only when HEAD is reachable from a retained ref or
   intended base, or the user explicitly abandoned those commits. Inspect a
   host cleanup command's effects before using it; otherwise remove only a
   worktree that is clean or contains solely identified, explicitly abandoned
   task changes, with no retained ignored data. Leave the current worktree in
   place for Codex.

   Before deleting any branch, recheck its tip and worktree use. For merged work,
   the tip must still equal the source head verified at merge time or be reachable
   from the intended base. If neither can be proved, retain the branch. Retain
   and report a branch that advanced beyond completed or explicitly
   abandoned work. Check whether any open PR uses a remote branch as its head or
   base; retain it if so. Delete a remote branch only when its current tip is
   eligible and its deletion is in scope: merged task cleanup, explicitly
   abandoned task cleanup, or an explicit request for that remote branch. Use
   an expected-tip lease for remote deletion so a concurrent push
   causes the delete to fail; see [git-push](https://git-scm.com/docs/git-push).

   If a clean current worktree holds a branch being deleted, detach it at the
   appropriate base first; otherwise leave the worktree and branch in place.
   Delete a local branch only if no worktree holds it, using an atomic
   expected-old-tip check; see [git-update-ref](https://git-scm.com/docs/git-update-ref).
   After deletion, remove its branch-specific Git config only if the branch name
   remains absent; retain and report the config if that name has been recreated.
   This also covers squash-merged branches after their merge-time source head is verified.

4. **Refresh the local default branch (`main` here).** Fetch its configured
   upstream, or the repository's explicitly established authoritative remote
   ref, then compare tips. If local is behind, fast-forward it in its existing
   worktree only when that worktree is clean. If it is not checked out, confirm
   ancestry and use an atomic expected-old-tip ref update. Leave it unchanged
   and report why when it is ahead, diverged, dirty in its checkout, or lacks a
   usable remote. Do not switch another worktree to it, reset it, or force-move it.

5. **Verify and report.** Confirm stopped processes have exited, kept devices
   have the expected power and install state, and deleted temporary devices no
   longer appear in the platform's device inventory. Recheck changed resources
   and refs, affected worktrees, and the local default branch against its selected
   upstream. Report what was removed, bytes freed when measured, what was retained
   or skipped and why,
   and recovery details such as recorded branch heads or reflogs. State partial
   cleanup plainly.

An explicit cleanup request or a handoff from [merge](../merge/SKILL.md) after an authorized merge covers disposal of verified task-owned temporary resources, including development processes, simulator/emulator installs, disposable test data, and temporary devices created for the task, in that scope. It does not authorize unrelated or uncertain targets.
