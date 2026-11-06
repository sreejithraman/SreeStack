# Controlled comparison

Run a controlled comparison only when a decision depends on one: a claim of benefit or
equal behavior, a context saving, or removing a safeguard because the model no longer
needs it. A fresh-session try while working on a skill is not a controlled comparison.

1. **Fix the variants before editing.** Compare the original and the candidate. Add a
   no-skill control for a claim of benefit, removal, or model default. The control
   keeps the same tools and help, with none of the skill's text.
2. **Match everything else.** Use the same model, effort, tool versions, fixture, and
   prompt. Changing the model is a separate comparison. Start every trial from the
   same fixture snapshot, with its own mutable state and outputs, and isolate or reset
   external state.
3. **Choose real tasks.** Sample 10–15 requests from real sessions, and add more if the
   sample misses the motivating case, a path, a reference lookup, a rare constraint, or
   a handoff. Define observable end states and mark required cases before
   any run. Use disposable fixtures for anything a
   [guardrail](../SKILL.md#writing-for-agents) covers.
4. **Isolate and calibrate.** Load the exact skill copy, apart from installed skills,
   memory, and user rules, using disposable profiles so real configuration and logins
   stay untouched. Prove it with three probes: a disposable skill's random
   instruction takes effect and its read is logged; the same request without the skill
   shows neither; a harmless command is logged with its known result. Recalibrate after
   any runtime change.
5. **Run repeats.** Pilot two tasks to check the scoring. Then run each task 3 times per
   variant in fresh sessions with alternating order, and add runs where results vary.
6. **Record each session.** Keep task, variant, skill and fixture hashes, settings,
   versions, the transcript, ordered tool calls, token usage, and elapsed time. Treat
   missing telemetry as a gap, not a zero. Keep failed trials. Reuse a result only if
   its task, fixture, variant, settings, and checks all match. Clean up only what the
   session created, and keep retained evidence.
7. **Judge the outcome.** Inspect end states and the full call sequence. Prove each
   check against a known failure. For qualitative output, use a fresh judge with
   anonymized outputs in random order. Repair a wrong scorer from independent expectations, keep the superseded
   results, and rerun every affected comparison.
8. **Decide.** Every planned trial needs a result or a stated gap. A failed required
   case rejects the candidate, whatever the average says. One pass, or a no-skill pass
   on a common task, says nothing about a safeguard for other conditions. Finding no
   decline does not prove equivalence. Compare loaded context, including
   later reference reads. File bytes are not tokens or cost. Then try the candidate
   with the normal skill collection, because discovery and handoffs can still fail.

Report task results, repetitions, variation, resources, calibration, exclusions, and
the limits of the claim. Without isolation or telemetry, report the checks you could
run and mark the broader claim unverified.
