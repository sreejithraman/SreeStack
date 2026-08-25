---
name: animate
description: Animation implementation. Use when asked to add motion, animate a component, build a transition, or make an interaction's motion or feedback feel responsive; decide whether motion should exist, then implement and test the smallest sound solution.
---

# Animate

Build the requested animation. Make each decision in order; an instant state change is a valid result when motion would add delay without meaning.

## Process

1. Inspect the real interaction, nearby motion, design tokens, browser targets, input methods, use rate, state changes, and runnable surface. Finish when each animated element in scope has this evidence.
2. Gate the motion. Name its purpose and frequency tier below. If it fails the gate, keep the state change instant, test that state on the real surface, and explain why.
3. Choose the simplest tool, properties, curve, timing, interruption behavior, and exit path that fit the interaction.
4. Implement with the current design system and motion tools. Include reduced-motion and input-specific behavior in the same change.
5. Test enter, exit, rapid repeat, interruption, keyboard, pointer, touch, reduced motion, and a busy page. Slow playback when timing or coordination needs closer study.

When motion passes the gate, the work is done when it has a stated purpose, uses the product's own system, affected keyboard, pointer, touch, and reduced-motion paths pass, and any unavailable device check is named. When motion fails the gate, the work is done when the reason is clear and the instant or static state passes the same affected paths.

## Motion gate

| Use rate | Default |
| --- | --- |
| Very frequent or keyboard-led | Instant |
| Frequent, such as hover or list movement | None or very short |
| Occasional, such as a modal, drawer, or toast | Standard UI motion |
| Rare, explanatory, or celebratory | More room for delight |

Motion needs one job:

- Confirm input.
- Explain spatial origin or destination.
- Mark a state change.
- Bridge a change that would otherwise feel abrupt.
- Teach a rare flow.
- Add delight to a rare moment without blocking the task.

If none applies, stop at the gate.

## Tool choice

Use the first tool that meets the need:

| Need | Tool |
| --- | --- |
| Hover, press, color, or class-driven state | CSS transition |
| Entry on mount without extra state, when browser targets support it | CSS `@starting-style` |
| Fixed sequence or loop | CSS keyframes |
| Programmatic playback without a library | Web Animations API |
| Gesture, spring, layout, or interruptible value | The product's existing motion library |

Extend current tokens before adding new curves or times. Add a library only when the existing stack cannot express the required behavior.

## Ingredients

- Prefer `transform` and `opacity`; measure before accepting layout-heavy properties.
- Name every transitioned property. `transition: all` can animate later changes by mistake.
- Enter near the final size, such as `scale(0.95)` with opacity, rather than growing from `scale(0)`.
- Set a trigger-anchored surface's transform origin to its trigger. Keep an unanchored modal centered.
- Use percentages when travel should track the animated element's own size.
- Enter or exit: start with a strong ease-out.
- Move or morph on screen: start with ease-in-out.
- Hover or color change: start with ease.
- Continuous motion: use linear.
- UI motion should usually finish within 300ms. Start near 100–160ms for press feedback, 125–200ms for tooltips and small popovers, 150–250ms for menus, and 200–500ms for large panels.
- Treat values as test points. Distance, size, content, and product tone change what feels right.

## Interruption and gestures

- Use transitions for state changes that must retarget and springs for gesture-driven values.
- Start an interruption from the live on-screen value, not the previous target.
- Carry release velocity into gesture motion and project it toward the likely resting point.
- Keep dragged content attached to the pointer, preserve the grab offset, and capture the pointer through the gesture.
- Apply rising resistance past a drag boundary rather than a hard stop.
- Enter and exit along paths that preserve spatial meaning. Tune their times separately when the system response should be faster.

## Access and input

- Honor `prefers-reduced-motion`. Replace large movement, zoom, parallax, and bounce with a short fade, color change, or instant state change.
- Gate hover-only motion with `@media (hover: hover) and (pointer: fine)`.
- Keep controls usable while decorative motion runs.
- Test gesture work on a real touch device when possible.

## Handoff

Deliver the implemented code first. When the gate rejects motion, deliver the no-motion decision and its instant or static alternative instead. Then state:

- The motion gate result and purpose.
- When motion passes the gate: the chosen tool, properties, curve, and time or spring. When it fails: the instant or static mechanism.
- Any feel check that still needs slow motion, frame stepping, or device testing.

Keep the note brief; the tested interaction is the result.

## Source

Adapted from Emil Kowalski's [`animate` skill](https://github.com/emilkowalski/skills/blob/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/animate/SKILL.md). See `LICENSE.md`.
