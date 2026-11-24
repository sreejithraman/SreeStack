# Codex handoff

Codex biases toward action and thoroughness. When a brief states only high-level goals or
invariants, Codex fills unstated gaps with defensive guards, compatibility shims, extra
abstractions, and oversized test matrices—especially during review-fix rounds—or stalls on an
ambiguous finish line.

## Brief

For every Codex brief:

- **Make the finish line and verification commands explicit.** State falsifiable acceptance
  criteria and the exact commands to run so Codex stops once they pass instead of stopping early or
  grinding extra hardening passes.
- **Supply UI references when Codex must touch UI.** Provide visual references, design tokens, or
  exact layout specs rather than leaving visual taste open.

For Codex implementation handoffs, make scope and shape concrete before dispatching:

- **Name the target shape and what to delete or replace.** Point to the exact files, seams, and
  existing patterns to edit. When simplifying or replacing behavior, list the files, types, phases,
  or flags to delete and say explicitly not to keep a fallback or wrapper beside them. State when
  no new files, types, config options, or persisted state should be added.
- **Settle design ambiguity before handing off.** If the minimal approach is unsettled, pick the
  shape yourself—or ask for a short options note before coding—instead of handing an open-ended
  problem to Codex.
- **Draw an explicit edge-case and compatibility fence.** Replace generic slogans ("keep it
  simple", "avoid over-engineering") with named exclusions: state which legacy or pre-release
  formats, multi-user or fleet cases, speculative I/O faults, and adjacent refactors are out of
  scope. Tell Codex to report or defer unexpected edge cases rather than patching around them.
- **Bound the test surface.** Name the specific behaviors or regressions to test—and obsolete tests
  to remove alongside deleted code—so Codex writes focused seam tests instead of exhaustive
  permutation suites for internal helpers.
- **Cap review-fix expansion.** State that if a fix or review finding requires new files, new
  persisted state, compatibility paths, or materially expands the diff beyond the target shape,
  Codex must stop and return the tradeoff to the caller instead of layering defensive guards.

| Loose brief | Bounded Codex brief |
| --- | --- |
| Preserve user data on setup retry without breaking conflict handling; keep it simple. | Fix retry merge in `SetupMergePlanner.swift` to skip locally deleted IDs. Do not add new files, persisted state, or pre-release manifest fallbacks. Add two regression tests (local delete vs. remote edit) and run `swift test --filter SetupMergeTests`. Stop and report if a fix or review finding needs new state or files. |
| Remove the retired legacy sync path while keeping local data safe. | Delete `LegacyTextSyncAdapter`, the five `SwiftDataCloudText*` files, and their tests. Keep only `StoredCloudTextRecord` in shipped schemas; do not retain legacy protocol decoders, upgrade shims, or unused error cases. Run `swift test` and confirm no references to `LegacyTextSyncAdapter` remain; stop and report if deletion affects other shipped schemas. |

## Accept

Before accepting a Codex implementation diff, inspect for additive bloat even when CI and Codex's
own review loop are green:

- **Pruning over wrapping:** confirm obsolete code, parameters, error cases, and tests were removed
  rather than wrapped or kept behind compatibility decoders.
- **Diff and test proportionality:** flag new helper files, defensive fallbacks, legacy-build
  recovery paths, or large test matrices that go beyond the brief's target shape and named test
  cases.
- **Return concrete cuts:** reject or return over-built diffs naming the exact files, guards, or
  tests to cut instead of accepting bloat for a later cleanup pass.
