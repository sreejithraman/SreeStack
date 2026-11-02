---
name: animate
description: "Design, implement, and tune web, SwiftUI, and UIKit interface motion. Use for motion on those platforms when deciding whether to animate, building or reviewing transitions, shaping gesture-driven motion, or honoring reduced-motion preferences."
---

# Animate

Use the platform's motion before designing your own.

1. Inspect the existing interaction, components, and supported platform versions.
2. Use the standard component and its behavior when it fits. Let the system own
   its timing, gestures, and presentation lifecycle.
3. For additional motion, prefer built-in effects, transitions, and presets.
4. Build custom motion only for a requirement those options cannot meet. Reuse
   the product's components, motion tokens, and dependencies.
5. Verify the affected interaction on the target platform, including rapid
   repetition, interruption, affected input methods, and reduced motion. Preserve
   controls, useful feedback, and the final state when motion is disabled or the
   preference changes during use.

Added motion should explain a change or provide useful feedback. Occasional
delight can fit when it leaves the task unblocked. Keep frequent interactions
quiet, useful content available, and reading surfaces steady. An instant state
change is a valid result.

On Apple platforms, native behavior includes Liquid Glass interaction and
morphing. Using framework animation APIs to recreate a standard interaction is
still custom work. Keep system defaults unless an observed problem requires a
change. Framework skills own component and material setup.

On the web, preserve the existing accessible component's behavior and use the
simplest suitable browser mechanism.

Read supporting guidance only when needed:

- [Apple motion pitfalls](references/apple-platforms.md) for app-owned motion,
  custom gestures, or reduced-motion handling beyond the system's behavior.
- [Web implementation checks](references/implementation.md) when adding or
  changing web motion. Read [tools and recipes](references/web.md) only when the
  component needs additional motion.
- [Web tuning](references/tuning.md) when an observed timing or feel problem
  needs correction. Reference values are starting points for added effects.

For a build or fix, implement and test. For a plan or review, report the proposal
or findings without editing the product. State any verification left untested.
