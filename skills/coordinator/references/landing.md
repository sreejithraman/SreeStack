# Landing releases

Land picked under the finish-line policy authorizes merging an outcome within program scope. Your
release decides when; [Merge](../../merge/SKILL.md) enforces current-head review, required checks,
and passing proof.

## When an outcome may land

An outcome may land in dependency order once accepted at its current heads, nothing in it is
provisional, and no open decision or hold affects it. Unrelated outcomes need not wait on each
other. A stacked layer lands with every unmerged layer below it, so every layer in the set must
meet the same gates.

When the user reserves merge approval, put the accepted merge set (PRs and heads) in the Inbox
first; their answer authorizes that exact set at those heads.

## Name one lander

Record exactly one lander per merge set via `record.py land`:

- **The owner** (for a set within one outcome): record the release naming the owner, each PR's
  accepted head/base, and any resources dependents still need, then resume the owner. Immediately
  before submitting, the owner re-reads `HEAD:program.json` to confirm `chief`, its active release,
  itself as sole lander, and no affecting hold or decision, matching forge head/base to the
  release. Any mismatch returns to you. Replace an unable owner before releasing.
- **You** (for a set spanning multiple owners): confirm every owner stopped writing, then land via
  [Merge](../../merge/SKILL.md) and [gh-stack](../../gh-stack/SKILL.md) as a caller that keeps its
  own repair owners (resuming or replacing the slice's owner for any readiness gap). Merge stops on
  any PR whose body still carries `## Provisional`.

## Serialize landings

Keep at most **one pending landing per target branch** (counting queued merges and armed auto-merges,
including any an adopted owner armed). After it merges or is confirmed stopped, recheck the next
set against the updated base before releasing. Land overlapping sets one at a time even across
targets.

A shared parent lands once; coordinate bottom-up restacks and rechecks with dependent owners. Check
tracker parent/child rules before closing rollups, and verify actual merge state (a closed PR did
not land).

## Withdraw a release

Whenever a release's head, base, coordinator, lander, finish line, provisional state, decision, or
hold changes, withdraw it first (`record.py land --landing <ID> --to withdrawn --note "<why>"`)
before notifying its owner. Cancel any pending auto-merge or queue entry through Merge's controls
and confirm it stopped before releasing another set or lander. Report anything already merged or
unconfirmed. Only the user can lift a human hold.
