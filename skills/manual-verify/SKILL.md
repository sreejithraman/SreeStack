---
name: manual-verify
description: Verify changes through real user workflows when hands-on testing would add confidence, including web apps in a browser and iOS apps in Simulator.
---

# Manual Verify

Exercise the product through the interface its users operate. Judge whether the
workflow works and remains usable; a successful command or build is supporting
evidence, not the verdict.

## Workflow

1. **Choose workflows.** Read the request and changes. Identify the affected
   users, their goal, and nearby behavior the change could break. Select the
   smallest useful set of realistic workflows covering the main path and any
   material error or edge case. State the expected result of each workflow.

2. **Choose the interface.** Use the product surface its users use. For a web
   app, read [web verification](references/web.md). For an iOS app, read
   [iOS verification](references/ios.md). Use the same observe-act-observe loop
   for other interactive products with the best available interface tooling.

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

   If an interaction appears to fail because the interface moved or was still
   loading, recapture its state and retry once. Treat a repeated failure as
   evidence instead of retrying until it disappears.

   When the reported behavior is intermittent, choose a bounded attempt count
   before testing, repeat the same controlled workflow, and record every outcome.
   Report `reproduced` or `not reproduced in N attempts`; do not turn one
   successful attempt into a pass for the intermittent report.

4. **Judge the result.** Compare the observed result with the workflow's expected
   result. Check function and usability, including relevant layout, readability,
   focus, input, navigation, loading, empty, disabled, and error states. Distinguish:

   - functional failures, such as the wrong destination or an unresponsive action;
   - visual failures, such as clipped, overlapping, unreadable, or misplaced content;
   - crashes and unexpected exits;
   - transient states that settle correctly; and
   - expected states, such as a disabled submit action for incomplete input.

5. **Report evidence.** For each workflow, state what was exercised, the expected
   result, the observed result, and its status: `passed`, `failed` or `reproduced`,
   `not reproduced in N attempts`, or `blocked` or `untested`. A result that was
   not reproduced is not a pass. Include screenshots, logs, or semantic snapshots
   when they explain the conclusion. Name any untested behavior or environmental
   gap rather than treating it as passing.

If login or another step requires the user, tell them exactly what to do and
where, then resume after they finish. Continue independent checks meanwhile.

After UI work, use `showroom` to package useful visual checkpoints. Keep workflow
selection and the pass or fail judgment in this skill.
