---
name: prototype
description: Build throwaway UI prototypes for web, mobile, or desktop. Use when the user wants to explore layouts, compare design options, or try a screen or interaction before choosing a design.
---

# Prototype

Build enough UI to answer a design question. Use the target platform and the
project's stack so the user can judge the design where it will run.

## 1. Set the scope

Infer the screen, platform, and design question from the request and nearby code.
Ask only when a missing choice would change what you build. State the question,
where the prototype will run, and which options you will compare.

Default to three variants; follow the user's count or single concept when given.
Make variants differ in layout, information hierarchy, navigation, or the main
interaction. Each should offer a clear design choice beyond color or copy.

## 2. Choose a home

Prefer the existing screen with its surrounding navigation, components, and
realistic content. A new section of a screen still belongs in that screen.
Use a separate prototype route, screen, preview, or development target when no
existing screen fits. Follow the project's conventions and clearly name prototype
files. Keep prototype entry points and controls out of release builds.

Match the platform:

- **Web:** use the existing route where possible. A `?variant=` parameter makes
  each option easy to reopen and share.
- **Mobile:** use the app's UI framework and run in a simulator, emulator, or
  device. A native preview works for layout; use the running app when judging
  navigation, gestures, keyboard behavior, or system UI.
- **Desktop and other platforms:** use the app's normal window or preview host,
  with the input methods and window sizes relevant to the question.

For a native app, use a browser mockup only when the user asks for one or accepts
it as a fallback. If target tooling is missing, explain what blocks the native
preview and what the fallback would let them judge.

## 3. Build the variants

Use the project's design system and components. Keep each variant's layout free
to differ; share stable controls and fixtures where useful.

Use the same representative content across variants, including relevant empty,
loading, or crowded states. Reuse safe read-only data access where it helps.
Stub writes and keep interaction state in memory. Add only enough behavior to
try the flow; keep backend integration out of the prototype.

Spend effort on what the user is judging: hierarchy, spacing, touch targets,
safe areas, keyboard overlap, or window resizing as the platform requires.
Keep the code disposable, with only enough error handling to run reliably.
Skip automated tests for throwaway variants; verify them by running them.

## 4. Make comparison easy

Provide one shared development control with a clear variant label and a way to
move between options without rebuilding. Keep it distinct from the design and
clear of the content and controls under review. For a single concept, omit the
variant switcher.

- **Web:** a floating switcher can update `?variant=` through the router.
  Optional arrow-key shortcuts must leave text inputs and other keyboard
  controls alone.
- **Mobile:** use a debug menu, sheet, or compact native picker. Respect safe
  areas and avoid taking over app gestures or covering bottom navigation.
- **Desktop:** use a development menu or toolbar suited to the app.

Keep the same sample state when switching where practical. If variants need
different navigation or state, reset to a known starting point and make the
reset clear. Include a short name that explains each option's design choice.

## 5. Run and show it

Run each variant on the target platform and try the interactions that answer the
question. Check that switching works and the comparison control stays out of the
way. State any behavior you could not verify.

Use `showroom` for web and iOS handoff. For other platforms, provide a screenshot
or recording from the running prototype and the exact steps to open it. Give the
user the run command or build target, screen, and variant controls needed to
return to it. Screenshots should identify the variant they show.

Briefly explain the tradeoff each option tests. Leave the design choice open
until the user picks one or asks you to choose; combine parts when requested.

## 6. Record the decision

Once the user chooses, record which design won and why. Preserve the variants
on a throwaway branch, out of main, with enough run steps to revisit them. Keep
the branch pointer and verdict in the handoff or an authorized implementation
issue update.

When implementation is in scope, apply the chosen design with the project's
normal quality checks. Remove prototype controls and unused variants from the
production change. A prototype request alone ends with a reviewable prototype;
it does not call for shipping the design.
