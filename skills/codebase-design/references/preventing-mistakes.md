# Preventing recurring mistakes

Assess the design from the view of a contributor who opens a few files and
copies the nearest working example. Prefer a supported path whose correctness
does not depend on discovering hidden ownership rules.

## Assess the supported path

When ownership, private implementation, or repeated definitions make a mistake
easy to copy, read the shared
[Data and interface decisions](../../engineering-principles/references/design.md).
When replacing an operation's supported route, read **Migrate Callers Then Delete
Legacy APIs** in
[State, retries, and migration](../../engineering-principles/references/state-and-migrations.md).

Trace the nearest working example through the interface a contributor would
actually use. Identify the concrete mistake it permits, the bypass that remains
available, and the callers exposed to it. Base a recommendation on that path and
observed maintenance friction, rather than a preferred module layout.
For an interface-bypass finding, cite the accessible symbol and the visibility,
export, or import rule that permits the bypass.

## Choose enforcement and proof

For design or review, return a recommendation and its required proof; leave
implementation to its owner. Use [correct](../../correct/SKILL.md) when the
requested task is to mine recurring mistakes or prevent a known failure class;
it owns historical evidence, prioritization, and the repair workflow.

When selecting a guard, read **Encode Lessons in Structure** in
[Executing substantial work](../../engineering-principles/references/execution.md).

## Prove the historical guard

Name an isolated fixture or revision containing a real past mistake, the check
that should reject it, and the repaired path that should pass. Record the
historical violation and expected failure signal so a check failing for an
unrelated reason cannot count as proof. Include legitimate adapters or required
compatibility paths in the passing cases when the guard could reject them.

For a large existing violation set, a ratchet may block new violations while
preserving an explicit migration plan. State which violations remain and how
the guard distinguishes existing debt from a newly introduced mistake.

When implementation is authorized, prove that rejection and repaired-path
success before handoff. Use the same relevant check locally and in CI when CI
enforcement is part of the change.
