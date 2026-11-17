---
name: mac-work
description: Use when routing heavy commands on a shared Mac or qualifying its admission queue.
---

# Mac Work

Route heavy commands through one host-wide admission owner. Start with the
command, owner, worktree, revision and separate queue/execution deadlines.
Leave a stable task receipt and a result the caller can open in T3. Done means
the command and its owned descendants have stopped before capacity is released.

**Admission is blocked at the upstream fitness gate.** The pinned candidate
frees capacity while owned descendants still run. No production heavy-command
launcher or shared host installation is provided yet. Preserve existing holds;
return the counterexamples instead of routing work through this candidate.

To reproduce qualification, use [private runtime setup](references/setup.md)
and `scripts/fitness.py --help`. The tool uses actual upstream CLI/MCP processes,
private queue state and harmless synthetic commands. It rejects version or
source drift before invoking a queue. Exit 0 means all selected assertions
passed; 1 means a counterexample; 2 means setup or observation was blocked.
A partial selection does not qualify the candidate.

Read [fitness findings](references/fitness.md) and the
[bounded repair proposal](references/repair.md) before changing admission.
The proposal distinguishes the fixed qualification CLI from the unsettled
operational CLI/config/receipt contract. Requalify every repair before exposing
heavy-command execution or activating any host configuration.

The parent owns integration and release in the [spec and tasks](references/plan.md).
SimLock keeps device lifecycle ownership. T3's exact bound driver keeps UI
ownership; its admission integration remains pending. Keep the existing device
limits and slim/full choices until the later task's proof passes.
