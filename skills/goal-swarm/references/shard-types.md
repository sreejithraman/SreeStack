# Shard Types

Use shard types as planning vocabulary. They are not mandatory labels.

## Implementer

Use for bounded code, test, config, or doc changes.

Owns files or modules. Returns changed files, verification, blockers, and residual risks.

May use `/implement` when the shard is a coding task.

## Explorer

Use for questions, codebase discovery, technical options, or unknown-risk areas.

Owns a question. Returns a direct answer with evidence and recommended next step.

Should not edit files unless explicitly asked.

## Reviewer

Use for correctness, standards, security, maintainability, or spec review.

Owns a review surface. Returns findings first, with file and line references when possible.

Should not fix findings unless the shard explicitly says to.

## Verifier

Use for manual checks, browser QA, CLI/API validation, reproduction, or regression confirmation.

Owns evidence. Returns commands or actions performed, observed results, and unverified areas.

## Synthesizer

Use when multiple artifacts need reconciliation, comparison, or consolidation.

Owns integration analysis. Returns accepted inputs, rejected inputs with reasons, and final recommendation.

## Operator

Use for external-system work such as GitHub, Slack, Gmail, Drive, or issue trackers.

Owns a bounded operation. Returns actions taken, links or identifiers, and any confirmations still required.
