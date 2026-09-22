# Adoption and verification

Apply only the settings the user asked to adopt or accepted from a completed
audit. Keep each batch small enough to attribute new diagnostics or failures.

## Establish the baseline

Before editing:

- account for existing user changes;
- record Xcode, SDK, scheme, configuration, and destination;
- save the effective values for the settings in the batch;
- run the normal build for each affected target;
- record existing warnings and analyzer findings separately.

If a baseline build fails, continue only when the security change can be
validated independently. Do not attribute the existing failure to the audit.

## Choose the owner and surface

Modify the highest-level source that intentionally owns the value. Choose the
fastest reliable way to edit it:

1. project generator configuration;
2. shared or target `.xcconfig` with the correct conditional scope;
3. a native or structured Xcode project API, or Xcode through computer use,
   whichever makes the intended project change faster and easier to verify.

Avoid textual search-and-replace in `.pbxproj`. Preserve `$(inherited)`, SDK or
architecture conditions, configuration-specific values, and target overrides.

## Apply batches

Use this order when the audit recommends more than one category:

1. **Compiler and analyzer diagnostics.** Enable only language-relevant,
   supported settings. Build or analyze, then resolve findings before escalating
   them to errors.
2. **Enhanced Security.** Apply compatible compiler hardening to relevant
   source-built targets and runtime entitlements to supported executable
   products. Include and verify `ENABLE_CPLUSPLUS_BOUNDS_SAFE_BUFFERS` for C++
   targets when the active capability definition enables it. Validate build
   settings and runtime entitlements together.
3. **Advanced protections.** Handle C bounds safety, hardware memory tagging,
   checked pointer arithmetic, and other separately enabled protections as
   focused work with their own device and source-migration plan.

After each batch, re-query effective settings. A line added to an `.xcconfig`
is not proof when a later include or target override wins.

## Verify and report

Run the smallest set that covers every changed scope:

- the project's normal build for every affected discovered configuration, or
  representative optimized and nonoptimized configurations when exhaustive
  coverage would be redundant;
- Analyze for affected C, C++, Objective-C, or Objective-C++ targets;
- tests that compile and exercise changed low-level code;
- `manual-verify` for affected launch, extension, IPC, plug-in, or allocation
  workflows;
- archive or distribution validation only when the task includes release
  configuration, signing, or distribution.

When a batch fails, identify the exact new diagnostic, setting, target, and
configuration. Fix compatible source issues when they are within scope. Leave a
setting deferred with a concrete blocker when adoption requires broader
migration; do not weaken unrelated settings to make the build pass.

For every changed setting or capability, report previous and final effective
values, owning layer, covered targets and configurations, new diagnostics,
verification, and deferrals. Adoption is complete when all intended effective
values are verified and required evidence passes, or every remaining blocker is
explicitly deferred without an accidental partial configuration.
