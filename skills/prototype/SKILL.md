---
name: prototype
description: Build runnable, disposable UI prototypes for web, mobile, or desktop. Use to answer a design question by trying one concept or comparing meaningfully different layouts or interactions before production implementation.
---

# Prototype

Build enough UI to answer a design question on the target platform.
A prototype is an exploration surface, not authorization to ship the result.

## 1. Frame the experiment

Inspect the request, current interface, nearby code, and available tooling. State
the design question, where the prototype will run, and what evidence would make
the options distinguishable. Ask only when a missing choice would materially
change what you build; continue safe, reversible work while waiting.

Choose an option set large enough to expose the real decision:

- Use one concept when the question is whether a specific direction works.
- Use two when the decision is a genuine tradeoff.
- Add further options when each represents a distinct direction that the
  existing set does not test.

Variants should differ in layout, information hierarchy, navigation, behavior,
or motion rather than only color or copy. Follow a count the user specifies.

## 2. Choose the real surface

Prefer the existing screen with its surrounding navigation, components, and
representative content. Use a separate prototype route, screen, preview, or
development target when no existing screen fits. Clearly mark prototype files,
entry points, and controls, and keep them out of release builds.

Load only the specialists the experiment needs:

- Use `ui-design` for visual direction and for browser behavior or
  accessibility.
- Use `animate` when motion is part of the question.
- Use `swiftui` or `uikit` for native Apple construction and behavior.

Match the platform:

- **Web:** use the existing route when possible. A query parameter can make each
  option easy to reopen and share.
- **SwiftUI or UIKit:** use the app's framework. A preview can answer a static
  layout question; use the running app for navigation, gestures, keyboard
  behavior, system UI, or other runtime behavior.
- **Other mobile or desktop platforms:** use the app's normal framework and
  host, with the relevant input methods and window sizes.

Use a browser mockup for a native product only when the user requests or accepts
that fidelity. When target tooling is unavailable, state the blocking tooling
gap and what the fallback can and cannot establish.

## 3. Build safely

Use the project's components and design system while allowing each option to
make its intended structural choice. Share stable fixtures and controls rather
than forcing the options through one premature abstraction.

Use the same representative content and meaningful empty, loading, error, or
crowded states across options. Reuse safe read-only data access when helpful.
Stub writes, keep experimental state local, and prevent external side effects.
Add only enough behavior to try the flow.

When the requested workflow would write real data or cause another external
effect, keep that step stubbed, state exactly what was not exercised, and offer
a provider test mode, disposable account, or local fixture instead.

Spend effort on the dimensions the question tests, such as hierarchy, spacing,
touch targets, safe areas, keyboard overlap, resizing, or motion character.

Keep the code disposable but reliable enough to evaluate. Prefer running the
prototype over production-grade automated coverage. Add a narrow test only when
non-obvious experimental logic would otherwise make the result untrustworthy.

## 4. Make comparison easy

For multiple options, provide one development-only control that identifies the
current option and switches without rebuilding. Keep it visually separate from
the interface under review and away from its controls.

- **Web:** a switcher can update the option through the project's router.
  Keyboard shortcuts must leave text inputs and other controls alone.
- **Mobile:** use a debug menu, sheet, or compact native picker that respects
  safe areas and existing gestures.
- **Desktop:** use a development menu or toolbar suited to the app.

Keep sample state stable while switching when that makes the comparison fair.
When options require different state or navigation, reset to a known starting
point and make the reset visible. Give each option a short name that states its
design choice.

## 5. Exercise and present

Run every option on the target platform and exercise the interactions that
answer the design question. Use `manual-verify` when the judgment depends on a
real workflow. Use `showroom` to package useful visual evidence.

For multiple options, exercise the switcher and confirm that its control stays
clear of the interface and interactions under review.

Provide the run command or build target, entry screen, option controls, and any
environment prerequisite needed to return to the prototype. Identify each
screenshot or recording by option. Explain the tradeoff each option tests and
state any behavior or platform condition that remains unverified.

Leave the choice open until the user picks one or asks you to choose. Combine
parts only when the resulting direction remains coherent and testable.

## 6. Record and dispose

Before a decision, keep the prototype reviewable on the task branch or another
clearly marked development surface. Once a direction is chosen, record the
winner and why in a durable project surface already in scope, such as a PR
description, project note, or authorized issue update.

When production implementation is in scope, apply the chosen direction with the
project's normal quality checks and remove prototype controls and unused
options. Preserve the prototype branch or artifacts when the user requests it,
revisiting the comparison still has value, or no durable project record is
authorized. When retained, record the branch pointer and run steps in the
durable record when one is available. Otherwise retain the decision and
evidence there, then clean up the disposable work.

A prototype-only request ends with a reviewable prototype, not a production
change.

## Done

The prototype is ready for a decision when the design question is explicit,
each option tests a distinct answer, relevant states and interactions run on the
target surface, comparison is easy, and the evidence and remaining gaps are
clear. After a decision, completion also requires a recorded verdict and an
explicit disposition for the disposable work.
