# Model the Domain

Represent domain rules in data where that removes duplicated decisions or
invalid combinations: a state machine for lifecycle transitions, a sum type
for exclusive cases, a registry for dispatch, or an index for repeated lookup.
Group behavior by the knowledge and invariants it owns, not execution phases.
Derive repeated definitions from one authority. Keep a clear existing shape
when another abstraction would add coordination without removing it.
When derivation is impractical, check parity so a partial update fails visibly.

Use [domain-modeling](../../domain-modeling/SKILL.md) for vocabulary and ADRs;
use [codebase-design](../../codebase-design/SKILL.md) for deep modules and seams.
