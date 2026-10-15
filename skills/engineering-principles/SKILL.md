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

- [Foundational Thinking](references/foundational-thinking.md)
- [Redesign From First Principles](references/redesign-from-first-principles.md)
- [Model the Domain](references/model-the-domain.md)
- [Boundary Discipline](references/boundary-discipline.md)
- [Type System Discipline](references/type-system-discipline.md)
- [Experience First](references/experience-first.md)

## Refactoring or code that is hard to follow

- [Laziness Protocol](references/laziness-protocol.md)
- [Subtract Before You Add](references/subtract-before-you-add.md)
- [Minimize Reader Load](references/minimize-reader-load.md)

## Retries, concurrent writers, or caller migration

- [Outcome-Oriented Execution](references/outcome-oriented-execution.md)
- [Make Operations Idempotent](references/make-operations-idempotent.md)
- [Migrate Callers Then Delete Legacy APIs](references/migrate-callers-then-delete-legacy-apis.md)
- [Separate Before Serializing Shared State](references/separate-before-serializing-shared-state.md)

## Failed fixes, competing designs, tests, or measured claims

- [Attack the Premise](references/attack-the-premise.md)
- [Exhaust the Design Space](references/exhaust-the-design-space.md)
- [Prove It Works](references/prove-it-works.md)
- [Fix Root Causes](references/fix-root-causes.md)
- [Test Behavior, Not Implementation](references/test-behavior-not-implementation.md)
- [Explain the Number](references/explain-the-number.md)

## Sweeps, delegation, long tasks, or repeated instructions

- [Build the Lever](references/build-the-lever.md)
- [Sequence work into verifiable units](references/sequence-work-into-verifiable-units.md)
- [Guard the Context Window](references/guard-the-context-window.md)
- [Never Block on the Human](references/never-block-on-the-human.md)
- [Encode Lessons in Structure](references/encode-lessons-in-structure.md)

For a cross-cutting task, read the applicable principles across groups. Give
delegates the relevant file paths and the decision or proof they own through
[Orchestration](../orchestration/SKILL.md).

Explain the concrete choice and its evidence when it matters to the result.
Keep proposed checks distinct from checks run. A principle name or a completed
checklist does not establish that the behavior works.
