# Publish the command center

Publish one private command center per program: Claude sessions use a private Claude artifact;
Codex sessions use a private ChatGPT Site via the available `sites:sites` plugin. Never install
plugins automatically. On another provider (such as Gemini/Antigravity or Grok) that lacks both
Claude artifact tools and `sites:sites`, either delegate just publishing the rendered
`command-center.next.html` + `files/` to a one-shot Codex (`sites:sites`) or Claude helper when
available, or run local-only (`command-center.html` on disk + Inbox in chat) and tell the user.
Every command center uses **Copy answer** in the Inbox so switching providers mid-program never
strands answers.

When sharing a Claude artifact link with the user, append `#no_universal_links` so iOS opens it in
the browser instead of the Claude app (per Claude's
[app-site association](https://claude.ai/.well-known/apple-app-site-association)); keep `hosting`
in `program.json` without the fragment.

## Render and publish

Every `record.py` write renders `HEAD` to `command-center.next.html` beside `command-center.html`
and prints `page: behind record <commit>` (plus any `files/<hash>.<ext>` images to publish with it)
when the page changed. On resume, coordinator move, or same-thread provider switch, force
publication even if unchanged so skill updates reach the hosted page.

Reuse the selected backend's existing target. Switching backends needs no extra approval:

1. **Before publishing:** note any existing `hosting` URL so you can tell the user if it becomes
   frozen.
2. **Publish once on the active backend:**
   - **Claude:** call `publish_files` with the page as `index.html` and each listed image as
     `files/<name>` (from `files/` beside the page). Update the existing private artifact by slug
     and current version in patch mode so unchanged images stay.
   - **Codex:** read the plugin-managed `sites:sites` skill and deploy the prepared output below as
     a buildless static Site from the sibling `<program>/site/` checkout (never nested inside
     `record/`), reusing its `.openai/hosting.json` (`project_id`). If reopening a missing Site
     checkout via `sites:sites` (for example on resume or migration), reopen or select that separate
     checkout first and prepare output into its returned checkout's `dist` so `project_id` is
     preserved. Put any temporary `.tar.gz` package archive in `$TMPDIR` and delete it after
     confirmed deploy. Keep `site/` inside the program container until the program folder itself is
     pruned so `.openai/hosting.json` survives pause/resume. Use no framework starter, package
     install, local server, or public audience. Wait for a confirmed terminal deployment URL
     (registration or saved version alone is not publication).

Only after confirmed publication of a staged `command-center.next.html` on a hosted backend,
advance the marker (skip this move on a forced unchanged publish where `command-center.html` was
deployed directly):

```bash
mv /absolute/path/command-center.next.html /absolute/path/command-center.html
```

In **local-only mode** (when no hosted backend is available), do not claim external publication: if
the render staged `command-center.next.html` (`page: behind`), verify it on disk and run the same
`mv` locally so `command-center.html` stays current and `status --turn-end` passes; if the render is
unchanged (`page: current`, no `.next.html` staged), verify and retain the existing
`command-center.html`. In both cases, post any open Inbox items directly in chat. When switching
from a previously hosted page to local-only mode, tell the user which previous hosted URL is now
frozen and that the local file plus chat Inbox are active instead.

If the deployed URL changed, record it once with `record.py grant --hosting <url>` and tell the
user the new URL and that the previous URL is now frozen (the renderer omits `hosting`, so an
otherwise unchanged render needs no second publish; if the render does change, publish it normally).
On publish failure, leave `command-center.html` and `hosting` untouched, keep Site identity so a
retry reuses the same target, and report the failure and any created target or saved version needed
to retry. If recording the link (`record.py grant --hosting <url>`) fails after publication, report
the confirmed deployed URL and the incomplete record write, and retry the metadata write with that
URL without redeploying.

## Prepare Sites output

Before deploying to Codex Sites, run from this skill's folder (passing `.next.html` on changes, or
`command-center.html` on forced unchanged republish; omitting `--output` writes the sibling
`../site/dist` when `--page` is in `record/`, while legacy flat records or custom Site checkouts
pass `--output` explicitly):

```bash
python3 scripts/prepare_sites.py --page /absolute/path/<program>/record/command-center.next.html
# Legacy flat record or custom Site checkout:
python3 scripts/prepare_sites.py --page /absolute/path/command-center.next.html --output /absolute/path/<site-checkout>/dist
```

This writes `index.html`, `chief-version.json`, and `files/` images together into `site/dist/`
for live refresh without touching `program.json`, the published-page marker, or `record/.git`.
Keep all generated files in the same deployment. To remove live refresh later, copy the raw
rendered HTML to `site/dist/index.html`, delete `chief-version.json` (and any old
`chief-refresh.js`), and redeploy.
