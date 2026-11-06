# Wide refactors

A wide refactor is one mechanical change, such as renaming a column or retyping a shared symbol,
that breaks call sites across the codebase at once. No single path through the layers can land
green, so sequence it as expand and contract:

1. **Expand:** add the new form beside the old, so nothing breaks. For stored data, write both
   forms and backfill here, so the batches can read the new one.
2. **Migrate:** move call sites in batches sized by what each one touches, such as one package or
   directory. Each batch is its own task, blocked by the expand. CI stays green from batch to batch
   because the old form still exists.
3. **Contract:** stop using the old form, then delete it once no caller or running version uses
   it, in a separate deploy when versions overlap. This task is blocked by every batch.

When even the batches can't stay green alone, keep the sequence and let them share an integration
branch. Every batch then blocks a final task that integrates and verifies, and green is promised
only there.
