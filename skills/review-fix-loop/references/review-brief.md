# Review brief

## Dispatch

- Agent role and requested model/effort: read the active settings.
- Context: explicitly pass `fork_turns: "none"` to the spawn tool.
- Permissions: read-only; leave edits, delegation, and acceptance to the parent.
- Emphasis: the assigned review focus; it never limits full-diff coverage.
- Review references: absolute paths to the references selected for this emphasis.

## Requirements and scope

- Original user requirements or spec: include the full relevant text or artifact.
- Accepted scope changes: include each change and its acceptance criteria, or none.
- Repository and worktree: absolute paths.
- Original resolved base SHA and current HEAD SHA.
- Current complete `git diff <base> --` artifact, covering committed, staged,
  and unstaged changes.
- Nonignored untracked files: output of `git ls-files --others --exclude-standard`
  and the complete contents of each file, or an explicit statement that none exist.
- Relevant repo standards and related instructions: absolute paths.
- Main risks and realistic sample requests, especially for agent instructions.

## Test evidence

- Commands, results, and full output paths for checks run on this snapshot.
- Failed, skipped, or unavailable checks and their reasons. Mark stale evidence
  and identify the state it tested; do not present it as current.

## Review request

Read the assigned references and review the full scope, inspecting nearby code
or instructions as needed. Return findings in the references' requested format
and report any scope you could not review.
