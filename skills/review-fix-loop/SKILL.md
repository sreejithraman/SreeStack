---
name: review-fix-loop
description: Use when a local diff needs repeated review, accepted-finding fixes, and verification before handoff or push, or when another skill requests a current local quality check.
---

# Review Fix Loop

Review fix loop runs review sources over one local diff, sweeps their findings through `/review-sweep`, verifies the result, and repeats until stable or blocked. It leaves commits, pushes, PR work, and merges to its caller.

## Steps

1. Scope the loop.

   Inspect git status, resolve the supplied review base, and identify the reviewed diff, intended behavior, affected modules, available spec or issue source, standards sources, and verification commands.

   Finish this step only when the supplied fixed point resolves and the complete diff scope is known.

2. Run review sources.

   Run `/ponytail-review` in diff mode against the complete loop diff.

   Run a strict maintainability review against the Greenfield Standard below. When the user separately invokes `/thermo-nuclear-code-quality-review`, include its returned findings in this loop.

   Run `/code-review` when a fixed point is available, so Standards and Spec are reviewed as separate axes.

   Run `/gemini-review` when the external-review path is available: at least on the first pass, and again after material edits.

   Finish this step only when every applicable review source has returned findings or an explicit blocker.

3. Sweep findings.

   Combine review findings and run `/review-sweep`. Treat external reviews as advisory until verified against code and project context.

   `/review-sweep` owns classification, accepted-finding fixes, and parent-owned defers. Finish this step only when every finding has one disposition.

4. Verify.

   Run the commands from step 1 plus focused checks made necessary by fixes.

   Run `/manual-verify` when the diff has a browser, user-facing, CLI, API, file, or workflow surface that can be exercised.

   If verification fails because of loop changes, repair the regression and rerun verification. Finish this step when every planned check passes or has an evidenced blocker unrelated to the diff.

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
