# CI and reviews

## Assess current state

Read the PR's head, immediate base, mergeability, checks, and review state.
Use the GitHub connector for summaries and `gh` for Actions jobs and logs.
Checks may target the head or GitHub's test merge; verify the current target.
Re-read after a push, base change, or watcher wake. Earlier results do not prove
the current state ready.

Collect required and visible optional checks. Explain missing expected checks,
including workflows filtered out by a stacked PR's base or draft status.
Inspect failures, timeouts, cancellations, and action-required results:

- Send code-caused failures and [review findings](pr-feedback.md) together to
  one [review-sweep](../../review-sweep/SKILL.md) pass. Verify accepted edits and
  require applicable complete-scope review evidence before publication; run
  [delivery's review step](../SKILL.md#deliver-changes) if it is missing or stale.
  Then [publish](publish.md), [post held replies and resolve threads](pr-feedback.md#reply-and-resolve),
  and reassess checks and feedback.
- Retry a proven infrastructure or flaky-test failure once when evidence
  supports it. Record the outcome.
- Report configuration and external blockers with the exact condition, owner,
  and required action.

## Wait for events

Only the parent thread owning the PR watches it. Delegated children return
their results to the parent. Use one watcher per PR.

Handle existing checks and comments first. While checks or reviews are pending,
or monitoring is explicitly requested, call `watch_pull_request` and end the
turn. T3 wakes the thread for check results, comments, reviews, or conflicts.
Follow live tool instructions; a wake supplies news to assess, not merge
authorization. On an event needing no action, keep waiting without filler
messages. Watches persist across pushes; reassess the new head rather than
starting a second watcher.
See the [T3 watch contract](https://github.com/pingdotgg/t3code/blob/c71ca063dfcd8c2e3dcb2bd92adbb2180cbbece3/apps/server/src/mcp/toolkits/pullRequests/tools.ts#L290).

Before handing back control because the PR is ready, blocked, or needs a user
decision, call `unwatch_pull_request`. Ending a turn to await watcher events
keeps the watch active. GitHub must confirm any merge or close.

If watching stops because GitHub cannot be read, inspect the error and rate
limits (`gh api rate_limit`) before retrying. Use REST reads if GraphQL alone
is exhausted. Report an exhausted limit and its reset time rather than
repeatedly restarting the watch.

Outside T3, use the host's supported PR watcher. If no watcher is available,
report the pending state and capability gap. Do not create polling or sleep
loops, run `gh --watch`, or duplicate the watch with a scheduled task.

## Ready or blocked

Ready means required checks pass for the current target, expected checks are
present or explained, every non-success result has a disposition, and feedback
collection and handling are complete. Account for open threads and pending
human approval; report any unmet repository requirement. Check base freshness
and mergeability yourself: the watcher reports conflicts, not every base change.
Incorporate the base when repository policy or affected verification requires
it; use `gh-stack` for stack updates. Refresh verification against the updated
base before claiming readiness.

For a draft, finish when every started check has a terminal disposition, no
code-caused failure remains, and checks omitted by draft policy are recorded.
Pending work stays pending. Use [merge](../../merge/SKILL.md) only when merging
was requested; queued submission is not a confirmed merge.
