---
name: swarm
description: Use when asked to swarm work, or when a job needs parallel coverage, disjoint implementation, exploration, or a race between approaches.
---

# Swarm

Run one bounded job in parallel. Start from a job and its evidence bar. Return one combined result.
You are done when every assignment returned or you reported it lost.
[Orchestration](../orchestration/SKILL.md) governs who may delegate, briefs, recovery, and
acceptance.

## Check the fit

Give independent, ready work to separate children when that adds speed or coverage. Work is
independent when each worker can finish and be checked against fixed inputs, no worker's finding
could change another's work before the end, and workers don't contend for accounts, fixtures, ports,
or devices. Separate files don't prove it.

Keep cohesive work with one owner, and say so in the result. Start a dependent slice after its input
is accepted. Never split to manage context.

Use [Arena](../arena/SKILL.md) to pick a base and graft the best of competing candidates. A target
to pursue until met belongs to an [Implement](../implement/SKILL.md) owner, which runs Swarm rounds
that select the best result toward it.

## Assign

- **Coverage:** split the job into required slices.
- **Race:** give workers the same outcome and separate outputs. Before starting, declare the
  selection rule: first valid pass, rank all, or best result.
- **Mixed:** race approaches within slices, then assemble the required coverage.

Keep writers apart under [Orchestration's assignment rules](../orchestration/SKILL.md#assign) and
[child limit](../orchestration/SKILL.md#dispatch). When outputs must land in one place, name one
child to integrate them. If you are a child yourself, integrate them.

Tell each worker the skills to use. Each returns **PASS**, **ISSUES**, or **BLOCKED** with evidence
and gaps, reports every supported issue in its scope, and separates what it exercised from
hypotheses.

## Combine

Once a race is decided, cancel unneeded workers. A timed-out worker is still running. Reconcile live
writers before you reuse or replace their outputs, under
[Replacing work](../orchestration/references/reuse-and-recovery.md#recover-work).

A result that lacks the revision and method its brief named doesn't count. Rerun that slice once.
After a second miss, record a gap. A gap is not a pass. A lost required slice stays required and
leaves the job unmet.

Apply a race's declared rule; its winner counts only when it covers the whole brief. A proven issue
stays an issue even when other workers pass. Agreement across workers does not establish an
unobserved outcome. Settle conflicts against the artifact, or return the open claim and the check
that would settle it.

Return accepted outputs, one line per issue, each worker's disposition, evidence, gaps, the
selection rule, and delivery work left for the caller. Swarm grants no program, native goal,
recurring schedule, PR publication, or merge.
