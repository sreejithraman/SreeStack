# Dependencies and provisional work

Use this to schedule outcomes that block each other, build on unmerged or
undecided inputs, or join into one review chain.

## Dependencies

A dependency is satisfied for building when its artifact is available and
verified at the dependent's base. Another owner's unmerged branch can satisfy
it, and the dependent is then [provisional](#provisional-work). A finished owner
turn, a closed ticket, or a PR whose artifact is not in that base cannot. The
base must land before the dependent does only when the dependent's finish line
lands.

Keep logical dependencies (`blockedBy`) apart from branch order (a layer's
stack parent). A provisional base is a satisfied build input, not a missing one.

## Schedule ready outcomes

1. Read the specs, tickets, existing PRs, and dependency edges. Account for
   completed and partial work. Resolve missing blockers, cycles, and ambiguous
   contracts before starting the work they affect.
2. Find the frontier: unfinished outcomes that are
   [ready](../../to-tasks/SKILL.md#ready). Track accepted artifacts yourself; a
   tracker may keep tickets open until the final merge and so misstate
   readiness. A decision, a support dependency, or missing proof can block an
   outcome even when its ticket edges are clear.
3. Start ready owners within Orchestration's limits. Independent outcomes start
   from the intended shared base. A dependent can stack only when its inputs are
   committed on the chosen parent branch; otherwise it waits for them at its
   base. Several inputs must all be present in that base; a ticket edge alone
   does not put their code there. Use [gh-stack](../../gh-stack/SKILL.md) for
   stack operations.
4. Record each result's base, head, and verification.
5. Recompute the frontier after each accepted result, landing, answer, or
   dependency change. Permission to start a stacked dependent is not delivery of
   its parent.

## Provisional work

Implement defines [provisional work](../../implement/SKILL.md#2-state-the-finish-line-and-prepare):
it rests on another owner's unmerged branch or PR, or on a recorded assumption
awaiting a decision. It can build, prove, and be shown. It is reviewed only when
a PR state was requested, never merges, and never takes destructive or
outward-facing steps on its own; Implement says what the user's scrap allows.
Land becomes Try while it lasts. An owner's own planned
layers are not provisional.

For each provisional outcome, record the branch, PR, or assumption it rests on,
the open decision or unmerged base, what may continue, and that it cannot
land. The morning view shows it on the outcome and on each Need
that holds it.

When the base or decision moves:

- **Base changed:** its dependents restack and recheck, bottom first, one owner
  at a time. Record the new heads and bases.
- **Base landed, or decision answered as assumed:** the owner refreshes the
  affected proof and then removes the PR body's `## Provisional` section. The
  picked finish line returns, and the outcome goes through acceptance and
  release again.
- **Decision answered another way:** the owner rebuilds on the answer, or
  offers the work for scrap.
- **Base scrapped:** each dependent gets its own scrap or rebase choice in
  Needs you. Nothing continues on the scrapped base.

When two options are close and building both costs less than waiting, the
outcome's owner builds each on its own branch, as a Swarm race. The answer keeps
one and scraps the other.

### Examples

**Another owner's unmerged layer.** W2 reports retry status, which needs W1's
cancellation layer W1-L2, still in review. W2's owner stacks W2-L1 on W1-L2 and
marks W2 provisional on W1, so its Land becomes Try. When W1 lands, W2 restacks
onto the default branch, refreshes its proof, and drops the Provisional
section; then it is accepted and released like any Land outcome.

**An open decision.** W6 expires old downloads, and W6-D1 asks whether expired
entries stay visible. The recommended option, keep them, is reversible, so W6
builds on it. W6-D1 blocks W6 at `acceptance`, and its `meanwhile` says W6 builds
on keeping the entry. If the user picks hiding, W6's owner reworks or offers
scrap.

**An option that is not reversible.** A migration whose recommended option
deletes rows waits: its Need blocks it at `start`, and unrelated outcomes keep
running.

## Stacks and joins

Plan branch topology before dispatch when outcomes must review as one chain, or
when a dependent needs several unmerged inputs. For independent A and B feeding
C, a reviewable linear chain is A, then B on A, then C on B. Record that
branch-order constraint apart from the logical dependencies, and verify C's base
contains both inputs before C starts. B and C are provisional while a base below
them belongs to another owner and is unmerged.

If A and B already have sibling PRs, choose an anchor and work through their
owners and gh-stack: B's owner restacks only B's own change onto A's verified
branch and updates B's PR base to A. C can then start above B. Preserve local
work through PR's [preserve local files](../../pr/references/preserve-local-files.md).
Check that each immediate-base diff still holds its intended change, and refresh
review and proof that changed heads or bases affect. This prepares a review
chain; it lands nothing.

After A changes, B's owner restacks and verifies first, then C's. Record the new
heads and bases and recheck affected evidence. Serialize these operations, one
writer per branch. If the repository cannot support the chain, make the batch
one cohesive outcome with one owner and bounded workers, or put the topology
constraint in Needs you. Never wait indefinitely for merges outside the finish
line, and never invent multi-parent stacks in a linear-chain tool.

## Integration

Check compatibility at shared boundaries as results arrive. Serialize branch,
index, and stack operations through their owners. Concurrent work can move an
integration tip after a worker read it: incorporating an earlier tip guarantees
neither a fast-forward nor that earlier proof covers the merge. Restacking or
changed upstream behavior can invalidate downstream evidence, so recheck the
affected scope before accepting.

Verify the combined behavior where outcomes interact, not only each outcome. A
cohesive batch delivered through one integration PR has one owner, who uses
bounded workers inside it.

When the program grows, classify each addition as required or optional, and put
limits that need the user's decision in Needs you.
