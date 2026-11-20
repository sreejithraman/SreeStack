# Controlled comparison and trials

Single home for empirical checks: session-log sampling, fresh-session trials,
controlled comparisons, and closing cross-model gaps.

## Learn from real runs

Read session logs for user corrections, skipped rules, repeated failures, tool errors,
and references agents read or missed. Count actual uses—mentioning a skill is not using
it—and count resumed or forked sessions and duplicated calls once. Always state the
sample window and denominator.

## Run trials safely

- Load the edited copy in a fresh session and confirm it from a logged read. A worktree
  edit does not update installed skills, so an unconfirmed trial is a gap.
- For a new or changed description or pointer, load the copy through the host's skill
  listing in a disposable profile, leave its path out of the prompt, and include
  near-misses that must not fire it. If you cannot, report trigger firing as untested.
- Use disposable fixtures and profiles whenever a trial risks anything a guardrail
  covers. Leave real configuration and logins untouched.
- *"Each model"* means the default model on each host that uses the skill.

## Run a controlled comparison

Run a controlled comparison only when a decision depends on measured evidence: a claim of
benefit or equal behavior, a context or cost saving, or removing a guardrail because the
model no longer needs it. A smoke trial while editing a skill is not a controlled
comparison.

1. **Fix the variants before editing.** Freeze the original and candidate trees. Add a
   no-skill control (same tools and help, no skill text) for claims of benefit, removal,
   or model default.
2. **Match everything else.** Use the same model, effort, tool versions, fixture
   snapshot, and prompt. Verify the served model reported by each run, not just the
   requested flag, because hosts can silently fall back on an unknown ID or quota limit
   (note when a harness does not report served model separately from requested model).
   Changing the model is a separate comparison. Give every trial isolated mutable state
   and reset external state.
3. **Prepare real tasks safely.** Set up disposable fixtures first for any guarded
   action, and never run a prohibited command against a real account or live state.
   Sample 10–15 requests from real sessions, adding cases for the motivating failure, any
   unexercised path, reference lookups, rare constraints, and handoffs. Before authoring
   a task for a "don't" rule, check feasibility safely—reproduce the agent's real tool
   conditions (such as closed stdin and no TTY) inside a disposable fixture, or inspect
   source or a dry run when live execution would be guarded; if it cannot fail on this
   host, drop the task and treat the rule as a cut candidate. Define observable end states
   and mark required cases before any run. When iterating across candidate fixes, hold
   back about a third of tasks blind (at least one per failure cause) until final
   validation to catch overfitting.
   - **Claude Code cases:** author [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals)
     cases with deterministic graders where they can decide, and prepare options for
     [`scripts/compare.py`](../scripts/compare.py) (`python3 <path-to-compare.py> --help`
     lists targets, exit codes, and runner limits; ensure flags include the no-skill arm
     and repeats when required).
   - **Trust prerequisite before any eval launch:** confirm you trust both skill trees
     and the eval suite, and isolate or mock hooks, MCP servers, and executable fixtures.
     `compare.py` passes `--trust-plugin`, and `plugin eval` sandboxes shell tools, not
     hooks, MCP servers, or scaffolds running outside the sandbox.
4. **Isolate and calibrate.** Load the exact skill copy apart from installed skills,
   memory, and user rules in disposable profiles. Prove isolation with three probes: a
   disposable skill's unique plain token (such as `Version <random>`, not `CANARY-*`,
   which some models refuse to echo) takes effect and logs its read; the same request
   without the skill shows neither a successful skill read in its trace nor leaked skill
   content (a blocked lookup attempt can pass; bound shell calls with a timeout, because
   some models search the disk when a skill is absent); a harmless command logs its
   expected result. Recalibrate after any runtime change.
