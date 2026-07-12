---
name: github-review-sweep
metadata:
  owner: sree
description: GitHub review sweep. Use when PR review comments need review-sweep fixes, replies, and thread resolution.
argument-hint: "<PR number, branch, or review request>"
---

# GitHub Review Sweep

GitHub review sweep applies `/review-sweep` to PR review feedback, then posts replies and resolves threads on GitHub.

Prefer the GitHub connector for PR metadata and comments. Use `gh` only for connector gaps, thread state, resolution status, or inline context required by this workflow.

## Steps

1. Fetch GitHub review comments.

   Resolve the PR and collect unresolved inline threads, review-level comments, requested-changes summaries, and enough diff context to understand each comment.

2. Run `/review-sweep`.

   Convert each GitHub item into a finding with `source`, `id`, `location`, and `claim`. Let `/review-sweep` verify, classify, and fix accepted findings.

3. Verify changed work.

   If `/review-sweep` changed the diff, run focused verification before replying.

4. Reply and resolve comments.

   Post concise replies with each finding's disposition. Resolve threads when the finding was fixed, rejected with a reason, blocked with evidence, source noise, duplicate, or intentionally deferred to the parent.

5. Return

   Report changed files, verification results, posted replies, resolved threads, open threads, and deferred decisions.
