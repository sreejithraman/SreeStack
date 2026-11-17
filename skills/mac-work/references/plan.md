# Shared Mac coordination

Finish line: **Try**, built, proved and shown locally. No review, PR, push,
merge, host activation or migration of existing holds in this slice.
Integration and release owner: parent session. Admission implementation owner:
this slice. Branch ownership is serialized. Current main is the base.

## Contract and acceptance

One host-wide admission configuration, pinned runtime and state must serve all
providers and projects. Start with Block agent-task-queue and one heavy command
at a time. Queue wait and execution deadlines are separate. Stable task handles
and receipts retain owner, worktree, revision, command, deadlines and results;
late reads never submit again. Cancellation, server death and restart must retain
capacity until every owned descendant stops. A failed upstream fitness gate
blocks activation; keep counterexamples and propose a bounded adapter or patch,
not a replacement scheduler. Routing is cooperative, not raw-shell prevention.

SimLock owns device lifecycle. T3's exact bound driver owns interactive UI.
Prepare builds before acquiring devices where supported, consume the same build
artifacts, and use one bounded acquisition order. Keep global=4, iOS=4,
Android=1; keep slim Android/iOS defaults and explicit full overrides. Diagnose
pressure and show results in T3 before adding pressure enforcement. Increase
capacity only after representative matched workload measurements. Installation,
upgrade and rollback must preserve active work and existing coordination holds.

## Tasks

1. **Qualify and expose heavy-command admission**
   Outcome: the upstream candidate has a reproducible fitness verdict and precise
   repair inputs. Qualification alone does not complete production admission.
   Proof: independent lightweight clients test atomic admission, wait versus
   execution deadlines, queued/running cancellation, crash/restart, lingering
   descendants, stable reads and mismatch rejection in private state.
   Inputs: approved spec above; isolated worktree/runtime; Block source pin;
   serialized branch/commit ownership. No hardware jobs or live state.
   Blocked by: None.
   Status: qualification accepted by parent; production admission remains required
   and incomplete. See [findings](fitness.md) and [repair proposal](repair.md).
   Finish line: Try. Stop before review/PR/merge; activation requires passing fitness.

1a. **Repair dependency lifecycle without replacing admission**
   Outcome: a maintained pinned patch repairs nondestructive initialization,
   records launch ownership, and retains unresolved permits and receipts.
   Proof: real independent CLI/MCP processes, repeat cold-start/cancel/crash
   probes, quarantine/restart/no-replay assertions, and artifact/hash refusal.
   Inputs: task 1 accepted qualification; parent-authorized local dependency
   repair; no reliable Mac detached-lineage seam. Default quarantine is safe
   blocking, not automatic availability. Serialized branch ownership in this slice.
   Blocked by: 1.
   Status: local experimental patch/build recipe implemented. Universal safety
   and usable automatic completion remain incompatible without a narrower
   enforceable contract or containment seam; see [repair boundary](repair.md).
   Finish line: Try; no host activation, upstream publication or handoffs.

1b. **Settle and expose usable canonical admission**
   Outcome: one run/status/cancel route serves providers/projects with a shared
   host config/runtime/state, stable operation IDs and complete receipts.
   Proof: real mixed clients share root capacity 1; deadline/cancel/restart and
   supported workload cases pass without unsafe release or permanent quarantine.
   Inputs: parent acceptance of an enforceable workload/containment boundary;
   pinned repair; owner/worktree/revision/config/receipt contracts; parent owns
   integration. An unrestricted launcher is not justified by group-only tests.
   Blocked by: 1a and the unresolved operational-boundary decision.
   Status: blocked; no production launcher or settled host config contract.
   Finish line: Try; stop before activation/review/PR/merge.

2. **Integrate build and device handoffs**
   Outcome: project runners and agent skills use the fixed admission contract,
   then SimLock/T3 without duplicate ownership or indefinite nested holds.
   Proof: synthetic integration checks cover acquisition order, bounded waits,
   cleanup and exact artifact/task/lease identity; parent runs hardware proof.
   Inputs: task 1b's accepted CLI/config/receipt contracts; integration owner parent;
   existing lifecycle rules and holds; global4/iOS4/Android1; slim/full choices.
   T3 device_open has no established admission hook; a supported bounded session
   or native seam needs a settled design. Device-open coverage remains pending.
   Blocked by: 1b (including accepted ownership boundary).
   Finish line: Try; no live hold migration or host activation.

3. **Expose pressure and command results in T3**
   Outcome: owners can attribute pressure and inspect queue wait, execution,
   failures and receipts from T3; signals do not change admission policy.
   Proof: synthetic workloads generate correctly attributed, secret-free results;
   explicit missing/stale signal cases; parent observes the shared T3 result.
   Inputs: fixed task 1b receipt schema; task 2 run/lease handoffs; parent integration
   owner. Shares skill docs/config with task 2: serialize edits or assign fields.
   Blocked by: 2 for complete result attribution.
   Finish line: Try; no new pressure enforcement.

