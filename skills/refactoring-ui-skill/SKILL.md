---
name: refactoring-ui
description: Improve visual hierarchy and styling in web, SwiftUI, and UIKit interfaces through coherent spacing, typography, color, depth, and token systems. Use for visual design work on those platforms when UI looks cluttered, flat, inconsistent, generic, unfinished, amateurish, plain, or "off"; when asked to make one of those interfaces look better; and when choosing visual design values or tokens.
---

# Refactoring UI

Turn vague visual dissatisfaction into a small set of system decisions. Preserve the product's existing design language when it is coherent; repair or extend it before introducing another one.

For an authorized build or fix, implement and verify the process below. For a
plan, review, or advisory task, leave the product unchanged and apply proposed
roles or values only to disposable examples; report exact changes and checks for
the eventual implementation.

## Process

1. Identify the requested outcome. For an interface change, inspect the real interface, nearby components, existing tokens, target platform and versions, content density, interaction states, appearance modes, text sizes, and runnable surface. For system or advisory work, inspect the existing tokens, documented roles, platform constraints, and representative components available in scope.
2. Identify the visual failure or system gap before changing values. For an existing interface, name the hierarchy, grouping, consistency, legibility, or depth problem. For new interface work, name the primary content and action. For system work, name the semantic roles and relationships the values must support.
3. Establish the hierarchy that applies: primary, secondary, and tertiary content; groups and their spacing; primary, secondary, and tertiary actions. De-emphasize competitors before enlarging the primary element.
4. Read the platform branch before choosing units or APIs:
   - For websites and web apps, read [diagnosis](references/diagnose.md) first for an existing UI, then read [web visual design](references/web.md). For new work, start with web visual design. When creating or substantially reshaping a brief-specific aesthetic direction, also use `frontend-web-design`: it owns art direction and palette anchors, while this skill owns diagnosis, scale expansion, and semantic roles. `frontend-web-design` also owns web component behavior when the change affects feedback, async or edge states, interruption, or repeated input. When both skills apply to art direction, establish that direction first, then continue here with the approved anchors.
   - For SwiftUI or UIKit, read [Apple-platform visual design](references/apple-platforms.md). When implementation changes native code, also use `swiftui` or `uikit`: those skills own framework structure, state, and lifecycle, while this skill owns visual-system decisions.
5. Extend the current system with the fewest new spacing, type, color, radius, or depth values needed. Apply the same semantic role consistently across components and states.
6. When implementation is in scope, style every applicable visual state: default, pressed or selected, disabled, loading, empty, error, focus, and high-contrast or appearance variants. Preserve how the component enters and leaves those states; use `frontend-web-design` when a web change also alters behavior, interruption, or repeated input.
7. Verify the result at the level the request permits. Run an implemented interface and compare before and after at relevant sizes. For system or advisory work, apply the proposed roles and values to representative components or concrete examples. Check hierarchy, grouping, readable text, contrast, text scaling, appearance modes, and affected input methods where applicable.

The work is done when the visual problem or system gap is named, the result uses a coherent system rather than isolated values, applicable states and accessibility variants are covered, and the result fits the surrounding product and requested scope.

## Shared principles

- Choose values from a small, deliberate scale. Add a value only when neighboring values cannot serve the role.
- Build hierarchy with position, spacing, weight, color, and size together. Size alone produces oversized primary content and unreadable secondary content.
- Keep more space around a group than within it. Ambiguous spacing is an information-architecture defect, not decoration.
- Style actions by importance in the current task. Destructive does not automatically mean primary.
- Put controls near the content or state they affect. Prefer familiar placement and behavior unless evidence supports a different pattern.
- Use color consistently and pair it with text, shape, iconography, or another cue when it communicates state.
- Prefer semantic roles such as surface, primary text, secondary text, action, warning, and separator over raw visual values at call sites.
- Use depth to explain layering and interaction. A border, shadow, material, background change, or overlap needs a structural job.
- Use standard platform components and the product's existing patterns before custom styling. Customize deliberately where identity or hierarchy needs it.
- Keep content usable at larger text sizes, in light and dark appearances, and with increased contrast.

## Handoff

Show the implemented result or the concrete system proposal. State the diagnosed visual problem or system gap, the values or semantic roles changed, and the states and accessibility variants checked. Name any device, browser, appearance, or implementation check that remains.

For a plan, account for every component in the requested scope with a concrete
change, semantic role assignment, or explicit reason it remains unchanged, plus
the checks its implementation must pass.
