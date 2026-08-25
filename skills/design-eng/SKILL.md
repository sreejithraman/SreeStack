---
name: design-eng
description: Emil Kowalski's compact guide to interface motion and polish.
disable-model-invocation: true
---

# Design engineering

Use this process to plan, build, or review interface motion. Match the product's own design system before applying any numeric default below.

## Process

1. Inspect the real interaction. Record its input method, use rate, state change, current motion, nearby motion, and reduced-motion behavior. Finish when every interaction in scope has this evidence.
2. Decide whether motion helps. Keep motion only when it explains space or state, confirms input, softens a sharp change, or teaches a rare flow. Frequent and keyboard-led actions should usually feel instant.
3. Choose the motion model, properties, curve, and timing from the rules below. Keep related motion consistent with the product.
4. Implement the chosen motion with the smallest change that fits the existing component and design system.
5. Test the full path: enter, exit, interruption, repeated input, pointer and touch use, reduced motion, and a busy page. Slow playback to find bad origins, abrupt stops, and properties that drift out of sync.
6. Report each issue with its location, current behavior, exact change, and reason. Rank changes by user impact.

The work is done when each interaction in scope has a clear motion decision and the tested result stays clear, quick, interruptible where needed, and usable with reduced motion.

## Motion decisions

### Frequency and purpose

| Use rate | Default |
| --- | --- |
| Constant or keyboard-led | Instant |
| Frequent, such as hover or list movement | None or very short |
| Occasional, such as a modal, drawer, or toast | Standard UI motion |
| Rare, explanatory, or celebratory | More room for delight |

Motion needs a job: show where an item came from, mark a state change, confirm input, explain a feature, or keep a change from feeling abrupt. Remove motion that adds delay without doing one of these jobs.

### Curves and time

- Enter or exit: start with a strong ease-out so the interface responds at once.
- Move or morph on screen: start with ease-in-out.
- Hover or color change: start with ease.
- Constant motion: use linear.
- UI motion should usually finish within 300ms. Start near 100–160ms for press feedback, 125–200ms for tooltips and small popovers, 150–250ms for menus, and 200–500ms for large panels.
- Tune enter and exit on their own. The system's response on exit often benefits from a shorter time.
- Use the product's curves. If none exist, strong starting points are `cubic-bezier(0.23, 1, 0.32, 1)` for ease-out and `cubic-bezier(0.77, 0, 0.175, 1)` for ease-in-out.

Treat these values as test points, not laws. Content, distance, size, and product tone change what feels right.

## Interaction rules

- Give pressable controls quick feedback. A small active scale, often `0.97`, works when it fits the control and does not shift layout.
- Enter near the final size, such as `scale(0.95)` with opacity, instead of growing from `scale(0)`.
- Set a popover's transform origin to its trigger. Keep an unanchored modal centered.
- Delay the first tooltip enough to avoid stray activation, then show nearby tooltips at once while the user explores the group.
- Stagger only rare, decorative entrances. Keep gaps short and leave controls usable during the sequence.
- For drag dismissal, consider both distance and speed. Add resistance past bounds, keep pointer capture through the drag, and ignore extra touch points until it ends.
- Preserve momentum when an action may reverse midway. Springs suit gestures and other interruptible motion; keep bounce slight unless play is part of the product.

## Implementation rules

- Prefer `transform` and `opacity` for smooth visual motion. Measure before accepting layout-heavy animation.
- Name each transitioned property. `transition: all` hides cost and can animate later changes by mistake.
- Use transitions for state changes that must retarget. Use keyframes for fixed sequences or loops. Use the Web Animations API when code needs direct control without a motion library.
- Use percentages when travel should track the element's own size.
- Watch inherited CSS variables in large trees: changing one can restyle many children. Update the target element directly when measurement shows this cost.
- Keep good defaults and edge cases inside a component. A polished default matters more than a wide set of options.

## Access and input

- Honor `prefers-reduced-motion`. Keep useful fades or color changes, and remove or cut large movement, zoom, parallax, and other motion that may cause harm.
- Gate hover-only effects with `@media (hover: hover) and (pointer: fine)`.
- Keep input and state changes available while decorative motion runs.
- Test touch and drag work on a real device when possible.

## Review checks

Check every item that applies:

- The motion has a stated purpose and suits how often people see it.
- Keyboard-led actions respond at once.
- Curves, times, and transform origins match the action.
- Enter, exit, rapid repeat, and mid-motion reversal work.
- The code names animated properties and avoids needless layout or paint work.
- Reduced-motion and touch or hover input paths work.
- Motion fits nearby components and the product's tone.

## Source

Adapted from Emil Kowalski's [`emil-design-eng` skill](https://github.com/emilkowalski/skills/blob/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng/SKILL.md). See `LICENSE.md`.
