---
name: review-sweep
description: Use when findings from local review, PR feedback, or CI need verification, triage, accepted fixes, and clear parent-owned defers.
---

# Review Sweep

Review sweep turns raw technical findings into verified decisions, accepted fixes, and parent-owned defers.

Source wrappers fetch input and handle external side effects such as replies, remote thread resolution, commits, pushes, and issue creation. This skill owns normalization, verification, classification, local fixes, and the return summary.

## Steps

1. Collect every supplied review and normalize raw input using
   [finding schema](references/finding-schema.md). Include native and external reviews, PR
   feedback, CI findings, and findings from incomplete reviews. Preserve each
   source and every source id when merging duplicates. Record coverage gaps
   separately; an incomplete review is not a clean result.

   Merge duplicate claims and record input without a technical claim as source
   noise. Finish when every item is a finding, duplicate, source noise, or
   separately recorded coverage gap.

2. Verify each finding.

   Check findings against actual code and project context before trusting them. Treat review wording as input, not truth.

   For each finding, inspect the referenced code, nearby ownership boundary, changed behavior, tests or build impact, public contracts, security or data-loss risk, and local conventions. Use `verify` when exercising a UI, CLI, or service workflow would resolve a disputed claim. Decide whether the claim is true, duplicate, pre-existing, already handled, contradicted by code, or more churn than clarity. Finish this step when every finding has evidence and a verified claim state.

3. Classify each finding using [classification](references/classification.md).

   Assign exactly one class. Only `Must-fix` and `Worth-fixing` are accepted findings. Finish this step when every verified finding has one class and a reason.

4. Fix accepted findings.

   Preserve intended behavior and public contracts within the task's authorized
   scope; ask when a remedy requires an unauthorized behavior change. Run focused
   checks after meaningful fixes, using `verify` when real-workflow evidence adds
   confidence. Recheck any affected React Doctor diagnostics for React or Next
   fixes. Keep evidence only while it applies to the resulting change. This checks
   findings and fixes; the implementation owner supplies initial acceptance
   evidence. Missing proof identified by review is itself a finding to resolve.
   Finish when accepted findings are fixed and their checks pass, or report
   explicit blockers. Rejected or deferred findings need new evidence to reopen.

5. Return grouped results using [return format](references/return-format.md).

   Include changed files, verification results, coverage gaps, blockers, and every
   parent-owned defer, including when the findings list is empty.
