# Drag to dismiss

Use for a draggable drawer, toast, or sheet whose motion can reverse while held. Keep the item attached to the pointer, then decide whether to dismiss or return.

## Track the active pointer

- Define the gesture's axis contract on the target and relevant ancestor chain
  before the gesture starts. A horizontal dismissal inside vertically scrolling
  content should allow `touch-action: pan-y pinch-zoom`; use the corresponding
  perpendicular pan value with `pinch-zoom` for a vertical dismissal inside a
  horizontal scroller. When scrolling and dismissal need the same axis, provide
  a dedicated handle or an explicit boundary policy instead of making both claim
  the whole surface.
- Track one initial pointer and ignore additional pointers. Wait for a small,
  tunable movement threshold before committing to a direction. Keep plausible
  directions unresolved until intent is clear. Record the grab offset on pointer
  down even when capture must wait.
- If no browser scroll can compete, capture the initial pointer on pointer down.
  Otherwise capture it only once dismissal wins. If perpendicular scrolling
  wins, leave the pointer to the browser and clear local gesture state. Do not
  use `touch-action: none` or cancel the browser's default behavior while
  scrolling remains a valid outcome.
- Handle `pointercancel` as browser or system takeover: release capture and clear
  the pressed or drag state without committing dismissal. Release capture on
  teardown. A second touch must not take over the drag.
- Write the dragged element's transform directly. Limit high-frequency style updates to the moving element.
- Apply rising resistance beyond bounds. Preserve the intended dismissal direction.

```js
// Choose X or Y from the axis contract; distance is signed toward dismissal.
element.style.transform = `translate${axis}(${distance}px)`;
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
