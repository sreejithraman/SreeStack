# Landing releases

Land picked under the finish-line policy authorizes merging an outcome within
the program scope. Your release decides when, and Merge's own requirements stay
the gate: review of the current head, required checks, and passing proof. Merge
owns the landing mechanics; this reference keeps the coordination that stops
two landings from colliding.

## When an outcome may land

An outcome can land in dependency order once it is accepted at its current
heads, nothing in it is provisional, and no open decision or hold affects it.
Later outcomes need not wait for unrelated ones. A stacked layer lands with every
unmerged layer below it, so each of those layers must meet the same conditions.

Where the user decides merges, first put the accepted merge set in Needs you,
naming its PRs and heads. The outcomes stay accepted, and the answer grants that
set at those heads.

## Name one lander

Record exactly one lander for each merge set.

- **The owner,** for a set within its own outcome. Record a **landing release**
  from the current chief naming the owner, each PR with its accepted head and
  base, and any resources dependents still need, then resume the owner with it.
  The record is authoritative. Immediately before submitting a merge, the owner
  re-reads it to confirm the current chief, its active release, itself as the
  one lander, and no affecting decision or hold, and matches the forge's head
  and base to the release. A mismatch returns to you for reconciliation. If the
  owner cannot act, replace it under Orchestration's
  [replace an owner](../../orchestration/references/reuse-and-recovery.md#replace-an-owner)
  first.
- **You,** for a set that spans owners, such as outcomes that must ship
  together. Confirm its owners have stopped writing, then land it through
  [Merge](../../merge/SKILL.md) and [gh-stack](../../gh-stack/SKILL.md). Merge
  stops on any PR whose body still has a `## Provisional` section. Invoke Merge as
  a caller that keeps its own repair owner for each PR, and resume that owner,
  or replace it if it cannot act, for any readiness gap Merge returns.

## Serialize landings

Keep one pending landing per target branch, counting queued merges and armed
automatic merges, including one an adopted owner armed. After it merges or is
confirmed stopped, recheck the next set against the current base before you
release it. Land overlapping sets one at a time, even across targets.

A parent shared by several outcomes lands once; recheck each dependent after it
restacks, and coordinate restacks with the branch owners. Read the tracker's
parent and child completion rules before closing a rollup, and keep unfinished
and unrelated children open. Confirm the actual merge and issue state: a PR
closed without merge did not land.

## Withdraw a release

When a release's head, base, chief, lander, finish line, provisional state,
decision, or hold changes, withdraw it in the record before you notify its
owner. Reconcile any in-flight submission at the forge, and cancel pending
automatic or queued landing through Merge's supported controls. Confirm it
stopped before you assign another lander or release the next set. Report
anything that already merged or whose cancellation you cannot confirm. Only the
user can lift a human hold.
