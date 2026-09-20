---
name: review-fix-loop
description: Review a branch, PR, or local diff; fix accepted findings and verify before handoff or push. Use when the user asks to review project changes and before handing off code changes that affect behavior or docs that change agent behavior.
---

# Review Fix Loop

The parent owns scope, dispatch, triage, fixes, and verification. Leave commits,
pushes, PR replies, and merges to the caller.

## Scope and review path

Resolve the supplied base once; use the merge-base for branch comparisons.
Otherwise use the established parent branch or repo setting; ask if ambiguous.
Stop on an invalid base or empty scope.

Default scope: `git diff <resolved-base> --` plus contents from
`git ls-files --others --exclude-standard`. This includes committed, staged,
unstaged, and untracked work. Honor a narrower scope when requested.
Gather requirements from the user, issues, or spec; repo standards; and checks.
Record the base, head, diff, and untracked contents for each round. Every
reviewer reads that complete scope in every round, including the integrated
work of all authors. Keep the original base when fixes change the diff.

Prepare a complete [review brief](references/review-brief.md) for each independent
reviewer. All reviewers get the same requirements and accepted scope changes,
base/head, full diff and untracked contents, standards, and test evidence.
Supply complete contents inline or through absolute paths; summaries do not
replace them. Keep any brief files and diff snapshots outside the reviewed diff.
Pause edits until all independent reviewers return.
Allow inspection of nearby code. Exclude earlier reviewer verdicts and the
author's defense from the brief and inherited context.

Use focused parent review for ordinary docs and wording-only instruction edits.
When docs change agent behavior, use one independent reviewer as described below.
Use the code loop for code or mixed changes, including executable skill scripts.
Judge the changed content, not its extension. Honor an explicit request for
additional reviewers or rounds.

## Required Gemini review

Send every nonempty review scope to Gemini through [Gemini](../gemini/SKILL.md),
using its [review packet flow](../gemini/references/review.md). This applies to
all paths below. Gemini joins the parent or native reviewers; it does not replace
them or count toward the code path's limit of two native reviewers.

Give Gemini the same complete brief and review references, with contents in the
packet rather than paths alone. Start a fresh Gemini conversation each round.
Include its findings in parent triage or `/review-sweep`, keeping Gemini as the
source. A round is complete only when Gemini and all required native reviewers
finish with full coverage. A failed, denied, or incomplete Gemini run is a blocker;
never silently omit it or count it as clean. Follow the Gemini flow's bounded
recovery rules and report any unresolved gap.

The paths below govern repeats: code fixes start a fresh round for all reviewers;
substantive instruction fixes do too. Ordinary docs and wording-only instruction
fixes need targeted verification after the initial Gemini review.

## Focused review: ordinary docs

The parent reviews the whole scope once against the requirements and repo rules.
Check facts, conflicting instructions, missing requirements, and broken references.
Treat style preferences as optional; enforce explicit writing requirements.

Triage findings and apply accepted fixes, then check the revised text and relevant
links, examples, and skill structure. Resolve remaining substantive issues and
recheck the affected sections. Finish when accepted fixes are complete and relevant
checks pass, or report concrete blockers and unfinished work.

This path ends with targeted verification; edits do not start another full review
or dispatch the code reviewers below. Report the result using the shared handoff.

## Docs that change agent behavior

Use one fresh, independent native review agent plus Gemini for changes to skill procedures, global
instructions, or agent configuration. Set `fork_turns: "none"` explicitly. Follow
[agent routing](../orchestration/references/agent-routing.md) for role selection and
settings each round.

Add realistic sample requests to the brief. Ask the reviewer to trace their effects,
check conflicts and missing requirements, and report findings with evidence,
coverage, and gaps. Keep it read-only and independent of earlier conclusions.

The parent triages findings, fixes accepted issues, and checks relevant links,
examples, syntax, and skill structure. After substantive fixes, restart with a fresh
native reviewer and Gemini on the whole updated change against the original base. Wording-only
fixes need targeted checks. Finish after a complete clean review and passing
checks; report missing coverage or an unavailable reviewer as a blocker.

