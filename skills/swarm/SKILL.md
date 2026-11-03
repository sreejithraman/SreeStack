---
name: swarm
description: Run a bounded parallel assignment and return one consolidated result. Use when asked to swarm work or when a session needs parallel coverage, disjoint implementation, exploration, or a race between approaches.
---

# Swarm

Provide parallel work to the calling session. The caller keeps its PR or
program ownership; this tool ends when its bounded result is returned. Use
[Orchestration](../orchestration/SKILL.md) for model selection, briefs,
isolation, concurrency, recovery, and acceptance.

## Frame

Establish the requested result, preserved constraints, completion evidence,
and return artifact before dispatch. Choose the shape:

- **Coverage:** partition into required slices with explicit ownership.
- **Race:** give independent workers the same outcome and declare the selection
  rule before starting: first valid pass, rank all, or best result.
- **Mixed:** compare approaches within slices and then assemble required coverage.

A race winner satisfies the assignment only when it covers the whole brief. A
losing experiment can finish its worker's assignment without satisfying the
caller's result. Use [Arena](../arena/SKILL.md) when selecting a base and
synthesizing competing candidates is the actual task. A target to pursue until
it is met belongs to an [Implement](../implement/SKILL.md) owner, which runs
Swarm rounds that select the best result toward it.

## Dispatch

Give every worker an Orchestration brief naming its slice or race arm, owned
writable paths, relevant skills, and return format. Each returns **PASS**,
**ISSUES**, or **BLOCKED** with artifact/revision, decisive evidence, and
coverage gaps, reporting every supported issue in its scope rather than only
the first.

The caller or its named integrating owner serializes shared writes and
branch/index operations.

Verification arms get concrete failure questions and suitable empirical checks,
deterministic tools, or source/contract arguments. Keep what was exercised
separate from what remains a hypothesis; agreement across workers does not
establish an unobserved outcome. Requested formal checks follow
[Verify](../verify/SKILL.md), including model/code correspondence and limits.

Follow live completion and wait rules; a timeout leaves work running. Once a
race is decided, cancel unneeded workers through the host and reconcile live
writers before replacing or reusing their outputs.

## Aggregate and return

Accept worker results under Orchestration. For coverage, every required slice
needs an accepted result. For a race, apply the declared rule. A proven issue
stays an issue even when other workers pass. Resolve conflicting results
against the artifact, or return the open claim and the check that would settle it.

Verify integration affected by combining outputs. Return one consolidated
result: accepted outputs, issue one-liners, worker dispositions, evidence,
gaps, the selection rule, and remaining delivery work for the caller. When
invoked directly, the user is the caller and you perform its acceptance for
this bounded assignment. Swarm alone creates no program, native goal,
recurring schedule, PR publication, or merge grant.