4. **Prove representative hardware workflows**
   Outcome: real iOS/Android builds, slim/full devices and exact T3 UI routing
   work under admission while retained devices and old holds remain safe.
   Proof: parent-owned mixed-client hardware run with command/build/lease receipts,
   bounded cleanup and cancellation; T3-visible evidence.
   Inputs: parent owns hardware and integration; available task-owned devices;
   same artifacts across build/test; existing holds remain with their owners.
   Blocked by: 2, 3.
   Finish line: Try; stop before rollout.

5. **Prepare installation, upgrade and rollback**
   Outcome: a managed shared installation can verify pins/config, detect drift,
   and safely drain or stop for upgrade/rollback without losing active ownership.
   Proof: disposable install/upgrade/rollback with active/queued tasks and mismatch
   refusal; fresh process sees the same authoritative configuration.
   Inputs: task 1b accepted runtime contract; parent integration owner; no live activation.
   Blocked by: 1b.
   Finish line: Try, documented and locally proved only.

6. **Pilot and migrate cooperative callers**
   Outcome: selected callers adopt the tested route; old holds move only with their
   owners; raw-shell bypass limitations and recovery are visible.
   Proof: parent records the caller inventory, owner-approved transitions, rollback
   and real pilot receipts. Existing holds stay intact until adopted.
   Inputs: parent release decision for live activation and named hold owners.
   Blocked by: 4, 5.
   Finish line: Try release task; stop for parent before live changes.

7. **Measure and decide capacity**
   Outcome: capacity stays one unless matched representative workloads justify a
   larger value without pressure or behavior regressions.
   Proof: before/after queue wait, execution, throughput, pressure and contention
   measurements using the same workload; explicit decision and tradeoffs.
   Inputs: parent owns hardware schedule and capacity decision; baseline/pilot data;
   serialize runs on the shared Mac; device limits unchanged.
   Blocked by: 6.
   Finish line: Try release task; stop for parent before capacity changes.

8. **Publish external sources and release**
   Outcome: accepted source changes and any upstream report/patch are published
   with credits/licenses, current proof and an explicit release decision.
   Proof: parent checks exact published revisions, source links and rollout state.
   Inputs: parent publishing/integration owner; explicit authorization for external
   publication; no credentials or private workload data in artifacts.
   Blocked by: accepted relevant tasks above; task 7 only for a capacity increase.
   Finish line: Try release task; no publication in the current slice.

## Dependency and shared-resource cut

Proposed stack: admission → lifecycle → handoffs → diagnostics. Only create a later layer
when its predecessor delivers its contract. Task 5 can prepare against fixed
operational contracts only after task 1b alongside task 2 with disjoint files; parent integrates it.
Task 4 and task 7 serialize actual Mac workloads. Task 6 serializes each hold's
owner transition. Task 8 is a separate outward-facing release, never implicit
in local Try. No task rebuilds the scheduler or adds kernel quotas.

## Parent integration evidence

Parent inspected clean `/Users/sree/Documents/Dev/t3code`. Public device_open
accepts hostId/deviceId/platform; `apps/server/src/mcp/toolkits/device/handlers.ts:244`
calls DeviceService.open directly. `t3 --help` has no device CLI; thread supports
list/start/send/show. No supported external queue hook is established. Task 2
must settle a bounded admission session around normal device tools or a native
integration seam before claiming coverage. These are parent findings, not
independent device proof from this slice. Parent's old-base checker passed
448 tests / 62 skills; final current-main checks remain required here.

Parent confirmed through the official GitHub API that Block main remains the
inspected 48d16da revision (commit date 2026-08-28). No newer main revision removes
the need for the local repair. Parent's corrected Android hardware lane remains
with its original owner/restoration supervisor; this slice runs only isolated
lightweight process fixtures and performs no device or live host changes.

## Parent-reported native hardware foundation

SimLock tests `a323088f` (production remains `392e0ac5`) passed the selected
native Android slim workflow through normal `slow-e2e.sh` in 474.6 seconds.
Parent reports default slim/effective RAM, explicit full/separate sources,
slim baseline copy/data isolation/mismatch, daemon restart and owned emulator
crash recovery with lease/data/animation 0.5 preserved. Guest MemTotal was
1501552 KiB slim and 4009600 KiB full; the old 2G config was not measured guest RAM.
This is native foundation proof, not queue admission or a performance claim.

Proof: `/Users/sree/.local/share/simlock-builds/android-slim-392e0ac5/hardware-proof-20261117/verdict.md`
and `hardware.log` alongside it. Parent reports the live worker restored,
connected and undrained, with zero leases/queue. Task 4 under admission remains
blocked by the canonical operational boundary and handoff integration. This
slice has not driven devices or independently rerun that owner's hardware proof.
