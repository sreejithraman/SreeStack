# Programmatic animation

Use the Web Animations API when playback needs JavaScript control but the project does not need a motion library.

```js
element.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```

This example reveals a clipped surface. Choose duration and properties for the task. Compositor execution depends on the animated property and browser; measure it rather than assuming hardware acceleration.

Retain the returned `Animation` when you need pause, reverse, cancellation, or completion handling. Clean it up on teardown, handle cancellation, and transfer the final state to the component rather than leaving a stale filled animation. Apply the final state directly for reduced motion.
