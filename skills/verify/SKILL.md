---
name: verify
description: Use when proving a change, a named workflow, or the whole app works in the real product, checking whether a reported behavior reproduces, auditing an interface, stress-testing a component with edge data, creating or changing a verification map, or model-checking an invariant or race, or when a change or request touches a formal check.
---

# Verify

Prove claims about a change through the entry points its users reach. Start from
claims in a brief, request, or diff. Leave a verdict and readable evidence for
each claim. You are done when every selected assertion has a verdict and its kept
proof survives cleanup.

An **assertion** is one observable expected result; a **workflow** is one user
path with its assertions.

- **Formal checks:** for an invariant, race, or event ordering to prove, a
  request to maintain a formal check, or changed code covered by an existing
  formal check (search by function, not name), read
  [formal verification](references/formal-verification.md). It owns its
  prerequisites, verdicts, and repo writes. A model does not replace product
  claims, and ordinary workflows need no new model.
- **Verification maps:** Verify writes no docs in any repo. If the user asks to
  create or change a map, route to
  [verification maps](../setup-sreestack/references/verification-map.md).

## Keep proof, not runs

Separate disposable **run scratch** from **kept proof** from the start:

- **Run scratch** holds reproducible artifacts: plans, helper/rerun scripts,
  per-step snapshots, result bundles, intermediate reruns, and non-reused builds.
  Create it with `mktemp -d` (under `$TMPDIR`) and delete it when the run ends,
  pass or fail. Only a checkout's sole builder leaves builds in the build
  system's default path (see [iOS build output](references/ios.md#build-output)).
  Record builds by build identity rather than copying builds or inputs such as
  source trees or Pods.
- **Kept proof** holds only what proves the verdicts: the verdict table, captures
  behind each verdict (visual for visual claims: screenshots, recordings,
  transcripts, responses), cited log excerpts, and build identity (commit SHA
  plus hash of the installed or tested product). For repeated attempts, keep
  outcome counts plus captures only for open findings.

Write each run's kept proof to a new folder. In a linked worktree on a branch
(where `git rev-parse --path-format=absolute --git-dir --git-common-dir` prints
two distinct paths and `git symbolic-ref -q HEAD` succeeds), store it in that
worktree's private Git directory so Git ignores it and worktree removal deletes it:

```sh
proof=$(git rev-parse --path-format=absolute --git-path verify-proof)
mkdir -p "$proof" && mktemp -d "$proof/$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short HEAD)-XXXXXX"
```

Otherwise put it in session scratch (or `$TMPDIR` if the host has none) and state
in the report that it lasts only for the session.

## Choose what to prove

Read the request, session context, diff, and project instructions.

- **With a verification map:** read its index, shared setup, and affected feature
  recipes (following links when linked behavior is affected; search recursively if
  there is no index). A map is working knowledge, not proof of whole-app coverage.
- **Without a map:** write a temporary plan in run scratch. An existing project
  verification skill may supply launch or control facts if its invocation policy
  allows it; verify those facts against the current app, revision, and environment,
  and leave it in place. Reach explicit-only skills only through the user.

Pick coverage by request:

- **This change (default):** every changed behavior and workflows sharing its
  dependencies.
- **Named workflow, surface, or suite:** needs no diff; each required test in a
  named suite is an assertion.
- **Whole app:** when asked; inventory user-facing capabilities across mapped
  features and important unmapped surfaces, disclosing gaps.

Cover the main path, reachable error and edge cases, persistence, distinct entry
points, and every required assertion in a recipe. For stateful flows, exercise
supported sequences—repeated input while pending, failure/retry, interruption,
cancellation, and late completion—including architecture-discovered sequences,
with expectations from product requirements rather than the transition table
(reducer or unit tests alone do not prove product wiring).

Write each assertion's expected result before driving. Every assertion requires:
1. **An independent expectation:** a requirement, spec, trusted example, design
   standard, or prior base behavior (never derived from the new code).
2. **A runnable public entry point** reachable here.

Find or ask for either if missing; otherwise mark the assertion `blocked`.
Done when every changed behavior has an assertion or a stated reason for omission.

Add specialist references only when needed:
- Component stress tests or content-dependent failures: [edge data](references/edge-data.md).
- Visual, interaction, accessibility, or platform-material audits:
  [interface review](references/interface-review.md).
- Performance claims:
  [measurement validity](../engineering-principles/references/measurement-validity.md).

## Get a known starting point

