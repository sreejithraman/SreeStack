# Type System Discipline

Make the compiler reject contradictory variants, mismatched semantic IDs, and
unhandled cases. Use discriminated unions, enums with payloads, or equivalent
language features; construct valid values rather than accepting loose shapes
and repairing them everywhere. Brand or wrap primitives when interchange is a
real risk. Parse external values, exhaust variants, and derive types from owned
schemas. Prefer narrowing and validated construction over unchecked casts;
isolate any necessary unsafe operation behind an auditable interface.

Strengthen a type where partiality creates a real invalid operation. A total
sum can accept an empty collection; an operation requiring a first element
needs a nonempty value or an explicit absent result. Precision should remove
failure paths, not burden callers with facts they never need.
