# Review evidence

Use this when assigning delegated reviews. Reviewers follow
[Delegated reviews](../SKILL.md#delegated-reviews) for their read/write limits and
coverage block.

## Assign outputs

Give the review loop a stable `workflow_id` and integer `pass`, starting at 1.
Each pass binds one frozen snapshot (`base`, `HEAD`, and any included uncommitted or
untracked source). Use the next pass after changes; a retry on the same snapshot
keeps the pass and gets a new report path.

Give each assessment a unique assignment key and report path, and record
workflow/pass, criteria, configured provider, model and options, snapshot identity,
required references, and exact report path in the brief or task. Bind the returned
task ID to its assignment.

## Set boundaries

Designate generated review input and output paths before collecting source, and
exclude them from source discovery, snapshot checks, and searches. Common inputs
stay readable as named evidence; keep same-round peer outputs separate and state
Review's peer-read boundary in every brief.

Keep source access read-only and permit writes only to the assigned report path.
Use runtime write restrictions when supported; otherwise check that source and
other assessments' files stay untouched before accepting completion.

An assessment that received same-round peer content is not independent. Apply the
caller's failure policy to it; other valid assessments stay valid.

## Validate completion

Before accepting a result:

1. **Snapshot match:** confirm the reviewed snapshot did not move during the review,
   and that the output matches the brief's workflow/pass, assignment, criteria, and
   report path.
2. **Evidence & coverage:** confirm the coverage block includes Review and every
   assigned reference, reports no unaddressed unread hunks or unmet criteria, and
   that cited files, lines, symbols, and quotes match the frozen snapshot. For a
   clean verdict with zero findings, corroborate coverage against the delivered
   diff packet or reviewer tool reads (recording a coverage gap when the host
   hides tool activity). A fabricated location, mismatched quote, or unread
   changed hunk invalidates the affected coverage (retain any useful observations
   as unverified claims).
3. **Preserve prior reports:** keep earlier-pass reports intact at their unique pass
   paths before starting later passes or repairs so prior evidence is never
   overwritten.

Apply the caller's failure policy to invalid or missing coverage.
