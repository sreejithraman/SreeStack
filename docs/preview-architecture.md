# Preview handoff architecture

## Goal

After interactive product work, produce the best available verified review surface and report it through one provider-neutral record. A review surface may be a URL, device, artifact, command, transcript, plan, or report.

The system is standalone: projects may opt in with a small manifest, but neither runtime state nor machine-specific values are committed to a project. It does not depend on `sree.world`.

## Modules and seams

`preview` is the policy module. Its interface is the user intent plus the current project. It selects a surface in this order:

1. Existing project-native PR or branch preview.
2. Configured hosted provider for durable availability.
3. Local platform adapter for active or uncommitted work.
4. Evidence-only surface.

`previewctl` is the lifecycle module. Its interface is the command surface and normalized JSON result. It owns project/worktree identity, local adapters, the machine registry, leases, verification state, evidence, and exact cleanup.

Hosted provider skills remain separate workflow modules. The `preview` skill invokes an installed provider skill and then asks `previewctl` to register its result. Provider deployment logic and credentials never enter `previewctl`.

Adapters are internal seams. The first concrete adapter is `web-local`; the second is `ios-simulator`. Other project kinds can return evidence-only records until a real adapter earns a common interface.

## Files and state

- Optional project manifest: `.preview.toml` at the repository root.
- macOS state: `~/Library/Application Support/previewctl/`.
- Other platforms: `$XDG_STATE_HOME/previewctl/` or `~/.local/state/previewctl/`.
- Registry: atomic, locked JSON with schema versioning.
- Per-preview directories: logs, evidence, generated launchd property lists, and non-secret metadata.
- macOS LaunchAgents: generated under the state directory and loaded into the current GUI user domain only after explicit authorization.

No state path, hostname, credential, provider token, generated property list, simulator UDID, or personal signing setting is committed.

## Identity and idempotency

Project identity is derived from the canonical repository common directory. Worktree identity is derived from the canonical worktree root. The stable preview ID combines the identity, selected adapter, and an optional configured profile.

`start` reconciles an existing record before creating resources. If the record is healthy it returns it; if it is repairable it repairs only registered resources; otherwise it transitions the exact record safely. `stop`, `cleanup`, lease operations, and registration are idempotent.

Registry writes use a short atomic data lock. Adapter allocation and external mutation use cross-process locks scoped to the shared Serve or Simulator namespace so concurrent repositories cannot both win a check-then-act claim while unrelated platform adapters remain independent. Slow verification updates only a still-matching lifecycle record and preserves concurrent lease changes.

The web adapter writes exact ownership metadata before its first external mutation. The iOS adapter records the UDID immediately after Simulator creation and before boot, install, launch, or capture. A stale `starting` record must consume available ownership metadata and reconcile claimed resources before a replacement start is reserved. A stale `stopping` operation records its previous state and can be resumed after the resource lock proves the prior process is gone.

## Manifest

The TOML manifest is intentionally small. Top-level fields describe `version`, `kind`, `working_directory`, `command` as an argument array, `port`, `health_check_path`, `hosted_provider`, `privacy`, `lease_hours`, and `cleanup`. Native and evidence settings live in nested tables.

Commands are arrays by default and run without a shell. This preserves argument boundaries and prevents manifests from silently becoming arbitrary shell programs. An explicitly enabled shell mode may be added later if demonstrated projects need it.

## Registry and common result

Each record includes:

- Stable preview, project, repository, and worktree identity.
- Type, adapter/provider, lifecycle owner, and provider resource ID.
- URL, device, artifact, or command.
- Origin process or launchd identity, port, and Simulator UDID where applicable.
- Verification state, timestamp, detail, logs, and evidence paths.
- Created, renewed, and expiration timestamps plus pinned state.
- Availability limitations.
- Exact inspect, renew, pin, unpin, verify, and stop commands.

Human output is derived from this record. `--json` emits the record directly so Codex and tests do not scrape prose.

## Safety invariants

- Never invoke Tailscale Funnel or create public exposure implicitly.
- Bind local origins to loopback unless a project explicitly requires otherwise.
- Never call broad `tailscale serve reset`; remove only a route proven to be owned by the record.
- Never kill a process by name or port. Act only on an exact registered process/launchd identity after ownership checks.
- Never erase, reset, or delete ordinary Simulator devices. Delete only manager-created devices whose UDID and ownership marker both match the registry.
- Never delete a provider deployment without an exact provider resource ID, lifecycle ownership, an available provider workflow, and explicit authorization.
- `cleanup --dry-run` performs no writes or external mutations.
- Installing the optional periodic janitor and changing user configuration require explicit approval.

## Phases

### Phase 1: working local vertical slice

- Project detection and `.preview.toml` parsing.
- Registry, leases, locking, atomic writes, normalized output.
- Generic command surface.
- Web origin supervision and collision-safe ports.
- Ordinary Tailscale Serve integration, health verification, logs, and exact cleanup.
- Reconciliation during normal commands; no periodic janitor installation.

### Phase 2: iOS Simulator

- Xcode discovery and Simulator build.
- Manager-owned Simulator clones for concurrent worktrees.
- Install, launch, deep links/arguments, screenshot and optional recording evidence.
- Exact clone ownership and cleanup.

### Phase 3: durable hosted surfaces

- Skill-level dispatch to installed `vercel-deploy`, `netlify-deploy`, `cloudflare-deploy`, or `render-deploy`.
- Registration of opaque provider results and lifecycle ownership.
- Project-native PR preview discovery before ad hoc deployment.

### Phase 4: optional automation and more adapters

- Explicitly installed macOS janitor after reconciliation has proven safe.
- Android, desktop, API, and richer evidence adapters based on demonstrated projects.
- Tailscale Services only for deliberately configured tagged hosts and tailnet administration.

## Acceptance checks

- Repeated starts return or repair one stable record.
- Concurrent worktrees receive distinct ports and identities.
- Expiry and pinning are deterministic under a fake clock.
- Cleanup dry-runs are byte-for-byte state preserving.
- Cleanup ignores unrelated processes, routes, simulators, deployments, and files.
- Partial start failures roll back only resources created by that attempt.
- Interrupted start and stop operations converge through exact persisted identities.
- Concurrent allocation across worktrees is serialized at the machine resource boundary.
- Web start reports success only after origin and tailnet route verification.
- iOS visual work reports evidence from a launched app, not merely a successful build.
