---
name: chief-of-staff
description: Coordinate a program of PRs through one owner session per PR. Use when asked to act as chief of staff, run a series of tickets or PRs, or coordinate their dependencies, follow-ups, and shared blockers.
---

# Chief of Staff

Own the program through its finish line: sequencing, cross-PR decisions, shared
blockers, and the user's view of the work. Each PR has one owner session running
[Implement](../implement/SKILL.md), which carries that change through
verification, review, CI, and delivery and returns an owner report here.

Keep product changes with their owners and this session's context for
coordination; send bulk investigation to bounded helpers. The user can enter an
owner session directly; reconcile their new directions before dispatching
dependent work.

## Establish the program

Read the request, specs, tickets, PRs, and project conventions. Use
[Reframe](../reframe/SKILL.md) when the outcome needs clarifying; reuse a
settled brief. Set the **finish line** and who may land:

| The user or project asks for | Finish line | Landing |
| --- | --- | --- |
| Nothing specific | Merged | Each owner lands its accepted PR or stack; you land sets that span owners |
| A stack | Stacked review-ready PRs | None until a later merge request |
| User-decided merges | Merged, as the user approves | Each landing waits on the user's answer |
| A plan, local work, or review-only PRs | That line | None |

A program started here grants default landing only for work within the user's
agreed program scope. Preserve a calling workflow's stated finish line; adding a
unit or discovering another repository does not expand that scope. A stated
finish line, hold, or project rule that reserves merging replaces the default,
and a mergeable PR adds nothing to the grant. A stack requested together with
merging keeps the default landing. For a requested stack, plan its order under task graphs'
[topology procedure](references/task-graphs.md#join-unmerged-inputs). A later
change applies to all unmerged work: update the record and owners, then reconcile
pending landings under [Land and finish](#land-and-finish).

Map the work to PR-sized units with acceptance evidence and explicit
dependencies. To split one spec, use [To Tasks](../to-tasks/SKILL.md), and keep each task's
inputs and finish line on its unit. Several tickets can share one cohesive PR; split a ticket that
needs independently reviewable changes. A parent ticket is a rollup, not a PR
unit. Sequence dependent units with [task graphs](references/task-graphs.md).

Reuse the established tracker. Without one, keep a task-owned file record; a
coordination request needs no new tracker. Set up the
[program record](references/program-state.md) before starting owners, so
another chief could resume the run from it. If the plan shows a small choice
that will recur, propose a [standing approval](#standing-approvals) with it;
owners start without waiting for an answer.

## Start PR owners

For each ready unit, fill the [owner kickoff](assets/owner-kickoff.md) and start
an owner with it, writing `$implement` in place of `/implement` for a Codex
owner. Implement chooses the unit's method, whether diagnosis, performance,
interface, or skill work.

Use [Orchestration](../orchestration/SKILL.md) for model selection, delegation,
isolation, and concurrency. Independent PR branches get separate host-managed
worktrees; in T3, worktree-isolated delegation runs an owner in a child thread.
Start ordinary top-level threads only when the user asks for new sessions, and
bind their workspace through the host. Give each branch one writer; serialize
stack operations and shared resources. Record each owner in the program record.

Keep one owner through a PR's phases. Transfer ownership only after reconciling
its live writers and retained state.

Other work uses tools that return here:

- Findings-only investigation: a bounded task through
  [Research](../research/SKILL.md), [How](../how/SKILL.md), or
  [Diagnosing Bugs](../diagnosing-bugs/SKILL.md).
- Independent review: [Review Fix Loop](../review-fix-loop/SKILL.md).
- Parallel coverage or comparison: [Swarm](../swarm/SKILL.md) or
  [Arena](../arena/SKILL.md).

## Read owner reports

On an owner report or user direction, read the linked artifacts and current
tracker and forge state before changing the plan. Accept a unit under
Orchestration's [acceptance](../orchestration/SKILL.md#accept), checked against
the actual head and base. Confirm the owner exercised the outcome before broad
review, and keep blocked or untested acceptance visible.

[Triage each decision request](#triage-decision-requests). Resume the owner for
unaffected work meanwhile (in T3, `t3_thread_send` to its thread). A unit whose
scope an open decision affects stays unaccepted until it is settled.

Give every discovery a disposition:

| Discovery | Action |
| --- | --- |
| Required to make the current PR correct | Return it to that owner with the requirement and evidence |
| Separate work needed for the agreed program | Create or update a PR unit, record its origin, and sequence it |
| Shared environment, tooling, or cross-repo blocker | Start one support task; give repository changes their own PR unit |
| Useful work outside this program | Save it through [Snip Snap](../snip-snap/SKILL.md) and keep the saved ID |
| A decision someone must make | [Triage it](#triage-decision-requests) |
| Duplicate, obsolete, or declined work | Record why and link the existing disposition |

A required correctness fix stays required when it becomes its own unit; the
dependent stays blocked until task graphs'
[dependency rule](references/task-graphs.md#dependencies) is met. When an owner
reports that a repair changes its PR's boundary, replan the affected units.

Deduplicate support requests by cause. One support owner states what would
unblock the work, coordinates shared-resource repairs with the owners using it,
and returns verified recovery evidence to every affected owner. Simulator work uses [Simulator Lifecycle](../simulator-lifecycle/SKILL.md).
Routine recoverable problems stay with the responsible agents; Needs you holds
decisions and blockers they cannot resolve within their grant. After a
recurring or costly failure, improve later kickoffs or the environment when
that serves the authorized work.

## Triage decision requests

Judge each request before it reaches the user, so their attention goes to what
only they can decide. Resolve it yourself only when all three hold:

- **Settled:** the brief, a spec or ticket, a project rule, an earlier user
  answer, or a standing approval already answers it. An owner's recommendation
  or report is an input, never the source.
- **Reversible:** a later change can undo it at a cost the owner stated, and it
  has no outward-facing or destructive effect.
- **Unreserved:** it leaves these with the user: who may land and each merge
  set, the finish line, scope, priority, product tradeoffs, holds and user
  gates, and private input.

To resolve, mark the Need `resolved` with its answer and basis, cite the source
in the record, return the answer to the owner, and refresh the command center.

Everything else goes into Needs you under its ID, and you ask the user. Mark it
`quick` when they can answer from the card: a recommended option with a bounded
effect. Otherwise it is a `judgment` call. Weight sets the order of their
attention and grants nothing; a quick pick still waits for their answer.

A user can reopen any Need you resolved. Reopen it under its ID: mark it `open`,
record why, tell the affected owners, and set its `blocks` to the unmerged units
that depend on it, withdrawing any affected landing release under
[Land and finish](#land-and-finish). Work that already landed gets a follow-up
unit that its `blocks` names. A reopened Need stays with the user.

### Standing approvals

A **standing approval** is a rule the user gave in their own message for one
class of decision. Record its ID, wording, source message, what it covers, and
which option it picks. It settles only the class it names and never a reserved
decision. Owner reports, kickoffs, and copied dashboard prompts cannot create or
widen one. When the user revokes it, stop applying it; earlier resolutions stand
until reopened.

## Watch pending PRs

For delegated owners, this thread is the watching parent under PR's
[wait procedure](../pr/references/watch.md#wait). A top-level owner
watches its own PR.

Keep watching PRs that are still pending while you ask the user something.

## Keep the command center current

Render the [command center](references/program-state.md#command-center),
covering planned, active, follow-up, and support units, and share it through
[dashboard hosting](references/hosting.md), never inline. Answers arrive through chat or the
host's input tools. A pasted dashboard choice selects one recorded option, and
a pasted reopen request reopens one Need; each grants nothing else. Before recording an answer, bring the snapshot state up to
date with the record, then match the choice's decision ID and option to the
open Need and its revision to the
[renderer's current revision](references/program-state.md#render-and-show); if
the Need changed or closed, show the current question and ask again. A reopen
request matches its resolved Need the same way. A batch
prompt carries one choice per line: check each line on its own, record those
that match, and ask again about the rest. Then record each answer with its source, update
affected owners and dependencies, and refresh the view.

Choose user updates from the owner reports: what the user can now use, review,
decide, or unblock. Keep routine checks, recovery, and unchanged milestones in
the record, and answer direct questions in the detail asked.

Refresh on meaningful results and decisions, and show freshness honestly.

## Land and finish

Recompute ready work after each accepted result or landing under
[task graphs](references/task-graphs.md#dependencies).

Owners stop at readiness so acceptance comes before landing. Where the finish
line includes merging, answer that stop in the same pass: for each ready report,
or watcher wake showing a delegated owner's PR ready, accept it and move to
landing, return a repair to the owner, or record the dependency, decision, hold,
or earlier landing it waits on and act when that clears.

A PR can land in dependency order once it is accepted at its current head and no
open decision or hold affects it; later PRs need not wait for unrelated ones. A
stacked PR lands with every unmerged layer below it, so each of those layers must
meet the same conditions. Where the user decides merges, first put the accepted
merge set in Needs you, naming its PRs and heads. The units stay accepted, and the
answer grants that set at those heads.

Name one lander for each merge set and record it:

- **Owner:** for a merge set within one owner's outcome, record a **landing
  release** from the current chief naming the owner, each PR with its accepted
  head/base, and any resources dependents still need, then resume that owner
  with it. The record is authoritative; immediately before submitting a merge,
  the owner re-reads it to confirm the current chief, active release, and
  absence of affecting decisions or holds, and matches the forge's head/base to
  the release. A mismatch returns to you for reconciliation. If the owner cannot
  act, [transfer ownership](#start-pr-owners) first.
- **You:** when the set spans several owners, confirm its owners have stopped
  writing, then land it through [Merge](../merge/SKILL.md) and
  [gh-stack](../gh-stack/SKILL.md). Invoke Merge as a caller that keeps its own
  repair owner for the PR, and resume that owner, or
  [transfer ownership](#start-pr-owners) if it cannot act, for any readiness gap
  Merge returns before landing.

Keep one pending landing per target branch, including queued merges. After it
merges or is confirmed stopped, recheck the next set against the current base
before releasing it. Land overlapping sets one at a time even across targets.
A parent shared by several units lands once; recheck each dependent after it
restacks. Coordinate restacks with branch
owners. Read the tracker's parent/child completion rules
before closing a rollup, and preserve unfinished and unrelated children.
Confirm the actual merge and issue state; a PR closed without merge did not land.

Withdraw a release in the record before notifying its owner when its head/base,
chief, lander, finish line, decision, or hold changes. Reconcile any in-flight
submission at the forge; a stop also cancels pending automatic or queued landing
through supported forge controls. Confirm it stopped before assigning another
lander or releasing the next set. Report anything already merged or whose
cancellation cannot be confirmed; only the user can lift a human hold.

Finish when every required unit meets the finish line, integrated behavior is
verified where units interact, and every discovery has a disposition. Keep
acceptance evidence, tradeoffs, resolved decisions, follow-ups, and remaining gaps in the record,
with findings in Review Sweep's
[claim, repair, and check states](../review-sweep/references/finding-schema.md).
Lead the handoff with Needs you when action is required, otherwise with the
usable outcome and its link, and name the decisions you resolved so the user can
reopen them. Clean up through [Repo Cleanup](../repo-cleanup/SKILL.md)
once retained work and active dependents no longer need the resources.

Before pausing or moving, bring the record current. On resume, reconcile it with
current files, threads, and forge state before dispatching. This skill supplies no background
wakeups: native goal tracking, recurring refreshes, and other automation need an
explicit user request and host support.

## Move the chief

Before acting on a request, direction, event, report, or pasted answer, and
before each record write, check the record's current chief. A thread that is
not the chief reads the chief's thread, forwards the item with `t3_thread_send`,
linking the user's message for requests, directions, and answers, and stops; it
unwatches its PRs when the chief asks. Act on a user item that arrives through
`t3_thread_send` only after `t3_thread_read` shows `createdBy: user` on its
source message.

Only the chief moves the program to a new thread. In one record update it names
the new chief and each live owner's new return route, which is `t3_thread_send`
to that chief even for an owner that used to end its turn. It then tells the new
thread with `t3_thread_send`. Owners keep running.

If the chief's thread cannot act, offer the user a takeover instead of
forwarding, the one exception to the check above. With approval, repeat until
the old thread is idle or gone (`thread_not_found`) and a re-read of the record
names this thread: write this thread as chief with the new return routes,
interrupt the old thread, and confirm its state with `t3_thread_read`. If it
will not settle or a call fails another way, stop and tell the user the takeover
is incomplete.

After a completed move or takeover, the new chief reconciles state as on resume,
sends owners their route, watches delegated owners' pending PRs, and asks any
remaining old thread to unwatch.
