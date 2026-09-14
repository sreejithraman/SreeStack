---
name: animate
description: "Use when a task concerns interface motion: deciding whether to animate, adding or tuning transitions and enter or exit effects, shaping gesture or input feedback, or supporting reduced motion."
---

# Animate

Build the requested animation. Make each decision in order; an instant state change is a valid result when motion would add delay without meaning.

## Process

1. Inspect the real interaction, nearby motion, design tokens, browser targets, input methods, use rate, state changes, and runnable surface. Finish when each animated element in scope has this evidence.
2. Gate the motion. Name its purpose and frequency tier below. If it fails the gate, keep the state change instant, test that state on the real surface, and explain why.
3. Choose the simplest tool, properties, curve, timing, interruption behavior, and exit path that fit the interaction.
4. Read the matching pattern below and [implementation checks](references/implementation.md). Use the current design system and motion tools. Include reduced-motion and input-specific behavior in the same change. For timing or feel changes, read [tuning](references/tuning.md).
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

Keep content steady while someone reads or acts on it. Decorative motion must not move useful data or its controls.

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

Apply motion to the project's existing accessible components. Preserve focus management, keyboard behavior, and state semantics; a motion recipe does not supply a complete modal, menu, or control.

Extend current tokens before adding new curves or times. Add a library only when the existing stack cannot express the required behavior.

## Motion choices

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

## Patterns

Choose by the interaction and state change after motion passes the gate. Read only the relevant guides, including their variables, state hooks, CSS, JavaScript, and limits. Each guide combines techniques for one interaction; choose the variant that fits the existing component. If none fits, build from the rules above.

### Surfaces and layout

| Need | Guide |
| --- | --- |
| Resize a container | [Card resize](references/patterns/card-resize.md) |
| Open a trigger-anchored menu or popover | [Menu dropdown](references/patterns/menu-dropdown.md) |
| Open a centered dialog and backdrop | [Modal open / close](references/patterns/modal.md) |
| Reveal a panel inside a region | [Panel reveal](references/patterns/panel-reveal.md) |
| Move between screens | [Page side-by-side](references/patterns/page-side-by-side.md) |
| Open an edge sheet or drawer | [Drawer or sheet](references/patterns/drawer.md) |
| Expand a disclosure | [Accordion expand](references/patterns/accordion.md) |
| Show or dismiss a notification | [Toast open / close](references/patterns/toast.md) |
| Stack notices and expand them on hover | [Banner stacking](references/patterns/banner-stacking.md) |

### Controls and gestures

| Need | Guide |
| --- | --- |
| Confirm a press | [Button press](references/patterns/button-press.md) |
| Drag, flick, interrupt, and settle a surface | [Drag to dismiss](references/patterns/drag-to-dismiss.md) |
| Move a tab indicator or reveal active labels | [Tabs sliding](references/patterns/tabs-sliding.md) |
| Show hints and move between nearby triggers | [Tooltip open/close](references/patterns/tooltip.md) |
| Turn a trigger into its menu | [Plus to menu morph](references/patterns/plus-menu-morph.md) |
| Check or clear a checkbox | [Checkbox check](references/patterns/checkbox-check.md) |
| Move a switch thumb | [Toggle](references/patterns/toggle.md) |
| Show deliberate hold progress | [Hold to confirm](references/patterns/hold-to-confirm.md) |

### Feedback and changing content

| Need | Guide |
| --- | --- |
| Reveal a badge or dot | [Notification badge](references/patterns/notification-badge.md) |
| Update digits with a short entry | [Number pop-in](references/patterns/number-pop-in.md) |
| Roll digits through a counter | [Spinning counter](references/patterns/spinning-counter.md) |
| Replace text in place | [Text states swap](references/patterns/text-states-swap.md) |
| Replace an icon | [Icon swap](references/patterns/icon-swap.md) |
| Confirm completion | [Success check](references/patterns/success-check.md) |
| Signal a validation error | [Error state shake](references/patterns/error-state-shake.md) |
| Animate a cleared input | [Input clear with dissolve](references/patterns/input-clear-dissolve.md) |
| Confirm a like | [Like button](references/patterns/like-button.md) |
| Blend overlapping content states | [Crossfade with overlap](references/patterns/crossfade.md) |

### Loading and streams

| Need | Guide |
| --- | --- |
| Replace a placeholder with content | [Skeleton loader and reveal](references/patterns/skeleton-reveal.md) |
| Animate an in-progress label | [Shimmer text](references/patterns/shimmer-text.md) |
| Switch status labels | [Thinking states](references/patterns/thinking-states.md) |
| Advance real log or status entries | [Log stream](references/patterns/log-stream.md) |
| Reveal arriving words | [Streaming text](references/patterns/streaming-text.md) |
| Show a dot-matrix loading state | [Matrix dot loader](references/patterns/matrix-loader.md) |

### Hover and entry

| Need | Guide |
| --- | --- |
| Lift nearby items in a row | [Avatar group hover](references/patterns/avatar-group-hover.md) |
| Tilt a decorative card toward the pointer | [Card hover tilt](references/patterns/card-tilt.md) |
| Turn a chevron into an arrow | [Learn more hover](references/patterns/learn-more-hover.md) |
| Reveal lines, lists, or grids in sequence | [Texts reveal](references/patterns/stagger.md) |
| Reveal occasional content on entering the viewport | [Scroll reveal](references/patterns/scroll-reveal.md) |
| Control playback with the Web Animations API | [Programmatic animation](references/patterns/programmatic-animation.md) |

## Handoff

Deliver the implemented code first. When the gate rejects motion, deliver the no-motion decision and its instant or static alternative instead. Then state:

- The motion gate result and purpose.
- When motion passes the gate: the chosen tool, properties, curve, and time or spring. When it fails: the instant or static mechanism.
- Any feel check that still needs slow motion, frame stepping, or device testing.

Keep the note brief; the tested interaction is the result.
