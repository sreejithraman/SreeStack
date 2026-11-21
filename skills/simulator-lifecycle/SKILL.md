---
name: simulator-lifecycle
description: Use before touching an iOS simulator or Android emulator, or before running simctl, adb, emulator or xcodebuild for a simulator, or agent-device. Simlock shares these devices between agents and has rules every agent must follow.
---

# Simulator Lifecycle

Use SimLock to isolate disposable simulator and emulator runs without colliding with
sibling sessions or retained inspection devices. Start from a simulator or emulator task,
its host route, and whether the target is disposable or a retained inspection device. Leave
a run receipt, any required evidence exported before teardown, and a released lease or an
explicitly recorded retention. You are done when every run-owned consumer has stopped, the
lease is released (or explicitly retained with an owner) and teardown status is confirmed, or
an exact host/capacity blocker is reported.

Follow the host's live device contract first. In T3, read
[T3 device routing and recovery](references/t3.md) before acquisition, interaction, setup,
or recovery. For retained inspection targets or disposable runs, read
[run and handoff conventions](references/workflow.md) before touching a device; the
disposable-pool checks below never authorize resetting or enrolling a retained device.

For disposable simulator/emulator work:

1. Check setup: run `simlock whoami`. If `simlock` is not found or `whoami` fails, tell the
   user and do not touch any device.
2. Read the installed rules in every session: run `simlock instructions` and follow them
   rather than relying on memory.

Apply the [run ownership guard](references/workflow.md#choose-the-route-before-acquiring)
before following reuse, release, or cancellation advice: a shared requester may belong to a
sibling run.

Check the machine that runs the device once before acquiring or booting it. Read free space
with `df -h "$HOME"` and the 1-minute load average with `uptime`, and compare the load with
the CPU count (`sysctl -n hw.logicalcpu` or `nproc`). Less than 10% free space, or a load
above twice the CPU count, is critical: hold device work, continue independent work, and
recheck when that runs out. If it is still critical, report both numbers as the blocker.
Free space only through [Cleanup](../cleanup/SKILL.md)'s ownership checks. On a remote
device host, single-quote the commands so `$HOME` expands there, such as
`ssh <host> 'df -h "$HOME"; uptime; sysctl -n hw.logicalcpu'`; if the host offers no shell,
report the check as not run and continue under the host's controls.

Before acquiring, finish eligible device-independent builds with
[Mac Work handoffs](../mac-work/references/handoffs.md); command admission does not cover
automatic T3 device boots. Read [project runner integration](references/project-runners.md)
when changing normal test commands, and [setup and rollout](references/setup.md) for
authorized adoption.

If acquisition, runner preparation, or a device command fails, read
[when a session fails](references/workflow.md#when-a-session-fails) before retrying. A hold
message from a session using [break glass](references/break-glass.md) says what to do.
