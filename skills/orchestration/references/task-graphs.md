# Implementing a task graph

Use when a spec has tickets with explicit blocking relationships. The finish
line is the spec implemented and verified on one integration branch, with each
ticket accounted for through the project's tracker workflow.

1. Read the spec, ticket bodies, dependencies, and project tracker convention.
   Identify completed work, blocked tickets, and the **frontier**: unfinished
   tickets whose dependencies are satisfied. Detect cycles and missing blockers
   before dispatch. Use supplied tracker information; resolve a missing required
   choice with the user rather than imposing a setup workflow.

2. Reuse or create a task-owned integration branch from the intended base.
   Record its tip. Assign independent frontier tickets to workers using the
   normal orchestration brief, model policy, context, and concurrency rules.
   Group tightly coupled tickets under one owner. Delegated children share the
   integration checkout: give parallel workers disjoint paths and serialize
   shared files, commits, and other git/index changes. Preserve unexpected edits.
   When isolation is necessary, keep the work serial unless the user explicitly
   requests separate ordinary threads. For those threads, follow agent routing's
   workspace rules and bind task-owned worktrees from the integration tip before
   execution; do not pretend they are delegated children.

3. Workers implement against the spec and applicable `tdd` seams. Shared-checkout
   children return the ticket, starting/current shared HEAD, changed paths and
   patch or content evidence, checks and the state they tested, and unresolved
   work. Their HEAD may be unchanged despite working-tree edits; do not require
   a child commit. Explicit separate-thread workers also return their branch's
   base/head revisions. Link durable spec, ticket, research, and commit artifacts
   instead of repeating them in status messages. Temporary research notes must
   remain accessible to subsequent workers while needed.

4. The integrating owner accepts shared-checkout changes and serializes any
   commits or merges onto the integration branch. Compare each result with the
   current integration state; resolve stale bases or conflicts without losing
   another worker's changes. Verify integrated behavior and shared boundaries.
   Only separate-thread branches need merging; a worker incorporating a prior
   integration tip does not guarantee a fast-forward after concurrent progress.

5. Recompute the frontier after accepting each integration. Mark a dependency
   satisfied only when its required outcome is integrated and verified; keep
   blocked or partial work visible. Continue ready work within the configured
   limit until every ticket's required outcome is accounted for.

6. Review the complete integrated change through `review-fix-loop`, or let
   `pr` own that review when it will publish the same scope. If the user
   requested a PR or the tracker workflow requires one, open a draft once there
   is a reviewable commit and use `pr` for readiness. Leave final issue
   completion to the applicable tracker/merge workflow; integrated work alone
   does not establish that a required PR is merged.

7. Use `repo-cleanup` for disposable task-owned worktrees and artifacts once no
   unmerged work or active dependent task needs them. Return the integration
   branch, ticket dispositions, verification, and any PR or remaining blockers.

Scheduling a spec does not create an agent goal. Use `goal-swarm` only when the
user explicitly requests goal-backed work.
