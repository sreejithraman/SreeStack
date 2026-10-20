---
name: showroom
description: "Use when work produces something the user can inspect or try, or during UI iteration to show progress. Choose and deliver demonstrations and access suited to the work, the user's next step, and available tools."
---

# Showroom

Help the user experience and judge the result. Choose how to show it and how
to make it available, using the task, environment, and user's preferences.
This applies to interfaces, commands, services, generated files, and other
inspectable results.

`verify` owns acceptance checks and their judgments. Reuse its current evidence
and selected environment when they fit; use it when broader workflow checking
is needed. Showroom owns the demonstration and access at handoff and during
iteration. A demonstration supports only the behavior actually observed.

## Choose the showing

Decide what would help the user assess the work and what would let them try it.
Inspect existing run artifacts, available tools, running services, and suitable
devices before choosing. Follow explicit format and target requests; otherwise
make the choice without asking the user to select a medium.

Read the matching [delivery guidance](references/delivery.md) before selecting
access. Website work always follows its preview-link requirement.

Choose formats for what they communicate. These are examples, not a ranking:

- Screenshots make appearance and individual states easy to inspect.
- A collage or contact sheet makes states, variants, or before/after views
  easy to compare; retain access to the full-size images.
- Video shows timing, gestures, transitions, and connected interactions.
- A checked URL lets the user explore a website themselves.
- A development install puts an app on an available device, including the
  user's iPhone, when hands-on use is valuable.
- A runnable command, request and response, or sample session shows nonvisual
  behavior. An accessible generated file lets the user inspect the artifact.

Combine formats when they answer different questions. During UI iteration,
use screenshots or video readily to make feedback concrete, even when a link
or installed build also provides access. Choose enough context to judge the
change; optimize for understanding rather than artifact count.

A document or configuration edit may be best shown through a direct file link
and a focused explanation. Match the showing to the work instead of creating
media for its own sake. Reuse suitable evidence while its revision, setup,
and state still match. Read [captures](references/captures.md) when producing
visual media.

## Exercise and inspect

Reach the changed behavior through the real interface or public entry point.
Use the project's run path and the host's browser, device, or terminal routing.
For web and iOS tools, follow Verify's
[web](../verify/references/web.md) and [iOS](../verify/references/ios.md) routing;
delivery target choices follow [delivery](references/delivery.md).

Confirm the current changes are present. Inspect each artifact as delivered:
open the URL or file, view the saved media, or run the example. Use safe sample
data and remove secrets or private content from evidence. A loading screen,
stale build, home screen, or fabricated output cannot stand in for the result.

When a chosen route is unavailable, use another suitable format if it still
helps, and label the gap. Preserve explicit target requirements and distinguish
secondary evidence from checks on that target. Report the exact blocker when
the result cannot be shown or made accessible.

## Handoff

Present the selected media, links, artifacts, or runnable examples in the reply.
Explain what the user is seeing and how to reach or try the changed behavior.
For images and video, use absolute paths so the host can render them; link
generated files directly. Include the full-size sources for composite media.

State relevant access requirements, availability limits, and untested behavior.
Keep services needed for the user's inspection running, and record ownership
and exact stop actions as described in [delivery](references/delivery.md).
Finish when the user can inspect the result and use the offered access path,
or the handoff clearly identifies what remains unavailable and why.
