---
name: prototype
description: Use when asked to build a UI prototype, or when a UI design decision needs trying the interface before production implementation.
---

# Prototype

Build enough real UI to answer a design question on the target platform before production
implementation. Start from an open UI decision, the existing surface or target platform,
and nearby project code. Leave a clearly marked, reviewable prototype with labeled evidence.
You are done for a decision when the question is explicit, each option tests a
distinct answer, relevant states and interactions run on the target surface, comparison is
easy, and evidence plus remaining gaps are clear; after a decision, completion also requires
a recorded verdict and disposition of the disposable work.

A prototype is an exploration surface, not authorization to ship the result.

## 1. Frame the experiment

Inspect the request, current interface, nearby code, and available tooling. State the design
question, where the prototype will run, and what evidence distinguishes the options. Ask
only when a missing choice would materially change what you build; continue safe, reversible
work while waiting.

Size the option set to expose the real decision (honoring any count the user specifies):
- One concept when testing whether a specific direction works.
- Two when the decision is a genuine tradeoff.
- Additional options only when each tests a distinct direction the existing set does not.

Unless the user's question is specifically about copy or color, options should differ in
layout, information hierarchy, navigation, behavior, or motion.

## 2. Choose the real surface

Prefer the existing screen with its surrounding navigation, components, and representative
content; use a separate prototype route, screen, preview, or dev target when no existing
screen fits. Mark prototype files, entry points, and controls clearly and keep them out of
release builds.

Load only the specialists the experiment needs: [ui-design](../ui-design/SKILL.md) for
visual direction and browser behavior/accessibility, [animate](../animate/SKILL.md) when
motion is part of the question, and [swiftui](../swiftui/SKILL.md) or
[uikit](../uikit/SKILL.md) for native Apple construction and behavior.

Match the platform:
- **Web:** prefer the existing route; a query parameter makes each option easy to reopen and
  share.
- **SwiftUI or UIKit:** use the app's framework. A preview answers static layout questions;
  use the running app for navigation, gestures, keyboard behavior, system UI, or runtime
  behavior.
- **Other mobile or desktop:** use the app's normal framework and host with relevant input
  methods and window sizes.

Use a browser mockup for a native product only when the user requests or accepts that
fidelity. When target tooling is unavailable, name the blocking gap and what any fallback
can and cannot establish.

## 3. Build safely

Use the project's components and design system while letting each option make its structural
choice. Share stable fixtures and controls without forcing options through a premature
abstraction.

Use the same representative content and meaningful empty, loading, error, or crowded states
across options. Reuse safe read-only data access when helpful, stub writes, keep
experimental state local, and prevent external side effects. When the workflow would write
real data or trigger external effects, keep that step stubbed, state what was not exercised,
and offer a provider test mode, disposable account, or local fixture instead.

Spend effort on the dimensions the question tests (hierarchy, spacing, touch targets, safe
areas, keyboard overlap, resizing, motion), adding only enough disposable, reliable behavior
to try the flow. Prefer running the prototype over
production-grade automated coverage; add a narrow test only when non-obvious experimental
logic would otherwise make the result untrustworthy.

## 4. Make comparison easy

For multiple options, add one development-only control that names the active option and
switches without rebuilding, visually separated from and clear of the interface under
review:
- **Web:** a switcher updating the option through the router; keyboard shortcuts must not
  hijack text inputs or controls.
- **Mobile:** a debug menu, sheet, or compact native picker respecting safe areas and
  existing gestures.
- **Desktop:** a development menu or toolbar suited to the app.

Keep sample state stable across switches when that makes the comparison fair; when options
require different state or navigation, reset to a known starting point and make the reset
visible. Give each option a short name stating its design choice.

## 5. Exercise and present

Run every option on the target platform and exercise the interactions that answer the design
question. For multiple options, exercise the switcher and confirm it stays clear of the
interface and interactions under review. Use [verify](../verify/SKILL.md) when judgment
depends on a real workflow, and [show-me](../show-me/SKILL.md) to choose demonstrations and
access.

Give the run command or build target, entry screen, option controls, and environment
prerequisites to revisit the prototype. Label each screenshot or recording by option,
explain the tradeoff each option tests, and name any behavior or platform condition that
remains unverified. Leave the choice open until the user picks one or asks you to choose;
combine parts only when the resulting direction remains coherent and testable.

## 6. Record and dispose

Before a decision, keep the prototype reviewable on the task branch or a clearly marked dev
surface. Once a direction is chosen, record the winner and why in a durable surface already
in scope (such as a calling workflow's record, PR description, project note, or authorized
issue update).

When production implementation is in scope, apply the chosen direction with the project's
normal quality checks and remove prototype controls and unused options. Preserve the
prototype branch or artifacts when the user requests it, revisiting the comparison still has
value, or no durable record is authorized (recording the branch pointer and run steps in the
durable record when available); otherwise retain the decision and evidence there and clean
up the disposable work. A prototype-only request ends with a reviewable prototype, not a
production change.
