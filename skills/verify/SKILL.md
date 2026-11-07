---
name: verify
description: Use when proving a change, a named workflow, or the whole app works in the real product, checking whether a reported behavior reproduces, auditing an interface, stress-testing a component with edge data, creating or changing a verification map, or model-checking an invariant or race, or when a change or request touches a formal check.
---

# Verify

Prove claims about a change through the entry points its users reach. Start from the
claims in a brief, a request, or a diff. Leave a verdict and evidence for each one. You
are done when every selected assertion has a verdict and its evidence is still
readable after cleanup.

An **assertion** is one observable expected result. A **workflow** is one user path
through the product, with its assertions.

For an invariant, a race, or event ordering you were asked to prove, a request to maintain
a formal check, or changed code that an existing formal check covers, read [formal verification](references/formal-verification.md).
It owns its prerequisites, verdicts, and repo writes. The steps below apply to product
claims. A model doesn't replace them, and ordinary workflows need no new model. Look for
existing formal checks by function, not by name.

Keep plans, scripts, and evidence in the session scratch directory. Verify writes no
docs in any repo, including a repo's verification map. If the user asks to create or
change a map, follow [verification maps](../setup-sreestack/references/verification-map.md).

## Choose what to prove

Read the request, the session, the diff, and the project instructions.

If the project has a verification map, read its index and shared setup, then the
recipes for the affected features. Follow links when the linked behavior is affected.
Without an index, search for recipe files recursively. A map is working knowledge. It
doesn't show the whole product is covered.

Without a map, write a temporary plan. A project verification skill can supply launch
or control facts if its invocation policy allows it. It isn't a map, and you leave it
in place. Check its facts against this app, revision, and environment. Reach an
explicit-only skill only through the user.

Choose the coverage:

- **This change (default):** every changed behavior, plus the workflows that share its
  dependencies.
- **A named workflow, surface, or suite:** when the request names one. It needs no diff.
  Each required test in a named suite is an assertion.
- **Whole app:** when asked. Inventory the user-facing capabilities, with every mapped
  feature and each important surface the map lacks. Disclose gaps.

Cover the main path, the error and edge cases the change can reach, persistence, and
each entry point that behaves differently. Use a recipe's required assertions in full.

For stateful flows, pick the sequences the product supports: repeated input while
pending, failure then retry, interruption, cancellation, and late completion after
cancellation or replacement. Include sequences found during architecture work, and
take their expected results from product requirements, not from the transition table.
Reducer or state machine tests alone don't show the product connects these paths.

Before you drive anything, write the expected result of each assertion. Every assertion
needs both:

- **An independent expectation:** a requirement, a spec, a trusted example, a named
  design or specialist standard, or prior behavior you observed on the base. An
  expectation taken from what the new code does proves nothing.
- **A way to run it:** a public entry point you can reach here.

If either is missing, find it or ask for it. Otherwise mark the assertion `blocked`.
Done: each changed behavior has an assertion, or a stated reason for leaving it out.

Add what the work needs:

- Component stress tests or content-dependent failures: [edge data](references/edge-data.md).
- A whole-surface visual, interaction, or accessibility audit, or checks that involve
  accessibility or platform materials: [interface review](references/interface-review.md).
- Deciding how to judge an ambitious target, a consequential change, competing
  candidates, or qualitative work: [acceptance guidance](../reframe/references/acceptance.md).
- Performance claims: [measurement validity](../diagnosing-bugs/references/measurement-validity.md).

## Get a known starting point

Read the guide for the platform: [web](references/web.md), [iOS](references/ios.md),
[macOS](references/macos.md), or [terminal and services](references/terminal-and-service.md).
For anything else, use the best tool that shows the public interaction and its result.
For simulators and emulators, follow [Simulator Lifecycle](../simulator-lifecycle/SKILL.md).
For a physical-device install, read [device delivery](../show-me/references/native-device-delivery.md).
For login or authenticated commands, read
[authenticated verification](references/authenticated-verification.md) before you
retrieve credentials or drive a login.

