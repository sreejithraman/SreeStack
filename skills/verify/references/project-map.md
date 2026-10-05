# Project verification map

Keep reusable product facts and recipes in the map. Retain run proof separately
unless the user requests committed evidence.

## Location and authoritative index

Honor an established project documentation location with equivalent structure.
For requested setup without an established location, start with:

```text
docs/agents/verification/
  index.md
  features/
    search.md
    exports.md
```

Start with flat feature files. Nest only when a substantial user-facing area
benefits from grouping, for example `features/billing/subscriptions.md`. Group by
user capability, rather than code module or harness. One file describes one
coherent capability and its distinct workflows. Split when prerequisites, entry
paths, or driving instructions materially diverge; merge coherent duplicated
workflows. File names and paths are working organization, not permanent contracts.

The index is authoritative and links every recipe, including nested files.
Check its links against a recursive listing of recipe files: fix orphaned files,
dead links, and duplicate entries together. State the mapped scope and known
unmapped surfaces so the index cannot imply whole-product completeness.

Keep shared facts in the index: prerequisites, secure credential setup by name,
useful launch and observable health checks, instance identity, fixture conventions,
harness acquisition or routing, evidence conventions, and run-owned cleanup or
recovery quirks. Cache facts a cold agent cannot readily discover, such as the
required connection order or why a reset matters. Link authoritative run docs or
configuration for obvious commands; avoid a generic tutorial or copies of
easy-to-discover `--help` output. Specify actual available tools and commands;
illustrative helpers must not masquerade as installed tooling.

Add or update a concise discovery pointer in the project's established
agent-facing instructions when appropriate. Respect local `AGENTS.md` or
`CLAUDE.md` conventions; do not require both files or create unnecessary layers.
For example: “For product acceptance checks or verification-map maintenance,
read `docs/agents/verification/index.md` and use Verify.” These docs need no
generated skill, frontmatter, or separate invocation policy.

## Feature recipe formula

Use these four sections for each feature. Preserve useful human meaning when
adapting an existing format; exact headings are less important than complete
recipes. Give features, workflows, entry points, and required assertions stable
identifiers where they help connect coverage and proof. Update references if an
identifier changes.

When creating recipes or clarifying how to pair actions with assertions and
proof, read the [recipe example](recipe-example.md).

### User-facing description

Describe what the user can accomplish. Include **Sub-features** listing the
distinct workflows and materially different states within that capability. Keep
source implementation detail only when it helps drive or judge the workflow.

### How to get to it

Describe navigation from the user's point of view. Enumerate supported entry
points such as menus, shortcuts, deep links, routes, public commands, or API
operations. State which workflows each entry point reaches and any differences
requiring separate assertions. A direct route alone does not prove menu or
shortcut navigation; cover entry-point-specific behavior when affected or when
the mapped workflow requires it.

### Driving it with `<available harness>`

Name the actual browser, device, CLI, HTTP, or PTY harness and how to locate it.
Reuse the project's tools and host routing; helpers are optional, and a CLI can
drive UI workflows. Document prerequisites, isolated fixtures, permissions,
starting state, and consequential side effects. Reference shared setup instead
of repeating it.

For each distinct workflow, pair every action with an observable expected result
and proof. Identify required assertions, including materially relevant error or
edge cases and their side effects. For persistence, specify a fresh read that
reloads durable state rather than reusing the current model. Make the recipe
usable without interpreting “confirm it works.” Record feature-specific cleanup
and recovery when shared instructions are insufficient.

### Gotchas

Record quirks needed to reproduce or interpret results: readiness signals,
permission states, environment limitations, unstable targets, asynchronous waits,
and product or harness limitations. Keep intended behavior clear even when the
current product violates it. Mark unproved instructions draft and name blocked
or untested steps; documentation status is separate from the product verdict.

## Maintain the current product model

Treat the map as revisable working knowledge. Rewrite, split, merge, rename,
regroup, or remove affected entries when capabilities change; repair the index
and cross-links in the same change. Preserve useful assertions and gotchas, not
outdated file layouts or wording. Remove obsolete capabilities based on product
evidence, rather than hiding a failing assertion. Keep human edits' useful meaning.

Check the requested scope against relevant source and public entry points. Add
missing recipes, update drifted shared facts and affected consumers, and leave
unrelated sections alone unless they block the run. For whole-map maintenance,
reconcile the index and recursive recipe inventory against source and live
behavior. Prove every new or changed recipe through the main Verify workflow,
reporting recipe proof separately from product verdicts.
