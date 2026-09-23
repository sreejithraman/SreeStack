---
name: react-best-practices
description: "Use for React or Next.js performance work: waterfalls, bundle size, server rendering, data fetching, or re-renders."
---

# React Best Practices

Performance patterns for React and Next.js applications. The 68 rules are
candidates, not a checklist or a promise of impact. Locate the bottleneck in
the actual workload before changing code. Check the project's React, Next.js,
compiler, and data-layer choices; compare the same workload before and after.

## When to Apply

Reference these guidelines when:

- Eliminating waterfalls in data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring React/Next.js for load time or re-renders
- Optimizing bundle size or load times

## Rule Categories

| Category | Prefix |
|----------|--------|
| Eliminating Waterfalls | `async-` |
| Bundle Size Optimization | `bundle-` |
| Server-Side Performance | `server-` |
| Client-Side Data Fetching | `client-` |
| Re-render Optimization | `rerender-` |
| Rendering Performance | `rendering-` |
| JavaScript Performance | `js-` |
| Advanced Patterns | `advanced-` |

## How to Use

1. From the category table, pick the prefixes that match the measured bottleneck or the current task; when this skill is a review reference, use the diff.
2. Open only the Quick Reference links whose ids start with those prefixes and whose one-liners match the request, or the diff when this skill is a review reference.
3. When this skill is a review reference, report findings from the opened files and leave edits to the parent. Otherwise apply only rules that fit the project's versions and existing architecture. The one-liners are only for choosing which files to open.

Rule files provide the relevant rationale, examples, tradeoffs, and references.

## Quick Reference

### Eliminating Waterfalls

- [`async-cheap-condition-before-await`](rules/async-cheap-condition-before-await.md) - Check cheap sync conditions before awaiting flags or remote values
- [`async-defer-await`](rules/async-defer-await.md) - Move await into branches where actually used
- [`async-parallel`](rules/async-parallel.md) - Use Promise.all() for independent operations
- [`async-dependencies`](rules/async-dependencies.md) - Use better-all for partial dependencies
- [`async-api-routes`](rules/async-api-routes.md) - Start promises early, await late in API routes
- [`async-suspense-boundaries`](rules/async-suspense-boundaries.md) - Use Suspense to stream content

### Bundle Size Optimization

- [`bundle-barrel-imports`](rules/bundle-barrel-imports.md) - Avoid barrel-file import cost
- [`bundle-analyzable-paths`](rules/bundle-analyzable-paths.md) - Prefer statically analyzable import and file-system paths to avoid broad bundles and traces
- [`bundle-dynamic-imports`](rules/bundle-dynamic-imports.md) - Use next/dynamic for heavy components
- [`bundle-defer-third-party`](rules/bundle-defer-third-party.md) - Load analytics/logging after hydration
- [`bundle-conditional`](rules/bundle-conditional.md) - Load modules only when feature is activated
- [`bundle-preload`](rules/bundle-preload.md) - Preload on hover/focus for perceived speed

### Server-Side Performance

- [`server-auth-actions`](rules/server-auth-actions.md) - Authenticate server actions like API routes
- [`server-cache-react`](rules/server-cache-react.md) - Use React.cache() for per-request deduplication
- [`server-cache-lru`](rules/server-cache-lru.md) - Scope and invalidate cross-request caches of shared data
- [`server-dedup-props`](rules/server-dedup-props.md) - Avoid duplicate serialization in RSC props
- [`server-hoist-static-io`](rules/server-hoist-static-io.md) - Hoist static I/O (fonts, logos) to module level
- [`server-no-shared-module-state`](rules/server-no-shared-module-state.md) - Avoid module-level mutable request state in RSC/SSR
- [`server-serialization`](rules/server-serialization.md) - Minimize data passed to client components
- [`server-parallel-fetching`](rules/server-parallel-fetching.md) - Restructure components to parallelize fetches
- [`server-parallel-nested-fetching`](rules/server-parallel-nested-fetching.md) - Chain nested fetches per item in Promise.all
- [`server-after-nonblocking`](rules/server-after-nonblocking.md) - Use after() for non-blocking operations

### Client-Side Data Fetching

- [`client-swr-dedup`](rules/client-swr-dedup.md) - Use existing SWR caching for request deduplication
- [`client-passive-event-listeners`](rules/client-passive-event-listeners.md) - Use passive listeners for scroll
- [`client-localstorage-schema`](rules/client-localstorage-schema.md) - Version and minimize localStorage data

### Re-render Optimization

