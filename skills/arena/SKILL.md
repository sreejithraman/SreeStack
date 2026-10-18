---
name: arena
description: "Produce independent candidates for one artifact, pick a base, and graft the strongest parts into one verified result. Use for arena requests, comparisons of competing designs or implementations, or candidate synthesis requested by another workflow."
---

# Arena

Open a task plan with one entry per phase (Frame, Fan out, Cross-judge, Pick,
Graft, Verify) before launching anything. By default, return one synthesized
artifact. Comparison-only work returns a recommendation; production
implementation follows only when requested. Preserve the caller's finish line.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing, the constraints it must
   preserve, and the evidence that would establish success.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks
   like on *this* task. Share the requirements and criteria with the candidates
   and judge. Set them before seeing candidates.
3. Pick the runners through [orchestration](../orchestration/SKILL.md). Use its
   working selection for candidates and primary review selection for the
   cross-judge unless the caller specifies models. Honor a requested candidate
   count. Use at least two candidates for a comparison; add more when they test
   distinct directions. Independent attempts on the same model are useful too.
   Report any requested model diversity that could not be obtained.
4. Give each candidate its own output location: a task-owned worktree through
   the host's delegation tools for code changes, or a per-runner scratch
   directory for standalone artifacts. Follow the host's current workspace
   rules and orchestration's ownership and recovery rules. Give every candidate
   the same starting source. For isolated checkouts, confirm the starting
   revision and supply relevant uncommitted inputs explicitly rather than
   assuming they were copied.

Use [prototype](../prototype/SKILL.md) when a UI question needs observation on
the target platform, and [architecture experiments](../improve-codebase-architecture/references/experiments.md)
for technical assumptions. Keep product preferences distinct from facts a run
can settle. Coverage partitions and races belong to orchestration; arena gives
each runner the same artifact to produce.

## Phase B: Fan out

Dispatch independent candidates through orchestration, each with the same task,
criteria, shared grounding, its own output path, and instructions to produce
the artifact and a short rationale naming the alternatives it considered and
what it rejected. Keep candidates independent of each other's work. Run in
parallel within capacity, or in waves with the same starting inputs.

If a candidate produces no usable output, note the dropout. Follow
orchestration's bounded recovery. With fewer than two usable candidates, report
the comparison as incomplete rather than claiming a winner.

## Phase C: Cross-judge

After all Phase B candidates stop writing, spawn one read-only judge through
orchestration. It sees the rubric and the candidates by path label, scores each
criterion, and recommends a base with rationale. It runs in parallel with your
reading in Phase D. Keep the candidates fixed while judging them.

The judge assesses evidence, not model reputation. An unavailable required
judge is a coverage gap; retain the candidates and report it. Model settings
and recovery come from orchestration rather than an arena-specific panel.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric
criterion by criterion, not on holistic feel, and compare with the cross-judge.
Agreement supports the pick. Disagreement may indicate bias or an ambiguous
rubric. Read both rationales and check the evidence before deciding; if the
rubric needs clarification, apply it to every candidate before choosing.

Pick the base a future maintainer can extend most easily without breaking
invariants. When two feel tied, prefer the cleaner interface or smaller public
surface, per [Laziness Protocol](../engineering-principles/references/laziness-protocol.md).
Judge UI behavior on the target surface and measured claims on comparable
workloads. A score does not replace the required proof.

For a comparison-only request, return the candidates, evidence, tradeoffs, and
recommendation here. Preserve an explicitly requested user choice or checkpoint
before synthesis.

## Phase E: Graft (synthesis only)

Walk each losing candidate once more for what is worth porting into the base,
usually one or two things per candidate, not most of it. Fold each graft in by
hand, per [Redesign From First Principles](../engineering-principles/references/redesign-from-first-principles.md),
so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, note the agreement and use the
consensus shape. No graft is needed. If they answer incompatible interpretations
of the brief, reframe and re-run rather than averaging the divergence. Preserve
the invariants and accepted tradeoffs of the chosen base as you graft.

## Phase F: Verify (synthesis only)

Verify the synthesized artifact like any other output, per
[Prove It Works](../engineering-principles/references/prove-it-works.md).
Run the checks the combined result needs; passing candidates do not establish
that their combination works. A design sketch supports only the claims its
caller checks or experiments exercised. Mark untested runtime claims explicitly.

If verification finds a problem the arena missed, revisit the frame or the
graft that introduced it. Don't paper over it. For production changes, use
[verify](../verify/SKILL.md) for the real workflow and
[review-fix-loop](../review-fix-loop/SKILL.md) for the complete integrated change,
or let [pr](../pr/SKILL.md) own that review when publishing the same scope.

## Outputs

Comparison-only work returns the candidates, evidence, tradeoffs, and
recommendation, including any dropouts.

Synthesis returns one synthesized artifact, with a short synthesis note alongside
naming the base and why, the cross-judge's verdict, each graft with its source
candidate, what was rejected and why, any convergence or dropouts, and the
verification result. Include run instructions and remaining evidence gaps for
either finish line. Retain the candidates until the decision and decisive
evidence are recorded; clean up task-owned disposable work only when it is no
longer needed.
