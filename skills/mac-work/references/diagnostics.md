# Inspect jobs and pressure

Use the selected root's report without submitting work:

```sh
MAC_WORK_ROOT/bin/mac-work report --limit 20
MAC_WORK_ROOT/bin/mac-work report --id OPERATION_ID --sample \
  --output /absolute/new-proof/report.json --json
MAC_WORK_ROOT/bin/mac-work report --sample-file /absolute/new-proof/report.json
```

Help owns flags and bounds. Reports prioritize running/recovery holds, then
queued and recent operations. Select exact IDs for old results. JSON/readable
output retains task/operation, owner, worktree/revision, queue wait, execution,
program exit, closure state, held capacity and receipt/log paths. Handoff digest
and producer identity remain in the dependent request. Logs/argv are not embedded
in the summary; their linked files remain verbatim, not automatic secret redaction.

Queue wait ends at admission (or queued closure). Execution wall time starts at
admission and includes verified group closure, which can outlast root-program
duration. Pending times end at observation. The report reconciles lifecycle state
like status; pressure never enters admission decisions. It does not submit,
cancel, force-clear, change caps or stop processes. Use the existing status/cancel
commands for exact operation actions.

Live `--sample` is a one-shot observation: timestamped kernel pressure, free-memory
percentage, swap, compressor physical/logical bytes and observed job-group RSS.
Native probes have two-second timeouts and 1 MiB output limits. Up to 100 jobs
(20 by default), 20 exact IDs and 100 displayed members per group are allowed;
large group sums include all sampled members and label truncation. Database
queries have a five-second progress budget in addition to existing bounded
lifecycle checks. No polling service, dashboard or pressure policy is installed.

`ps` RSS uses 1024-byte units, converted to bytes. Summing RSS double-counts shared
pages and is not physical footprint or causal attribution. The report records
the original anchor identity match and observed group membership; it cannot
discover arbitrary escaped descendants or establish their ownership. A missing
anchor/group is not closure authority. Receipt lifecycle remains authoritative.
Compressor physical pages and logical stored pages are separate metrics; page
size comes from vm_stat. Swap M/G units use powers of 1024. Unknown native formats,
permission failures and timeouts report unavailable rather than normal/zero.
Kernel pressure sysctl is a private macOS signal and can be absent; free percentage
is not a replacement pressure level. Its dispatch-level mapping follows
[Apple's source](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_memorystatus_notify.c#L1754)
and [event constants](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event.h).

Saved host samples retain their timestamps: older than 60 seconds is stale;
future timestamps are clock-skew. Historical imports copy only known numeric
host fields, not arbitrary private metadata. They do not resample process/lease
evidence; open the original report for that historical context. Jobs are current.
`--output` only creates a new JSON file, preserving earlier proof.

## Correlate known leases without activation

```sh
MAC_WORK_ROOT/bin/mac-work report --sample \
  --simlock /absolute/qualified/simlock --lease-id KNOWN_RUN_LEASE --json
```

Explicit `--simlock` opts into the qualified 0.7 `events --since 5m` route. It
connects to existing history/daemon without starting one, has a five-second
timeout and 1 MiB output budget, and keeps only event time/type and lease/device
IDs. Unknown versions refuse that probe. Ordinary status/list can launch a daemon
and are not automatic report probes. Qualification used the maintained local
build `392e0ac5a8d1168d19fb3d4447b908e05652d1e5`, not a published GitHub revision;
the local source path is `src/cli/commands/events.ts` (non-starting route at line 47).
See the [local build record](../../simulator-lifecycle/references/setup.md#establish-the-worker).
Version 0.7.0 alone does not establish that another build has identical behavior.

Recent events and caller-supplied IDs are correlation evidence, not a current
active-lease inventory, ownership proof or permission to renew/release. A quiet
or unavailable history does not prove zero leases. Use the run's existing
SimLock/T3 owner for authoritative lease reconciliation; the report never reads
or prints private configs, credentials or environment values.

MCP work_report(limit, operation_ids, sample, simlock, lease_ids) uses the same
installed config/database and bounded samplers. `diagnostics_fitness.py --root ROOT
--output NEW_DIR [--simlock /absolute/simlock]` proves real CLI/MCP attribution,
queue/execution separation, live RSS, stale/missing signals and recovery holds
with lightweight fixtures. Parent owns representative workload measurements,
T3 display and any capacity decision; observation alone does not justify an increase.
