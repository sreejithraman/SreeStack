---
name: design-eng
description: Design engineering. Use when planning, building, or reviewing interface polish, component behavior, motion, gestures, visual hierarchy, materials, typography, or accessibility.
disable-model-invocation: true
license: LICENSE.md
---

# Design engineering

Use this process to plan, build, or review interface craft. Match the product's own design system before applying any default below.

## Process

1. Inspect the real interface. Record its purpose, hierarchy, states, content, input methods, use rate, type, surfaces, nearby patterns, and access behavior. Finish when every component in scope has this evidence.
2. Decide what the interface must communicate and which feedback, motion, material, or type choices serve that goal. Frequent and keyboard-led actions should usually feel instant.
3. Choose the component behavior and visual rules below. Extend the product's current tokens and patterns before adding new ones.
4. For an authorized build or fix, implement the smallest change that solves the full interaction, including edge states. For planning or review, keep the product unchanged and specify the exact change instead.
5. For a build or review, test the relevant path: enter, exit, interruption, repeated input, keyboard, pointer and touch use, focus order, semantics, announced status, text scaling, reduced motion, and a busy page. For a plan, name the exact checks the implementation must pass. Slow motion when needed to find bad origins, abrupt stops, or properties that drift out of sync.
6. Report each issue with its location, current behavior, exact change, and reason. Rank changes by user impact.

Completion depends on the task:

- A plan is done when every component in scope has an exact change and test plan.
- A review is done when every applicable check has evidence and every finding has a clear fix.
- A build is done when the implemented result passes the applicable checks on its real surface.

## Foundations

- Start with purpose and hierarchy. The most important action or content should be the easiest to find and understand.
- Put controls near what they affect. Use familiar placement and behavior unless testing proves a new pattern works better.
- Give immediate, continuous feedback while input is active. Show status, completion, warning, and error states at the point where they matter.
- Prefer strong defaults over many options. Handle loading, empty, error, overflow, interruption, and repeated input inside the component.
- Keep related components consistent in spacing, shape, type, color, motion, and control behavior.
- Use delight as the result of clarity, response, and craft rather than as decoration added at the end.

## Motion decisions

### Frequency and purpose

| Use rate | Default |
| --- | --- |
| Very frequent or keyboard-led | Instant |
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

## Component and gesture behavior

- Give pressable controls quick feedback. A small active scale, often `0.97`, works when it fits the control and does not shift layout.
- Start press feedback on pointer-down; commit on a valid release or click. Cancel when the pointer leaves the allowed target or the press becomes a drag. Keep keyboard feedback equally clear and immediate.
- Enter near the final size, such as `scale(0.95)` with opacity, instead of growing from `scale(0)`.
- Set a popover's transform origin to its trigger. Keep an unanchored modal centered.
- Delay the first tooltip enough to avoid stray activation, then show nearby tooltips at once while the user explores the group.
- Stagger only rare, decorative entrances. Keep gaps short and leave controls usable during the sequence.
- Keep dragged content attached to the pointer and preserve the point where the user grabbed it. Capture the pointer through the full gesture.
- Use a small movement threshold before committing a gesture direction. Ignore extra touch points until the gesture ends.
- For drag dismissal and snapping, consider both distance and release speed. Project momentum toward the likely resting point instead of using the release position alone.
- Apply rising resistance past a boundary instead of a hard stop.
- Start an interrupted animation from its live on-screen value and carry velocity into the new target. Springs suit gestures and other interruptible motion; keep bounce slight unless play is part of the product.

## Materials and hierarchy

- Use surface treatment to explain structure: solid surfaces for primary content, raised or translucent surfaces for controls that float above it, and scrims for blocking tasks.
- Match separation to the surface. Prefer a restrained mix of background, border, shadow, and blur over stacking every effect.
- Keep text and controls legible over translucent or busy backgrounds. Avoid stacking light translucent layers where contrast collapses.
- Dim the background for a modal task. Keep a parallel, non-blocking panel connected to the main flow without a heavy scrim.
- Make surface weight fit size and role. Large panels may need stronger separation than chips or small controls.

## Typography

- Use the product's type scale first. Build hierarchy with size, weight, line height, spacing, and contrast as one system.
- Tune tracking for the typeface, size, and writing system. Avoid one letter-spacing value across all text.
- Use tighter line height for large headings and more room for body text. Check long copy, localization, and dense data.
- Prefer fonts with the needed weights, symbols, scripts, and optical sizing. Use `font-optical-sizing: auto` when the face supports it.
- Let text and layout scale together with relative units. Test the user's larger text setting instead of treating overflow as an edge case.

## Implementation rules

- Prefer `transform` and `opacity` for smooth visual motion. Measure before accepting layout-heavy animation.
- Name each transitioned property. `transition: all` hides cost and can animate later changes by mistake.
- Use transitions for state changes that must retarget. Use keyframes for fixed sequences or loops. Use the Web Animations API when code needs direct control without a motion library.
- Use percentages when travel should track the element's own size.
- Watch inherited CSS variables in large trees: changing one can restyle many children. Update the target element directly when measurement shows this cost.

## Access and input

- Honor `prefers-reduced-motion`. Keep useful fades or color changes, and remove or cut large movement, zoom, parallax, and other motion that may cause harm.
- Honor reduced-transparency and increased-contrast preferences where the platform exposes them. Replace blur with a more solid surface and preserve clear boundaries.
- Prefer native elements and semantics. Give controls clear names, roles, values, and states; associate form labels, help, and errors with their fields.
- Keep focus visible and ordered by the task. Every action should work from the keyboard without trapping focus.
- Announce async status, validation, and errors when sighted users can see them but focus does not move.
- Gate hover-only effects with `@media (hover: hover) and (pointer: fine)`.
- Keep input and state changes available while decorative motion runs.
- Test touch and drag work on a real device when possible. Check changed semantics and announcements with a screen reader.

## Review checks

Check every item that applies:

- Purpose, hierarchy, labels, and control placement are clear.
- Loading, empty, error, overflow, and interruption states work.
- Keyboard, pointer, touch, focus, screen-reader, and larger-text paths work.
- Motion has a purpose, suits its use rate, and handles rapid repeat and reversal.
- Curves, times, transform origins, and gesture physics match the action.
- Materials preserve hierarchy and contrast across their backgrounds.
- Type remains legible across size, weight, localization, and text scaling.
- The code names animated properties and avoids needless layout or paint work.
- Reduced-motion, reduced-transparency, contrast, and hover paths work.
- The result fits nearby components and the product's tone.

## Source

Adapted from Emil Kowalski's [`emil-design-eng`](https://github.com/emilkowalski/skills/blob/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/emil-design-eng/SKILL.md) and [`apple-design`](https://github.com/emilkowalski/skills/blob/d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7/skills/apple-design/SKILL.md) skills. See `LICENSE.md`.
