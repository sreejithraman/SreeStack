# Diagnosing existing UI

Use this reference for web surfaces. For native Apple UI, use
[Apple-platform visual design](apple-platforms.md).

Use this when an existing web interface looks wrong and the complaint does not
yet identify a cause. Inspect the rendered component with real content before
choosing a fix.

Treat each row as a hypothesis. Check its cause against the actual hierarchy,
styles, and content; apply a candidate only when that evidence supports it.
Keep the change local and judge it against the original symptom and the
component's interaction and accessibility contracts.

| Symptom | Possible cause | Candidate change |
|---|---|---|
| Noisy, chaotic, "wall of content", nothing draws the eye | Everything has equal weight | De-emphasize secondary and tertiary content before increasing primary emphasis |
| One element won't stand out no matter what you do to it | Its neighbours are competing | Soften the competitors: fade inactive nav items, remove the sidebar's background so content sits forward |
| Cramped, claustrophobic | Groups and content compete for too little space | Increase space around the affected groups, then tighten to the product's density |
| Ambiguous grouping — which label goes with which field? which heading owns this paragraph? | Equal spacing inside and between groups | Give groups more space around them than within them. In multiline lists, separate items visibly more than wrapped lines within an item; check horizontal rows too |
| Busy, boxed-in, over-compartmentalized | Several cues repeat the same boundary | Try spacing, surface contrast, or a shadow in place of redundant decorative borders. Preserve cues needed to identify controls and states |
| Text on a colored panel looks faded, dull, or disabled | Grey text, or white at reduced opacity, on color | Hand-pick a color at the background's hue with adjusted saturation/lightness |
| Headline over a photo is unreadable at some sizes | The image is too dynamic, not the text | Semi-transparent overlay; or lower image contrast (+brightness to compensate); or desaturate + multiply a brand color; or a large-blur, zero-offset text-shadow used as a glow |
| Primary content too big *and* secondary content too small | Font size doing all the hierarchy work | Move the emphasis to weight (600/700) and color; pull sizes back toward the middle of the scale |
| Big red button for something that isn't the main action | Styled by semantics instead of hierarchy | Give destructive actions secondary or tertiary treatment; save the red primary button for the confirmation dialog |
| Page title feels oversized and dominates | Heading semantics were mistaken for required visual weight | Keep the correct heading level, then use a quieter, body-like visual size when the composition calls for it |
| Data reads like a database dump (`Name:`, `Email:`, `Phone:`) | Naive label/value pairs | Drop labels the format or context already implies; merge label into value ("3 bedrooms"); otherwise make the label visibly secondary |
| Icon next to text overpowers it | Solid icons cover more surface area | Try a softer icon color while preserving required contrast for meaningful graphics |
| 1px border either invisible or harsh | Trying to solve weight with color | Keep the soft color, go to 2px |
| Large icons look chunky and crude | Small-format icon geometry was scaled too far | Render near the icon's intended size and use a surrounding shape when it needs more presence |
| Screenshot is an unreadable mush of tiny detail | Full-size screenshot scaled down | Screenshot a smaller (tablet) viewport, or crop to one region, or draw a simplified illustration of the UI |
| Logo turns to mush as a favicon | Detailed artwork scaled down | Redraw a simplified version at the target size |
| Layout spread thin across a huge viewport | Filling the screen because it's there | Use only the width the content needs. Or split into columns rather than stretching |
| Sidebar too wide on big screens, truncating on small | Percentage width from a grid | Fixed width for the sidebar; main content flexes |
| Mobile headline enormous | Desktop type scale exceeds the available measure | Tune fluid bounds or responsive type roles against actual wrapping; large and small text need not scale proportionally |
| Mixed font sizes on one line look misaligned | Vertically centered | `align-items: baseline` |
| All-caps label hard to read | Default letter-spacing is tuned for sentence case | Add ~0.05em letter-spacing |
| Every link is colored and it's overwhelming | Prose link styling dominates a link-dense UI | Use quieter but recognizable link treatment; keep links discoverable without hover and retain visible keyboard focus |
| Long centered paragraphs are hard to read | Centering obscures a steady reading edge | Use start alignment, or shorten the copy when centered composition serves the task |
| Numeric table columns hard to compare | Left-aligned numbers | Right-align them |
| Justified text has rivers of whitespace | No hyphenation | `hyphens: auto`, or don't justify |
| Flat, plain, "nothing wrong but nothing right" | No visual accents anywhere | Add one role-specific accent: a border, section background, restrained two-hue gradient, low-contrast pattern, or geometric shape |
| Feels unfinished / prototype-y | Defaults and custom styling are mixed without a system | Keep native controls when they fit; apply a coherent type, spacing, color, and focus system; customize controls only when their complete interaction and access behavior can be preserved |
| Screen is blank for new users | No first-use path | Explain the next useful action with a clear headline and call to action; add imagery when it helps. Suppress unavailable setup-only controls, but preserve filters or search needed to recover from zero results |
| A component looks generic | Familiar composition hides the content's relationships | Consider the [component composition](web.md#component-composition) alternatives when they improve the task |
| Elements look pasted onto the page | Everything is in its own rectangle | Overlap layers: negative margins so a card straddles two backgrounds, or extends past its parent's edges |
| Overlapping images clash | No separation between them | Give them a border matching the page background — an "invisible border" that guarantees a gap |
| User avatars/thumbnails lose their shape | Image background matches the UI background | Subtle inset box shadow (`inset 0 0 0 1px hsla(0,0%,0%,.1)`), not a border — borders clash with the image colors |
| User-uploaded images wreck the grid | Media geometry depends on the incoming image | Use [stable media boxes](techniques.md#stable-media-boxes); choose cropping or containment according to the content |
| Chart unreadable for colorblind users | Series distinguished only by hue | Combine lightness/contrast with labels, shapes, patterns, or position; give color-coded metrics a secondary cue |

For list grouping, judge the combined line-height and inter-item spacing. With
24px line-height and otherwise unspaced items, an added 8px gap gives about 32px
between baselines across an item boundary, versus 24px within a wrapped item.
The CSS gap itself need not exceed line-height. See [gaps between boxes](https://drafts.csswg.org/css-align-3/#gaps).

Measure meaningful control and state cues against [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
For a supported diagnosis, continue with the matching [web visual system](web.md),
[layout](web-layout.md), or [behavior](web-behavior-and-accessibility.md) branch
and verify the affected states.
