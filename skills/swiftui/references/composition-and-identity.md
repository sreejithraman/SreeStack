# Composition and Identity

## Compose by responsibility

Keep `body` declarative and quick to evaluate. Move side effects, data access,
formatting with material cost, and business decisions into the feature owner or a
focused helper. A semantic subview should have a clear job and a narrow interface.

Use native layout and container types before building custom infrastructure. Keep
modifier order intentional because layout, drawing, hit testing, accessibility,
and effects compose in order.

## Preserve identity

SwiftUI associates state and lifetime with view identity. Keep the structural
position and explicit identity of a stateful view stable across ordinary updates.
Use an explicit `id` reset only when discarding that state is the intended result.

For collections, use identifiers that represent the domain item across insertions,
deletions, sorting, and refreshes. Array offsets, a newly generated UUID during
each render, and mutable display text do not provide stable identity. If duplicate
values are valid, the value itself is not a unique identifier.

Make conditional branches represent real structural alternatives. When only a
property changes, prefer a stable view with a conditional value or modifier so
focus, scroll position, task lifetime, and local state remain attached to the same
identity.

## Control update cost

After measurement identifies an expensive update, use Apple's
[SwiftUI performance guidance](https://developer.apple.com/documentation/xcode/understanding-and-improving-swiftui-performance)
to interpret it and reduce the dependency or work responsible:

- read only the observable properties a view renders;
- move repeated computation out of `body` or cache it at an owner with a valid
  invalidation rule;
- keep list identity stable; and
- prevent feedback loops in geometry, preference, and change handlers.

Prefer concrete view types. Add type erasure only at a boundary that genuinely
needs heterogeneous storage or return types.
