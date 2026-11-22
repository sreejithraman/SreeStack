---
name: implement
description: Use when asked to implement a spec, ticket, task, or feature, deliver a change as a PR or stack, or pursue a measurable target until it is met. Excludes multi-outcome program coordination (coordinator) and read-only research or review.
---

# Implement

Carry one outcome to its finish line as one PR or a planned stack. Start from a brief, spec,
task, ticket, or clear request. Leave merged work for **Land**, something inspectable for **Try**,
or a PR at its requested state, plus a report for your caller. You are done when the finish line's
gates pass, the user can open what you showed, and the report is delivered.

Edit your workspace directly by default. Use [Orchestration](../orchestration/SKILL.md#who-does-the-work)
only when delegating independent review or verification, parallel fan-out ([Swarm](../swarm/SKILL.md)),
a specialized model, or background work the user requested. Each linked skill owns its own procedure.
Scale checks to the change; Land's merge requirements always apply in full.

## 1. Resolve one outcome

Read the request, accepted corrections, any brief, spec, ticket, or program record supplied,
project instructions, the code, and its checks. A brief supplements its sources and adds no
requirements; reuse a settled brief. Use [Reframe](../reframe/SKILL.md) only for what is unsettled.
Ask when a ticket reference is ambiguous; a supplied spec needs no tracker. When the user is your
caller and the direction is too rough to build, offer [Shape](../shape/SKILL.md).

Resolve the repository, base, branches, available inputs, covered code, and behavior to preserve.
Split PRs only for reviewability, never to manage context; several tickets can share one PR when
they form one reviewable change.

**Multiple outcomes:** when the work splits into several independent outcomes, return the proposed
outcomes to a session caller, or route a user caller to [Coordinator](../coordinator/SKILL.md):
- If the request itself is several outcomes (especially 3+, cross-dependent, or async), offer
  Coordinator and wait before starting them.
- If extra outcomes emerged while building one requested outcome, finish the requested one and
  leave the rest to the offer.

Done when the outcome, covered code, preserved behavior, proof, inputs, caller, and holds are known.

## 2. State the finish line and prepare

Pick the finish line from the idea, not the work type. A finish line, hold, or project rule from
the user, caller, or project wins. When the user is your caller and did not specify one, state your
pick in your first message so they can override it in one word:

| Finish line | Pick when | Ends at |
| --- | --- | --- |
| **Land** | Settled (user knows what they want, or checks can judge it) and reversible | Merged via [Merge](../merge/SKILL.md) and shown |
| **Try** | Idea is taking shape, complicated, hard to undo, or uncertain | Built, proved, and shown — stopped before review and PR |
| **PR** | User or caller asks for a PR state (review-ready or draft) | That state via [PR](../pr/SKILL.md) |

Land picked under this policy is the merge request Merge needs; approving an outline or plan grants
no landing. Destructive, outward-facing, or hard-to-reverse actions stop for the user regardless of
finish line. Performance work lands only when before-and-after numbers meet the target with no
regression.

Before running unattended:
- **Access:** confirm tools, logins, and accounts work via [Agent Login](../agent-login/SKILL.md)
  (setup requires user request). Record missing prerequisites and continue unaffected work.
- **Showing:** capture pre-change baselines for screens or metrics via [Show Me](../show-me/SKILL.md).
- **Layers:** plan known stack order via [stack design](../gh-stack/references/stack-design.md).
- **Provisional work:** if this work rests on another owner's unmerged branch or an open decision,
  read [provisional work](references/provisional.md).

Done when the finish line is set, required access works or its block is recorded, baselines exist,
and any provisional assumptions are named.

## 3. Build and integrate

Use [TDD](../tdd/SKILL.md) at meaningful behavior seams for features and repairs, checking small
units as they become usable. On shared Macs with Mac Work configured, route qualified heavy builds
and tests through [Mac Work](../mac-work/SKILL.md).

Keep cohesive work with one writer; use Swarm only for bounded independent
slices or races. Pushing, rebasing, retargeting, and merging stay with you unless explicitly
serialized.

- **Hard measurable targets:** read [target pursuit](references/target-pursuit.md).
- **Repeated invariant breaks:** when successive fixes break the same ownership, ordering, or state
  invariant, stop varying local guards and run
  [Attack the Premise](../engineering-principles/references/attack-the-premise.md). Keep the
  counterexamples; report boundary or dependency changes to your caller.

Done when all layers are built, helper results are accepted and integrated, and relevant checks pass.

## 4. Prove and show

Before any review, prove the outcome through its real entry points with [Verify](../verify/SKILL.md).
Required proof must pass at the current head of each layer; a failed, blocked, or untested
assertion is a gap, and review cannot supply unobserved proof.

Show the work with Show Me when it first works, when a visible result
changes, and at every stop.

Done when required assertions pass (or exact gaps are reported) and the user can open what you showed.

## 5. Reach the finish line

- **Try:** stop before review and PR (run [Review Fix Loop](../review-fix-loop/SKILL.md) only if
  asked). Show the result. For a user caller, ask through the host's question tool: merge, changes,
  or scrap (`/merge` goes to Merge; changes return to stage 3; scrap goes to
  [Cleanup](../cleanup/SKILL.md)). For a session caller, return the Try result and choice.
- **PR:** publish and watch to the requested state via PR.
- **Land:** land via Merge (stacks bottom-up as one merge set).

An open decision affecting scope blocks landing; provisional work follows the provisional
work reference and never merges (`Land` becomes `Try`). Coordinate
cross-layer stack changes via [gh-stack](../gh-stack/SKILL.md). When a session caller supplies a
kickoff, grant, report format, or landing-release rule, follow it: run your own review loop, stop
at readiness when landing requires caller release, and land only on that release.

## Keep scope and decisions

**Scope only shrinks.** You or your caller may split, defer, or create a follow-up without asking;
nobody grows a PR's scope or asks the user to. Apply
[Review Sweep's scope boundary](../review-sweep/references/classification.md#scope-boundary) to
decide what fixes in place versus defers.

Route every deferred finding or out-of-scope discovery returned by review, PR feedback, or building
to a real durable home before finishing — never leave a deferral as unbacked prose:

| Caller & work | Goes to |
| --- | --- |
| Session caller (program or parent workflow) | Structured `Follow-ups` in your caller report; send a partial report immediately when impact is `shared-contract` or `requested-scope` |
| User caller — related and helped by this session's context | Follow-up PR from this session (or tracked issue if not built now) |
| User caller — independent | Tracked issue or separate session offered to the user |
| User caller — useful but unrelated | [Snip Snap](../snip-snap/SKILL.md) (keep the saved ID) |

Handle `Stops` returned by review or PR steps by caller: decide reversible implementation-design
choices yourself and note them; escalate scope, irreversible, taste, and caller-reserved stops
through [Orchestration's return rules](../orchestration/SKILL.md#return) for a session caller (or
ask a user caller directly). When the user gives direction inside a caller-owned session, record it
and report scope, dependency, or acceptance changes back to the caller.

## Report

For a user caller, lead with what they can use, what needs their action, links, verification
status, routed follow-ups (with IDs/links), and any remaining gaps (a Land report ends at what
landed). For a session caller — or when pausing, transferring, or being adopted — follow
[caller report and handoff](references/caller-report.md).
