# Share a website

Include a checked link for website work in the report, without being asked. After a
merge, link only a deployment you checked holds the change. If none does, post the
captures, say so, and share no local preview. Stop one you started by following
[Take it down](#take-it-down).

1. Use the project's PR preview if it holds the current changes. Use a requested
   deployment if the user named one. Open no PR just to get a preview.
2. Otherwise share the local target through Tailscale Serve, below.
3. Open the linked route, exercise the change, and confirm it's there. If you have no
   browser tool, check the route with `curl` or another read-only request, and name the
   interaction you didn't check. A stale deployment or a localhost URL doesn't count.
4. State any login, network, or runtime requirements. If sharing is unavailable, name
   the blocker and give the best checked showing you can.

## Tailscale Serve

1. Start or find the repo's `dev` or `start` server, bound to `127.0.0.1`. Record its
   process identity, including its command and start time or session, and whether you
   started it or reused it.
2. Check the current Serve configuration, and choose an unused high port other than
   443, 8443, or 10000.
3. Publish with `tailscale serve --bg --https=<port> http://127.0.0.1:<origin>`. Never
   use Funnel. Keep any origin you started running.
4. Check the URL from another tailnet client if you can. Otherwise report phone access
   as unverified, because a check from this Mac doesn't prove it.

Return the URL, and say it needs this Mac awake and on Tailscale, with the user's
device on the tailnet. Include the Serve mapping and `tailscale serve --https=<port>
off`. If you started the origin, include its stop command. If you reused it, say it
keeps running.

## Take it down

This covers Tailscale Serve previews. Leave a PR preview or deployment to its owner, and
name it. Find the record in the report that shared the preview, using the host's thread
search from a new thread. With no record, report that and leave everything running.

Compare the current Serve mapping and origin identity with the recorded ones. Stop
Serve if its mapping still belongs to this preview, even if the origin changed. Stop
the origin only if this preview started it and its identity still matches. Report any
mismatch or doubt, and leave that service running. Never run `tailscale serve reset`.
Never kill by process name or port. Confirm the URL stopped responding, then report what
stopped and what still runs.
