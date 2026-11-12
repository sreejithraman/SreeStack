# Publish the command center

Publish one private command center per program. Claude sessions use a private
Claude artifact; Codex sessions use a private ChatGPT Site through the available
Sites plugin. The chief must have the selected publishing tools. If they are
unavailable, stop and report the blocker; do not install plugins automatically.
`hosting` holds the current published page's URL. When you give the user a
Claude artifact link, append `#no_universal_links` so iOS opens it in the
browser, not the Claude app, per Claude's
[app-site association](https://claude.ai/.well-known/apple-app-site-association).
Keep `hosting` without the fragment. Keep one canonical
`program.json` and git history, without a parallel backend mirror.

## Render and publish

After each commit under [write the record](program-state.md#write-the-record),
render `HEAD` from this skill's folder:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --page /absolute/path/command-center.html
```

It writes `command-center.next.html` beside the page file and prints `changed`
when that differs from `command-center.html`, the last successfully published
page. On `changed`, publish the `.next` file. On every resume and chief move,
force publication even when unchanged, using the page file in that case, so
skill updates reach it.

Reuse the selected backend's existing target on successive updates. If
`hosting` is absent or points to the other backend, create or use the selected
target and publish there. Changing backend needs no extra provider-switch
approval; [chief ownership](chief-move.md) still needs its existing coordination
and takeover authorization.

- **Claude:** update the private artifact in `hosting`. Create one when there is
  no artifact target. Confirm the artifact update succeeded. Use its native
  viewer; keep the rendered HTML without the Sites refresh assets.
- **Codex:** discover and read the plugin-managed `sites:sites` skill. Give it
  the [prepared output](#prepare-sites-output) as a buildless static Site. Keep a
  durable Site source checkout with its tracked `.openai/hosting.json`; preserve
  its `project_id` and reuse that Site. Let Sites own registration, source sync,
  packaging, and private publication. Its source repository is deployment source,
  not another program record. Use no framework starter, package install, local
  server, new scheduler, or public audience. Wait for a successful terminal
  deployment result with its URL; registration or a saved version alone is not
  publication.

Only after successful publication, move a published `.next` file over the page
file:

```bash
mv /absolute/path/command-center.next.html /absolute/path/command-center.html
```

If the published URL differs from `hosting`, record it through the normal
checked record write and give the user the new URL. Render that metadata commit
as usual: the renderer omits `hosting`, so an otherwise unchanged page needs no
second deployment. This completes the link write without a recursive publish;
if the render does change, publish it normally.

A failed or skipped publication leaves the last successfully published page
file and `hosting` as they were. Stop and report the failure and any created
target or saved version needed to retry. If recording the link fails after
publication, report the deployed URL and the incomplete record write. Keep Site
identity so a retry uses the same target.

## Prepare Sites output

Before Sites packages the source, run this from the chief skill's folder. Pass
the rendered `.next` file on `changed`, or the last published page on a forced
unchanged publication:

```bash
python3 scripts/prepare_sites.py --page /absolute/path/command-center.next.html --output /absolute/path/site-source/dist
```

It writes `index.html` and `chief-version.json` together in `dist/` and prints
their content version. Keep both in the same deployment. The refresh script is
inline, so replacing the page needs no separate script request. Preparation also
removes the obsolete generated `chief-refresh.js` file from earlier output.
The helper leaves the rendered input, program record, and Site manifest alone;
Sites still owns registration, source synchronization, packaging, and deployment.
Keep the published-page marker as the original renderer output, and advance it
only after publication succeeds.

An open Site checks every 20 seconds while visible and on return or focus. It
replaces the full document with matching fetched HTML after same-origin checks,
without a second document request that could fail after validation. It keeps the
URL and uses the page's existing view restoration. Failed, malformed, timed-out,
sign-in, or mismatched responses leave the page available for the next check.
Hidden pages stop checks and abort pending requests. Preparation scopes each
view's script and clears its clock before replacement, because
[`document.open()`](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#dom-document-open)
reuses the document and its window.

To remove live refresh, stop preparing the output and copy the original rendered
HTML to `dist/index.html` again. Remove `chief-version.json` and any old
`chief-refresh.js` from the Site source and deploy through Sites. The renderer,
program record, and Claude publication path need no changes.
