# Open-source readiness

Audit date: 2026-09-06. The repository remains private. This checklist records
release work; it does not approve publication.

## Completed

- Removed 17 local branches whose tips were merged or matched a merged PR head.
- Removed nine remote branches after checking their tips against merged PRs.
- Removed one clean old worktree. The final worktree list contains the main
  checkout and the open-source prep checkout.
- Saved and verified a Git bundle of all refs before cleanup, outside tracked
  files. No history rewrite or garbage collection ran.
- Added setup and contribution notes, plus six upstream license notices fetched
  at the recorded import revisions. See THIRD_PARTY_NOTICES.md for their scope.
- Enabled automatic deletion of merged PR branches.
- Ran Gitleaks 8.30.1 with redacted reports: no findings in all 169 commits in
  the pre-cleanup bundle, 146 commits on remaining refs, or current files.
  This scan covers known patterns, not every possible secret or private fact.
- Compared the Apache-2.0 eli5 skill with its recorded import; it matches byte
  for byte.
- Checked commit author emails on remaining refs; all use GitHub noreply addresses.
- Found no user-specific absolute paths or personal email addresses in current
  skill files with the patterns checked.

## Resolve before publication

- [ ] Choose a root license for original work and add its copyright notice.
  Keep upstream terms and notices attached to imported material.
- [ ] Resolve `skills/liquid-glass`: no license file appeared in the upstream
  tree at `2c1b2789c30dc2c9208f3b9a3811d42480714577`, and the local skill
  declares no license. Obtain permission or remove that imported material
  from the public release. Account for copies in Git history as well.
- [ ] Decide how to handle `skills/react-doctor`. Its recorded revision uses
  Modified MIT with restrictions on model training and certain paid services.
  Keep the exact terms, obtain different terms, or omit it from the public
  release. A plain MIT label would not describe the whole collection.
- [ ] Resolve unknown import revisions for animate, design-eng, and
  refactoring-ui-skill; check that notices cover the actual imported material.
- [ ] Review old filenames, commit messages, and removed documents for private
  context. Branch deletion does not remove content from GitHub history.
- [ ] Pick the public history: retain the reviewed history or publish a clean
  initial commit. If private or unlicensed material needs removal, prepare
  and review that change before publishing.

## Before inviting users

- [ ] Try installation in a fresh skill directory and a supported agent host.
  Test representative skills; document host and tool requirements that fail.
- [ ] Add CI for skill structure, relative links, and secret scanning. Select
  required checks once they pass on this repository.
- [ ] Set a main-branch ruleset, including force-push and deletion controls.
- [ ] Check available GitHub secret scanning and push protection settings.
- [ ] Set up private vulnerability reporting and document a working contact
  before adding a security policy that promises a reporting channel.
- [ ] Review repository description, topics, and release notes.
- [ ] Approve the final diff and make the repository public only after the
  release blockers above are resolved.
