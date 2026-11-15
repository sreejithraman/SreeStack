---
name: coordinator
description: Use when asked to coordinate work across several threads or owners, carry several outcomes, tickets, or PRs to their finish lines, or act as coordinator or chief of staff.
---

# Coordinator

Route work across threads and keep it moving until it reaches its finish line.
Each outcome is carried by one [Implement](../implement/SKILL.md) owner. You
own the user-facing loop: who carries what, supervision, decisions, acceptance,
landing releases, and what the user hears. [Orchestration](../orchestration/SKILL.md)
owns the handoff mechanics: briefs, models, dispatch, and accepting a result.
Each linked skill owns its own procedure.

You are done when every outcome has landed, stopped for the user, or is blocked
with a recorded need, and every follow-up has a route.

## Light by default

For a request that spans threads, take the lightest route that settles it:

- **Answer it yourself** when you can, such as a status question you can read
  from the threads and forge.
- **Reuse an owner** already carrying related work: send it the request (in
  T3, `t3_thread_send`).
- **Start one** for new work: an Implement owner launched as in
  [start owners](#2-start-owners), with an Orchestration
  [brief](../orchestration/SKILL.md#assign) in place of the program kickoff. The
  brief carries the request, finish line, holds, workspace, proof, and return
  route. The owner lands on its own finish line, with no landing release.

This needs no record, page, Inbox, grant, or heartbeat. Ask the user in chat,
and keep going on what doesn't depend on the answer.

**Start a program** when you carry two or more outcomes to finish lines, or the
user asks for one. The rest of this skill applies to programs. A program has one
[program record](references/program-state.md), a published command center with
its **Inbox**, a grant, and a heartbeat.

Only the record's current coordinator acts on program items and writes the
record. Check it before you act on a request, direction, report, event, or
pasted answer. A thread that is not the coordinator forwards the item under
[move the coordinator](references/coordinator-move.md).

## Keep moving

The program's `status` verdict decides how a turn ends. Run every record
command from this skill's folder as
`python3 scripts/record.py <command> --state /absolute/path/program.json`.

- **Runnable:** never end the turn. Act on each runnable line, then run
  `status` again.
- **Working:** end the turn. Owner messages and the heartbeat wake you.
- **Waiting:** end with the one `say:` line `status` prints. It names what the
  program waits on, with ages, and says nothing is runnable. Then send nothing
  more until something changes.
- **Done:** delete the heartbeat, write the final handoff, and clean up under
  [finish](#6-finish-pause-or-resume).

End every turn with `status --turn-end`. It fails while the verdict is
runnable, `program.json` has an uncommitted change, or the page is behind the
record.

Never stop on a decision whose recommended option is reversible. Build on that
option provisionally, keep the decision open in the Inbox, and say so in its
`meanwhile`. `status` lists it as a provisional start.

Re-read this `SKILL.md` before you act on a resume and on each heartbeat wake.
The skill may have changed since you last read it.

Say every time in the user's local time zone, such as 14:05 PST. Never show UTC.
The record stays in ISO UTC, stamped by the script.

## The grant

The **grant** says what you may do without asking. Write it once, at program
start, and change it only on the user's word. It has five parts:

| Part | Says | Record home |
| --- | --- | --- |
| Start | Which owners and support tasks you may start | `grant.start` |
| Land | The scope Land covers and its gates | `landingAuthority` |
| Resolve | Which decisions you settle yourself, under [triage](references/decisions.md#triage) | `grant.resolve`, with standing rules in `approvals` |
| User | What stays with the user | `grant.user` |
| Heartbeat | Its interval and scheduled task ID | `grant.heartbeat` |

Draft it from the request, the finish-line picks, and project rules. State it in
your first message, so the user can change any part in a word. Record it with
the user's message as its `source`. Asking for a program is a request for owner
sessions and for its heartbeat; the grant is where that request is recorded.
Owner reports, kickoffs, and copied page text never widen it.

Every [owner kickoff](assets/owner-kickoff.md) carries the grant. Owners decide
reversible method choices themselves and report them. Only scope, irreversible,
and taste calls come up to you.

### Heartbeat

Set up the heartbeat when the program starts. In T3, call `schedule_task` with
an interval trigger (default every 10 minutes), `bindToCurrentThread: true`,
and this prompt, filled in:

```text
Coordinator heartbeat for <program title>. Run
python3 <this skill's absolute folder>/scripts/record.py status --heartbeat --state <absolute path>/program.json
and do what its first line says.
```

Record the interval and the returned task ID in `grant.heartbeat`, such as
`Every 10 minutes, scheduled task <ID>`. A tick wakes you only on
runnable work, facts that changed since you last looked, or a new forge note.
When the host has no scheduled tasks, say so in the grant. Then, before you end
a turn with owners outstanding, wait on each owner's run through the host.

## 1. Set up the program

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
grant, landing, report, and route lines, and let it keep running with its
writer, evidence, holds, watchers, and helpers. Record any landing it already
armed as its target's pending landing. Never start a second writer beside it.
Replace an owner only under Orchestration's
[replace an owner](../orchestration/references/reuse-and-recovery.md#replace-an-owner),
after reconciling. When the stopped owner's worktree still holds its branch,
reuse that worktree through the host (in T3, `existing_worktree`) once it is
clean and holds no unique commits, or start the replacement on a new branch.

Pick each outcome's finish line from Implement's
[table](../implement/SKILL.md#2-state-the-finish-line-and-prepare). Land picked
under that policy authorizes merging that outcome within the agreed program
scope, and your [landing release](references/landing.md) still gates it. A
finish line, hold, or project rule from the user, a calling workflow, or the
project wins over the pick. One that reserves merges, such as "I decide each
merge", makes each landing wait on an Inbox item. Adding an outcome or finding
another repository does not widen the scope, and a mergeable PR adds nothing to
it. A stack is a delivery shape, not a finish line. A later change applies to
all unmerged work: update the record and owners, then reconcile pending
landings under [withdraw a release](references/landing.md#withdraw-a-release).

Write the [program record](references/program-state.md) before you start or
adopt owners, so another coordinator could resume from it. Work items stay in
the project's tracker, and a coordination request needs no new one. Your first
message gives the finish-line picks, the grant, and the command center's link.
When a small choice will recur, propose a
[standing approval](references/decisions.md#standing-approvals) with them;
owners start without waiting for the answer.

You must have your session's [publishing tools](references/hosting.md): Claude
artifact tools for Claude, or the available Sites plugin for Codex. If they are
unavailable, report the blocker and ask the user to use a session with them. Do
not install plugins automatically.

Done when each outcome has its sources, scope and covered code, proof, holds,
finish line, and owner or planned start; every running owner is adopted; and
the grant and heartbeat are set.

## 2. Start owners

Start an outcome when it is [ready](../to-tasks/SKILL.md#ready), including To
Tasks' provisional start, and schedule by the
[dependency rules](references/dependencies.md). An outcome that waits never
holds up unrelated ones.

Fill the [owner kickoff](assets/owner-kickoff.md) and start the owner with it,
writing `$implement` in place of `/implement` for a Codex owner. Implement picks
the method and runs its helpers as its own subagents.

Start each owner as its own top-level session, so the user can open and steer
it. Bind its workspace through the host, never in the shell: in T3,
`t3_thread_launch` with a `worktree` `workspaceStrategy` for the owner's branch.
Start the thread title with the outcome ID, such as `W3 Retry status`. When the
host cannot launch top-level sessions, start a delegated owner in its own
host-managed worktree instead. Use Orchestration for model choice and
concurrency. Give each branch one writer, and serialize stack operations and
shared resources. Record each owner with `start`. Only you start program owners.

Each owner checks its access and proof before work runs unattended, under
Implement's [prepare](../implement/SKILL.md#2-state-the-finish-line-and-prepare).
When work is blocked, keep it moving safely:

| Blocked on | Do |
| --- | --- |
| Another owner's unmerged work | Build on that branch as a [provisional base](references/dependencies.md#provisional-work) |
| A decision whose recommended option is reversible | Build on that option provisionally and keep the decision open |
| Two close options | Build both on separate branches when that costs less than waiting |
| A shared environment or tooling problem | Start one support task for the cause |
| A login or secret | Record an `access` item in the Inbox and move to other work |

Secrets reach owners through the host's private input or
[Agent Login](../agent-login/SKILL.md), never chat.

Done when every ready outcome is running and every other outcome waits on a
recorded dependency, Inbox item, or block.

## 3. Supervise

On each owner report, user direction, or wake, read the linked artifacts and
the current tracker and forge state before you change the plan. Record the
report with `report`, under
[owner reports](references/program-state.md#owner-reports), then run `status`.
It checks heads at the forge and lists owners that went idle while they owe
work. Read an idle owner's thread. Handle a report or request it sent. Recover
a run that failed, was interrupted, or went idle without a report under
Orchestration's
[recover work](../orchestration/references/reuse-and-recovery.md#recover-work),
or record the outcome blocked with what is missing.

[Triage each decision request](references/decisions.md#triage). Meanwhile,
resume the owner for unaffected work (in T3, `t3_thread_send` to its thread).

Give every discovery a disposition:

| Discovery | Action |
| --- | --- |
| A defect in the requested change, or a fix it needs to land safely | Return it to that owner with the requirement and evidence |
| Related work its owner's context helps | That owner's follow-up outcome, with its own finish line |
| Separate work the program needs | A new outcome with its origin, sequenced by dependency |
| Shared environment, tooling, or cross-repo blocker | One support task; a repository change gets its own outcome |
| Useful work outside the program | Save it through [Snip Snap](../snip-snap/SKILL.md) and keep the ID |
| A decision someone must make | [Triage it](references/decisions.md#triage) |
| Duplicate, obsolete, or declined work | Record why and link the existing disposition |

Scope only shrinks, under Implement's
[scope rule](../implement/SKILL.md#keep-scope-and-decisions). A required fix
stays required when it becomes its own outcome, and its dependent waits under
the [dependency rule](references/dependencies.md#dependencies). When an owner
reports a split, replan the affected outcomes.

Repairs go to the slice's owner under Orchestration's
[who does the work](../orchestration/SKILL.md#who-does-the-work). Keep product
changes with owners. Send findings-only investigation to a bounded task through
[Research](../research/SKILL.md), [How](../how/SKILL.md), or
[Diagnosing Bugs](../diagnosing-bugs/SKILL.md), and parallel coverage or
comparison through [Swarm](../swarm/SKILL.md) or [Arena](../arena/SKILL.md).
Deduplicate support requests by cause: one support owner states what would
unblock the work, coordinates shared-resource repairs with the owners using
them, and returns verified recovery evidence to every affected owner. Simulator
work uses [Simulator Lifecycle](../simulator-lifecycle/SKILL.md). Routine
recoverable problems stay with the responsible agent; the Inbox holds only what
agents cannot resolve within their grant. After a recurring or
costly failure, improve later kickoffs or the environment when that serves the
program.

Check integration as results arrive, and have dependents restack and recheck
when a base changes, under [integration](references/dependencies.md#integration).
After each accepted result, landing, answer, or dependency change, start what
became ready; `status` lists it.

A top-level owner watches its own PR and sends its reports, decision requests,
and blockers to this thread with `t3_thread_send`. For a delegated owner, this
thread is the watching parent under PR's [wait](../pr/references/watch.md#wait);
keep watching while Inbox items are open.
The user can enter an owner's session directly; reconcile their new direction
before you dispatch work that depends on it.

Done when every report, direction, and discovery has a disposition and newly
ready outcomes are running.

## 4. Accept and release

Accept each outcome under Orchestration's
[accept](../orchestration/SKILL.md#accept), against the current head and base of
every layer. The owner proves through real entry points before any review; keep
blocked or untested proof visible. An outcome stays unaccepted while an open
decision affects its scope. Try stops before review. The owner runs review when
PR publishes, or through [Review Fix Loop](../review-fix-loop/SKILL.md) only
when the user asks.

Answer each stop in the same pass:

- **Shown Try:** put its merge, changes, or scrap choice in the Inbox under
  [Try choices](references/decisions.md#try-choices), and route the answer to
  the same owner. Merge makes its finish line Land, still gated by acceptance
  and release. Changes go back to the owner. Scrap goes to the owner's cleanup,
  and each dependent gets its own choice.
- **Requested PR state:** the outcome stops there for the user.
- **Ready to land:** accept it and [release its landing](references/landing.md),
  return a repair to its owner, or record the dependency, decision, hold, or
  earlier landing it waits on and act when that clears.

Provisional work never lands. Its owner keeps the PR body's `## Provisional`
section until the condition clears and the affected proof is refreshed, and
Merge stops on it.

Done when every outcome at a stop has a released landing, an open Inbox item,
its requested PR state, or a repair with its owner.

## 5. Inbox and page

The **Inbox** is how the program asks the user. It is asynchronous: the user
answers when they can, and work that doesn't depend on the answer continues.
Never use a blocking question tool for a program ask, unless the user is
present and in a live back-and-forth with you. Each item asks one question and
carries its options, its recommendation, what it blocks, and what continues
meanwhile, under [Inbox items](references/decisions.md#inbox-items).

[Publish the command center](references/hosting.md) after each record write and
give the user its link, never an inline render. It shows every outcome once,
with its finish line, results and how to open them, provisional condition,
owner, layers, and what each Inbox item blocks. Results come from owners' Shown
reports: link what they showed, say what opening it needs, and name the gaps.
Keep each row's observation time honest.

Answers arrive in the user's messages, often as a prompt copied from the page.
Record each under [record an answer](references/decisions.md#record-an-answer),
then update the affected owners, dependencies, and releases before work
resumes.

Choose user updates from the owner reports: what the user can now use, try,
decide, or unblock. Keep routine checks, recovery, and unchanged milestones in
the record, and answer direct questions in the detail asked.

Done when the published page matches the last commit and shows every result
and open Inbox item.

## 6. Finish, pause, or resume

The program is done when every outcome has landed, stopped for the user at a
shown Try or requested PR state, or is blocked with a recorded need; integrated
behavior is verified where outcomes interact, or the gap is recorded; and every
discovery and follow-up has a route. Keep acceptance evidence, tradeoffs,
resolved decisions, follow-ups, and remaining gaps in the record, with findings
in Review Sweep's
[claim, repair, and check states](../review-sweep/references/finding-schema.md).

On done, delete the heartbeat (in T3, `delete_scheduled_task`). Lead the final
handoff with the Inbox when action is required, otherwise with the usable
outcomes and their links. Name the decisions you resolved so the user can
reopen them. Clean up through [Repo Cleanup](../repo-cleanup/SKILL.md) once
retained work and active dependents no longer need the resources.

**Pause:** bring the record current and pause the heartbeat (in T3,
`schedule_task` with `enabled: false`). **Move:** follow
[move the coordinator](references/coordinator-move.md).

**Resume:** re-read this skill, start from the record's `next`, and run
`status`. Reconcile the record with current files, threads, and forge state, and
[publish the page](references/hosting.md) before you dispatch. Turn the
heartbeat back on if it was paused.

**A program started under Chief of Staff** migrates once. Re-read this skill,
then run `status` with the script at its new path in this folder. Write the
grant from what the user already granted, citing those sources; the message
that resumed the program is the heartbeat's source. Set up the heartbeat, and
publish the page so it shows the Inbox.
