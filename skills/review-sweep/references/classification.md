# Classification

## Scope boundary

**Scope only shrinks during triage.** Fix defects and real-use edge cases in the
requested change in place (including bugs in earlier repairs); edge cases
impossible in real use need no fix. Findings outside the requested change — new
guarantees or pre-existing base code — are out of scope and defer even when
labeled security or correctness, **unless** this change exposes or worsens a
security hole, data-loss risk, or breakage in base code (fix that in place).

## Classes

Classify each canonical issue once after merging equivalent source reports:

- **Must-fix**: a material bug, security or data-integrity failure, required
  build/test failure, explicit requirement or contract violation, or structural
  code-quality blocker under the active review bar, inside scope.
- **Worth-fixing**: high-confidence maintainability work inside scope that
  materially simplifies the current change without changing intended behavior.
- **Defer**: a valid concern below the active review bar, or outside the scope
  boundary above, however severe.
- **Acknowledge**: valid context recorded for awareness.
- **Won't do**: rejected finding: weak, speculative, line-impossible, contradicted
  by code, or more churn than clarity.

Only `Must-fix` and `Worth-fixing` are accepted findings.

Duplicate is a report relationship, not a rejection reason. Valid corroborating
reports retain the canonical issue's disposition. If the issue is already settled,
link the repeat to that decision and its repair/check evidence without creating
another issue or edit. Reopen it only when new evidence warrants it. Reject a
contradicted claim on its evidence rather than merging it merely because it
mentions the same location.

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

### Handling `Defer`

Record every `Defer` with its origin, evidence, reason, and impact:

- **`unrelated`**: below-bar or pre-existing debt with no effect on this change or
  sibling work.
- **`shared-contract`**: out of this change's scope, but affects a shared contract,
  base module, or sibling work the caller may need to know about immediately.
- **`requested-scope`**: would split part of what was originally requested out of
  this change (as opposed to rejecting reviewer scope creep).

When called by a parent workflow, return `Deferred` items in the grouped report so
the caller routes them (flagging `shared-contract` and `requested-scope` items
prominently). When running standalone directly for the user, give each `Defer` a
real durable home now — a tracker issue or Snip Snap ID, never an unbacked prose
promise — and report it.

For example, two reports of the same reachable data-loss bug produce one
`Must-fix` issue and one repair, with both reports retained. A repeat after a
verified repair links to that history; a fresh reproduction of the failure reopens
the issue. A proposed cut with no demonstrated behavioral or maintenance benefit
does not become `Worth-fixing` just because it removes lines.

## Continue or stop

Sort every issue by its outcome, not its source. Local reviewers, CI, bots, and
people all use one test, before and after a PR opens: is this still what was asked
for or kept, and is the fix settled and reversible?

| Continue | Stop for the caller |
| --- | --- |
| Nothing real needs changing: an invalid finding dismissed with a reason, or a flaky run that passes on rerun | It would change, drop, or dispute behavior that was requested, tried, or kept |
| A fix inside the scope boundary above, including one for a security or data-loss bug in the requested change | It needs a product, scope, or design decision, or touches something the caller reserved |
| A clean rebase | It conflicts with another change to the same behavior |
| A simple conflict with an obvious resolution | Applying the fix carries security or data-loss risk, or can't be undone |
| A `Defer` packaged for the caller (or saved to a real durable home when standalone), unless it splits requested scope without caller authorization | It needs an approval or permission you lack |
| | The same repair has failed twice |

When an issue fits both columns, the stop wins. Settle a stop yourself only when it
is a reversible implementation-design choice that keeps requested behavior and
every caller/user gate intact; return every other stop to the caller (or user when
standalone), even if you disagree.

Rerun a proven infrastructure or flaky failure once, and record the result. If it
fails again, it's a stop. A stop keeps its evidence and states the decision needed.
Leave it unfixed and report it under `Stops:` in the grouped report.
