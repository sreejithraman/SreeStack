# Review brief

Prepare the same scope, requirements, and evidence for every reviewer. Name
each assigned set of criteria and include this skill and the needed references.
Accessible absolute paths are sufficient for children in the shared checkout;
supply full contents when a reviewer cannot read the source. Keep briefs and
snapshots outside the reviewed diff.

For delegated assessments, use [Review evidence](review-evidence.md) to assign
workflow/pass identity, unique output paths, source exclusions, and snapshot
identity. Include its coverage receipt contract and the exact report/receipt
paths in every brief; retain the task-to-assignment mapping when dispatch returns.

For example, keep one pass's common inputs in
`.artifacts/review-inputs/pass-02/`, reviewer outputs in
`.artifacts/review-outputs/pass-02/<assignment>/`, and caller-retained originals
in `.artifacts/review-archives/pass-02/`. Name individual input files and the
reviewer's own report and receipt as absolute paths in the actual brief. Copy
needed earlier-round findings and evidence into the common inputs. These names
are examples; the read boundary comes from Review evidence, not the directory names.

First-round reviewers receive no earlier verdicts or author defenses. Later
rounds include original scope, prior findings, their evidence and dispositions,
stable issue IDs and first-seen passes, responses, and unresolved objections.
Mark supplied known issues as prior inputs rather than new discoveries.
Ask reviewers to verify those claims
against the updated work and assess the complete assigned scope, including
regressions from fixes. Earlier acceptance or rejection is not proof. Work
read-only; leave edits, commits, external actions, delegation, and acceptance
to the caller.
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
- For a follow-up pass: the prior reviewed snapshot identity, all changes since
  that snapshot (including untracked inputs), affected behavior and dependencies,
  relevant checks, and retained coverage with reasons it still applies. The
  original diff remains context; mark the complete scope assigned for this pass.
- Source exclusions: exact generated review input, output, and archive paths.
  Apply Review evidence's boundary throughout discovery, snapshotting, and rechecks.
- Nonignored untracked source: output of `git ls-files --others --exclude-standard`
  with those path exclusions, and each file's complete contents, or none.
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
Return the delegated coverage receipt with the findings, including actual read
evidence and explicit gaps. Cite only locations checked against this snapshot.
