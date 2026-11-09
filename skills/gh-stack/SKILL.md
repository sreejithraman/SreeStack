---
name: gh-stack
description: Use when creating, inspecting, or changing stacked Git branches or dependent PRs with gh-stack.
metadata:
  author: github
  version: "0.2.0"
---


# gh-stack

`gh stack` manages linear chains of branches and PRs. Stacks print trunk-first:
`(main) <- auth <- api <- frontend`. Left is bottom and merges first; right is
top. `up` moves away from trunk; `down` moves toward it. Put dependencies below
their callers and use separate stacks for independent work.

## Before acting

- Choose new layers with [stack design](references/stack-design.md), up front when
  the order is known and otherwise as the work takes shape. For an existing stack,
  inspect `gh stack view --json` and edit the layer that owns the concern; use
  `git log --all -- <path>` when ownership is unclear.
- Check `gh stack --version` and `gh stack <command> --help` before relying on
  newer capabilities. `gh stack help <command>` prints top-level help instead.
  For installation/configuration, use [setup](references/commands.md#setup).
  Before a new stack's first `init`, check that setup for the `rerere` prompt;
  explicit branch names alone do not suppress it.
- Before checkout or history-changing work, follow
  [Preserve local files](../pr/references/preserve-local-files.md) in every
  affected worktree. Retain verified backups through conflicts and recovery.
- With multiple remotes, `push`, `submit`, `sync`, `rebase`, and `link` need
  `--remote <name>` unless `remote.pushDefault` selects it. `checkout` and `trunk`
  have no `--remote` flag and require that config.
- In T3, link every scoped PR taken over, created, or pushed, using
  [PR's publish step](../pr/SKILL.md#publish). A CLI operation doesn't link its layers
  to the thread.
- Before `gh stack submit`, or `gh stack link` when it creates PRs or marks them ready, run
  PR's [Prepare and Review steps](../pr/SKILL.md#publish) on each layer against its immediate
  base.
  Run each layer's held `review-fix-loop` status command unchanged once its SHA is pushed, as
  [Review Fix Loop's finish step](../review-fix-loop/SKILL.md#6-finish) says. After a restack,
  rerun the loop for that layer as a [repair pass](../review-fix-loop/SKILL.md#4-route-repairs).
  Land through [Merge](../merge/SKILL.md): run
  `gh stack merge` only from its land step.

### Worktree capabilities

Shared catalogs, foreign-owner navigation, and owner-aware recovery require a
supporting extension. Check the installed version and relevant help before
assuming those behaviors. If navigation help lacks `--print-path`, use Git's
worktree inventory to locate an existing owner and work there; do not invent
that flag, force another checkout, mix old/new writers, or upgrade outside scope.

With supported path mode, navigation or explicit-target `checkout --print-path`
returns an owner's path without taking its checkout. Unoccupied targets are
checked out here first. Use stdout only after exit 0, quote the path, and never
`eval` it. See [navigation](references/commands.md#navigation) for the guarded
shell helper and [worktree recovery](references/troubleshooting.md#driving-stacks-from-another-tool-or-worktree)
for migration and ownership limits.

## Common calls

Give explicit arguments and flags even under a PTY: bare commands can open a TUI.
Use names from the task; branch names are used verbatim, including slashes.

| Task | Non-interactive call |
| --- | --- |
| Inspect state | `gh stack view --json` |
| Create layers bottom to top | `gh stack init <branch>...` |
| Add the next layer from the top | `gh stack add <branch>` |
| Select a layer or stack | `gh stack checkout <target>` |
| Navigate | `gh stack up`, `down`, `top`, `bottom`, or `trunk` |
| Publish PR layers ready for review | `gh stack submit --auto --open` |
| Update branches without creating PRs | `gh stack push` |
| Replay upper layers after a lower-layer edit | `gh stack rebase --upstack` |
| Synchronize | `gh stack sync` |
| Merge a scoped set | `gh stack merge <target> --yes` |

Stage specific files and commit the owning layer before moving up. After an edit
below the top, rebase upstack, return to the top, then push. Read the affected
[command behavior](references/commands.md) for preconditions and partial effects.

`--open` marks new and existing PRs ready for review; without it, `submit --auto`
creates drafts. Omit it only when the user asks for drafts. Titles/bodies are
generated; use `gh pr edit` for custom text. `sync` fetches, reconciles, rebases,
pushes, and refreshes PR state; under a TTY it also asks to prune and defaults to
yes, so decline it. Delete branches after a merge through
[Repo Cleanup](../repo-cleanup/SKILL.md): `sync --prune` alone doesn't compare a
branch's tip to the PR's merge-time head, so it can delete later commits' only ref.
A diverged stack can return exit 0 with `Sync aborted`: verify the resulting state
instead of declaring synchronization.

A merge target scopes the operation: a PR includes every unmerged PR below it;
a stack number includes the whole unmerged stack. Bare numbers resolve as stack
numbers first; confirm the selected set when IDs overlap. The selected set is
all-or-nothing for direct merging. A base merge queue chooses the method despite
method flags and can land separate groups. Use `gh stack merge`, following the
caller's merge authorization. See [merge behavior](references/commands.md#merge).

Other public commands: `link`, `unstack` (see command behavior); `alias`,
`feedback` (see installed help). `switch` and the `modify` editor are menu-only;
use explicit checkout/navigation, or the documented recovery flags for an
existing interrupted operation. For non-interactive restructuring, read
[restructuring](references/troubleshooting.md#restructuring-a-stack).

## State and failures

Parse successful `view --json` stdout; status messages are on stderr.
`view --short` is human-readable. The [state schema](references/commands.md#view)
and [exit codes](references/commands.md#exit-codes) live with command behavior.

On exit 3, follow [conflict recovery](references/troubleshooting.md#rebase-conflicts-exit-3).
A failed rebase pauses; sync attempts rollback. Inspect whether restoration
completed before restarting anything. Resolve/stage only in the diagnostic's
owner worktree; a later conflict may name another owner. Supported recovery
flags use recorded owners. Keep retained files accounted for after success or
recovery. Lock and interrupted-modify diagnostics also require their specific
[recovery procedure](references/troubleshooting.md), rather than bypassing state.
