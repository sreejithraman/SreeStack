# Publish tasks

Use the tracker the user named, or the one in `docs/agents/issue-tracker.md`. If a required choice
is unknown, ask the user, who can supply it or run `/setup-sreestack`.

Show the list and ask whether the size feels right, whether each blocker really gates its task, and
whether any task should merge or split. Iterate until the user approves. Skip this only when the
user said to publish without checking.

Publish in dependency order, blockers first, so each edge can name a real task. Leave any parent
issue open and unchanged.

- **Local files:** write one file per task at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`,
  numbered from `01`, with `Status: open` and a `Blocked by: NN, NN` line near the top.
- **A real tracker:** publish one issue per task. Use its native blocking or sub-issue link where
  it has one. Otherwise list blockers in a `Blocked by:` line.

Give each task its fields from the list, with Proof as a checklist, and link any parent issue or
spec.

Leave out file paths and code, which go stale. A prototype snippet can stay
when it records a decision better than prose can, such as a state machine, schema, or type shape.
Trim it to the decision, and say it came from a prototype.
