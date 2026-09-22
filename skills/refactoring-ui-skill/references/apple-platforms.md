# Apple-platform visual design

Use this branch for SwiftUI and UIKit. Start with the app's existing design system and standard platform components. Check the deployment target before choosing APIs, and prefer system behavior when custom styling would only recreate it.

## Hierarchy and layout

- Place the most important content early in reading order and give it enough space. Use alignment, indentation, grouping, and progressive disclosure to make relationships visible.
- Respect safe areas, system margins, readable-content guides, bars, sheets, and resizable-window behavior. Avoid importing web breakpoints or percentage-grid rules.
- Build an adaptive layout for supported orientations, window sizes, localization, right-to-left direction, and text sizes. Let content drive structural changes instead of identifying devices by model.
- Keep controls distinct from content. Prefer standard navigation, toolbar, list, form, sheet, and control appearances before replacing them with custom containers.

Apple's [Layout](https://developer.apple.com/design/human-interface-guidelines/layout) guidance covers grouping, visual hierarchy, safe areas, adaptability, Dynamic Type, localization, and window changes.

## Typography and scale

- Prefer semantic system text styles. Use weight and semantic foreground roles to refine hierarchy without replacing text styles with a fixed point-size ladder.
- Keep the number of typefaces and weights small. Avoid light weights for small interface text.
- In SwiftUI, use system `Font` styles and `@ScaledMetric(relativeTo:)` when custom geometry or icon sizing must scale with text.
- In UIKit, use preferred text-style fonts. Scale custom fonts and related metrics with `UIFontMetrics`.
- Test every supported Dynamic Type size. Preserve the relative hierarchy, allow useful text to wrap, and avoid truncating information merely to hold the original layout.

See Apple's [Typography](https://developer.apple.com/design/human-interface-guidelines/typography), SwiftUI [`ScaledMetric`](https://developer.apple.com/documentation/swiftui/scaledmetric), and UIKit [`UIFontMetrics`](https://developer.apple.com/documentation/uikit/uifontmetrics).

## Color and appearance

- Prefer semantic system colors for standard roles. Do not copy documented system color values into custom constants.
- Give custom colors semantic asset names and provide light, dark, and increased-contrast variants. Test them over every surface and material they actually use.
- Keep one meaning per color role. Do not reuse an interactive tint for unrelated decorative text.
- Use color as one cue, not the only cue. Preserve meaning for people who cannot distinguish the chosen hues.
- Measure contrast rather than judging it from a single screenshot. Recheck text, symbols, control outlines, separators that carry meaning, disabled states, and content over materials.

See Apple's [Color](https://developer.apple.com/design/human-interface-guidelines/color), [Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode), and [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) guidance.

## Depth, shape, and materials

- Use system materials and presentation layers to explain hierarchy. Do not port CSS shadow values directly to SwiftUI or UIKit.
- When custom elevation is necessary, define a small semantic scale and tune it on the rendered surface. Combine separation cues sparingly; a surface rarely needs a strong border, shadow, material, and background change at once.
- Keep corner treatment consistent with the component family and platform. Match container shapes, hit regions, clipping, and content backgrounds.
- Check legibility over translucent or variable materials in every supported appearance. Apparent material color can change with content and system settings.
- When Reduce Transparency is enabled, replace blur or translucent separation
  with a more opaque surface and preserve the boundary and hierarchy it conveyed.

Apple's [Materials](https://developer.apple.com/design/human-interface-guidelines/materials) guidance explains why material selection and contrast must be evaluated in context.

## Verification

For implemented interface work, run the actual screen in Simulator or on device.
For advisory work, apply the proposed roles and values to representative component
examples. Check what the requested scope makes available:

- Small and large supported windows or devices, rotation, safe areas, and keyboard presentation.
- Short, long, localized, and right-to-left content.
- Every supported Dynamic Type size, including accessibility sizes.
- Light, dark, and increased-contrast appearances.
- Reduced Transparency when the interface uses translucent materials.
- Default, selected, pressed, disabled, loading, empty, and error states that apply.
- Touch targets, spacing between controls, VoiceOver reading order, and any pointer or keyboard path the app supports.

Use Accessibility Inspector for contrast and representation checks when it is
available; otherwise report that manual check as outstanding. Inspect screenshots
at full size; a scaled-down overview can hide weak contrast, bad baselines, and
cramped controls.
