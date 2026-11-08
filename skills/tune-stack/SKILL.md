---
name: tune-stack
description: Improve SreeStack skills and checks from session logs, run metrics, or a new model release, proving each change against the old version.
disable-model-invocation: true
---

# Tune Stack

Improve the SreeStack skills and checks from evidence: past sessions, run
metrics, or a new model release. Start from the user's question and the sources
they name. Leave each selected change at its finish line with evidence that it
beat the old version in a replay or a measured run. You are done when every
selected change reached its finish line with that evidence, or was reported as
unproven with the old version kept, and every deferred finding has a destination.

You own the question, the evidence window, the choice of one hypothesis, the
comparison's declared target, the handoffs, and the finish line. Each linked
skill owns its method and returns to you: [Retro](../retro/SKILL.md) reads
sessions, [Correct](../correct/SKILL.md) handles recurring failures and their
guards, [Writing for Agents](../writing-for-agents/SKILL.md) owns evaluation and
comparison, and [Implement](../implement/SKILL.md) builds and delivers.

## What invoking it allows

- **A retrospective request** asks about past runs and asks for no change, such
  as "what went wrong last week" or "is review worth its cost". It ends at
  [stage 2](#2-select) with ranked recommendations and an offer to test the top
  one. Save recommendations the user doesn't take up with Snip Snap only when
  the user asks.
- **Any other request** allows choosing one hypothesis, running its comparison,
  and building the change through Implement to **Try**. Land only when the user
  says Land. Publish a PR or merge only when the user asks.
- **Overnight replays** of stack workflows run only when the user asks for them.

Product bug hunting is a separate chore source: [Verify](../verify/SKILL.md)'s
exploratory and edge-data checks, [Diagnosing Bugs](../diagnosing-bugs/SKILL.md)
for failures, confirmed bugs saved with Snip Snap, and fixes through Implement.
Use only its evidence that the stack missed bugs.

## 1. Ground

Read the request and the sources it names. Fix the evidence window, the hosts
and models in it, the improvement the user wants, and what this request allows.
For sessions and metrics, use the definitions and log cautions in
[evidence](references/evidence.md); report each window with its denominator and
missing records. For a new model release, run a regression check, not an
improvement hypothesis. Pick the cases whose rules assume something the old
model could not do, and run the same fixed skill text and cases on the old and
the new model. A regression is a case the old model passed and the new one
fails. Report the regressions found, or "none found on N cases", never
equivalence. A skill edit follows only from a regression, as a normal
hypothesis.

Done when the source, window, models, desired improvement, and authority are
stated in the thread.

## 2. Select

Find candidates and route each kind to its owner:

| The evidence shows | Use |
| --- | --- |
| Problems in specific sessions | Retro, for recommendations with session evidence |
| The same failure in two or more independent incidents | Correct, for the class, its exposure, and its guard |
| A skill or instruction that reads wrong or carries no-ops | Writing for Agents' audit |

Check each candidate against the current version: an old failure that it
already prevents is resolved, not a hypothesis. A rule in the text is not proof
the behavior is fixed. When the logs can't show whether the failure still
happens, reproduce it on the current version with the cheapest proof from
[stage 3](#3-baseline), such as a dry-run trial, before selecting or dropping
it. In a retrospective, reproducing is part of the offer: label the exposure
unverified and offer the test. Rank the live ones by impact and current
exposure, and pick one. A hypothesis needs cited incidents, the current path
that still allows the failure, and a win a check or a blind judge can observe.
Show the user the ranked rest.

Done when one hypothesis has its evidence, current exposure, and observable
win, or, for a retrospective request, the ranked recommendations and the
offer are delivered.

## 3. Baseline

Freeze the old version: the commit and the skill tree's hash. Pick the cases:
the motivating incidents plus the coverage that
[Controlled Comparison](../writing-for-agents/references/controlled-comparison.md)
asks for. Write each case's expected result before any run, and mark the
required cases and the behavior to preserve.

Declare one primary target before the experiment, such as fewer review rounds,
a corrected observed failure, or lower cost at the same quality. Any failed
required case vetoes the change. Equal pass rates are not a win, and three runs
don't prove significance; add repeats where results vary. The user decides
tradeoffs, and changing the target after seeing results starts a new experiment.

Choose the cheapest proof that settles the claim:

- **A routing or handoff question:** a dry-run trial. Freeze the tree, write the
  expected handoffs first, and have fresh sessions trace the scenario without
  running it, under
  [Run trials safely](../writing-for-agents/references/working-on-skills.md#run-trials-safely).
  It proves routing only, not tool effects, discovery, or cost.
- **A deterministic check:** Correct's guard proof, historical rejection plus
  valid-path success. Add a model run only when you also claim agent behavior
  improves.
- **Any other claim:** a measured run with the
  [comparison runner](../writing-for-agents/scripts/compare.py), calibrated
  before the first task.

Done when the old version, cases, expectations, target, and a passing
calibration exist, or each missing one is named with what it blocks.

## 4. Change and compare

Hand each change to Implement as one outcome with this brief:

- **Old snapshot:** the frozen commit and tree hash.
- **Incidents:** the cited evidence behind the hypothesis.
- **Cases** and their **expected results**.
- **Target,** required cases, and **preserved behavior.**
- **Finish line:** Try, or Land when the user said Land.

Implement builds it with Writing for Agents, or Correct for a guard. Compare the
final candidate with the old version under the declared test. A later edit to
anything a case loads makes its evidence stale, so rerun it. When a candidate
fails or is inconclusive, revise it while the evidence points to a better
attempt. Otherwise keep the old version and report the change as unproven.

Done when every selected change has a result on its final version that shows
the declared improvement with every required case passing, or is reported as
unproven with the old version kept.

## 5. Finish

Implement carries each change to its finish line: Try stops before review and
the PR. Show the evidence with [Show Me](../show-me/SKILL.md): the score, the
task table, and the evidence path.

Save each deferred finding with [Snip Snap](../snip-snap/SKILL.md), with its
evidence and next action, after checking existing snips and plans for it.

Report, per change, the target, the result against the old version, the limits
of the sample, and its disposition.

Done when each change is at its finish line or reported unproven, the user can
open the evidence, and every deferred finding is saved.
