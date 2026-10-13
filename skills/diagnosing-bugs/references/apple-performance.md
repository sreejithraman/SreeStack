# Apple performance diagnosis

Use this branch after the parent skill has reduced the complaint to one
measurable Apple-platform workload.

Use [measurement validity](measurement-validity.md) for benchmark checks and
verdicts; this reference adds Apple target and capture requirements.
For a requested estimate, apply the shared ballpark rules and the target
guidance below. Use the capture steps when tracing is needed for diagnosis or
the requested evidence.

## Choose the target

Record the hardware, OS, and build with each capture, using the shared
measurement procedure for workload, comparison conditions, and repetitions.

Use Simulator to narrow code paths when it produces a faster loop. Make claims
about device performance on representative hardware, including an older
supported device when that matters. Apple's
[performance workflow](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance)
centers repeated measurement, and its
[responsiveness guidance](https://developer.apple.com/documentation/xcode/improving-app-responsiveness)
recommends testing interaction performance on real devices.

Done when the selected target supports the intended claim or its limitations
are explicit.

## Select the profiler from the symptom

Use Instruments through Xcode for interactive work. For repeatable captures,
discover the templates and options installed with the active Xcode:

```bash
xcrun xctrace list templates
xcrun xctrace help record
```

Choose from what is installed. Typical mappings include CPU or Time Profiler
for CPU work, Hangs or Animation Hitches for responsiveness, Allocations or
Leaks for memory, and subsystem-specific instruments for networking, file I/O,
Swift concurrency, or SwiftUI updates. Apple's
[Performance and metrics](https://developer.apple.com/documentation/xcode/performance-and-metrics)
documentation is the current index for these tools. Instruments releases add
and rename capabilities, so avoid hard-coding a template or command that local
help does not confirm.

ETTrace is optional. Use it when the project already supports it or the user
chooses it for a Simulator investigation. Record its version and temporary app
wiring, and remove that wiring after the capture. Instruments and `xctrace`
remain the portable default.

Done when the selected profiler can distinguish at least two ranked
hypotheses, and a baseline artifact has been saved with its run metadata.

## Read the trace and prove the change

Restrict analysis to the measured interval. Separate app-owned work from system
activity, verify that first-party frames are symbolicated, and identify the
call path or wait that dominates the user-visible delay. Sampling evidence is
directional; apply the shared repeatability and verdict rules when using it to
support a measurement claim.

Alongside the shared measurement report, include:

- the hardware, OS, and build used for the capture;
- the first-party hotspot or blocking path that changed;
- sampling limits and any Simulator-only limitation;
- paths to the raw traces, after checking them for sensitive data.

For a repair, completion requires the original performance loop to be green,
the shared measurement verdict to support the claimed effect, and these Apple
target and capture requirements to hold. An inconclusive measurement cannot
establish a speedup.
