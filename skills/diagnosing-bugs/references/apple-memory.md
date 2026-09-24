# Apple memory diagnosis

Use this branch for growing memory, abandoned objects, retain cycles,
allocation leaks, or memory-pressure termination on Apple platforms.

## Classify the symptom

Name the user flow and the memory behavior it should have when the flow ends or
repeats. Allow deferred cleanup to settle and capture the same point each time.
Distinguish these cases before choosing a fix:

- high but bounded working-set or cache use;
- an app-owned object retained past its intended lifetime;
- unreachable leaked memory or a strong reference cycle;
- memory-pressure termination, which needs system or jetsam evidence.

Simulator can make growth easier to inspect, but a green Simulator memory gauge
does not show that an iOS app is safe from device memory pressure. Apple calls
out this difference in
[Gathering information about memory use](https://developer.apple.com/documentation/xcode/gathering-information-about-memory-use).

Done when the expected lifetime or footprint is explicit, the observed signal
is repeatable, and the investigation is classified as bounded use, object
retention, an allocation leak, or memory-pressure termination.
For an unreplayable field termination, a matching jetsam report can support
provisional classification; it does not establish a repeatable signal or verify
a fix.

## Inspect object lifetime

Use this path when an app-owned object or allocation survives past its intended
lifetime.

Use Xcode's Debug Memory Graph for object relationships. When allocation stack
traces are needed, enable Malloc Stack in the scheme's Run diagnostics before
capturing the graph. Use Instruments Allocations and Leaks for a time-based
investigation. Export a memory graph when offline comparison helps. Apple's
[memory-use guide](https://developer.apple.com/documentation/xcode/gathering-information-about-memory-use)
describes these paths and notes that exported graphs can be inspected with
`vmmap` and `leaks`.

For command-line inspection, query the installed tools before relying on an
option:

```bash
leaks -help
vmmap -help
```

Start from the first app-owned object whose intended lifetime has ended. Trace
the retaining edge or ownership path back to source. Grouped counts can locate
a candidate type; they do not explain why it survives.

Memory graphs may include object descriptions and application data. Apply the
[runtime privacy rules](apple-runtime.md#protect-diagnostic-data) before
retaining or sharing them.

Done when evidence identifies an app-owned ownership path or allocation site,
or rules memory retention out in favor of a different cause.

Remove or shorten the incorrect ownership edge at the narrowest correct seam.
Deferring the allocation only counts as a fix when the intended lifetime also
changes. Run the same lifecycle before and after. Prove that the named object
or path no longer survives past its expected release point and that the
original user flow still works. A smaller graph, lower RSS, or lower total
allocation count alone does not prove a leak is fixed.

This path is complete when the specific lifetime violation is gone under the
same reproduction conditions.

## Inspect suspected memory-pressure termination

On iOS, iPadOS, tvOS, visionOS, and watchOS, obtain the matching jetsam event
report from the affected device or release-diagnostics flow. Confirm that the
jettisoned process belongs to the app, then record the device model, OS, build
UUID, app state, termination reason, page size, resident pages, lifetime
maximum, and relevant coalition processes. Convert page counts with the
report's own page size.

Apple's
[jetsam report guide](https://developer.apple.com/documentation/xcode/identifying-high-memory-use-with-jetsam-event-reports)
describes these fields and cautions that a foreground disappearance is not by
itself proof that memory pressure killed the app. If the jettisoned process is
different, return to runtime crash diagnosis.

On macOS, start with the [runtime reference](apple-runtime.md) to identify the
actual termination evidence; macOS does not use this jetsam report path. When
the evidence implicates app footprint, reproduce the workload with Instruments
and observe system memory pressure and the app process in Activity Monitor.
Apple's [release-build testing guidance](https://developer.apple.com/documentation/xcode/testing-a-release-build)
describes the relevant macOS memory statistics.

Reproduce the same workload on representative hardware. Use Xcode's memory
report and Instruments Allocations to locate the categories or phases that
drive the peak, including bounded allocations that are individually valid but
collectively too large. A bounded working set can still require a fix when its
peak exceeds the device budget.

After the repair, repeat the device workload and compare peak footprint under
equivalent build, data, app state, and system conditions. Because available
system memory varies, use repeated runs and report the range. Completion means
the app survives the original workload on the affected device class and the
peak-footprint evidence supports the change; absence of one termination is not
enough.

## Report the result

Report the target and build, exact lifecycle, capture point, affected app-owned
types or resources, ownership path or footprint categories, repair,
before/after evidence, and remaining memory noise.
