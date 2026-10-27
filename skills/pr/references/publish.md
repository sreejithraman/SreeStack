# Publish

## Commit and push

Inspect status, the complete diff, and staged files. Stage only owned paths and
preserve unrelated work. Keep the feature branch; on the default branch, create
`agent/<short-description>` first. Use the caller's immediate base, including
a parent layer for stacks.

Commit owned edits with a terse subject, run checks needed by final staging,
and push with upstream tracking. Push existing ahead commits without an empty
commit; reuse an already published head when nothing changed. For a caller-owned
restack, use force-with-lease only on the named branch after review. Return a
lease failure to the caller as changed remote state.

Before rebasing or restacking, follow [Preserve local files](preserve-local-files.md)
for retained files affected by tracking deletions. Verify restoration after the
operation or recovery before reporting readiness.

## Create or update the PR

Prefer the GitHub connector; use `gh` for missing capabilities, current-branch
discovery, or cross-repository heads. Reuse the PR matching the head branch,
or create one. Confirm it targets the supplied immediate base.

Apply [thread registration](../SKILL.md#thread-registration) immediately after
creation or push; GitHub operations alone do not link the PR in T3.

Use [PR body](pr-body.md) for the title and description. Refresh them when fixes
change scope, evidence, or landing risk. Mark ready unless a draft was requested.

Confirm the remote head matches the intended local head, the base is correct,
and one PR represents that branch. Record its URL and remote head for
[CI and reviews](ci.md).
