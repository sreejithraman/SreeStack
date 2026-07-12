# Quality Gates

Apply every gate before handoff. Record evidence from the real surface.

## Meaning

- The signature moment communicates brand, product, or story.
- Supporting movement preserves a clear hierarchy and reading order.
- Repeated effects share a motif; unrelated effects have a reason to differ.
- Static content remains complete and understandable.

## Control

- Keyboard focus is visible and follows the same state logic as pointer interaction.
- Touch and coarse-pointer behavior is intentional; hover-only information has an equivalent path.
- Required actions respond immediately. Scrolling stays native unless a clearly signposted narrative interaction owns it.
- Autoplaying media is muted, pausable when it carries meaningful duration, and backed by a poster/loading state.

## Reduced motion

- The OS preference is respected globally.
- Large translation, scale, parallax, cursor pursuit, and autoplay video become opacity, an instant state change, or a still frame.
- Spatial meaning and task feedback survive the reduction.
- The reduced experience is manually exercised and supported by visible evidence.

## Rendering

- Frequent animation stays on transform and opacity where possible.
- Layout reads and writes are separated; scroll and pointer work share a frame clock when continuous.
- Observers, timelines, media listeners, and animation frames clean up on unmount and route change.
- Resize and orientation changes recalculate geometry without jumps.
- Pinned sections release correctly and preserve document flow.

## Loading

- Hero media has dimensions, a poster or placeholder, and a deliberate failure state.
- Below-fold media loads near need.
- Mobile receives an asset budget appropriate to its viewport and connection.
- Fonts avoid invisible content and preserve acceptable fallback metrics.
- Animation libraries are loaded once and earn their bundle cost.

## Browser evidence

Verify at minimum:

1. Desktop: load, signature moment, complete scroll, pointer interactions, keyboard path.
2. Mobile: load, complete scroll, touch interactions, orientation or a second narrow width.
3. Reduced motion: reload, signature area, one interactive state, complete scroll.
4. Runtime: console errors/warnings, failed media requests, horizontal overflow, stuck fixed layers.

Capture the URL or command, viewport, actions, expected result, and observed result. A screenshot or recording is strongest for visual gates; console/network evidence is strongest for runtime gates.
