# Drag to dismiss

Use for a draggable drawer, toast, or sheet whose motion can reverse while held. Keep the item attached to the pointer, then decide whether to dismiss or return.

## Track the active pointer

- Capture one pointer, retain its grab offset, and ignore other pointers until release or cancellation.
- Handle `pointercancel` and release capture on teardown. A second touch must not take over the drag.
- Write the dragged element's transform directly. Limit high-frequency style updates to the moving element.
- Apply rising resistance beyond bounds. Preserve the intended dismissal direction.

```js
element.style.transform = `translateY(${distance}px)`;
```

## Release and settle

Use both distance and recent velocity toward the dismissal edge. A whole-gesture average can miss a flick after a pause, and absolute speed can dismiss a gesture moving back toward rest. Keep recent pointer samples and choose thresholds for the component and input device.

```js
// Distances and speed are signed toward the dismissal edge.
if (distanceTowardExit >= distanceThreshold || velocityTowardExit > velocityThreshold) {
  dismiss();
} else {
  returnToRest();
}
```

Settle from the current position with the release velocity. Use the project's spring API; this is a starting configuration when it supports duration and bounce:

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

Retarget an interrupted settle from its live value. Keep dismissal available by keyboard and controls. Reduced motion should preserve direct manipulation while making release and return brief or instant.
