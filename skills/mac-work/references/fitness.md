# Original upstream fitness findings

This records the unpatched baseline. The local lifecycle repair (`lifecycle.md`)
adds separate group-closure and quarantine proof without clearing these original
counterexamples or establishing universal automatic availability.

Candidate: Block agent-task-queue commit
`48d16da41f57801bbf9462ed2df923713978b6ae`, package 0.4.1.
Test platform: this shared Mac, arm64, Python 3.12.12. Tests used new private
queue state and lightweight sleep/marker processes, never compiler jobs or devices.

## Verdict

**Blocked for heavy-command admission.** Every complete run failed the descendant
lifetime checks. Concurrent first use failed in some runs and passed in others;
a later pass does not clear the reproduced intermittent counterexample.

| Assertion | Observation |
| --- | --- |
| Warm cross-process root admission | Four CLI processes in separate leaf queues completed; observed peak 1. |
| Concurrent first use | Earlier run: exits `[0,1,0,0]`, observed peak 2; another run peak 1 with one setup failure. Final run passed. Still failed overall. |
| Queue wait versus execution | CLI waited over 2 seconds with execution limit 1 second, then succeeded. Mixed CLI/MCP case also passed. |
| Execution timeout | CLI exited 124; MCP reported timeout; following client ran. The timed-out fixture never emitted its normal end. |
| Queued cancellation | CLI and MCP cancelled jobs never started. |
| CLI running cancellation | CLI exited 130; the next job started while its signal-resistant descendant still ran. Failed. |
| CLI owner death | Owner killed with SIGKILL; the next job started while its old descendant ran. Failed. |
| Successful CLI parent exit | CLI reported success while its owned background descendant remained; next job started. Failed. |
| MCP ordinary group cancellation | Queued/running cancellation passed; resistant descendant in the same group stopped. |
| MCP server death/restart | Replacement server started next job while old descendant ran; old task status became unknown. Failed. |
| MCP detached descendant cancellation | Cancel returned, next job started, detached descendant remained live. Failed. |
| Successful MCP parent exit | Success returned while a background descendant remained; next job started. Failed. |
| Late result read | Fresh server returned success for the same task; fixture start count stayed 1. Passed for completed tasks. Crash case above failed. |

The gate observes independent fixture events plus a live `ps` identity check;
it does not infer process closure from upstream's terminal status. The detached
fixture uses `start_new_session=True` and ignores SIGTERM. Ordinary lingering
fixtures ignore SIGTERM within the original group. Each one has a bounded
20-second lifetime, and the harness kills its owned groups during cleanup.

## Compatibility and source evidence

An unconstrained install selected FastMCP 4.2.0 and failed server import:
`ModuleNotFoundError: No module named 'fastmcp.tools.tool'`.
Pinning FastMCP 2.14.4 exposed Fakeredis 2.40.0 incompatibility with pydocket:
`ImportError: cannot import name 'FakeServer' from 'fakeredis.aioredis'`.
Pinning Fakeredis 2.32.1 allowed the real MCP tests to run. `runtime.lock` keeps
that tested dependency set, rather than silently relying on latest packages.

The [pinned cleanup implementation](https://github.com/block/agent-task-queue/blob/48d16da41f57801bbf9462ed2df923713978b6ae/queue_core.py)
sends SIGTERM then deletes orphan admission rows without observing descendant
closure. Its generic database recovery unlinks database/WAL files after an
OperationalError, explaining the first-use race. The CLI cleanup waits for its
shell then releases; normal CLI and MCP completion also release after parent
completion. MCP's own cancellation improves ordinary group cleanup, but cannot
make the shared orphan path safe or contain detached descendants.

The [CLI](https://github.com/block/agent-task-queue/blob/48d16da41f57801bbf9462ed2df923713978b6ae/tq.py)
and [MCP server](https://github.com/block/agent-task-queue/blob/48d16da41f57801bbf9462ed2df923713978b6ae/task_queue.py)
were both invoked with `--data-dir PRIVATE_STATE --queue-capacity heavy=1`.
Overrides remain process-local. Every tested client used the same root cap;
child queues differed in the concurrency probe. No default shared `/tmp` queue
or existing host hold was used.

## Retained evidence and limits

The owner's report links the absolute private-Git proof path. Each new run keeps
`verdicts.json`, runtime identity, fixture events, process output and MCP requests/
responses. Earlier runs remain beside the final run to retain intermittent
failures and dependency blockers. Scratch state and task-owned processes are
removed; setup keeps only its private runtime until the owner removes it.

The repository's fast tests exercise only qualification refusal using metadata
stubs. They do not substitute for these real upstream subprocess gates. The new
refusal check went red for an incompatible transitive pin, then green after the
runtime check validated every locked dependency version. Package/source mismatch
and missing-runtime guard cases also pass without queue installation.

No canonical production CLI, shared host configuration, activation, install
upgrade/rollback, hardware workload, pressure policy or T3 device-open admission
was proved here. No fresh-model skill discovery/invocation trial ran; this slice
was explicitly assigned one writer with no further agents. Finite process probes
establish observed counterexamples and bounded passing cases, not a general
formal proof of every possible interleaving. See `repair.md`
and the parent-owned remaining tasks in `plan.md`.
