# showroom operations

`showroom` is bundled with the skill of the same name and uses only Python 3.11 standard-library modules.

Run it from the source checkout:

```sh
skills/showroom/scripts/showroom --help
```

After copying the skill to the personal skills directory:

```sh
python3 ~/.agents/skills/showroom/scripts/showroom --help
```

An optional executable symlink on `PATH` is a user configuration change; create it only with explicit approval.

## Commands

- `start`: detect the project and return an existing healthy lease or start the selected local adapter.
- `status [id]`: return one normalized record. Without an ID, resolve the current worktree/profile.
- `list`: list machine records.
- `verify [id]`: exercise the adapter's real surface and update verification evidence.
- `renew [id] [--hours N]`: renew a lease.
- `pin [id]` / `unpin [id]`: disable expiration or create a fresh lease.
- `stop [id]`: stop only exact registered resources.
- `cleanup [--dry-run]`: reconcile expired, missing-worktree, stopped, and stale local-resource records. Dry-run includes exact adapter commands and paths when available.
- `doctor`: report state-directory and platform prerequisites without repairing them.
- `register`: normalize an externally created hosted or evidence-only surface.

Use `--json` for Codex workflows. Exit code `0` indicates command success, `1` indicates a completed but unhealthy verification/doctor/cleanup result, and `2` indicates invalid input or a blocked operation.

Each stored handoff renders lifecycle commands with the exact Python interpreter, bundled script path, and registry state directory used to create it. They remain runnable without installing a global `showroom` symlink.

## Project discovery

Showroom owns no project dotfile. It detects common project files and uses checked-in native run paths. Web projects use an existing `dev` or `start` package script. iOS projects use checked-in Xcode containers and shared schemes. When a repository has more than one valid path, use its own tooling to create the surface and then call `showroom register`.

The registry definition is in the skill's `references/registry.schema.json`.

## State and leases

On macOS, machine state lives under `~/Library/Application Support/showroom`. Other platforms use `$XDG_STATE_HOME/showroom` or `~/.local/state/showroom`. Tests and isolated automation may set `SHOWROOM_STATE_DIR`.

Registry updates use a machine lock and atomic replacement. Local leases default to 24 hours; ad hoc hosted registrations owned by `showroom` default to seven days. Provider- and pull-request-owned records have no guessed expiration, and pinned records have no expiration. Normal commands reconcile leases; this version does not install a periodic user LaunchAgent janitor.

Adapter allocation and exact external mutations use cross-process locks scoped to the shared Serve or Simulator namespace, preventing concurrent worktrees from claiming the same listener or template without blocking unrelated platform adapters. iOS subprocesses have a bounded 20-minute ceiling. Verification commits with compare-and-swap semantics so a slow health check cannot overwrite a concurrent pin, renewal, or stop. Interrupted starts recover from exact Showroom ownership metadata.

## Web-local approvals

The web-local adapter requires both explicit flags because it loads a lease-scoped GUI LaunchAgent and changes exact Tailscale Serve configuration:

```sh
showroom start --approve-persistence --approve-tailscale-config --json
```

Only pass those flags after the user has authorized the actions. The adapter never invokes Funnel, Serve reset, process-name kills, or broad launchd operations. First-time Tailscale HTTPS enablement remains an interactive blocker because it can publish the machine and tailnet DNS names in Certificate Transparency.

## iOS

The iOS adapter detects one checked-in Xcode container and one shared scheme. If either choice is ambiguous, use the project's native Simulator or TestFlight workflow and register the result. The adapter uses exact manager-owned Simulator IDs, per-worktree Derived Data and result bundles, and install, launch, and evidence checks. It never uses `booted`, broad Simulator cleanup, provisioning-update flags, or signing overrides.

Simulator operations require a working Xcode/CoreSimulator user session. A build without a launched app and visual evidence remains unverified.

TestFlight is deliberately outside the per-edit Simulator adapter. Use a project's existing authorized distribution workflow only for meaningful durable checkpoints, then register the resulting review surface without storing signing or App Store credentials in `showroom`.

## Hosted registration

Run the installed provider deployment skill first. Then normalize its result, for example:

```sh
showroom register \
  --adapter vercel-deploy \
  --provider vercel \
  --type url \
  --provider-resource-id dep_123 \
  --lifecycle-owner provider \
  --url https://example.invalid \
  --verification-status passed \
  --lease-hours 168 \
  --json
```

`showroom` records provider resources but does not duplicate deployment or deletion logic from provider skills. Provider- and pull-request-owned resources are not deleted by generic cleanup. `showroom stop` on such a record stops only the local registration and marks its verification stale; the external resource remains owned by its provider or pull-request lifecycle.
Registered URLs are health-checked through a provider-neutral HTTP probe. Artifacts are checked for existence. A recorded command is not considered verified until its execution transcript or equivalent evidence is attached.
