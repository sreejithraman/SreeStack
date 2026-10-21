---
name: goal-swarm
description: Pursue an explicitly requested goal or swarm through its finish line. Work solo or coordinate bounded attempts, evaluate progress, and adapt without lowering required outcomes.
---

# Goal Swarm

Own the requested outcome through its finish line. The parent chooses useful
next actions, integrates results, and accepts the whole. A goal is the outcome
to achieve; native goal tracking is optional. Honor the user's scope, agent
limits, permissions, and effort budget.

Use this strategy only when the user explicitly requests Goal Swarm, a swarm,
or sustained pursuit of a goal. Ordinary delegation uses
[Orchestration](../orchestration/SKILL.md).

## Form the goal

Use [Reframe](../reframe/SKILL.md) to form a new goal from the user's request,
project context, and settled decisions. Reuse a current brief that already
establishes the goal. A precise request needs only a concise confirmation;
uncertain framing needs the deeper pass that the task warrants.

Keep the resulting brief in the existing task record and use it to guide
execution and acceptance. Reframe returns the brief here; this workflow keeps
ownership and continues authorized work without a routine approval checkpoint.
Ask for material user decisions under the shared acceptance guidance.

Reuse the settled brief through attempts and resume. Revisit it when new evidence
or user direction challenges the framing; preserve explicit requirements and
obtain authorization for material scope or tradeoff changes. Grow evaluation as
discovery reveals risks, using Verify's
[acceptance guidance](../verify/references/acceptance-contract.md).

## Choose solo work or bounded workers

Use [Orchestration](../orchestration/SKILL.md) for model selection, assignments,
isolation, concurrency, task lifecycle, recovery, and integration. Work solo
when the work is cohesive or splitting adds waiting and coordination.

For useful parallelism, partition required outcomes, compare independent
approaches to the same outcome, or mix both. Before dispatch, state how results
will be selected and which coverage is required. A race can end with one
acceptable result only when it satisfies the whole requested brief. Use
[Arena](../arena/SKILL.md) when candidate synthesis is the task.

Assign each worker through Orchestration's self-contained brief, including its
bounded outcome and evaluation. Workers use their relevant task skills; they
need no native goal object or separate Goal Swarm invocation. Further delegation
requires the parent's permission. Completing a losing experiment can satisfy a worker's
assignment without completing the parent outcome.

## Learn, retain progress, and adapt

Choose the next action from what prevents success and what the last attempt
established. Explore uncertain approaches reversibly. Measure the bottleneck
before performance changes. Reach for original inputs, stronger instruments,
or useful methods from another field when they can resolve the remaining gap.
Use [Architect](../architect/SKILL.md) for consequential design decisions.

Evaluate meaningful results against the outcome and preserved constraints.
Preliminary findings guide discovery; accepting a change needs suitable evidence.
Inspect the artifact and decisive evidence rather than relying on a worker's
summary. Missing coverage, failed workers, or evidence for the wrong artifact
or method leave a gap to repair or report. A failed candidate does not remove
its required slice from the parent goal.

Retain supported progress separately from unproven experiments. Reject
regressions in required behavior even when the headline target passes. A correct
improvement that misses a hard target is progress, not completion. Keep the
target intact while changing approaches; stronger methods do not authorize
new scope or tradeoffs. Repeating equivalent attempts is not progress. When
evidence establishes a limit needing a user decision, explain the gap and ask.

Keep enough context in the existing task record to resume: accepted results,
remaining gaps, decisive evidence, and the next useful action. Record comparison
conditions where claims depend on them. On resume, reconcile the latest user
decisions, artifacts, and pending tasks before continuing, applying the acceptance
guidance to evidence affected by changes. Delivered commits, PR layers, and
rollout stages retain their required checks, per
[Outcome-Oriented Execution](../engineering-principles/references/outcome-oriented-execution.md).

## Deliver and report

Evaluate the final integrated result using the agreed criteria. Use
[Verify](../verify/SKILL.md) for real product workflows. For a PR finish line,
[PR](../pr/SKILL.md) owns review, publication, CI, feedback, and fixes; use
`pr yolo` only for an explicitly requested merge. For local code or agent-procedure
changes, use [Review Fix Loop](../review-fix-loop/SKILL.md) when its trigger applies.
Pass evaluation criteria, decisive evidence, and gaps into the existing review.

Finish only when the requested outcome, relevant constraints, evaluation, and
delivery state are satisfied. Intermediate progress or exhausted effort is not
completion of an unmet goal. Honor a requested pause. Report what was accepted,
what remains unfinished, evidence and artifacts, and the requested next decision.
Account for every required worker outcome; a dropout or missing check is not a pass.

## Native tracking and continued execution

When the user explicitly requests native goal tracking, use it if exposed by
the current host and follow its lifecycle and budget instructions. Keep native
state consistent with the actual outcome. Without native tracking, pursue the
same outcome through ordinary work and task records. If requested tracking or
unattended continuation is unavailable, report that limitation and continue
useful authorized work without claiming the missing capability.

An instruction to persist guides an active run; wakeups and continued execution
need runtime support. Use the host's supported continuation mechanisms within
the request's authorization. This skill alone creates no recurring schedule
or separate top-level conversation.
