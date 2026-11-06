# Agent instructions

A root `AGENTS.md` is a map, not a manual. It loads before the agent knows the task, so
every line competes with the task.

## Keep the root thin

Keep a line only if it passes all three tests. A guardrail stays until
[Settle what changed](working-on-skills.md#settle-what-changed) clears it, even if it
fails them.

1. Most tasks in the file's scope need it, or it must reach the agent before an on-demand
   file could load.
2. The agent cannot find it by looking.
3. No tool or check enforces it today on every host that reads the file.

That usually leaves commands the agent cannot guess, traps that caused real failures,
guardrails, and the map: what each deeper file holds and when to read it. Leave out
overviews, directory listings, rules a formatter enforces, and copies of a source of truth.

For a new or generated file, such as `/init` output, prove each command as
[targeted change step 4](working-on-skills.md#change-an-existing-skill) says, then cut every
line that fails the tests. In [one study](https://arxiv.org/html/2602.11988v1), generated
files raised cost by 20–23% and slightly lowered success.

Treat host limits as ceilings: [Claude Code](https://code.claude.com/docs/en/memory) advises
under 200 lines per file, and [Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
stops adding files at 32 KiB combined by default.

## Use one file

Write `AGENTS.md`, because both hosts read it. Any `CLAUDE.md`, `.claude/CLAUDE.md`, or
`CLAUDE.local.md` at or above the working directory makes Claude Code skip `AGENTS.md`, and
a user's Project instructions setting can hide that.

- On a Rewrite of an instruction file or a request to consolidate them, move every
  `CLAUDE.md` in the repo into an `AGENTS.md` in one change.
- Put Claude-only lines in `.claude/rules/`.
- If a tool requires a `CLAUDE.md`, symlink one to each `AGENTS.md`. A `CLAUDE.md` holding
  `@AGENTS.md` loses the root rules in a session started in a subfolder.

Checked on Claude Code 2.1.318 and Codex 0.166.0. Recheck on other versions.

## Put the rest where it will load

| What it is | Where it goes |
| --- | --- |
| A rule for one folder or package | `AGENTS.md` in that folder, plus a root pointer that names it |
| A rule for paths spread across the repo | `.claude/rules/` with `paths` on Claude Code, plus a root pointer for Codex |
| A procedure only this repo uses | A doc, with a pointer in the root |
| A procedure several repos share | A skill |
| An explanation, decision, or spec | The project's docs folder |

From the root, Codex never loads a folder file, Claude Code loads it only on Read, and a
general pointer failed on Codex. Use pointers, not `@path` imports, because an import loads
with its file and saves no context.

Keep guardrails in the root or in code, because a folder file or doc can arrive after the
first write.

Keep the map in the root. In [Vercel's evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals),
an always-loaded docs index passed 100%, and a skill agents had to choose to load passed
53%.

Keep docs thin too. A doc holds what code cannot show: reasons, constraints, decisions,
and outside requirements. Link to the code, schema, or command for the rest. Use the docs
the project already maintains, and add no agent-only copy.

## Change an existing file

Use a [targeted change](working-on-skills.md#change-an-existing-skill) for one edit, and
[Rewrite](working-on-skills.md#rewrite) to thin a whole file. Move what still matters to
its home instead of deleting it.

A targeted change covers the changed line and any command it names. Report any other
failing line you notice, and leave it as it is. It moves no `CLAUDE.md`. If Claude Code
would skip the edited `AGENTS.md` in any session, report that instead. A Rewrite covers
every line and command, from a clean checkout.

Test instruction-file lines with the three tests, and doc lines against what a doc holds.
Prove each covered command as targeted change step 4 says.

After adding, moving, or removing an instruction file, start fresh sessions at the root
and in each changed folder, and confirm that every file that should load still does:

- **Claude Code:** run `/context all`. After a move, confirm no real `CLAUDE.md` remains in
  the repo. For a rule with `paths`, have the agent open a matching file and quote the rule.
- **Codex:** ask it to summarize its current instructions.

Done: every file that should load still does, each covered command is proved or reported
as unproven, and each covered line passes its test, is a guardrail, or is a line the user
gave word for word or asked to keep.
