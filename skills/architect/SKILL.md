---
name: architect
description: "Sketch caller usage, types, signatures, and module structure, then stay in the loop while implementation fills in. Use for architect requests or consequential interface and ownership decisions that need a design to guide implementation."
---

# Architect

Design consequential interfaces and module structure from caller usage first,
synthesize across independent candidates, and keep the sketch aligned while
implementation fills it in. Start from a design request, existing callers and
constraints, or a caller-supplied selection. Leave a caller-first type sketch,
module map, and design rationale—plus verified code when implementation is in
scope. You are done when the requested finish line is met (design package,
ordered migration plan, or verified implementation) with checked vs unproven
claims separated.

[Codebase Design](../codebase-design/SKILL.md) supplies the shared vocabulary
(**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**,
**locality**). Routine changes with an established shape need no design panel.

Open a task plan for the applicable phases: Ground, Sketch, Agree, Implement, and
Scrap (when needed), and resolve the finish line from the request up front.

## Phase A: Ground the problem

Build a real mental model of every system the change touches: read affected
callers, types, state owners, project glossary, and relevant ADRs, and trace how
data and control flow and which invariants must hold. Use [Why](../why/SKILL.md)
when redefining ownership or layering so prior rationale acts as a constraint,
and [How](../how/SKILL.md) when runtime/data-flow walkthroughs are missing. Skip
Phase A only for genuinely greenfield work, still naming requirements and caller
constraints.

## Phase B: Sketch

If the caller supplied a selected design, reuse its rationale, checked findings,
and experiments while they still fit current callers and requirements; fill gaps
and reopen only unresolved or invalidated choices without running a new panel.

For a fresh design decision, run [Arena](../arena/SKILL.md) with the Phase A
grounding and pass [design candidate brief](references/design-candidate.md) to
each runner (model selection, isolation, and recovery follow
[Orchestration](../orchestration/SKILL.md)):

- **Design it twice:** require at least two independent whole-shape candidates
  per [Exhaust the Design Space](../engineering-principles/references/exhaust-the-design-space.md).
  If candidates converge, use Arena's consensus branch—record why constraints
  favor that shape and what was rejected instead of manufacturing differences.
- **Screen before synthesis:** check every candidate against
  [preventing recurring mistakes](../codebase-design/references/preventing-mistakes.md).
  Prefer the design where an agent reading only a few files and copying the
  nearest example stays right for the whole repo.
- **Compare interface depth:** prefer hiding more complexity behind a smaller,
  simpler public surface that keeps call chains short.
- **Test empirical questions:** use [Prototype](../prototype/SKILL.md) for UI
  interaction and
  [architecture experiments](../codebase-design/references/experiments.md) for
  caller compatibility, state, concurrency, or performance. Record what each
  experiment proved and what stays unproven before finalizing synthesis.

Arena returns one synthesized design package; its verdict fills the rationale's
Synthesis decision section.

## Phase C: Agree (opt-in)

For implementation requests, proceed directly unless the user explicitly asks
for a checkpoint (*"architect with checkpoint"*, *"stop and show me before
implementing"*); then present the design and wait for sign-off. Design-only
requests finish here with the checked design; planning-only requests finish with
the ordered migration plan specified under Outputs below without entering
implementation.

The accepted design can be its own commit when commits are in scope. Keep
temporary scaffolding inside development boundaries and restore delivery checks
before handoff per
[Outcome-Oriented Execution](../engineering-principles/references/outcome-oriented-execution.md).
Use [Review](../review/SKILL.md) if independent pre-implementation assessment
was requested. Treat human pushback on the shape as Phase A evidence: re-ground
and re-run Phase B before writing code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code and pseudocode with logic. Treat the
accepted sketch as the contract: surface deviations rather than absorbing them
silently—if a function needs an unanticipated parameter, determine whether the
sketch was wrong, a requirement was missed, or the implementation overreached.
Resolve technical questions from code and experiments; ask the user only for
product choices that materially change the result.

Implement with [TDD](../tdd/SKILL.md) at the agreed seams, sequencing multi-part
work into small verifiable units. Verify real workflows with
[Verify](../verify/SKILL.md), demonstrate integrated results with
[Show Me](../show-me/SKILL.md), remove temporary stubs and comparison controls,
and record decisive evidence in the project record already in scope.

## Phase E: Scrap when the architecture is wrong

When implementation repeatedly produces friction the sketch cannot absorb, scrap
the sketch instead of bolting fixes onto a wrong design per
[Redesign From First Principles](../engineering-principles/references/redesign-from-first-principles.md)
and [Fix Root Causes](../engineering-principles/references/fix-root-causes.md).

Watch for recurring patterns (a few isolated edge cases or genuine data
complexity do not condemn a design):
- the same workaround recurring across unrelated code;
- multiple unrelated edge cases requiring special-case branches;
- type escape hatches (`any`, casts, always-set optionals) needed to compile;
- reaching for a lock when the sketch assumed unshared state;
- callers needing internal abstraction rules to use the interface;
- two or more independent Phase D deviations of the same shape.

To scrap: (1) re-ground with the new caller and runtime evidence, (2) redesign
with those constraints as day-one assumptions, (3)
[Subtract Before You Add](../engineering-principles/references/subtract-before-you-add.md)
so the new sketch starts smaller, and (4) return to Phase B within requested
scope.

## Outputs

Write caller usage first and derive the type sketch from it (one file for small
changes; module map plus types for larger work). Ship the prose rationale per
[design rationale](references/design-rationale.md), including usage sketch,
synthesis decision, experiment commands and evidence, remaining gaps, and any
requested plan or verified implementation, keeping proposed behavior separate
from checked claims. A requested migration plan sequences verifiable units and
names affected callers, dependencies, compatibility paths, and proof per unit
after technical uncertainties are checked or explicitly bounded.
