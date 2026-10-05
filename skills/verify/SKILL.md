---
name: verify
description: Use for real-workflow acceptance checks or interface audits across web, native, CLI, and service products, or to set up or maintain project verification documentation.
---

# Verify

Exercise real user workflows through the product's public entry points.
The observed outcome establishes the verdict.

## Scope and project knowledge

Read the request, current session, relevant diff, and project instructions.
When a verification map exists, read its index and shared setup first. Select
affected features and related regressions from the request, changes, and index,
then load those recipes. Expand to linked recipes when their behavior is relevant;
read every recipe for whole-app verification or whole-map maintenance. If the
index is missing, list recipe files recursively to locate relevant entries.

If the request leaves documentation unchanged, use a temporary plan and report
discovered drift. Otherwise maintain the affected scope of an existing map,
including incomplete maps or missing indexes: correct stale steps, add missing
recipes, and reorganize while preserving useful assertions and gotchas. Create
a new map only for a setup or reusable-documentation request. Without an existing
map or setup request, use a temporary plan without documentation writes. For
setup or maintenance, read [project maps](references/project-map.md).

Choose coverage independently of whether a map exists:

- **Verify this change (default):** account for changed behavior and related
  regressions in the session and diff, then exercise the selected workflows.
- **Whole-app verification:** inventory current user-facing capabilities and
  exercise their required workflows. With a map, include every mapped feature
  and important unmapped surfaces. Without a map, build that inventory temporarily.
  Disclose coverage gaps in either case.
- **Set up or refresh documentation:** discover and document the requested scope,
  then prove new or changed recipes live. A whole-map maintenance request audits
  every mapped feature against source and live behavior, including index links,
  recursive recipe inventory, and recent user-facing surfaces.

A map is working knowledge, not proof of whole-product completeness. Plain
project docs are the main reusable input. Existing project verification skills
may supply useful launch or control facts only when their invocation policy
permits using them; do not indirectly invoke an explicit-only skill. Match facts
to the intended app, revision, and environment. Keep this skill's procedure as
the owner of this run; do not automatically delete, rewrite, or migrate existing
project skills.
A project verification skill alone does not establish a documentation map.

## Workflow

1. **Account for coverage before driving.** Map every behavior-changing part of
   the current diff and session to affected feature and workflow identifiers,
   required assertions, and related regressions, including shared dependencies.
   Identify missing recipes and explain material exclusions.
   Finish selection only when each changed behavior has a check or an explicit
   reason for exclusion. State expected results before observing outcomes.

   For acceptance work, select realistic workflows covering the main path and
   materially relevant error or edge cases, persistence, and distinct entry
   points. Use the mapped required assertions rather than sampling a workflow's
   obligations away. For docs-only requests, select the recipes being maintained
   without inventing a product diff.

   For component stress tests, worst-case data, or content-dependent failures,
   read [realistic edge data](references/edge-data.md) to select fixtures and
   required assertions.

   For a whole-surface visual, interaction-quality, or accessibility audit, read
   [interface review](references/interface-review.md) for specialist selection,
   exhaustive coverage, and audit reporting. Also read it when acceptance checks
   involve accessibility or platform material changes; apply its relevant checks
   to the selected workflows.

2. **Prepare the recipes and interface.** Prepare temporary or maintained recipes
   according to the documentation policy above.

   Read the relevant platform reference: [web](references/web.md),
   [iOS](references/ios.md), [macOS](references/macos.md), or
   [terminal and services](references/terminal-and-service.md). Use the same
   workflow with the best available tooling for other interactive products.

   Discover actual launch commands, readiness signals, prerequisites, fixtures,
   and isolation options from the repository and environment. Reuse available
   browser, device, CLI, HTTP, or PTY tooling; custom helpers are optional. A CLI
   can drive a UI. Choose by the public interaction and observable evidence it
   exposes, honoring host browser and device routing first. Internal setters and
   test-only endpoints may prepare state or support diagnosis; they cannot prove
   a public interaction works. Verify what dry-run or test modes actually change.

