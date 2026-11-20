# Dependencies, stacks, and integration

Read this when scheduling outcomes with dependencies, provisional bases, fork-and-join stacks, or
cross-outcome integration. For single-outcome provisional rules, see
[Implement's provisional work](../../implement/references/provisional.md).

## Frontier scheduling

A dependency is satisfied for building when its artifact is available and verified at the
dependent's base. Another owner's unmerged branch can satisfy it (making the dependent provisional);
a finished turn, closed ticket, or absent PR cannot. Keep logical dependencies (`blockedBy`) apart
from branch order (`stackedOn`).

1. Read specs, tickets, open PRs, and edges; resolve cycles, missing blockers, and ambiguous
   contracts before starting affected work.
2. Compute the ready frontier using [To Tasks' ready rule](../../to-tasks/SKILL.md#ready). Track
   accepted artifacts yourself — trackers may hold tickets open until final merge.
3. Start ready owners within Orchestration's concurrency limit (using a canary unit first for 3+
   homogeneous outcomes). Independent outcomes branch from the intended shared base; dependents
   stack only once all required inputs are committed on the chosen parent branch.
4. Recompute the frontier after every accepted result, landing, answer, or dependency change.

## Coordinating provisional work

Record each provisional outcome's `basis`, `clears`, and `on` (if resting on another owner's
outcome) in `program.json`, and show what continues in the holding decision's `meanwhile`.

- **Base changed:** dependents restack and recheck bottom-first, one owner at a time.
- **Base landed, or decision answered as assumed:** owner refreshes affected proof, drops
  `## Provisional`, and returns through acceptance and landing release.
- **Decision answered another way:** owner rebuilds on the answer or offers the work for scrap.
- **Base scrapped or closed without merge (dead base):** halt every dependent with its own
  scrap-or-rebase decision in the Inbox. Record the user's choice atomically with
  `record.py work --scrap` or `--rebase-onto <base> [--stack-on <layer>]` plus `--decision`:
  - Onto another unmerged layer: retargets `stackedOn` and `provisional.on`.
  - Onto the target branch: drops `stackedOn` and clears dead-base `provisional`; owner restacks
    and refreshes proof.
- **Two close options:** when building both costs less than waiting, the outcome's owner builds
  both on separate branches as a [Swarm](../../swarm/SKILL.md) race; the user's answer keeps one
  and scraps the other.

## Stacks and joins

Plan branch topology before dispatch when outcomes must review as one chain or a dependent needs
multiple unmerged inputs:

- Linearize independent inputs A and B feeding C as A → B on A → C on B. Record `stackedOn` apart
  from `blockedBy`, and verify C's base contains both inputs before C starts.
- If A and B already have sibling PRs, pick an anchor and have B's owner restack only B's change
  onto A via [gh-stack](../../gh-stack/SKILL.md), preserving local files under
  [preserve local files](../../pr/references/preserve-local-files.md). Refresh diffs, review, and
  proof affected by the base change.
- Serialize restacks bottom-first (one writer per branch). Never invent multi-parent stacks in a
  linear-chain tool; if the repo cannot support the chain, collapse into one cohesive outcome with
  one owner or escalate the topology choice in the Inbox.

## Integration

Check compatibility at shared boundaries as results arrive. Concurrent merges move integration tips,
invalidating earlier proof — recheck affected scope before accepting, and verify combined behavior
where outcomes interact, not only isolated slices. When the program grows, classify additions as
required or optional (`work --optional`), and escalate scope/limit tradeoffs in the Inbox.
