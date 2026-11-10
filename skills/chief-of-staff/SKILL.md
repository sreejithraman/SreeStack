---
name: chief-of-staff
description: Use when asked to act as chief of staff, carry several outcomes, tickets, or PRs to their finish lines, or coordinate their dependencies, follow-ups, and shared blockers.
---

# Chief of Staff

Carry several outcomes to their finish lines through
[Implement](../implement/SKILL.md) owners. Start from any set of work: a spec, a
list in chat, saved snips, follow-ups, tickets, existing PRs, or an Implement
session whose work grew. Leave each outcome landed, stopped for the user, or
blocked with a recorded need, and leave the user a morning view of all of it.
You are done when every outcome is in one of those states and every integration
gap and follow-up has a route.

You own the program: its scope, who owns each outcome, dependencies and
scheduling, shared blockers, decisions and what each one blocks, integration
across outcomes, acceptance, landing releases, the program record, and the
morning view. Each owner carries one outcome, as one PR or its own planned
stack, and reports here. Each linked skill owns its own procedure. Keep product
changes with owners. Send findings-only investigation to a bounded task through
[Research](../research/SKILL.md), [How](../how/SKILL.md), or
[Diagnosing Bugs](../diagnosing-bugs/SKILL.md), and parallel coverage or
comparison through [Swarm](../swarm/SKILL.md) or [Arena](../arena/SKILL.md).
The user can enter an owner's session directly; reconcile their new direction
before you dispatch work that depends on it.

Only the record's current chief acts on program items and writes the record.
Check it before acting on a request, direction, report, event, or pasted answer;
a thread that is not the chief forwards the item under
[chief move](references/chief-move.md).

## 1. Establish or adopt

