# Architecture signals

Use these prompts to investigate structural friction in the assigned scope.
Ground a candidate in actual callers, state transitions, or maintenance history.
Group symptoms with the same cause into one recommendation.

## Investigate the consequence

| Signal | Evidence to seek |
| --- | --- |
| Hidden coupling | A caller must know an ordering rule, configuration choice, or shared-state detail that the interface leaves implicit. Trace where that obligation is established and consumed. |
| Folders grouped by technical layer | One domain change repeatedly spans the same folders because ownership is scattered. Distinguish that friction from legitimate edits to separate adapters or contracts. |
| Repeated logic | Multiple definitions own the same invariant and can drift. Check whether they change for the same reason before proposing shared ownership. |
| Invalid states | A type or constructor permits contradictory combinations that callers must reject or interpret. Show a constructible state and how an actual consumer handles it. |
| Too many responsibilities | A module combines independently changing concepts or forces callers to learn unrelated details. Use responsibilities and caller knowledge to assess cohesion. |
| Scattered edits | A single rule requires coordinated edits across modules. Trace a real change or its required edits, and identify the knowledge that could have one owner. |
| Interface bypasses | Callers access implementation details through an available export, import, or mutable value. Cite the path that bypasses the intended owner. |
| Pass-through wrappers | An extra interface adds caller knowledge without hiding complexity. Trace what callers would need to take over if it were removed, including validation, policy, substitution, and compatibility roles. |
| Misplaced validation or error handling | External values reach consumers before validation, internal callers repeat an established guarantee, or an error loses meaning needed for recovery. Trace the value or failure through its owning interface. |

File length, folder names, similar text, and wrapper counts are clues. A large
implementation can belong to a deep module; a small adapter can preserve a
necessary contract. Recommend a change when it improves ownership, depth, or
locality for the actual use, and explain the tradeoff.

Preserve checks whose guarantees can change through mutation, suspension, or
new input.

Use the table and repository evidence to identify a concrete candidate first.
Read further guidance only when validating that candidate requires it; reuse
relevant guidance already read for this task:

- Ownership or bypass proof: [preventing recurring mistakes](preventing-mistakes.md).
- State design: [Type System Discipline](../../engineering-principles/references/type-system-discipline.md).
- Validation or visibility: [Boundary Discipline](../../engineering-principles/references/boundary-discipline.md).

When the table and code evidence suffice, continue the owning workflow without
opening supporting references.

## Apply the requested scope

Architecture exploration can use these signals to discover candidates within
its selected area and history. Carry worthwhile candidates into its existing
design and experiment workflow.

In review, connect a structural finding to what the supplied change introduces
or worsens. Inspect surrounding owners and callers to establish the consequence;
separate broader existing debt from the fixes needed for this change. Show the
changed location, affected obligation or invariant, concrete consequence, and
smallest remedy that earns its migration cost. Choose severity through the
review workflow's evidence and classification rules. A signal alone does not
establish a blocking finding or authorize a refactor.
