# Sequence PR-sized work

Use for a spec, ticket set, migration, or queue with blocking relationships.
The graph's nodes are PR-sized units; tickets map to those units. Keep the
program's requested finish line with the graph.

## Dependencies

A dependency is satisfied when its required artifact is available and verified
at the dependent's base. An unmerged stacked parent can satisfy it; a finished
owner turn, a closed ticket, or an open parent PR whose artifact is not yet in
that base cannot. Landing is required only when the finish line requires it.

## Sequence

1. Read the specs, tickets, existing PRs, and dependency edges. Account for
   completed and partial work. Resolve missing blockers, cycles, and ambiguous
   contracts before starting affected work. Group tightly coupled tickets in
   one PR; give independent changes separate owners.
2. Identify the frontier: unfinished units whose required inputs are available
   and verified. Track accepted artifacts yourself; a tracker may keep tickets
   open until the final merge and therefore misstate readiness during a run.
   A human decision, support dependency, or missing acceptance contract can
   block a unit even when its ticket edges are clear.
3. Start [ready](../../to-tasks/SKILL.md#ready) owners within Orchestration's limits. Independent PRs start from
   the intended shared base. A dependent PR can stack only when its required
   inputs are committed on the chosen parent branch; otherwise it waits for
   delivery to its base. Use [gh-stack](../../gh-stack/SKILL.md) for stack
   capabilities and management. Several blockers must be present in that base;
   a ticket dependency alone does not place their code there. For a join of
   independent branches before landing, use the topology procedure below.
4. Record base/head and verification for each result. Check compatibility at
   shared boundaries. Serialize branch/index changes and stack operations
   through their owners. Concurrent work can move an integration tip after a
   worker read it; do not assume that incorporating an earlier tip guarantees
   a fast-forward or that prior verification covers the resulting merge.
5. Recompute the frontier after accepting evidence or changing dependencies.
   Distinguish permission to start a stacked PR from completed delivery of its
   parent. Restacking or changed upstream behavior can invalidate downstream
   evidence; recheck the affected scope before accepting delivery.
6. Verify the combined outcome, not just the individual PRs. If a cohesive
   batch is intentionally delivered through one integration PR, it has one PR
   owner and uses bounded workers internally. The owner integrates and verifies
   that result; the workers are not separate PR sessions.

## Join unmerged inputs

Plan branch topology before dispatch when the user requests a stack, or when a
dependent PR needs several inputs and the finish line keeps them unmerged. For
two independent units A and B feeding C, a reviewable linear chain can be A,
then B based on A, then C based
on B. Record the extra branch-order constraint separately from logical ticket
dependencies. Verify C's base contains both required artifacts before starting it.

If A and B already have sibling PRs, choose an anchor and coordinate through
their owners and gh-stack: the B owner restacks only B's own change onto A's
verified branch and updates B's PR base to A. C can then start above B. Preserve
local work through PR's history-change procedure. Check each immediate-base
diff still contains its intended change and refresh review/verification affected
by changed heads or bases. This prepares a review chain; it does not merge a PR
or authorize landing on the default branch.

After A changes, have the B owner restack and verify first, then the C owner;
record the new heads/bases and recheck affected evidence. Serialize these
operations and keep one writer per branch. If the repository cannot support
that chain, choose a cohesive integration PR with one owner and bounded workers,
or surface the topology constraint and needed boundary decision. Do not wait
indefinitely for merges outside the requested finish line or invent multi-parent
stack support in a linear-chain tool.

When work grows, classify each addition as required or optional and report
limits that need a user decision.
