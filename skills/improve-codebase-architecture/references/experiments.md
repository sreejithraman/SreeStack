# Architecture experiments

Use a disposable technical experiment when a design decision depends on a fact
that code or records cannot settle. A type sketch, real-caller migration slice,
state-machine harness, or concurrency replay can test architecture without a UI
prototype. For a question about the interface a person sees or uses, use
[prototype](../../prototype/SKILL.md).

## Frame and run

State the decision, competing hypotheses where useful, and the observable result
that would distinguish them before building. Use the smallest real caller,
representative fixture, or historical failure that reaches the disputed behavior.
Keep known product requirements and legitimate compatibility paths in the check.

Use a temporary directory or clearly marked development surface. Keep experiments
out of release builds and external writes stubbed or confined to an already
authorized disposable environment. Preserve unrelated work. Permission to
investigate a design does not authorize production migration.

Run the relevant check: compile a proposed interface against its caller, replay
the failure, exercise state transitions, or measure the operation. A sketch that
was never compiled or run supports a proposal, not an experimental result.
For performance comparisons, use
[measurement validity](../../diagnosing-bugs/references/measurement-validity.md)
before choosing from the numbers.

## Decide and retain proof

Record the revision, fixture, exact commands, observed outcomes, and limitations.
Recommend an option on that evidence; label unresolved hypotheses and name the
next check. An unavailable environment narrows the conclusion rather than turning
an unrun experiment into a pass.

Retain the smallest reviewable artifacts and run instructions until the planning
decision is made. Before deleting a disposable experiment, preserve its decisive
evidence in the requested plan or existing project record. A successful experiment
does not make the candidate production-ready; implementation still needs caller
migration, regression checks, and review.
