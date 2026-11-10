# Publish the command center

Publish one private command center per program. Claude sessions use a private
Claude artifact; Codex sessions use a private ChatGPT Site through the available
Sites plugin. The chief must have the selected publishing tools. If they are
unavailable, stop and report the blocker; do not install plugins automatically.
`hosting` holds the current published page's URL. Keep one canonical
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
  no artifact target. Confirm the artifact update succeeded.
- **Codex:** discover and read the plugin-managed `sites:sites` skill. Give it
  the generated HTML as a buildless static Site at `dist/index.html`. Keep a
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
