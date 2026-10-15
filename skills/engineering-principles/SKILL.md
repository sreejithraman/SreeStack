---
name: engineering-principles
description: Guide engineering design and implementation decisions. Use when choosing data models or interfaces, simplifying code, planning migrations, handling retries or shared state, evaluating evidence, or organizing substantial work.
---

# Engineering Principles

Use these principles to choose the shape of the work. The relevant workflow
still owns its procedure, checks, and completion criteria. Apply them within
the user's scope, product requirements, and execution permissions.

Read the sections that match the decision before acting:

- **Data, types, interfaces, or product tradeoffs:**
  [Data and interface decisions](references/design.md). Start here before writing new stateful logic
  or extending a shape that callers must coordinate.
- **Refactoring, another layer, or code that is hard to follow:**
  [Simplifying a change](references/simplicity.md). Check existing consumers before a cut.
- **Retries, concurrent writers, or a caller migration:**
  [State, retries, and migration](references/state-and-migrations.md). Establish the
  ownership and compatibility requirements before choosing locks or adapters.
- **Repeated failed fixes, competing designs, tests, or a measured claim:**
  [Evidence for a decision](references/evidence.md). Choose a check that can distinguish the
  alternatives and use the relevant verification or diagnosis workflow.
- **Sweeps, delegation, long tasks, or repeated instructions:**
  [Executing substantial work](references/execution.md). Choose rerunnable tools, verifiable
  increments, and durable enforcement where they improve the work.

A named principle selects its matching heading in those references. For a
cross-cutting task, read each affected reference; a small decision needs only
its relevant sections. Give delegates the applicable source paths and the
decision or proof they own through [Orchestration](../orchestration/SKILL.md).

Explain the concrete choice and its evidence when it matters to the result.
Keep proposed checks distinct from checks run. A principle name or a completed
checklist does not establish that the behavior works.
