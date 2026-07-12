---
name: review-fix-loop
metadata:
  owner: sree
description: Review/fix loop. Use when a diff needs local review, external review, accepted-finding fixes, and verification before handoff or PR readiness.
disable-model-invocation: true
---

# Review Fix Loop

Review fix loop runs review sources over the current diff, sweeps their findings through `/review-sweep`, verifies the result, and repeats until stable or blocked.

## Steps

1. Scope the loop.

   Inspect git status, resolve the review base, identify the reviewed diff, intended behavior, affected modules, available spec or issue source, standards sources, and verification commands.

2. Run review sources.

   Run `/thermo-nuclear-code-quality-review` for strict maintainability review.

   Run `/code-review` when a fixed point is available, so Standards and Spec are reviewed as separate axes.

   Run `/gemini-review` when the external-review path is available: at least on the first pass, and again after material edits.

3. Sweep findings.

   Combine review findings and run `/review-sweep`. Treat external reviews as advisory until verified against code and project context.

   `/review-sweep` owns classification, accepted-finding fixes, and parent-owned defers.

4. Verify.

   Run the commands from step 1 plus focused checks made necessary by fixes.

   Run `/manual-verify` when the diff has a browser, user-facing, CLI, API, file, or workflow surface that can be exercised.

   If verification fails because of loop changes, repair the regression and rerun verification.

5. Repeat.

   Repeat review sources, sweep, and verification after material edits. Stop when the latest relevant review pass has no unblocked accepted findings and verification is green, or when remaining blockers are explicit.

## Greenfield Standard

Behavior changes require user approval; otherwise preserve intended behavior and public contracts. Within that boundary, treat the current implementation as a draft: put the seam in the right place, keep the interface small, hide complexity inside a deep module, follow local idioms, delete obsolete scaffolding, and prefer fewer concepts over patched complexity.

## Report

End with:

- review base and diff scope
- review sources run
- accepted findings fixed by `/review-sweep`
- deferred or blocked findings
- verification commands and results
- manual verification result or blocker
- residual risk
