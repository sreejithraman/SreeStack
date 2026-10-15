# Simplifying a change

## Laziness Protocol

Understand the requested behavior and actual consumers before minimizing the
solution. Try the first option that meets the requirements:

1. Remove work or a concept that is unnecessary.
2. Reuse an existing implementation or pattern in the repository.
3. Use the standard library or native platform capability.
4. Use an already-installed dependency when it fits.
5. Write the smallest clear implementation that handles the real cases.

Consolidate repeated decisions under one owner. Count the knowledge callers
must coordinate, not just changed lines. A small patch in the wrong place can
leave sibling callers broken. Preserve interfaces, adapters, and checks whose
consumers or invariants justify them.

## Subtract Before You Add

Remove proven dead paths, redundant checks, speculative hooks, and empty
scaffolding before building on them. Search callers, tests, fixtures, strings,
and dynamic references before deletion. Keep checks required by the trust model
or failure contract. Choose the order that reduces migration work without
breaking a supported consumer. In instructions, delete duplicated guidance
once an applicable pointer reaches its authoritative home.

## Minimize Reader Load

Assess both layers to trace and state to hold in mind. Prefer interfaces that
hide meaningful decisions; collapse pass-through layers that add neither policy
nor adaptation. Derive values instead of synchronizing copies. Keep mutable
state as local as its real owner allows. Before adding a layer or field, name
the complexity it removes for callers or maintainers.

Use [codebase-design](../../codebase-design/SKILL.md) to assess interface depth,
locality, and seam placement. A one-caller wrapper is a candidate to inspect,
not proof that the abstraction is useless.
