# Web motion

Use this branch for websites and web apps. Follow [implementation checks](implementation.md) for every web motion change, whether or not a pattern fits. For timing or feel changes, also read [tuning](tuning.md).

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
- For a drag without competing browser scrolling, capture the active pointer on
  pointer down, preserve its grab offset, and keep the content attached through
  the gesture. When drag intent competes with scrolling, declare the browser's
  allowed pan axis and defer capture until the drag wins. Follow
  [drag to dismiss](patterns/drag-to-dismiss.md) for arbitration and cancellation.
- Apply rising resistance past a drag boundary rather than a hard stop.
- Enter and exit along paths that preserve spatial meaning. Tune their times separately when the system response should be faster.

## Access and input

- For motion on a web control, use `web-interface` for the action's activation,
  cancellation, pointer, and keyboard contract. This skill owns the moving
  feedback's timing and interruption.
- Honor `prefers-reduced-motion`. Replace large movement, zoom, parallax, and bounce with a short fade, color change, or instant state change.
- Gate hover-only motion with `@media (hover: hover) and (pointer: fine)`.
- Keep controls usable while decorative motion runs.
- Test gesture work on a real touch device when possible.
- Test on a representative busy page or loaded application state, not only an isolated component.
- For JavaScript-driven motion, respond when the media query changes and cancel work that no longer applies. CSS alone does not stop JavaScript timers or animation loops.

The Web Animations API guidance also recommends a way to pause or disable animation and a complementary experience for reduced-motion users. See [MDN: Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API#accessibility) and [`prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion).

## Patterns

Choose by the interaction and state change after motion passes the gate. Read only the relevant guides, including their variables, state hooks, CSS, JavaScript, and limits. Each guide combines techniques for one interaction; choose the variant that fits the existing component. If none fits, build from the rules above.

### Surfaces and layout

| Need | Guide |
| --- | --- |
| Resize a container | [Card resize](patterns/card-resize.md) |
| Open a trigger-anchored menu or popover | [Menu dropdown](patterns/menu-dropdown.md) |
| Open a centered dialog and backdrop | [Modal open / close](patterns/modal.md) |
| Reveal a panel inside a region | [Panel reveal](patterns/panel-reveal.md) |
| Move between screens | [Page side-by-side](patterns/page-side-by-side.md) |
| Open an edge sheet or drawer | [Drawer or sheet](patterns/drawer.md) |
| Expand a disclosure | [Accordion expand](patterns/accordion.md) |
| Show or dismiss a notification | [Toast open / close](patterns/toast.md) |
| Stack notices and expand them on hover | [Banner stacking](patterns/banner-stacking.md) |

### Controls and gestures

| Need | Guide |
| --- | --- |
| Confirm a press | [Button press](patterns/button-press.md) |
| Drag, flick, interrupt, and settle a surface | [Drag to dismiss](patterns/drag-to-dismiss.md) |
| Move a tab indicator or reveal active labels | [Tabs sliding](patterns/tabs-sliding.md) |
| Show hints and move between nearby triggers | [Tooltip open/close](patterns/tooltip.md) |
| Turn a trigger into its menu | [Plus to menu morph](patterns/plus-menu-morph.md) |
| Check or clear a checkbox | [Checkbox check](patterns/checkbox-check.md) |
| Move a switch thumb | [Toggle](patterns/toggle.md) |
| Show deliberate hold progress | [Hold to confirm](patterns/hold-to-confirm.md) |

### Feedback and changing content

| Need | Guide |
| --- | --- |
| Reveal a badge or dot | [Notification badge](patterns/notification-badge.md) |
| Update digits with a short entry | [Number pop-in](patterns/number-pop-in.md) |
| Roll digits through a counter | [Spinning counter](patterns/spinning-counter.md) |
| Replace text in place | [Text states swap](patterns/text-states-swap.md) |
| Replace an icon | [Icon swap](patterns/icon-swap.md) |
| Confirm completion | [Success check](patterns/success-check.md) |
| Signal a validation error | [Error state shake](patterns/error-state-shake.md) |
| Animate a cleared input | [Input clear with dissolve](patterns/input-clear-dissolve.md) |
| Confirm a like | [Like button](patterns/like-button.md) |
| Blend overlapping content states | [Crossfade with overlap](patterns/crossfade.md) |

### Loading and streams

| Need | Guide |
| --- | --- |
| Replace a placeholder with content | [Skeleton loader and reveal](patterns/skeleton-reveal.md) |
| Animate an in-progress label | [Shimmer text](patterns/shimmer-text.md) |
| Switch status labels | [Thinking states](patterns/thinking-states.md) |
| Advance real log or status entries | [Log stream](patterns/log-stream.md) |
| Reveal arriving words | [Streaming text](patterns/streaming-text.md) |
| Show a dot-matrix loading state | [Matrix dot loader](patterns/matrix-loader.md) |

### Hover and entry

| Need | Guide |
| --- | --- |
| Lift nearby items in a row | [Avatar group hover](patterns/avatar-group-hover.md) |
| Tilt a decorative card toward the pointer | [Card hover tilt](patterns/card-tilt.md) |
| Turn a chevron into an arrow | [Learn more hover](patterns/learn-more-hover.md) |
| Reveal lines, lists, or grids in sequence | [Texts reveal](patterns/stagger.md) |
| Reveal occasional content on entering the viewport | [Scroll reveal](patterns/scroll-reveal.md) |
| Control playback with the Web Animations API | [Programmatic animation](patterns/programmatic-animation.md) |
