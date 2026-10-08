# Registered motion values

Use a typed custom property when several decorative values should follow one
state with the same easing. Keep actual action or progress state in the existing
component; this recipe coordinates visual feedback.

```css
@property --card-emphasis {
  syntax: "<number>";
  inherits: true;
  initial-value: 0;
}

.motion-card { --card-emphasis: 0; }
.motion-card:focus-within { --card-emphasis: 1; }
@media (hover: hover) and (pointer: fine) {
  .motion-card:hover { --card-emphasis: 1; }
}

.motion-card-icon {
  display: inline-block;
  rotate: calc(var(--card-emphasis) * 15deg);
}
.motion-card-accent {
  transform-origin: left;
  scale: calc(0.75 + var(--card-emphasis) * 0.25) 1;
  opacity: calc(0.5 + var(--card-emphasis) * 0.5);
}

@media (prefers-reduced-motion: no-preference) {
  .motion-card {
    transition: --card-emphasis 180ms var(--ease-out, ease-out);
  }
}
@media (prefers-reduced-motion: reduce) {
  .motion-card-icon { rotate: none; }
  .motion-card-accent { scale: none; }
}
```

Registration gives a custom property a type so it can interpolate. `syntax` and
`inherits` are required; typed registrations also need a computationally independent
`initial-value`. Choose inheritance deliberately: this specimen passes a number
to children, while an isolated local value should use `inherits: false`. Use a
component-specific name because registration has document scope. Other useful
types include `<length-percentage>` and `<angle>`.
See [CSS Properties and Values API](https://drafts.css-houdini.org/css-properties-values-api-1/#at-property-rule).

Transforms need a transformable box, so give inline icons `inline-block` or another
appropriate display type. A script may write the property while CSS owns timing,
but gesture feedback should still track input directly and follow the skill’s
interruption rules. Without registration support, the explicit baseline and state
values still work and can change instantly. The reduced-motion path preserves
emphasis without rotation or scaling. Profile style recalculation on the real
subtree; registering or inheriting a value is not a performance guarantee.
