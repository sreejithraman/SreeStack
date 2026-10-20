# Make the result available

Choose an access path that serves the user's next step and is supported by the
project and current tools. Respect explicit target and distribution requests.
Use existing authorization for routine development actions. Publishing,
distribution, and live side effects follow their owning workflow and standing
scope; a demonstration does not expand that scope.

## Websites

For website work with a runnable target, include a checked preview link in the
final reply without waiting for the user to ask. Prefer the project's PR preview
when it contains the current changes. Otherwise share the local target through
Tailscale Serve using [web sharing](web-sharing.md). Honor an explicitly requested
deployment and return its checked URL. Use the existing PR workflow when
applicable; a new PR solely to obtain a preview is unnecessary.

Open the linked route and confirm the current changes are present. Pair the
link with screenshots, video, or other evidence when that helps assessment.
A stale deployment or localhost-only URL does not satisfy the preview handoff.
If sharing is unavailable, name the blocker and provide whatever checked
demonstration is still possible.

State login, network, and runtime requirements. A request from the host machine
does not establish access from another device; disclose unverified remote-client
access. Keep a server needed for inspection running after handoff. Record its
process identity, ownership, and exact stop action. Reused services retain their
owner. Stop an origin only when this showing started it and its recorded identity
still matches. Tailnet teardown checks mapping and origin separately under
[web sharing](web-sharing.md).

## Native apps and devices

Choose between a running Simulator/emulator, a connected physical device, and
an existing development or beta distribution path based on what the user needs
to assess or try. An iPhone install may be the right delivery even when earlier
checks used Simulator. Discover available devices and development tooling;
select a suitable target, build the current revision, and install and launch
when that is the chosen path and within the task's scope.

Use Verify's [iOS tooling](../../verify/references/ios.md) for builds and device
operations and the host's device routing for available platforms. Its default
verification target does not require choosing the same delivery target. Keep
evidence labeled by target: a Simulator capture cannot establish physical-device
behavior. Preserve an explicitly requested target; if unavailable, report that
gap and identify any secondary demonstration.

Confirm the intended app and changed screen or flow after launch. Report which
device or distribution path holds which build and how the user can open it.
An install alone does not show an interaction; add captures or a demonstrated
flow when useful. Preserve existing app data and unrelated devices; avoid
resets, uninstalls, or device creation unless needed and within scope. Use
`app-store-connect` for TestFlight or other Apple distribution work.

## Commands and services

Use a representative example through the public command or API. Return its
invocation, required setup, and observed result, with output excerpts or a
sample session when helpful. Validate the example in the current environment.
Keep credentials out of commands and captured output; name approved credential
setup instead. For state-changing examples, use task-authorized test data and
describe the effect before inviting the user to rerun them.

Keep test verdicts with Verify. An example demonstrates its observed case;
call out dependencies or checks that remain untested. If access needs a running
service, record its URL or port, ownership, lifetime, and exact stop action.
Preserve reused services and stop only processes this showing owns whose
identity still matches.

## Files and documents

Link the actual output so the user can open, download, or inspect it. Check that
it opens and contains the intended result with available tools. State required
software or environment limitations. Add a rendered preview or excerpt when
it helps assessment; keep the original artifact accessible.
