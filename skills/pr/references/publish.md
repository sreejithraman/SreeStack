# Publish

## Commit

Commit before review, so the review covers a committed head. Inspect status, the
complete diff, and staged files. Stage only owned paths and preserve unrelated
work. Keep the feature branch; on the default branch, create
`agent/<short-description>` first. Use the caller's immediate base, including
a parent layer for stacks.

Commit owned edits with a terse subject, and run checks needed by final staging.

## Push

Push after review, with upstream tracking. Push existing ahead commits without an
empty commit; reuse an already published head when nothing changed. Then run any
held `review-fix-loop` status command as
[Review Fix Loop's finish step](../../review-fix-loop/SKILL.md#6-finish) says. For a
caller-owned restack, use force-with-lease only on the named branch after review.
Return a lease failure to the caller as changed remote state.

Before rebasing or restacking, follow [Preserve local files](preserve-local-files.md)
for retained files affected by tracking deletions. Verify restoration after the
operation or recovery before reporting readiness.

## Create or update the PR

Prefer the GitHub connector; use `gh` for missing capabilities, current-branch
discovery, or cross-repository heads. Reuse the PR matching the head branch,
or create one. Confirm it targets the supplied immediate base.

Use [PR body](pr-body.md) for the title and description. Refresh them when fixes
change scope, evidence, or landing risk. Mark ready unless a draft was requested.

Confirm the remote head matches the intended local head, the base is correct,
and one PR represents that branch. Record its URL and remote head for
[watching](watch.md).
