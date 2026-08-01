# PR Feedback

Use these rules when the current PR has comments, reviews, requested changes, or unresolved threads.

## Collect

Prefer the GitHub connector for PR metadata and flat comment reads. Use `gh` for unresolved thread state, inline context, review summaries, resolution, or connector gaps.

Collect:

- unresolved inline threads
- review-level comments
- requested-changes summaries
- conversation comments with technical claims
- current approval state
- enough diff context to verify each claim

Bind the collection to the current PR head. Re-read feedback after a push because the diff and review state may have changed.

## Decide And Fix

Map each technical item into the `/review-sweep` finding schema with its GitHub id, location, claim, and source. Merge duplicate claims while retaining every source id.

Return the normalized findings to the single `/review-sweep` pass for the current watch. Keep requests for product or behavior choices as parent-owned decisions.

## Reply And Resolve

Reply immediately for dispositions that need no code edit. Resolve those threads when the finding is rejected with evidence, already handled, duplicate, source noise, or deliberately deferred to the parent.

For an accepted finding that changes the local diff, hold the reply and resolution until `/review-fix-loop` passes, the fix is pushed, and the recorded remote head contains it. Then reply with the published head and evidence before resolving the thread. Keep a thread open when more author work or a user decision is required.

Missing approval is a waiting-for-human state. It becomes a blocker only when the requested completion state requires that approval now.

## Completion

Feedback handling is complete when every collected item has a disposition, every required reply is posted against the right remote head, resolved work has no open thread, remaining threads name their owner, and the current approval state is recorded.
