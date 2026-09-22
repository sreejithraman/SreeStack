---
name: ui-visual-design
description: Design and improve visual systems for web, SwiftUI, and UIKit interfaces. Use when choosing or repairing hierarchy, spacing, typography, color, depth, shape, or design tokens; creating a distinct visual direction; or when an interface looks cluttered, flat, inconsistent, generic, unfinished, amateurish, or "off." Use web-interface for browser behavior and accessibility.
---

# UI Visual Design

Turn a visual brief or vague dissatisfaction into a coherent set of design
decisions. Preserve a product's established language when it works; repair or
extend it before introducing another one.

For an authorized build or fix, implement and verify the change. For a plan,
review, or advisory task, leave the product unchanged and make the proposed
roles, values, affected components, and acceptance checks concrete.

## Process

1. Inspect the real interface, nearby components, existing tokens, target
   platforms, content, states, appearance modes, text scaling, and runnable
   surfaces available in scope.
2. Name the visual problem or design job before choosing values. Identify the
   primary content and action, their competitors, the meaningful groups, and
   the semantic roles the system must support.
3. Choose the relevant guidance:
   - For a new identity or a substantial change in visual direction, read
     [art direction](references/art-direction.md) first.
   - For an existing web interface that looks wrong, read
     [diagnosis](references/diagnose.md), then
     [web visual design](references/web.md). For new web visual-system work,
     start with the web reference. Use `web-interface` as well when browser
     semantics, component state behavior, focus, or input changes.
   - For SwiftUI or UIKit, read
     [Apple-platform visual design](references/apple-platforms.md). Use
     `swiftui` or `uikit` when implementation changes native code; those skills
     own framework structure, state, and lifecycle.
4. Establish hierarchy through position, grouping, spacing, weight, color, and
   size. De-emphasize competitors before enlarging the primary element.
5. Extend the system with the fewest new type, spacing, color, shape, or depth
   values needed. Apply semantic roles consistently across components and
   states.
6. When implementation is in scope, style every affected visual state,
   including pressed or selected, disabled, loading, empty, error, focus,
   appearance, and increased-contrast variants where applicable. Preserve the
   interaction contract unless the request includes changing it.
7. Compare the result with the brief and surrounding product on the real
   surface at relevant sizes. Check hierarchy, grouping, legibility, contrast,
   text scaling, appearance modes, and every affected state.

The work is done when the visual job is explicit, the result uses a coherent
system rather than isolated values, affected states and accessibility variants
are covered, and the result fits both the brief and its surrounding product.

## Shared principles

- Prefer semantic roles such as surface, primary text, secondary text, action,
  warning, and separator over raw values at call sites.
- Keep more space around a group than within it. Ambiguous spacing obscures the
  information architecture.
- Style actions by importance in the current task. Destructive does not
  automatically mean primary.
- Use color consistently and pair it with text, shape, iconography, or another
  cue when it communicates state.
- Use depth, borders, materials, and overlap to explain structure. Each cue
  needs a job.
- Treat scales and token counts as tools, not quotas. Add a value when the
  existing system cannot express a real role clearly.
- Prefer standard platform components and existing product patterns before
  custom styling. Customize deliberately when identity or hierarchy needs it.

## Handoff

Show the implemented result or concrete system proposal. State the diagnosed
visual job, the semantic roles or values changed, and the states and access
variants checked. Name any device, browser, appearance, or implementation check
that remains.

For a plan, account for every component in scope with a concrete change,
semantic-role assignment, or explicit reason it remains unchanged.
