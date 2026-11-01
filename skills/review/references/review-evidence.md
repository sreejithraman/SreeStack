# Review evidence

Use this contract for delegated reviews. The caller owns acceptance; a reviewer's
coverage claim alone does not prove that the assigned source was read.

## Assign outputs

Assign the review loop a stable `workflow_id` and integer `pass`, starting at 1.
A pass binds one frozen scope and snapshot. Use the next pass when assigning
assessment of changed inputs; retries on the same inputs keep the pass and
receive a new assignment key.
Keep the workflow ID when fixes, PR preparation, or integration reuse its coverage.
A separate loop gets a new ID and links any reused earlier evidence. Keep task
counters separate; they do not determine the pass number.

Give each assessment a unique assignment key and output directory, including
retries and later rounds. Record workflow/pass, criteria, configured provider,
model and options, base/head, snapshot identity, required inputs, and exact report
and coverage paths in the existing brief. Bind the returned task ID to that
assignment. Retain its outcome and completion time from host records when
available; mark unavailable metadata unknown. A snapshot identity must cover the
diff and complete untracked inputs, not just HEAD.

Designate generated review input, output, and archive paths before collecting
source. Exclude those exact paths from source discovery, snapshot identity,
source searches, and rechecks, including tracked and untracked enumeration when
they are inside the worktree. Keep all other nonignored untracked source in
scope. Common inputs remain readable as named evidence, subject to the peer-read
boundary below; they are not part of the reviewed source set.

Keep source access read-only and permit report writes only to those exact paths.
Use runtime write restrictions when supported. With cooperative write limits,
check the source and other assessments' artifacts before accepting completion;
report that limit rather than claiming filesystem isolation. A task may not
repair another assessment's report or fill its coverage gaps.

Give reviewers exact common input paths and their own output paths. Keep
same-round peer outputs outside the common input directory and exclude those
outputs and their archives from source and evidence searches. State in every brief:
reviewers must not read same-round peer reports, coverage receipts, summaries,
or task conversations, including completion archives. Earlier-round findings,
evidence, and dispositions remain inputs for independent reassessment.

If a reviewer receives same-round peer content, stop that assessment and disclose
the exposure. It cannot count as independent; apply the failure policy below.
Other valid assessments remain valid. These are cooperative read restrictions
unless the runtime enforces them; directory placement is not filesystem isolation.

## Record reads

Return a coverage receipt alongside the findings. Include workflow/pass, the
assignment key, snapshot identity, references read, and a table with one row per
reviewed input:

| Input | Snapshot file/hash | Lines read | Read evidence | Gaps |
| --- | --- | --- | --- | --- |
| Source or required reference | Exact path and content hash | Inclusive ranges, or empty file | Tool call/output or supplied packet location | Unread ranges and reason, or none |

Record actual reads, including nearby context used to support findings. Metadata,
file listings, and truncated command output cover only what was visible. Recover
missing output before claiming its ranges. The caller checks ranges against the
frozen inputs and available tool activity or packet evidence. Full-scope reading
includes every changed hunk and complete new file; it does not require reading
every unchanged line in the repository. List unmet criteria separately from
unread source. A self-authored manifest without supporting read evidence leaves
coverage unproven.

## Validate and retain completion

Before accepting a result:

1. Match its task, workflow/pass, assignment, criteria, snapshot, and exact output
   paths to the brief. Missing files, another task's output, or unexpected writes
   leave a gap.
2. Check the receipt against required inputs and criteria. Verify cited files,
   line ranges, symbols, and quoted snippets against the frozen source, including
   citations supporting a clean verdict. A nonexistent symbol, mismatched quote,
   or wrong source location invalidates that assessment's affected coverage.
   Retain useful findings as unverified claims for settlement.
3. Copy the original report and receipt bytes into a separate caller-owned
   completion archive before dispatching later work that could reuse their paths.
   Record hashes and the assignment/task mapping, make archived files read-only,
   and keep this archive outside later reviewers' writable outputs. Preserve the
   original bytes rather than regenerating a receipt from a later summary.
4. Verify archived hashes before reusing evidence and recheck source identity.
   If an output is overwritten, use only the verified archived original. If that
   original cannot be recovered, record lost coverage; a reconstructed report
   does not restore an independent assessment.

Apply the caller's failure policy to invalid or missing coverage. Required
assessments need a fresh review; optional assessments may be skipped under
[Review Fix Loop's policy](../../review-fix-loop/references/review-assignments.md#handle-failures).
Keep reviewer independence when supplying earlier-round findings.
