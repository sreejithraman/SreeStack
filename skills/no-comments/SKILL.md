---
name: no-comments
description: Audit and remove redundant code comments, fix the code they excuse, and encode enforceable constraints.
disable-model-invocation: true
---

# No comments

Prefer code that explains itself. Use an independent audit to find removable
comments and the code changes needed to make their explanations unnecessary.

## Scope and audit

Use the caller's files or diff. Otherwise resolve the base using
[Review](../review/SKILL.md) and inspect the current diff, including working-tree
changes and nonignored untracked files. Keep edits inside that scope.

Delegate a fresh, read-only audit through
[Orchestration](../orchestration/SKILL.md), using its primary review selection.
Supply the scope, base, relevant project rules, and
[comment audit](references/comment-audit.md). The auditor proposes deletions
and exact refactor targets; the parent owns edits. If independent auditing is
unavailable, report that gap instead of claiming this workflow completed.

## Settle and fix

Inspect each finding against nearby code and the audit's exceptions. Reject
scope escapes, unsupported claims, and deletions of protected comments. For
unclear claims, inspect the live call path; use [Code Why](../code-why/SKILL.md)
when history would establish the reason. Keep unresolved constraints and report
the missing evidence. Give a materially incomplete or invalid audit one fresh
rerun with the failure named; a second invalid audit leaves the workflow open.

Delete accepted narration, banners, and commented-out code. Fix accepted
refactor targets with the smallest root-cause change: rename, extract, improve
a type, remove a dead path or parameter, or use the supported API. When a fix
needs a design decision, use [Codebase Design](../codebase-design/SKILL.md) for
the affected boundary before implementing. Preserve intentional behavior.

For suppressions, fix the underlying problem before removing the directive.
If the repair exceeds scope, keep the directive and report the exact blocker.
For an enforceable constraint, implement the cheapest fitting type, runtime
check, test, or existing CI lint within the authorized scope. Prove that it
catches a violation before deleting the comment. Keep the comment if enforcement
is unavailable or outside scope; describe the remaining work. Required
external/platform explanations and public API contracts remain useful prose.

## Verify and report

Run affected build, type, lint, or behavior checks for code and directive
changes. Inspect the final diff for lost constraints and scope escapes. Use
[Review Fix Loop](../review-fix-loop/SKILL.md) for behavior changes; plain
comment deletions need a focused diff check.

Report comments deleted and retained with reasons, refactors, constraint
encodings and their proof, audit reruns, checks, and unresolved work. Treat
missing required fixes or proof as incomplete.
