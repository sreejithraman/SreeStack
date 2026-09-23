---
title: Cache Repeated Function Calls
impact: MEDIUM
impactDescription: avoid redundant computation
tags: javascript, cache, memoization, performance
---

## Cache Repeated Function Calls

Cache a pure calculation when profiling shows repeated work. Keep the cache at
the narrowest useful lifetime: a render or request for user data, and a bounded
module cache only for stable, non-sensitive inputs. React Compiler may already
memoize calculations inside components and hooks. The example below only avoids
duplicate names within one render; its `Map` is rebuilt on the next render and
may cost more than it saves when most names are unique.

**Incorrect (redundant computation):**

```typescript
function ProjectList({ projects }: { projects: Project[] }) {
  return (
    <div>
      {projects.map(project => {
        // slugify() called 100+ times for same project names
        const slug = slugify(project.name)

        return <ProjectCard key={project.id} slug={slug} />
      })}
    </div>
  )
}
```

**Correct (deduplicate within this render):**

```typescript
function ProjectList({ projects }: { projects: Project[] }) {
  const slugs = new Map<string, string>()
  return (
    <div>
      {projects.map(project => {
        let slug = slugs.get(project.name)
        if (slug === undefined) {
          slug = slugify(project.name)
          slugs.set(project.name, slug)
        }

        return <ProjectCard key={project.id} slug={slug} />
      })}
    </div>
  )
}
```

If the same input array stays stable across renders and React Compiler is not
handling this calculation, compare a component-level `useMemo` against the
uncached version. Do not keep login, permission, or request-derived results in
a module cache.

Reference: [How we made the Vercel Dashboard twice as fast](https://vercel.com/blog/how-we-made-the-vercel-dashboard-twice-as-fast)
