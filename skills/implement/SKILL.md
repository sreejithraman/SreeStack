---
name: implement
description: Use when asked to implement a spec, ticket, task, or feature, to deliver a change as a PR or stack, or to keep pursuing a measurable target until it is met.
---

# Implement

Carry one outcome to its finish line. Start from a brief, spec, task, ticket, or
clear request. Leave merged work for **Land**, something to try for **Try**, and
an owner report for your caller: the session that started you, or the user in a
top-level thread. You
are done when the finish line's gates pass, the user can open what you showed,
and the report is delivered.

You own the outcome, the finish line, the order of handoffs, integration, scope,
and the report. Each linked skill owns its own procedure. Helpers return to you.
In a top-level thread, a subagent writes the change under Orchestration's
[who does the work](../orchestration/SKILL.md#who-does-the-work); a child writes
it itself. Scale building and proof to the change: a small local fix needs its
relevant checks, not every handoff below. Land's merge requirements always
apply in full.

## 1. Resolve one outcome

Read the request and accepted corrections, any brief, spec, ticket, or program
record you were given, project instructions, the code, and its authoritative
checks. A brief supplements its sources and adds no requirements. Reuse a
settled brief. Use [Reframe](../reframe/SKILL.md) only for what is unsettled:
the outcome, its proof, preserved behavior, or the finish line. Ask when a ticket
reference is ambiguous; a supplied spec needs no tracker.

Before changing anything, resolve the repository, base, branches, available
inputs, and the behavior to preserve. Record the code the outcome covers; scope
decisions use that list.

One outcome ships as one PR or as a planned stack from you. Split PRs by
reviewability, never to manage context. Several tickets can share a PR when they
form one reviewable change. Several layers alone are no reason to promote.

When the work is several outcomes that need coordinating, promote it. A session
caller gets the proposed outcomes back. A user caller gets an offer of
[Chief of Staff](../chief-of-staff/SKILL.md):

- **The request itself is several outcomes:** offer Chief of Staff and wait for
  the answer. Start none of them.
- **The work grew from one requested outcome:** keep building that outcome while
  the offer waits. Start none of the new ones.

Done when the outcome, covered code, preserved behavior, proof, inputs, caller,
and holds are known.

## 2. State the finish line and prepare

Pick the finish line and state it in your first message, so the user can
override it in one word:

| Finish line | Pick it when | It ends |
| --- | --- | --- |
| **Land** | The work is settled (the user knows what they want, or checks can judge it) and reversible | Merged through [Merge](../merge/SKILL.md), and shown |
| **Try** | The idea is still taking shape, is complicated or hard to undo, or you are unsure | Built, proved, and shown, stopped before review and the PR |
| **PR** | The user or caller asks for a PR state, such as review-ready or draft | At that state, through [PR](../pr/SKILL.md) |

Choose by the idea, not the type of work. A finish line, hold, or project rule
from the user, caller, or project wins over your pick. Performance work lands
only when before-and-after numbers meet the target with no regression. Land
picked under this policy is the merge request Merge needs; approving an outline
or plan grants no landing by itself. Destructive, outward-facing, or
hard-to-reverse actions stop for the user whatever the finish line.

Prepare before work runs unattended:

- **Access:** confirm the build and proof have the tools, logins, and accounts
  they need, through [Agent Login](../agent-login/SKILL.md). Its setup route
  needs the user's request.
- **Showing:** plan the captures. Before you change a screen or anything you'll
  measure, capture the baseline with [Show Me](../show-me/SKILL.md).
- **Layers:** when the stack's order is known, plan its layers with gh-stack's
  [stack design](../gh-stack/references/stack-design.md).

When something is missing, record the exact block: what is missing, who can
supply it, and what it blocks. Continue with the work that doesn't need it.

Work is **provisional** when it rests on something you don't control: another
owner's unmerged branch or PR, or a recorded assumption awaiting a decision.
Your own planned layers are not provisional; Land lands your stack bottom-up
through Merge. Name the branch or assumption provisional work rests on. It can
build and prove, and is reviewed only when the caller asks for review or a PR.
Provisional work never merges and never crosses into destructive or
outward-facing actions on your own initiative. The user's explicit scrap of this
outcome allows only its scoped cleanup through Repo Cleanup: its branch, PR, and
worktree; work built on it still gets its own choice. Land becomes Try, but a
requested PR state, draft or review-ready, can still be reached. Publish a
provisional PR with the **Provisional** section from PR's
[body guide](../pr/references/pr-body.md); that section is where its status
lives, and you remove it only after its condition is met and affected proof is
refreshed. If its base changes, restack and recheck it. If its base is scrapped,
offer it for scrap too.

Done when the finish line is stated, required access works or its block is
recorded, needed baselines exist, and every provisional assumption is named.

## 3. Build and integrate

Choose the method by the work: [Diagnosing Bugs](../diagnosing-bugs/SKILL.md)
for a defect or performance regression, [TDD](../tdd/SKILL.md) for features and
repairs at meaningful behavior seams, [UI Design](../ui-design/SKILL.md) and
the platform skill, such as [SwiftUI](../swiftui/SKILL.md) or
[UIKit](../uikit/SKILL.md), for interface work, [Writing for Agents](../writing-for-agents/SKILL.md) for skills
and agent instructions, and
[Engineering Principles](../engineering-principles/SKILL.md) for consequential
design choices. Check small units as they become usable, and strengthen checks
as you discover risks; a complete harness is not a prerequisite for useful work.

Use [Orchestration](../orchestration/SKILL.md) for model choice, delegation, and
accepting helper results, within your caller's delegation allowance. Keep
cohesive work with one writer. Use [Swarm](../swarm/SKILL.md) for bounded
parallel coverage, experiments, or disjoint implementation. Pushing, rebasing,
retargeting, and merging stay with you unless you assign them explicitly and
serialize them.

**Pursue a hard target relentlessly.** A correct improvement that misses the
target is progress: keep it, and change approach while the target stays fixed.
Choose each attempt from what the last one established; an equivalent retry is
not a new attempt. Explore uncertain approaches reversibly, and reach for
original inputs, stronger instruments, or methods from other fields when they
can close the gap. Measure through Reframe's
[acceptance guidance](../reframe/references/acceptance.md). Reject regressions in
required behavior even when the headline number improves. When evidence shows a
limit that needs a tradeoff, return it as a decision request. Keep accepted
progress, the remaining gap, and the next attempt where a resumed session can
find them. Use native goal tracking or scheduled continuation only when the user
asks and the host supports it.

**When repairs keep breaking the same ownership, ordering, or state invariant,**
stop varying local guards and use
[Attack the Premise](../engineering-principles/references/attack-the-premise.md).
Keep the counterexamples. If the fix changes the outcome's boundary or its
dependencies, report it to the caller. The correctness requirement stays
blocking while the work is replanned.

Done when the outcome is built across its layers, helper results are accepted
and integrated, and the project's relevant checks pass.

## 4. Prove and show

Before any review, prove the outcome through its real entry points with
[Verify](../verify/SKILL.md). Required proof must pass: a failed, blocked, or
untested assertion is a gap, not success, and review cannot supply an
unobserved result. Proof covers the current head of each layer, so rerun what
later fixes or base changes affect.

Show the work with [Show Me](../show-me/SKILL.md) when the first version works,
when a visible result changes, and at every stop, not only at the end.

Done when every required assertion passed on the current result, or its gap is
reported as a gap, and the user can open what you showed.

## 5. Reach the finish line

- **Try:** stop before review and the PR; run
  [Review Fix Loop](../review-fix-loop/SKILL.md) here only when the request asks
  for review. Show the result. When the caller is the user, ask through the
  host's question tool: merge, changes, or scrap. Otherwise return the Try
  result and that choice through the caller's recorded route; a chief's
  acceptance and release stay the landing gate. `/merge` in this thread means
  keep: go to Merge, which runs review, opens the PR, and lands it. Changes go
  back to stage 3. Scrap goes to [Repo Cleanup](../repo-cleanup/SKILL.md).
- **PR:** PR runs review, publishes, and watches to the requested state.
- **Land:** go to Merge; a stack lands bottom-up as one merge set. Until hard
  gates exist, Merge's requirements are the gate: review of the current head,
  required checks, and passing proof. Land is done when GitHub reports every PR
  merged and the result is shown. A closed PR did not land.

Provisional work never merges: Land becomes Try, and a requested draft or
review-ready PR state is still reached through PR, with its body's
**Provisional** section open until the condition clears. An open decision
request on this outcome's scope blocks landing. Coordinate stack changes that
affect other layers with the caller and [gh-stack](../gh-stack/SKILL.md). Repairs go to the slice's owner
under Orchestration's [who does the work](../orchestration/SKILL.md#who-does-the-work).

**Under a chief,** stop at readiness and return it for acceptance. Land only on
the chief's recorded release, as the kickoff describes: you land your own PR or
stack, and the chief lands sets that span several owners. The record names
exactly one lander.

**While a PR is pending,** follow PR's [wait](../pr/references/watch.md#wait).
A top-level owner watches its own PR. A delegated owner returns a pending report
and lets its parent watch; it doesn't claim completion.

## Keep scope and decisions

Fix what the outcome needs to be correct. Route work that leaves it, each item
with its origin, evidence, and its own Land or Try finish line:

| Work is | Goes to |
| --- | --- |
| Related, and helped by this session's context | A follow-up PR from this session |
| Independent | A separate session, offered to the user or returned to the caller |
| Part of a chief's program | The chief, who picks the route |
| Useful but unrelated | [Snip Snap](../snip-snap/SKILL.md) |

Never grow the current scope silently.

Return decisions and shared or cross-repo blockers through Orchestration's
[return](../orchestration/SKILL.md#return) as they arise; ask the user directly
when they are your caller. When the user gives direction in this session, record
it and report changes to scope, dependencies, or acceptance to the caller.

## Report

Send a partial report as soon as you hit a missing prerequisite, a human
decision, or a pending PR. Name what continues meanwhile and the event that
resumes the rest. Partial means partial.

The owner report carries every field that applies:

- **Outcome and finish line:** the line you picked and why, and the actual
  delivery state against it.
- **Layers:** each PR, branch, or local artifact, with its link, head, base,
  revisions, and working-tree state.
- **Proof:** each required assertion's verdict and evidence, and what is blocked
  or untested.
- **Shown:** what you showed and how to open it, with what it needs, such as a
  login or a running server and its stop action.
- **Waits:** pending PRs, live helpers and watchers, and the events they await.
- **Decisions:** open decision requests with their IDs, and each provisional
  assumption with what depends on it.
- **Follow-ups:** each routed item, with its destination and finish line.
- **Sources:** follow-up messages received and handled.

Write the full report to the path the caller gave, or put it in your final
message when you can't write there. Write nothing else in a caller's records.
For the user, lead with what they can use, what needs their action, and limits
that matter. A Land report ends at what landed.

## Pause, transfer, or adoption

When the user asks to pause or transfer, write the state through
[Handoff](../handoff/SKILL.md). When a chief adopts this session, keep running:
take the report path and route it gives, and send your current state there.
A replacement owner reconciles the files and branches, live writers, helpers and
watchers, evidence, decisions and holds, any armed landing, and the caller route
before it writes. It never runs as a second writer beside the old one.
