# CI Watch

Use these rules to watch one PR's checks after each push.

## Bind The Watch

Record the PR number, head SHA, immediate base, and the check target shown by GitHub. A repository may require checks on the head commit or on GitHub's test merge result; follow the PR's current check set.

Results from an earlier head or test merge do not satisfy the current watch.

Collect required checks and visible non-required checks. Compare them with the checks the repository normally expects for this change. A missing expected check is a state to explain, not a passing result.

## Watch

Prefer the GitHub connector for check summaries and `gh` for Actions run discovery, waiting, jobs, and logs. Wait for the current check set to reach terminal results. Report useful progress while checks remain queued or running.

## Diagnose

Inspect failed, timed-out, cancelled, action-required, and missing checks.

Classify each result as:

- **Code finding**: the current diff caused a build, test, type, lint, security, or behavior failure. Add the technical claim to the single `/review-sweep` pass for the current watch.
- **Transient failure**: runner, network, service, or proven flaky-test failure. Rerun the failed work once when the evidence supports a retry, then record the result.
- **Configuration blocker**: an expected workflow did not run, including a base-branch filter that excludes a stacked PR. Report the exact workflow or policy condition.
- **External blocker**: permissions, billing, environment approval, unavailable secrets, or another outside dependency. Report its owner and required action.
- **Superseded**: a newer push replaced the watched state. Discard the old result and bind the watch to the new state.

## Completion

In ready mode, CI is complete when all required checks for the current PR state pass, every expected check is present or explained, each non-success result has one disposition, and no result belongs to a superseded state.

In draft mode, CI is complete when every started check has a terminal disposition, no code-caused failure remains, checks absent under draft policy are recorded, and no result belongs to a superseded state.
