# Publish

Use these rules for the commit, push, and PR update owned by `/pr-prep`.

## Scope

- Inspect `git status`, the complete diff, and staged state before committing.
- Preserve unrelated work and stage explicit paths when the worktree is mixed.
- Stay on an existing feature branch. When the work sits on the repository's default branch, create `agent/<short-description>` before committing.
- Use the immediate base supplied by the caller. A stacked PR therefore targets its parent layer rather than the repository default.

## Commit And Push

Choose the matching branch state:

- **Owned local edits**: stage only the owned paths, write a terse commit subject, run any focused check made necessary by final staging, and push with upstream tracking.
- **Committed local head ahead of remote**: push the existing commits without creating an empty commit.
- **Local and remote heads match**: reuse the current remote head and continue to the PR watch without a new commit or push.
- **Caller-owned restack**: after the local review passes, update only the named owned branch with force-with-lease, then confirm the remote head. Treat a lease failure as a new remote state and return it to the caller.

After a push or reuse, resolve the remote head SHA again. That SHA replaces all earlier watch state.

## Pull Request

Prefer the GitHub connector for PR discovery, creation, metadata, and updates. Use `gh` for connector gaps, current-branch discovery, cross-repository heads, or fields the connector cannot set.

Create a PR when none exists. Update the existing PR when its head branch matches. Set its base to the supplied immediate base and confirm the base after the write.

The PR body should state:

- what changed
- why it changed
- user or developer effect
- root cause for a fix
- local verification
- stack position and adjacent PRs when applicable

Ready mode marks the PR ready for review. Draft mode preserves or sets draft state.

## Completion

Publishing is complete when the intended files are committed, the remote head matches the local head, one PR targets the intended base, and its URL and head SHA are recorded.
