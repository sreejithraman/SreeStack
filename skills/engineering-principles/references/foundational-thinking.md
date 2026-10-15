# Foundational Thinking

Before writing logic, name the data shape, invariants, dominant reads and
writes, and state owner. Choose collections and types that fit those access
patterns. Establish shared types and the smallest useful check before dependent
features. Simplify obsolete structure before adding scaffolding; each increment
should add a coherent capability rather than coordination spread across callers.
Give each mutable fact one authoritative owner; other modules read it or request
changes through that owner. Define refresh and invalidation for derived views.
