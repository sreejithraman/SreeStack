# Stacked Pull Requests

Read this reference fully when delivery needs two or more dependent PRs.

## Terms And Invariants

A **stack** is an ordered set of dependent PR **layers** from base to tip. Each layer has one purpose, one head branch, one immediate base, one reviewable diff, and one PR. Swarm and Push may own independent PRs or more than one stack; each stack remains one linear chain.

The first layer targets the delivery base. Each later layer targets the branch immediately below it. Every owned change belongs to exactly one layer.

Agent shards describe work ownership. PR layers describe code dependency and review order. Map one to the other only when both shapes match.

## Choose A Stack

Use a stack when the change has a real dependency order and each layer can be reviewed as a coherent step. Keep one PR when splitting would create pass-through layers, temporary breakage, or review order with no code dependency.

Each layer should be safe to merge before the layer above it. A layer that needs later code to build, test, or preserve behavior belongs with that later code unless a guarded intermediate state is intentional.

## Plan Progressively

Make a layer concrete when current work has a reviewable boundary and a real dependency on the layer below it. Keep later work in the task or ticket graph until its boundary becomes clear.

Record each current layer from base to tip:

```text
Layer:
Purpose:
Head branch:
Immediate base:
Owned commits and files:
Depends on:
PR URL:
Current head SHA:
Review-push-and-watch state:
```

Finish current planning when the order is acyclic, every current change has one owner layer, every immediate base exists or has a creation step, and every current diff states a reviewer-facing purpose. Future layers need no branch, commit, or file plan.

## Create And Process

Create local branches and commits for current layers from base to tip. Leave each push and PR creation to `/pr-prep`, passing the exact head branch, immediate base, owned commits and files, existing PR if any, and ready mode without `yolo`.

Run `/pr-prep` on the base layer first, using its immediate base as the review base. Continue upward only after the lower layer is stable or has a blocker that does not invalidate the higher diff.

Each layer has its own PR feedback and CI state. Higher-layer CI usually exercises the cumulative code through that layer. `/pr-prep` owns the state of one layer; swarm and push owns the ordered set.

## Invalidation And Restacking

A change to a lower layer invalidates every descendant whose base history or effective diff changed.

After a lower-layer push:

1. Mark affected descendants stale.
2. Rebase or rebuild each descendant onto its updated immediate base from low to high.
3. Resolve conflicts without moving changes between layers unless the stack plan is also updated.
4. Mark the handoff as a caller-owned restack so `/pr-prep` can publish it with force-with-lease after local review.
5. Run `/pr-prep` again for every changed descendant.

The stack is current when every layer records its latest head, intended immediate base, current diff, and current pr-prep result.

## CI Caveat

Check whether PR workflows filter on the base branch. A workflow limited to the delivery base may run for the first layer and skip later layers that target stack branches. Treat a missing expected check as a configuration blocker unless repository policy provides another valid check path.

## Report

Report a table ordered from base to tip with layer purpose, branch, immediate base, PR URL, head SHA, local review, feedback, CI, and readiness. Name every stale descendant and the lower-layer change that invalidated it.
