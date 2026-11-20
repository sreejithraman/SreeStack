---
name: writing-for-agents
description: Write, edit, audit, or rewrite skills, AGENTS.md, CLAUDE.md, tool guides, or agent docs, or evaluate whether an instruction change improves agent behavior or context use.
---

# Writing for Agents

Make every line in an agent-facing document earn its context by changing what the agent
does. Start from the document or skill to create, edit, audit, or evaluate and the goal
or failure behind it. Leave the guidance in the strongest home that can hold it—code,
tool help, or the document—with proof matching the change's risk. You are done when
every covered line passes the line test or is a protected guardrail, project checks
pass, and the required proof for the change type succeeded or has its gap stated.

## Go to the matching guide first

Read only the guide for the work in front of you before editing:

- `AGENTS.md`, `CLAUDE.md`, or repo docs: [agent instructions](references/agent-instructions.md).
- Creating, editing, auditing, or rewriting a skill: [working on skills](references/working-on-skills.md).
- Documenting a CLI, API, SDK, native tool, MCP tool, or bundled script: [tool guidance](references/tool-guidance.md).
- Sampling session logs, running trials, closing a cross-model gap, or running a controlled comparison: [controlled comparison](references/controlled-comparison.md).
- Moving a prose reminder into code, tests, hooks, or types: [Show Don't Tell](../show-dont-tell/SKILL.md).

## Guardrails

**The line test:** would removing this line change what the agent does? If not, cut it.

**The exception is a guardrail:** a rule against data loss, data leaving the machine, a
security failure, unauthorized or irreversible action, unplanned spending, a false pass,
lost review independence, or colliding writers. Keep a guardrail even when the model
follows it unprompted, until code enforces it on every host or a controlled comparison
exercising its condition clears it. When unsure whether a line is a guardrail, treat it
as one.

**Exact user wording:** if the user supplies a rule word for word, add it as given,
report any stronger home, and skip behavioral trials.

## Choose the home

Give each piece of guidance the strongest home that can hold it:

| Guidance | Home |
| --- | --- |
| Something that must always happen | Code: a script, test, hook, or gate |
| How to call a tool | The tool's help, errors, and schema |
| A fact the agent can look up | Scripts, config, and the directory layout |
| What the model or harness does unprompted (compaction, waiting, standard style) | Nothing |
| History, credits, paper stats, and measurements only people read | `README.md`, `SOURCES.md`, or commit messages |
| The goal, proof bar, user standards, ownership, and traps looking cannot show | The document |

Copy a repo fact into prose only when looking it up is costly. Remove a prose reminder
only after code exists, rejects a violation, and runs on every host that reads the
document.

## Write rules agents follow

- **State outcome, constraints, and a falsifiable `Done` condition.** Number steps only
  when order changes the result; express other required work as conditions the result
  must meet. Ask for coverage (*"every modified model accounted for"*) rather than vague
  completion (*"understanding reached"*). If an agent still rushes an early stage, hide
  later stages behind a subagent or handoff.
- **Replace judgment words with a test.** Swap *small*, *big*, *relevant*, *appropriate*,
  *tight*, or *as needed* for how to decide. Prefer one test over a list of cases, and
  sort rules by outcome rather than source.
- **Set precedence when rules can collide.** Reserve absolute words for real guardrails;
  where priorities can conflict, state which wins (user instruction > guardrail > project
  rule > skill default).
- **Pair prohibitions with the replacement path.** State the action you want directly;
  when forbidding an action, name what the agent should do instead.
- **Give a one-clause *why* for counterintuitive rules.** Skip rationale for obvious
  rules, but explain surprising traps (*"Run `gh` outside the sandbox; its token lives in
  macOS Keychain"*) so agents neither rationalize around them nor misapply them when
  conditions change.
- **Calibrate with 1–2 concrete examples.** Use a short before/after or boundary example
  whenever prose alone leaves format, scope, or tone open:

| Before | After |
| --- | --- |
| Use the applicable selection, choosing the working selection, before direct work or dispatch. | Pick a model before you start or delegate. |
| A result is only accepted subject to inspection of its artifact. | Inspect the artifact before you accept a result. |
| Verification should be proportional to scope. | Check the changed behavior and the workflows that depend on it. |

- **Place end-of-task gates where attention is fresh.** Put final checks at the end of a
  workflow or in code, not buried in an opening paragraph.

## Load as late as possible

From earliest to latest loaded: always-loaded root files → skill descriptions → skill
body → references and docs behind a pointer. Keep what every path needs early; move
branch-specific detail behind a request-shaped pointer placed at the step that needs it
(`Read docs/release.md when cutting a release`). Leave the target's content to the
target.

- **One home per meaning.** Keep a concept's definition, rules, and caveats under one
  heading, and link to the owner instead of repeating it.
- **Keep references flat and independent.** Link every reference directly from `SKILL.md`
  so agents do not miss nested reads, and never cross-reference another document by step
  number.
- **Link only to unread material the agent needs to act.** Keep links for unread
  references, scripts, handoff skills, and external specs the agent must look up (such as
  an experimental CLI format). Skip same-file `#anchor` jump-links, back-links to an
  already-loaded `SKILL.md`, repeated links to the same target in one file, and
  background or citation URLs (put those in `SOURCES.md` or `README.md`).
- **Keep script outputs compact.** When a skill ships a helper script, emit a compact
  verdict or structured summary to stdout and diagnostics to stderr.
- **Keep docs alive.** Move a reference back in if most runs read it. Rewrite silted
  documents fresh from their purpose instead of patching around dead structure, and
  retest assumptions after major model releases.

## Match proof to risk

Before adding a rule, name the failure it prevents and stop at the first home that
handles it: enforce it in code or tool errors first, edit an existing rule that covers
the class before appending a new line, and put incident details in the commit message.

| Change | Minimum proof |
| --- | --- |
| Factual or command fix, link fix, exact user wording, or rule moved into passing code | Prove the command safely or verify against source, and run project checks. |
| Adding or editing a behavioral rule or trigger | Confirm the failure (session log or reproduction), apply the edit, and run a fresh-session smoke trial (plus a near-miss for triggers). |
| Removing, weakening, moving, or rewriting guidance | Run [Settle what changed](references/working-on-skills.md#settle-what-changed); keep survival items and guardrails intact. |
| Claiming measurable improvement (cost, turns, pass rate) or clearing a guardrail | Run a controlled comparison. |

**Proving a command safely:** run a command live only if it risks nothing a guardrail
covers or the request authorizes it. Otherwise use a documented dry run, disposable
fixture, or real-schema stub (which proves call construction, not live effects), or cite
the exact source, and report live effects as unproven.
