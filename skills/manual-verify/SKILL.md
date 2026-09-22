---
name: manual-verify
description: Exercise and assess real user workflows when hands-on acceptance testing or an evidence-based interface audit would add confidence, including web apps in a browser and native iOS or macOS apps.
---

# Manual Verify

Exercise the product through the interface its users operate. Judge whether the
workflow works and remains usable; a successful command or build is supporting
evidence, not the verdict.

## Workflow

1. **Choose workflows.** Read the request and changes. Identify the affected
   users, their goal, and nearby behavior the change could break.

   Treat verification of a changed workflow or behavior as acceptance work.
   Treat a whole-surface visual, interaction-quality, or accessibility judgment
   as an interface audit. If the request includes both, apply each completeness
   rule to its own scope.

   For acceptance verification, select the smallest useful set of realistic
   workflows covering the main path and any material error or edge case. State
   the expected result of each workflow.

   For an interface audit, first inventory every in-scope surface, component,
   state, input method, and accessibility path. Load `refactoring-ui` for visual
   systems and `animate` for motion. For implementation criteria, load
   `frontend-web-design` on web and `swiftui` or `uikit` for the framework in a
   native Apple project. If no matching specialist exists, use the project's
   platform guidance and the observe-act-observe workflow below. Turn every
   applicable criterion from that inventory into an assertion; do not sample the
   audit down to a representative subset.

2. **Choose the interface.** Use the product surface its users use. For a web
   app, read [web verification](references/web.md). For an iOS app, read
   [iOS verification](references/ios.md). For a native Mac app, read
   [macOS verification](references/macos.md). Use the same observe-act-observe
   loop for other interactive products with the best available interface tooling.

3. **Observe, act, observe.** Start from a known state and wait for the interface
   to settle. Identify the environment and external effects before exercising a
   consequential workflow. Use disposable accounts, fixtures, and provider test
   modes when available. Complete an irreversible or externally visible action
   only when the task authorizes it; otherwise stop at the last safe step and
   report the remaining gap.

   Inspect both the rendered appearance and semantic representation when
   available. Perform one meaningful interaction, then inspect the resulting
   state before continuing. Prefer semantic targets such as roles, labels, and
   identifiers; use coordinates only when the interface exposes no stable target.

   If an interaction produces no expected change, record that outcome before any
   retry. Retry once only when observable evidence shows that the target moved or
   the interface had not settled, and count the retry as a separate attempt.
   Treat a repeated failure as evidence instead of retrying until it disappears.

   When the reported behavior is intermittent, choose a bounded attempt count
   before testing. Restore an equivalent known state with disposable or uniquely
   identified data before every planned attempt so earlier outcomes cannot affect
   later ones. Record every outcome. Recovery retries are separate from the
   planned attempt count and must be recorded separately. Report `reproduced` or
   `not reproduced in N attempts`; do not turn one successful attempt into a pass
   for the intermittent report.

4. **Judge the result.** Compare the observed result with the workflow's expected
   result. Check function and usability, including relevant layout, readability,
   focus, input, navigation, loading, empty, disabled, and error states. Distinguish:

   - functional failures, such as the wrong destination or an unresponsive action;
   - visual failures, such as clipped, overlapping, unreadable, or misplaced content;
   - crashes and unexpected exits;
   - transient states that settle correctly; and
   - expected states, such as a disabled submit action for incomplete input.

   When the expected result includes persisted data or an output artifact, verify
   it through a fresh read path rather than relying on the current screen alone.

   When accessibility is in scope, check names, roles, values, states, label and
   error relationships, task-ordered focus, keyboard traps, text scaling, and
   whether visible async status is announced when focus does not move.
   When materials are affected, check increased contrast and reduced transparency
   where the platform exposes them.

5. **Report evidence.** For each workflow, state what was exercised and the
   expected and observed result. Give each required acceptance assertion a status:

   - `passed` when the observed result matched the expected assertion;
   - `failed` when the observed result differed from the expected assertion;
   - `blocked` when a missing prerequisite prevented the check; or
   - `untested` when the selected check was not exercised.

   Report defect reproduction separately as `reproduced` or
   `not reproduced in N attempts`. A reproduced defect makes its affected
   assertion and the overall workflow `failed`. When the defect is not reproduced,
   report that outcome beside the acceptance status and state that it does not
   establish that the defect is fixed.

   A workflow passes when every required assertion passed. Otherwise report every
   non-passing assertion and use `failed` when any assertion failed, then
   `blocked`, then `untested` as the overall status. Include screenshots, logs, or
   semantic snapshots when they explain the conclusion. Name any untested
   behavior or environmental gap rather than treating it as passing.

   For an interface review, report each issue with its location, observed
   behavior, exact change, and reason, then rank the findings by user impact.

   An interface audit is complete only when every inventoried item and applicable
   specialist criterion is `passed`, `failed`, `blocked`, or explicitly
   `untested`. The audit passes only when all required assertions pass.

If login or another step requires the user, tell them exactly what to do and
where, then resume after they finish. Continue independent checks meanwhile.

After UI work, use `showroom` to package useful visual checkpoints. Keep workflow
selection and the pass or fail judgment in this skill.
