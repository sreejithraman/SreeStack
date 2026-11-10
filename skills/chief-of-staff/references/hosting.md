# Publish the command center

The command center is one private Claude artifact per program, and `hosting`
holds its link.

After each commit under [write the record](program-state.md#write-the-record),
render `HEAD` from this skill's folder:

```bash
python3 scripts/render_dashboard.py --state /absolute/path/program.json --page /absolute/path/command-center.html
```

It writes `command-center.next.html` beside the page file and prints `changed`
when that differs from `command-center.html`, the last page you published. On
`changed`, publish the `.next` file to the artifact in `hosting`, then move it
over the page file:

```bash
mv /absolute/path/command-center.next.html /absolute/path/command-center.html
```

A failed or skipped publish leaves the page file as it was, so the next render
still prints `changed`. Create the artifact only when `hosting` has none, then
record its link. On every resume and chief move, publish the page file even when
unchanged, so skill updates reach it.