Read the request and accepted corrections, every source it names, project
conventions, and the current forge and thread state. Keep each source's ID. A
saved snip stays Not Done under Snip Snap's
[complete saved work](../snip-snap/SKILL.md#complete-saved-work) until its
outcome is verified. Use [Reframe](../reframe/SKILL.md) only for what is
unsettled, and reuse a settled brief. A spec is one input, not a requirement.
When the direction is too rough to cut into outcomes, offer the user
[Shape](../shape/SKILL.md).

Cut the work into outcomes. When one body of work holds several, split it with
[To Tasks](../to-tasks/SKILL.md) and keep each task's outcome, proof, inputs,
and finish line on its outcome. One outcome ships as one PR or a planned stack
from one owner. Tickets track work: several can share an outcome, and a parent
ticket is a rollup. Never split to manage context.

Find running owners and existing PRs before you assign anything. **Adopt** an
Implement session already carrying an outcome: send it the kickoff's program,
landing, report, and route lines, and let it keep running with its writer,
evidence, holds, watchers, and helpers. Record any landing it already armed as
its target's pending landing. Never start a second writer beside it; replace an
owner only under Orchestration's
[replace an owner](../orchestration/references/reuse-and-recovery.md#replace-an-owner),
after reconciling. When the stopped owner's worktree still holds its branch,
reuse that worktree through the host (in T3, `existing_worktree`) once it is
clean and holds no unique commits, or start the replacement on a new branch.

Pick each outcome's finish line from Implement's
[table](../implement/SKILL.md#2-state-the-finish-line-and-prepare) and state the
picks in your first message, so the user can override any one in a word. Land
picked under that policy authorizes merging that outcome within the agreed
program scope, and your [landing release](references/landing.md) still gates it.
A finish line, hold, or project rule from the user, a calling workflow, or the
project wins over the pick. One that reserves merges, such as "I decide each
merge", makes each landing wait on a Need. Adding an outcome or finding another
repository does not widen the scope, and a mergeable PR adds nothing to it. A
stack is a delivery shape, not a finish line. A later change applies to all
unmerged work: update the record and owners, then reconcile pending landings
under [withdraw a release](references/landing.md#withdraw-a-release).

Set up the [program record](references/program-state.md) before you start or
adopt owners, so another chief could resume from it. Work items stay in the
project's tracker, and a coordination request needs no new one. When a small
choice will recur, propose a
[standing approval](references/decisions.md#standing-approvals) with the plan;
owners start without waiting for the answer.

Done when each outcome has its sources, scope and covered code, proof, holds,
finish line, and owner or planned start, and every running owner is adopted.

## 2. Prepare and schedule

Start an outcome when it is [ready](../to-tasks/SKILL.md#ready), including To
Tasks' provisional start, and schedule by the
[dependency rules](references/dependencies.md). An outcome that waits never
holds up unrelated ones.

For each ready outcome, fill the [owner kickoff](assets/owner-kickoff.md) and
start an owner with it, writing `$implement` in place of `/implement` for a
Codex owner. Implement picks the method and runs its helpers as its own
subagents.

Running a chief of staff is a request for sessions: start each owner as its own
top-level session, so the user can open and steer it. Bind its workspace through
the host, never in the shell: in T3, `t3_thread_launch` with a `worktree`
`workspaceStrategy` for the owner's branch. When the host cannot launch
top-level sessions, as in a plain Claude Code or Codex session, start a
delegated owner in its own host-managed worktree instead. Use
[Orchestration](../orchestration/SKILL.md) for model choice and concurrency.
Give each branch one writer, and serialize stack operations and shared
resources. Record each owner with its start mode, route, and report path. Only
you start program owners.

Each owner checks its access and proof before work runs unattended, under
Implement's [prepare](../implement/SKILL.md#2-state-the-finish-line-and-prepare).
When work is blocked, keep it moving safely:

| Blocked on | Do |
| --- | --- |
| Another owner's unmerged work | Build on that branch as a [provisional base](references/dependencies.md#provisional-work) |
| A decision whose recommended option is reversible | Build on that option provisionally and keep the decision open |
| Two close options | Build both on separate branches when that costs less than waiting |
| A shared environment or tooling problem | Start one support task for the cause |
| A login or secret | Record an `access` Need and move to other work |

Secrets reach owners through the host's private input or
[Agent Login](../agent-login/SKILL.md), never chat.

Done when every ready outcome is running and every other outcome waits on a
recorded dependency, Need, or block.

## 3. Coordinate

On each owner report, user direction, or watcher wake, read the linked artifacts
and the current tracker and forge state before you change the plan. Record the
report under [owner reports](references/program-state.md#owner-reports).

[Triage each decision request](references/decisions.md#triage), and record the
outcomes it blocks with the phase each waits at. Meanwhile, resume the owner for
unaffected work (in T3, `t3_thread_send` to its thread).

Give every discovery a disposition:

| Discovery | Action |
| --- | --- |
| Required to make the current outcome correct | Return it to that owner with the requirement and evidence |
| Related work its owner's context helps | That owner's follow-up outcome, with its own finish line |
| Separate work the program needs | A new outcome with its origin, sequenced by dependency |
| Shared environment, tooling, or cross-repo blocker | One support task; a repository change gets its own outcome |
| Useful work outside the program | Save it through [Snip Snap](../snip-snap/SKILL.md) and keep the ID |
| A decision someone must make | [Triage it](references/decisions.md#triage) |
| Duplicate, obsolete, or declined work | Record why and link the existing disposition |

A required correctness fix stays required when it becomes its own outcome, and
its dependent waits under the
[dependency rule](references/dependencies.md#dependencies). When an owner
reports a repair that changes its outcome's boundary, replan the affected
outcomes.

Repairs go to the slice's owner under Orchestration's
[who does the work](../orchestration/SKILL.md#who-does-the-work). Deduplicate
support requests by cause: one support owner states what would unblock the work,
coordinates shared-resource repairs with the owners using them, and returns
verified recovery evidence to every affected owner. Simulator work uses
[Simulator Lifecycle](../simulator-lifecycle/SKILL.md). Routine recoverable
problems stay with the responsible agent; Needs you holds only what agents
cannot resolve within their grant. After a recurring or costly failure, improve
later kickoffs or the environment when that serves the program.

Check integration as results arrive, and have dependents restack and recheck
when a base changes, under [integration](references/dependencies.md#integration).
Recompute ready work after each accepted result, landing, answer, or dependency
change, and start what became ready.

A top-level owner watches its own PR and sends its reports, decision requests,
and blockers to this thread with `t3_thread_send`. It gives you no completion
wake-up, so after you start or message one, and before you end a turn with
owners outstanding, wait on each outstanding owner's run through the host (in
T3, `t3_thread_wait`, following its `next`). When a run ends, read the owner's
thread. Handle a sent report or request as usual. Reconcile a run that failed,
was interrupted, or went idle without a report or pending-PR partial: recover
it under Orchestration's
[recover work](../orchestration/references/reuse-and-recovery.md#recover-work),
or record the outcome blocked with what is missing. For a delegated owner, this
thread is the watching parent under PR's [wait](../pr/references/watch.md#wait).
Keep watching pending PRs while you ask the user something.

Done when every report, direction, and discovery has a disposition and newly
ready outcomes are running.

## 4. Accept and release

Accept each outcome under Orchestration's
[accept](../orchestration/SKILL.md#accept), against the current head and base of
every layer. The owner proves through real entry points before any review; keep
blocked or untested proof visible. An outcome stays unaccepted while an open
decision affects its scope. Try stops before review. Review runs when PR
publishes, or through [Review Fix Loop](../review-fix-loop/SKILL.md) only when
the user asks.

Answer each stop in the same pass:

- **Shown Try:** put its merge, changes, or scrap choice in Needs you under
  [Try choices](references/decisions.md#try-choices), and route the answer to
  the same owner. Merge makes its finish line Land, still gated by acceptance and
  release. Changes go back to the owner. Scrap goes to the owner's cleanup, and
  each dependent gets its own choice.
- **Requested PR state:** the outcome stops there for the user.
- **Ready to land:** accept it and [release its landing](references/landing.md),
  return a repair to its owner, or record the dependency, decision, hold, or
  earlier landing it waits on and act when that clears.

Provisional work never lands. Its owner keeps the PR body's `## Provisional`
section until the condition clears and the affected proof is refreshed, and
Merge stops on it.

Done when every outcome at a stop has a released landing, an open Need for the
user, its requested PR state, or a repair with its owner.

## 5. Show and continue

Host the [command center](references/program-state.md#command-center) through
[dashboard hosting](references/hosting.md), never inline. It renders
`program.json` each time it is opened, so every record write reaches it. It
shows every outcome once, with its finish line, results and how to open them,
provisional condition, owner, layers, and what each Need blocks. Results come
from owners' Shown reports: link what they showed, say what opening it needs,
and name the gaps. Keep each row's observation time honest.

Answers arrive through chat or the host's input tools. Record each under
[record an answer](references/decisions.md#record-an-answer), then update the
affected owners, dependencies, and releases before work resumes.

Choose user updates from the owner reports: what the user can now use, try,
decide, or unblock. Keep routine checks, recovery, and unchanged milestones in
the record, and answer direct questions in the detail asked.

Done when the hosted page serves the current `program.json` without an error
banner and shows every result and open Need.

## 6. Settle or resume

The program is done when every outcome has landed, stopped for the user at a
shown Try or requested PR state, or is blocked with a recorded need; integrated
behavior is verified where outcomes interact, or the gap is recorded; and every
discovery and follow-up has a route. Keep acceptance evidence, tradeoffs,
resolved decisions, follow-ups, and remaining gaps in the record, with findings
in Review Sweep's
[claim, repair, and check states](../review-sweep/references/finding-schema.md).

Lead the handoff with Needs you when action is required, otherwise with the
usable outcomes and their links. Name the decisions you resolved so the user can
reopen them. Clean up through [Repo Cleanup](../repo-cleanup/SKILL.md) once
retained work and active dependents no longer need the resources.

Before pausing or moving, bring the record current. On resume, reconcile it with
current files, threads, and forge state, and
[host the page again](references/hosting.md#host-again), before dispatching. To move the program to another thread or take over from a chief
that cannot act, follow [chief move](references/chief-move.md). This skill supplies no background
wakeups: native goal tracking, recurring checks, and other automation need an
explicit user request and host support.
