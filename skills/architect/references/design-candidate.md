# Design candidate brief

The coordinator passes this file to every candidate runner during Phase B and
fills in the task, criteria, Phase A grounding artifacts, isolated working
directory, and output path. What matters is independence between candidates.

You are producing one candidate design in architect's parallel exploration.
Read [architect](../SKILL.md) for context; your assignment ends with this
candidate, not the coordinator's synthesis or implementation. Output a type
sketch, function signatures, module map, and prose rationale shaped per the
[design rationale](design-rationale.md). Leave the synthesis decision to the
coordinator. Use [Codebase Design](../../codebase-design/SKILL.md)'s vocabulary.

Apply the following discipline. The coordinator compares candidates on these
axes to pick a base.

- Caller's usage first. Write the README-style usage and two or three real call
  sites before the types, then derive the type sketch from them. The usage is
  the spec. The two must agree, so reconcile the sketch to the usage, not the
  reverse.
- Data structures first. Get the core types right and the code becomes obvious.
  Trace each dominant access pattern through the proposed structure. If the
  answer is "we'll add a map / index / cache later," revisit the structure.
- Interface depth. Compare the capability hidden behind the public surface
  relative to the size of that surface. Prefer a simple interface that pulls
  complexity into the callee, even when the implementation becomes less simple.
  Do not put transport or wire types on the public interface. Parse into domain
  types behind the interface.
- Shared state: if two actors might both write, ask "what happens?" Default to
  per-actor state with a merge at the read boundary when the invariant permits
  it, per [Separate Before Serializing Shared State](../../engineering-principles/references/separate-before-serializing-shared-state.md).
- Make ownership and interfaces visible. `not implemented` errors for bodies,
  pseudocode for tricky logic, and intent and invariants alongside the sketch.
  A reader should trace data from input to output by reading types and
  signatures alone.
- Encode invariants in types: hard-to-misuse types > runtime checks > prose
  comments, per [Encode Lessons in Structure](../../engineering-principles/references/encode-lessons-in-structure.md).
- Validate at boundaries, trust types inside, per
  [Boundary Discipline](../../engineering-principles/references/boundary-discipline.md).
  Business logic as pure functions. The shell stays thin.
- Single source of truth per invariant. Derive instead of sync.
- Idempotent state transitions where applicable, per
  [Make Operations Idempotent](../../engineering-principles/references/make-operations-idempotent.md).
  Ask what happens if the operation runs twice or crashes halfway.
- Short call chains. If tracing the flow requires bouncing across files, look
  for pass-through layers to flatten, per
  [Laziness Protocol](../../engineering-principles/references/laziness-protocol.md)
  and [Minimize Reader Load](../../engineering-principles/references/minimize-reader-load.md).

Produce the best design your assignment can make. Don't hedge against the
others. Differences between candidates are the signal used to pick a base and
graft. Choosing a safe-looking middle to anticipate the others defeats the
exploration. Independent agreement is useful evidence; record it rather than
forcing disagreement.
