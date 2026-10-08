# Scroll overflow feedback

Use a scroll timeline for optional edge decoration that indicates remaining
horizontal content. Native scrolling and controls must work first. Keep essential
labels and focus cues readable; fading an interactive row needs clipping and
focus checks. Use an explicit affordance when discovering overflow is necessary
for the task.

```css
@property --overflow-fade-start {
  syntax: "<length>";
  inherits: false;
  initial-value: 0px;
}
@property --overflow-fade-end {
  syntax: "<length>";
  inherits: false;
  initial-value: 0px;
}

.overflow-feedback {
  --overflow-fade-start: 0px;
  --overflow-fade-end: 0px;
  overflow-x: auto;
}

@keyframes overflow-edges {
  from { --overflow-fade-start: 0px; --overflow-fade-end: 1rem; }
  10%, 90% { --overflow-fade-start: 1rem; --overflow-fade-end: 1rem; }
  to { --overflow-fade-start: 1rem; --overflow-fade-end: 0px; }
}

@supports (animation-timeline: scroll(self inline)) {
  @media (prefers-reduced-motion: no-preference) {
    .overflow-feedback {
      animation: overflow-edges 1ms linear both;
      animation-timeline: scroll(self inline);
      mask-image: linear-gradient(
        to right,
        transparent,
        #000 var(--overflow-fade-start),
        #000 calc(100% - var(--overflow-fade-end)),
        transparent
      );
    }
    .overflow-feedback:focus-within { mask-image: none; }
  }
}
```

This specimen assumes horizontal left-to-right content. Adapt mask direction and
start/end behavior for RTL or other writing modes, and test rather than assuming
physical edges match logical scroll progress. Default fade lengths are zero:
when the scroller has no scroll range the inactive timeline leaves it unfaded.
The support guard prevents an unsupported timeline from becoming a timed animation.
Write `animation-timeline` after the shorthand because `animation` resets it.
See [CSS Scroll-driven Animations](https://drafts.csswg.org/scroll-animations-1/#scroll-progress-timelines)
and [MDN: animation-timeline](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation-timeline).

If both edges only need an overflow cue, use one unregistered length with identical
`from` and `to` keyframe values; interpolation is unnecessary. Keep its explicit
zero baseline and the same support guard. This mechanism does not justify changing
layout or hiding content based only on animation progress.

Reduced motion and unsupported timelines retain native scrolling without the
mask. Unregistered lengths may change discretely on older targets; use static
edge feedback when that is unsuitable. Test a fitting row, start/middle/end,
content changes, keyboard focus, RTL, and representative paint cost. Keep scrollbar
or button affordances available when users need them.
