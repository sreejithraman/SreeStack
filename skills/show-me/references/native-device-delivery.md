# Put an app on a device

Choose a running simulator or emulator or a connected device by what the user needs to
try. An iPhone install can be right even when earlier checks ran on a simulator.

Use a beta path such as TestFlight only when the user named it or says yes. Asking for
the app on their phone isn't a yes, because an upload can reach other testers.
[App Store Connect](../../app-store-connect/SKILL.md) owns that upload and its checks.

Use Verify's [iOS guide](../../verify/references/ios.md) for builds and device
operations, and the host's device tools for devices. Follow the host's device contract. This guide adds no operations,
recovery steps, or authorization to it.

Label evidence by target: a simulator capture says nothing about a physical device.
If the user named a target and it's unavailable, report the gap and name any secondary
showing.

Install only within the task's scope. Keep existing app data and unrelated devices. Reset,
uninstall, or create a device only when the task needs it and allows it.

An install doesn't show an interaction. Add captures or a demonstrated flow when they
help.

## Simulators and emulators

Use [Simulator Lifecycle](../../simulator-lifecycle/SKILL.md) before you allocate or
hand off one. Its [finish or retain](../../simulator-lifecycle/references/workflow.md#finish-or-retain)
section owns lease renewal and data that must survive. Closing a panel doesn't release a
lease.

## Reuse the known delivery path

Read the project's verification and delivery records, scripts, and past successful
build commands before you change signing or connections. Match them to the current app,
target, toolchain, and build. A past success gives you a candidate, not proof.

Keep production signing untouched, along with the app's identity, data access, and
existing data. Check signing and required capabilities before an in-place install. A
required capability the local build can't support is a blocker. Keep private keys,
credential values, raw profiles, and needless device metadata out of shared output.

On iOS:

- Inspect existing signing identities, profile metadata, and approved local entitlement
  overrides before you ask for a sign-in or provisioning change. A stock build's account
  or entitlement error doesn't prove the project's local path needs new credentials.
- Keep app and extension identifiers, private and shared Keychain groups, and required
  entitlements. Check signed artifacts against them and against profile coverage before
  you install.
- A documented local exception, such as no APNs, stays local to that build. Report what
  it stops the user trying.

Keep exact overrides, asset locations, commands, capability limits, and run evidence in
the project. Use [Agent Login](../../agent-login/SKILL.md) when credentials are needed.
Delivery alone doesn't authorize account or grant changes.

## Find the stage that failed

Keep the exact failed operation and error, and test these stages separately:

1. **Build and signing:** does this revision produce a compatible signed app with the
   required identifiers and capabilities?
2. **Discovery:** can the tools identify the device?
3. **Reachability:** for wireless delivery, can this host reach the device's current
   endpoint?
4. **Trusted connection:** can the platform tools open a trusted development connection
   and query the device? On iOS, a pairing record isn't an active tunnel and Remote
   Service Discovery connection.
5. **Install and launch:** does that signed app replace the intended app in place and
   launch with the requested entry point or arguments?

Use bounded, read-only probes to separate them. Record tool and OS versions, and compare
them with past successes before you blame compatibility or ask the user to change
networks. Discovery and reachability don't prove a trusted connection. "Paired but
unavailable" is a state to investigate.

Ask the user to act only when evidence shows a missing prerequisite. Change or withdraw
that request if later evidence changes the diagnosis.

## Recover

Follow the host's recovery path and its stop conditions. For a simulator that won't
boot, use [Simulator Lifecycle's failure steps](../../simulator-lifecycle/references/workflow.md#when-a-session-fails).
Keep pairing records, app
data, network settings, and unrelated services. Unpairing, resets, uninstalls, and
global service restarts aren't routine fixes. Escalate an unresolved stage with its
evidence instead of cycling fixes.

Refresh a process only when all of these hold:

- Evidence points to that process.
- The host allows it, and the task authorizes its effects.
- Host-supported coordination keeps new consumers out through the refresh and recovery.
- Immediately before acting, you have confirmed the exact executable, process identity,
  and UID, and that nothing depends on it, including other tasks and devices on a shared
  host.

If any of these is uncertain, leave the process alone and escalate. Use the narrowest
scope, because a per-user process and a host-wide service are different resources. Keep
before-and-after evidence and rerun the failed operation. A passing retry shows that
operation recovered, but the cause may still be unknown.

## Confirm the build

Read back the installed app's identity and build, then its running process and launch
entry point. Compare something that tells builds apart, such as a revision, unique build
ID, or content hash. An app identifier, bundle location, or reused version number can't.
Tie the running process to that matched build. Report a mismatch as a delivery failure.
If the tools can't establish a match or launch intent, mark that claim unverified.

Building, installing, launching, and passing a visual or touch check are separate claims.

Inspect the changed screen or flow if the tools reach the physical interface. Otherwise
say its look and feel are unverified, and give the exact way to reopen the app and any
build limits.

Report the final device, build, and access path, remaining blockers, and evidence
locations, with private metadata redacted. Use `verify` for judgments beyond delivery.
