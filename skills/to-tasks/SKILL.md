---
name: to-tasks
description: Use when a spec, plan, or list of work needs splitting into tasks that can run in parallel, or when asked to create or publish tickets for it.
---

# To Tasks

Split work into tasks that can run side by side. Start from a spec, a plan, an issue, or the
conversation. Leave a task list an owner can start from. You are done when every outcome in the
input belongs to a task, each task delivers one result, and every pair that runs together passes
the [parallelism test](#parallelism-test).

This skill plans. Whoever called it starts the tasks and owns integration.

1. **Read the input.** Read a linked spec or issue in full, with its comments. Read enough of the
   code to test each pair. Use the project's glossary terms, and respect ADRs in the area. Nothing
   the input puts out of scope becomes a task.

2. **Settle shared contracts first.** Find what several tasks would have to agree on, such as a
   schema, an interface, or a name. Take it from the input, or make settling it the first task.
   Each settled contract unlocks more parallel work. A decision only the user can make goes under
   Inputs, as step 5 says.

3. **Cut the tasks.** Each task cuts a narrow, complete path through every layer, such as schema,
   API, UI, and tests, not a slice of one layer. It delivers one result you can check on its own.
   Split a task that delivers two. Size tasks by that result and the parallelism test, never by
   context. Put prefactoring first, when it makes the rest easier. A contract or prefactoring task
   delivers what it unlocks. Make a destructive or outward-facing action its own task, apart from
   the work that builds it. One mechanical change that breaks many call sites at once can't be cut
   this way: follow [wide refactors](references/wide-refactors.md).

4. **Test every pair.** Apply the [parallelism test](#parallelism-test) to each pair that could run
   together. When a pair fails, add a blocking edge if one needs the other's output or decision,
   note how they share a resource under Inputs, or merge them.

5. **Write the list.** Give each task these fields:

   ```text
   1. Title
      Outcome: what works when it's done, from the user's side, not a list of layers
      Proof: how to check that it works
      Inputs: what it needs but won't build, including any user approval or answer, or None
      Blocked by: tasks that must deliver first, or None
      Finish line: land it, or stop for the user
   ```

   Use the caller's finish line. Without one, land work that is settled and reversible, and stop
   the rest. **Settled** means the user knows what they want, or checks can judge it.

   Whatever the finish line, a task needs the user before it starts when its outcome is unclear,
   it's destructive, outward-facing, or hard to undo, or the split around it needs their judgment.
   Name the one approval or answer under Inputs on every task it affects, and return it in the
   list. That approval covers the whole task. Such a task holds up only what it blocks. A task
   waiting only on a decision can still start provisionally under [Ready](#ready).

6. **Publish only when the user asks.** Follow [publish](references/publish.md). Otherwise return
   the list.

## Parallelism test

Two tasks can run together when all of these hold:

- Each can finish and be checked against fixed inputs.
- Neither waits on, interprets, or revises around the other's decisions.
- Writes, accounts, fixtures, ports, and devices are independent or explicitly coordinated.
- One owner is responsible for integration.

Separate files or worktrees alone don't prove independence.

## Ready

A task is ready when its blockers have delivered what it needs, its inputs exist, including any
user approval, its proof can show the result, and it passes the parallelism test against the tasks
running beside it. An empty "Blocked by" alone doesn't make a task ready.

**Provisional start:** when an open decision is a task's only missing input and the recommended
option is reversible, the task is ready to build on that option as a stated assumption. Name the
assumption and the decision under Inputs. Its acceptance and landing wait for the answer, and
destructive or outward-facing steps still wait for the user. Tasks that don't depend on the
decision never wait on it.
