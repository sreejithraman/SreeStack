# Heartbeat, pause, resume, and migration

Read this when setting up or tuning a program's heartbeat, pausing or resuming a program, or
migrating an older Chief-of-Staff program.

## Heartbeat

Set up one heartbeat at program start as a liveness backup (owner messages and PR watches act
sooner). Choose a finite next-check interval from owner reports, next expected event, deadlines,
and acceptable delay if an event is missed. Honor user cadence/limits; keep 10 minutes when active
owners are running and timing is unknown, and record a timing reason in `next` whenever lengthening
unchanged waits.

- **0 running owners, waiting purely on the user:** pause the heartbeat (`enabled: false`) so idle
  ticks don't compact the thread — the user's reply resumes you immediately. `record.py status`
  prints a `hint:` whenever its verdict is `waiting`. On the first ordinary wake or Inbox answer
  that restores running owners or external waits, explicitly re-enable the paused heartbeat
  (`enabled: true`) and verify `enabled` and `nextRunAt`.
- **0 running owners, waiting only on slow external events** (upstream issue, teammate review):
  lengthen to 1–6 hours with the reason in `next`.
- **Long-lived, heavily compacted coordinator thread:** move to a fresh thread via `record.py move`
  under `coordinator-move.md` instead of letting context rot accumulate. `record.py status` (and
  `status --heartbeat`, once) warns once `chief` reaches 400 runs or 8,000 items, or times out.

In T3, call `schedule_task` with an interval trigger, `bindToCurrentThread: true`, and this exact
prompt verbatim — never stuff holds, grants, or model notes into it (`program.json` holds those):

```text
Coordinator heartbeat for <program title>. Run
python3 <this skill's absolute folder>/scripts/record.py status --heartbeat --chief-id <this thread ID> --state <absolute path>/program.json
and follow its first line. On `heartbeat: quiet`, end the turn immediately without reading `SKILL.md` or posting a message. On `heartbeat: not-chief`, delete this stale heartbeat task and end the turn without acting. On `heartbeat: wake` or `heartbeat: done`, check `chief` in `HEAD:program.json`, re-read <this skill's absolute folder>/SKILL.md, act on what `status` lists, and update the heartbeat under <this skill's absolute folder>/references/lifecycle.md only when the cadence should change.
```

Record the timing policy and task ID with `record.py grant --heartbeat "<policy and task ID>"`.
Before ending any working or waiting turn, replace `next` with one short line (at most 280
characters): the next action, interval/reason if changed, and sooner-wake event — never a history
log. Update the existing task by `scheduledTaskId`
(`schedule: {type: "interval", everyMs: <ms>}`) only when the interval changes; verify returned
`enabled` and `nextRunAt` and report any failure instead of claiming liveness. (Every tick invokes
the model; `status --heartbeat` prints `quiet` so you skip `SKILL.md` and end with no user message,
not zero model calls.)

If the host has no scheduled tasks, record that in `grant.heartbeat`, and wait on outstanding owner
runs through the host before ending a turn.

## Pause

Bring the record current and pause the heartbeat (`schedule_task` with `enabled: false` in T3).

## Resume

1. Re-read `SKILL.md`, start from `next`, and run `record.py status`.
2. Reconcile the record with current files, threads, and forge state, and force-publish the page
   under `hosting.md` before dispatching new work.
3. Re-enable the paused heartbeat — or recreate it if deleted/missing, updating `grant.heartbeat` —
   and verify `enabled` and `nextRunAt` (upgrade any older heartbeat prompt to the template above).

## Upgrading an active program

On an existing program's first active turn or provider switch under this skill: update its
installed heartbeat prompt to the template above; if `grant.wake` still records a legacy webhook
task, delete and verify that task (clearing `config/wake` if Claude DB tools are available, or
telling the user to re-answer any pending old-page picks via Copy answer) and record
`record.py grant --wake "None (<reason>)"`.

## Chief-of-Staff migration

For a program created under the older Chief of Staff skill: run `record.py status` from this skill's
folder, record the grant (`record.py grant`) from what the user already authorized (citing those
sources; the resuming message authorizes the heartbeat), set up the heartbeat, and republish the
page so it shows the Inbox.
