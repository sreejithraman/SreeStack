# Designing a stack

How to decide what goes in each layer. Read this before running `gh stack init` or adding a layer.

## Contents

- [When to add a layer](#when-to-add-a-layer)
- [Set the order](#set-the-order)
- [Branch naming](#branch-naming)
- [Staging changes deliberately](#staging-changes-deliberately)
- [Separate stacks for independent outcomes](#separate-stacks-for-independent-outcomes)

## When to add a layer

Split work into layers only for true dependency order and reviewability. A layer is one result a
reviewer can assess.

Add a branch when the next result depends on what you have built so far and is easier to review on
its own. Signals:

- The next changes have a different reviewer audience
- The current branch's diff is already large enough to review on its own

Tests and docs stay with the behavior they prove unless there is a concrete review reason to
separate them.

One result is an ordinary PR through [PR](../../pr/SKILL.md), not a stack, even when the user asks
for a stack; say why in your reply to them. GitHub needs at least two PRs to form a stack, so a
one-layer stack never appears there and `gh stack merge` refuses it.

## Set the order

A stack is a dependency chain. If code in one layer depends on code in another, the dependency must
live in the same branch or a lower one.

When the order is already known, lay it out at once:

```bash
gh stack init billing/schema billing/invoices billing/receipts
```

`init` checks out the last branch, so run `gh stack bottom` before the first commit.

Otherwise, start with the first layer and add the next as the work takes shape:

```bash
gh stack init billing/schema
# commit the schema
gh stack add billing/invoices
```

Fixing the order later is expensive: there is no non-interactive in-place reorder, so it means
[`unstack` and `init` again](troubleshooting.md#restructuring-a-stack). Splitting a finished branch
has the same cost, so start the next layer as soon as its result is clear.

## Branch naming

Prefer a shared topic prefix plus the layer's result:
`<topic>/<result>` — for example, `billing/schema`, `billing/api`, `billing/ui`.
This keeps related branches recognizable without using generic names that could belong to any
stack. **User and repository branch naming conventions take precedence; follow them instead.**

Names are used exactly as given — nothing is prepended or transformed, and slashes are kept, so
`gh stack add refactor/foo` creates a branch literally named `refactor/foo`.

If you pass `-m` without a branch name, the name is generated from the commit message in
date-and-slug form (for example `03-24-add_api_routes`). Prefer naming the branch yourself.

## Staging changes deliberately

Use `git add` and `git commit` directly rather than the `add -Am` shortcut. The point is control
over which changes land in which branch. With several modified files in the working tree, stage the
subset that belongs to the current layer, commit it, then create the next branch and stage the rest
there:

```bash
git add internal/models/user.go internal/models/session.go
git commit -m "Add user and session models"

gh stack add api-routes
git add internal/api/routes.go internal/api/handlers.go
git commit -m "Add user API routes"
```

Multiple commits per branch are fine. What matters is that every commit in a branch serves that
layer's result, and that a change belonging to another result goes in that result's branch.

Note that `gh stack add <branch>` without `-Am` does not touch the working tree, so uncommitted
changes carry over to the new branch. Commit or stash first if you want the new layer to start clean.

## Separate stacks for independent outcomes

A stack should read as a coherent progression: a reviewer walks the PRs bottom to top and sees each
result build on the one below.

**Use a single stack** when each layer depends on the one below it.

**Start a separate stack or PR** for an independent outcome, even inside one feature, and for
unrelated work such as a different feature, an unrelated bug fix, or an independent refactor. When a
later result needs two independent outcomes, put both below it in one stack, in either order. Do not
mix efforts into one stack just because you happened to work on both. Use `gh stack init` for the
new effort, or `gh stack checkout <target>` to move between existing stacks.

A trivial incidental fix can ride along in the current stack. Once it grows into its own project, it
deserves its own stack.
