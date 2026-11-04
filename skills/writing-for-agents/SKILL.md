---
name: writing-for-agents
description: Write documents agents consume. Use when creating, revising, or auditing skills, checking their tool guidance, evaluating skill effectiveness or context use, or modifying AGENTS.md or CLAUDE.md.
---

# Writing for Agents

Write so an agent takes the same process on every run. The output can vary; the
path should hold steady. These rules apply to skills, `AGENTS.md` / `CLAUDE.md`,
and any doc reached by a link.

For a skill, read [skill mechanics](SKILL-MECHANICS.md) for frontmatter,
invocation, and router skills. Then add the guidance the work needs:

- Asked to audit a skill, or asked whether it has bloated:
  [auditing skills](references/auditing-skills.md).
- Changing an existing skill: [revising skills](references/revising-skills.md).
- Writing tool instructions, fixing drift, or replacing them with `--help`:
  [tool guidance](references/tool-guidance.md).
- Comparing instruction variants, or measuring their effect on outcomes or
  context use: [evaluating skills](references/evaluating-skills.md).

## Write plainly

Write for a capable reader who is new to this repo.

- **Lead with the action.** State what to do, then its condition or exception.
- **Give each instruction its own sentence.** Split a sentence that holds two
  actions.
- **Use everyday words.** Keep technical terms and names exact.
- **Name the thing.** Write "the model", not "the applicable selection".
- **Replace vague qualifiers with a test.** _Relevant_, _applicable_,
  _appropriate_, _as needed_, and _where helpful_ leave the decision open. Say
  how to decide, or cut the word.
- **Use one term for one thing.** Define a coined term once, where it first
  matters.
- **State what to do.** A ban brings the banned behavior to mind, so write "keep
  comments to one line". Keep a prohibition only for a hard guardrail, and pair
  it with the behavior you want.
- **Fix the rule, not the incident.** When an agent fails, change the rule that
  should have covered the failure. Add a rule only when none covers it, and
  write it for the class of failure.

| Before | After |
| --- | --- |
| Use the applicable selection, choosing the working selection, before direct work or dispatch. | Pick a model before you start or delegate. |
| A result is only accepted subject to inspection of its artifact. | Inspect the artifact before you accept a result. |
| Verification should be proportional to scope. | Check the changed behavior and the workflows that depend on it. |

If you have to read a sentence twice, rewrite it.

## Write pointers that fire

A **context pointer** names material outside the agent's context and says when
to reach it. A skill description and a line in `AGENTS.md` are both pointers. The
wording decides how reliably the agent reaches the material. If a must-have
target gets missed, sharpen the pointer first. Inline the target only if that
fails.

A pointer says what the material is and lists its **branches**: the distinct
cases that should load it.

- Phrase each branch as a request or situation: `Use when the user asks to clean
  up a finished task or unused worktree`.
- Give each branch one trigger. Synonyms for one case are one branch.
- Put the strongest trigger word first.
- Leave capabilities and procedure to the body.

## Spend load deliberately

- **Context load** is what always-loaded text costs the agent, on every turn,
  whether or not it fires. Prune pointers harder than bodies.
- **Cognitive load** is what the human must remember: which documents exist and
  when to use each. Spend it where human judgment matters.

## Place material by who needs it

Keep what every branch needs in the file. Move what only some branches need to a
separate file behind a pointer. If a reference is read on most tasks, move it
back in. Hiding needed material costs as much as burying the steps.

Put steps first. Order them as the agent performs them. Keep reference material
where it is consulted, and keep flat rule lists flat.

Keep a concept's definition, rules, and caveats under one heading. A long
document fails even when every line is true, because attention thins. Cut it by
moving branches out or splitting by branch or sequence.

## End each step on a checkable condition

Every step ends with a condition that shows it is done. Vague conditions such as
"understanding reached" invite the agent to stop early, pulled by the steps it
can see ahead.

- Sharpen the condition first.
- Ask for coverage: "every modified model accounted for" drives more digging
  than "produce a change list". "Every rule applied" works the same way for a
  list of rules.
- If the condition cannot be sharp and you see the agent rush, hide later steps
  behind a subagent or hand-off. An inline call leaves them in context, so it
  hides nothing.

## Split only for a reason

Each new document spends load, so split only for one of these reasons:

- **Sequence:** later steps tempt the agent to rush the current one. Merging
  sequences brings that risk back.
- **Branch:** each path should carry only what it needs.
- **Invocation:** see [splitting by invocation](SKILL-MECHANICS.md#splitting-by-invocation).

## Use leading words

A **leading word** is a compact term the model already knows and the agent thinks
with, such as _tracer bullet_ or _fog of war_. Use one to replace a repeated
explanation:

- "fast, deterministic, low-overhead" becomes _tight_.
- "a loop you believe in" becomes _red_: the loop goes red on the bug, or it
  does not.

Repeat the word, not its explanation. Used in a pointer, in your prompts, and in
the code, it also helps the agent find the material. Prefer an existing word;
a coined word costs its definition. A word too weak to change behavior needs a
stronger word: _relentless_ beats _thorough_.

## Prune

- **One home per meaning.** Changing a behavior should be a one-place edit.
  Repeating a meaning costs upkeep and tokens, and overstates its importance.
- **Let the environment answer.** Scripts, config, the directory layout, and
  `--help` are sources of truth. Copy from them only when looking it up is costly.
  Do record what looking cannot show: the unwritten convention, the reason for a
  choice, the gotcha.
- **Cut stale lines.** Remove lines that no longer bear on the task. Adding feels
  safe and removing feels risky, so documents silt up unless you prune on purpose.
- **Cut no-ops.** A **no-op** tells the model what it would do anyway. Delete the
  whole sentence. Defaults differ by model, so settle a disagreement by trying the
  document in a fresh session on each model that uses it.
