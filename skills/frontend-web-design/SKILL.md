---
name: frontend-web-design
description: Web interface art direction, component behavior, and accessibility implementation. Use only for websites and web apps when creating or substantially reshaping a visual identity; building or reviewing component feedback, loading, empty, error, overflow, interruption, or repeated-input behavior; or working on keyboard, focus, semantics, and accessible status behavior. Use refactoring-ui for routine visual-system cleanup.
---

# Frontend Web Design

Choose the branch the request needs. For a new or substantially reshaped visual
identity, follow the art-direction guidance and process through restraint and
self-critique. For component interaction work, preserve the product's visual
direction and follow [Component behavior](#component-behavior), plus
[Access and input](#access-and-input) for affected access paths. For narrow
accessibility work, go directly to Access and input. Combine art direction with
the implementation branches only when the requested scope includes both.

Choose the task mode before applying a branch. For an authorized build or fix,
implement the smallest change that satisfies the branch. For a plan or review,
leave the product unchanged and report each location, current behavior, exact
change, and check the implementation must pass. Treat branch completion rules as
the plan or review's acceptance criteria, not as evidence that unrun checks pass.

For art-direction work, approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in your memory about the client's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a toy for girls aged 8–11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:
- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

When the design includes motion, use `animate` to decide whether it belongs and
to implement its timing, interruption, input, and reduced-motion behavior.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: plan, review against the brief, build, critique

Where the brief pins down a visual direction, follow it exactly — the brief's own words always win. As with a hired human designer, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles.
- Color: describe the core base palette as 4–6 named hex values.
- Type: the typefaces and their roles.
- Layout: a layout concept, using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Include alignment guidance; should the content be left aligned, center aligned, justified?
- Principles: the high-level guidance for what makes this page unique.

This plan owns the brief-specific art direction and named palette anchors. Use
`refactoring-ui` to diagnose an existing interface or expand approved anchors
into full ramps, semantic roles, and a consistent component system. Preserve the
chosen direction instead of replacing it with starter values.

Then review that plan against the brief: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. For a build, start writing code only after confirming the revised plan. For a plan or review, hand off the revised direction, exact proposed changes, and required checks without implementing it.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and an element-based selector like .cta). This can happen often with padding/margin between sections.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it — a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creatives have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## Component behavior

Inspect the component's purpose, affected content or state, existing interaction
contract, input methods, and nearby patterns before changing it. Put controls
near what they affect and prefer familiar native behavior unless evidence
supports a different pattern.

- Give immediate, continuous feedback while input is active. Show status,
  completion, warnings, and errors where they matter.
- Start press feedback on pointer or key down, but commit the action only on a
  valid activation or release. Clear the pressed state when input cancels,
  leaves the allowed target, or becomes a drag.
- Keep loading, empty, disabled, error, and overflow behavior inside the
  component instead of relying on a happy-path page shell.
- Handle interruption and repeated input without stale work overwriting the
  current state. Keep the control usable while work is pending when the action
  safely permits it.
- Prefer strong defaults over adding options that avoid making a clear component
  decision.
- Use `animate` when feedback moves or transitions. This branch still owns the
  component's action, state model, and valid commit behavior. `animate` repeats
  the commit and cancellation boundary while it owns the moving feedback's
  purpose, timing, interruption, and reduced-motion path.
- Exercise the real component through its affected pointer, touch, and keyboard
  paths, including rapid repeat, interruption, and its non-happy states. Use
  `manual-verify` for hands-on evidence.

This branch is done when the component communicates each affected state at the
point of action and its main, interruption, repeated-input, and edge-state paths
pass on the real page.

## Access and input

For this branch, inspect the rendered interaction and its semantic representation.
For a build, implement the smallest native-element or semantic fix that covers
every affected state; for a plan or review, specify that fix without changing the
product. Exercise the complete keyboard and focus path and inspect names, roles,
values, states, relationships, status updates, and layout at the user's larger
text setting. Use `manual-verify` for hands-on evidence. Report a screen-reader or
announcement check as outstanding when the environment cannot run it.

- Prefer native elements and preserve clear names, roles, values, and states.
- Associate labels, help, validation, and errors with the controls they describe.
- Keep focus visible and ordered by the task. Every action must work from the
  keyboard without trapping focus.
- Expose async status, validation, and errors to assistive technology when the
  same change is visible but focus stays in place.
- Honor increased-contrast, forced-color, and reduced-transparency preferences
  where the environment exposes them. Replace blur with a more solid surface
  while preserving clear boundaries.
- Use `animate` when motion is in scope, including reduced-motion behavior and
  keeping controls usable while decorative motion runs.

This branch is done when every affected keyboard, focus, semantic, status, and
larger-text path passes on the real page, with a screen-reader check or a named
evidence gap.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.
