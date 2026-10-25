---
name: architect
description: "Sketch caller usage, types, signatures, and module structure, then stay in the loop while implementation fills in. Use for architect requests or consequential interface and ownership decisions that need a design to guide implementation."
---

# Architect

Sketch types, function signatures, class shapes, and module structure with
`not implemented` bodies and pseudocode. Synthesize across independent
perspectives, then fill in code against the chosen sketch within the requested
scope. [Codebase Design](../codebase-design/SKILL.md) supplies the shared
module, interface, depth, seam, adapter, leverage, and locality vocabulary.

## Start

Open a task plan with one entry per applicable phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap, when the architecture is wrong

Resolve the finish line from the request. A design-only or planning request
ends with the design or plan. An implementation request continues through
implementation and verification. Routine changes with an established shape
use the normal implementation workflow; they need no design panel.

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Read the
affected callers, types, state owners, project glossary, and relevant ADRs.
Naming a file isn't grounding. Explain how data and control move through the
affected system and which invariants the new design must preserve. If the
design redefines ownership or layering, also use [why](../why/SKILL.md)
on the existing shape so the rationale becomes a constraint, not a guess.

Use [how](../how/SKILL.md) when a subsystem walkthrough would establish missing
runtime and data-flow grounding.

Skip Phase A only when the work is genuinely greenfield with no surrounding
system to integrate. Even then, name the requirements and caller constraints.

## Phase B: Sketch

When the caller supplies a selected design, reuse its rationale and checked
findings and experiments while they still apply to the current callers and
requirements. Fill missing parts of the design package and proof; reopen only
unresolved or invalidated choices. If the shape is settled, continue to Phase C
without requiring a new panel.

For a fresh design decision, run [arena](../arena/SKILL.md) with the design-sketch
task and the Phase A grounding artifacts. Pass [the design candidate brief](references/design-candidate.md)
to each runner. Model selection, delegation, isolation, and recovery belong to
[orchestration](../orchestration/SKILL.md).

Design it twice. Require at least two independent candidates before synthesis,
even when the first looks sufficient. This is
[Exhaust the Design Space](../engineering-principles/references/exhaust-the-design-space.md)
made concrete. Whole-shape alternatives, not point fixes inside one shape.
If independent candidates converge, use arena's consensus branch: record why
the constraints favor that shape and which alternatives were rejected. Do not
manufacture structural differences just to meet a count.

Screen every candidate against Codebase Design's
[ownership and enforcement checks](../codebase-design/references/preventing-mistakes.md)
before synthesis. Assume the next contributor is an agent that sees only the
files it opened, copies the nearest example, and takes the shortest path that
compiles. Prefer the design where a change that looks right from one file is
right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides
more complexity behind a smaller, simpler public surface. A rich interface can
keep call chains short by concentrating capability instead of scattering it
across layers.

Answer empirical questions by running something. Use
[prototype](../prototype/SKILL.md) for the interface a person sees or uses, and
[architecture experiments](../improve-codebase-architecture/references/experiments.md)
for caller compatibility, state, concurrency, or performance. Record what each
experiment proved and what stays unproven before finalizing the synthesis.

Arena returns one synthesized design package. Its synthesis decision fills
the rationale's "Synthesis decision" section.

## Phase C: Agree (opt-in)

For an implementation request, proceed directly with the accepted design
unless the user requested a checkpoint. Opt in when the invoker explicitly
asks: "architect with checkpoint," "stop and show me before implementing," or
similar. Then surface the accepted design and pause for sign-off. A design-only
request is complete with the checked design. A planning-only request completes
with the ordered plan described below. Neither enters implementation.

The accepted design can be its own commit when commits are in scope.
Keep temporary scaffolding within the development boundary and restore the
delivery checks before handoff, per
[Outcome-Oriented Execution](../engineering-principles/references/outcome-oriented-execution.md).
For requested independent assessment before implementing, use
[review](../review/SKILL.md) on the concrete sketch and experiment evidence.

If the human pushes back on the shape, treat that as Phase A evidence.
Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

For implementation requests, replace `not implemented` bodies with code,
pseudocode with logic. The accepted design is the contract. Deviations from it
are signal to surface, not friction to absorb silently. If a function needs a
parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was
missed, or the implementation is overreaching. Resolve technical questions
from the code and experiments; bring product choices to the user only when
their answer materially changes the result.

Use the project's implementation skills, including [tdd](../tdd/SKILL.md) at
the agreed interfaces. For multi-part work, order the implementation into
small verifiable units; a requested migration plan names affected callers,
dependencies, compatibility paths, and the proof for each unit. Record plan
steps after the design's technical uncertainties are checked or explicitly
bounded.

Verify the real workflow with [verify](../verify/SKILL.md), and use
[showroom](../showroom/SKILL.md) for demonstrations and access to the integrated
result. Review the complete
integrated change through [review-fix-loop](../review-fix-loop/SKILL.md), or let
[pr](../pr/SKILL.md) own that loop when publishing the same scope. Remove
temporary stubs and comparison controls from the production result. Preserve
the chosen design, decisive evidence, and reasons in the project record
already in scope.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the
sketch out. Don't bolt fixes onto a wrong design, per
[Redesign From First Principles](../engineering-principles/references/redesign-from-first-principles.md)
and [Fix Root Causes](../engineering-principles/references/fix-root-causes.md).

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in
  practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the
  implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems
are legitimately complex. Complexity in the data is not complexity in the
design.

When you scrap:

1. Re-ground in what's been built, including the new caller and runtime evidence.
2. Redesign as if the new constraints had been day-one assumptions.
3. [Subtract before adding](../engineering-principles/references/subtract-before-you-add.md).
   The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run arena within the requested scope.

## Outputs

The caller's usage is written first and the type sketch derived from it. One
file with new types and signatures for small changes. Module map plus type
definitions for larger work. The rationale ships alongside, shaped per the
[design rationale](references/design-rationale.md), including the usage sketch
and the synthesis decision. Distinguish proposed behavior from checked claims.
Return experiment commands, evidence, remaining gaps, and the requested plan
or verified implementation when those are in scope.
