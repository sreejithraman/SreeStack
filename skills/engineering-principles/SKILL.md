---
name: engineering-principles
description: Guide engineering design and implementation decisions. Use when choosing data models or interfaces, simplifying code, planning migrations, handling retries or shared state, evaluating evidence, or organizing substantial work.
---

# Engineering Principles

Use these principles to choose the shape of the work. The relevant workflow
still owns its procedure, checks, and completion criteria. Apply them within
the user's scope, product requirements, and execution permissions.

Read only the principles that match the decision before acting. Each link opens
one principle; a named request selects that principle directly.

## Data, types, interfaces, or product tradeoffs

- [Foundational Thinking](references/foundational-thinking.md): when choosing data structures, access patterns, invariants, or state ownership before writing logic.
- [Redesign From First Principles](references/redesign-from-first-principles.md): when a new requirement calls an existing design into question.
- [Model the Domain](references/model-the-domain.md): when stateful logic branches heavily or repeats domain rules across callers.
- [Boundary Discipline](references/boundary-discipline.md): when parsing external input, enforcing trust boundaries, or introducing framework adapters.
- [Type System Discipline](references/type-system-discipline.md): when designing types, signatures, or schemas that should rule out invalid operations.
- [Experience First](references/experience-first.md): when product, interface, or feature-scope tradeoffs compete with implementation convenience.

## Refactoring or code that is hard to follow

- [Laziness Protocol](references/laziness-protocol.md): when refactoring or considering another abstraction, dependency, or layer.
- [Subtract Before You Add](references/subtract-before-you-add.md): when sequencing an addition, refactor, or rewrite around existing dead or redundant structure.
- [Minimize Reader Load](references/minimize-reader-load.md): when layers, hidden state, or pass-through wrappers make code hard to follow.

## Retries, concurrent writers, or caller migration

- [Outcome-Oriented Execution](references/outcome-oriented-execution.md): when planning a rewrite or migration with explicit development and delivery boundaries.
- [Make Operations Idempotent](references/make-operations-idempotent.md): when commands, lifecycle steps, or processing loops can repeat, crash, or restart.
- [Migrate Callers Then Delete Legacy APIs](references/migrate-callers-then-delete-legacy-apis.md): when introducing a replacement internal interface while callers still use the old route.
- [Separate Before Serializing Shared State](references/separate-before-serializing-shared-state.md): when concurrent actors might write the same file, key, object, or shared state.

## Failed fixes, competing designs, tests, or measured claims

- [Attack the Premise](references/attack-the-premise.md): when successive fixes share an assumption and keep failing the same check.
- [Exhaust the Design Space](references/exhaust-the-design-space.md): when a novel interaction or unresolved architecture tradeoff needs a concrete comparison.
- [Prove It Works](references/prove-it-works.md): when deciding whether an artifact or consumer workflow satisfies the requested outcome.
- [Fix Root Causes](references/fix-root-causes.md): when diagnosing a defect or repairing a symptom that may affect sibling callers.
- [Test Behavior, Not Implementation](references/test-behavior-not-implementation.md): when choosing assertions, expected results, or mocks that must detect broken behavior.
- [Explain the Number](references/explain-the-number.md): before trusting, reporting, or acting on a performance measurement or evaluation result.

## Sweeps, delegation, long tasks, or repeated instructions

- [Build the Lever](references/build-the-lever.md): when substantial or repeated work could benefit from a rerunnable tool or shared recipe.
- [Sequence work into verifiable units](references/sequence-work-into-verifiable-units.md): when ordering dependent edits, migration stages, commits, or PR layers into checkable increments.
- [Guard the Context Window](references/guard-the-context-window.md): when large outputs, repeated reads, or broad investigations crowd out useful context.
- [Never Block on the Human](references/never-block-on-the-human.md): when routine, reversible uncertainty tempts a question that repository evidence or an experiment can settle.
- [Encode Lessons in Structure](references/encode-lessons-in-structure.md): when repeated instructions or recurring corrections reveal a rule that needs durable enforcement.

For a cross-cutting task, read the applicable principles across groups. Give
delegates the relevant file paths and the decision or proof they own through
[Orchestration](../orchestration/SKILL.md).

Explain the concrete choice and its evidence when it matters to the result.
Keep proposed checks distinct from checks run. A principle name or a completed
checklist does not establish that the behavior works.
