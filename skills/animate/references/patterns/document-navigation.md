# Document navigation

For occasional navigation between separate documents, a cross-document view
transition can bridge the page change while preserving the existing navigation.
Apply it only after the motion gate; ordinary navigation is the baseline.

```css
@media (prefers-reduced-motion: no-preference) {
  @view-transition { navigation: auto; }
}
```

Both same-origin documents must opt in, and the navigation must qualify for a
cross-document transition. See [Chrome: cross-document view transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document).
The default effect crossfades page snapshots; this recipe opts out for reduced
motion. A deliberately chosen short fade can remain for that preference, but test
its scale, repetition, and reading cost rather than treating all fades as exempt.

This enhances rendering; it does not replace routing, data loading, focus strategy,
or document semantics. Use [page side-by-side](page-side-by-side.md) for in-document
screen changes. Avoid applying competing native and scripted navigation effects.
Custom snapshot names and geometry need project-specific checks. Test same-origin
forward/back navigation, unsupported targets, failed navigation, reduced motion,
and pages whose header or focus must remain steady. Unsupported browsers should
navigate normally without delaying content.
