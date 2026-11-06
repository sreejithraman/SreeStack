---
name: show-me
description: Use before changing a screen or anything you'll measure, when a visible result first works or changes, when you or the user ask about or choose anything visual, before any stop or report on a result the user can open, run, or view, and when the user asks to see something or take a preview down.
---

# Show Me

Put the work in front of the user so they can judge it from their phone. You need a
result that runs, renders, or opens. Leave media, links, output, or a build in the
thread. You are done when the user can open
everything you showed from their phone, or you have named what they can't open and
why.

## When to show

Show during the work, not only at the end:

- **Before you change a screen, or anything you'll measure:** capture the before
  state or baseline. For screens, use [captures](references/captures.md).
- **When the first version works.**
- **When a visible result changes.**
- **When you ask about anything visual:** put the choices side by side, stacked if
  they won't fit a phone. If they aren't built, use a labeled mock when looks can
  settle it, or [prototype](../prototype/SKILL.md) when it depends on how they behave.
- **At every stop:** a question, a blocker, a finished change, or a report.
- **When work will merge:** capture first, then post it after the merge. End that
  report at what landed, with no next steps or prompts.

One post can cover several of these. Describing a visible result doesn't show it. If
the table below gives you nothing to show, say why.

## Choose the form

Follow the form the user asks for. Otherwise check the run artifacts, tools, services,
and devices you already have, then choose without asking. Combine forms when they answer
different questions.

| The work | Show |
| --- | --- |
| How something looks | A screenshot |
| Several states, variants, or a before and after | A collage, with links to the full-size images |
| Timing, gestures, transitions, or a connected flow | A video |
| A mock, or a comparison or interaction images can't show | An inline HTML view, through the host's HTML preview tools |
| A website | A checked link, from [web sharing](references/web-sharing.md) |
| A native app the user should try by hand | A build on their device, from [device delivery](references/native-device-delivery.md) |
| A command, API, or service | The command, its setup, and its real output or before-and-after numbers |
| A file, document, or configuration | A link to the file by absolute path, with an excerpt or rendered view if that helps |

Put images and video in the reply with absolute paths, so the host renders them
inline. Read [captures](references/captures.md) before you make visual media.

## Show only what is real

- Reach the changed behavior through its real interface, using the project's run path
  and the host's browser, device, or terminal tools. For browsers, follow Verify's
  [web guide](../verify/references/web.md). For iOS, follow its
  [iOS guide](../verify/references/ios.md) and
  [Simulator Lifecycle](../simulator-lifecycle/SKILL.md).
- Confirm the current changes are present, then inspect each item as delivered. Open
  the link, view the saved image, or run the example. A loading screen, stale build,
  home screen, or made-up output doesn't count. A labeled mock of an unbuilt option is
  the one exception.
- Claim only the behavior you observed. `verify` owns pass and fail. Reuse its evidence
  while the revision, setup, and state still match.
- Use safe sample data. Remove secrets and private content from everything you show.
  Keep credentials out of commands and output, and name the approved setup instead.
- For an example that changes state, use test data the task allows, and describe the
  effect before you invite the user to rerun it.
- Routine development actions need no new approval. Publishing beyond a private preview,
  distributing a build, and live side effects each need their own authorization, and
  showing something grants none.
- If a form is unavailable, use another that still helps, and label the gap. If the
  user named a target, keep that target, and mark anything else as secondary evidence.

## Keep it reachable

Keep any server the user needs running after you hand off. Put its URL or port,
process identity, owner, lifetime, and exact stop action in your report, which is the
record for later. Stop a process only if a showing started it and its recorded identity
still matches. A reused service keeps its owner. To take a preview down, follow [web sharing](references/web-sharing.md#take-it-down).

## Report

Say what changed, what you decided, and how to open each item. Add what it needs to
work, such as a login, a network, or this Mac staying awake. Name what you didn't test.
Retire any request to the user that no longer applies.
