# Finding Schema

Map each raw technical item into this shape:

```text
source:
id:
location:
claim:
evidence:
triage:
reason:
recommended_action:
parent_decision_needed:
```

`source`, `id`, `location`, and `claim` must be filled before verification. `source` may name a local reviewer, a GitHub review item, or a CI check.

If the source lacks a stable id, assign a short local id.

Fill `evidence`, `triage`, `reason`, `recommended_action`, and `parent_decision_needed` after verification and classification.

Merge duplicates that point to the same underlying issue. Keep every source id on the merged finding so source wrappers can still reply to each source.

Record raw input without a technical claim as source noise. The source wrapper keeps operational states such as missing checks, service failures, and waiting for human approval.
