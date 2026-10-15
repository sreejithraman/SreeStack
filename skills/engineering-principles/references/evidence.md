# Evidence for a decision

## Attack the Premise

When successive fixes sharing an assumption fail the same check, write down that
assumption before another attempt. Choose a discriminating observation that could
refute it. For uneven resource ownership or actor behavior, count the distribution
per actor across runs and trace what assigns their roles. For other failures,
measure the fact the assumption depends on. Use the evidence to revise the model
or rule it out; another variation of the same patch is not a new hypothesis.

## Exhaust the Design Space

For a novel interaction or unresolved architecture tradeoff, compare meaningfully
different designs against the same requirements and criteria. Try enough options
to expose the decision; use a single experiment when testing one concrete claim
and additional candidates when they answer distinct questions. Use
[prototype](../../prototype/SKILL.md) for UI and
[architecture experiments](../../improve-codebase-architecture/references/experiments.md)
for technical assumptions. Existing precedents can settle routine decisions.

## Prove It Works

Check the actual artifact or consumer workflow against the requested outcome.
A build, file timestamp, child summary, or cached screenshot proves only what
it directly observes. Prefer a rerunnable check with captured inputs and outputs.
Inspect surprising observations for a faulty measurement method as well as a
product failure. Reuse proof only while its revision, configuration, and scenario
still apply. [Verify](../../verify/SKILL.md) owns real-workflow acceptance checks.

## Fix Root Causes

Reproduce the actual symptom and test falsifiable causes before repairing it.
Inspect sibling callers for the same mechanism; repair at the owner within the
authorized scope. A guard is justified when it enforces the real contract, not
when it hides a failed invariant. Restart failures call for inspecting persisted
state and its recovery protocol. Use [diagnosing-bugs](../../diagnosing-bugs/SKILL.md)
for reproduction, instrumentation, repair, and regression proof.

## Test Behavior, Not Implementation

Call the subject through its consumer-facing interface and assert an independently
established result or observable effect. Expected values should come from the
contract, a worked example, or a trusted fixture. The test must fail if the relevant
behavior is removed or returns the wrong result. For mocked effects, inspect the
meaningful payload; for an empty or absent result, exercise a contrasting case
when it distinguishes correct behavior from doing nothing.

Empty results, error assertions, relation checks, and compile-time type tests can
be valid contracts. Judge what they detect instead of banning assertion syntax.
Keep [tdd](../../tdd/SKILL.md)'s seam selection and vertical red/green workflow
for implementation, and its examples for tests and mocking.

## Explain the Number

Before acting on a measurement, establish what completed, whether it was correct,
and which resource or mechanism bounds the result. Rule out skipped work, fast
errors, unfair settings, cache effects, and noise. Report units, conditions,
repetitions, spread, and the limit the evidence supports. Performance comparisons
use [measurement validity](../../diagnosing-bugs/references/measurement-validity.md).
For an evaluation, check that trials performed the task and the difference holds
across appropriate cases and repeats. A bounded trial supports that scenario;
it does not prove general agent reliability.
