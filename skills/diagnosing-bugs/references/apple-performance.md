# Apple performance diagnosis

Use this branch after the parent skill has reduced the complaint to one
measurable Apple-platform workload.

## Define a comparable run

Write down the start event, end condition, target hardware, OS, build and
configuration, data set, cache or warm-up state, network conditions, and sample
count. Capture a before measurement, change one cause, and repeat the same run.
If a relevant condition changes, treat the result as a new experiment instead
of a before/after comparison.

Use Simulator to narrow code paths when it produces a faster loop. Make claims
about device performance on representative hardware, including an older
supported device when that matters. Apple's
[performance workflow](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance)
centers repeated measurement, and its
[responsiveness guidance](https://developer.apple.com/documentation/xcode/improving-app-responsiveness)
recommends testing interaction performance on real devices.

Done when the workload, environment, metric, and repetition rule are precise
enough for another person to produce a comparable capture.

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
directional; repeat enough runs to show that the pattern is stable.

After the fix, repeat the same workload and report:

- the user-visible metric and before/after values or distributions;
- target, OS, build, configuration, data, cache state, and sample count;
- the first-party hotspot or blocking path that changed;
- remaining variance and any Simulator-only limitation;
- paths to the raw traces, after checking them for sensitive data.

The branch is complete when the original performance loop is green and the
comparable after captures support the claimed cause. A faster unrelated metric
or a trace from different conditions is not completion evidence.
