# Executing substantial work

## Build the Lever

For substantial edits, migrations, analyses, or checks, consider a rerunnable
codemod, script, query, generator, or shared task recipe. Prefer the smallest tool
that makes the work or its proof reproducible. Do one representative unit to learn
the recipe, then compare the automated result with that known case. Make reruns
safe and keep the tool when future verification or maintenance needs it.

Use a deterministic pass for mechanical work it can cover; reserve independent
agents for decisions and slices that benefit from them. Keep shared recipes and
acceptance criteria outside delegates' writable scope. Small obvious edits can
remain direct; tool-building should earn its setup and maintenance cost.

## Sequence work into verifiable units

Order dependent work into coherent increments with a check at each boundary.
Establish the baseline, make one meaningful change, inspect the result, then
build on it. Choose boundaries that localize failures and fit the workflow;
one unit may include a failing reproduction and its repair. A tool can make the
checks cheap without turning every file into a separate delivery unit.

Order reviewable delivery so the evidence explains the change: baseline before
treatment, subtraction before reshape, foundations before dependents. Use
[gh-stack](../../gh-stack/SKILL.md) when stacked delivery is requested. Its layer
checks and repository CI requirements govern what can land independently.

## Guard the Context Window

Search and read bounded material tied to the current decision. Keep source paths,
requirements, and accepted decisions available; summarize large outputs instead
of repeatedly loading them. Delegate independent bulk investigation when it
improves coverage or preserves useful parent context. Use
[orchestration](../../orchestration/SKILL.md) for ownership and acceptance; context
pressure does not justify missing scope or trusting an unverified child summary.

## Never Block on the Human

Resolve routine, reversible choices from the repository and evidence, do the
authorized work, and present a reviewable result. Use experiments for empirical
questions. Ask when a missing preference, product choice, access grant, or explicit
gate materially changes the outcome and cannot be inferred; continue independent
work while waiting. Host permissions and existing user authorization govern
external actions, destructive steps, and publication. A principle expands neither.

## Encode Lessons in Structure

For an evidenced recurring instruction, choose the highest effective enforcement:
remove the opportunity through ownership or interface design, encode the invariant
in types, add an actionable lint/build check, or test the behavior. Read existing
checks and their wiring before creating another. Use instructions for judgment
those mechanisms cannot encode. Remove redundant reminders once the constraint
enforces their rule; keep navigation to the supported path where it helps users.

[Correct](../../correct/SKILL.md) owns recurring-failure investigation and repair;
the shared [guard proof](../../codebase-design/references/preventing-mistakes.md)
defines historical rejection and repaired-path success. This differs from building
a lever for today's task: it prevents the next occurrence of a known failure class.
