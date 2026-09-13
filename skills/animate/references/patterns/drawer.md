# Drawer or sheet

Use for a surface that enters from an edge. Travel by the drawer’s own dimension so the closed position tracks content size. Use the project’s drawer curve, or start with `--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1)`.

```css
.drawer {
  transform: translateY(0);
  transition: transform 500ms var(--ease-drawer);
}

.drawer[data-closed] {
  transform: translateY(100%);
}
```

The 500ms duration is a starting point for a large panel; tune it to size and use rate. Keep the existing dialog’s focus, keyboard, and exit behavior. Use an instant or short fade state for reduced motion.

For swipe dismissal, read [drag-to-dismiss](drag-to-dismiss.md). Suspend the timed transition while the pointer drives the drawer, then settle with a spring.
