---
name: review-fix-loop
description: Review a branch, PR, or local diff; fix accepted findings and verify before handoff or push.
---

# Review Fix Loop

The parent owns scope, dispatch, triage, fixes, and verification. Leave commits,
pushes, PR replies, and merges to the caller.

1. **Scope.** Resolve the supplied base once; use the merge-base for branch
   comparisons. Otherwise use the established parent branch or repo setting;
   ask if ambiguous. Stop on an invalid base or empty scope.

   Default scope: `git diff <resolved-base> --` plus contents from
   `git ls-files --others --exclude-standard`. This includes committed, staged,
   unstaged, and untracked work. Honor a narrower scope when requested.
   Gather requirements from the user, issues, or spec; repo standards; and checks.
   Record the base, head, diff, and untracked contents for this pass.

2. **Review.** Launch a fresh, read-only subagent per brief, in parallel within
   available slots; batch the rest:

   - [Ponytail](references/ponytail.md): cuts and reuse.
   - [Thermo](references/thermo.md): structural quality, every pass.
   - [Standards](references/standards.md): repo rules and code smells.
   - [Spec](references/spec.md): requirements; skip explicitly if none exist.

   Pass each agent the same scope, requirements, standards, its brief’s absolute
   path, and this contract:

   > Read the whole supplied scope and enough surrounding code to judge it.
   > Report findings with locations, evidence, impact, and proposed remedies,
   > plus coverage and gaps. Leave edits and further delegation to the parent.

   Keep reviewers independent of earlier conclusions or the author’s defense.
   Pause edits until all return. If the code changes during review, refresh the
   scope and rerun affected reviews. Report unavailable subagents as a blocker.

   Run `/gemini` directly for a read-only review on every pass, when available.
   Pass the resolved base, complete file scope, requirements, and standards.
   Confirm its reported scope matches; report missing coverage as a blocker.

   Continue only when every applicable source has a report or explicit blocker.
   Missing coverage or a failed reviewer is not a clean review.

3. **Sweep.** Run `/review-sweep` in the parent. Keep each finding’s source,
   including Standards versus Spec. Finish when every finding has a disposition
   and every accepted fix is complete or blocked. Preserve intended behavior
   and contracts within the user’s authorized scope.

4. **Verify.** Run planned and fix-specific checks. Use judgment to decide
   whether `/manual-verify` would add useful confidence, based on the changed
   behavior, risk, and existing test coverage. Invoke it when needed, even if
   review found no fixes. Fix failures and rerun affected checks; reassess manual
   verification after fixes. Keep evidence only while it still applies to the
   current code. Report any verification you consider necessary but cannot run
   as a concrete blocker.

5. **Repeat.** If this pass made any fixes during sweep or verification, refresh
   the diff and untracked contents and return to step 2 against the same base.
   Small fixes count too. Reopen rejected or deferred findings only with new
   evidence. Finish cleanly only after a full pass makes no fixes, needs no
   further accepted fixes, and has complete review coverage and passing checks,
   including any manual verification judged necessary. If a blocker prevents that,
   report it and any unfinished work; a blocked pass is not a clean result.

Report scope, reviews run or skipped, fixes, deferrals, blockers, checks,
any manual verification evidence, and remaining risks.
