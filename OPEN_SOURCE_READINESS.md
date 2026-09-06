# Release notes

Checked on 2026-09-06. The repo remains private.

## Done

- Added MIT for original work and kept upstream notices. React Doctor keeps
  its Modified MIT terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- Removed merged branches and the remaining old worktree. Saved a verified
  recovery bundle outside tracked files. Enabled deletion of merged PR branches.
- Added setup and contribution notes.
- Added one CI workflow for required skill fields, source entries, inline
  local Markdown links, whitespace, and Gitleaks secret scanning.
- Gitleaks found no secrets in the 169 commits saved before cleanup or in
  current files. Reviewed filenames and commit subjects, and checked historical
  file contents for personal paths, email addresses, and Tailscale addresses.
  The checks found one old `/Users/sree/...` path in the removed gemini-review
  skill; other matches were examples or upstream contacts. Keep the history.
  These checks do not prove that every private fact is absent.
- Confirmed that all 42 current skills have required fields, source entries,
  and working inline local Markdown file links.

## Kept as requested

Liquid Glass stays in the collection at the owner's direction. The source
record still notes that no license was found at the imported revision.
Unknown import revisions remain recorded in SOURCES.md. No further upstream
license research is planned for this release.

## At publication

GitHub rejects branch protection and rulesets for this private repo on its
current plan. After making it public:

- Enable protection for `main`: require the `Skills and secrets` check,
  block force pushes, and block branch deletion. Extra reviewers are optional.
- Enable GitHub secret scanning, push protection, and private vulnerability
  reporting where available.

The checks run on pushed branches and pull requests. Merge the prep branch
before changing visibility. No history rewrite or paid plan is needed for
this preparation.