5. **Pilot and run repeats.** Only after passing calibration and confirming the trust
   prerequisite, pilot two tasks to check scoring, then run each task 3+ times per
   variant in fresh sessions with alternating order, adding runs where results vary.
   - **Claude Code:** run `compare.py` with one declared target and the required cases
     (paid sessions—run only for an authorized comparison). Report sequential order (old
     suite before new) as a limit. Its JSON output includes a `cases` summary (old/new
     stats, `required`, and the `without` arm per case when present).
   - **Other hosts (without `claude plugin eval`):** run dry-run trials under Run trials
     safely and mark measured claims unverified, unless authenticated isolated behavioral
     runs are available on that host.
6. **Record each session.** Keep task, variant, skill and fixture hashes, settings,
   versions, transcripts (`--keep-temp` on `plugin eval`), ordered tool calls, token and
   cost telemetry, and elapsed time. Treat missing telemetry as a gap, never zero. Keep
   failed trials. Reuse a prior result only when task, fixture, variant, settings, and
   checks all match. Clean up only session-created artifacts while keeping evidence.
7. **Judge the outcome.** Inspect end states and full call sequences. For rules about
   hangs or waiting, record and fail on tool timeouts—a model that hangs, times out, and
   retries can still pass an end-state check alone. Prove each grader rejects a known
   failure. For qualitative output, use a fresh judge with anonymized outputs in random
   order. Repair a wrong scorer from independent expectations, keep superseded results,
   and rerun every affected comparison.
8. **Decide.** Every planned trial needs a result or stated gap. Any failed run of a
   required case rejects the candidate regardless of averages. One pass, or a no-skill
   pass on a common task, says nothing about a guardrail under other conditions. No
   observed decline does not prove equivalence. Compare actual loaded context (including
   later reference reads); file bytes are neither tokens nor cost. Finally, test the
   candidate inside the normal skill collection, because discovery and handoffs can still
   fail.

Done: report per-case and aggregate results, repetitions, variation, resources,
calibration, exclusions, and the limits of the claim. Without isolation or telemetry,
report the checks you could run and mark the broader claim unverified.

## Close a cross-model gap

When a skill passes less often on a target model than on a reference model, fix it with
shared text that helps the target without hurting other models.

1. **Measure matched baselines before editing.** Follow the controlled comparison steps
   above: freeze `base` and `none` variants, pick matched tasks covering each gap case,
   split about a third blind into held-back tasks before tuning (even for a single
   candidate), calibrate, and run repeated `base` and `none` trials on the tuning tasks
   for each model (keeping held-back tasks untouched). Confirm a repeatable gap and check
   whether the target already performs better with `none` (which points to cutting lines
   first). Run models on the same host when possible; if hosts differ, report the result
   as a host-plus-model comparison, and leave model-specific outcome claims unverified
   when served models cannot be verified or a host is limited to dry runs.
2. **Check loading first.** Compare how often each model opens `SKILL.md` in those
   baseline runs. If the target opens it much less often, fix the trigger description
   before editing body rules. If reads are already healthy (or rise without passes
   improving), move to step 3 instead of pushing body procedure into the trigger
   description.
3. **Diagnose side by side.** Compare each failing target run with a passing reference
   run of the same task to classify the cause:
   - Skipped, misread, or missing rule → reword, widen, or load it earlier in the body
     (keep descriptions trigger-only, limited to pre-call loading cues).
   - Stopped early or asked unnecessarily → add a one-line `Done` condition.
   - Tool, fixture, or harness bug → fix it outside the skill.
   - Capability ceiling (still fails when the reference's steps are pasted directly into
     the prompt) → if the case is optional, drop it from that model's goal and report
     it; if it is a required case, treat it as a blocker or unsupported model (narrow a
     required case only by explicit user decision with revised acceptance criteria before
     running a new comparison).
   - Scorer bug → fix the grader and rerun across every version and model.
4. **Fix one change at a time and harm-check other models.** Because every model reads
   the same file, test kept changes together on the reference and other models as well.
   Watch for read-rate drops on other models, and report the added token cost when a
   model starts opening the skill more often.
5. **Validate once on held-back tasks.** Run paired `base` vs final candidate trials on
   the same held-back tasks across the target and harm-check models. Ship only if the
   target improves on held-back cases without regressing other models or failing any
   required case; if gains hold only on tuning tasks, the edits overfit.
