# Acceptance contract

Pair the desired improvement with the requirements that must survive it.
Use this guidance for ambitious targets, consequential changes, or candidate
selection. The request and relevant domain contracts supply the requirements;
the task owner accepts the integrated result.

## Start with enough to act

Establish three things in the existing brief, task record, or temporary plan:

- **Outcome:** what should improve and what finish line the user requested.
- **Constraints:** what relevant behavior, obligations, and scope must hold.
- **Evaluation:** how the result will be judged and by whom.

A few sentences can suffice. Reuse settled decisions and project knowledge;
no fixed schema, new project document, or whole-app audit is required. Follow
Verify's documentation policy for any project-map writes.

Resolve facts and routine choices from context. Ask when a missing preference,
conflicting requirement, consequential tradeoff, or missing authorization
materially changes the result and cannot be resolved from available evidence.
Bring a concrete recommendation where possible and continue independent work
while waiting. Do not silently lower the target or change allowed tradeoffs.

## Choose evaluation that fits the work

For **verifiable behavior**, use executable checks and observable outcomes.
Derive expectations from requirements, trusted examples, or another independent
source, using
[Test Behavior, Not Implementation](../../engineering-principles/references/test-behavior-not-implementation.md).
Reuse existing tests and fixtures. Add the smallest useful missing check when
acceptance depends on it; use [TDD](../../tdd/SKILL.md) for durable behavior checks.
Demonstrate meaningful failure detection with a contrasting input, known bug,
or invalid disposable fixture when that would resolve uncertainty about a check.
An implementation and test that repeat the same mistake are not independent
support. Use Verify's product workflow for runtime acceptance claims.

For **qualitative work**, agree on useful criteria, references, and the judge.
Compare concrete alternatives or use grounded critique where helpful. Explain
tradeoffs and uncertainty; do not invent scores or metrics to make taste appear
objective. A requested draft or set of options can be complete when delivered
with the relevant rationale. A result the user explicitly needs to approve
remains unfinished until they choose or accept it.

For **research and strategy**, distinguish sourced facts, assumptions, and
hypotheses. Assess source quality, coverage, reasoning, and unresolved questions.
Validate empirical claims where possible; do not present a recommendation as
an observed outcome. Use the relevant specialist workflow for the investigation.

Tasks can combine these methods. For example, an interface needs working
behavior and an assessment of its clarity; neither substitutes for the other.

## Grow checks with understanding

In a brownfield codebase, begin with the known objective, relevant constraints,
and next useful check. Inspect callers, tests, docs, and observed behavior as
the work reveals dependencies. Reuse valid baseline evidence and run the
relevant missing checks. Discovery and reversible experiments can start before
a comprehensive verification plan exists; exploratory observations guide the
next step without establishing acceptance.

Expand coverage for the actual change and its indirect consumers. Batching may
need ordering, filtering, and authorization checks; adding a cache may introduce
tenant isolation and invalidation risks. Use
[Blast Radius](../../blast-radius/SKILL.md) for consequential indirect effects.
Ground required expectations before accepting a change rather than deriving
them from whatever the candidate happens to do. Existing quirks are not
automatically requirements; explicit behavior changes are distinct from regressions.

For performance work, use
[measurement validity](../../diagnosing-bugs/references/measurement-validity.md)
before trusting a baseline, gain, or comparison. It owns bottleneck measurement,
completed-work checks, comparable conditions, noise, and end-to-end relevance.

## Accept with sufficient evidence

Keep evidence proportional to the claim and its consequences. Record artifact
identity, configuration, harness, workload, environment, and raw results where
a conclusion depends on them, rather than for every exploratory edit. Include
relevant uncommitted or generated changes when identifying the tested artifact.
Reuse valid checks; rerun those affected by integration or later changes. Final
claims must describe the actual delivered result and the conditions evaluated.

For required product assertions, use Verify's passed, failed, blocked, and
untested verdicts. A failed preserved requirement rejects adoption even when
the improvement passes. Passing preservation checks with an unmet target is
valid progress, not completion. Missing required evidence remains blocked or
untested; a substitute environment or child summary cannot supply an unobserved
result. Fulfill the requested review and delivery steps before calling the
whole task complete.

Hard requirements filter selection before preference scores. Inspect material
side effects through observable outputs or fresh reads as appropriate. Finite
checks support their covered conditions; they do not establish the absence
of every possible regression. For a 200 ms target, a correct 300 ms result is
progress; an 180 ms result that drops required records is rejected.

Inspect changes to tests, fixtures, and measurement methods with the result.
A legitimate check repair needs the failure, an authoritative reason for the
correction, and affected comparisons rerun under the corrected method. Mark
superseded evidence. Fix broken checks without silently weakening the success bar.

Reuse the existing independent review to assess decisive evidence and changes
to checks. Add dedicated verification only when material uncertainty warrants
it; delegation being available does not itself require another verifier.
Independent expectations matter more than agreement between agents. Pass the
evaluation criteria, evidence, and remaining gaps into the review workflow.

Keep pre-existing failures visible. Exclude a failure from acceptance only with
baseline evidence and a concrete reason it is unrelated to required evaluation.
A required assertion or mandatory delivery gate still fails when inherited.
Report its state accurately without expanding into unrelated repairs.
Goal state and delivery decisions remain with the calling workflow.
