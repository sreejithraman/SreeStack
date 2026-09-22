# Enhanced Security

Enhanced Security is an Xcode capability with compile-time and runtime parts.
Apple's current
[Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
says `ENABLE_ENHANCED_SECURITY` enables pointer authentication, typed allocator
support, hardened C++ standard-library behavior, and security compiler warnings.
The capability also provisions hardened-process entitlements for supported
executables. Read Apple's
[Enhanced Security adoption guide](https://developer.apple.com/documentation/xcode/enabling-enhanced-security-for-your-app)
against the active Xcode version before constructing a change.

Apple warns that these checks can affect performance or stability and can turn
unsafe behavior into a deliberate crash. Treat capability adoption as a staged
hardening change informed by the app's threat model.

## Assess compatibility

For each candidate target:

1. Confirm that its product type and platform support the capability in the
   active Xcode. Apply supported compiler hardening to relevant source-built
   targets, including libraries and frameworks. Apply hardened-process
   entitlements only to supported executable products. Treat tests, DriverKit,
   and other special products according to the active capability definition.
2. Inspect all effective values cascaded by `ENABLE_ENHANCED_SECURITY`. Do not
   duplicate those settings manually or assume the cascade is unchanged across
   Xcode versions.
3. Review C and C++ diagnostics. Current Apple guidance says adding the
   capability sets `ENABLE_CPLUSPLUS_BOUNDS_SAFE_BUFFERS = YES` for the target,
   enabling standard-library hardening and making unsafe-buffer diagnostics
   errors. Include and verify that value for C++ targets. When migration blocks
   adoption, record a narrowly scoped opt-out and its remediation plan.
4. Identify custom allocation wrappers. Type-aware allocation can require
   annotations or wrapper changes; see Apple's
   [type-aware allocation guide](https://developer.apple.com/documentation/xcode/adopting-type-aware-memory-allocation).
5. Identify raw Mach IPC and unusual dynamic-library loading. Runtime platform
   restrictions can turn insecure patterns into failures; see
   [Mach IPC security restrictions](https://developer.apple.com/documentation/xcode/conforming-to-mach-ipc-security-restrictions).
6. Inventory binary frameworks and XCFrameworks. Verify their origin and
   supported architectures rather than assuming pointer-authentication
   compatibility. Apple documents Xcode's signature checks in
   [Verifying the origin of your XCFrameworks](https://developer.apple.com/documentation/xcode/verifying-the-origin-of-your-xcframeworks).

Do not disable pointer authentication merely because a binary dependency
exists, and do not add a Simulator override preemptively. Build the intended
device configuration first. If the arm64e link fails, identify the exact
incompatible artifact, prefer an updated vendor build, and scope any temporary
exception to the affected target and configuration. Validate pointer
authentication on supported physical hardware.

## Apply through the easiest reliable surface

Prefer a native Xcode capability or structured project tool when one is
available. Opening Xcode through computer use is appropriate when the Signing &
Capabilities editor can coordinate the build setting and entitlements more
reliably than direct edits. Otherwise:

- change XcodeGen, Tuist, Bazel, or other generator input instead of its output;
- change the owning `.xcconfig` when configurations already use one;
- use a structured project editor for `.pbxproj` changes;
- update an existing entitlement file only from the exact current Apple
  capability definition. Never synthesize the entitlement family from memory.

When a supported executable has no entitlement file, create the plist in the
repository through the generator or project source of truth, populate it from
the active capability definition, and wire its path through the generator or
`CODE_SIGN_ENTITLEMENTS`. Treat the compiler settings and required runtime
entitlements as one batch. If both parts cannot be represented and verified,
remove the task's partial change and defer that target.

Keep capability adoption target-specific. Preserve existing entitlement values
and explicit overrides until their purpose is known. Inspect the current
entitlement reference, including
[`com.apple.security.hardened-process`](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.hardened-process),
before editing.

## Validate

After enabling the capability:

1. Re-query effective settings for every changed target and discovered
   configuration.
2. Build every affected configuration, or representative optimized and
   nonoptimized configurations when the full matrix would be redundant. Use
   `Debug` and `Release` only when those names exist.
3. Run Analyze for C-family code and fix new diagnostics at their source.
4. Exercise launch, IPC, plug-in or framework loading, and allocation-heavy
   workflows affected by the enabled protections.
5. Validate edited plists with `plutil -lint`. Inspect the built product's signed
   entitlements with `codesign -d --entitlements :-` where applicable rather
   than relying only on the source plist.

Adoption is complete when effective settings and signed entitlements match the
intended capability, builds pass for supported destinations, and affected
runtime workflows pass. Record any target-specific exception and its reason.

Hardware memory tagging and checked pointer arithmetic require separate
hardware, OS, and rollout decisions. C bounds safety changes the C programming
model and stays outside the default Enhanced Security batch. C++ bounds-safe
buffers remain inside the current capability batch unless explicitly deferred.
