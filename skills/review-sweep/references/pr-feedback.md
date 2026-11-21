# PR feedback

## Collect

Take threads, comments, reviews, and check results from the caller's complete PR
state read (such as `pr_state.py`), or read every page via `gh` when running
standalone. An incomplete read means feedback isn't proven. Older open threads
still need a decision against the current code.

Give each item the finding schema with its GitHub ID, location, claim,
and source. Merge duplicates and keep their IDs. Take a failing or missing check in the same
pass, with its log from `gh run view` or the workflow file that explains it. Rerun a flaky one
with `gh run rerun --failed`, and return it as pending for the PR's watcher. Human and bot comments get the same treatment.

## Reply and resolve

Reply to a thread with `addPullRequestReviewThreadReply` and close it with
`resolveReviewThread`, using the `id` from `pr_state`.

- **No edit needed:** reply with the reason and evidence, then resolve rejected, handled,
  duplicate, or noise threads.
- **Deferred:** when a durable home is already recorded (issue/snip link or
  caller tracking ID), reply with the decision and that home, then resolve. When
  a parent workflow must route the deferral first, leave the thread open and
  return a **held deferred reply** keyed by thread ID and canonical issue ID so
  the caller can reply with the recorded home and resolve it once routed (never
  resolve on an unbacked prose promise).
- **Stop:** reply naming who decides under classification's Continue or stop rules,
  and keep the thread open. Once the stop is settled, reply and resolve as for its result.
- **Accepted edit:** return a held reply to your caller. Once the fix is in the remote head, the
  caller replies with that head and evidence, and resolves. Read feedback again for anything new.

A comment or review body has no thread to resolve. Record its decision in your report, and answer
with `gh pr comment` when its author needs one.

## Finish

Finish when every finding, including comments and review bodies, has a disposition, replies are
posted or held for your caller, only stops and held replies leave a thread open, and approval
state is recorded.
