---
name: arena
description: "Produce independent candidates for one artifact, pick a base, and graft the strongest parts into one verified result. Use for arena requests, comparisons of competing designs or implementations, or candidate synthesis requested by another workflow."
---

# Arena

Produce independent competing candidates for one artifact, judge them against a
shared rubric, and either recommend a winner or synthesize a verified result.
Start from an artifact goal, constraints, and finish line (synthesis by default;
comparison-only when requested). Leave the required Outputs below for that
finish line. You are done when the requested finish line is delivered with
observed proof, or reported incomplete under Phase B.

Open a task plan with one entry per phase (Frame, Fan out, Cross-judge, Pick,
Graft, Verify) before launching. Preserve the caller's finish line; production
implementation follows only when requested.

## Phase A: Frame

Every candidate receives the same prompt as its contract:
1. State the artifact, preserved constraints, and success evidence.
2. Define 3–6 concrete gradeable rubric criteria before seeing any candidate, and
   share them with candidates and the cross-judge.
3. Choose runners through [Orchestration](../orchestration/SKILL.md) using its
   model defaults for candidates and Primary review for the cross-judge unless
   the caller names models. Honor requested counts (minimum two for comparison;
   independent attempts on one model count too) and report any unobtainable
   model diversity.
4. Give each candidate an isolated output path—a delegated worktree for code or
   a per-runner scratch directory for standalone artifacts—starting from the
   same confirmed revision, passing relevant uncommitted inputs explicitly.

Use [Prototype](../prototype/SKILL.md) for UI observation on the target platform
and [architecture experiments](../codebase-design/references/experiments.md) for
technical assumptions; keep product preferences distinct from facts a run can
settle. Coverage partitions and races belong to
[Swarm](../swarm/SKILL.md); Arena assigns every runner the same artifact.

## Phase B: Fan out

Dispatch independent candidates through Orchestration with the shared task,
rubric, grounding, output path, and instructions to include a short rationale of
considered and rejected alternatives. Keep candidates isolated from each other;
run in parallel within capacity, or in waves using the same starting inputs.
On dropouts, apply Orchestration's bounded recovery; fewer than two usable
candidates makes the comparison incomplete rather than declaring a winner.

## Phase C: Cross-judge

After all candidates stop writing, dispatch one read-only cross-judge through
Orchestration (running in parallel with your Phase D reading) with the rubric
and path-labeled candidates. Keep the candidates fixed while judging them. The
judge scores each criterion on evidence—not model reputation—and recommends a
base. An unavailable required judge is a coverage gap to report while retaining
candidates.

## Phase D: Pick a base

Read every candidate end to end, score criterion by criterion, and compare with
the cross-judge. Agreement supports the pick; disagreement signals potential
bias or rubric ambiguity—check evidence and clarify the rubric across all
candidates if needed.

Prefer the base easiest to extend without breaking invariants; on ties, prefer
the cleaner interface or smaller public surface per
[Laziness Protocol](../engineering-principles/references/laziness-protocol.md).
Judge UI on the target surface and performance on comparable workloads; scores
never replace required proof.

Comparison-only requests finish here with candidates, evidence, tradeoffs, and
recommendation. On any path—including synthesis—preserve an explicitly requested
user choice or checkpoint here before proceeding to Phase E grafting or
consensus adoption.

## Phase E: Graft (synthesis only)

Scan each losing candidate for 1–2 high-value improvements to fold into the
base by hand per
[Redesign From First Principles](../engineering-principles/references/redesign-from-first-principles.md)
so the result keeps one coherent mental model without breaking base invariants.
If candidates converge on one shape, use the consensus shape with no graft. If
they answered incompatible interpretations of the brief, reframe and rerun
instead of averaging.

## Phase F: Verify (synthesis only)

Verify the combined artifact per
[Prove It Works](../engineering-principles/references/prove-it-works.md)—passing
candidates never prove their combination works. Design sketches support only
claims exercised by caller checks or experiments; label untested runtime claims.
For production changes, run [Verify](../verify/SKILL.md). Revisit the frame or
graft if verification fails instead of papering over it.

## Outputs

- **Comparison-only:** candidates, evidence, tradeoffs, recommendation, dropouts,
  run instructions, and remaining evidence gaps.
- **Synthesis:** synthesized artifact plus synthesis note (base and why,
  cross-judge verdict, each graft and source, rejections and why, convergence or
  dropouts, verification result, run instructions, and gaps).

Retain candidates until the decision and decisive evidence are recorded; clean
up task-owned disposable work only after it is no longer needed.
