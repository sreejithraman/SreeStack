---
name: ui-design
description: Use for visual hierarchy, art direction, or design systems on web, SwiftUI, or UIKit; and for web CSS, responsive layout, browser component behavior, input, or accessibility.
---

# UI Design

Own visual design across web, SwiftUI, and UIKit, plus browser styling and
behavior. Use `swiftui` or `uikit` for native implementation, state, lifecycle,
and accessibility; use `animate` for moving feedback and transitions. The
platform owner keeps the action and state contract.
Change only the jobs the request puts in scope.

For an authorized build or fix, implement and verify the change. For a plan,
review, or advisory task, leave the product unchanged and make each proposed
change and acceptance check concrete.

## Work the request

1. **Inspect.** Examine the available interface and nearby components with
   representative content. Identify existing tokens, patterns, and the authoring
   system. Check the target platforms and versions, available runnable surface,
   and affected states, sizes, appearance modes, text scaling, inputs, and access paths.
   Finish with the affected components and supported variants identified.
2. **Diagnose.** Select the job: visual hierarchy or identity, CSS/layout,
   browser behavior, accessibility, or a combination. For visual work, identify
   the primary content and action, competing emphasis, groups, and semantic
   roles. For behavior work, identify the expected activation, focus, input,
   status, and state contract. Finish with an observable problem or design
   intent and the contracts the change must preserve.
3. **Choose guidance.** Follow each applicable branch below; read the sections
   that address the job. An identity change starts with art direction, then the
   platform guidance. A local CSS or behavior fix starts at its matching branch.
   Finish with the proposed change tied to the diagnosed cause or design intent.
4. **Build or propose.** Use the product's tokens, components, and authoring
   stack. For visual work, resolve hierarchy and layout before decorative detail;
   compare values with their neighbors and test the narrowest relevant surface
   before wider compositions. Sketch or prototype when a direction needs trying.
   Prefer intrinsic layout and native capabilities when they meet the contract.
   Check feature support against the actual targets and provide a usable fallback
   where needed. Cover every affected component, state, and access variant.
   For advisory work, make those changes and checks concrete without editing
   the product.
5. **Check.** For implementation, exercise the changed surface at the affected
   sizes and through its input and accessibility paths. Syntax support or a
   screenshot alone does not establish an interaction works. Use `verify` for
   hands-on acceptance. For advisory work, trace each proposal through the
   representative components and state the checks implementation must pass.

## Read by task

Combine branches when the request crosses them. Keep visual direction stable
for behavior-only work, and interaction/access contracts stable for visual-only
work.

| Task | Guidance |
| --- | --- |
| New identity or substantial visual redirection | [Art direction](references/art-direction.md), then the web or Apple branch |
| Existing web interface looks wrong | [Diagnosis](references/diagnose.md), then the relevant [web visual system](references/web.md) sections |
| Web type, spacing, color roles, shape, hierarchy, or starter tokens | [Web visual systems](references/web.md) |
| Build or repair a numbered HSL web color ramp | [Palette workflow](references/systems.md); keep another working color model when it fits |
| Web reset, logical properties, fluid scales, or theme/color implementation | [CSS foundations](references/web-css-foundations.md) |
| Web content widths, grids, containers, responsive layout, spacing, or overflow | [Web layout](references/web-layout.md) |
| Browser semantics, states, focus, input, announcements, or accessibility | [Web behavior and accessibility](references/web-behavior-and-accessibility.md) |
| Web viewport, safe areas, virtual keyboard, touch, scrolling, browser chrome, carousel, or bounded panel | [Mobile browser behavior](references/mobile-web.md), plus the behavior contract when input or state changes |
| Web shadows, text alignment, image contrast/cropping, or media geometry | Matching [visual techniques](references/techniques.md) sections |
| SwiftUI or UIKit visual design | [Apple-platform visual design](references/apple-platforms.md), with the framework owner |

## Visual decisions

Use position, grouping, spacing, weight, color, and size together to establish
hierarchy. Preserve the product's established language where it serves the job.

- Prefer semantic roles such as surface, primary text, secondary text, action,
  warning, and separator over raw values at call sites.
- Keep more space around a group than within it. Ambiguous spacing obscures the
  information architecture.
- Give the primary action the strongest treatment, keep secondary actions
  clearly available, and use quiet or link-like treatment for tertiary actions.
  Destructive actions become primary only when they are the current decision,
  such as in a deletion confirmation.
- Use color consistently and pair it with text, shape, iconography, or another
  cue when it communicates state.
- Use depth, borders, materials, and overlap to explain structure. Each cue
  needs a job.
- Extend scales only when an existing value cannot express a real role clearly.
  Scales and token counts are tools, not quotas.
- Prefer standard platform components and existing product patterns before
  custom work. Customize deliberately when identity, hierarchy, or behavior
  requires it.

## Handoff

Deliver the implemented result or concrete proposal and state the diagnosed
job, roles or contracts changed, and checks performed. Completion requires every
affected component and variant to be accounted for, a coherent system that fits
the brief and surrounding product, and explicit remaining evidence gaps by
browser, device, appearance, input, or accessibility path.

For a plan, account for every component in scope with a concrete change or an
explicit reason it remains unchanged.
