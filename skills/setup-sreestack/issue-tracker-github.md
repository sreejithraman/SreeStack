# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --json title,body,comments,assignees,blockedBy`
- **List issues**: `gh issue list --json number,title,body,assignees,blockedBy`
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## Blocking and claiming

- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh issue edit <ticket> --add-blocked-by <blocker>`. The `blockedBy` field also lists closed blockers, so check each node's `state`. Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the ticket body.
- **Claim**: Run `gh issue edit <n> --add-assignee @me` as the session's first write. If you chose the ticket yourself, re-read it first, and leave it if it has an assignee, even your own account, if a blocker is open, or if it isn't ready under the Ready rule in the `to-tasks` skill. If someone gave you a ticket another account holds, ask them before you claim it.
