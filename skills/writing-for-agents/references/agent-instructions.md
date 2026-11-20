# Agent instructions

A root `AGENTS.md` is a map, not a manual. It loads before the agent knows the task, so
every line competes with the task.

## Keep the root thin

Keep a root line only if it passes all three tests. A guardrail stays until cleared even
if it fails them.

1. Most tasks in the file's scope need it, or it must reach the agent before an on-demand
   file could load.
2. The agent cannot find it by looking.
3. No tool or check enforces it today on every host that reads the file.

That usually leaves commands the agent cannot guess, traps from real failures,
guardrails, and the map: what each deeper file holds and when to read it. Omit project
overviews, directory listings, formatter rules, and copies of a source of truth. Keep
the root short—well under host truncation ceilings.

For a new or generated file (such as `/init` output), prove each command safely per the
Proof ladder in `SKILL.md`, then cut every line that fails the three tests.

## Use one file

Write `AGENTS.md` so every host reads the same source of truth. On a full rewrite or
consolidation, fold duplicate host-specific files (such as `CLAUDE.md` or `GEMINI.md`)
into `AGENTS.md`. If an external tool requires another filename, symlink it to
`AGENTS.md` rather than using `@` imports, which load eagerly and can break in
subfolders. Put truly host-only rules in that host's rules folder.

## Put the rest where it will load

| What it is | Where it goes |
| --- | --- |
| A rule for one folder or package | `AGENTS.md` in that folder, plus a root pointer naming it |
| A procedure only this repo uses | A repo doc, with a pointer in the root |
| A procedure several repos share | A skill |
| An explanation, decision, or spec | The project's docs folder |

Hosts walk up from the working directory, not down into subfolders from the root, so a
subfolder `AGENTS.md` needs a root pointer to be discoverable from root sessions. Use
pointers rather than eager `@` includes, which load with the file and save no context.

Keep guardrails in the root or in code, because a folder file or doc can arrive after the
first write.

Keep repo docs thin too. A doc holds what code cannot show: reasons, constraints,
decisions, and external requirements. Link to code, schemas, or commands for the rest.
Reuse docs the project already maintains and add no agent-only copy.

## Edit or rewrite instruction files

- **Targeted edit:** check only the changed lines and the commands they name. Report any
  other failing lines or competing host instruction files you notice without moving them
  unasked.
- **Full rewrite:** check every line and command from a clean checkout, moving rules that
  still matter to their proper home instead of deleting them, and settle removed or
  weakened rules per the Proof ladder.

Test instruction-file lines against the three root tests, and doc lines against what a
doc holds. Prove each covered command safely per the Proof ladder.

After adding, moving, or removing an instruction file, start fresh sessions at the root
and in each changed folder and confirm every expected file loads (via the host's context
inspector or by asking it to quote the rule).

Done: every file that should load still does, every covered command is proved or reported
unproven, and every covered line passes its test, is a guardrail, or was supplied or kept
explicitly by the user.
