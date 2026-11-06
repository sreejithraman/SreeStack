# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- A `Status:` line near the top of each issue file records `open`, `claimed`, or `resolved`
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Blocking and claiming

- **Blocking**: a `Blocked by: NN, NN` line near the top.
- **Claim**: Set `Status: claimed` and save before any work. If you chose the ticket yourself, re-read it first, and leave it if its `Status:` isn't `open`, if a blocker isn't `resolved`, or if an input doesn't exist. Only sessions sharing this checkout see the claim, so start parallel worktrees through one owner.
- **Resolve**: append the result under `## Comments`, then set `Status: resolved`.
