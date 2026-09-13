# Tuning motion

Use when existing motion feels slow, abrupt, inconsistent, or poorly timed. Inspect the requested interaction and its current tokens first. A broader scan belongs only to a broader request. Check CSS, keyframes and their driving animation, inline styles, CSS-in-JS, Tailwind values, and motion-library options as needed.

Match a value to its purpose before changing it. Reuse the project's token for that purpose; nearby numbers alone do not make tokens equivalent. Keep unmatched values unless observation gives a reason to change them. Report the behavior a change improves, then test the affected interaction.

## Timing and sequence

- Closings usually benefit from shorter, quieter motion: dropdown/modal 250ms in and 150ms out; panel 400ms in and 350ms out. For a toast, start near 250ms on close and test against the product’s existing behavior.
- Reversible changes can keep the same timing both ways: page slide, tabs, accordion, and icon swap around 250ms; text swap around 150ms. A separate exit phase is not always needed.
- Overshoot can suit a rare entrance or playful gesture. A close should settle promptly. Exit distance and blur can shrink while preserving the spatial path.
- Hover entry should be direct, usually 250ms or less. A softer return can fit a playful avatar row; use only when the motion gate and product style support it.
- Start a stagger around 40ms per item, or 80ms for a few large items. Keep the last item's start delay near 300ms or less: with zero-based indices, that delay is `(count - 1) * offset`. Shrink the offset or cap the animated group for long lists. Also check the last item's finish time and keep interaction available.
- An intent delay can prevent stray tooltip activation; start around 80ms. A short delay can also sequence a checkmark path. Add delay only for a clear purpose. If feedback feels late, inspect existing delay and duration; dismissal and hover-out should start promptly.

## Starting values

Read these alongside the selected pattern's own variables. Use [implementation checks](implementation.md) when values differ or when mapping them to a project.

| Dimension | Values and intended use |
| --- | --- |
| Duration | 40ms stagger; 80ms intent/path delay or shake segment; 150ms close, text swap, tooltip entry; 250ms icon swap, modal/dropdown entry, tabs, page slide; 350ms panel close; 400ms panel entry, skeleton reveal, input clear; 500ms rare emphasis, badge, text reveal, success check |
| Distance | 4px text swap; 6px small shake; 8px badge, page slide, large shake; 12px text reveal; 30px check badge entry |
| Initial scale | 0.96 modal; 0.97 dropdown entry; 0.98 tooltip; 0.99 dropdown close; resting scale 1 |
| Blur | 2px panel, icon/text swap, skeleton, digit entry; 3px page slide or text reveal; 8px success entry; resting blur 0 |

Distance is the offset from rest, not the element's final position. Large travel can make a small state change feel slow; a full panel or drawer may need its full dimension. Larger surfaces can start slightly farther from scale 1. Tune both to geometry and purpose rather than enforcing fixed cutoffs.

Blur is optional. Add it only when it improves a visible overlap or transition and performs well. A fade or color change does not need blur merely to match this table.

| Easing | Value | Intended use |
| --- | --- | --- |
| Smooth out | `cubic-bezier(0.22, 1, 0.36, 1)` | Surface entry/exit, slides, resize, position changes |
| In/out | `ease-in-out` | Icon/text swap, text reveal, skeleton reveal |
| Out | `ease-out` | Tooltip entry/exit |
| Linear | `linear` | Continuous shimmer, pulse, spinner |
| Bounce | `cubic-bezier(0.34, 1.36, 0.64, 1)` | Badge entry |
| Strong bounce | `cubic-bezier(0.34, 3.85, 0.64, 1)` | Playful avatar return |

Each pattern lists the variables its implementation uses. Extend current project tokens before adding names. Keep state hooks and timing-dependent JavaScript aligned with changes. Test enter, exit, repeat, interruption, and reduced motion after tuning.
