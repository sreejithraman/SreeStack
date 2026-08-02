# Review-surface contract

## Project discovery

Detect the project from checked-in native files and use its existing scripts, schemes, release paths, and provider setup. When discovery is ambiguous, use optional [configuration.md](configuration.md) to name stable project facts.

Keep runtime state, hostnames, ports, Simulator IDs, personal signing values, and credentials outside the repository. Machine registry records follow [registry.schema.json](registry.schema.json).

## Normalized record

Return these fields in JSON and human output:

- Showroom ID
- Type and adapter/provider
- URL, device, artifact, or command
- Source repository and worktree
- Verification status, timestamp, and detail
- Evidence and log paths
- Created, renewed, and expiration times
- Pinned state and lifecycle owner
- Availability limitations
- Commands to inspect, verify, renew, pin, unpin, and stop it

Use ISO 8601 UTC timestamps. Use `null` expiration for pinned records and provider/PR-owned lifecycles when their expiry is not known.

## Lease defaults

- Local surfaces: 24 hours.
- Ad hoc hosted surfaces: 7 days unless the provider owns cleanup.
- PR surfaces: until pull-request close.
- Pinned surfaces: no automatic expiration.

Pinning preserves the prior lease metadata so unpinning can create a fresh lease rather than immediately expiring the record.

## Verification vocabulary

- `pending`: created but not exercised.
- `passed`: exercised through the declared surface and observed healthy.
- `failed`: exercise completed and observed a failure.
- `blocked`: a concrete environmental prerequisite prevented exercise.
- `stale`: previous evidence no longer proves the current resource state.
