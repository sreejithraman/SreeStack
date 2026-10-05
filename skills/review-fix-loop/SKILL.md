---
name: review-fix-loop
description: Coordinate independent reviews and fix accepted findings until a change is reviewed or blocked. Use before handing off behavior changes or when asked to review and fix a branch, PR, or local diff.
---

# Review Fix Loop

Run [review](../review/SKILL.md), external review, and
[review-sweep](../review-sweep/SKILL.md) in rounds. Leave commits, pushes,
PR replies, and merges to the caller.

1. **Prepare.** Establish scope using Review and its
   [brief](../review/references/review-brief.md). Resolve the base once and keep
   it across rounds. Record current head, complete diff, untracked contents,
   requirements, and verification evidence. For external packets, include the
   Review skill and matching reference contents. Pause edits until reviews return.

2. **Review.** For ordinary docs and wording-only instruction edits, the parent
   performs one Review. For changes to agent procedures or configuration, use
   one independent native reviewer. For code or mixed changes, use one for a
   small change to one behavior; use two for substantial changes, multiple
   behaviors, shared contracts, risky logic, or work from several agents.
   Keep at most two unless the user asks for more. Reassess after fixes.

   Follow [agent routing](../orchestration/references/agent-routing.md).
   Start fresh reviewers each round with `fork_turns: "none"`, in parallel when
   using two. Supply the same complete brief and ask each to use Review over the
   full scope. With two, emphasize correctness for one and code quality for the
   other; both cover the whole change. Missing native coverage blocks completion.

   Also request one external review through [gemini](../gemini/SKILL.md).
   If it cannot complete, try [opencode](../opencode/SKILL.md) on GLM Flash 5.3
   once with the same evidence. These skills own execution and result checks.
   Respect permission denials; fallback cannot bypass them. If neither completes,
   retain any findings and report the external review gap; it does not replace
   native coverage or count as a successful external review.

3. **Sweep.** Give Review Sweep all reviews received, including external findings
   and any other supplied reviews. Preserve sources and coverage gaps. Sweep
   owns claim validation, accepted fixes, and their verification. Reuse evidence
   only while it applies to the resulting change.

4. **Repeat or finish.** After code or substantive instruction fixes, refresh
   the complete snapshot and repeat against the original base. If the snapshot
   changed during review, restart that round. Ordinary docs and wording-only
   fixes need targeted checks through Sweep rather than another full round.
   Finish when required native review is complete, the external attempt is
   accounted for, findings are settled, and applicable checks pass. Code and
   substantive instructions require a final round with no fixes. Reopen rejected
   or deferred findings only with new evidence. Report blockers or stalled work;
   incomplete rounds never count as clean.

5. **Report.** Return scope, rounds, reviewer settings, external completion or
   gaps, findings, fixes, deferrals, checks, and blockers. Distinguish requested
   settings from confirmed runtime settings.
