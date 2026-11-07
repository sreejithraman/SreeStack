---
name: tdd
description: Use when implementing a feature or bug fix, or when the user asks for test-driven development.
---

# Test-Driven Development

Build the requested behavior test first, through the red → green loop. Start from
the requested behavior and an existing or inferred public seam. Leave tests worth
keeping and the code that passes them. You are done when every behavior went red, then
green, one at a time.

## The loop

1. Name the [seam](#seams-where-tests-go), and list the behaviors in plan order, in the
   project's [domain language](#domain-language). The list is a plan, not tests.
2. Write the test for the next behavior only. Several cases of one behavior can go
   together.
3. Run it and watch the behavior fail for the expected reason. A guard case that
   already passes can stay beside it.
4. Write only enough code to pass it, and run it to green. Leave later behaviors to
   their own cycles.
5. Repeat from step 2. The next behavior waits until this one passes.

Work in **vertical slices**: one seam, one behavior, and one minimal implementation per
cycle. Each test is a **tracer bullet** that responds to what the last cycle taught you.
Tests written in bulk verify _imagined_ behavior: they test the _shape_ of things rather
than user-facing behavior, they go insensitive to real changes, and they commit you to a
test structure before you understand the implementation.

Refactoring is not part of the loop. It belongs to the review stage (see the
`review-fix-loop` skill), not the red → green implementation cycle.

Every section below applies on every cycle: consult them before and during the loop,
not after.

## Domain language

Resolve project, legacy, or custom glossary paths with [glossary paths](../domain-modeling/references/glossary-paths.md) before reading or writing the domain vocabulary.

When exploring the codebase, read `GLOSSARY.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

When choosing assertions and checking that tests detect a broken behavior, read
[Test Behavior, Not Implementation](../engineering-principles/references/test-behavior-not-implementation.md)
and [Prove It Works](../engineering-principles/references/prove-it-works.md).

Take each expected value from a source independent of the code under test: a known-good
literal, a worked example, or the spec. A test is **tautological** when its oracle
copies the production algorithm, derives from the actual result, or asserts a constant
equal to itself.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.
For lifecycle or async behavior, use the [event-sequence example](tests.md#event-sequences)
to choose scenarios through the agreed public seam.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Choose the test seam from the requested
behavior, existing public interfaces, and project conventions. A seam
established by the spec or project conventions counts as pre-agreed. Name it
before writing a test. Ask the user only when plausible seams would materially
change the result and the choice cannot be inferred. You can't test everything —
agreeing the seams up front is how testing effort lands on the critical paths
and complex logic instead of every edge case.

Ask yourself: "What's the public interface, and which seams should we test?"

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), apply the skill "codebase-design" for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.
