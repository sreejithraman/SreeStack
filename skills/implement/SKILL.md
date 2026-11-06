---
name: implement
description: Own one PR-sized change from spec or ticket through implementation, verification, review, and its finish line. Use when asked to implement a spec, ticket, or feature, to deliver a change as a PR, or to keep pursuing a measurable target until it is met.
---

# Implement

Own one cohesive change through its finish line. You are its only owner:
helpers return to you, and you return one **owner report** to your caller (the
user, or the session that started you). Scale the process to the change; a
small local fix needs its relevant checks, not every step below.

## Resolve the assignment

Read the spec or ticket, the original request and accepted corrections, any
brief and program record you were given, project instructions, existing code,
and authoritative checks. A brief supplements its sources; it adds no
requirements of its own. Resolve the repository, intended base, owned branch
and files, available dependencies, preserved behavior, and an ambiguous ticket
reference before changing anything.

Use Reframe's [acceptance guidance](../reframe/references/acceptance.md)
to name the user-visible result, the invariants that must hold, and the
observations that would establish them. Strengthen checks as discovery reveals
risks; a complete harness is not a prerequisite for useful work.

Set the **finish line** from the request and project conventions: local
changes, a prepared or published PR, or merged. A request to implement
authorizes implementation and its checks; publishing and merging follow an
actual request. Several tickets can share this PR when they form one cohesive
change. When the work needs several independently reviewable PRs, keep what is
done and return the proposed PR split under Deferred; for a user caller, suggest
[Chief of Staff](../chief-of-staff/SKILL.md).

Choose the method: [Diagnosing Bugs](../diagnosing-bugs/SKILL.md) for a defect
or performance regression, the relevant platform and design skills for
interface work, and [Writing for Agents](../writing-for-agents/SKILL.md) for
skills and agent procedures. For a requested or planned before/after UI
comparison, read Show Me's [capture guidance](../show-me/references/captures.md)
and keep a matching real baseline before changing the UI or its state.

## Build and prove

Use [Orchestration](../orchestration/SKILL.md) for model selection and any
delegation. Keep cohesive work direct; use [Swarm](../swarm/SKILL.md) for
bounded parallel coverage, experiments, or disjoint implementation. Pushing,
rebasing, retargeting, and merging this PR stay with you unless you assign one
explicitly and serialize it.

Use [Engineering Principles](../engineering-principles/SKILL.md) for
consequential design choices and [TDD](../tdd/SKILL.md) at meaningful behavior
seams. Verify small units as they become usable, run the project's relevant
checks, and use [Verify](../verify/SKILL.md) for the workflow the user will
actually use. For performance, measure the bottleneck and compare the same
workload before and after.

Pursue a measurable target relentlessly. A correct improvement that misses the
target is progress: keep it and change approach while the target stays fixed.
Choose each next attempt from what the last one established; an equivalent
retry is not a new attempt. Explore uncertain approaches reversibly, and reach
for original inputs, stronger instruments, or methods from other fields when
they can close the gap. Reject regressions in required behavior even when the
headline number improves. When evidence shows a limit that needs a tradeoff,
report it as a decision request. Keep accepted progress, remaining gap,
and the next attempt where a resumed session can find them. Use native goal
tracking or scheduled
continuation only when the user requests it and the host supports it.

When successive repairs keep breaking the same ownership, ordering, or state
invariant, stop varying local guards and use
[Attack the Premise](../engineering-principles/references/attack-the-premise.md).
Keep the counterexamples. If the fix changes this PR's boundary or its
dependencies, report it to the caller; the correctness requirement stays
blocking while the work is replanned.

## Keep scope and decisions

Fix what this PR needs to be correct. Report a separate improvement in the
owner report with its origin, evidence, suggested destination, and whether it
blocks this PR. With no session caller, save it through
[Snip Snap](../snip-snap/SKILL.md).

Return decisions and shared-resource or cross-repo blockers through
Orchestration's [return](../orchestration/SKILL.md#return) as they arise; ask
the user directly when they are your caller. When the user gives direction
directly in this session, record it and report changes to scope,
dependencies, or acceptance to the caller.

## Review and deliver

Before broad review, exercise the requested outcome through its real entry
points and keep the evidence. An unavailable required check is blocked or
untested; review can probe risk but cannot supply an unobserved result.

[PR](../pr/SKILL.md) owns preparation, publication, CI, and feedback for a PR
finish line. For local behavior or procedure changes, use
[Review Fix Loop](../review-fix-loop/SKILL.md). Reuse matching coverage so the
same scope is reviewed once. Settle findings through Review Sweep's
[claim, repair, and check states](../review-sweep/references/finding-schema.md);
prefer a reproduction where feasible and keep precise source or contract
arguments where execution is hard. Recheck evidence affected by fixes or base
changes. Review repairs and babysitting stay with you.

For a pending PR, follow PR's [wait procedure](../pr/references/ci.md#wait-for-events):
a delegated owner returns its pending report and lets the parent watch.
Merge only within the assignment's authorization, with no open decision
request on this PR's scope, through [Merge](../merge/SKILL.md). Coordinate stack changes affecting other layers
with the caller and [gh-stack](../gh-stack/SKILL.md). Only a confirmed merge
lands the change; a closed PR did not.

Use [Show Me](../show-me/SKILL.md) to make the result inspectable, then
return the owner report.

## Owner report

Return these fields to the caller, omitting none that apply:

- **Result:** PR or local artifact link, head and base, working-tree state.
- **Acceptance:** evidence per requirement, and what remains blocked or untested.
- **Delivery:** the actual state (local, PR open, ready, merged) against the finish line.
- **Pending:** a PR's pending report, live helpers, and waits.
- **Decisions:** open decision requests with their IDs.
- **Deferred:** each separate item with its destination or open disposition.
- **Sources:** follow-up messages received and handled.

Write the full report to the path the caller gave, marking a partial report
as partial, or put it in your final message when you cannot write there.
Write nothing else in a caller's records. A summary for the user leads with what they can use, what needs their
action, and limits that matter.

When the user asks to pause or transfer, write the PR's state through
[Handoff](../handoff/SKILL.md). A replacement owner reconciles the branch and
live writers before taking over the same PR.
