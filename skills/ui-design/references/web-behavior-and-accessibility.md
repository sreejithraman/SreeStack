# Web behavior and accessibility

Use this branch for browser component behavior, semantics, input, state, and
accessibility. Preserve the product's visual direction unless visual design is
also in scope.

1. Inspect the rendered component, semantic tree, interaction contract,
   affected states, supported input methods, and nearby product patterns.
2. Prefer native HTML elements and browser behavior. When a custom component is
   justified, preserve the equivalent name, role, value, state, relationship,
   focus, and keyboard contract.
3. Associate labels, help, validation, and errors with the controls they
   describe. Keep focus visible and ordered by the task. Restore or move it
   deliberately after navigation or dismissal, and prevent keyboard traps.
4. Expose visible async status, validation, and errors to assistive technology
   when focus remains elsewhere.
5. Model loading, empty, disabled, error, overflow, cancellation, and
   interruption inside the component contract rather than relying on a
   happy-path page shell.
6. Start press feedback on pointer or key down, but commit only after a valid
   activation. Clear the pressed state when input cancels, leaves the allowed
   target, or becomes a drag.
7. Handle rapid and repeated input without stale work overwriting current
   state. Keep the control usable while work is pending when the action safely
   permits it.
8. Honor increased contrast, forced colors, reduced transparency, and larger
   text where the browser or operating system exposes them.
9. Exercise affected mouse, touch, keyboard, focus, and assistive-technology
   paths on the real component. Include rapid repeat, interruption, and
   non-happy states. When an announcement or screen-reader check cannot run,
   name that evidence gap.

Use `animate` for the moving feedback's timing and interruption while keeping
the action and state contract here. Use `verify` when hands-on evidence
would add confidence.

This branch is complete when every affected semantic, keyboard, focus, status,
input, and edge-state path passes on the real page, or its remaining evidence
gap is explicit.

## Content under constraint

When real data breaks a component, use `verify`'s edge-data workflow to
reproduce it through the existing data boundary. Choose the display contract per
field, then fix the demonstrated cause:

- Keep identifying content and compared numbers, amounts, and dates readable.
  Wrap, clamp previews, or truncate according to the task; expose the complete
  value through a usable detail or expansion path when shortened. A hover-only
  tooltip does not cover touch or keyboard access.
