# Heartbeat, pause, resume, and migration

Read this when setting up or tuning a program's heartbeat, pausing or resuming a program, or
migrating an older Chief-of-Staff program.

## Heartbeat

Set up one heartbeat at program start as a liveness backup (messages, PR watches, and the answer
wake act sooner). Choose a finite next-check interval from owner reports, next expected event,
deadlines, and acceptable delay if an event is missed. Honor user cadence/limits; keep 10 minutes
when active owners are running and timing is unknown, and record a timing reason in `next` whenever
lengthening unchanged waits.

- **0 running owners, waiting purely on the user:** pause the heartbeat (`enabled: false`) so idle
  ticks don't compact the thread — the user's reply or answer wake resumes you immediately. On the
  first ordinary wake or Inbox answer that restores running owners or external waits, explicitly
  re-enable the paused heartbeat (`enabled: true`) and verify `enabled` and `nextRunAt`.
- **0 running owners, waiting only on slow external events** (upstream issue, teammate review):
  lengthen to 1–6 hours with the reason in `next`.
- **Long-lived, heavily compacted coordinator thread:** move to a fresh thread via `record.py move`
  under `coordinator-move.md` instead of letting context rot accumulate.

In T3, call `schedule_task` with an interval trigger, `bindToCurrentThread: true`, and this exact
prompt verbatim — never stuff holds, grants, or model notes into it (`program.json` holds those):

```text
Coordinator heartbeat for <program title>. Re-read <this skill's absolute folder>/SKILL.md and check the current coordinator before acting.
When grant.wake names an answer wake, first record stored picks under <this skill's absolute folder>/references/hosting.md ("Stored picks"). Then run
python3 <this skill's absolute folder>/scripts/record.py status --heartbeat --state <absolute path>/program.json
and do what its first line says. Before ending an active program's turn, choose the next heartbeat under <this skill's absolute folder>/references/lifecycle.md, including after a quiet result.
```

Record the timing policy and task ID with `record.py grant --heartbeat "<policy and task ID>"`.
Before ending any working or waiting turn, replace `next` with one short line (at most 280
characters): the next action, interval/reason if changed, and sooner-wake event — never a history
log. Update the existing task by `scheduledTaskId`
(`schedule: {type: "interval", everyMs: <ms>}`) only when the interval changes; verify returned
`enabled` and `nextRunAt` and report any failure instead of claiming liveness. (Every tick invokes
the model; `status --heartbeat` prints `quiet` so you end with no user message, not zero model
calls.)

If the host has no scheduled tasks, record that in `grant.heartbeat`, and wait on outstanding owner
runs through the host before ending a turn.

## Pause

Bring the record current, pause the heartbeat (`schedule_task` with `enabled: false` in T3), and
turn off tap-to-answer under `hosting.md`.

## Resume

1. Re-read `SKILL.md`, start from `next`, and run `record.py status`.
2. Reconcile the record with current files, threads, and forge state, and force-publish the page
   under `hosting.md` before dispatching new work (which owns restoring tap-to-answer and
   updating `grant.wake` once when on Claude).
3. Re-enable the paused heartbeat — or recreate it if deleted/missing, updating `grant.heartbeat` —
   and verify `enabled` and `nextRunAt` (upgrade any pre-stored-picks prompt to the template above).

## Chief-of-Staff migration

For a program created under the older Chief of Staff skill: run `record.py status` from this skill's
folder, record the grant (`record.py grant`) from what the user already authorized (citing those
sources; the resuming message authorizes the heartbeat), set up the heartbeat and answer wake, and
republish the page so it shows the Inbox.
