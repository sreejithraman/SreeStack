# Diagnosing existing UI

Use this reference for web surfaces. For native Apple UI, use
[Apple-platform visual design](apple-platforms.md).

Use this when the task is *improve this*, not *build this*. Complaints about UI are almost
always vague ("looks off", "feels cheap"). Each vague symptom maps to a small number of
specific, mechanical fixes.

Start near the top because those causes are common, then skip any hypothesis the
rendered interface does not support. The fixes are candidate moves; adapt them
to the platform, product system, content, and measured result.

| Symptom | What's actually wrong | Fix |
|---|---|---|
| Noisy, chaotic, "wall of content", nothing draws the eye | No hierarchy — everything has equal weight | Deliberately de-emphasize secondary and tertiary content. Don't amplify the primary |
| One element won't stand out no matter what you do to it | Its neighbours are competing | Soften the competitors: fade inactive nav items, remove the sidebar's background so content sits forward |
| Cramped, claustrophobic | Space was *added* until it stopped looking bad | Start over with far too much space, then remove until happy |
| Ambiguous grouping — which label goes with which field? which heading owns this paragraph? | Equal spacing inside and between groups | More space *around* a group than *within* it. Same bug in bullet lists (gap must exceed line-height) and horizontal rows |
| Busy, boxed-in, over-compartmentalized | Too many borders | Replace with a box shadow, two slightly different background colors, or just more spacing. If you have both a border and a background change, drop the border. Borders that *identify a control* (input outlines, checkbox edges) stay — and those need 3:1 |
| Text on a colored panel looks faded, dull, or disabled | Grey text, or white at reduced opacity, on color | Hand-pick a color at the background's hue with adjusted saturation/lightness |
| Headline over a photo is unreadable at some sizes | The image is too dynamic, not the text | Semi-transparent overlay; or lower image contrast (+brightness to compensate); or desaturate + multiply a brand color; or a large-blur, zero-offset text-shadow used as a glow |
| Primary content too big *and* secondary content too small | Font size doing all the hierarchy work | Move the emphasis to weight (600/700) and color; pull sizes back toward the middle of the scale |
| Big red button for something that isn't the main action | Styled by semantics instead of hierarchy | Give destructive actions secondary or tertiary treatment; save the red primary button for the confirmation dialog |
| Page title feels oversized and dominates | Heading semantics were mistaken for required visual weight | Keep the correct heading level, then use a quieter, body-like visual size when the composition calls for it |
| Data reads like a database dump (`Name:`, `Email:`, `Phone:`) | Naive label/value pairs | Drop labels the format or context already implies; merge label into value ("3 bedrooms"); otherwise make the label visibly secondary |
| Icon next to text overpowers it | Solid icons cover more surface area | Lower the icon's contrast (softer color) |
| 1px border either invisible or harsh | Trying to solve weight with color | Keep the soft color, go to 2px |
| Large icons look chunky and crude | Small-format icon geometry was scaled too far | Render near the icon's intended size and use a surrounding shape when it needs more presence |
| Screenshot is an unreadable mush of tiny detail | Full-size screenshot scaled down | Screenshot a smaller (tablet) viewport, or crop to one region, or draw a simplified illustration of the UI |
| Logo turns to mush as a favicon | Detailed artwork scaled down | Redraw a simplified version at the target size |
| Layout spread thin across a huge viewport | Filling the screen because it's there | Use only the width the content needs. Or split into columns rather than stretching |
| Sidebar too wide on big screens, truncating on small | Percentage width from a grid | Fixed width for the sidebar; main content flexes |
| Mobile headline enormous | `em`-based sizing carried over from desktop | Size independently per breakpoint. Large things shrink faster than small things |
| Mixed font sizes on one line look misaligned | Vertically centered | `align-items: baseline` |
| All-caps label hard to read | Default letter-spacing is tuned for sentence case | Add ~0.05em letter-spacing |
| Every link is colored and it's overwhelming | Link styling meant for prose, used in a link-dense UI | Emphasize with weight or a darker color instead; for truly ancillary links, style on hover only |
| Long centered paragraphs are hard to read | Center alignment past 2–3 lines | Left-align. Or rewrite the copy shorter so centering works |
| Numeric table columns hard to compare | Left-aligned numbers | Right-align them |
| Justified text has rivers of whitespace | No hyphenation | `hyphens: auto`, or don't justify |
| Flat, plain, "nothing wrong but nothing right" | No visual accents anywhere | Add one role-specific accent: a border, section background, restrained two-hue gradient, low-contrast pattern, or geometric shape |
| Feels unfinished / prototype-y | Defaults and custom styling are mixed without a system | Keep native controls when they fit; apply a coherent type, spacing, color, and focus system; customize controls only when their complete interaction and access behavior can be preserved |
| Screen is blank for new users | Empty state was an afterthought | Illustration + a clear headline + an emphasized call to action. Hide tabs/filters/search that do nothing until content exists |
| A component looks generic | Default mental model of the component | Break the box — multi-column dropdowns with icons and descriptions, tables with combined columns and inline images, radio groups as selectable cards |
| Elements look pasted onto the page | Everything is in its own rectangle | Overlap layers: negative margins so a card straddles two backgrounds, or extends past its parent's edges |
| Overlapping images clash | No separation between them | Give them a border matching the page background — an "invisible border" that guarantees a gap |
| User avatars/thumbnails lose their shape | Image background matches the UI background | Subtle inset box shadow (`inset 0 0 0 1px hsla(0,0%,0%,.1)`), not a border — borders clash with the image colors |
| User-uploaded images wreck the grid | Displayed at intrinsic aspect ratio | Fixed containers, `background-size: cover`, crop the overflow |
| Chart unreadable for colorblind users | Series distinguished by hue | Distinguish by lightness — shades of one color. Add icons/arrows to any color-coded metric |
