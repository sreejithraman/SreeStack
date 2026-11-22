# Share a website with Tailscale Serve

Fallback when T3's preview tunnel cannot serve the preview (outside T3 Code,
Preview tunnel disabled, or when a phone needs HTTPS or an external browser).

## Publish

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

Compare the current Serve mapping and origin identity with the recorded ones. Stop
Serve if its mapping still belongs to this preview, even if the origin changed. Stop
the origin only if this preview started it and its identity still matches. Report any
mismatch or doubt, and leave that service running. Never run `tailscale serve reset`.
Never kill by process name or port. Confirm the URL stopped responding, then report what
stopped and what still runs.
