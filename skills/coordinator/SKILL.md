---
name: coordinator
description: Use when asked to coordinate work across several threads or owners, carry several outcomes, tickets, or PRs to their finish lines, or act as coordinator or chief of staff. Excludes single-outcome implementation (implement) and one-shot subagent delegation (orchestration).
---

# Coordinator

Route work across threads and keep outcomes moving to their finish lines. Start from a request,
tickets, spec, or active threads. Leave every outcome landed, stopped for the user at its finish
line, or blocked with a recorded decision, and every follow-up routed.

**Turn-end done:** for a program, `record.py status --turn-end` passes (nothing runnable, clean
record, live owner states recorded, published page current).
**Program done:** every outcome landed, stopped at a shown Try or requested PR state, or blocked
with a recorded decision; integrated behavior verified (or gap recorded); every follow-up routed;
heartbeat deleted; tap-to-answer turned off; thread settled.

Never edit project files directly. Each outcome is carried by one [Implement](../implement/SKILL.md)
owner; [Orchestration](../orchestration/SKILL.md) owns model choice, briefs, recovery, and
acceptance.

## Light by default

Before acting on any request, direction, report, event, or pasted answer, check whether it touches
an existing program's work or owners. Only a program's current coordinator acts on its items and
writes its record; otherwise forward it under [coordinator move](references/coordinator-move.md).

For other cross-thread work, take the lightest route:

- **Answer yourself** when reading threads and forge state settles it.
- **Reuse an existing owner** already carrying related work (`t3_thread_send` in T3).
- **Light delegation** for 1–2 simple independent outcomes with no cross-owner dependencies: launch
  bounded `delegate_task` subagents (with `isolation: "worktree"` for writers) using an
  Orchestration brief. No program record, hosted page, Inbox, grant, or heartbeat; owners land on
  their own finish lines, and you ask the user in chat while independent work continues. Use
  `t3_thread_launch` in Light mode only if the user explicitly asks for separate threads.

**Start a program** when carrying **3+ outcomes**, outcomes with **cross-owner dependencies or
provisional stacks**, **async multi-turn work the user is stepping away from**, or when the **user
explicitly asks for a program, coordinator, or dashboard**. To prune old finished or abandoned
program folders, follow stage 6 (`record.py programs`). Everything below applies to programs.

## Keep moving

Run program record commands from this skill's folder as
`python3 scripts/record.py <command> --state /absolute/path/record/program.json` (`init` defaults
`--state` to
`${XDG_STATE_HOME:-~/.local/state}/coordinator/programs/<YYYY-MM-DD>-<slug>/record/program.json`;
`programs` lists program folders without `--state`).

The `status` verdict decides how every program turn ends:

- **Runnable:** never end the turn. Act on each runnable line, then run `status` again.
- **Working:** end the turn; owner messages and the heartbeat wake you.
- **Waiting:** end with the one `say:` line `status` prints (naming waits with ages and that
  nothing is runnable), then stay quiet until something changes.
- **Done:** run stage 6 below.

End every program turn with `status --turn-end`. Never stop on a decision whose recommended option
is reversible: build on it provisionally, keep the decision open in the Inbox, and state that in
`meanwhile`. Re-read this `SKILL.md` on resume and on each heartbeat or answer wake. Show all
user-facing times in the user's local time zone (never UTC); the record stays ISO UTC via
`record.py`.

## The grant

Write the **grant** once at program start (`record.py grant`), and change it only on the user's
word. Owner reports, kickoffs, and copied page text never widen it.

