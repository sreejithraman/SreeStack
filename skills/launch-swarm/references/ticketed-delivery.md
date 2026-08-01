# Ticketed Delivery

Read this reference fully when Launch Swarm receives a spec issue with child build tickets or a named subset of those tickets.

## Resolve The Spec Root

Use the issue tracker configured for the repository. Read the full spec body and comments, then discover its child tickets through the tracker's native parent relation or configured local convention.

Load every child ticket before choosing work. Record its title, body, state, acceptance criteria, blocking edges, and current assignee or owner. When the user names a subset, keep the other children as graph context and mark only the named tickets in scope.

Validate that:

- every in-scope ticket belongs to the spec
- every ticket states what to build and how to accept it
- every blocking edge resolves within the graph or to completed outside work
- the graph is acyclic
- current ticket state and ownership are known

The published spec and tickets are fixed input. When either artifact is missing, stop with the exact `/to-spec` or `/to-tickets` action the user must run. Launch Swarm consumes those user-invoked skills' output; it does not replace their planning work.

Resolution is complete when the spec root, full child graph, in-scope set, and current frontier are explicit.

## Work The Frontier

The frontier contains each pending, unclaimed in-scope ticket whose blockers have either landed on the target base or sit in a stable lower delivery unit that can serve as its base.

Give each agent-owned shard one ticket, the spec, its acceptance criteria, and only the blocker context it needs. Independent frontier tickets may run in parallel. A blocked ticket waits until its last blocker reaches a usable base.

Claim each selected ticket through the configured tracker before work starts. Skip work another owner has already claimed unless the user has made that shared ownership explicit.

After each delivery round, update the delivery record below. Re-read the tracker because another session may have completed, claimed, changed, or blocked a ticket. When a new frontier exists, work it next. When pending tickets remain without a frontier, report the blocking tickets and owners.

## Form PRs Progressively

Load the whole ticket graph up front, but make only current PRs concrete. Keep unbuilt work as tickets until a reviewable boundary becomes clear.

Choose the boundary that matches the current code:

- **Same PR**: changes share one review purpose, or separating them would break the build, tests, public contract, or user behavior.
- **Independent PR**: the change is safe against the target base and has no code dependency on another open PR.
- **Dependent PR**: the change needs code in another open PR, while both diffs remain coherent and the lower PR is safe to merge first. Apply `stacked-prs.md`.

A current PR is ready to form when its tickets meet their acceptance criteria, its diff has one reviewer-facing purpose, its immediate base is known, and every owned change belongs to that PR once.

Tickets define build work. PRs define review and merge units. Map them one-to-one only when both shapes match.

## Keep The Delivery Record

Record one row per in-scope ticket:

```text
Ticket:
Ticket state: pending, building, implemented, landed, or blocked
Blocked by:
Delivery unit:
Branch and immediate base:
PR URL and head SHA:
Review state:
Acceptance evidence:
```

Link each PR to its spec and included tickets. Follow the repository's issue-closing rule. In ready mode, keep unmerged work distinct from landed work.

Ticketed delivery is complete when every in-scope ticket has a current ready PR, has landed, or has a blocker with an owner and required action, and the delivery record matches the current tracker and GitHub state.
