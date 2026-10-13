---
name: review-sweep
description: Validate supplied review or CI findings and implement accepted fixes. Use when local reviews, PR feedback, or checks need triage, repair, and explicit dispositions.
---

# Review Sweep

Turn supplied findings into verified decisions and fixes. The caller owns input
fetching, commits, publication, remote replies/resolution, and later review rounds.

1. **Account for input.** Normalize every item with the
   [finding schema](references/finding-schema.md). Preserve each source and ID,
   including model/assignment provenance. Merge duplicates without losing their
   sources; separate source noise and incomplete-review coverage gaps.
2. **Verify each claim.** Inspect the actual location, owner, consumers, contracts,
   requirements, and relevant checks. Use [verify](../verify/SKILL.md) when a real
   workflow resolves a dispute. Finish when every claim has evidence and a state:
   true, pre-existing, handled, contradicted, duplicate, or unjustified churn.
3. **Decide.** Apply [classification](references/classification.md) once per item.
   Only Must-fix and Worth-fixing are accepted. Record reasons for rejection,
   acknowledgment, or deferral, including the parent decision a deferral needs.
4. **Repair and check.** Use the working selection from
   [agent routing](../orchestration/references/agent-routing.md#model-defaults).
   Preserve intended behavior within the authorized scope; a changed product
   decision belongs to the parent. Run checks affected by accepted fixes,
   including relevant React Doctor diagnostics. Reuse proof while it remains
   valid. Missing implementation acceptance proof is itself a finding to resolve.

Finish when every input has a disposition and each accepted fix passes its
checks, or report the precise blocker. Reopen settled findings only with new
evidence. Return the [grouped report](references/return-format.md): findings,
fixes, checks, rejected/deferred reasons, coverage gaps, and remaining owners.
