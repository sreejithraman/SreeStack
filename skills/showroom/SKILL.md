---
name: showroom
description: Use after changing what a user sees — an iOS screenshot in the reply, or a Tailscale URL for a local web page they can open away from the Mac.
---

# Showroom

After UI work, show the UI. A build or test does not replace it. If the change has no user-visible UI, skip. If you cannot show the UI, name the blocker.

## Web

1. Start the repo's existing `dev` or `start` script bound to `127.0.0.1`. Keep that process running after this command returns.
2. Publish it with Tailscale Serve: `tailscale serve --bg --https=<port> http://127.0.0.1:<origin>`. Use a high Serve port; do not use 443, 8443, or 10000. Never Funnel.
3. Return the `https://…ts.net…` URL. Open it if a browser tool is available.
Finish when that URL loads. Say that it needs this Mac awake and on Tailscale. In the reply, include the exact `tailscale serve --https=<port> off` command and how to stop the origin process this run started.

When asked to take the page down, run those exact commands. Do not run `tailscale serve reset`. Do not kill by process name or port.

## iOS

1. Build for Simulator and launch the app.
2. Use one simulator. Create one only if none is usable. Leave every other device untouched.
3. Screenshot the running app, not the home screen.
4. Put the PNG in the reply with its absolute path so the coding app renders it.
Finish when the image is in the reply.
