# Host the command center

Use when the user wants a dashboard link they can return to outside the chat.
The page is a read-only snapshot. The chief owns its data; hosting serves the
file and adds no coordinator, database, or wakeups.

1. Choose a task-owned directory that survives worktree cleanup. Keep the
   program record, snapshot JSON, logs, and hosting details outside a dedicated
   public folder, and publish only the rendered page there.
2. Render each snapshot to a staging file. When it validates, move it over the
   public `index.html` on the same filesystem, so the last valid page stays up
   and no partial file is served.
3. Use [Showroom's delivery workflow](../../showroom/references/delivery.md#websites)
   to choose hosting. For Tailscale, follow its
   [web sharing procedure](../../showroom/references/web-sharing.md): a
   loopback-only origin on an unused port, existing Serve mappings preserved,
   verification, lifetime, and teardown. A small Python static file server is
   enough when the project has no server to reuse; serve only the public folder.
4. Return the actual HTTPS URL after checking its normal hostname and page
   content, ideally from the user's phone or another tailnet client. A check
   with an explicit IP or DNS override proves only that path; label the rest
   unverified.

Record the URL, public path, origin process and start time, Serve mapping,
exact stop commands, and access limits in the program record. The hosting
machine must stay awake and connected, and viewers need tailnet access.

On each meaningful result or decision, replace the page at the same path.
Reloading shows the new snapshot; the open page does not refresh itself, and
answers still go through chat.

For teardown, follow the
[web sharing procedure](../../showroom/references/web-sharing.md)'s take-down
rules. Keep the state and any page the chief still needs.
