---
title: Cross-Request LRU Caching
impact: HIGH
impactDescription: caches across requests
tags: server, cache, lru, cross-request
---

## Cross-Request LRU Caching

`React.cache()` is scoped to one request. A process-local LRU can avoid repeated
work across requests for shared, non-sensitive data. Check the framework's
cache facilities first. Cache only when the key, authorization scope,
staleness window, and invalidation policy are explicit. A process-local cache
is not shared across instances or guaranteed to survive restarts.

**Implementation:**

```typescript
import { LRUCache } from 'lru-cache'

const cache = new LRUCache<string, any>({
  max: 1000,
  ttl: 5 * 60 * 1000  // 5 minutes
})

// Each published version is immutable and remains public for the TTL.
export async function getPublishedConfig(version: string) {
  const cached = cache.get(version)
  if (cached) return cached

  const config = await db.publishedConfig.findUnique({
    where: { version }
  })
  if (config) cache.set(version, config)
  return config
}

// Request 1: DB query, result cached
// Request 2: cache hit, no DB query
```

Use when measured sequential requests need the same immutable public data and
the chosen TTL is acceptable. If access or content can change during the TTL,
use guaranteed invalidation or a cache with the required consistency guarantees.
Keep user-specific or authorization-dependent data in a
request-scoped cache unless the application has a reviewed access-aware cache
design; a user ID alone is not an authorization boundary.

**With Vercel's [Fluid Compute](https://vercel.com/docs/fluid-compute):** LRU caching is especially effective because multiple concurrent requests can share the same function instance and cache. This means the cache persists across requests without needing external storage like Redis.

**In traditional serverless:** Instances do not share process memory, though a
warm instance may serve later invocations. Treat a local LRU as an opportunistic
hit; use a shared store when cross-instance cache hits or consistency matter.

Reference: [https://github.com/isaacs/node-lru-cache](https://github.com/isaacs/node-lru-cache)