- [`rerender-defer-reads`](rules/rerender-defer-reads.md) - Don't subscribe to state only used in callbacks
- [`rerender-memo`](rules/rerender-memo.md) - Extract expensive work into memoized components
- [`rerender-memo-with-default-value`](rules/rerender-memo-with-default-value.md) - Hoist default non-primitive props
- [`rerender-dependencies`](rules/rerender-dependencies.md) - Use primitive dependencies in effects
- [`rerender-derived-state`](rules/rerender-derived-state.md) - Subscribe to derived booleans, not raw values
- [`rerender-derived-state-no-effect`](rules/rerender-derived-state-no-effect.md) - Derive state during render, not effects
- [`rerender-functional-setstate`](rules/rerender-functional-setstate.md) - Use functional setState for stable callbacks
- [`rerender-lazy-state-init`](rules/rerender-lazy-state-init.md) - Pass function to useState for expensive values
- [`rerender-simple-expression-in-memo`](rules/rerender-simple-expression-in-memo.md) - Avoid memo for simple primitives
- [`rerender-split-combined-hooks`](rules/rerender-split-combined-hooks.md) - Split hooks with independent dependencies
- [`rerender-move-effect-to-event`](rules/rerender-move-effect-to-event.md) - Put interaction logic in event handlers
- [`rerender-transitions`](rules/rerender-transitions.md) - Use startTransition for non-urgent updates
- [`rerender-use-deferred-value`](rules/rerender-use-deferred-value.md) - Defer expensive renders to keep input responsive
- [`rerender-use-ref-transient-values`](rules/rerender-use-ref-transient-values.md) - Use refs for transient frequent values
- [`rerender-no-inline-components`](rules/rerender-no-inline-components.md) - Don't define components inside components

### Rendering Performance

- [`rendering-animate-svg-wrapper`](rules/rendering-animate-svg-wrapper.md) - Animate div wrapper, not SVG element
- [`rendering-content-visibility`](rules/rendering-content-visibility.md) - Use content-visibility for long lists
- [`rendering-hoist-jsx`](rules/rendering-hoist-jsx.md) - Extract static JSX outside components
- [`rendering-svg-precision`](rules/rendering-svg-precision.md) - Reduce SVG coordinate precision
- [`rendering-hydration-no-flicker`](rules/rendering-hydration-no-flicker.md) - Keep theme first paint and hydration consistent
- [`rendering-hydration-suppress-warning`](rules/rendering-hydration-suppress-warning.md) - Suppress expected mismatches
- [`rendering-activity`](rules/rendering-activity.md) - Use Activity component for show/hide
- [`rendering-conditional-render`](rules/rendering-conditional-render.md) - Use ternary, not && for conditionals
- [`rendering-usetransition-loading`](rules/rendering-usetransition-loading.md) - Prefer useTransition for loading state
- [`rendering-resource-hints`](rules/rendering-resource-hints.md) - Use React DOM resource hints for preloading
- [`rendering-script-defer-async`](rules/rendering-script-defer-async.md) - Use defer or async on script tags

### JavaScript Performance

- [`js-batch-dom-css`](rules/js-batch-dom-css.md) - Group CSS changes via classes or cssText
- [`js-index-maps`](rules/js-index-maps.md) - Build Map for repeated lookups
- [`js-cache-property-access`](rules/js-cache-property-access.md) - Cache object properties in loops
- [`js-cache-function-results`](rules/js-cache-function-results.md) - Scope caches for repeated pure calculations
- [`js-combine-iterations`](rules/js-combine-iterations.md) - Combine multiple filter/map into one loop
- [`js-length-check-first`](rules/js-length-check-first.md) - Check array length before expensive comparison
- [`js-early-exit`](rules/js-early-exit.md) - Return early from functions
- [`js-hoist-regexp`](rules/js-hoist-regexp.md) - Hoist RegExp creation outside loops
- [`js-min-max-loop`](rules/js-min-max-loop.md) - Use loop for min/max instead of sort
- [`js-set-map-lookups`](rules/js-set-map-lookups.md) - Use Set/Map for O(1) lookups
- [`js-tosorted-immutable`](rules/js-tosorted-immutable.md) - Use toSorted() for immutability
- [`js-flatmap-filter`](rules/js-flatmap-filter.md) - Use flatMap to map and filter in one pass
- [`js-request-idle-callback`](rules/js-request-idle-callback.md) - Defer non-critical work to browser idle time

### Advanced Patterns

- [`advanced-effect-event-deps`](rules/advanced-effect-event-deps.md) - Don't put `useEffectEvent` results in effect deps
- [`advanced-event-handler-refs`](rules/advanced-event-handler-refs.md) - Store event handlers in refs
- [`advanced-init-once`](rules/advanced-init-once.md) - Initialize app once per app load
- [`advanced-use-latest`](rules/advanced-use-latest.md) - useEffectEvent for stable callback refs
