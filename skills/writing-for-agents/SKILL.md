---
name: writing-for-agents
description: Use before adding to or changing AGENTS.md, CLAUDE.md, or other documents agents consume, and when creating, revising, or auditing skills, checking their tool guidance, or evaluating skill effectiveness or context use.
---

# Writing for Agents

Write only what changes what an agent does. These rules apply to skills,
`AGENTS.md`, `CLAUDE.md`, and any doc reached by a link. Read them, then read
[the guide for what you are writing](#go-to-what-you-are-writing) before you write
anything.

**The test for every line:** would removing it change the agent's behavior? If
not, cut it.

**The exception is a guardrail:** a line against data loss, data leaving the machine,
a security failure, unauthorized or irreversible action, unplanned spending, a false
pass, lost review independence, or colliding writers. Keep a guardrail even when the
model follows it unprompted, until
[Settle what changed](references/working-on-skills.md#settle-what-changed) clears it.
When unsure whether to remove a line, treat it as a guardrail.

## Choose the home

Give each piece of guidance the strongest home that can hold it:

| Guidance | Home |
| --- | --- |
| Something that must always happen | Code: a script, test, hook, or gate |
| How to call a tool | The tool's help, errors, and schema |
| A fact the agent can look up | Scripts, config, and the directory layout |
| What the model or harness does unprompted, such as compaction and waiting | Nothing |
| History, credits, and measurements only a person reads | The README, commit message, or project record |
| The goal, the proof bar, the user's standards, who decides what, and reasons looking cannot show | The document |

Copy a fact into a document only when looking it up is costly.

To move a reminder into code, use [Show Don't Tell](../show-dont-tell/SKILL.md).
Remove the prose only after the code exists, rejects a violation, and runs on every
host that reads the document.

## Write plainly

Write for a capable reader who is new to this repo.

- **Lead with the action.** State what to do, then its condition.
- **Give each instruction its own sentence.**
- **Use everyday words.** Keep technical terms and names exact.
- **Name the thing.** Write "the model", not "the applicable selection".
- **Use one term for one thing.** Define a coined term once, where it first
  matters.

| Before | After |
| --- | --- |
| Use the applicable selection, choosing the working selection, before direct work or dispatch. | Pick a model before you start or delegate. |
| A result is only accepted subject to inspection of its artifact. | Inspect the artifact before you accept a result. |
| Verification should be proportional to scope. | Check the changed behavior and the workflows that depend on it. |

If you have to read a sentence twice, rewrite it.

## Write rules agents can apply

- **Replace judgment words with a test.** _Small_, _big_, _relevant_,
  _appropriate_, and _as needed_ leave the decision open. Say how to decide.
- **Prefer one test to a list of cases.** A test covers cases you did not foresee.
- **Sort by outcome, not source.** Two events that lead to the same outcome get
  the same rule, wherever they came from.
- **Write the normal path first.** Give a rare case one line, or a reference file
  if it needs more.
- **State what to do.** A ban brings the banned behavior to mind, so write "keep
  comments to one line". Keep a prohibition only for a hard guardrail, and pair it
  with the behavior you want.

## Add a rule

Name the failure the rule prevents, then stop at the first step that handles it. If
the user gives a rule's exact wording, skip these steps, add it as given, and report any
stronger home.

1. **Fix it below the document.** Use a [stronger home](#choose-the-home), such as a
   check or a clearer error.
2. **Check the model needs it.** [Reproduce the case](references/working-on-skills.md#run-trials-safely)
   three times on each model that reads the document, including any model that failed.
   If every run reaches the failure's condition and gets it right, add nothing and report
   that. Guardrails skip this step.
3. **Edit the rule that covers it.** Change that line instead of appending one.
4. **Add one rule.** Cover the class of failure, and put the incident in the commit
   message. [Place it](#disclose-progressively) on the lowest level that works.

## Give a job a goal and an end

Apply this when a document tells an agent to do a job, such as a skill or runbook.

State the outcome, the context the agent lacks, and how the result will be
judged. A list of steps caps the agent at your solution, so number steps only
where their order changes the result. State other required work as a condition
the result must meet.

End the job, and each stage in it, with a condition that shows it is done. A vague
condition such as "understanding reached" invites the agent to stop early.

- Sharpen the condition first.
- Ask for coverage: "every modified model accounted for" drives more digging than
  "produce a change list".
- If the condition cannot be sharp and you see the agent rush, hide later steps
  behind a subagent or hand-off. An inline call leaves them in context.

## Write pointers that fire

A **context pointer** names material outside the agent's context and says when
to reach it. A skill description and a line in `AGENTS.md` are both pointers. Its
wording decides how reliably the agent reaches the material. If a must-have
target gets missed, sharpen the pointer first. Inline the target only if that
fails.

- Phrase each case that should load it as a request or situation: `Read
  docs/release.md when cutting a release`.
- Leave the target's content to the target.

Always-loaded text costs context on every turn, so prune pointers hardest.

## Disclose progressively

Put each fact on the lowest level that still reaches the agent before it needs it.
From first loaded to last, the levels are always-loaded files, a skill's description,
its body, then references and docs behind a pointer. Keep what every path needs high,
and move what only some paths need behind a pointer.

Use real reads to check the cut: move a reference back in if most tasks read it.

Put each pointer at the step that needs it.

Keep a concept's definition, rules, and caveats under one heading. A long
document fails even when every line is true, because attention thins. Split a document
only to move what some paths skip, or to hide later steps from an agent that rushes.

## Use leading words

A **leading word** is a compact term the model already knows and the agent thinks
with, such as _tracer bullet_ or _fog of war_. Use one in place of a repeated
explanation: "fast, deterministic, low-overhead" becomes _tight_.

Repeat the word, not its explanation. Prefer an existing word, because a coined
word costs its definition. A word too weak to change behavior needs a stronger
one: _relentless_ beats _thorough_.

## Keep it alive

- **One home per meaning.** Link to the owner, so a change is a one-place edit.
- **Cut no-ops.** A no-op tells the model what it would do anyway. Delete the whole
  sentence. Defaults differ by model, so settle a disagreement with the runs in
  [Settle what changed](references/working-on-skills.md#settle-what-changed).
- **Rewrite silted documents.** Patches preserve a structure that stopped fitting.
  Write them again from their purpose.
- **Retest after major model releases.** Documents silt up because adding feels
  safe, and every rule assumes something the model cannot do alone. Remove rules
  that stopped changing behavior, using
  [Settle what changed](references/working-on-skills.md#settle-what-changed). A run
  that never reaches a rule's condition says nothing about it.

## Go to what you are writing

Before you write anything, read each guide that matches, even for a one-line change:

- A skill, including changing, auditing, or rewriting one:
  [working on skills](references/working-on-skills.md).
- `AGENTS.md`, `CLAUDE.md`, or docs agents read:
  [agent instructions](references/agent-instructions.md).
- Instructions for a CLI, API, or other tool:
  [tool guidance](references/tool-guidance.md).
- A claim that a change helps, keeps behavior equal, or saves context:
  [controlled comparison](references/controlled-comparison.md).
