---
name: ponytail-review
description: Use when the user asks to simplify a repo or PR/diff, review it for lazy or over-engineered code, find bloat or boilerplate, cut needless dependencies, or identify what can be deleted.
license: MIT
---

# Ponytail Review

Lazy means rigorous about understanding and ruthless about excess. Read the full flow first, then seek the least code that preserves required behavior. Ponytail review reports proven cuts and leaves fixes to its caller.

## Steps

1. Fix the scope.

   Use `repo` mode when the user asks for a whole-codebase review. Use `diff` mode for a PR, branch, commit range, staged changes, or working tree.

   In diff mode, resolve the exact base and head or the exact local diff. For a PR, use its refs when available and otherwise inspect the PR diff while stating any limit on nearby code. In repo mode, list every top-level first-party source area and dependency manifest that the review must cover.

   Finish when the reviewed command or file set is exact and non-empty, or report the empty scope as a blocker.

2. Read enough context to prove cuts.

   Read the rules that govern the target, its dependency manifests, and the code around each candidate. Trace the real flow end to end. Search the repo for existing helpers, types, patterns, callers, and uses before claiming that code is redundant. Lazy review reduces code only after it understands the whole flow.

   In diff mode, account for every changed hunk and the nearby flow needed to judge it. In repo mode, account for every source area and manifest from step 1 as inspected or blocked.

   Finish when every part of the scope has a coverage state and each candidate cut has supporting code evidence.

3. Run the ponytail ladder.

   Stop at the first choice that preserves required behavior and public contracts:

   1. `delete` — current behavior or the supplied spec does not need it.
   2. `repo reuse` — the repo already provides it.
   3. `stdlib` — the language standard library provides it.
   4. `native` — the platform provides it.
   5. `dependency reuse` — an installed dependency already provides it.
   6. `inline` — an interface, factory, wrapper, setting, or helper has one real use and adds no useful boundary.
   7. `shrink` — the minimum direct form keeps the behavior with fewer concepts or lines.

   Apply these lazy rules:

   - Remove speculative abstractions, settings, flags, and scaffolding for later needs.
   - Prefer deletion to addition and direct code to clever code.
   - Prefer the fewest concepts and files after finding the right ownership point.
   - Prefer one root-cause fix in the shared path to repeated symptom patches at callers.
   - When two small choices fit, choose the one that handles edge cases correctly.
   - Accept a simple choice with a known ceiling only when the limit and upgrade point are clear.

   Apply these safety limits:

   - Preserve every explicit requirement and public contract.
   - Treat trust-boundary validation, data-loss prevention, security, and accessibility as required behavior.
   - Retain hardware calibration and settings that account for real physical variance.
   - Keep tests, assertions, and checks that protect real behavior; judge their size against the risk they cover.
   - Reject a cut that depends on an unproven behavior change.

   Send correctness, security, and speed concerns to the normal review sources unless removing excess code also resolves them.

   Finish when every candidate has a proven ladder result or an explicit reason for rejection, and every result passes the lazy rules and safety limits.

4. Rank and report.

   Rank findings by concepts removed, then dependencies, files, and lines. Use one item per independent cut:

   ```text
   <tag> <path>:L<start>-L<end> — Cut: <code or concept>. Replace: <exact replacement>. Proof: <repo evidence>. Estimate: <range of lines and exact dependency count, or unknown>.
   ```

   End with the review mode, exact scope, coverage, total estimated cut, and context limits. Use ranges when line counts are uncertain. If no cut survives proof, report `Lean already. No cuts found.`

   Finish when every reported finding has a location, exact replacement, proof, estimate, and rank, and the report accounts for the full scope.
