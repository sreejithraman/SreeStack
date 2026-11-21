# Minimize Reader Load

Assess both layers to trace and state to hold in mind. Prefer interfaces that
hide meaningful decisions; collapse pass-through layers that add neither policy
nor adaptation. Derive values instead of synchronizing copies. Keep mutable
state as local as its real owner allows. Before adding a layer or field, name
the complexity it removes for callers or maintainers.

Assess interface depth, locality, and seam placement before restructuring. A
one-caller wrapper is a candidate to inspect, not proof that the abstraction is
useless.
