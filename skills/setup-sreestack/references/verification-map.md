# Verification maps

A map lets a cold agent launch the product and check a feature without rediscovering
how. [Verify](../../verify/SKILL.md) reads it and reports drift. This guide creates and
maintains it, only when the user asks.

Create or change maps only in a repo the user owns or maintains. For any other repo,
say so and stop.

Keep reusable product facts and recipes in the map. Keep run proof outside it unless
the user asks for committed evidence.

## Location and index

Honor an established location with equivalent structure. Otherwise use
`docs/agents/verification/index.md`:

```text
docs/agents/verification/
  index.md
  features/
    search.md
    exports.md
```

Start with flat feature files. Nest one only when a large user-facing area needs
grouping, such as `features/billing/subscriptions.md`. Group by user capability, not by
code module or harness. One file covers one capability and its workflows. Split a file
when prerequisites, entry paths, or driving steps diverge, and merge files that repeat
one workflow. File names are working organization, not contracts.

The index links every recipe, including nested files. Check its links against a recursive
listing, and fix orphaned files, dead links, and duplicates together. State the mapped
scope and the known unmapped surfaces, so the index can't imply the whole product is
covered.

An index can hold shared setup before any recipe exists. Then say that feature coverage
isn't documented yet and mark unproved details. Create `features/` with the first recipe,
and link only files that exist.

## Shared setup

Give the index five parts. Write down what a cold agent can't find by looking, such as a
required connection order or why a reset matters. Link run docs and config for obvious
commands.

- **Launch:** prerequisites, how to start the app, secure credential setup by name, and
  the signal that a workflow is usable after initialization, migrations, and fixtures.
  For setup or first-run recipes, include launch from an isolated empty profile and any
  setup still unverified on the real target.
- **Doctor:** a read-only command that reports the instance, the build including
  uncommitted changes, the port, the login, each provider's test or live mode, and
  workflow readiness.
- **Drive:** how to get and route the browser, device, CLI, HTTP, or PTY harness, plus
  fixture conventions.
- **Evidence:** what to capture and where it goes.
- **Cleanup:** run-owned teardown and recovery quirks.

Ship repeated steps as commands in the repo, such as a doctor script, instead of prose
an agent retypes. Reuse the project's tools, and name only tools that exist here. Helpers are optional, and an example helper
must not read as installed tooling.

For executable suites, link the project command, pinned tool version or install source,
build and install prerequisites, explicit target selection, fixture and reset policy,
and report locations. Recipes link the actual test or flow files and map their checks to
required assertions. Keep executable steps in those files. Describe the user-visible
contract and the remaining interactive checks in the recipe. A suite name or a green CI
badge doesn't show which assertions it covers. For iOS suites, see
[iOS verification](../../verify/references/ios.md).

For authenticated workflows, link the approved credential mapping rather than copying
account scope. Record the expected role, credential-provider setup path, actual secure
delivery route, and runtime access and automatic login readiness separately, with exact
blockers when unproved. Keep values out of the map, and link this setup from recipes.

Add the verification pointer from [instruction pointers](project-workflow.md#instruction-pointers).

## Feature recipes

Use these four sections, keeping useful meaning when you adapt an existing format. Give
features, workflows, entry points, and required assertions stable identifiers where they
connect coverage and proof. See the [recipe example](recipe-example.md).

**User-facing description:** what the user can do, with **Sub-features** listing the
distinct workflows and states. Keep source detail only when it helps drive or judge.

**How to get to it:** navigation from the user's point of view. List entry points such as
menus, shortcuts, deep links, routes, public commands, or API operations, which workflows
each reaches, and any differences that need separate assertions. A direct route doesn't
prove menu or shortcut navigation.

**Driving it with `<available harness>`:** the real harness and how to find it, plus
prerequisites, isolated fixtures, permissions, starting state, and consequential side
effects. Link shared setup. For each workflow, pair every action with an observable
expected result and proof. Mark required assertions, including error and edge cases and
their side effects. For persistence, name a fresh read that reloads durable state. "Confirm
it works" isn't a step. Add cleanup and recovery that shared setup lacks.

**Gotchas:** quirks needed to reproduce or interpret results, such as readiness signals,
permission states, environment limits, unstable targets, async waits, and product or harness
limits. Keep intended behavior clear even when the product violates it. Mark unproved
instructions draft and name blocked or untested steps. A recipe's status is separate from
the product verdict.

## Set up a map

1. Inspect existing verification docs and reuse them. Keep useful assertions and gotchas.
2. Write shared setup and the doctor.
3. Seed recipes for the top 3 to 5 user features, or the scope the user named.
4. Prove at least one feature live through [Verify](../../verify/SKILL.md) before you
   hand over. Run its doctor, drive it, and confirm its cleanup.

Done: each recipe is proved or marked draft with its blocker, the index links resolve,
and the report separates recipe proof from product verdicts.

## Maintain a map

Treat the map as revisable. When capabilities change, or Verify reports drift, rewrite,
split, merge, rename, or remove the affected entries, and repair the index and links in
the same change. Remove a capability only on product evidence, never to hide a failing
assertion. Keep the meaning of human edits.

- **Targeted update:** check the requested scope against source and public entry points.
  Add missing recipes, fix drifted shared facts and what depends on them, and leave
  unrelated sections alone unless they block the run.
- **Whole map:** audit every mapped feature against source and live behavior, plus index
  links, the recursive recipe listing, and recent user-facing surfaces.

Prove every new or changed recipe through Verify. A recipe that detects a product failure
can be valid while its assertion stays failed.
