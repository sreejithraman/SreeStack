---
name: ui-design
description: Cross-platform visual design and browser interface behavior. Use for visual hierarchy, art direction, or design systems in web, SwiftUI, or UIKit; also use for browser component states, input, and accessibility. Use swiftui or uikit for native implementation and behavior, and animate for motion.
---

# UI Design

Turn an interface brief, usability problem, or vague dissatisfaction into a
coherent design. Preserve the product's established language and interaction
contract where they work; change only the dimensions the request puts in scope.

For an authorized build or fix, implement and verify the change. For a plan,
review, or advisory task, leave the product unchanged and make each proposed
change and acceptance check concrete.

## Process

1. Inspect the real interface, nearby components, existing tokens, target
   platforms, content, states, appearance modes, text scaling, input methods,
   access paths, and runnable surfaces available in scope.
2. Select the dimensions the task actually requires: visual system, art
   direction, component behavior, or accessibility. Name the design job before
   choosing values or changing behavior. For visual work, identify the primary
   content and action, their competitors, the meaningful groups, and the
   semantic roles the system must support.
3. Read only the guidance for those dimensions:
   - For a new identity or a substantial change in visual direction, read
     [art direction](references/art-direction.md) first.
   - For an existing web interface that looks wrong, read
     [diagnosis](references/diagnose.md), then
     [web visual design](references/web.md). For new web visual-system work,
     start with the web reference.
   - For browser semantics, component states, focus, keyboard or pointer input,
     announcements, or accessibility, read
     [web behavior and accessibility](references/web-behavior-and-accessibility.md).
   - For SwiftUI or UIKit visual work, read
     [Apple-platform visual design](references/apple-platforms.md). Use `swiftui`
     or `uikit` for native implementation, behavior, and accessibility; those
     skills own framework structure, state, and lifecycle.
   - Use `animate` when feedback moves or transitions. The relevant platform
     skill still owns the action and state contract.
4. For visual work, establish hierarchy through position, grouping, spacing,
   weight, color, and size. Extend the system with the fewest new values needed
   to express real semantic roles across affected components and states. When
   only visual dimensions are selected, keep interaction and access contracts
   unchanged.
5. For web behavior or accessibility work, preserve the component's semantic,
   activation, focus, input, status, and state contracts across the paths in
   scope. Keep visual changes limited to what those contracts require unless
   visual direction is also selected.
6. When implementation is in scope, cover every affected state and access
   variant rather than styling or testing only the happy path.
7. Exercise the result on the real surface at relevant sizes and through the
   affected input and accessibility paths. Use `manual-verify` when hands-on
   evidence would add confidence.

The work is done when every selected dimension has an explicit design job,
affected components and states use one coherent system and contract, and the
result fits both the brief and its surrounding product. Name any browser,
device, appearance, input, or accessibility evidence that remains unchecked.

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
  custom work. Customize deliberately when identity, hierarchy, or behavior
  requires it.

## Handoff

Show the implemented result or concrete proposal. State the selected design
dimensions, diagnosed job, roles or contracts changed, and states and access
paths checked.

For a plan, account for every component in scope with a concrete change or an
explicit reason it remains unchanged.
