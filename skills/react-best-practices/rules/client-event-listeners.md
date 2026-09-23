---
title: Share Repeated Global Event Listeners
impact: LOW
impactDescription: can reduce duplicate handlers for the same global event
tags: client, event-listeners, subscription
---

## Share Repeated Global Event Listeners

When profiling shows many components doing duplicate work for the same global
event, give the listener one owner at the relevant app or feature boundary.
The browser can handle multiple listeners; their count alone is not a reason to
add a global registry or a new data-fetching dependency.

For related shortcuts owned by one feature, one effect can dispatch both:

```tsx
import { useEffect } from 'react'

function EditorShortcuts({
  save,
  closePreview,
}: {
  save: () => void
  closePreview: () => void
}) {
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key === 's') {
        event.preventDefault()
        save()
      } else if (event.key === 'Escape') {
        closePreview()
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [save, closePreview])

  return null
}
```

Mount this owner once for the feature. When distant components need to register
independent actions, use the project's existing shortcut or event manager. If
none exists and measured duplicate work warrants one, create a feature-owned
dispatcher. Keep each registration distinct, remove it on unmount, and scope
the single listener and callbacks to the same lifetime. If the project already
uses SWR subscriptions for this purpose, account for `SWRConfig` cache-provider
boundaries rather than pairing provider-scoped listeners with a module-global
callback map.

Reference: [SWR subscription](https://swr.vercel.app/docs/subscription),
[SWR cache providers](https://swr.vercel.app/docs/advanced/cache).
