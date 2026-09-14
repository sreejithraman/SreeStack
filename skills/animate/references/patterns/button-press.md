# Button press

Use for brief feedback on a real press when motion passes the gate. Use the project’s `--ease-out` token; if absent, start with `cubic-bezier(0.23, 1, 0.32, 1)`.

```css
.button {
  transition: transform 160ms var(--ease-out);
}

.button:active {
  transform: scale(0.97);
}
```

Scaling a button also scales its label and icons. `:active` works for touch presses; gate any hover motion separately. For reduced motion, use instant color or another steady pressed state.
