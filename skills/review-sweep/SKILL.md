---
name: review-sweep
metadata:
  owner: sree
description: Review sweep. Use when review findings need verified triage, accepted-finding fixes, and parent-owned defers.
---

# Review Sweep

Review sweep turns raw review findings into verified decisions, accepted fixes, and parent-owned defers.

Source wrappers fetch input and handle external side effects such as replies, remote thread resolution, commits, pushes, and issue creation. This skill owns normalization, verification, classification, local fixes, and the return summary.

## Steps

1. Normalize raw review input using `references/finding-schema.md`.

   Map each raw item into a finding. Merge duplicates that point to the same underlying issue. Record raw input without a technical claim as source noise.

2. Verify each finding.

   Check findings against actual code and project context before trusting them. Treat review wording as input, not truth.

   For each finding, inspect the referenced code, nearby ownership boundary, changed behavior, tests or build impact, public contracts, security or data-loss risk, and local conventions. Decide whether the claim is true, duplicate, pre-existing, already handled, contradicted by code, or more churn than clarity.

3. Classify each finding using `references/classification.md`.

   Assign exactly one class. Only `Must-fix` and `Worth-fixing` are accepted findings.

4. Fix accepted findings.

   Preserve intended behavior and public contracts. Behavior changes require user approval. Run focused verification after meaningful fixes.

5. Return grouped results using `references/return-format.md`.

   Include changed files, verification results, blockers, and every parent-owned defer.