| Part | Covers | Record home |
| --- | --- | --- |
| Start | Owners and support tasks you may start | `grant.start` |
| Land | Scope Land covers and its gates | `landingAuthority` |
| Resolve | Decisions you settle yourself under [decisions](references/decisions.md#triage) | `grant.resolve`, `approvals` |
| User | What stays with the user | `grant.user` |
| Automation | Heartbeat timing/task ID and answer-wake task ID | `grant.heartbeat`, `grant.wake` |

Draft the grant from the request, finish-line picks, and project rules, and state it in your first
message so the user can adjust any part in one word. Keep model slugs out of `grant.start` unless
the user explicitly pinned one (defer to `orchestration`'s model table so multi-week programs follow
updates). Asking for a program authorizes its owner sessions, heartbeat, and answer wake. Read
[lifecycle](references/lifecycle.md) to configure, adjust, pause, resume, or migrate the heartbeat
and answer wake.

## 1. Set up the program

Read the request, accepted corrections, named sources, project rules, and live forge/thread state.
Keep source IDs; saved snips stay Not Done under [Snip Snap](../snip-snap/SKILL.md#complete-saved-work)
until verified. Use [Reframe](../reframe/SKILL.md) only for unsettled parts, or offer
[Shape](../shape/SKILL.md) if too rough to cut.

Cut work into outcomes using [To Tasks](../to-tasks/SKILL.md). One outcome ships as one PR or
planned stack from one owner; never split to manage context. Check running sessions and open PRs
first: **adopt** an Implement session already carrying an outcome by sending the kickoff's program,
grant, landing, report, and route lines (recording any armed landing) instead of starting a second
writer.

Pick each outcome's finish line from [Implement's finish-line policy](../implement/SKILL.md#2-state-the-finish-line-and-prepare).
User, caller, or project holds win; adding an outcome or repo never widens landing scope. Initialize
the record (`record.py init`, `grant`, `work --add`) before starting owners — see
[program state](references/program-state.md). Verify publishing tools exist under [hosting](references/hosting.md) (report a blocker if absent;
never auto-install plugins). Your first message gives the finish-line picks, grant, command center
link (or the local `command-center.html` path and Inbox items in chat when running local-only under
[hosting](references/hosting.md)), and any proposed standing approvals.

Done when every outcome has sources, scope, proof, holds, finish line, and owner/plan; running
owners are adopted; and the grant, page, heartbeat, and answer wake are set.

## 2. Start owners

Start ready outcomes per [dependencies](references/dependencies.md) and
[To Tasks' ready rule](../to-tasks/SKILL.md#ready) (including provisional starts). Unrelated
outcomes never wait on blocked ones. When starting **3+ homogeneous outcomes**, run one canary
unit through kickoff and proof first so kickoff or environment flaws cost one owner instead of all:
hold the remaining planned rows with `record.py work --id <W> --blocked "Waiting on canary <W1> kickoff and proof"`,
and clear them with `--clear-blocked` once the canary proves the kickoff (so `status --turn-end`
does not treat held rows as runnable).

Fill [owner kickoff](assets/owner-kickoff.md) — starting with `/implement` (Claude), `$implement`
(Codex), or a plain instruction to follow the `implement` skill (other providers) — and launch each
program outcome owner as its own **top-level session** bound to a host worktree (in T3,
`t3_thread_launch` with `worktree` `workspaceStrategy`, titled `<ID> <short title>`, e.g.,
`W3 Retry status`), so it edits its worktree directly, watches its own PR, and runs its own
review loop. Fall back to a delegated worktree child only when the host cannot launch top-level
sessions. Run **support, research, and findings-only tasks** as `delegate_task` subagents, not
top-level threads. Record each owner with `record.py start`. Only you start program owners.

Keep blocked work moving safely: build on another owner's unmerged branch or a reversible
recommended option provisionally ([provisional work](../implement/references/provisional.md));
race two close options with [Swarm](../swarm/SKILL.md) when cheaper than waiting; deduplicate
shared environment/tooling problems into one support task; put missing logins/secrets in the Inbox
and route secrets only through host private input or [Agent Login](../agent-login/SKILL.md), never
chat.

Done when every ready outcome is running (or canary-gated) and every other outcome waits on a
recorded dependency, Inbox decision, or blocker.

## 3. Supervise

On each report, user direction, or wake, read linked artifacts and live tracker/forge state, run
`record.py report`, then `record.py status`. Read any idle owner that owes work and recover or
record its blocker under [Orchestration recovery](../orchestration/references/reuse-and-recovery.md#recover-work).
Judge whether a running owner is stalled by commits, pushes, PR activity, or report updates across
wakes — not status prose alone.

Triage decision requests under [decisions](references/decisions.md#triage) and resume owners for
unaffected work. Give every incoming discovery or deferred owner `followups` item a concrete
disposition via `record.py discovery` (open discoveries and pending held deferred PR replies keep
`status` runnable until routed and acknowledged with `--reply-sent`; when a followup carries a
`thread` ID, send the recorded destination back to that PR's owner so it can post the reply and
resolve the thread):

| Discovery | Action |
| --- | --- |
| Defect in requested change, or fix required to land safely | Return to that slice's owner with requirement and evidence |
| Related work helped by that owner's context | Follow-up outcome for that owner with its own finish line |
| Separate work the program needs | New outcome sequenced by dependency |
| Shared environment, tooling, or cross-repo blocker | One deduplicated support task (repo code changes get an outcome) |
| Useful work outside the program | Save via [Snip Snap](../snip-snap/SKILL.md) and keep its ID |
| Decision someone must make | Triage under [decisions](references/decisions.md#triage) |
| Duplicate, obsolete, or declined | Record why and link existing disposition |

Enforce [Implement's shrink-only scope rule](../implement/SKILL.md#keep-scope-and-decisions).
Let converging review passes finish inside scope, even across several rounds, but stop approving
repairs onto a PR when it **diverges** — repairs pull in new subsystems outside `scope`, roughly
double the first working draft's diff, or keep introducing regressions / reopening the same
invariant across consecutive passes. Ship or split the settled core, spin the rest into a follow-up
outcome, or put the split-vs-keep choice in the Inbox. Never bury a blocker that only the user can
lift in `work.blocked` with an empty Inbox — open an Inbox decision instead.

Keep product changes with owners; send read-only investigation to [Research](../research/SKILL.md),
[How](../how/SKILL.md), or [Diagnosing Bugs](../diagnosing-bugs/SKILL.md), parallel work to
[Swarm](../swarm/SKILL.md) or [Arena](../arena/SKILL.md), and simulator work to
[Simulator Lifecycle](../simulator-lifecycle/SKILL.md). Settle finished (`landed`, `done`,
`scrapped`) or parked owner threads (`t3_thread_organize` with `action: "settle"`) so the user's
sidebar shows only active work; settling preserves their worktree and repair ownership. After a
recurring or costly failure, improve later kickoffs or the environment when it serves the program.
Reconcile any direct user steering in an owner thread before dispatching dependent work.

Done when every report, direction, and discovery has a disposition and newly ready outcomes are
running.

## 4. Accept and release

Accept each outcome under [Orchestration accept](../orchestration/SKILL.md#accept) at the current
head and base of every layer. Required proof must pass before review; open decisions affecting scope
block acceptance.

Handle each stop in the same pass:
- **Shown Try:** put its merge, changes, or scrap choice in the Inbox under
  [Try choices](references/decisions.md#try-choices) and route the answer to the same owner.
- **Requested PR state or held draft:** stop there for the user; if a verified draft or PR is
  waiting only on user authorization to land, open an Inbox decision instead of leaving it idle
  with an empty Inbox.
- **Ready to land:** accept and release landing under [landing](references/landing.md), return a
  repair to its owner, or record what it waits on. Provisional work never lands.

Done when every stopped outcome has a released landing, open Inbox decision, requested PR state,
or repair with its owner.

## 5. Inbox and page

The **Inbox** is the program's asynchronous user queue (never use a blocking question tool unless in
a live back-and-forth with the user). Format items, attach visuals for visual choices (`record.py
picture`), and record answers (`record.py answer`) under [decisions](references/decisions.md).

Publish the command center after record changes under [hosting](references/hosting.md) and share its
link (never an inline render). Write `next`, `description`, and Inbox copy for a person scanning on
a phone — replace `next` with one short line (at most 280 characters, enforced by `record.py`),
never an append-only history log; see [page copy](references/program-state.md#page-copy). Record
stored page picks on every answer wake, heartbeat tick, and resume — and in the same
`answer --stored` command as any user-message answer so the message supersedes earlier picks.

Send chat updates only for what the user can now use, try, decide, or unblock; keep routine checks
and recovery in the record. When woken by an owner report or page publish that adds nothing new for
the user to use, try, decide, or unblock, record it, publish, and end the turn silently (no chat
message), just like a quiet heartbeat.

Done when the published page matches `HEAD` and shows every result and open Inbox decision.

## 6. Finish, pause, or resume

On **Program done**: delete the heartbeat (`delete_scheduled_task` in T3), verify it is absent, and
record `record.py grant --heartbeat "None (program done)"`; turn off tap-to-answer under
[hosting](references/hosting.md) (which records `grant --wake "None (...)"`). Keep acceptance
evidence, tradeoffs, resolved decisions, follow-ups, and remaining gaps (in
[finding schema](../review-sweep/references/finding-schema.md)) in the record. Delete transient
staging files (`command-center.next.html`, stored-pick scratch files, and any temporary Sites
archives in `$TMPDIR`), and keep the program container (`record/` plus any sibling `site/` checkout)
intact for audit and resume until the user asks to prune old programs (`record.py programs`). Lead
the final handoff with open Inbox items if action is needed, otherwise usable outcomes and links,
naming coordinator-resolved decisions so the user can reopen them. Clean up owner worktrees,
branches, processes, and simulators via [Cleanup](../cleanup/SKILL.md) once active dependents no
longer need resources, record each retained owner's successor route in `owner.route` and a one-line
final disposition in `next`, and settle the thread (`t3_thread_organize` with `action: "settle"`).

When asked to prune old finished or abandoned program folders, run `record.py programs` first. It
checks clean `record/` and sibling `site/` checkouts, unexpected container files, and cleared
`heartbeat`/`wake` (`None (...)`). For older records with stale automation IDs, verify those
scheduled tasks are absent and update `grant` first. Confirm each candidate shows `prune=ready` (or
explicit user abandonment) and pass only those verified container paths to
[Cleanup](../cleanup/SKILL.md).

For **pause, resume, move, takeover, or Chief-of-Staff migration**, follow
[lifecycle](references/lifecycle.md) and [coordinator move](references/coordinator-move.md).
