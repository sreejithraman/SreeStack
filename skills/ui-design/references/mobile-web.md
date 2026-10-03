# Mobile browser behavior

Use for web layouts, controls, and gestures on phones or mixed-input devices.
Match the reported symptom and change only the responsible surface. Native
Apple implementation stays with `swiftui` or `uikit`; motion stays with `animate`.

## Viewport, safe areas, and keyboard

- Keep a device-width viewport and user zoom available. Avoid scale limits or
  `user-scalable=no` as remedies for a layout or focus problem.
- Choose viewport units by the layout job: `svh` uses the space with browser UI
  expanded and stays stable as that UI retracts; `dvh` follows the dynamic size
  and can resize content during scrolling; `vh`/`lvh` use the large viewport.
  Use a content-driven minimum height for a page that can grow, and an explicit
  scroll strategy for bounded shells. A full-screen shell may need `dvh`; a
  stable first screen may need `svh`. See [viewport unit definitions](https://drafts.csswg.org/css-values-4/#viewport-relative-lengths).
- Test keyboard-open and keyboard-closed states independently. The keyboard
  can shrink the visual viewport while leaving the layout viewport and viewport
  units unchanged. `interactive-widget=resizes-content` opts into resizing both
  viewports where supported; verify support and the resulting layout on each
  target rather than treating it or `dvh` as a universal keyboard fix. Keep the
  focused field, validation, and required actions reachable. See [Chrome's
  viewport and keyboard behavior](https://developer.chrome.com/blog/viewport-resize-behavior).
- Use `viewport-fit=cover` when edge-to-edge rendering is intended, then inset
  important content with `env(safe-area-inset-*, 0px)`. Combine those insets with
  ordinary spacing rather than replacing it, and assign each edge to one layout
  owner so nested bars and sheets do not double-pad. Include landscape's left
  and right edges. Safe-area values are not keyboard height. See [WebKit's
  safe-area guidance](https://webkit.org/blog/7929/designing-websites-for-iphone-x/).
- Keep input text readable at the computed size. If focusing a field causes
  unwanted zoom, inspect font sizing and transforms on the target browser;
  increase the field's readable size and retest while preserving user zoom.
  Choose `type`, `inputmode`, capitalization, correction, and `enterkeyhint` for
  the field's meaning. A numeric keyboard hint does not validate input or make a
  code a numeric quantity. See [HTML input modalities](https://html.spec.whatwg.org/multipage/interaction.html#input-modalities:-the-inputmode-attribute).

## Touch and mixed input

- Gate optional hover decoration with `(hover: hover)`; add `(pointer: fine)`
  only when precision is relevant. These describe the primary pointing input,
  not a device category: a stylus can be fine, and touch and mouse can coexist.
  `any-hover`/`any-pointer` describe available capabilities, not the input used
  for a particular event. Keep actions reachable without hover and maintain
  keyboard focus feedback. See [interaction media features](https://drafts.csswg.org/mediaqueries-4/#mf-interaction).
- Follow the [press and activation contract](web-behavior-and-accessibility.md).
  Immediate feedback may use `:active` or pointer-down state; an action still
  commits through valid activation, with cancellation and drag handled.
  `touch-action: manipulation` allows panning and pinch zoom while excluding
  double-tap zoom; apply it to a control only when that tradeoff addresses a
  demonstrated need. It does not repair slow application work. See [Pointer
  Events touch-action](https://www.w3.org/TR/pointerevents/#the-touch-action-css-property).
- Preserve browser tap feedback unless a verified replacement covers that
  control. Scope any vendor tap-highlight override to the affected controls.
  Scope selection suppression to control labels or drag handles that need it;
  leave names, addresses, identifiers, error messages, and body content copyable.
  Preserve useful link and image long-press actions unless the component's
  explicit interaction contract calls for replacing them.

## Scroll and gesture ownership

- Prefer native overflow scrolling for a carousel or long list; add scroll
  snapping when it serves navigation. Use a custom gesture only when its behavior
  requires one, and keep an accessible alternative to dragging.
- `touch-action` names what the browser may handle. For a custom horizontal
  drag, `pan-y pinch-zoom` keeps vertical browser panning and zoom; for a vertical
  drag, `pan-x pinch-zoom` keeps the other axis and zoom. Inspect ancestor rules
  too: their restrictions can remove these permissions. Avoid `none` as a
  general drag recipe because it suppresses browser panning and zoom. Handle
  `pointercancel` and lost capture without committing an unintended action.
  See [Pointer Events](https://www.w3.org/TR/pointerevents/#the-touch-action-css-property)
  and [pinch-zoom semantics](https://compat.spec.whatwg.org/#touch-action).
- Use `overscroll-behavior` on the relevant scroll container and axis when a
  sheet or nested list must not chain to the page. `contain` suppresses chaining
  and non-local boundary actions while retaining local overscroll affordances;
  `none` suppresses those affordances too. Change root pull-to-refresh or
  navigation gestures only when the app contract requires it. Verify on the
  target browser, including a container too short to scroll. Avoid blanket
  touch-event cancellation for scroll control. See [overscroll behavior](https://drafts.csswg.org/css-overscroll-1/).

## Browser chrome and evidence

Use `theme-color` as a browser hint matching the adjacent surface where supported.
Scheme-specific metadata can follow system appearance; an app-owned theme switch
must keep metadata consistent with the selected theme. Browser UI may adjust or
ignore the hint, and installed presentation has its own platform behavior. Check
the actual supported mode. See [HTML theme-color](https://html.spec.whatwg.org/multipage/semantics.html#meta-theme-color).

Use `manual-verify` for mobile acceptance checks. Device emulation is useful for
layout and some input checks, but is an approximation; verify browser chrome,
keyboard, safe areas, gestures, and touch feel on the target browser and hardware
when available. Report which paths used emulation, a simulator, or a device and
which remain unchecked. See [Chrome Device Mode limitations](https://developer.chrome.com/docs/devtools/device-mode#limitations).
