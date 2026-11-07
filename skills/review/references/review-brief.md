# Review brief

Prepare the same scope, requirements, and evidence for every reviewer. Name each
assigned set of criteria, and include [Review](../SKILL.md) and the references those
criteria need. Absolute paths are enough for children in the shared checkout. Supply
full contents when a reviewer cannot read these files. Keep briefs and snapshots
outside the reviewed diff.

For delegated assessments, also apply [Review evidence](review-evidence.md).

## Requirements and scope

- Original user requirements or spec: the full relevant text or artifact.
- Accepted scope changes: each change and its acceptance criteria, or none.
- Repository and worktree: absolute paths.
- Original resolved base SHA and current HEAD SHA.
- Current complete `git diff <base> --` artifact, covering committed, staged, and
  unstaged changes.
- Source exclusions: exact generated review input, output, and archive paths.
- Nonignored untracked source: output of `git ls-files --others --exclude-standard`
  with those exclusions, and each file's complete contents, or none.
- Relevant repo standards and related instructions: absolute paths.
- Main risks and realistic sample requests, especially for agent instructions.
- For a skill change that removes, weakens, or moves guidance: the old text and the
  settled list, and an instruction to check each drop against them. If the list is
  missing or older than this diff, rebuild it from the old text using
  [Settle what changed](../../writing-for-agents/references/working-on-skills.md#settle-what-changed),
  and mark each group with no recorded decision as open, for review to report.

## Test evidence

- Commands, results, and full output paths for checks run on this snapshot.
- Failed, skipped, or unavailable checks and their reasons. Mark stale evidence, and
  identify the state it tested.
- When the work uses the [acceptance guidance](../../reframe/references/acceptance.md),
  include the outcome, constraints, evaluation criteria, evidence, and unresolved
  gaps. Review the target and preserved requirements together. For empirical claims,
  include the artifact identities, conditions, and raw results needed to assess the
  comparison. For qualitative claims, include the criteria, judge, rationale, and
  uncertainty.

## Round inputs

First-round reviewers, including a later wave that stays first discovery, receive
no earlier verdicts or author defenses. [Review Fix Loop](../../review-fix-loop/SKILL.md)
makes the Adversarial wave first discovery. Mark such a wave "first discovery" in its
brief, because the peer-read boundary depends on that mark. Reviewers within a round
receive no peer findings or verdicts from that round, even when concurrency requires
serial dispatch.

Later rounds include:

- original scope
- prior findings, their evidence and dispositions, stable issue IDs and first-seen
  passes, responses, and unresolved objections, marked as prior inputs rather than
  new discoveries
- the prior reviewed snapshot identity
- all changes since that snapshot, including untracked inputs
- affected behavior and dependencies, and relevant checks
- retained coverage, with reasons it still applies
- the complete scope assigned for this pass, with the original diff kept as context

Copy needed earlier-round findings and evidence into the common inputs. Ask reviewers
to verify prior claims against the updated work and assess the complete assigned
scope, including regressions from fixes. Earlier acceptance or rejection is not proof.

## Review request

Read the assigned references and apply Review to the full scope. Follow
[Delegated reviews](../SKILL.md#delegated-reviews), and return its coverage receipt.
Do not read same-round peer reports, coverage receipts, summaries, or task
conversations, including completion archives. Work read-only, and leave edits,
commits, external actions, delegation, and acceptance to the caller. Return findings
in the references' requested format.
