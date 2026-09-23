---
title: Use SWR for Automatic Deduplication
impact: MEDIUM-HIGH
impactDescription: automatic deduplication
tags: client, swr, deduplication, data-fetching
---

## Use SWR for Automatic Deduplication

When the project already uses SWR, its shared cache can deduplicate requests
across component instances. In other projects, use the existing data-fetching
layer's equivalent before adding a new dependency just for deduplication.

**Incorrect (no deduplication, each instance fetches):**

```tsx
function ProductList() {
  const [products, setProducts] = useState([])
  useEffect(() => {
    fetch('/api/public-products')
      .then(r => r.json())
      .then(setProducts)
  }, [])
}
```

**With SWR (multiple instances share one request):**

```tsx
import useSWR from 'swr'

function ProductList() {
  const { data: products } = useSWR('/api/public-products', fetcher)
}
```

For session-dependent responses, include every response-affecting identity,
tenant, and permission boundary in the cache key. Partition or clear affected
entries when the session or authorization changes. A shared key must not serve
one caller's cached data to another with different access.

Reference: [https://swr.vercel.app](https://swr.vercel.app)
