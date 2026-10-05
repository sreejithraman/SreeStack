# Realistic edge data

Use when stress-testing a component or investigating a failure tied to its
content. Exercise plausible production values and actual contract limits through
the component's normal rendering path. For a bounded acceptance task, cover the
affected fields and material neighbors; for a whole-component stress audit,
account for every rendered value and applicable catalog category below.

## Map, fixture, render, judge

1. Inventory each rendered value with its source, type, optionality, and limit:
   names, identifiers, labels, counts, timestamps, status text, media, and the
   collection's length. Inspect validation, API contracts, storage limits, form
   constraints, and import paths. Record disagreements. Say `no limit found`
   when the evidence is incomplete; reserve `unbounded` for a known contract.
2. Choose a realistic extreme or a schema-backed boundary for each applicable
   case. Mix different stresses across visible rows, then add separate empty,
   one-item, pagination-boundary, and realistic high-volume fixtures as needed.
   Keep each fixture type-correct; distinguish accepted data from malformed or
   partial responses used specifically to test defensive behavior.
3. Feed fixtures through the existing props, mock, fixture loader, or API stub.
   Keep markup and styling intact while reproducing the failure. Use existing
   fixture selection first. Add a development-only comparison control or route
   only when it materially helps inspect repeatable states; keep it outside the
   component's layout and out of production. Use reserved domains such as
   `example.com` and local media or controlled stubs rather than live recipients.
4. Render at the component's actual container size, its narrowest and widest
   supported placements, and relevant text scaling or browser zoom (including
   200% when enlargement is in scope). Check supported appearance and direction
   variants. Root font-size changes and browser zoom test different paths; state
   which ran. Inspect action reachability, full-value access, wrapping, clipping,
   fallback identity, formatted values, scroll performance, and state transitions.
5. Report each observed failure with the triggering fixture, container/environment,
   location, expected behavior, impact, and proposed correction. Distinguish a
   demonstrated defect from an inferred risk or missing limit. Record applicable
   cases that held up and any untested assertions using the main skill's statuses.

For a review, leave fixes to its implementation owner. When fixes are already
authorized, preserve that scope: use `ui-design` for design and browser behavior,
or the relevant native specialist, then rerun both the failing fixtures and the
ordinary state. Retain useful fixtures in the project's existing conventions;
remove disposable harness code or document why it remains.

## Fixture catalog

Select concrete values from the supported domain; examples suggest boundaries,
not mandatory datasets. A missing name or negative count belongs in the accepted
fixture only if its contract allows it. Use separate response-failure tests otherwise.

| Category | Realistic cases | Assertions to inspect |
| --- | --- | --- |
| Names and identity | `Aleksandra Wiśniewska-Kowalczyk`, `Jo`, `J`; suffixes and particles; apostrophes, repeated spaces, missing optional display name | Short links remain usable; wrapping, fallback identity, initials, and duplicate-name disambiguation work |
| Scripts and graphemes | `Đặng Thị Ngọc Hân`, `王秀英`, Arabic display names, `👩🏽‍💻 Priya`; supported mixed-direction strings | Tall glyphs stay visible; initials do not split a character sequence; punctuation and reading order remain intelligible |
| Identifiers | A long address at an `example.com` subdomain; plus-addressing; a URL with query parameters; UUID; filename with version and extension; short handle | Siblings and actions stay reachable; meaningful distinguishing text and full values remain accessible |
| Labels and prose | Long translated action/status labels; a compound word; many tags and one long tag; empty or whitespace title; newlines; a long pasted description within limits | Controls grow or wrap coherently; missing content has an intentional fallback; expansion works; literal text is rendered according to the content contract |
| Counts and amounts | `0`, `1`, `1284`, large supported totals, negative money where valid, rounding-sensitive fractions, null response values, live `99` → `100` updates | Plurals, grouping, precision, signs, and missing-value handling are correct; compared values remain readable and updates do not disturb controls |
| Collections | Empty, one, exactly page size, page size + 1, realistic high volume; duplicate names; one unusually tall item | Empty and singular states work; pagination boundaries are correct; rows remain distinguishable; scrolling and navigation stay usable |
| Time | Now, relative-time thresholds, future time, timezone day/year boundary, long duration, absent or sentinel timestamp | The date matches the intended timezone and precision; missing dates are not presented as real events; labels remain readable |
| Media | Missing and failed image; slow load; panorama and portrait; transparent or low-contrast logo | Fallback and crop fit the content; space is reserved appropriately; loading does not strand actions or cause disruptive movement |
| States and permissions | Loading, error, partial data, every relevant status, no permission, current-user row | Errors have a usable recovery path; layout and semantics survive partial responses; actions reflect permission and self-action rules |
| Environment | Narrow sidebar and broad placement; enlarged text and zoom; supported dark mode and RTL; non-hover input | Content remains readable and distinguishable; controls and full values remain reachable through the supported access paths |

The stress check is complete when each required field/category has an exercised
fixture and assertion result, or an explicit evidence gap. A static CSS diagnosis
can identify risks, but cannot substitute for an observed rendered result.
