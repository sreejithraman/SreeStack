---
title: Bound Repeated Storage Reads
impact: LOW-MEDIUM
impactDescription: avoids repeated synchronous reads in measured hot paths
tags: javascript, localStorage, storage, caching, performance
---

## Bound Repeated Storage Reads

Browser storage reads are synchronous. If a measured operation reads the same
value repeatedly, read it once for that operation:

```typescript
function exportRows(rows: Row[]) {
  // Called from a client-side user action.
  let format: 'json' | 'csv' = 'csv'
  try {
    if (localStorage.getItem('export-format') === 'json') format = 'json'
  } catch {
    // Storage can be blocked; keep the default.
  }
  return rows.map(row => formatRow(row, format))
}
```

This snapshot is intentionally short-lived. If many components need the value,
use the app's existing reactive state or store and keep it in sync with writes.
A longer-lived cache needs a complete invalidation path for same-tab writes,
other tabs, removals, and `clear()`; the `storage` event fires in other
documents, not the writer, and its key is `null` for `clear()`. Avoid a
module-level cache for session-dependent values or cookies whose changes the
app cannot observe reliably.

Read browser storage only on the client. In a server-rendered view, choose an
initial value that agrees with hydration or use an intentional post-hydration
path; see [theme hydration](rendering-hydration-no-flicker.md).

References: [Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API),
[storage event](https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event),
[StorageEvent](https://developer.mozilla.org/en-US/docs/Web/API/StorageEvent).
