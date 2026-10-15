# Data and interface decisions

## Foundational Thinking

Before writing logic, name the data shape, invariants, dominant reads and
writes, and state owner. Choose collections and types that fit those access
patterns. Establish shared types and the smallest useful check before dependent
features. Simplify obsolete structure before adding scaffolding; each increment
should add a coherent capability rather than coordination spread across callers.
Give each mutable fact one authoritative owner; other modules read it or request
changes through that owner. Define refresh and invalidation for derived views.

## Redesign from First Principles

When a requirement changes the design, ask what shape you would choose if it
had been present from the start. Read the affected callers, types, examples,
and constraints. Compare that target with a local extension and justify the
scope by current benefit. Deliver the selected change incrementally; a fresh
design perspective is not authorization for an unrelated rewrite.

## Model the Domain

Represent domain rules in data where that removes duplicated decisions or
invalid combinations: a state machine for lifecycle transitions, a sum type
for exclusive cases, a registry for dispatch, or an index for repeated lookup.
Group behavior by the knowledge and invariants it owns, not execution phases.
Derive repeated definitions from one authority. Keep a clear existing shape
when another abstraction would add coordination without removing it.
When derivation is impractical, check parity so a partial update fails visibly.

Use [domain-modeling](../../domain-modeling/SKILL.md) for vocabulary and ADRs;
use [codebase-design](../../codebase-design/SKILL.md) for deep modules and seams.

## Boundary Discipline

Parse external input into domain values where trust changes: requests, CLI
arguments, configuration, stored records, and third-party responses. Keep
transport, storage, and framework representations behind the interface. Prefer
pure domain logic with a thin effectful shell. Inside a validated trust domain,
use established invariants instead of scattering the same checks through callers.
Runtime authorization, changing state, and data arriving from untrusted code
still need checks at their actual enforcement point.
Enforce private implementation through language visibility, package exports, or
an import rule so callers cannot take a convenient bypass. Inject effectful
dependencies when real callers or tests need to substitute them.

## Type System Discipline

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

## Experience First

Choose the experience of the consumer and next maintainer over implementation
convenience. Justify controls and options by the core workflow, and prefer a
finished, useful scope over many rough paths. For a library, consider the caller's
usage and errors; for a UI, include loading, feedback, accessibility, and failure
states. Use [prototype](../../prototype/SKILL.md) when feel or interaction needs
to be tried. Product direction and required capabilities remain the user's.