Find the launch command, readiness signal, prerequisites, fixtures, and isolation
options in the repo and the environment. Follow
[Orchestration's UI rule](../orchestration/references/models.md#operate-a-ui) for
who drives an interface and with which model. The driver reports what it saw, and you
keep the verdicts.

Prefer a script you can rerun over steps by hand. Put repeatable setup, driving, and
evidence capture in it, and give the rerun command in your report.

**Run a read-only doctor before you drive.** Run the map's doctor if it has one, then
check whatever it doesn't cover, without changing state:

- The right instance and the right build, including uncommitted changes.
- The right port or target, and the required connections.
- The right account and role, and the right test or live mode for each external
  provider.
- Readiness for this workflow, after initialization, migrations, and fixtures. A
  responsive port or a database health check can pass before that. Check what the signal
  proves.

Bound every wait with an observable condition and a deadline. If the doctor fails,
fix the setup or report it. Keep the failing command and its output, and separate a
missing prerequisite from a product failure. Missing fixtures keep their assertions:
mark them `blocked`, or `failed` if the product's setup should have supplied them.

For first-run behavior, launch from an isolated empty data profile where the product
supports one. Routine checks can reuse known state and leave user data alone. If a
substitute environment did setup the real target won't do, those steps stay unverified,
and the assertions that depend on the target can't pass.

**Keep runs apart.** Before concurrent or long checks, find what tasks and worktrees
share. Apply [Separate Before Serializing Shared State](../engineering-principles/references/separate-before-serializing-shared-state.md),
and leave active owners alone. Reuse a launched instance for related checks, and
serialize drives that share mutable state. Changing a harness needs the task's
authorization. If you change its isolation, prove two simultaneous runs reach their own
resources, then stop one and confirm the other still works.

**Limit side effects.** Prefer disposable accounts, fixtures, and provider test modes.
Check what a dry-run or test mode really changes. Take an irreversible or externally
visible action only within the task's authorization. A request to verify doesn't
authorize real money, live customer data, or messages to real people unless the user
names that action. Otherwise stop at the last safe step and mark the rest `blocked`. Record credential names and setup paths, never values.
Remove secrets and private data from evidence.

## Show it red first

When a claim says a behavior changed or a bug is fixed, reproduce the old result before
you trust the new one. Run the same check, with the same environment and fixtures,
against the base revision, in a disposable checkout if the change is already in place,
and keep both results. Run the doctor there too. Red counts only when the old side runs
and shows the old behavior. A setup error isn't red.

A check that passes on both sides proves nothing: change it until it tells them apart, or
mark the claim `untested`. If you can't run the old side, revert the change in a disposable
copy and run the check there. If that fails too, mark the claim `untested` and say why.
Reuse red evidence from `tdd` or `diagnosing-bugs` if the method matches.

## Drive

Exercise the workflows through their public interfaces. A CLI can drive a UI. Internal
setters and test-only endpoints can prepare state or help diagnosis, but they can't prove
a public interaction works.

**By hand:** Wait for the starting state to settle. Inspect the rendered view and the
semantic tree when available. Do one meaningful action, then inspect the result before
the next one. Target roles, labels, and identifiers. Use coordinates only when no stable
target exists, and take them from current state.

**With a suite:** Find the targeted checks for the changed behavior and shared
dependencies. Before running them, connect each assertion to a real check, and confirm
the target, fixtures, filters, optional checks, and retries. Afterward, reconcile every
selected test with its result: actual skips, unmet preconditions, and unfinished tests.
Count a duplicate test once for coverage and keep every attempt's outcome. Exercise
uncovered assertions yourself. A green command, zero tests, partial results, or a passing
rerun can't establish a pass. Keep required broader gates, and report any you didn't run.

**When something doesn't change:** Record it before you retry. Retry once, only when
evidence shows the target moved or the interface hadn't settled, and record the retry as
its own attempt. A repeated failure is evidence. After a stuck interface or a surprising
result, check instance health and restore known state, even if the process looks fine.

**Intermittent reports:** Choose the attempt count before you start, and use it on both
sides. Use about 3 divided by the failure rate, so about 30 attempts for 1 in 10. Restore
equivalent state with disposable or uniquely named data before each planned attempt.
Record every outcome, and count recovery retries separately.

## Judge

Compare each observed result with the expected result you wrote down. Check that it
works and that it's usable: layout, readability, focus, input, navigation, and loading,
empty, disabled, and error states.

For saved data or output files, use a fresh read that doesn't go through the current
screen, and record the value or file you read.

If tests, fixtures, or measurements changed with the code, check that they still detect
the failure and measure the same work.

Sort each mismatch:

- **Drift:** a recipe or a project doc is wrong. Fix the steps for this run, drive again,
  and report the drift. Leave the doc as it is.
- **Harness gap:** the tooling can't show the result. Fix it within the task's scope, or
  mark the assertion `blocked`.
- **Product failure:** the assertion is `failed`. Change the product only if the task
  includes fixing it.

Keep the expectation you wrote. Weakening an assertion to accept a defect is a false pass.

Call a failure pre-existing only with a runtime baseline that matches the source,
including local changes, plus the environment, fixtures, and test method. Matching source
or another revision's results don't show that. State the limits of the comparison.

## Clean up and report

Keep failed attempts and the screenshots, snapshots, logs, transcripts, or responses
behind each verdict. Visual claims need visual captures.

Stop only the processes and sessions this run started, and remove their disposable data,
after success or failure. Leave reused services and source fixtures running. Then open
the kept evidence to confirm it survived.

Give each workflow and entry point its actions, expected and observed results, and
evidence location. Give every assertion one verdict:

- `passed`: the observed result matched.
- `failed`: the observed result differed.
- `blocked`: a missing prerequisite stopped the check.
- `untested`: no check ran, or for a claimed change, none told the old result from the new.

A workflow passes only when every required assertion passes. Otherwise it takes the
first of `failed`, `blocked`, `untested` that applies.

Report defect reproduction separately, as `reproduced` or `not reproduced in N attempts`.
A defect reproduced on the build under test fails its assertion. Failing to reproduce a
defect doesn't show it is fixed. Mark a fix claim `passed` only when the defect reproduced
on the old behavior and a check tied to its cause now passes. Otherwise leave it `untested`
and report the attempts, or `blocked` if it has no independent expectation.

Name anything left out, surfaces with no recipe, blockers, and drift. For drift, say
what the map or doc should now read, and that `setup-sreestack` can apply it.

If a step needs the user, give the exact action and where to do it, keep going on
independent checks, and resume when they finish. Label what they did and saw as
user-reported. To show results or let the user try
them, use [Show Me](../show-me/SKILL.md) with this evidence.
