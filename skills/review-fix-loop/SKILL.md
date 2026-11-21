---
name: review-fix-loop
description: Use when asked to review and fix a branch, PR, or local diff until clean or stopped. Excludes read-only review without fixes (review) and settling already-collected PR feedback or CI failures (review-sweep).
---

# Review Fix Loop

Converge a change through independent reviews and accepted fixes. Start from a
branch, PR head, or local diff with its base, requirements, and verification
evidence. Leave a reviewed snapshot with its coverage summary, any commit status
record, all `Deferred` findings, and any `Stops` for the caller. You are done when
every required angle covers the final snapshot, accepted findings and checks are
settled on it, and no accepted code or substantive-instruction fixes remain — or a
stop is reported with the decision needed.

The change's owner (or invoking runner) drives this loop, delegates independent
read-only assessments through [Orchestration](../orchestration/SKILL.md), settles
findings with [Review Sweep](../review-sweep/SKILL.md), and applies or commits
in-scope repairs between passes. Never let an agent that wrote or directed the
assessed work serve as its independent reviewer.

## Scope and coverage

Resolve the original base once using [Review](../review/SKILL.md). Gather the
snapshot, requirements, and verification evidence with the
[review brief](../review/references/review-brief.md), and establish a stable
`workflow_id` and `pass` counter (starting at 1) under
[Review evidence](../review/references/review-evidence.md).

When reviewing a committed head (such as a branch headed for a PR), every pass
starts with no in-scope uncommitted edits and its snapshot is `HEAD`. Commit any
in-scope repairs before the pass that assesses them. Before each pass, run
`git status --porcelain`; anything it prints must be unrelated local work excluded
and recorded in the brief.

Select initial discovery from the first matching row, honoring explicit user or
caller requests:

| Change | Initial discovery |
| --- | --- |
| Ordinary prose or wording only, with no procedure change | Owner review |
| Substantial, or not clearly contained | Wave 1: Primary, Ponytail, and Thermo. Wave 2: Adversarial |
| Contained and failure-sensitive, or with a plausible material consequence still uncertain | Primary plus the fitting lens, usually Adversarial |
| Remaining contained behavior or agent-procedure change | One independent Primary |

**Failure-sensitive** behavior covers security, data integrity, persistence,
ordering, concurrency, retries, partial failure, migrations, and recovery.

**Contained** work affects one bounded behavior with no substantial trigger.
A change is **substantial**, even with a small diff, when it changes a shared
contract or ownership boundary, introduces interacting behaviors across modules or
authors, introduces or redesigns a multi-step workflow, broadly adds or rewrites
implementation or instructions, or reaches beyond one contained path with
failure-sensitive behavior. Judge changed behavior and consequences, not line or
file count alone.

Record the selection and a one-sentence reason in the brief. Apply
[review assignments](references/review-assignments.md) for criteria, model
mapping, provider references, and failure handling.

**Coverage rule:** Coverage counts for the final snapshot only when an assessment
of it, or proof that still applies to it, supports that angle:
- **Never covered:** a newly required angle assesses the complete current change.
- **Stale:** a repair pass covers changed behavior, affected dependencies, and
  whatever an edit invalidated.
- **Retained:** coverage carries forward where its source, assumptions, and proof
  still apply, with the reason recorded.

When scope expands or changes materially, update the selection, apply this rule,
and run any newly required angles while keeping the original base and diff for
context.

## Initial discovery

Each pass gets a fresh brief, frozen snapshot, and unique report path. Dispatch
each selected read-only assessment through Orchestration, excluding any agent that
wrote or directed the assessed work. Await all required assessments.

Substantial work runs in two waves, using Validate and settle between them:

1. Run Wave 1 (Primary, Ponytail, and Thermo),
   then validate, settle findings, and apply accepted fixes.
2. Run Wave 2 (Adversarial) over the complete settled change as `first discovery`
   — mark the brief `first discovery` so Wave 1 reports are treated as same-round
   peer outputs and Adversarial stays unanchored. If Wave 1 produced repairs,
   verify them under Route repairs (Wave 2 satisfies any Adversarial route).

## Validate and settle

Recheck the snapshot before accepting results. If it moved during review, cancel
obsolete tasks, keep useful observations as unverified claims, and rerun with
refreshed inputs; superseded assessments do not satisfy coverage.

