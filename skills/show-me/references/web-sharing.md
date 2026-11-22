# Share a website

Include a checked link for website work in the report, without being asked. After a
merge, link only a deployment you checked holds the change. If none does, post the
captures, say so, and share no local preview. Stop one you started under Take it
down below.

1. Use the project's PR preview if it holds the current changes. Use a requested
   deployment if the user named one. Open no PR just to get a preview.
2. Otherwise, in T3 Code, share the local server through T3's preview tunnel below.
   Use [Tailscale Serve](tailscale-serve.md) instead when outside T3 Code, when the
   host's Preview tunnel is off, or when the page needs HTTPS or a browser outside T3's
   WebView (iOS/iPadOS secure-context APIs such as clipboard, service workers/PWA,
   WebAuthn, camera/mic, or geolocation; mobile Safari/Chrome; WebRTC; OAuth HTTPS
   callbacks; custom hostnames; or tailnet sharing outside T3).
3. Open the linked route, exercise the change, and confirm it's there. If you have no
   browser tool, check the route with `curl` or another read-only request, and name the
   interaction you didn't check. A stale deployment—or a `localhost` URL without T3's
   preview tunnel—doesn't count.
4. State any login, network, or runtime requirements. If sharing is unavailable, name
   the blocker and give the best checked showing you can.

## T3 local preview

1. Start or reuse the repo's `dev` or `start` server, bound to loopback (`127.0.0.1` or
   `localhost`). Record its process identity, including its command and start time or
   session, and whether you started it or reused it. Keep any server you started running.
2. Open and check the route with `preview_open` using
   `target: { kind: "environment-port", port, path }` (adding `protocol: "https"` only
   for HTTPS dev servers). Leave that preview tab open for the user.
3. Return the checked `http://localhost:<port><path>` (or `https://` for HTTPS dev
   servers) link and note that the preview tab is open (tap the link on T3 Mobile to
   open natively on device, use the preview tab or **Servers** panel on Desktop, or view
   the streamed tab on Web). State that it needs this Mac awake and T3 connected.
   Include the stop command if you started the server, or say a reused server keeps
   running.

## Take it down

Leave a PR preview or deployment to its owner, and name it. Find the record in the
report that shared the preview, using the host's thread search from a new thread. With
no record, report that and leave everything running.

If the record includes a Tailscale Serve mapping, follow
[Tailscale Serve teardown](tailscale-serve.md#take-it-down). Otherwise, compare the
running process identity with the recorded one. Stop the server only if this preview
started it and its identity still matches. Report any mismatch or doubt, and leave that
service running. Never kill by process name or port. Close the preview tab if this
thread owns it. Confirm the port stopped responding, then report what stopped and what
still runs.
