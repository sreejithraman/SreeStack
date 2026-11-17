---
name: mac-work
description: Use when routing foreground build/test commands on a shared Mac or qualifying its admission queue.
---

# Mac Work

Run foreground heavy commands through the canonical shared `mac-work` route.
Start with a stable operation ID, owner, argv and absolute Git worktree. Leave a
receipt and log the caller can open in T3. Done means the owned group stopped
before upstream capacity was released, or unresolved capacity remains inspectable.

The user-approved pilot supports commands that wait for all heavy work in their
launched process group. Use foreground options or verified project wrappers.
Background/shared daemons and escaping groups/sessions are unsupported; this is
not OS containment. Keep existing holds with their owners until parent integration.

Use the one installed root's `bin/mac-work` across providers/projects. For setup,
CLI/MCP contracts and maintenance, read [foreground runner](references/runner.md).
Routine calls are `run --id ... --owner ... --worktree ... --queue-seconds ...
--execution-seconds ... -- COMMAND...`, `status --id ...`, and `cancel --id ...`.
`--json` exposes task/operation IDs, closure state, receipt and log paths. An
observation wait does not cancel a task. Status never submits. Same ID/input is
idempotent; changed inputs conflict. Do not replace this route with raw queue flags.

On `recovery-pending`, inspect the receipt/log and read status after verified group
closure. Capacity stays held while ownership is uncertain. Never force-clear or
switch policy to release it. Output is verbatim, not secret redaction; avoid secret
argv/output. Runtime/config/hash drift fails closed instead of running unqueued.

Before device acquisition, use [build/artifact handoffs](references/handoffs.md).
The build must succeed and close before its exact artifacts are consumed. Only
an already-qualified foreground project runner may use `run --handoff BUILD_ID`.
SimLock retains device lifecycle and T3's exact bound driver retains UI ownership.
Automatic T3 boot admission is pending; the command queue does not cover it.
The parent owns real workload/device proof, adoption and release in the
[spec/tasks](references/plan.md). Device limits and slim/full choices stay unchanged.

When changing the dependency, use the [lifecycle recipe](references/lifecycle.md),
[implemented ownership seam](references/repair.md), [original qualification](references/setup.md)
and [counterexamples](references/fitness.md). Preserve the [license/change notice](NOTICE.md).