3. **Launch and establish known state.** Start or connect to the intended build
   and check instance identity, revision, readiness, access, and required
   connections before driving. Bound waits by observable conditions and deadlines.
   Preserve failing launch commands or health observations and their causes;
   distinguish product failures from missing environment prerequisites. Recipes
   that cannot be exercised remain draft with the specific blocker.
   Reuse launched instances for related checks; serialize drives that share
   mutable state.

   Identify external effects and consequential actions. Prefer disposable
   accounts, fixtures, isolated ports, data profiles, and provider test modes.
   Complete irreversible or externally visible actions only within the task's
   authorization; otherwise stop at the last safe step and mark the remaining
   assertions blocked. Record credential names and secure setup paths, never
   values. Redact secrets and private data before retaining evidence.

4. **Observe, act, observe.** Wait for the known starting state to settle. Inspect
   rendered appearance and semantic representation when available. Perform one
   meaningful interaction, then inspect its result before continuing. Prefer
   roles, labels, and identifiers; use coordinates only when stable targets are
   unavailable, derived from current state.

   If an action produces no expected change, record that outcome before retrying.
   Retry once only when observable evidence shows that the target moved or the
   interface had not settled; record the retry as a separate attempt. A repeated
   failure is evidence. After a stuck interface or surprising result, check
   instance health and restore known state or relaunch safely even when the
   process still looks healthy.

   For intermittent reports, choose a bounded attempt count before testing.
   Restore equivalent known state with disposable or uniquely identified data
   before every planned attempt. Record every outcome; recovery retries are
   separate from the planned count.

5. **Judge each assertion.** Compare expected and observed results. Check function
   and relevant usability: layout, readability, focus, input, navigation,
   loading, empty, disabled, and error states.

   For persisted data or output artifacts, use a fresh read path independent of
   the current screen and record the durable value or artifact inspected.

   Classify mismatches as documentation drift, a harness gap, or a product
   regression. Correct inaccurate driving steps and in-scope harness instructions,
   then re-drive affected steps. Save documentation corrections only when this
   run maintains or sets up a map. Change product behavior only when the active task
   includes fixing it. Preserve intended assertions; never weaken expectations
   to accept a defect. A recipe that detects a product failure can be valid
   documentation while its product assertion remains failed. Label unproved
   recipes draft, with blocked or untested steps and their reasons.

6. **Retain proof, clean up, and report.** Store run evidence outside the committed
   map and disposable state. Include failed attempts, relevant screenshots,
   semantic snapshots, logs, transcripts, or responses. Use visual captures for
   visual claims. Stop only run-owned processes or sessions and remove their
   disposable data after successful and failed attempts; preserve reused services
   and source fixtures. Inspect retained evidence after cleanup to confirm it
   survives and remains readable.

   For every workflow and entry point, give identifiers, actions, expected and
   observed results, and evidence locations. Assign every required assertion:

   - `passed`: observed result matched the assertion;
   - `failed`: observed result differed;
   - `blocked`: a missing prerequisite prevented the check;
   - `untested`: the selected check was not exercised.

   A workflow passes only when every required assertion passes. Otherwise its
   overall status follows `failed`, then `blocked`, then `untested`. Report defect
   reproduction separately as `reproduced` or `not reproduced in N attempts`.
   A reproduced defect makes the affected assertion and workflow failed;
   non-reproduction does not establish a fix.

   Report documentation changes and live recipe proof separately from product
   verdicts. Name material exclusions, unmapped surfaces, draft recipes, blockers,
   and untested coverage.

If a step requires the user, give exact actions and location, then resume after
they finish; continue independent checks meanwhile. After UI work, use `showroom`
to package useful visual checkpoints while Verify keeps selection and judgments.