## Code review loop

1. **Review.** Choose one reviewer for a small, clear change to one behavior.
   Use two for substantial changes, multiple behaviors, shared contracts, risky
   logic, or work from several agents. Keep at most two unless the user explicitly
   requests more.
   Reassess the choice when fixes change the scope.

   Follow [agent routing](../orchestration/references/agent-routing.md) for reviewer
   selection and settings each round.
   Launch fresh agents each round, in parallel when using two, within available
   slots. Set `fork_turns: "none"` explicitly for every reviewer; a new agent
   with inherited history is not a fresh-context review. Do not resume a prior
   reviewer for a new round.

   Cover these checks in every round:

   - **Correctness:** bugs, regressions, edge cases, security, data loss, and
     test gaps; use [Spec](references/spec.md) to trace requirements from the
     user request or supplied spec.
   - **Code quality:** [Ponytail](references/ponytail.md) for cuts and reuse,
     [Thermo](references/thermo.md) for structure and boundaries, and
     [Standards](references/standards.md) for repo rules.

   When the scope includes React or Next code, include
   [react-best-practices](../react-best-practices/SKILL.md) in every reviewer's
   references. Reviewers follow its How to Use against the diff. For Gemini, the
   parent follows that How to Use against the diff and puts the skill file and
   those matching rule files in the packet.

   One reviewer covers both sets. With two, assign one set to each for emphasis;
   both still read every changed hunk and new file, trace nearby effects, and
   may report issues outside their emphasis. Keep Spec, Standards, and
   react-best-practices findings labeled separately even when one reviewer
   supplies them.

   Name the change's main risks in the briefs, such as access control, concurrent
   updates, or data migration. These guide the existing reviewers' checks; they
   do not add another reviewer automatically.

   Include the references for each reviewer's assigned emphasis in its brief.
   Require findings with locations, evidence, impact, and proposed remedies,
   plus coverage and gaps. Leave edits, further delegation, and acceptance to
   the parent. A complete review may find
   no issues. Require a concrete benefit for structural changes; preferences
   alone do not require a fix or another round.

   If the code changes during review, refresh the whole scope and restart the
   round. Missing coverage or an unavailable reviewer
   is a blocker, not a clean review. Beyond required Gemini review, include extra reviews only when the user
   explicitly requests them, and include their findings in the sweep.

2. **Sweep.** Run `/review-sweep` in the parent. Keep each finding’s source,
   including Standards versus Spec versus react-best-practices. Finish when every
   finding has a disposition and every accepted fix is complete or blocked.
   Preserve intended behavior and contracts within the user’s authorized scope.

3. **Verify.** Run planned and fix-specific checks. When the scope includes
   React or Next code, run
   `npx react-doctor@latest --verbose --scope changed --base <resolved-base> --include-untracked`
   and put the report in test evidence. A dropped score is a failed check.
   Use judgment to decide whether `/manual-verify` would add useful confidence,
   based on the changed behavior, risk, and existing test coverage. Invoke it
   when needed, even if review found no fixes. Fix failures and rerun affected
   checks; reassess manual verification after fixes. Keep evidence only while it
   still applies to the current code. Report any verification you consider
   necessary but cannot run as a concrete blocker.

4. **Finish or repeat.** A complete clean round with passing checks can finish,
   including the first round. After any accepted fix or verification fix, refresh
   the full diff and untracked contents and return to step 1 against the original base.
   Small fixes count too; every round reviews the whole current change, not
   just fixes or earlier findings. Reopen rejected or deferred findings only
   with new evidence.

   Finish only when the last round makes no fixes, needs no further accepted
   fixes, has complete coverage, and passes relevant
   checks, including any manual verification judged necessary. Continue after
   fixes until that condition holds. If review stops making progress, diagnose
   the repeated issue, use a stronger reviewer when needed, or report the
   concrete blocker. An incomplete round never counts as clean.

## Handoff

Report scope, review path, round count, reviewer roles and requested settings,
Gemini status and coverage, fixes, deferrals, blockers, checks, any manual verification evidence,
and remaining risks. Distinguish confirmed settings from unverified requests.
