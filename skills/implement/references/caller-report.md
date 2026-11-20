# Caller report and handoff

Read this when your caller is another session, or when pausing, transferring, or being adopted.

## Partial reports

Send a partial report as soon as you hit a missing prerequisite, a human decision, a pending PR, or
a deferred finding with `shared-contract` or `requested-scope` impact. Name what continues
meanwhile and the event that resumes the rest. Partial means partial — never claim completion while
a PR or blocker is pending.

## Owner report fields

Write the full report to the path and structured format your caller supplied, or put it in your
final message if none was given. Write nothing else in a caller's records. Include every field that
applies:

- **Outcome and finish line:** picked line, reason, and actual delivery state.
- **Layers:** each PR, branch, or local artifact with link, head, base, and any uncommitted work
  proof covers.
- **Proof:** each required assertion's verdict and evidence, absolute path to kept proof, and what
  is blocked or untested.
- **Shown:** what you showed, how to open it, and any login or running server with its stop action.
- **Waits:** pending PRs, live helpers/watchers, and the events they await.
- **Decisions:** open decision requests with IDs, reversible method choices made, and provisional
  assumptions with what depends on them.
- **Follow-ups:** routed items, deferred review findings (with ID, origin, evidence, impact, and
  suggested destination/finish line), and fixes kept under the scope exception with their reason.
- **Sources:** follow-up messages received and handled.

## Pause, transfer, or adoption

- **Pause or transfer:** record state through [Handoff](../../handoff/SKILL.md).
- **Adoption by a session caller:** keep running; adopt the report path, grant, and return route it
  supplies, and send your current state there without starting a second writer.
- **Replacing a stopped owner:** reconcile files, branches, live writers, helpers, watchers,
  evidence, decisions, holds, any armed landing, and caller route before writing. Never run as a
  second writer beside an active owner.
