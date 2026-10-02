---
name: koubou
description: Design and iterate on App Store screenshots with Koubou. Use when creating or redesigning store screenshots, framing existing app captures, or changing their copy, layout, device size, or localization.
---

# Koubou

Build a screenshot campaign from the app's actual visual language and useful
content. Use HTML/CSS templates, real device frames, and measured output.
Each slide communicates one concrete benefit. User direction sets the scope
and style; readability, honest product claims, and correct canvas geometry
remain the quality bar.

## Read the app and settle the story

1. Read [style intake](references/style-intake.md). Inspect the app, captures,
   icon, assets, UI tokens, product docs, and existing marketing before asking
   for direction. Summarize the palette, contrast, density, typography, tone,
   and distinctive motifs that should carry into the campaign.
2. Resolve only material uncertainty using the
   [style interview](references/style-interview.md). Reuse answers and references
   already supplied. Establish the audience, main benefit, requested slides,
   target devices, and any localization. When captures are missing or weak,
   capture useful app states with the project's documented run path and the
   host's available device tools. Check assets' redistribution terms and retain
   their required notices.
3. Read the [design guide](references/design-guide.md). Draft the slide story
   and two or three copy options before CSS. Choose useful, realistic app
   content that makes each claim visible. Keep the app UI accurate.
4. Record the campaign direction: product signals, style, copy voice,
   backgrounds, device composition, and variation across slides. Ground each
   choice in the app or user direction. For a full set, vary the first three
   compositions; repeated upright centered phones are a weak default.
   For step-by-step work, finish one requested slide and return its checked
   preview before expanding the set.

## Prepare and compose

1. Use the project's existing Koubou installation, including a virtual
   environment when present. Follow [setup](references/setup.md); prepare HTML
   support with `kou setup-html`. Linking this skill does not install the CLI.
2. Read [YAML configuration](references/yaml-reference.md). Keep configuration,
   templates, and source captures in the app repo's established location;
   respect its ignored-output and machine-specific configuration rules.
3. Select the real device with `kou list-frames`, read `project.device` and
   `project.output_size`, and inspect its geometry before writing CSS:
   `kou inspect-frame "<device>" --output-size <size> --output json`.
   Use the returned screen bounds, margins, orientation, and canvas class.
4. Plan the text and device zones. Write HTML/CSS that fits the actual canvas,
   copy length, and frame proportions. In HTML, annotate each headline, any
   supporting copy, and the primary device when present with `data-kou-id`
   and `data-kou-role` so the output can
   be measured. Use the design guide's canvas-specific typography and scale.
   For highlights, zoom callouts, gradients, or content-mode composition,
   consult [capabilities](references/capabilities-reference.md).
5. For each checked export, use a fresh, empty, ignored `project.output_dir`;
   preserve earlier accepted outputs. Scope a targeted export to the requested
   slides/languages. Generate with `kou generate <config.yaml> --output json`
   and retain stdout/stderr. Reject per-slide or per-language generation errors
   even if the CLI reports success. Verify every expected slide × language PNG
   and HTML sidecar was produced in this run; existing files alone are not proof
   (see YAML configuration). Use `kou live <config.yaml>`
   when the user wants to iterate in a live preview; read its
   [asset-watch limits](references/capabilities-reference.md#live-mode).
   Prefer the host's shared
   browser tools for inspecting it.

## Check and iterate

Read every generated slide at full resolution and thumbnail size. Account for
every requested language and slide from the current export. For HTML outputs, inspect each sibling
`*.layout.json`, using `layout_path` when reported, for objective bounds,
proportions, and mathematical overlaps. Judge appearance from the image.
Content-mode YAML does not emit HTML annotation sidecars: verify its configured
positions and inspected frame geometry against each PNG, and report that
element-level sidecar measurements were unavailable. Choose HTML when that
measured verification is required.

Apply the design guide's rejection checklist to every requested output:

- Copy is specific, readable, truthful, and supported by the visible app state.
- Device frame and screen align; cropping is intentional and useful.
- Text fits its zone, stays legible, and avoids unintended device overlap.
- Empty space, visual hierarchy, and composition serve the slide's benefit.
- A set has deliberate variation while keeping the app's visual identity.
- HTML layout sidecars contain the required annotated elements; empty sidecars
  require an annotation fix before claiming measured verification.

Fix and regenerate failed slides before presenting them. A successful renderer
exit is not design acceptance. Return the checked visual preview, full-size
output paths, and any verification gap. For follow-ups, change only the scope
requested and recheck the affected outputs. Uploading or publishing belongs to
the user's authorized release workflow.