Load the matching platform guide: [web](references/web.md), [iOS](references/ios.md),
[macOS](references/macos.md), or
[terminal and services](references/terminal-and-service.md). For simulators and
emulators, follow [Simulator Lifecycle](../simulator-lifecycle/SKILL.md). For
physical-device installs, read
[device delivery](../show-me/references/native-device-delivery.md). For login or
authenticated commands, read
[authenticated verification](references/authenticated-verification.md) before
retrieving credentials or driving a login. Follow
[Orchestration's UI rule](../orchestration/references/models.md#operate-a-ui) for
who drives an interface; the driver reports observations and you keep verdicts.

Prefer a run-scratch script for repeatable setup, driving, and capture; when a
check repeats on a later commit, offer to turn it into a committed test or recipe.

- **Run a read-only doctor first:** run the map's doctor if present, then check
  anything uncovered without mutating state—right instance and build (including
  uncommitted changes), right port/target/connections, right account/role and
  provider test vs live mode, and real workflow readiness after initialization,
  migrations, and fixtures (a live port or DB health check alone is insufficient).
  Bound every wait with an observable condition and deadline. Separate missing
  prerequisites from product failures; missing fixtures leave assertions `blocked`
  (or `failed` if product setup should supply them).
- **Profiles and targets:** test first-run flows from an isolated empty profile
  where supported; routine checks can reuse known state while leaving user data
  untouched. Steps performed by a substitute environment instead of the real
  target stay unverified.
- **Keep runs apart:** before concurrent or long checks, follow
  [Separate Before Serializing Shared State](../engineering-principles/references/separate-before-serializing-shared-state.md)
  and leave active owners alone. Reuse a launched instance for related checks and
  serialize drives sharing mutable state. Harness isolation changes require task
  authorization plus proof that two simultaneous runs stay isolated and stopping
  one leaves the other working.
- **Limit side effects:** use disposable accounts, fixtures, and verified
  dry-run/test modes. Never touch real money, live customer data, or external
  recipients unless the user explicitly names that action; stop at the last safe
  step and mark the rest `blocked`. Record credential names and setup paths, never
  values, and redact secrets or private data from kept proof.

## Show it red first

For any claimed behavior change or bug fix, reproduce the old behavior before
trusting the new one: run the exact same check, environment, fixtures, and doctor
against the base revision (in a disposable checkout if changes are already in
place) and store both results in the same run folder. Red counts only when the old
side runs and exhibits the old behavior—a setup error is not red.

If the check passes on both sides, refine it until it discriminates or mark the
claim `untested`. If the base cannot run directly, revert the change in a
disposable copy; if that also fails, mark `untested` and explain why. Reuse
matching red evidence from `tdd` or `diagnosing-bugs` when the method matches.

## Drive

Exercise public interfaces only; internal setters and test-only endpoints can
prepare state or aid diagnosis, never prove public interaction.

- **By hand:** wait for settled state, inspect rendered view and semantic tree,
  perform one meaningful action, and inspect before the next. Target roles,
  labels, and identifiers; use current-state coordinates only when no stable
  target exists.
- **With a suite:** map each assertion to a real check; confirm target, fixtures,
  filters, optional checks, and retries. Afterward reconcile every selected test
  with actual skips, unmet preconditions, and unfinished runs; count duplicate
  tests once and record every attempt. Exercise uncovered assertions yourself. A
  green command, zero tests, partial results, or a passing rerun never establishes
  a pass. Keep required broader gates and report any skipped.
- **Unchanged or stuck state:** record the observation before retrying. Retry once
  only when evidence shows the target moved or had not settled, recording the
  retry as its own attempt. After a stuck or surprising state, verify instance
  health and restore known state even if the process looks alive.
- **Intermittent reports:** choose an attempt count up front (`~3 / failure_rate`,
  e.g., ~30 for 1 in 10) for both sides, restore fresh equivalent state before
  each attempt, record every outcome, and count recovery retries separately.

## Judge

Compare observed results against written expectations plus usability (layout,
readability, focus, input, navigation, and loading, empty, disabled, and error
states). Verify saved data or output files via a fresh read outside the current
screen and record what was read. If tests, fixtures, or measurements changed,
confirm they still detect failure and measure the same work.

Classify every mismatch:
- **Drift:** recipe or doc is wrong; adjust steps for this run, rerun, report the
  drift, and leave the doc untouched.
- **Harness gap:** tooling cannot observe the result; fix within task scope or
  mark `blocked`.
- **Product failure:** mark `failed`; fix only if the task includes fixing it.

Never weaken an assertion to accept a defect. Call a failure pre-existing only
with a matching runtime baseline (same source including local changes,
environment, fixtures, and method), stating comparison limits.

## Clean up and report

Pass or fail, stop only processes and sessions this run started, remove their
disposable data, delete run scratch, and leave reused services and source fixtures
alone. Open the kept proof afterward to confirm it survived.

Report each workflow's entry point, actions, expected and observed results, kept
proof absolute path, and one verdict per assertion:
- `passed`: observed result matched.
- `failed`: observed result differed.
- `blocked`: missing prerequisite prevented the check.
- `untested`: no check ran, or none distinguished old behavior from new.

A workflow passes only if every required assertion passes; otherwise it takes the
first applicable status of `failed`, `blocked`, `untested`.

Report defect reproduction separately as `reproduced` or `not reproduced in N
attempts`. Reproducing a defect on the build under test fails its assertion;
failing to reproduce does not prove a fix. Mark a fix claim `passed` only when the
defect reproduced on the old behavior and a cause-tied check now passes (otherwise
`untested`, or `blocked` without an independent expectation).

Name omissions, unmapped surfaces, blockers, and drift (stating what the map or
doc should read). For user-only steps, give the exact action and location,
continue independent checks, and label results `user-reported`. Use
[Show Me](../show-me/SKILL.md) with this evidence when showing results or letting
the user try them.
