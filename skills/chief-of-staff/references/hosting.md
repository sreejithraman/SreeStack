# Host the command center

The command center is hosted only: give the user a link to return to, not an
inline render in the chat. `scripts/serve_dashboard.py` renders the program's
last commit, `HEAD:program.json`, on every request, so a
[record write](program-state.md#write-the-record) reaches the page when it
commits. The server adds no coordinator, database, or wakeups.

1. Start the server from this skill's folder, detached so it outlives the turn.
   It picks an unused loopback port and writes its URL as the first line of its
   own log:

   ```bash
   log=/absolute/path/serve-$(date -u +%Y%m%dT%H%M%SZ).log
   nohup python3 scripts/serve_dashboard.py --program /absolute/path > "$log" 2>&1 &
   ```

   It binds `127.0.0.1` and serves only `/`, nothing else from disk. When the
   last commit fails to load, it serves the last good page under an error banner
   and logs the error; with no good page since it started, it serves an error
   page that retries. The next good commit clears it.
2. Use Show Me's [web sharing](../../show-me/references/web-sharing.md) to share
   it. For Tailscale, follow its procedure with this server as the origin:
   existing Serve mappings preserved, verification, lifetime, and teardown.
3. Return the actual HTTPS URL after checking its normal hostname and page
   content, ideally from the user's phone or another tailnet client. A check
   with an explicit IP or DNS override proves only that path; label the rest
   unverified.

Record the URL, the server's PID, port, start time, arguments, and log, the
Serve mapping, exact stop commands, and access limits in `record.hosting`. The
hosting machine must stay awake and connected, and viewers need tailnet access.

An open page fetches its URL every 20 seconds while visible and when the user
returns to it, then shows a changed page in place with its tab, selection,
sections, and scroll position kept. Each browser tab keeps that view for the
URL, so a manual refresh returns to it too; a new tab starts at Needs you. A
commit that changes only `record` keeps `updatedAt` and leaves open pages alone.
Answers still go through chat.

## Host again

On every resume and chief move, host the page again, however it looks. This
picks up skill updates, a server lost to a reboot, and a stale live server
alike. Bring the new server up before the old one goes down:

1. Start a new server as above, and confirm its loopback URL serves the last
   commit.
2. Point the HTTPS port in `record.hosting` at it, so the link stays the same,
   if that port is free or its mapping still belongs to this page, even if the
   origin changed. Otherwise pick a new port under Show Me's
   [Tailscale Serve](../../show-me/references/web-sharing.md#tailscale-serve)
   rules, and tell the user the link changed.
3. Confirm the HTTPS URL as above.
4. Record the new server in `record.hosting` with a
   [record write](program-state.md#write-the-record).
5. Only then stop the old server, and only if its PID, start time, and
   arguments match what `record.hosting` named before this write.

If a step before the commit fails, point Serve back at the old server, turn off
any new port, stop the new server, and tell the user. If the commit fails, stop
and report both servers' identities.

## Take it down

For final teardown, follow the
[web sharing](../../show-me/references/web-sharing.md#take-it-down)'s take-down
rules: stop the Serve mapping, then the server only if its PID, start time, and
arguments still match the record. Keep the program folder and its reports.
