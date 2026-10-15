# Preventing recurring mistakes

Assess the design from the view of a contributor who opens a few files and
copies the nearest working example. Prefer a supported path whose correctness
does not depend on discovering hidden ownership rules.

## Check the shape

- **State ownership:** each mutable fact has one authoritative owner. Other
  modules read it or request a change through that owner's interface. Separate
  derived views from competing writable copies; make cache invalidation explicit.
- **Supported path:** give each domain operation one canonical route. When
  replacing a route, migrate its actual callers and remove obsolete examples
  and implementations within the authorized scope. Preserve distinct adapters
  and externally required compatibility paths when they serve real consumers.
- **Private implementation:** make internals inaccessible to outside callers
  through language visibility, package exports, or an enforced import rule.
  A documented interface is insufficient if the convenient import bypasses it.
- **Authoritative definitions:** derive repeated registries and shapes from one
  owned definition. Where derivation is impractical, check parity so adding an
  entry in only one place produces an actionable failure.

Apply these checks to concrete ownership or maintenance friction. Preserve
legitimate variation and weigh migration cost against the observed benefit.

## Choose enforcement and proof

For design or review, return a recommendation and its required proof; leave
implementation to its owner. Use [correct](../../correct/SKILL.md) when the
requested task is to mine recurring mistakes or prevent a known failure class;
it owns historical evidence, prioritization, and the repair workflow.

Choose the highest effective repair: remove the opportunity through ownership
or interface design, encode the invariant in types, add an actionable lint or
build check, or test the observable behavior. Use instructions for judgment
that those mechanisms cannot encode. Match enforcement to the actual failure
and existing project tooling rather than adding a rule for every preference.

Name an isolated fixture or revision containing a real past mistake, the check
that should reject it, and the repaired path that should pass. For a large
existing violation set, a ratchet may block new violations while preserving an
explicit migration plan.

When implementation is authorized, prove that rejection and repaired-path
success before handoff. Use the same relevant check locally and in CI when CI
enforcement is part of the change.
