# PR feedback

## Collect and assess

Read unresolved inline threads, review summaries, technical conversation
comments, and approval state, with enough source and diff context to verify
each claim. Prefer the GitHub connector for flat reads; use `gh` for thread
state, resolution, or connector gaps.

Read every relevant page, including inline threads. Incomplete pagination leaves
feedback readiness unproven. Re-read after a push; older unresolved findings
still need a disposition against the current code.

Use the [review-sweep](../../review-sweep/SKILL.md) finding schema: GitHub ID,
location, claim, and source. Merge duplicate claims while retaining their IDs.
The [CI and reviews](ci.md) pass combines these with CI findings. Product and
behavior choices remain parent-owned decisions.

## Reply and resolve

For findings needing no edit, reply with the reason and evidence. Resolve
rejected, already handled, duplicate, or noise threads. Record deliberate
deferrals and their owner; keep threads open when author work or a user decision
remains.

For accepted edits, wait until the fix is pushed and confirmed in the remote
head. Then reply with that head and evidence before resolving. After publication,
post held replies and re-read feedback for anything newly arrived.

Finish when every finding has a disposition, required replies are posted,
resolved work has no open thread, remaining threads name their owner, and
approval state is recorded. Missing approval is a human wait; it blocks only
when the requested completion state requires it.
