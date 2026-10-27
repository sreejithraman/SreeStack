# Review evidence

Use this contract for delegated reviews. The caller owns acceptance; a reviewer's
coverage claim alone does not prove that the assigned source was read.

## Assign outputs

Give each assessment a unique assignment key and output directory, including
retries and later rounds. Record its criteria, base/head, snapshot identity,
required inputs, and exact report and coverage paths in the brief. Bind the
returned task ID to that assignment. A snapshot identity must cover the diff
and complete untracked inputs, not just HEAD.

Keep source access read-only and permit report writes only to those exact paths.
Use runtime write restrictions when supported. With cooperative write limits,
check the source and other assessments' artifacts before accepting completion;
report that limit rather than claiming filesystem isolation. A task may not
repair another assessment's report or fill its coverage gaps.

## Record reads

Return a coverage receipt alongside the findings. Include the assignment key,
snapshot identity, references read, and a table with one row per reviewed input:

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

1. Match its task, assignment, criteria, snapshot, and exact output paths to the
   brief. Missing files, another task's output, or unexpected writes leave a gap.
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
