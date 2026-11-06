# Break glass: restart the simulator backend

This is the last resort for iOS simulators that won't boot on this Mac, and the only
exception to keeping shared services running. The user decided that it needs no approval,
and that it applies even though the host's device rules say to tell them and stop once
recovery fails.

SimLock can't keep new work out during a restart, and a restart can break another agent's
boot and lose a night of progress across sessions. [`scripts/break_glass.py`](../scripts/break_glass.py)
holds the rules that must always hold: one claim per machine, one restart in 6 hours,
no restart after a failed one until the user clears it, and the machine check.
`glass` below means `python3 <this skill>/scripts/break_glass.py`.

## Use it only when all of these hold

Run `glass status` first, because it can save the wait. If it refuses because of a recent
restart, acquire once, then report either way. If it refuses for another reason, report it.

- The failure is a simulator boot before a grant, such as `BootTimeoutError` or T3's
  "failed to boot". It isn't a quota, policy, build, or app failure.
- The retry failed, and so did one other device model unless the user named the target.
  You then waited 15 minutes, and one more attempt failed the same way. Attempts an owner
  reports to you count.
- `simlock doctor`, without `--fix`, shows no other cause.
- The task's outcome needs a simulator, and the work that doesn't need one is done. A
  `show-me` capture alone never qualifies: post what you have and name the gap.
- You own the task, or your parent assigned you this repair. Any other delegated child
  reports to its parent instead.
- T3's thread tools can reach other sessions.

## Steps

1. **Claim.** Run `glass claim --thread <your thread>`. It prints `holdUntil` and
   `holdUntilLocal`, the deadline for everything below. Exit 2 means another session owns
   the restart: run `glass wait` in the background, then acquire once. Exit 3 means a rule
   refuses, so treat it like `glass status`.
2. **Hold.** Run `glass wait` in the background, so its exit wakes you at the deadline. List
   T3 sessions across all projects in the `preparing`, `queued`, `starting`, and `running`
   states, skipping your own. Leave idle, waiting, and finished sessions alone, because a
   message starts them. Send each one, in `steer` mode: "Break glass: <your thread> needs to
   restart CoreSimulator. Until it releases this or until <holdUntilLocal>, whichever is first, you and
   your subagents start no new simulator work. Let running work finish. Reply to that thread
   now, even if you have none, and again when it ends."
3. **Wait** until every session has replied and its simulator work has ended.
4. **Check.** List sessions again. If any are new, hold them and return to step 3. Then run
   `glass check --t3-open-sessions <open device sessions in this thread>`. If it refuses,
   you can repeat it until 5 minutes before `holdUntil`.
5. **Restart once.** Run `glass restart --thread <your thread> --t3-open-sessions <n>`. It
   repeats the check and refuses within 5 minutes of `holdUntil`. Exit 3 means it didn't
   restart, so abort. After any other exit, never run it again, and go on to steps 6 and 7.
6. **Acquire once** through the same route, then run `glass pid`.
7. **Finish.** Run `glass finish --thread <your thread> --result acquired|failed --new-pid <pid>`,
   leaving out `--new-pid` if there's no PID. A `failed` result blocks more restarts until
   the user runs `glass clear`.

## On every exit

If you stop after a successful claim and before the restart runs, run `glass abort --thread <your thread>
--reason <why>`. That covers a refused check, the deadline passing, and any session still
silent or busy. After `finish` or `abort`, list sessions again, and tell each held session
that's still active, in `steer` mode, that the hold is over and needs no reply. Report what happened, and stop device work if you have no device.

A success lets the work continue, but it doesn't prove what caused the failure.

Treat a change to SimLock's code as a proposal for the user, after this recovery has failed.
State what evidence supports its values. Offline tests prove the change's behavior, not that
it is the remedy.
