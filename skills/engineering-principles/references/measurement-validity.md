# Measurement validity

Use this for performance baselines, comparisons, and reported speedups or
regressions. A faster number supports a decision only when it measures correct,
completed work under comparable conditions.

## Define and inspect the measurement

State the claim, metric and unit, timed start and end, workload, and intended
environment before running. Read the harness to see what it counts, awaits,
and excludes. Record the revision, build settings, data, concurrency, cache
state, and relevant resource contention for each side.

Check these facts with run evidence:

- **Work and correctness:** the intended code ran inside the timed interval,
  asynchronous or lazy work completed, and its result was consumed and correct.
  Count failed requests, rejected operations, timeouts, and retries alongside
  successful work. Fast errors or skipped work cannot establish a speedup.
- **Comparable settings:** use equivalent production-relevant builds, versions,
  data, batching, pools, indexes, and warm or cold caches. Tune a setting that
  unfairly limits one side before choosing between implementations. If it cannot
  be tuned, report the configuration comparison and leave the adoption verdict
  inconclusive.
- **Bottleneck:** locate the limiting resource or code path with a separate
  profiling run or appropriate system counters, including the load generator.
  Keep instrumentation overhead out of reported timings. Reading code alone
  does not establish the measured limiter.
- **Plausibility:** compare the claimed gain with the changed portion's cost
  and the available CPU, disk, or network capacity. A gain beyond those bounds
  calls for checking caches, units, measurement boundaries, and missing work.
- **Repeatability:** choose repetitions appropriate to the run cost and noise;
  interleave comparison sides to distribute warm-up and environmental drift.
  Report run count and spread, using the median or another justified statistic.
  A gap comparable to variation does not establish a difference. Use the
  harness's statistical method when available and fitting.
- **User relevance:** pair a microbenchmark with the end-to-end operation the
  user waits for, under realistic sizes and concurrency. State how much of that
  operation the changed portion accounts for.

For an explicitly requested ballpark, one run can suffice: still confirm
correct, completed work, give its conditions, and label it a single-run
estimate. Choosing between options needs comparable repeated evidence.

## Decide and report

Report faster, slower, no measurable difference, or inconclusive. Include
before and after values with units, conditions, run count, spread, and the
evidenced bottleneck. Link raw measurements rather than filling a PR with them.

Keep the comparison inconclusive when work or correctness was not checked,
settings were unfair, or the evidence cannot explain the claimed gain. Name
the missing fact and the cheapest next measurement. A microbenchmark alone
supports only that workload, not an end-to-end speedup.
