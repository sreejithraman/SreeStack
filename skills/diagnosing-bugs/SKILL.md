---
name: diagnosing-bugs
description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
---

# Diagnosing Bugs

Build a tight signal for the user's exact symptom, reproduce and minimise it,
then test causes and repair. Skip a phase only with an explicit reason; the
artifact-only path below supports diagnosis, not a verified fix.

Resolve glossary paths with [glossary paths](../domain-modeling/references/glossary-paths.md)
before reading or writing domain vocabulary. Read an existing glossary and
relevant ADRs when exploring the affected modules.
Use [Fix Root Causes](../engineering-principles/references/fix-root-causes.md)
for repair ownership and root-cause decisions, and
[Attack the Premise](../engineering-principles/references/attack-the-premise.md)
when successive fixes fail the same check. This skill owns the runnable loop.

## Protect evidence

Read potentially sensitive artifacts through a redacting filter so secrets
become `<REDACTED>` **before tool output enters the conversation**. This applies
to inspection reads as well as final reports. Build commands against environment
variables so credentials stay in the environment. Captures may contain auth
headers; quote only the lines needed for the signal. If redacted evidence is
insufficient, explain what is missing and ask the user.

## Phase 1: Build a feedback loop

Spend the effort needed to make one command catch this bug. For performance
work, read [measurement validity](references/measurement-validity.md) before
building or using a baseline, choosing a fix, or reporting comparisons.

Try these loop forms in roughly this order:

1. A failing unit, integration, or end-to-end test at a seam that reaches the bug.
2. Curl or an HTTP script against a running dev server.
3. A CLI with fixture input and a known-good output comparison.
4. A browser reproduction asserting visible state, DOM, console, or network.
   Follow host browser routing; in T3 Code use the collaborative preview and
   recovery rules before a standalone driver's allowed fallback or explicit request.
5. Replay of a captured request, payload, or event log through the affected path.
6. A throwaway harness with the minimal system and mocked dependencies.
7. A property or fuzz loop for intermittent wrong output.
8. A bisection harness checking known commit, dataset, or version states.
9. A differential loop comparing versions or configurations on the same input.
10. As a last resort, a human-assisted script based on
    `scripts/hitl-loop.template.sh`, with captured observations returned to you.

### Apple targets

Load the reference matching the evidence needed:

- Runtime behavior, crashes, or suspected hangs:
  [Apple runtime](references/apple-runtime.md).
- Slow launch, hitches, excess CPU, or other measured regressions:
  [Apple performance](references/apple-performance.md). For a hang, classify and
  reproduce it with the runtime reference first; profile when delay needs measurement.
- Growing memory, abandoned objects, retain cycles, or memory-pressure termination:
  [Apple memory](references/apple-memory.md).

These refine this loop. After establishing cause and repair, use `verify` for
the final Apple user workflow check.

### Make the signal tight

Narrow setup and scope, assert the specific symptom, and pin time, random seeds,
filesystem, and network where relevant. Aim for seconds rather than minutes.
For nondeterministic failures, increase and pin the reproduction rate with
repetition, concurrency, stress, or controlled timing; record the observed rate.

For timing and lifecycle failures, capture starting state, event order, and
active operation identity, including relevant cancellation, replacement, and
completion timing. Use [Model the Domain](../engineering-principles/references/model-the-domain.md#stateful-behavior)
when repairing invalid states or transitions.

Phase 1 is complete when you have run one named command and shown its redacted
invocation and output. The command must be:

- **Red-capable:** drive the actual bug path and assert the user's exact symptom,
  with a verdict that can turn red on this bug and green after repair.
- **Deterministic:** the same verdict on repeat, or a pinned, high reproduction
  rate suitable for debugging a flaky bug.
- **Fast:** seconds, not minutes.
- **Agent-runnable:** unattended, with human participation only through the HITL template.

Establish this signal before forming a theory. Without it or the matching
artifact below, stop before hypothesising.

### When a runnable loop is unavailable

State what you tried and what prevents reproduction. Ask for access to the
affected environment, a redacted captured artifact (HAR, logs, core dump, or
timestamped recording), or permission for temporary production instrumentation.

An artifact capturing the exact symptom in the affected build supports a
**provisional diagnosis** when it cannot be replayed. Skip Phases 2 and 4;
use Phase 3's ranked falsifiable hypotheses and compare predictions with the
artifact, code, or independent observations. Distinguish supported conclusions
from untested ones. Stay on this diagnosis-only path until a runnable
reproduction exists: Phase 5 and a verified-fix claim require that loop.
Without a matching artifact, stop before hypotheses.

## Phase 2: Reproduce and minimise

Run the loop repeatedly. Confirm it goes red on the user's failure rather than
a nearby bug, and retain the exact error, output, or timing as repair evidence.
For a flaky failure, confirm the reproduction rate is high enough to debug.

Shrink the scenario one input, caller, configuration, datum, or step at a time;
rerun after each removal. Keep the original scenario for final verification.
Finish when the failure is reproduced and every remaining element is
load-bearing: removing it makes the loop green. Proceed only after both
reproduction and minimisation; the provisional path skips this phase.

## Phase 3: Rank falsifiable hypotheses

Generate 3–5 ranked hypotheses before testing any. For each, name a prediction:
“If X causes this, changing Y will remove the failure or changing Z will worsen it.”
Sharpen or discard a hypothesis without a testable prediction.

Show the ranking to the user before testing so they can supply domain knowledge
or prior exclusions. Continue with that ranking while they are unavailable.

## Phase 4: Probe predictions

Map each probe to a Phase 3 prediction and change one variable at a time.
Prefer debugger or REPL inspection; otherwise place targeted logs at boundaries
that distinguish hypotheses. Tag every temporary log with a unique prefix such
as `[DEBUG-a4f2]` so cleanup can find it. Avoid broad logging.

For performance regressions, establish the baseline with a timing harness,
profiler, or query plan, then bisect. Measure before fixing; apply the shared
measurement-validity requirements.

## Phase 5: Fix and add a regression test

Choose a **correct seam**: the test must exercise the real bug pattern at its
call site, including multiple callers or a triggering chain when required.
A shallow test that misses the pattern cannot lock down the repair.

If no correct seam exists, record the architectural limitation for the cleanup
report. If one exists:

1. Turn the minimised repro into a regression test **before editing the fix**.
2. Watch the test fail.
3. Apply the repair.
4. Watch the test pass.

In either case, rerun the Phase 1 loop against the original, unminimised scenario.

## Phase 6: Clean up and report

Finish only when the original repro is green, the regression test passes (or
its missing seam is documented), and temporary logs and throwaway prototypes
are removed or the prototypes moved to a clearly marked debug location.
Search for the unique debug prefix to confirm removal. State the supported
cause in the result and any commit or PR message.

When evidence establishes a recurring failure class, pass examples and the
verified cause to [correct](../correct/SKILL.md). Historical mining and broader
prevention require that scope from the user; keep active diagnosis focused on
this failure. An isolated incident supports a regression repair, not recurrence.

If the decisive fact required deep investigation, propose the cheapest
persistent signal that would have exposed it earlier: a health check, counter,
or structured log. Name the fact and the signal's runtime and privacy costs.
Implement only within the authorized fix; otherwise report it as a follow-up.
Keep persistent signals distinct from temporary probes.
