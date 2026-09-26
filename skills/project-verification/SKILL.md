---
name: project-verification
description: Create or refresh a project-local skill that can launch, drive, and verify a real UI, CLI, or service. Use when a repository needs a reusable verification path for future agents; use manual-verify for a one-time acceptance check.
---

# Project Verification

Build a verification guide another agent can use without this conversation. It should run the product through a real user entry point and leave observable proof. Keep the guide in the target project, using a skill directory its agent host discovers.

## Discover the control surface

Read the project's run instructions, commands or routes, existing tests, and relevant environment setup. Identify:

- the user-facing workflows worth checking and the primary surface to drive;
- the exact launch command and a reliable readiness check;
- an existing browser, device, PTY, HTTP, or test harness that can exercise the surface;
- the observable result and any persisted or external side effect;
- the data, account, port, profile, or device needed to isolate this run from a user's session.

Reuse an existing harness when it can drive the real workflow. Ask only for an unavailable prerequisite that cannot be inferred from the repository. If the product cannot start, record the failing command and cause; do not describe an unrun recipe as verified.

Before any live drive, identify consequential actions and use disposable data and provider test modes where available. If the only path would make an unauthorized external or irreversible change, stop at the last safe step, document the needed test prerequisite, and mark that workflow unverified.

Record required credential names and the project's secure setup path, never credential values. Use non-sensitive test data and redact logs, screenshots, and output before retaining evidence. If the needed proof cannot be captured safely, report that limit instead of saving sensitive material.

## Write the project guide

Find an existing project verification skill before creating another. Update its inaccurate instructions in place. Otherwise create one in the project's established skill directory and confirm its frontmatter and path make it discoverable in the target host.

The guide needs concrete instructions for:

1. **Launch and stop.** Start the exact build or app under test, identify readiness, and stop only the process or session this run created.
2. **Health check.** Read-only checks for the correct instance, version, connection, and required access. Run this before driving and after a surprising failure.
3. **Drive.** User-level selectors or commands that reach a workflow from a known state. Use stable labels, IDs, routes, or prompt text before coordinates.
4. **Evidence.** Capture the action and resulting state, including a fresh read of persistent output or other material side effects. Observe what a dry-run or test mode actually changes before relying on its name.
5. **Cleanup.** Remove run-owned scratch data and sessions while preserving evidence at a named location. State how another run avoids sharing mutable state.

Put the safety instructions in the generated guide too: name its disposable data and provider test mode, the point where an external or irreversible action needs authorization, credential setup by name without values, and how to redact and retain evidence. Mark a workflow unverified when the guide has no safe path to prove it.

Add a small feature map from the user's point of view: how to reach each important workflow, how to drive it, and what result proves it works. Start with the primary workflows visible in code or product documentation; do not claim whole-product coverage from a sample. Keep the map compact for a small app and split substantial workflows into linked files. Document any helper's exact invocation and make executable helpers runnable.

## Prove and maintain it

Run the new or revised guide once from launch through cleanup against at least one mapped workflow. Inspect the captured evidence after cleanup. Fix incorrect instructions and repeat the affected steps. Report the exercised workflow, result, evidence path, and any untested workflows or missing prerequisites. A guide that could not be run is a draft with a specific blocker.

When refreshing an established guide, compare affected workflows with current routes, commands, and source, then drive those workflows live. Classify differences as guide drift, harness gap, or product defect. Fix guide drift and harness gaps within the requested scope; report product defects separately. Use `manual-verify` when the task also calls for an acceptance verdict on product behavior.
