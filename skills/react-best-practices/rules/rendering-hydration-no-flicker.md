---
title: Prevent Theme Flicker Without Hydration Mismatch
impact: MEDIUM
impactDescription: keeps the first paint consistent with hydration
tags: rendering, ssr, hydration, theme, flicker
---

## Prevent Theme Flicker Without Hydration Mismatch

The server and the first client render must produce matching markup. A script
that changes a React-owned element between server rendering and hydration can
create a mismatch even if it removes a visible theme flash. React does not
guarantee that it will repair differing attributes during hydration.

**Incorrect (breaks SSR):**

```tsx
function ThemeWrapper({ children }: { children: ReactNode }) {
  // localStorage is not available on server - throws error
  const theme = localStorage.getItem('theme') || 'light'

  return (
    <div className={theme}>
      {children}
    </div>
  )
}
```

Server-side rendering will fail because `localStorage` is undefined.

**Incorrect (visual flickering):**

```tsx
function ThemeWrapper({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    // Runs after hydration - causes visible flash
    const stored = localStorage.getItem('theme')
    if (stored) {
      setTheme(stored)
    }
  }, [])

  return (
    <div className={theme}>
      {children}
    </div>
  )
}
```

Component first renders with default value (`light`), then updates after
hydration, causing a visible flash of incorrect content.

Prefer a theme value the server can know, such as a preference cookie. Render
the same value into the HTML and the client's initial props. After hydration,
later user changes can update both the UI and the cookie. If the system color
scheme is enough, CSS `prefers-color-scheme` avoids a client-storage read.

For example, have the framework's server entry read and validate the cookie,
then pass that same value to the client during hydration:

```tsx
import type { ReactNode } from 'react'

type Theme = 'light' | 'dark'

function ThemeShell({
  initialTheme,
  children,
}: {
  initialTheme: Theme
  children: ReactNode
}) {
  return <div data-theme={initialTheme}>{children}</div>
}
```

The server render and initial client render must receive the same
`initialTheme`. Wire up later user changes with the app's existing theme state
and cookie updates.

For a localStorage-only preference, the server cannot know the value. Choose
the tradeoff deliberately: use a framework-supported pre-paint theme script
only when it works with the app's Content Security Policy and hydration model,
or accept a post-hydration update. Do not copy a script that mutates a
React-owned element and claim it guarantees both no flicker and no mismatch.

Check the rendered first paint and hydration on a fresh load, with JavaScript
delayed, under the app's real CSP and theme choices.

References: [React hydration](https://react.dev/reference/react-dom/client/hydrateRoot),
[Next.js hydration errors](https://nextjs.org/docs/messages/react-hydration-error).
