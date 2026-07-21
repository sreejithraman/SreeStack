# Review-surface contract

## Project manifest

Projects may check in `.preview.toml`. Omit it when detection is sufficient. The manifest is provider-neutral and may set:

- `version = 1`
- `kind`: `auto`, `web`, `ios`, `android`, `desktop`, `api`, `cli`, `library`, `infrastructure`, `data`, or explicit `evidence`
- `working_directory`: repository-relative directory
- `command`: argument array; use `{port}` where the allocated port belongs
- `port`: integer or `"auto"`
- `health_check_path`: local HTTP health path
- `hosted_provider`: provider skill name or `"native"`
- `privacy`: `"private"`, `"tailnet"`, or `"public-requires-approval"`
- `lease_hours`: positive integer
- `cleanup_policy`: `"lease"`, `"provider"`, `"pull-request"` (`"pr"` alias), or `"manual"`
- `evidence_requirements`: array such as `http`, `screenshot`, `recording`, `transcript`, or `artifact`
- `[ios]`: `project` or `workspace`, shared `scheme`, optional `target`, `configuration`, `device`, `device_type_identifier`, `runtime_identifier`, `deep_link`, `launch_arguments`, `fixture`, `recording`, and `recording_seconds`

Never place secrets, personal signing values, absolute user paths, machine hostnames, ports allocated at runtime, or Simulator UDIDs in the manifest.

The authoritative parsed form is [manifest.schema.json](manifest.schema.json). Machine registry records follow [registry.schema.json](registry.schema.json).

## Normalized record

Return these fields in JSON and human output:

- Preview/review-surface ID
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
