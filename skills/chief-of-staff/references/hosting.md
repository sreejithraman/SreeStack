# Host the command center

The command center is hosted only: give the user a link to return to, not an
inline render in the chat. `scripts/serve_dashboard.py` renders `program.json`
on every request, so the page always shows the file as it stands. Writing the
file is all it takes to update the page. The server adds no coordinator,
database, or wakeups.

1. Start the server from this skill's folder, detached so it outlives the turn.
   It picks an unused loopback port and writes its URL as the first line of
   `serve.log`:

   ```bash
   nohup python3 scripts/serve_dashboard.py --state /absolute/path/program.json > /absolute/path/serve.log 2>&1 &
   ```

   It binds `127.0.0.1` and serves only `/`, nothing else from disk. When the
   file fails to load, it serves the last good page under an error banner and
   logs the error; with no good page since it started, it serves an error page
   that retries. Repair the file as [check the chief](chief-move.md#check-the-chief)
   says.
2. Use Show Me's [web sharing](../../show-me/references/web-sharing.md) to share
   it. For Tailscale, follow its procedure with this server as the origin:
   existing Serve mappings preserved, verification, lifetime, and teardown.
3. Return the actual HTTPS URL after checking its normal hostname and page
   content, ideally from the user's phone or another tailnet client. A check
   with an explicit IP or DNS override proves only that path; label the rest
   unverified.

Record the URL, the server's PID, port, start time, and arguments, the Serve
mapping, exact stop commands, and access limits in `record.hosting`. The hosting
machine must stay awake and connected, and viewers need tailnet access.

An open page fetches its URL every 20 seconds while visible and when the user
returns to it, then shows a changed page in place with its tab, selection,
sections, and scroll position kept. Each browser tab keeps that view for the
URL, so a manual refresh returns to it too; a new tab starts at Needs you. A
write that changes only `record` keeps `updatedAt` and leaves open pages alone.
Answers still go through chat.

## Host again

On every resume and chief move, host the page again, however it looks. This
picks up skill updates, a server lost to a reboot, and a stale live server
alike. Bring the new server up before the old one goes down:

1. Start a new server as above, and confirm its loopback URL serves the
   current `program.json`.
2. Point the HTTPS Serve port in `record.hosting` at it if that mapping still
   points at the recorded origin or the port is free, so the link stays the
   same. Otherwise pick a new port under Show Me's
   [Tailscale Serve](../../show-me/references/web-sharing.md#tailscale-serve)
   rules, and tell the user the link changed.
3. Confirm the HTTPS URL as above. Then stop the old server only if its PID,
   start time, and arguments match `record.hosting`, and record the new server
   there.

If a step fails, restore the old mapping, stop the new server, and tell the
user.

## Take it down

For final teardown, follow the
[web sharing](../../show-me/references/web-sharing.md#take-it-down)'s take-down
rules: stop the Serve mapping, then the server only if its PID, start time, and
arguments still match the record. Keep `program.json` and the reports.
