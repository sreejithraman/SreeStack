---
name: diagnosing-bugs
description: Use when the user asks to diagnose a failure or reports a bug or unexplained slowness.
---

# Diagnosing Bugs

Isolate the cause of a reported failure or slowdown through a tight, repeatable
signal, then repair and lock it down when fixes are in scope. Start from a user
symptom, failure report, or captured artifact. Leave an evidence-backed root
cause—and, for authorized repairs, a verified fix and cleanup. You are done when
the supported cause is reported (provisional when no runnable loop exists) and,
for authorized repairs, Phase 6's finish conditions hold.

Skip a phase only with an explicit reason.

Resolve domain terms with
[glossary paths](../domain-modeling/references/glossary-paths.md) and read
relevant ADRs when exploring affected modules. Use
[Fix Root Causes](../engineering-principles/references/fix-root-causes.md) for
repair ownership and
[Attack the Premise](../engineering-principles/references/attack-the-premise.md)
when successive fixes fail the same check.

## Protect evidence

Pass potentially sensitive artifacts through a redacting filter so secrets become
`<REDACTED>` **before tool output enters the conversation**—on initial reads as
well as final reports. Reference credentials via environment variables, quote only
signal lines from captures that may hold auth headers, and ask the user if
redacted evidence is insufficient.

## Phase 1: Build a feedback loop

Make one command catch this exact symptom. For performance work, read
[measurement validity](../engineering-principles/references/measurement-validity.md)
before building a baseline, choosing a fix, or reporting comparisons.

Try loop forms in rough order:
1. Failing unit, integration, or end-to-end test at a seam reaching the bug.
2. `curl` or HTTP script against a running dev server.
3. CLI run with fixture input against known-good output.
4. Browser repro asserting visible state, DOM, console, or network (host browser
   routing before standalone drivers).
5. Replay of a captured request, payload, or event log.
6. Minimal throwaway harness with mocked dependencies.
7. Property or fuzz loop for intermittent wrong output.
8. Bisection harness across commits, datasets, or versions.
9. Differential loop comparing versions or configs on the same input.
10. Human-assisted script from `scripts/hitl-loop.template.sh` as a last resort.

**Apple targets:** load the matching reference—runtime/crashes/hangs:
[Apple runtime](references/apple-runtime.md); slow launch/hitches/CPU:
[Apple performance](references/apple-performance.md) (classify hangs with runtime
first); growing memory/leaks/jetsam: [Apple memory](references/apple-memory.md).
Drive Simulators through [Simulator Lifecycle](../simulator-lifecycle/SKILL.md)
and host device rules; reach physical devices via
[iOS verification](../verify/references/ios.md).

**Make the signal tight:** narrow setup, assert the exact symptom, and pin time,
seeds, filesystem, and network. For timing or lifecycle bugs, capture starting
state, event order, and active operation identity (including cancellation,
replacement, and completion timing), using
[Model the Domain](../engineering-principles/references/model-the-domain.md#stateful-behavior)
for invalid transitions.

Done when one named command runs and shows its redacted invocation and output,
and is:
- **Red-capable:** exercises the actual bug path and asserts the exact symptom,
  turning red now and green after repair.
- **Deterministic:** repeatable verdict (for flakes, raise and pin reproduction
  rate via repetition, concurrency, stress, or timing and record the rate).
- **Short and bounded:** shortest faithful loop with a fixed end (launch/memory
  workloads may take minutes).
- **Agent-runnable:** unattended except via the HITL template.

Establish this signal (or the artifact path below) before hypothesizing.

**When no runnable loop exists:** state what you tried and what blocks
reproduction, and ask for environment access, a redacted artifact (HAR, logs,
core dump, timestamped recording), or temporary production instrumentation
permission. A captured artifact showing the exact symptom in the affected build
supports a **provisional diagnosis**: skip Phases 2 and 4, rank falsifiable
hypotheses in Phase 3 against the artifact and code, and separate supported
conclusions from untested ones. Stay diagnosis-only until a runnable loop exists;
Phase 5 and verified-fix claims require one. Without a matching artifact, stop
before hypothesizing.

## Phase 2: Reproduce and minimise

Run the loop repeatedly to confirm it fails on the user's bug rather than a nearby
defect, keeping exact output/timing as evidence. When noise hides the cause,
shrink one input, caller, config, datum, or step at a time until every remaining
element is load-bearing (removing it turns the loop green). Keep the original
unminimised scenario for final verification. Done when the loop reliably
reproduces the symptom (provisional path skips this phase).

## Phase 3: Rank falsifiable hypotheses

Rank every hypothesis the evidence still fits; compare several when multiple fit.
Give each a testable prediction (*"If X causes this, changing Y removes the
failure or changing Z worsens it"*), and sharpen or discard untestable ones. Show
the ranking to the user before testing so they can add domain knowledge or
exclusions; continue with that ranking if they are unavailable.

## Phase 4: Probe predictions

Map each probe to a Phase 3 prediction and change one variable at a time. Prefer
debugger or REPL inspection; otherwise add targeted boundary logs tagged with a
unique prefix (such as `[DEBUG-a4f2]`) for clean removal. Avoid broad logging.
For performance regressions, establish a baseline with a timing harness, profiler,
or query plan before fixing. Bisect when comparing known-good and failing
revisions settles competing causes.

## Phase 5: Fix and add a regression test

Pick a **correct seam** reaching the actual failure and its triggering caller
chain (including multiple callers when needed). Starting from the Phase 2 repro,
repair through [TDD](../tdd/SKILL.md)'s red → green cycle at that seam; temporary
probes are diagnostic, never regression or acceptance tests. If no correct seam
exists, record the architectural limitation. In either case, rerun the Phase 1
loop on the original unminimised scenario.

## Phase 6: Clean up and report

Finish only when:
- the original repro is green;
- the regression test passes (or its missing seam is recorded);
- any repair affecting a user workflow has a passing [Verify](../verify/SKILL.md)
  verdict (a green diagnostic loop is evidence, not acceptance; Verify can reuse
  matching red evidence);
- all temporary logs are removed (confirmed by searching for the unique debug
  prefix);
- throwaway prototypes are removed or moved to a clearly marked debug location.

State the supported cause in the report and commit or PR message. When evidence
establishes a recurring failure class, record the verified cause and examples for
recurring-failure prevention—historical mining and broader prevention require
that scope from the user; keep active diagnosis focused on this failure (an
isolated incident supports a regression repair, not recurrence).

If the decisive fact required deep investigation, propose the cheapest persistent
signal that would have exposed it earlier (health check, counter, or structured
log), naming the fact and its runtime and privacy costs; implement only within
authorized scope, keeping persistent signals distinct from temporary probes.