For a matching snapshot, verify outputs under
[Review evidence](../review/references/review-evidence.md). Invalid or missing
required coverage gets a fresh assessment under the
[failure policy](references/review-assignments.md#handle-failures).

Pass every result and partial finding with provenance to
[Review Sweep](../review-sweep/SKILL.md). Carry canonical issue IDs and per-issue
repair/check evidence across passes; reopen a settled finding only with new
evidence, and report stalled disputes rather than repeating equivalent passes.

- **Stops:** settle reversible implementation-design choices yourself; finish
  unaffected work, then return every other stop (including product, scope,
  irreversible, or caller-reserved decisions) to the caller with the decision
  needed. A stop blocks completion.
- **Deferred findings:** when a session or workflow caller owns routing, carry
  every `Defer` item forward (with origin, evidence, reason, and impact) into the
  final report so the caller routes it — surfacing `shared-contract` or
  `requested-scope` impact promptly, and treating an unauthorized split of
  requested scope as a stop. When running standalone directly for the user, give
  each `Defer` item a real durable home (a tracker issue or Snip Snap ID) before
  finishing and report it.

## Route repairs

Before every Pass 2+ repair or dispatch on a committed head, run the
deterministic convergence check against the reviewed workspace and paste its
output block at the top of the pass brief (uncommitted local-diff reviews apply
the same Pass 2+ scoped verification and premise-cut discipline directly):

```sh
python3 <review-fix-loop skill dir>/scripts/convergence.py --repo <workspace> --base <base sha> --pass1 <pass1 sha> --head HEAD [--premise-cut-at <sha>]
```

Act on its mode autonomously (no HITL unless a genuine product/scope decision or
required contract blocker remains):

- **`CONVERGING`:** continue with a tightly scoped repair-verification pass below.
  Pass 2+ reviewers verify accepted fixes, check for regressions, and check
  cumulative repair coherence using the compact `ID | Disposition | 1-line premise`
  table from prior passes — do **not** re-run open-ended Adversarial red-team
  fuzzing across unchanged surfaces (Wave 1 + Wave 2 already did full discovery).
- **`PREMISE_CUT`** (same production file repaired in 2+ consecutive passes, 3+
  total passes, or repair additions >50% of its Pass 1 diff): **additive patching
  on the flagged file(s) is forbidden.** Pause incremental fixes, apply
  [Attack the Premise](../engineering-principles/references/attack-the-premise.md)
  (and run a fresh `Ponytail` simplification pass if the cut isn't obvious) to
  **delete or narrow the offending abstraction** (tighten permissive inputs to
  structured contracts, or fail closed instead of auto-reconciling). Commit the
  simplification and pass `--premise-cut-at <sha>` on the next convergence check.
- **`DEFER_AND_FINISH`** (oscillation persists after a premise cut, or 5+ repair
  commits with repeated hits): stop adding complexity. Fail closed or `Defer`
  remaining non-critical or synthetic edge cases with 1-line factual premises (to
  durable homes), run one final scoped verification check on the settled head, and
  finish. Escalate to the caller/user only if a required contract blocker or
  product/scope decision genuinely cannot be settled autonomously.

Every repair pass uses fresh reviewer tasks under
[Orchestration's review-pass rule](../orchestration/references/reuse-and-recovery.md#reuse-an-agent)
(never resuming a prior reviewer thread), scoped to all changes since the last
completed pass plus affected behavior, consumers, and dependencies, with the
original diff and prior findings' compact disposition table as context. Reviewers
with no routed fix keep their valid coverage.

Choose the route by what changed:

- **Wording, typo, or comment-only polish** (zero behavior or procedure change):
  verify directly without opening a new review pass; prior coverage carries
  forward onto the updated snapshot.
- **Clean disjoint rebase or restack:** when a base update or restack has zero
  conflict edits, identical commit patches (`git range-diff`), no semantic
  overlap with the new base commits, and passing checks, prior review coverage
  carries forward onto the new SHA without a new review pass. Any rebase with
  conflict resolutions, code edits, or interacting base changes routes as a
  repair pass below.
- **Small repair** (one component, no new contract or failure-sensitive behavior)
  **or any Pass 2+ repair:** run **one** independent reviewer — the reviewer whose
  finding was fixed, or Primary when fixing findings from multiple reviewers.
  That reviewer checks the repaired findings, regressions, and cumulative repair
  coherence (with prior dispositions attached) and refreshes that coverage. Add a
  second reviewer only if a repair touches a component no earlier pass reviewed.
- **Large Pass-1 repair** (multiple components, or changing an ownership boundary,
  guarantee, types, or failure-sensitive behavior): run the union of fresh tasks
  for what changed — Primary for correctness/requirements/tests, Ponytail for
  pure simplification/deletion, Thermo for structure/boundaries/types, and
  Adversarial for failure-sensitive contracts. Add an outside perspective only
  for a disputed assumption or material ownership change.

Repeat Validate and settle and Route repairs until no routed fixes or convergence
actions remain.

**Final integrated check:** if code or substantive-instruction repairs ran after
initial discovery, ensure a fresh Primary assessment has checked **all accumulated
repairs since initial discovery and their interactions** on the current snapshot
(reusing a Primary pass only when its assessed scope already covered every repair
with no later repair after it, or when that scope survived wording-polish or
clean-rebase carry-forward). Process its results through Validate and settle.

## Finish

Finish when required coverage holds on the actual final snapshot, accepted
findings and checks are settled on it, and no accepted code or
substantive-instruction fixes remain. Missing required coverage, open accepted
findings, and unresolved stops block completion.

When reviewing a committed head, build and return the exact `review-fix-loop`
commit status command for the final covered SHA (including a clean disjoint rebase
or wording-polish SHA carrying forward its coverage), with a description of at most
140 characters:

```sh
gh api repos/<owner>/<repo>/statuses/<reviewed sha> -f state=success \
  -f context=review-fix-loop -f description="<workflow_id>: <N> passes"
```

Hand this command unchanged to the publishing workflow (which runs it once that SHA
is on the remote and its preparation checks cover the change). Do not post a PR
merge-gate status from a standalone review run unless the caller explicitly asked
to stamp it and confirmed preparation checks cover the final SHA. When posting
fails (missing permission, fork), report it as a blocker; another review run will
not fix it. A local-diff review with no PR planned finishes with its snapshot
evidence.

In the handoff to the caller, report:
- reviewed base and final snapshot/SHA (plus any carried-forward rebase or polish note)
- child tasks mapped to workflow/pass, assignment, criteria, configured model,
  and which prior reviewer each follow-up followed
- findings and dispositions, coverage gaps, and provider references used or
  unavailable
- all **`Deferred`** findings (origin, evidence, reason, impact) for the caller to route
- any **`Stops`** with the decision each needs
