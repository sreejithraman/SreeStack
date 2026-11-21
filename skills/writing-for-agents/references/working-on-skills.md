# Working on skills

## Give each skill one job

Write the contract first, and open `SKILL.md` with it in plain prose:

- **Job:** one sentence naming one outcome.
- **Input:** what it needs to start.
- **Output:** what it leaves behind.
- **Done:** the falsifiable check that ends it.

A skill belongs to one of three layers:

- A **foundation** holds shared vocabulary, principles, or reference criteria that
  higher layers consult without owning workflow execution.
- A **capability** does one job and can run standalone.
- A **workflow** chains capabilities (or lower workflows). It owns their order,
  handoffs, and finish line, links to each capability, and holds none of their
  procedure.

For example, `engineering-principles` is a foundation, `review` assesses a change,
`review-sweep` settles findings, and `review-fix-loop` chains them.

- **Dependencies point downward only.** A foundation never links up to a capability
  or workflow, and a capability or lower workflow never links up to a higher
  workflow or names its internals (such as `implement` or `coordinator` inside
  `review-sweep` or `pr`). Instead, it takes scope and limits from its caller and
  returns structured outcomes (such as deferred items or stops) for the caller to
  route. Entry-boundary routing pointers (such as `implement` offering `coordinator`
  for multi-outcome work) are the only exception.
- **Home shared rules in the lower layer.** Under *One home per meaning*, when a
  lower skill and a higher workflow share a rule or reference, place it in the
  lowest layer that uses it rather than linking upward. Never home a shared
  reference inside a higher workflow or a user-invoked skill when lower or
  model-invoked skills depend on it.

## Write the description

A model-invoked description is only a trigger; leave capabilities and procedure to the
body.

