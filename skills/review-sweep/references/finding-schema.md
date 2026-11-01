# Finding Schema

Keep one record per underlying issue, with its source reports attached:

```text
workflow_id:
source:
id:
first_seen_pass:
reports:
location:
claim:
evidence:
triage:
reason:
recommended_action:
parent_decision_needed:
repair:
check:
```

`source`, `id`, `location`, and `claim` must be filled before verification. `source` may name a local reviewer, a GitHub review item, or a CI check.

Use `id` as the stable issue ID within the workflow. Assign a short local ID
when needed; retain original source IDs in `reports`. Reuse the issue ID in later
passes. Preserve the earliest observed `first_seen_pass`; use unknown when its
history is unavailable rather than guessing from task names or dates.

Each report retains its source/ID, assignment, pass, snapshot, and evidence.
Mark its relationship as first report, corroboration, repeat, or prior input.
Prior input identifies an issue supplied before assessment, not a new discovery.
For standalone input without a review loop, use a local batch identity and keep
unavailable pass/assignment metadata unknown.

Fill `evidence`, `triage`, `reason`, `recommended_action`, and `parent_decision_needed` after verification and classification.

Merge equivalent claims about the same cause, preserving evidence and any
disagreements. Shared locations or similar symptoms alone do not establish a
duplicate. Every valid corroborating report links to the issue's disposition;
source wrappers can still reply to each original source ID.

For accepted issues, record `repair` as pending, applied, or unknown. Applied
requires the repaired snapshot and evidence of the change. Record `check` as
not run, passed, failed, unavailable, stale, or unknown, with its snapshot,
method, evidence, what it establishes, and limits. A reproduction supports the
claim; checking the repaired behavior supports the repair. A current-outcome
check without an established repair is not a verified fix. Later changes that
invalidate the proof make it stale; retain the old evidence and rerun affected
checks. Use the existing finding report rather than a second status ledger.

Record raw input without a technical claim as source noise. The source wrapper keeps operational states such as missing checks, service failures, and waiting for human approval.
