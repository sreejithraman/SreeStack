# Optional Codex instructions

These sections are inactive. Merge a section into the active global instruction
file only when you want its behavior.

Replace `/absolute/path/to/SreeStack` in this file and `optional.rules` with the
path to the clone you keep outside temporary worktrees.

## New Codex worktree preflight

Before reading or editing project files in a new Codex-managed worktree based on local `main`, run the optional preflight command `node /absolute/path/to/SreeStack/codex/scripts/worktree-start.mjs` outside the sandbox. It fetches `origin` and moves the detached worktree to `origin/main` only when safe. Treat a result with `"continue": false` as a hard stop: leave the worktree unchanged and tell the user why. Skip this preflight when the user chose another base or resumed an existing worktree.
