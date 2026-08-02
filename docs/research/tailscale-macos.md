# Tailscale Serve and `launchd` for macOS previews

Research date and source access date: **2026-07-20**. This note covers the
web-local adapter only. It records current provider and platform behavior,
then derives implementation requirements for `showroom`. It does not
authorize or perform any Tailscale, Funnel, Services, or `launchd` mutation.

## Recommendation

Use **ordinary Tailscale Serve** as the default private web-local transport.
Run each development origin as a separately identified per-user `launchd`
agent, bind it to `127.0.0.1` on a manager-allocated port, health-check the
origin, and then create a background Serve HTTPS route on a separately
allocated Tailscale-facing port. Store the exact launchd label, plist path,
Serve flags, origin port, route port, URL, and ownership token in the registry.

Do not invoke `tailscale funnel` at all. Do not invoke `tailscale serve reset`,
`tailscale funnel reset`, `tailscale down`, `tailscale up`, or modify the
device identity or tailnet policy. Those operations have a broader blast
radius than one preview.

Treat **Tailscale Services** as an opt-in deployment topology, not an automatic
upgrade. Services require administrative setup and a tag-authenticated host;
Tailscale explicitly says tags are inappropriate for user devices such as a
MacBook. A normal user-authenticated development Mac therefore cannot be
silently converted into a Services host.

## Provider behavior

### Ordinary Serve is private to the tailnet, subject to policy

