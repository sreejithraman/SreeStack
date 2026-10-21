# Review brief

Prepare the same scope, requirements, and evidence for every reviewer. Name
each assigned set of criteria and include this skill and the needed references.
Accessible absolute paths are sufficient for children in the shared checkout;
supply full contents when a reviewer cannot read the source. Keep briefs and
snapshots outside the reviewed diff.

First-round reviewers receive no earlier verdicts or author defenses. Later
rounds include original scope, prior findings, their evidence and dispositions,
responses, and unresolved objections. Ask reviewers to verify those claims
independently and assess the current complete snapshot, including regressions
from fixes. Earlier acceptance or rejection is not proof. Work read-only;
leave edits, commits, external actions, delegation, and acceptance to the caller.
An assigned emphasis never limits full-scope reading. Reviewers within a round
receive no peer findings or verdicts from that round, even when concurrency
requires serial dispatch; earlier-round findings remain part of later briefs.

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
- When the work uses the [acceptance guidance](../../verify/references/acceptance-contract.md),
  include the outcome, constraints, evaluation criteria, evidence, and unresolved
  gaps. Review the target and preserved requirements together. For empirical
  claims, include the artifact identities, conditions, and raw results needed
  to assess the comparison. For qualitative claims, include the criteria, judge,
  rationale, and uncertainty. Inspect whether changes to tests, fixtures, or
  benchmarks lost sensitivity or changed the measured work; a legitimate method
  repair needs its rationale and comparable reruns.

## Review request

Read the assigned references and review the full scope, inspecting nearby code
or instructions as needed. Return findings in the references' requested format
and report any scope you could not review.
