# Deliver a development build to a physical device

Use this procedure when the user needs a native app installed on a physical
device. Follow the host's device contract before choosing tools or attempting
recovery. This procedure does not expand its supported operations, recovery
limits, or the task's authorization. Simulator and emulator allocation stays
with [Simulator Lifecycle](../../simulator-lifecycle/SKILL.md).

## Recover the established delivery path

Read the project's verification and delivery records, scripts, and previous
successful build commands before choosing a signing or connection remedy.
Match those records to the current app, target, toolchain, and requested build;
history supplies a candidate setup, not proof that it still works.

Reuse a compatible approved setup without changing production signing
configuration. Preserve application identity, data access, and existing app data.
Check the artifact's signing compatibility and required capabilities before an
in-place install. A required capability the local build cannot support remains
a blocker. Keep private keys, credential values, raw profiles, and unnecessary
device metadata out of shared output.

For iOS, inspect existing signing identity and profile metadata and any approved
local entitlement overrides before requesting account sign-in or provisioning
changes. A stock build's account or entitlement error does not establish that
the project's local delivery path needs new credentials.

For that iOS build, preserve app and extension identifiers, private and shared
Keychain groups, and required entitlements. Check signed artifacts against those
requirements and profile coverage before installing. A documented local
capability exception, such as unavailable APNs, remains local to that build;
report its effect on what the user can try.

Keep exact overrides, asset locations, commands, capability limits, and successful
run evidence in the project. Use [Agent Login](../../agent-login/SKILL.md) when
credential delivery is actually needed, and
[App Store Connect](../../app-store-connect/SKILL.md) for authorized provisioning
or distribution work. Delivery alone does not authorize account or grant changes.

## Locate the failing boundary

Separate these stages and retain the exact failed operation and error:

1. **Build and signing:** can the intended revision produce a compatible signed
   app with the required identifiers and capabilities?
2. **Discovery:** can the tooling identify the intended physical device?
3. **Direct reachability:** for wireless delivery, can the host reach the
   currently advertised device endpoint?
4. **Trusted connection:** can the platform tooling establish the trusted
   development connection and query the device? On iOS, distinguish pairing
   records from an active tunnel and Remote Service Discovery (RSD) connection.
5. **Install and launch:** can that signed artifact replace the intended app
   in place and launch with the requested entry point or arguments?

Use bounded, read-only probes supported by the current tools to distinguish
these stages. Record relevant tool/OS versions and compare prior successful
conditions before blaming compatibility or asking the user to change networks.
“Paired but unavailable” is a connection state to investigate. Discovery and
direct reachability do not establish a trusted development connection.
Ask for user action when evidence identifies a missing prerequisite; revise or
withdraw that request when later evidence changes the diagnosis.

## Recover within the current scope

Follow the host's supported recovery path and stop conditions. Preserve pairing
records, app data, network settings, and unrelated services. Unpairing, resets,
uninstalls, and global service restarts are not routine connection remedies.
Escalate an unresolved boundary with its evidence rather than cycling remedies.

A process refresh is a conditional recovery action, not a default recipe.
Consider it only when evidence points to that process, the host permits the
action, and the task authorizes its effects. Use host-supported coordination
that excludes new consumers throughout refresh and recovery. Without that
protection, preserve the shared process and escalate. Under that protection,
immediately before acting, verify the exact executable, current process identity
and UID, and absence of active connections or consumers that depend on it,
including other tasks and devices on a shared host. Uncertain ownership or
consumer state blocks the refresh.
Use the narrowest supported scope; a per-user process and a host-wide service
are different resources. Retain before/after evidence and rerun the original
failing operation. A successful retry supports recovery of that operation;
the original cause may remain unknown.

## Confirm and hand off

Independently read back the installed app's identity and build, then the running
process and intended launch entry point. Compare distinguishing evidence from
the intended artifact with the installed readback, whether using a revision,
unique build identifier, or comparable content hash. The chosen evidence must
distinguish the relevant builds; a stable app identifier, bundle location, or
reused version number alone cannot establish build identity. Independently tie
the running process to that matched build. Report a mismatch as a delivery
failure; when supported tools cannot establish a match or launch intent, mark
that claim unverified.
Build success, installation, process launch, and visual or touch acceptance are
separate claims.

When tools expose the physical interface, inspect the changed screen or flow.
Otherwise state that physical appearance and interaction remain unverified and
give the user the exact reopening path and build limitations. A Simulator
demonstration supplies evidence only for that target.

Report the final device/build and access path, remaining blockers, and evidence
locations with private metadata redacted. Explicitly retire obsolete sign-in,
network, or other pending questions so the user knows which actions still matter.
Use Verify for acceptance judgments beyond delivery, reusing current evidence.