`tailscale serve` routes traffic from other devices in the same tailnet to a
local service. Tailnet access-control rules still apply. `tailscale funnel`, by
contrast, makes a local service reachable from the public internet.
([Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve), last
validated 2026-01-20; [Tailscale Funnel](https://tailscale.com/docs/features/tailscale-funnel),
last validated 2026-01-26.)

This means “private” is not synonymous with “only the current user.” The
effective audience is whichever tailnet users/devices and accepted external
shares are allowed by the tailnet policy. Serve can add requester identity
headers, and Tailscale recommends that a backend relying on those headers
listen only on localhost so another network client cannot spoof them.
([Tailscale Serve: identity headers](https://tailscale.com/docs/features/tailscale-serve#identity-headers).)

Implementation implications:

- The adapter must contain no code path from `start` to `tailscale funnel`.
- `doctor` and allocation should inspect both `tailscale serve status --json`
  and `tailscale funnel status --json` before claiming a Tailscale-facing port.
- The origin should bind to `127.0.0.1`, not `0.0.0.0`, unless the manifest
  explicitly requires otherwise and reports the extra LAN exposure.
- The handoff must say “available to permitted tailnet peers,” not merely
  “private.”

### Serve and Funnel share port configuration

Serve and Funnel cannot use the same port simultaneously. Tailscale documents
that the most recent command for a shared port determines whether that port is
tailnet-only (`serve`) or public (`funnel`). Funnel is limited to ports 443,
8443, and 10000; ordinary Serve exposes an explicit `--https=<port>` endpoint.
([Serve limitations](https://tailscale.com/docs/features/tailscale-serve#limitations);
[Funnel CLI](https://tailscale.com/docs/reference/tailscale-cli/funnel), last
validated 2026-01-26.)

Implementation implications:

- Never “take over” 443, 8443, or 10000, or any other route already reported by
  Serve/Funnel, even if the local origin port is free.
- Allocate the origin socket and Tailscale-facing HTTPS port under the same
  registry lock. Recheck provider status immediately before creation. The
  provider does not document an atomic create-if-unclaimed operation, so a
  final conflict check and fail-closed behavior are required.
- Prefer one high, collision-safe Tailscale-facing port per worktree instead of
  path multiplexing on 443. Many development servers do not work correctly
  below an injected base path. The installed Tailscale version must accept and
  verify the selected HTTPS port before success is reported; the official
  HTTPS flag documentation does not publish a narrower allowed-port list for
  ordinary Serve.
- After creation, verify that Serve reports the route and Funnel does not
  report the same port. A surprising Funnel claim is a hard safety failure.

### Serve configuration is daemon-owned and can outlive the CLI process

The relevant ordinary Serve interface is:

```text
tailscale serve --bg --https=<route-port> http://127.0.0.1:<origin-port>
tailscale serve status --json
tailscale serve --https=<route-port> off
```

`--bg` makes Serve persist after the shell exits and resume after a device
reboot or `tailscale down`/`tailscale up`. Without `--bg`, the foreground
session must be restarted. An `off` operation removes a server when it repeats
all original flags; the target is optional. `tailscale serve reset` clears the
entire Serve configuration.
([Tailscale Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve),
last validated 2026-01-26.)

Implementation implications:

- Let Tailscale own route persistence with `--bg`; supervise only the origin
  process with `launchd`. The two lifecycles remain independently observable.
- Record a canonical argv array for the exact creation and exact `off`
  operation. Do not reconstruct cleanup flags from project state that may have
  changed.
- Never use `tailscale serve reset` during normal stop or cleanup because it
  can remove routes not created by `showroom`.
- Treat “already absent” as success during idempotent stop. Treat “present but
  no longer matches the registry-owned target” as a conflict requiring manual
  review, not permission to remove it.
- `tailscale serve status` and `--json` currently expose different information,
  and the docs do not publish a versioned JSON schema. Parse defensively, retain
  the raw status as diagnostic evidence, and gate behavior by the installed
  Tailscale version. Do not infer ownership from a matching port alone.

On Tailscale 1.98.8, inspected locally and read-only on 2026-07-20,
`serve status --json` and `funnel status --json` returned the same complete
Serve configuration. Public exposure must therefore be identified from exact
true entries under `AllowFunnel`, not from the listeners returned by the
`funnel status` command. Tailscale's first-party `ServeConfig` source defines
`AllowFunnel` as the SNI/port set permitted to receive trusted ingress traffic
and applies the same rule to foreground configurations.
([Tailscale ServeConfig source](https://github.com/tailscale/tailscale/blob/main/ipn/serve.go).)

### HTTPS setup has a privacy side effect

Serve requires HTTPS certificates to be enabled for the tailnet. If the
requirement is missing, the CLI opens an interactive consent flow. Enabling
HTTPS publishes the machine name and tailnet DNS name to the public Certificate
Transparency ledger, although network access remains restricted by Tailscale.
([Tailscale Serve setup](https://tailscale.com/docs/features/tailscale-serve#get-started-with-serve);
[Enabling HTTPS](https://tailscale.com/docs/how-to/set-up-https-certificates),
last validated in the current Tailscale documentation.)

Implementation implications:

- `doctor` should explain the HTTPS/MagicDNS requirements and report readiness
  only when it can determine it through a read-only interface. The public docs
  do not identify a reliable read-only field for HTTPS readiness. An automated
  start must not silently accept the web consent flow or change tailnet-wide
  HTTPS settings.
- If setup is needed, return an approval-required result that explains the
  public certificate-name disclosure.
- Never persist the concrete machine hostname in a repository. It belongs only
  in machine-local registry state and the handoff result.

### macOS CLI variants must be detected without changing installation

For the Standalone macOS client, Tailscale's optional CLI integration installs
`/usr/local/bin/tailscale`. For the App Store client, the CLI is inside
`/Applications/Tailscale.app/Contents/MacOS/Tailscale`. In scripts,
`TAILSCALE_BE_CLI=1` forces the bundled executable into CLI mode. Port proxying
works with the sandboxed App Store and Standalone variants; direct file and
directory serving does not.
([Tailscale CLI on macOS](https://tailscale.com/docs/reference/tailscale-cli#using-the-tailscale-cli);
[Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve).)

Implementation implications:

- Resolve and record an absolute CLI path during `doctor`; do not edit shell
  startup files or install CLI integration.
- Set `TAILSCALE_BE_CLI=1` in the subprocess environment when using the bundled
  macOS app binary.
- The adapter should proxy a loopback HTTP origin. It should not depend on
  Tailscale's file-serving support.

### Availability is inherently host-bound

Tailscale states that a Serve-backed development server is reachable as long
as the development device is online and connected to Tailscale. Disconnecting
with `tailscale down` prevents Tailscale connectivity. A per-user LaunchAgent
also belongs to a user login session; Apple starts per-user agents when the
user logs in and terminates them when the user logs out.
([Serve examples](https://tailscale.com/docs/reference/examples/serve);
[Tailscale CLI: down](https://tailscale.com/docs/reference/tailscale-cli#down);
[Apple, Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html).)

Every handoff must therefore say the preview is unavailable when the Mac is
asleep or off, the relevant user is logged out, the origin is unhealthy, or
Tailscale/network connectivity is lost. `--bg` persistence is not an uptime
guarantee. Tailscale also documents unattended operation as unavailable on
macOS. ([Run Tailscale unattended](https://tailscale.com/docs/how-to/run-unattended).)

## Ordinary Serve versus Tailscale Services

Tailscale Services provide a stable service MagicDNS name and TailVIP that are
decoupled from any one host and can route to multiple approved hosts. They are
useful for deliberately managed, durable internal services. Setup requires an
active tailnet, Tailscale 1.86.0 or later on hosts, Owner/Admin/Network admin
permissions, a service definition in the admin console, and a host using a
tag-based identity. A user-authenticated device cannot be a Services host.
([Tailscale Services](https://tailscale.com/docs/features/tailscale-services),
last validated 2026-02-02.)

Applying a tag removes user authentication; Tailscale says tags are for
non-human/service devices and should not authenticate end-user devices such as
MacBooks. ([Tailscale tags](https://tailscale.com/docs/features/tags), last
validated 2025-12-04.)

Policy:

- Default to ordinary Serve on the current user-authenticated development Mac.
- Enable a Services adapter only when the manifest names a pre-existing
  `svc:<name>`, the current host is already intentionally tag-authenticated,
  an administrator has defined/approved the service or configured
  auto-approval, and the user has deliberately opted into that topology.
- Never tag or reauthenticate the developer's Mac, create a tailnet service,
  edit policy, or approve an advertisement from `showroom`.
- Services start in background mode automatically. Verification must check the
  configured endpoint and approval/advertisement state; pending approval is
  not a successful preview.
- Services cleanup should first run `tailscale serve drain svc:<name>` so new
  connections stop while existing connections close, then remove only the
  owned endpoint with the original flags plus `off`. `tailscale serve clear
  svc:<name>` is acceptable only if the registry proves the entire named
  service configuration is exclusively manager-owned. Never use reset.
  ([Services lifecycle](https://tailscale.com/docs/features/tailscale-services#common-scenarios).)

## `launchd` supervision

### Domain and installation model

Use a per-preview **LaunchAgent** in `gui/<uid>`, not a root LaunchDaemon.
Apple defines LaunchAgents as processes managed on behalf of the logged-in
user. User-specific agents conventionally live in `~/Library/LaunchAgents` and
are loaded at login, while `launchctl` is the supported interface for loading
and unloading agents. ([Apple Service Management](https://developer.apple.com/documentation/servicemanagement/);
[Apple Terminal User Guide](https://support.apple.com/guide/terminal/script-management-with-launchd-apdc6c1077b/mac).)

For lease-scoped origins, keep generated plists in the manager's user
Application Support directory and explicitly bootstrap them into the current
GUI domain. This survives terminal closure and supports crash restart during
the current login session without silently installing an auto-login item.
Apple identifies `Application Support` as the location for app-managed data
and support files. ([Apple File System Programming Guide](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html).)

An optional periodic janitor that must load automatically at future logins is
different: installing its plist under `~/Library/LaunchAgents` changes
user-level persistent configuration and must require explicit approval. Use a
single manager janitor rather than one periodic job per preview.

### Job shape

Each origin plist should contain at least:

- a collision-resistant, manager-prefixed `Label` derived from the preview ID;
- absolute `Program`/`ProgramArguments` or an absolute manager wrapper that
  immediately `exec`s the configured command;
- `WorkingDirectory` set to the detected project working directory;
- an explicit, minimal environment including the allocated port where the
  project contract requires it;
- `KeepAlive: true` for the lease-scoped job (which implicitly performs the
  initial launch), relying on `bootout` for an intentional stop;
- separate `StandardOutPath` and `StandardErrorPath` under manager-owned state;
- a finite `ExitTimeOut`; and
- no custom aggressive `ThrottleInterval`.

Apple documents that launchd-managed jobs must not daemonize or fork and let
the parent exit, should handle `SIGTERM`, and can have launchd set the working
directory and redirect standard output/error. `KeepAlive` restarts a job,
implies `RunAtLoad`, and throttles rapid failures; the current macOS 26.5.2
`launchd.plist(5)` manual reports a default 10-second spawn throttle.
([Apple, Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html);
Apple-supplied local `launchd.plist(5)` manual, macOS 26.5.2 build 25F84,
accessed 2026-07-20.)

Do not use a shell's interactive startup files as hidden configuration. Resolve
the executable and required environment when the preview is created, capture
them in the registry/plist, and never write credentials into the plist or
logs.

### Exact launchd lifecycle

The current Apple-supplied `launchctl(1)` interface defines:

```text
launchctl bootstrap gui/<uid> <absolute-plist-path>
launchctl bootout gui/<uid>/<exact-label>
launchctl kickstart -p gui/<uid>/<exact-label>
launchctl print gui/<uid>/<exact-label>
```

`bootstrap` adds a service definition to a domain, `bootout` removes a service,
and `kickstart` asks launchd to run it immediately. `print` is diagnostic; its
output is explicitly not a stable API and must not be structurally parsed.
(Apple-supplied local `launchctl(1)` manual, macOS 26.5.2 build 25F84,
accessed 2026-07-20.)

Implementation implications:

- Before bootstrap, atomically create the registry record and plist with a
  unique label. Do not boot out an unexpected pre-existing label; fail on that
  ownership conflict.
- `status` should use the registered label for a bounded `launchctl print`
  diagnostic probe but use the HTTP health check as the behavioral truth. Do
  not parse `print` output for PID or state.
- To stop, remove the public-facing route first, then `bootout` the exact
  service target so `KeepAlive` cannot respawn the process. Never use `pkill`,
  process-name matching, process-group guesses, or a broad launchd domain
  operation.
- A missing exact label is already stopped. A label whose on-disk definition
  no longer matches the registry-owned plist is a conflict, not a cleanup
  target.
- Delete the plist/logs only after the route and exact launchd job are absent,
  subject to the configured evidence-retention policy.

## Safe transactional lifecycle

### Start

1. Acquire a machine-local registry/allocation lock.
2. Reconcile only resources whose registry entry and ownership metadata agree.
3. Detect the Tailscale CLI/version without installing or authenticating it.
4. Inspect ordinary Serve and Funnel status. Choose an unclaimed origin port
   and an unclaimed Tailscale-facing port; retain a bound reservation socket
   until the launchd job is ready to bind, where the implementation permits.
5. Write the pending registry entry, logs directory, and per-preview plist.
6. Bootstrap the exact `gui/<uid>` label.
7. Poll `http://127.0.0.1:<origin-port><health-path>` with a finite timeout.
8. Create the exact background Serve route only after the origin is healthy.
9. Verify the local health endpoint, the Serve route/status, absence of Funnel
   on that port, and the tailnet HTTPS health URL before marking the record
   verified.
10. On any failure, compensate in reverse order using only identifiers already
    recorded. Preserve logs and the failed record long enough to diagnose it.

Do not use `--yes` by default: the flag updates without interactive prompts.
It may be considered only for an already-authorized, exact route operation and
must never be used to bypass the interactive HTTPS setup/consent flow.

### Stop and cleanup

1. Resolve an exact registry ID; never accept a repository-wide process name
   or an unvalidated PID as ownership.
2. Re-read Serve and Funnel status. If the registered port is now Funnel-owned
   or the Serve target differs, report a conflict and do not mutate it.
3. Run the recorded `tailscale serve ... off` operation for that one route.
4. `bootout` only `gui/<uid>/<registered-label>`.
5. Confirm the local endpoint and route are absent.
6. Mark the record stopped, then remove manager-owned ephemeral files according
   to policy.

`cleanup --dry-run` must perform steps 1-2 and report the exact commands and
paths it would target without invoking them. Cleanup must never call any reset,
kill by name, remove an unregistered plist, or touch a normal Tailscale device
configuration.

### Periodic janitor

Apple supports interval-triggered LaunchAgents, but `StartInterval` firings are
missed while the machine sleeps and while a prior invocation is still running.
([Apple-supplied local `launchd.plist(5)` manual, macOS 26.5.2 build 25F84,
accessed 2026-07-20.) The janitor therefore cannot be the only reconciliation
mechanism. Every ordinary CLI command should reconcile leases first, and the
optional approved janitor should be a bounded, single-shot process with a
manager lock, dry-run-capable cleanup logic, and no `KeepAlive`.

## `doctor` checks

Read-only `doctor` should report, without trying to repair:

- macOS version and whether the GUI user domain is available;
- resolved Tailscale CLI path and `tailscale version`;
- whether the daemon is running/connected;
- whether Serve prerequisites are already enabled when a read-only interface
  can determine that; otherwise, warn that start may require interactive
  consent;
- ordinary Serve routes and Funnel routes that make ports unavailable;
- a warning if the machine/tailnet name would be disclosed through first-time
  HTTPS enablement;
- registry/plist directory permissions and whether labels are unique;
- stale records, dead origins, missing repositories/worktrees, health failures,
  and route/registry ownership conflicts;
- whether the optional periodic janitor is absent, installed, or mismatched;
  and
- explicit availability limitations for sleep, power, login session, network,
  Tailscale connection, and tailnet access policy.

## Uncertainties and residual risks

1. **Serve JSON is not a versioned contract in the public docs.** The docs say
   human and JSON status currently return different information. Keep raw
   evidence, use fixture tests from supported client versions, and fail closed
   on an unknown shape.
2. **Port creation is not documented as atomic.** Registry locking protects
   cooperating `showroom` processes, not a concurrent human Tailscale CLI
   command. Recheck immediately before and after creation; never overwrite a
   surprising route.
3. **HTTPS setup can be interactive and tailnet-wide.** There is no basis for
   silently automating first-time consent. Treat it as an explicit setup
   blocker.
4. **Certificate Transparency reveals names, not reachability.** The service is
   still tailnet-restricted, but hostname disclosure may violate a user's
   privacy expectations and must be surfaced.
5. **LaunchAgent lifetime is login-scoped.** A route may persist while its
   origin is gone after logout or a failed restart. Remote HTTP verification,
   normal-command reconciliation, and the optional approved janitor are all
   needed.
6. **Development servers vary in signal and child-process behavior.** The
   manager wrapper must `exec` the server and tests must cover servers that
   spawn children; launchd's exact-label cleanup must not devolve into broad
   process matching.
7. **Ordinary Serve has a device-scoped hostname.** It is appropriate for an
   active local preview, not high availability. Services solve stable naming
   only when a deliberately configured tagged-host topology already exists.
8. **Official Funnel pages disagree about its default enablement.** The Serve
   overview says Funnel is enabled by default, while the Funnel overview says
   it is disabled by default. The adapter must not depend on either statement;
   it must avoid Funnel commands and inspect actual Funnel status.

## Sources consulted

All web sources are first-party and were accessed 2026-07-20.

- Tailscale, [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)
- Tailscale, [`tailscale serve` command](https://tailscale.com/docs/reference/tailscale-cli/serve)
- Tailscale, [Serve examples](https://tailscale.com/docs/reference/examples/serve)
- Tailscale, [Tailscale Funnel](https://tailscale.com/docs/features/tailscale-funnel)
- Tailscale, [`tailscale funnel` command](https://tailscale.com/docs/reference/tailscale-cli/funnel)
- Tailscale, [Tailscale Services](https://tailscale.com/docs/features/tailscale-services)
- Tailscale, [Group devices with tags](https://tailscale.com/docs/features/tags)
- Tailscale, [Tailscale CLI](https://tailscale.com/docs/reference/tailscale-cli)
- Tailscale, [Enabling HTTPS](https://tailscale.com/docs/how-to/set-up-https-certificates)
- Tailscale, [Run Tailscale unattended](https://tailscale.com/docs/how-to/run-unattended)
- Apple, [Service Management](https://developer.apple.com/documentation/servicemanagement/)
- Apple, [Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- Apple, [Script management with launchd in Terminal](https://support.apple.com/guide/terminal/script-management-with-launchd-apdc6c1077b/mac)
- Apple, [File System Programming Guide](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html)
- Apple-supplied `launchctl(1)` and `launchd.plist(5)` manuals from macOS
  26.5.2 (build 25F84), accessed locally and read-only on 2026-07-20
