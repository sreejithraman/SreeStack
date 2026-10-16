# Model the Domain

Represent domain rules in data where that removes duplicated decisions or
invalid combinations: a state machine for lifecycle transitions, a sum type
for exclusive cases, a registry for dispatch, or an index for repeated lookup.
Group behavior by the knowledge and invariants it owns, not execution phases.
Derive repeated definitions from one authority. Keep a clear existing shape
when another abstraction would add coordination without removing it.
When derivation is impractical, check parity so a partial update fails visibly.

## Stateful behavior

Use explicit states and transitions when behavior depends on event order,
several flags can contradict each other, or cancellation and retries make
async work hard to follow. Keep simple local state when it expresses the
behavior clearly.

- Name the finite states, accepted events, allowed transitions, and conditions
  (guards) that enable them. Evaluate guards synchronously from current data.
  Decide what happens to an event in each relevant state, including events that
  should be ignored or rejected. A reducer enforces these rules only when its
  decisions account for both the current state and event.
- Distinguish behavior modes from payload data. Use sum types with associated
  data where they rule out invalid combinations. Derive display flags from
  that authority rather than synchronizing independent copies.
- Keep transition decisions pure and effects explicit. Start effects only for
  accepted events or state entry, with an owner for cleanup and completion.
  On cancellation or replacement, cancel supported work and prevent stale
  completions from changing the current operation. Correlate results with the
  active attempt or use work scoped to the owning state's lifetime. Discarding
  a result does not undo an external effect.
- Enforce allowed actions in the model. UI controls reflect those rules so
  other entry points cannot bypass them.
- Check meaningful event sequences and forbidden transitions against product
  requirements through [behavior tests](test-behavior-not-implementation.md).
  A model's own transition table is not independent proof of those requirements.

A pure reducer or transition table can express a small machine. Use an
established statechart implementation when nested states, parallel behavior,
history, or effect lifecycles justify it; preserve a suitable existing library.

For example, a submission can follow these rules:

```text
editing + SUBMIT [valid draft]       -> saving (new attempt)
saving  + SUBMIT                     -> unchanged; no second save
saving  + RESOLVED [current attempt]  -> success (receipt)
saving  + REJECTED [current attempt]  -> failure (draft, error)
failure + RETRY                      -> saving (new attempt)
saving  + CANCEL                     -> editing
any     + completion [stale attempt] -> unchanged
```

Here, brackets name guards and parentheses name associated data. Unlisted
events leave the state unchanged and start no effects. Start a save
on entry to `saving`; derive `isSaving` from that state. Cancellation ends the
attempt's ownership before requesting cleanup, so even a completion that races
with cleanup cannot replace the current result. The UI sends events and renders
the resulting state; it does not maintain a separate permission flag.

Use [domain-modeling](../../domain-modeling/SKILL.md) for vocabulary and ADRs;
use [codebase-design](../../codebase-design/SKILL.md) for deep modules and seams.