- When a text column pushes siblings out of a flex row, inspect its automatic
  minimum size; `min-inline-size: 0` can let it shrink. Protect fixed-size icons
  and necessary trailing actions from unwanted shrinking. Verify the combined
  row at its real container width. See [flex automatic minimum size](https://drafts.csswg.org/css-flexbox-1/#min-size-auto).
- For identifiers that otherwise overflow, consider `overflow-wrap: anywhere`
  on that content, preserving normal breaks elsewhere. Diagnose before applying
  it globally. See [overflow wrapping](https://drafts.csswg.org/css-text-3/#overflow-wrap-property).
- Choose explicit missing-field and media fallbacks; retain enough identity to
  distinguish duplicate names. Format numbers, plurals, and time for the
  supported locale. Avoid clipping tall scripts or splitting multi-code-point
  characters when deriving initials.
- Treat a large collection as a measured usability and performance question.
  Choose pagination or virtualization when evidence and the interaction model
  warrant it, then check navigation and accessibility as well as scrolling.

### Wrapping, ellipsis, and clamped previews

Apply truncation to the text box, with shrinkable flex/grid ancestors:

```css
.text-column { min-inline-size: 0; }
.name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.excerpt {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}
```

The prefixed multi-line form needs the complete declaration set. Put padding
on a wrapper so extra lines do not leak into the clamp's padding. Prefer wrapping
for required instructions and identifying data; shorten previews only with the
full-value access path described above. `overflow: clip` has different scrolling
and formatting-context behavior; use it here only after verifying the ellipsis
or clamp in target browsers. Choose `overflow-wrap: anywhere` for otherwise
unbreakable strings that must shrink their min-content contribution, and
`break-word` when that intrinsic-size effect is undesirable. Automatic table
layout needs its own width/wrapping check. See [text overflow](https://drafts.csswg.org/css-overflow-3/#text-overflow)
and [line clamping](https://drafts.csswg.org/css-overflow-4/#line-clamp).

## Focus and input feedback

Keep a visible focus indication for every interactive component. A useful
starting point is:

```css
.control:focus-visible {
  outline: max(2px, 0.08em) solid var(--focus-ring, currentColor);
  outline-offset: 0.25em;
}
```

Choose a ring color visible against adjacent surfaces; a button's text or fill
color alone may not provide it. A custom shadow ring also needs an outline that
can survive forced-colors mode, such as a transparent solid outline that the
browser can recolor. Check clipping and ring offsets inside scroll containers.
See [focus-visible](https://drafts.csswg.org/selectors-4/#the-focus-visible-pseudo)
and [forced colors](https://drafts.csswg.org/css-color-adjust-1/#forced-colors-mode).

For hover capabilities, press cancellation, selection, and touch rules, use
[mobile browser input guidance](mobile-web.md#touch-selection-and-feedback).
CSS `:active` can supply simple visual feedback; keyboard and scripted pressed
states still need the component's real activation contract. A color or border
change can be sufficient. Use `animate` for moving/scaling feedback, including
its reduced-motion path.

## Hit areas and clickable cards

Prefer padding or a minimum control size that gives the real button/link a
usable target. When a compact visual must retain its size, a positioned
pseudo-element can extend its hit region:

```css
.icon-button { position: relative; }
.icon-button::after { content: ""; position: absolute; inset: -0.5rem; }
```

Measure the combined target rather than assuming an inset meets a size target.
Keep neighboring targets distinct; clipping ancestors can remove the extension.
Check overlaps, focus visibility, and any pseudo-element already used for
decoration. Use an associated label or wrapper pattern for native inputs whose
pseudo-elements cannot supply this hit area.

A card with one navigation destination can stretch its existing title link:

```css
.card { position: relative; }
.card-link::after { content: ""; position: absolute; inset: 0; }
.card :is(button, a:not(.card-link)) { position: relative; z-index: 1; }
@supports selector(.card:has(.card-link:focus-visible)) {
  .card-link:focus-visible { outline: 2px solid transparent; }
  .card:has(.card-link:focus-visible) {
    outline: 2px solid var(--focus-ring, currentColor);
    outline-offset: 2px;
  }
}
```

Use a real link with a meaningful name inside semantic card markup. Intermediate
positioned ancestors can change the overlay's containing block. Elevate secondary
controls so the overlay does not intercept them. The overlay blocks selection
of covered text; use a smaller linked region or another design when copying
that content matters. Keep the link's own visible ring as the unsupported-`:has()`
fallback. Check default browser rings too. See [containing blocks](https://drafts.csswg.org/css-position-3/#def-cb)
and [relational selectors](https://drafts.csswg.org/selectors-4/#relational).

## Native form state and content sizing

Use native constraints for their appropriate client-side checks and style
`input:user-invalid` when feedback should follow user interaction rather than
marking every untouched required field red. `:user-valid` can show positive
feedback when it serves the task. Associate useful error text with the control;
color or an icon alone cannot explain how to recover. Keep server validation
and the application's submission/error state. See [user validity](https://drafts.csswg.org/selectors-4/#user-pseudos).

For a growing composer, bound both dimensions and leave overflow reachable:

```css
.composer {
  inline-size: 100%;
  min-block-size: 3lh;
  max-block-size: 12lh;
  overflow-y: auto;
  resize: vertical;
}
@supports (field-sizing: content) {
  .composer { field-sizing: content; }
}
```

Use `rows` or the established sizing as the fixed, scrollable fallback. Test
empty values, long placeholders, wrapping, pasted content, font changes, and
the maximum size. Avoid a fixed `height` that defeats content sizing. Preserve
user resizing unless the bounded interaction provides an equivalent usable path.
Height animation is optional; use `animate` if justified. An observer-based
wrapper must own its observer lifecycle, synchronize box sizing and borders,
and keep the caret/content reachable throughout resizing. See
[field sizing](https://developer.chrome.com/docs/css-ui/css-field-sizing).

## Native disclosure and overlay contracts

Use `<details><summary>…</summary>…</details>` for a disclosure whose native
behavior fits. A shared `name` can make related details exclusive when that
is the intended contract and browser targets support it. Preserve a clear
expanded-state cue if replacing the default marker. Native details do not
supply the interaction contract of every accordion design. See
[details](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-details-element).

For a blocking dialog, use the established accessible component or native
`<dialog>` with `showModal()`, an accessible name, initial focus, valid dismissal,
and focus return. CSS `:modal` distinguishes that state from a non-modal dialog:

```css
html { scrollbar-gutter: stable; }
html:has(dialog:modal) { overflow: hidden; }
```

Use this scroll lock only when it meets the app's contract. Verify nested scroll
areas, actual mobile keyboard/viewport behavior, dismissal, and scroll restoration;
use the component's state-owned lock where CSS alone is insufficient. `:has()`
cannot nest another `:has()`. See [dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element).

A native auto popover can provide top-layer display and light dismissal for a
non-modal surface:

```html
<button type="button" popovertarget="account-links">Account links</button>
<nav id="account-links" popover aria-label="Account">
  <a href="/profile">Profile</a>
  <a href="/settings">Settings</a>
</nav>
```

The trigger provides an implicit anchor where supported. Enhance the existing
usable positioning with:

```css
@supports (position-area: block-end span-inline-end) {
  #account-links {
    margin: 0;
    margin-block-start: 0.5rem;
    position-area: block-end span-inline-end;
    position-try-fallbacks: flip-block, flip-inline, flip-block flip-inline;
  }
}
```

Check collision handling at every relevant edge, RTL, zoom, repeated instances,
and content wider than the trigger. Script-opened popovers must establish their
anchor explicitly, using the supported source option or a named anchor. Keep a
usable positioned component or alternative interaction when anchor positioning
or popovers are unavailable. An arbitrary centered fallback may break spatial
meaning. A popover does not implement a menu's roles, arrow navigation, or focus
management; choose semantics from the actual content. Use `animate`'s modal,
menu-dropdown, and accordion guides for transition mechanics. See
[popovers](https://html.spec.whatwg.org/multipage/popover.html) and
[anchor positioning](https://webkit.org/blog/17240/a-gentle-introduction-to-anchor-positioning/).
