---
name: simulator-lifecycle
description: Use before touching an iOS simulator or Android emulator, or before running simctl, adb, emulator or xcodebuild for a simulator, or agent-device. Simlock shares these devices between agents and has rules every agent must follow.
---

Simlock shares iOS simulators and Android emulators between agents. It works only if every agent follows its rules.

Follow the host's device contract first. For retained inspection targets, read
[run and handoff conventions](references/workflow.md) before touching the device;
the disposable-pool checks below do not authorize resetting or enrolling it.

For disposable simulator/emulator work:

1. Check it is set up: run `simlock whoami`. If `simlock` is not found, or `whoami` fails, tell the user and do not touch any device.

2. Get the rules: run `simlock instructions` and follow them. They match the installed Simlock, so read them again in each session instead of relying on memory.

Apply the [run ownership guard](references/workflow.md#choose-the-route-before-acquiring)
before following reuse, release or cancellation advice: a shared requester may
belong to a sibling run.

In T3, acquisition and interactive control must follow its documented route to
the same SimLock lease; an ordinary panel session is not proof of that lease.
Before acquiring, read [run and handoff conventions](references/workflow.md) for
host routing, run evidence, teardown and retention. Use
[project runner integration](references/project-runners.md) when changing normal
test commands, and [setup and rollout](references/setup.md) for authorized adoption.

If acquisition, runner preparation or a device command fails, read
[when a session fails](references/workflow.md#when-a-session-fails) before retrying.

More: [Connect your agent](https://github.com/callstackincubator/simlock/blob/822ea4c47d68cd8f7b1168192c40bbcffa23f4e9/website/src/content/docs/docs/getting-started/connect-your-agent.mdx).
