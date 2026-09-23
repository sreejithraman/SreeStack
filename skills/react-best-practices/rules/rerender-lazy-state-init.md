---
title: Use Lazy State Initialization
impact: MEDIUM
impactDescription: wasted computation on every render
tags: react, hooks, useState, performance, initialization
---

## Use Lazy State Initialization

Pass a function to `useState` for expensive initial values. Without the function form, the initializer runs on every render even though the value is only used once.

**Incorrect (runs on every render):**

```tsx
function Editor() {
  // The initial draft is rebuilt on every render but used only once.
  const [draft, setDraft] = useState(createEmptyDraft())
  return <DraftEditor draft={draft} onChange={setDraft} />
}
```

**Correct (defers creation to initialization):**

```tsx
function Editor() {
  // The draft is created for initialization, not every update.
  const [draft, setDraft] = useState(() => createEmptyDraft())
  return <DraftEditor draft={draft} onChange={setDraft} />
}
```

Use lazy initialization for expensive, pure initial state. If a value must
follow changing props, derive it during render or memoize the calculation
instead of freezing it in state. In server-rendered apps, the initializer also
runs during server rendering: DOM or browser-storage reads can throw or produce
a different first client render and a hydration mismatch. Use a server-provided
initial value or an intentional client-only/post-hydration path for that data.
React Strict Mode may call an initializer twice in development, so it must stay
pure ([React `useState`](https://react.dev/reference/react/useState)).

For simple primitives (`useState(0)`), direct references (`useState(props.value)`), or cheap literals (`useState({})`), the function form is unnecessary.
