# Share a local web preview

For an explicitly requested tailnet preview, or an established project sharing workflow:

1. Start or locate the repo's existing `dev` or `start` server bound to
   `127.0.0.1`. Record its process identity, including command and start time or
   controlled session, whether this preview started it or reused it.
2. Check the current Serve configuration. Choose an unused high port other
   than 443, 8443, or 10000, then publish with Tailscale Serve:
   `tailscale serve --bg --https=<port> http://127.0.0.1:<origin>`. Never Funnel.
   Keep any origin process started for this preview running after the command
   returns.
3. Exercise and capture the changed route or state through the returned URL.
   If no browser tool is available, check that route with `curl` or another
   read-only request and name the remaining remote visual-proof gap.

When available, check the URL from an off-home client too (on the tailnet for
Tailscale Serve). Otherwise report remote-client access as unverified; a check
from this Mac alone does not establish it.

Return the URL and say that access requires this Mac awake and on Tailscale,
and the user's device on the tailnet. Include the Serve mapping and the exact
`tailscale serve --https=<port> off` command. If this preview started the origin,
include its exact stop command or session action too; otherwise say the reused
origin will remain running after take-down.

When asked to take the preview down, compare the current Serve mapping and
origin process identity with the recorded ones. Stop Serve if its mapping still
belongs to this preview, even if the origin has changed. Stop the origin only
if this preview started it and its identity still matches. Report any mismatch
or uncertainty and leave that service running. Do not run
`tailscale serve reset`. Do not kill by process name or port.
