# Provisional work

Work is **provisional** when it rests on something you do not control: another owner's unmerged
branch or PR, or a recorded assumption awaiting an open decision. Your own planned stack layers are
not provisional.

## Rules

- Name the exact branch, PR, or open decision and assumption the work rests on, and what clears it.
- Provisional work may build, prove, and be shown, and is reviewed only when a PR state or review
  was requested.
- **Never merge provisional work**, and never take destructive or outward-facing actions on its own
  initiative.
- **Land becomes Try** while the provisional condition holds. A requested `draft` or `review-ready`
  PR state can still be reached via [PR](../../pr/SKILL.md), with the **Provisional** section from
  [PR body](../../pr/references/pr-body.md) kept in the PR body until the condition clears and
  affected proof is refreshed (Merge stops on that section).

## When the base or decision changes

- **Base changed:** restack onto the new base and rerun affected proof.
- **Base landed, or decision answered as assumed:** restack if needed, refresh affected proof, then
  remove the PR body's `## Provisional` section. The original finish line returns.
- **Decision answered another way:** rebuild on the answer, or offer the work for scrap.
- **Base scrapped:** stop work on the scrapped base and offer this outcome its own scrap or rebase
  choice. An explicit user scrap of this outcome authorizes only its scoped cleanup through
  [Repo Cleanup](../../repo-cleanup/SKILL.md) (branch, PR, worktree); downstream dependents still
  get their own choice.
