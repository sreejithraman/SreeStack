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
   normal orchestration brief, rank, context, and concurrency rules. Group
   tightly coupled tickets under one owner. Parallel workers use separate
   worktrees and task-owned branches based on the integration tip; preserve
   unexpected existing edits and create a fresh workspace rather than resetting
   someone else's work.

3. Workers implement against the spec and applicable `tdd` seams, returning the
   ticket, base/head revisions, changed paths, verification, and unresolved work.
   Link durable spec, ticket, research, and commit artifacts instead of repeating
   them in status messages. Temporary research notes must remain accessible to
   subsequent workers while needed.

4. The integrating owner serializes merges onto the integration branch. Compare
   each result with the current integration tip; resolve stale bases or conflicts
   without losing another worker's changes. Verify the integrated behavior and
   any shared boundaries affected by the merge. A worker merging a prior
   integration tip does not guarantee a fast-forward after concurrent progress.

5. Recompute the frontier after accepting each integration. Mark a dependency
   satisfied only when its required outcome is integrated and verified; keep
   blocked or partial work visible. Continue ready work within the configured
   limit until every ticket's required outcome is accounted for.

6. Review the complete integrated change through `review-fix-loop`, or let
   `pr-prep` own that review when it will publish the same scope. If the user
   requested a PR or the tracker workflow requires one, open a draft once there
   is a reviewable commit and use `pr-prep` for readiness. Leave final issue
   completion to the applicable tracker/merge workflow; integrated work alone
   does not establish that a required PR is merged.

7. Use `repo-cleanup` for disposable task-owned worktrees and artifacts once no
   unmerged work or active dependent task needs them. Return the integration
   branch, ticket dispositions, verification, and any PR or remaining blockers.

Scheduling a spec does not create an agent goal. Use `goal-swarm` only when the
user explicitly requests goal-backed work.
