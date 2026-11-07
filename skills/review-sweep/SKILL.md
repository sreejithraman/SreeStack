---
name: review-sweep
description: Use when review findings, PR comments, or failing checks need verifying, deciding, and fixing.
---

# Review Sweep

Settle every finding, whatever its source. Start from a set of findings: local review reports,
PR feedback, or CI failures. Leave each one verified, decided, and either fixed or handed to its
owner.
You are done when every input has a disposition and each accepted fix passes its checks, or
you have named the precise blocker.

When findings live on GitHub, collect and answer them through
[PR feedback](references/pr-feedback.md). The caller owns commits, publication, and later review
rounds.

1. **Account for input.** Normalize every item with the
   [finding schema](references/finding-schema.md). Preserve workflow, pass, model, and
   assignment provenance. Keep one stable issue ID per underlying cause, and keep each report's
   source ID and relationship to that issue. Separate source noise and coverage gaps.
2. **Verify each claim.** Inspect the actual location, owner, consumers, contracts,
   requirements, and checks. Use [Verify](../verify/SKILL.md) when a real workflow settles a
   dispute. Done: every claim has evidence and a state: true, pre-existing, handled,
   contradicted, duplicate, or unjustified churn.
3. **Decide.** Apply [classification](references/classification.md) once per issue, then its
   [continue or stop](references/classification.md#continue-or-stop) test. Only Must-fix and
   Worth-fixing are accepted. Record reasons for rejecting, acknowledging, or deferring.
4. **Repair and check.** Follow [Orchestration](../orchestration/SKILL.md#who-does-the-work) for who
   repairs, and pick the model of any repair you delegate from
   [the model table](../orchestration/references/models.md#choose-a-model).
   Keep intended behavior inside the authorized scope. A changed product decision is a stop.
   Run the checks accepted fixes affect, including React Doctor diagnostics where they apply.
   Reuse proof while it's valid. Record each issue's repair state and snapshot separately from
   its check result, snapshot, and what that proves. Missing acceptance proof is itself a
   finding.

Reopen a settled finding only with new evidence. Return the
[grouped report](references/return-format.md): findings, fixes, checks, reasons, coverage gaps,
stops, and remaining owners.
