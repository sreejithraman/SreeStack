# Classification

Assign exactly one class to each finding:

- **Must-fix**: a material bug, security or data-integrity failure, required build/test failure, explicit requirement or contract violation, or structural code-quality blocker under the active review bar.
- **Worth-fixing**: high-confidence maintainability work that materially simplifies the current change without changing intended behavior.
- **Defer**: valid concern that may be worth doing, but belongs to a separate change, issue, or parent decision.
- **Acknowledge**: valid context recorded for awareness.
- **Won't do**: rejected finding: weak, speculative, duplicate, line-impossible, contradicted by code, already handled, or more churn than clarity.

Only `Must-fix` and `Worth-fixing` are accepted findings.

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

`Defer` must include the parent decision needed.
