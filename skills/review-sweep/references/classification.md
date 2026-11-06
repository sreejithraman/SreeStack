# Classification

Classify each canonical issue once after merging equivalent source reports:

- **Must-fix**: a material bug, security or data-integrity failure, required build/test failure, explicit requirement or contract violation, or structural code-quality blocker under the active review bar.
- **Worth-fixing**: high-confidence maintainability work that materially simplifies the current change without changing intended behavior.
- **Defer**: valid concern that may be worth doing, but belongs to a separate change, issue, or parent decision.
- **Acknowledge**: valid context recorded for awareness.
- **Won't do**: rejected finding: weak, speculative, line-impossible, contradicted by code, or more churn than clarity.

Only `Must-fix` and `Worth-fixing` are accepted findings.

Duplicate is a report relationship, not a rejection reason. Valid corroborating
reports retain the canonical issue's disposition. If the issue is already
settled, link the repeat to that decision and its repair/check evidence without
creating another issue or edit. Reopen it only when new evidence warrants it.
Reject a contradicted claim on its evidence, rather than merging it merely
because it mentions the same location.

Judge bugs by supported triggers, practical exposure, and consequences. Record
that evidence and the impact rationale in the finding's `evidence` and `reason`.
Logical possibility alone does not establish a blocker. Reachable security,
data-loss, recovery, and required contract failures remain actionable even when
infrequent. Defer valid low-impact work that falls below the active review bar;
reject unsupported hypotheticals.

Structural or instruction findings need evidence of a violated contract or a
concrete benefit under the active review bar. A prompt's tone, file-size threshold,
or style preference alone does not establish a blocker.

`Defer`, `Acknowledge`, and `Won't do` need a reason.

`Defer` must name its owner: an issue, a snip, or the parent, with any parent decision
needed. A decision needed before this work can finish is a stop.

For example, two reports of the same reachable data-loss bug produce one
Must-fix issue and one repair, with both reports retained. A repeat after a
verified repair links to that history; a fresh reproduction of the failure
reopens the issue. A proposed cut with no demonstrated behavioral or maintenance
benefit does not become Worth-fixing just because it removes lines. Valid broader
work outside the current change belongs in Defer with an owner decision.

## Continue or stop

Sort every issue by its outcome, not its source. Local reviewers, CI, bots, and people all use
one test, before and after a PR opens: is this still what the user asked for or kept, and is the
fix settled and reversible?

| Continue | Stop for the parent |
| --- | --- |
| Nothing real needs changing: an invalid finding dismissed with a reason, or a flaky run that passes on rerun | It would change or dispute behavior the user asked for, tried, or kept |
| A fix that keeps the same outcome and behavior, including one for a security or data-loss bug | It needs a design decision or changes the outcome |
| A clean rebase | It conflicts with another change to the same behavior |
| A simple conflict with an obvious resolution | Applying the fix carries security or data-loss risk, or can't be undone |
| Valid work that belongs elsewhere, deferred to a named owner | It needs an approval or permission you lack |
| | The same repair has failed twice |

When an issue fits both columns, the stop wins. A dispute over what the user chose is theirs to
settle, even if you disagree with it.

Rerun a proven infrastructure or flaky failure once, and record the result. If it fails again,
it's a stop. A stop keeps its evidence and states the decision needed. Leave it unfixed and report
it in the grouped report.
