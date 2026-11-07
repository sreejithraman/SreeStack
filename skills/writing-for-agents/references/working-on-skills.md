# Working on skills

## Give each skill one job

Write the contract first, and open the skill with it in plain prose:

- **Job:** one sentence naming one outcome.
- **Input:** what it needs to start.
- **Output:** what it leaves behind.
- **Done:** the check that ends it.

A skill is one of two kinds:

- A **capability** does one job and can run without a workflow.
- A **workflow** chains capabilities. It owns their order, the handoffs, and the
  finish line. It links to each capability and holds none of their procedure.

For example, `review` assesses a change, `review-sweep` settles findings, and
`review-fix-loop` chains them.

Link every reference [directly from `SKILL.md`](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices),
because agents can read nested files only in part.

## Write the description

A model-invoked description is only a trigger. Leave what the skill is, its
capabilities, and its procedure to the body.

- Phrase each case as a request: `Use when the user asks to clean up a finished task
  or unused worktree`.
- Give each case one trigger. Synonyms for one case are one case.
- Put the strongest trigger word first.

## New skill

Follow [Rewrite](#rewrite), skipping steps 1 and 5. Take the contract and requests
from the user's request, and [choose who invokes it](#choose-who-invokes-it).

## Change an existing skill

Read its project record, such as its `SOURCES.md` entry. Keep its local adaptations
and invocation choice unless the user asks to change them. Edit the source of truth,
not an installed copy.

For a whole-skill change, use [Rewrite](#rewrite). Otherwise, make a **targeted
change**:

1. Find what depends on the changed text. If the reported problem does not hold, stop
   and report that.
2. If the edit removes, weakens, or moves guidance, or changes a trigger or handoff,
   first run [Rewrite](#rewrite) steps 1 and 2 on the affected paths.
3. Make the edit. To add guidance, use [Add a rule](../SKILL.md#add-a-rule).
4. Prove the change works. Run a command only if it risks nothing a
   [guardrail](../SKILL.md#writing-for-agents) covers, or the request authorizes it.
   Otherwise use a documented dry run, a disposable fixture, or a real-schema stub, or cite the exact
   source, and report the live effect as unproven.
5. For an edit under step 2, run Rewrite steps 4 through 7 on the affected paths,
   and keep the rest of the file.
6. For any other edit, run the project checks. If it changes what an agent does, also
   [try](#run-trials-safely) the affected requests in a fresh session. A line the user
   gave word for word skips the trial.

Done: the proof passed, or you reported that the problem does not hold, and each step
that applies has a result.

## Audit

An audit asks whether we would write the skill this way today. It reports findings
and changes no files. Apply its cuts only if the user asks, and treat them as removals.

To choose a target, rank skills by `SKILL.md` size and by lines added against lines
removed in `git log --numstat`.

1. Read the skill, its references, its record, and its
   [real runs](#learn-from-real-runs). For a skill that teaches a
   tool, add [tool guidance](tool-guidance.md).
2. Apply the line test. A skill is bloated when lines fail it: no-ops, duplicates,
   facts the environment holds, and stale or obsolete rules.
3. Check the skill's job, contract, finish condition, and invocation choice.
4. Report each failing line with its evidence. Label no-ops as predictions, because
   only a fresh-session run proves one.

Done: every line and reference was checked, and each finding has evidence.

## Rewrite

Use this when the user asks for a rewrite, or when a skill's structure no longer fits
its job.

1. **Record what must survive.** List the [invocation choice](#choose-who-invokes-it),
   local adaptations, supported hosts, legal notices, paths and anchors other files link to, tests that
   assert its text, consumers, and decisions the user has made. Done: the original can
   be recovered, and each source for the list was checked.
2. **Collect real requests.** Use its description, consumers, session history, and
   the rare cases its rules name. Done: each path has a request.
3. **Write fresh.** Write the contract, then the skill, from the requests and the
   survival list. Start a new file, because editing old text keeps its structure.
4. **Try it.** Run the requests in fresh sessions on each model that uses the
   skill. Include the old text when behavior must stay the same. If fresh sessions
   are unavailable, report the gap. Done: every request has a result or a stated gap.
5. **[Settle what changed](#settle-what-changed).**
6. **Check it.** Update the project record and any host metadata, such as
   `agents/openai.yaml`. Run the project checks. Verify new factual claims against
   sources.
7. **Report.** Give what changed, each dropped or moved group and why, where the settled
   list is, each request's result against the final text, and remaining gaps. Mark any
   result from an earlier draft as stale.

Claims of equal outcomes or context savings need a
[controlled comparison](controlled-comparison.md).

### Settle what changed

List each old rule the new text lacks, weakens, or moves, grouped by meaning. Use `git log -S`
or [Why](../../why/SKILL.md) when a reason is not obvious. A user's explicit decision
to remove or move a rule they named stands, so record it and report any risk you see. Approving
an audit's list is not that decision. Decide every other group in this order:

1. **Restore** anything on the survival list.
2. **Restore** a [guardrail](../SKILL.md#writing-for-agents). Skip it only if the new
   text states it as strongly before the action it constrains, code enforces it on
   every host that uses the skill, or a
   [controlled comparison](controlled-comparison.md) that exercises its condition shows the
   model no longer needs it.
3. **Drop** a no-op, a duplicate, a fact the environment holds, or a rule whose reason
   is obsolete. Name the evidence. A weaker version is not a duplicate. A no-op needs
   three runs without the line on each model that uses the skill, each reaching the
   line's condition and behaving correctly.
4. **Restore** a rule when a request failed without it, or when you can name the
   failure it still prevents.
5. **Otherwise** get the evidence or restore the rule.

A restored rule can sit in any home that reaches the agent before it needs the rule.
Write it in that home's voice, and rerun the affected requests. Done: every old rule is
in a group, and every group has a decision and a reason.

## Run trials safely

- Make each fresh session load the edited copy, and confirm it from a logged read. A
  worktree edit does not reach installed skills, so an unconfirmed trial is a gap.
- For a new or changed description or link, load the copy through the host's skill
  listing in a disposable profile, leave its path out of the prompt, and include near
  misses that must not fire it. If you cannot, report that firing is untested.
- Use disposable fixtures and profiles for any request that risks something a
  [guardrail](../SKILL.md#writing-for-agents) covers. Leave real configuration and
  logins untouched.
- "Each model" means the default model on each host that uses the skill.

## Choose who invokes it

Make the same choice in both hosts. [Claude Code reads
`disable-model-invocation` from `SKILL.md`](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill).
[Codex reads `policy.allow_implicit_invocation` from `agents/openai.yaml`](https://developers.openai.com/codex/build-skills#optional-metadata).

| | Model-invoked | User-invoked |
| --- | --- | --- |
| Use when | The agent must reach it on its own | Only a person ever starts it |
| Claude Code | Omit `disable-model-invocation` | `disable-model-invocation: true` |
| Codex | Omit `policy.allow_implicit_invocation` | `policy.allow_implicit_invocation: false` |
| Description | Only its triggers, written for the model | One line for a person, with no triggers |
| Cost | Its description loads on every turn | The person must remember it exists |

A person can type the name of either kind. A link lets an agent read a user-invoked
skill, but it grants nothing the choice withholds. Link one only behind a user's
request or a user-started workflow, and only when that request names its actions or
their effects.
Put content that workflows share in a reference or a model-invoked skill.

Every skill a person must remember costs their attention, so spend that only where
their judgment matters.

### Split by invocation

Split off a model-invoked skill only when it has a distinct trigger word you
actually use, or the agent must reach it alone.

## Learn from real runs

Read session logs for user corrections, skipped rules, repeated failures, tool
errors, and references that agents read or missed. Count actual uses, because a
session that mentions a skill did not necessarily use it. State the sample window and
denominator.
