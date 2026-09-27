---
name: add-to-snip-snap
description: Save text or a future todo in Snip Snap when the user asks, or capture a concrete agent-discovered idea or improvement outside current and already-planned work. Not for immediate tasks, reading, exporting, or editing existing snips.
---

# Add to Snip Snap

Use the installed `snipsnap add` command. It records `.agent` as the snip origin.
If `snipsnap` is unavailable on `PATH`, report that the CLI is unavailable and do not claim the snip was saved.

Save text when the user asks. Treat an action they ask to remember, revisit, follow up on, or look into later as a saved todo, preserving it as useful standalone text. For an idea or improvement you discover yourself, check the current task and any readily available plan or backlog. Save it when it is concrete and worthwhile, and neither current nor already planned. Write each distinct idea once as a standalone note that names the area, the proposed action, and why it matters. Capture it when discovered, then continue the current work.

1. Generate one UUID for the request. Resolve the destination and agent context once. Keep the UUID, text, destination, session title, and branch unchanged across every retry.
2. Send the exact text on standard input so shell quoting cannot alter it. Add `--list NAME` only when the user names a destination; otherwise use Inbox. Add `--session-title TITLE` when the host exposes a human-readable session title. Never pass a session ID as the title. When the title is unavailable, read the current Git branch once and pass it with `--branch NAME`; if there is no branch, omit both context flags. Reuse those exact flags on retries even if the working directory or current branch changes.
3. Pass `--request-id UUID --json`. A zero exit status with `"status":"added"` or `"status":"unchanged"` completes the request. `"status":"pending"` means the request is safely queued; tell the user it will appear when Snip Snap next opens.

If a named destination is deleted before a queued request is imported, Snip Snap saves the text to Inbox.

Provide the snip text through the process's standard input. If the command reports that a list is missing, ask for another list or omit `--list` to use Inbox. Report other failures without claiming the snip was saved.