- Put the strongest trigger words first.
- Phrase each case as a request or situation, and merge synonyms into one case.
- Name scope exclusions when sibling skills overlap (for example, *"Excludes local
  Simulator debugging"*) so near-misses do not false-trigger.

## Choose who invokes it

Keep the same choice in both hosts: Claude Code reads `disable-model-invocation` from
`SKILL.md`, and Codex reads `policy.allow_implicit_invocation` from `agents/openai.yaml`.
In repos with automated skill checks (such as SreeStack's `scripts/check_skills.py`), let
the check enforce host alignment.

| | Model-invoked | User-invoked |
| --- | --- | --- |
| Use when | The agent must reach it on its own | Only a person starts it |
| Claude Code | Omit `disable-model-invocation` | `disable-model-invocation: true` |
| Codex | Omit `policy.allow_implicit_invocation` | `policy.allow_implicit_invocation: false` |
| Description | Triggers and exclusions for the model | One line for a person, without triggers |
| Cost | Description loads on every turn | Person must remember it exists |

A person can invoke either kind by name. Do not record test notes in `model:` or
`effort:` frontmatter—Claude Code switches to those settings when the skill runs; keep
test notes in `SOURCES.md` or commit messages instead. Linking to a user-invoked skill
lets an agent read it, but grants nothing the choice withholds: link one only behind a
user request or user-started workflow that names its actions or effects. Put logic shared
across workflows in a reference or a model-invoked skill. Spend user-invoked slots only
where human judgment matters.

### Split by invocation

Split off a model-invoked skill only when it has a distinct trigger the user actually
uses, or when an agent must reach it independently.

## Create a skill

1. Define the contract, invocation choice, and a set of real requests covering every path
   (plus near-misses for a model-invoked description).
2. Write `SKILL.md` and only the references that some paths skip.
3. Update host metadata (`agents/openai.yaml`) and the project record (`SOURCES.md`).
4. Run project checks and prove the new skill on each model that uses it per the Proof
   ladder in `SKILL.md`, running trials per
   [controlled comparison](controlled-comparison.md#run-trials-safely).

Done: the contract is explicit, metadata and records are updated, checks pass, and each
request has a result or stated gap.

## Change an existing skill

Read the skill's project record (such as `SOURCES.md`) first. Preserve local adaptations
and its invocation choice unless the user asks to change them. Edit the source of truth,
not an installed copy. If the change touches a CLI, API, SDK, MCP tool, or bundled
script, also read [tool guidance](tool-guidance.md).

For a whole-skill overhaul, use Rewrite below. For a **targeted change**:

1. Inspect consumers, links, and tests that depend on the changed text. If the reported
   problem does not hold, stop and report that.
2. When the edit adds or changes a behavioral rule, trigger, or handoff, confirm the
   failure first per the Proof ladder in `SKILL.md` (new guardrails skip this step).
   When it removes, weakens, or moves guidance, or changes a trigger or handoff, also
   record the affected survival items and collect representative requests (including
   near-misses for triggers) before editing.
3. Apply the edit. Update the project record and host metadata (`agents/openai.yaml`) if
   local differences or metadata changed.
4. Prove the change per the Proof ladder in `SKILL.md`. When step 2 applies, run the
   affected requests in fresh sessions on each model that uses the skill against the
   final text (including the old text where behavior must stay equal), report
   unavailable trials as gaps, and run Settle what changed on any reduced or moved
   guidance.
5. Run project checks and report final-text results and any remaining gaps.

Done: the required proof passed or has its gap stated (or the problem was reported
invalid), any reduced or moved guidance is settled, and project checks pass.

## Audit

An audit asks whether we would write the skill this way today. It reports findings and
edits no files; apply cuts only when the user asks, and treat them as removals.

To pick a target, rank skills by `SKILL.md` size and lines added vs removed in
`git log --numstat`.

- Read `SKILL.md`, every reference, its project record, and its real runs (see Learn from
  real runs in controlled comparison); add tool guidance if it teaches a tool.
- Check the contract, `Done` condition, invocation choice, description triggers and
  exclusions, downward-only dependencies (flagging upward links, higher-workflow
  internals leaked into lower skills, or shared references homed above their lowest
  consumer), link hygiene (flagging same-file `#anchor` jump-links, back-links to
  `SKILL.md`, repeated links to the same target in one file other than distinct
  section anchors into a multi-section reference, nested reference-only chains, and
  inline background URLs), and every line against the line test
  (flagging no-ops, duplicates, environment-held facts, and stale rules).
- Report each failing line with evidence. Label suspected no-ops as predictions until a
  fresh-session trial proves them.

Done: every file in the skill was inspected and each finding cites evidence.

## Rewrite

Use when the user asks for a rewrite, or when the current structure no longer fits the
job.

1. **Record the survival list:** check each source and list the invocation choice, local
   adaptations, supported hosts, legal notices, paths and anchors other files link to,
   tests asserting text, consumers, and prior user decisions. Confirm the original is
   recoverable in git.
2. **Collect real requests:** pull from the description, consumers, session history, and
   rare rules so every path has a concrete request.
3. **Write fresh:** draft the contract and skill in a clean file from the requests and
   survival list so old structure does not carry over.
4. **Try it:** run the collected requests in fresh sessions on each model that uses the
   skill (Run trials safely in controlled comparison), comparing against the old text
   where behavior must stay equal; report unavailable trials as gaps.
5. **Settle what changed** against the original text.
6. **Finalize:** update `SOURCES.md` and host metadata (`agents/openai.yaml`), verify new
   factual claims against sources, and run project checks.
7. **Report:** state what changed, each dropped or moved group and why, where the settled
   list lives, each request's result against the final text (marking earlier-draft
   results stale), and remaining gaps.

Claims of equal outcomes or context savings require a controlled comparison.

### Settle what changed

List every old rule the new text lacks, weakens, or moves, grouped by meaning. Use
`git log -S` or [Why](../../why/SKILL.md) when a rule's reason is not obvious. A user's
explicit decision to drop or move a specific rule stands—record it and report any risk
you see. Approving a whole audit list is not that decision. Decide every other group in
this order:

1. **Restore** anything on the survival list.
2. **Restore** any guardrail. Skip it only if the new text states it just as strongly
   before the action it constrains, code enforces it on every host that uses the skill,
   or a controlled comparison exercising its condition shows the model no longer needs
   it.
3. **Drop** a duplicate, a fact the environment holds, or a rule whose reason is obsolete,
   citing the evidence. A weaker wording is not a duplicate. Drop a suspected no-op only
   when fresh-session trials without the line exercise its condition and behave correctly
   on each model (three runs per model for an isolated removal; for a rewrite, batched
   candidate runs that exercise each dropped rule's condition).
4. **Restore** a rule when a request failed without it, or when you can name a concrete
   failure it still prevents.
5. **Otherwise** gather the evidence or restore the rule.

A restored rule may live in any home that reaches the agent before the action. Write it
in that home's voice and rerun affected requests on each affected model. Done: every old
rule is in a group with a recorded decision and reason.
