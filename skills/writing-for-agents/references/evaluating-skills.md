# Evaluating skills

Use this procedure for empirical comparisons of agent outcomes or context use.
For a small correction, focused text and metadata preservation checks follow
[revision guidance](revising-skills.md). This reference defines an experiment,
not a bundled runner.
[Verify's acceptance guidance](../../verify/references/acceptance-contract.md)
owns preserved requirements, evidence validity, and acceptance. Existing review
assesses the experiment and its results alongside the change.

## Define the comparison before editing

Preserve **original** and **candidate** variants. Add scored **no-skill** trials
when assessing the skill's incremental benefit, removing it, or justifying cuts
as model-default behavior. That control has the same tools and help but none of
the tested skill's instructions, references, or injected copies. A two-version
preservation or context comparison needs only original/candidate trials.
Use the same model, effort, tool versions, fixtures, and prompt for each task.
Follow configured model routing; changing models is a separate comparison.
Keep unrelated tool/help changes out of the treatment.

Select tasks from actual requests, relevant session history, and requirements.
Cover the motivating case, affected trigger branches, reference lookup, difficult
calls, rare constraints, and cross-skill handoffs. Define observable end states
and important call-sequence requirements before seeing candidate outputs.
Use disposable fixtures or output-only tasks when external actions are outside
scope; written plans alone cannot prove execution behavior.

Choose task count and repetitions from coverage and observed variation. Start
with a small pilot to validate setup/scoring, then repeat every variant in fresh
sessions under matched conditions. Alternate variant order to reduce temporal
bias. One success, or a no-skill success on a common task, does not justify
deleting a safeguard for other conditions.

## Establish that sessions are comparable

Use a runtime that can select the exact skill copy and isolate it from installed
skills, plugins, memory, user-level rules, and ancestor instruction files. Keep
unavoidable host instructions identical and record them. Preserve real user
configuration and authentication; use supported disposable profiles/environments.
Source access and external effects still follow the task's authorization.

Before accepting comparative results, calibrate the runtime and logging:

1. Give a disposable skill a random instruction and verify both its effect and
   a logged read of the intended copy.
2. Run the same request without that skill; verify the instruction and its reads
   are absent, including copies injected through another route. This loading
   probe is separate from deciding whether tasks need a scored no-skill arm.
3. Run a harmless command with a known result; verify its execution and call log.

Retain calibration inputs and outputs. These probes establish selected signals,
not proof that all contamination or shared state is impossible. Verify other
relevant isolation settings and report gaps. Recalibrate after runtime, adapter,
or loading changes. Ordinary parent-context children are useful integration
checks, but are not clean no-skill controls when they inherit the tested guidance.

## Session adapter contract

For repeated trials, reuse a suitable runner or build the smallest adapter from
the installed runtime's supported interface. Give each session an explicit skill
variant (or none), prompt, fixture directory, output directory, and model settings.
Keep concurrent sessions' mutable state separate.

Retain a session record with:

- Task/variant identity, skill and fixture hashes, model/settings, tool/runtime
  versions, and applicable host instructions.
- Agent outcome separately from adapter failure; fixture setup and check results;
  final answer and paths to raw transcripts.
- Actual tool calls in order, including read paths and shell commands, with
  stable IDs where available. Capture code-mode calls as well as direct calls.
- Reported input/output/cache usage with the runtime's definitions, model request
  count, and elapsed time. Use null for unavailable fields. Reconcile totals and
  avoid counting cached or reasoning tokens twice.

Validate these fields against actual runtime output. Missing telemetry is a
measurement gap, not a task success or a zero. Preserve failed trials. Clean up
only session-owned disposable state, including after cancellation, without
deleting retained evidence. Resume only results matching the exact task, fixture,
variant, settings, and check versions; changed inputs invalidate affected runs.

## Judge outcomes and improve the checks

Inspect actual artifacts and the complete relevant call sequence, including later
wait/stop behavior and effects. Use end-state checks where possible; answer
regexes and exit zero alone cannot establish workflow success. Validate a check
with a known failure or contrasting fixture before trusting it.

For qualitative outputs, use the skill's applicable checker plus a fresh judge
given the task, rubric, and anonymized outputs in randomized order. Keep required
constraints separate from preference judgments. Trace failures to skill behavior,
runtime/fixture gaps, or faulty scoring before changing instructions.

Repair an incorrect scorer using independent expectations and rerun affected
comparisons under the corrected method. Keep superseded evidence. A task all
variants fail still represents its requirement: repair the setup, report the
failure, or justify exclusion rather than silently removing a difficult case.

Check every planned task/variant/repetition has a result or explicit gap. A
failed required preservation case rejects adoption regardless of aggregate
scores. Failure to detect a statistical decline is not proof of equivalence.
For a context target, compare actual loaded context including later reference
reads; report cache usage and billed cost separately where available. File bytes
are a structural measure, not task tokens or cost.

Finally, exercise representative workflows with the normal skill collection and
host context. An isolated gain may fail when discovery and handoffs interact.
Report task-level outcomes, repetitions and variation, measured resources,
calibration, integration results, exclusions, and the limits of the claim.
If an isolated runtime or required telemetry is unavailable, deliver the bounded
checks that were possible and mark the broader claim unverified.
