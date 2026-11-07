# Review evidence

Use this when you assign delegated reviews. Reviewers follow
[Delegated reviews](../SKILL.md#delegated-reviews), which holds the coverage
receipt and their read and write limits.

## Assign outputs

Give the review loop a stable `workflow_id` and an integer `pass`, starting at 1.
A pass binds one frozen scope and snapshot. Use the next pass to assess changed
inputs. A retry on the same inputs keeps the pass and gets a new assignment key.
Keep the workflow ID when fixes, PR preparation, or integration reuse its coverage.
A separate loop gets a new ID and links any earlier evidence it reuses. Keep task
counters separate, because they do not set the pass number.

Give each assessment a unique assignment key and output directory, including
retries and later rounds. Record workflow/pass, criteria, configured provider,
model and options, base/head, snapshot identity, required inputs, and exact report
and coverage paths in the brief or task. A snapshot identity must cover the diff and
complete untracked inputs, not just HEAD.

Bind the returned task ID to its assignment. Retain its outcome and completion time
from host records when available, and mark unavailable metadata unknown.

## Set boundaries

Designate generated review input, output, and archive paths before collecting
source. Exclude those exact paths from source discovery, snapshot identity, source
searches, and rechecks, including tracked and untracked enumeration inside the
worktree. Common inputs stay readable as named evidence, subject to the peer-read
boundary. They are not part of the reviewed source set.

Keep source access read-only and permit report writes only to those exact paths.
Use runtime write restrictions when supported. With cooperative read or write
limits, report that rather than claiming filesystem isolation. For writes, also check
the source and other assessments' artifacts before accepting completion.

Keep same-round peer outputs outside the common input directory, and exclude them
and their archives from source and evidence searches. State Review's peer-read
boundary in every brief.

An assessment that received same-round peer content cannot count as independent.
Apply the failure policy below to it. Other valid assessments remain valid.

## Validate and retain completion

Before accepting a result:

1. Match its task, workflow/pass, assignment, criteria, snapshot, and exact output
   paths to the brief or task. Missing files, another task's output, or unexpected
   writes leave a gap.
2. Check the receipt against required inputs and criteria. Its references read must
   include Review. Its ranges must cover every changed hunk in scope: a receipt that
   reads lines 1-50 of a file changed at 200-220 fails. Every file, range, symbol,
   and quote in the report and receipt must match the frozen source, including
   citations supporting a clean verdict. A nonexistent symbol, mismatched quote, or
   wrong source location invalidates that assessment's affected coverage. Reading is
   proved by tool activity, packet evidence, or, when neither is available, source
   text the assessment itself quotes. Credit only the lines that evidence shows.
   Coverage with no such evidence is unproven, which counts as invalid under the
   failure policy. Retain useful findings as unverified claims for settlement.
3. Copy the original report and receipt bytes into a separate caller-owned
   completion archive before dispatching later work that could reuse their paths.
   Record hashes and the assignment/task mapping, make archived files read-only,
   and keep this archive outside later reviewers' writable outputs. Preserve the
   original bytes rather than regenerating a receipt from a later summary.
4. Verify archived hashes before reusing evidence, and recheck source identity.
   If an output is overwritten, use only the verified archived original. If that
   original cannot be recovered, record lost coverage. A reconstructed report does
   not restore an independent assessment.

Apply the caller's failure policy to invalid or missing coverage. Required
assessments need a fresh review. Optional assessments may be skipped under
[Review Fix Loop's policy](../../review-fix-loop/references/review-assignments.md#handle-failures).
