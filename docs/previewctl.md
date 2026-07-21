# previewctl operations

`previewctl` is bundled with the `preview` skill and uses only Python 3.11 standard-library modules.

Run it from the source checkout:

```sh
skills/preview/scripts/previewctl --help
```

After copying the skill to the personal skills directory:

```sh
python3 ~/.agents/skills/preview/scripts/previewctl --help
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

Each stored handoff renders lifecycle commands with the exact Python interpreter, bundled script path, and registry state directory used to create it. They remain runnable without installing a global `previewctl` symlink.

## Manifest example

Check in `.preview.toml` only when detection needs an override:

```toml
version = 1
kind = "web"
working_directory = "."
command = ["npm", "run", "dev", "--", "--port", "{port}"]
port = "auto"
health_check_path = "/healthz"
privacy = "tailnet"
evidence_requirements = ["http", "screenshot"]
lease_hours = 24
cleanup_policy = "lease"
```

Commands are argument arrays and never implicit shell strings. `{port}` and adapter-supported placeholders are substituted without re-parsing through a shell. Working directories must remain inside the worktree.

The formal parsed manifest and registry definitions are in the skill's `references/manifest.schema.json` and `references/registry.schema.json`.

## State and leases

On macOS, machine state lives under `~/Library/Application Support/previewctl`. Other platforms use `$XDG_STATE_HOME/previewctl` or `~/.local/state/previewctl`. Tests and isolated automation may set `PREVIEWCTL_STATE_DIR`.

Registry updates use a machine lock and atomic replacement. Local leases default to 24 hours; ad hoc hosted registrations owned by `previewctl` default to seven days. Provider- and pull-request-owned records have no guessed expiration, and pinned records have no expiration. Normal commands reconcile leases; this version does not install a periodic user LaunchAgent janitor.

Adapter allocation and exact external mutations use cross-process locks scoped to the shared Serve or Simulator namespace, preventing concurrent worktrees from claiming the same listener or template without blocking unrelated platform adapters. iOS subprocesses have a bounded 20-minute ceiling. Verification commits with compare-and-swap semantics so a slow health check cannot overwrite a concurrent pin, renewal, or stop. Interrupted web starts recover from exact per-preview ownership metadata; interrupted iOS starts recover from the manager-owned Simulator registry.

## Web-local approvals

The web-local adapter requires both explicit flags because it loads a lease-scoped GUI LaunchAgent and changes exact Tailscale Serve configuration:

```sh
previewctl start --approve-persistence --approve-tailscale-config --json
```

Only pass those flags after the user has authorized the actions. The adapter never invokes Funnel, Serve reset, process-name kills, or broad launchd operations. First-time Tailscale HTTPS enablement remains an interactive blocker because it can publish the machine and tailnet DNS names in Certificate Transparency.

## iOS

Set `kind = "ios"` and add `[ios]` overrides when discovery is ambiguous. The adapter uses exact manager-owned Simulator UDIDs, per-worktree Derived Data and result bundles, and install/launch/evidence verification. It never uses `booted`, broad Simulator cleanup, provisioning-update flags, or signing overrides.

Simulator operations require a working Xcode/CoreSimulator user session. A build without a launched app and visual evidence remains unverified.

TestFlight is deliberately outside the per-edit Simulator adapter. Use a project's existing authorized distribution workflow only for meaningful durable checkpoints, then register the resulting review surface without storing signing or App Store credentials in `previewctl`.

## Hosted registration

Run the installed provider deployment skill first. Then normalize its result, for example:

```sh
previewctl register \
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

`previewctl` records provider resources but does not duplicate deployment or deletion logic from provider skills. Provider- and pull-request-owned resources are not deleted by generic cleanup. `previewctl stop` on such a record stops only the local registration and marks its verification stale; the external resource remains owned by its provider or pull-request lifecycle.
Registered URLs are health-checked through a provider-neutral HTTP probe. Artifacts are checked for existence. A recorded command is not considered verified until its execution transcript or equivalent evidence is attached.
