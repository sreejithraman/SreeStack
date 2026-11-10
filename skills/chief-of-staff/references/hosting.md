# Publish the command center

The command center is one private Claude artifact per program, and
`record.hosting` holds its link. The chief needs the Claude artifact tools;
owners don't.

After each commit under [write the record](program-state.md#write-the-record),
render the page from this skill's folder. It renders `HEAD` into the page file
beside the record and prints `changed` when the page differs from its last
render:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --page /absolute/path/command-center.html
```

When it prints `changed`, publish that file to the artifact in `record.hosting`.
Create the artifact only when `record.hosting` has none, then record its link. A
record-only commit keeps `updatedAt`, so its page is unchanged. Publish the file
even when unchanged on every resume and chief move, so skill updates reach the
page, and before any write that follows a failed publish.

If a publish fails, stop and report it to the user, as for a git error, so the
page never lags behind the record unnoticed. Give the user the link, never an
inline render. Teardown keeps the artifact unless the user asks to delete it.
