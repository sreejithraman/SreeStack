# Shared Mac coordination

Finish line: **Try**, built, proved and shown locally. No review, PR, push,
merge, live/default host activation or migration of existing holds in this slice.
Task-owned versioned Try installation/activation is authorized. The accepted
runner and combined Try installs are now parent-owned. Do not mutate, rebuild,
delete or use either root for new fitness; any new proof needs a fresh root.
Integration and release owner: parent session. Admission implementation owner:
this slice. Branch ownership is serialized. Current main is the base.

## Contract and acceptance

One host-wide admission configuration, pinned runtime and state must serve all
providers and projects. Start with Block agent-task-queue and one heavy command
at a time. Queue wait and execution deadlines are separate. Stable task handles
and receipts retain owner, worktree, revision, command, deadlines and results;
late reads never submit again. Cancellation, server death and restart must retain
capacity until the foreground command’s owned active process group stops. A failed upstream fitness gate
blocks activation; keep counterexamples and propose a bounded adapter or patch,
not a replacement scheduler. Routing is cooperative, not raw-shell prevention.

SimLock owns device lifecycle. T3's exact bound driver owns interactive UI.
Prepare builds before acquiring devices where supported, consume the same build
artifacts, and use one bounded acquisition order. Keep global=4, iOS=4,
Android=1; keep slim Android/iOS defaults and explicit full overrides. Diagnose
pressure and show results in T3 before adding pressure enforcement. Increase
capacity only after representative matched workload measurements. Installation,
upgrade and rollback must preserve active work and existing coordination holds.

## Authorized pilot boundary

The user selected **Foreground commands (Recommended)** when asked whether the
pilot should support foreground builds/tests or require containment of detached
programs. Foreground/process-group ownership is authorized, not provisional.
Commands must wait for all heavy work; background/shared daemons and escaping
process groups/sessions are unsupported. The original detached counterexample
remains known evidence outside this narrowed scope. Uncertain in-scope group
closure still retains capacity. No force-clear or policy reinterpretation is allowed.

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
   Status: qualification and canonical command pilot accepted by parent; global
   adoption remains task 6. See [findings](fitness.md) and [repair proposal](repair.md).
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
   Status: lifecycle repairs accepted by parent. User authorized the foreground
   boundary; see [ownership seam](repair.md). Runner adds atomic operation binding
   inside the same upstream state/receipt seam.
   Finish line: Try; no host activation, upstream publication or handoffs.

1b. **Settle and expose usable canonical admission**
   Outcome: one run/status/cancel route serves providers/projects with a shared
   host config/runtime/state, stable operation IDs and complete receipts.
   Proof: real mixed clients share root capacity 1; deadline/cancel/restart and
   supported workload cases pass without unsafe release or permanent quarantine.
   Inputs: user-approved foreground boundary; accepted lifecycle repair; parent
   owns integration and real-workload adoption. No detached containment claim.
   Blocked by: 1a (accepted and delivered).
   Status: runner0c4bc1c accepted, with qualified real daemon builds and public
   cancellation proved by parent. Combined handoffs/diagnostics8d4e9ec also
   accepted; both retained roots belong to parent. See [public runner contract](runner.md).
   Finish line: Try; stop before live/default activation, review, PR and merge.

2. **Integrate build and device handoffs**
   Outcome: project runners and agent skills use the fixed admission contract,
   then SimLock/T3 without duplicate ownership or indefinite nested holds.
   Proof: synthetic integration checks cover acquisition order, bounded waits,
   cleanup and exact artifact/task/lease identity; parent runs hardware proof.
   Inputs: task 1b's accepted CLI/config/receipt contracts; integration owner parent;
   existing lifecycle rules and holds; global4/iOS4/Android1; slim/full choices.
   T3 device_open has no established admission hook. Parent selected command-only
   queue admission; SimLock retains leases/boots. Automatic boot admission remains
   a separate native-integration gap, not a blocker for supported handoffs.
   Blocked by: 1b (accepted).
   Status: receipt-gated artifact seal and dependent foreground command verification
   implemented in mac-work/handoffs and accepted. Parent proved qualified daemon
   build → prebuilt app verification/seal → T3 interaction/retirement on both
   platforms in the supported local Try integration below. This does not qualify
   rebuilding those apps or queued T3 boot/cancellation. See [handoff contract](handoffs.md).
   Finish line: Try; no live hold migration or host activation.

3. **Expose pressure and command results in T3**
   Outcome: owners can attribute pressure and inspect queue wait, execution,
   failures and receipts from T3; signals do not change admission policy.
   Proof: synthetic workloads generate correctly attributed, secret-free results;
   explicit missing/stale signal cases; parent observes the shared T3 result.
   Inputs: fixed task 1b receipt schema; task 2 run/lease handoffs; parent integration
   owner. Shares skill docs/config with task 2: serialize edits or assign fields.
   Blocked by: 2 (local artifact/foreground seam delivered).
   Status: bounded CLI/MCP report over canonical receipts and observation-only OS/
   explicit non-starting SimLock event signals implemented in mac-work/diagnostics.
   Parent accepted live reports during both platform leases: task/owner/revision,
   wait/execution/results, caller-known lease IDs and timestamped normal pressure.
   Event history still does not establish active-lease authority.
   See [report contract](diagnostics.md).
   Finish line: Try; no new pressure enforcement.

4. **Prove representative hardware workflows**
   Outcome: real iOS/Android builds, slim/full devices and exact T3 UI routing
   work under admission while retained devices and old holds remain safe.
   Proof: parent-owned mixed-client hardware run with command/build/lease receipts,
   bounded cleanup and cancellation; T3-visible evidence.
   Inputs: parent owns hardware and integration; available task-owned devices;
   same artifacts across build/test; existing holds remain with their owners.
   Blocked by: broader app-build/lifecycle qualification; 2 and 3 accepted locally.
   Status: native Android foundation and supported prebuilt Android/iOS T3
   installation, interaction and retirement proved by parent. Real app rebuilds,
   Gradle/Xcode lifecycles and automatic queued T3 boot/cancel remain unproved.
   Finish line: Try; stop before rollout.

5. **Prepare installation, upgrade and rollback**
   Outcome: a managed shared installation can verify pins/config, detect drift,
   and safely drain or stop for upgrade/rollback without losing active ownership.
   Proof: disposable install/upgrade/rollback with active/queued tasks and mismatch
   refusal; fresh process sees the same authoritative configuration.
   Inputs: task 1b accepted runtime contract; parent integration owner; no live activation.
   Blocked by: 1b.
   Status: task-private immutable install/activation/rollback baseline is included
   in runner. Managed host adoption and future schema migration remain here.
   Finish line: Try, documented and locally proved only.

6. **Pilot and migrate cooperative callers**
   Outcome: selected callers adopt the tested route; old holds move only with their
   owners; raw-shell bypass limitations and recovery are visible.
   Proof: parent records the caller inventory, owner-approved transitions, rollback
   and real pilot receipts. Existing holds stay intact until adopted.
   Inputs: parent release decision for live activation and named hold owners.
   Blocked by: 4, 5.
   Status: supported local Try accepted; global adoption, old-hold transitions and
   rollout remain outstanding. Neither retained Try root is a second production pool.
   Finish line: Try release task; stop for parent before live changes.

7. **Measure and decide capacity**
   Outcome: capacity stays one unless matched representative workloads justify a
   larger value without pressure or behavior regressions.
   Proof: before/after queue wait, execution, throughput, pressure and contention
   measurements using the same workload; explicit decision and tradeoffs.
   Inputs: parent owns hardware schedule and capacity decision; baseline/pilot data;
   serialize runs on the shared Mac; device limits unchanged.
   Blocked by: 6.
   Status: exact daemon-build matched measurement and real cancellation remain
   valid for identical functional runner code. Keep heavy1/global4/iOS4/Android1;
   representative broader workloads and any capacity increase remain outstanding.
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

Current/planned stack: admission → lifecycle → runner → handoffs → diagnostics. Only create a later layer
when its predecessor delivers its contract. Task 5 can prepare against fixed
operational contracts only after task 1b alongside task 2 with disjoint files; parent integrates it.
Task 4 and task 7 serialize actual Mac workloads. Task 6 serializes each hold's
owner transition. Task 8 is a separate outward-facing release, never implicit
in local Try. No task rebuilds the scheduler or adds kernel quotas.

## Parent integration evidence

Parent inspected clean `/Users/sree/Documents/Dev/t3code`. Public device_open
accepts hostId/deviceId/platform; `apps/server/src/mcp/toolkits/device/handlers.ts:244`
calls DeviceService.open directly. `t3 --help` has no device CLI; thread supports
list/start/send/show. No supported external queue hook is established. Automatic T3 boot admission requires a supported native seam before claiming
coverage; command-only handoffs continue independently. These are parent findings, not
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
connected and undrained, with zero leases/queue. The later supported local Try
integration below adds T3 handoff proof; broader task 4 app-build qualification
remains. This slice has not driven devices or independently rerun hardware proof.

## Restack and ownership record

Parent restacked accepted admission/lifecycle onto main `b209c1ff1cd9ea9925b925f8a312a6dd90d0db79`.
Admission is `01c18f235f77669c6151c4f12b68713a8ab21a83`; lifecycle is
`01e8dcca192e8cd233d65d14dc56597e3da5165d` (bytes equal accepted pre-rebase
`63025ed`). Parent preserved 25 ignored files and recorded the verified restoration
in `verify-proof/restack-20261117/receipt.json`. This owner adds runner, then handoffs and diagnostics serially above
lifecycle. No live holds, provider profiles, devices or global capacity change.

## Real-command eligibility evidence

Parent observed Swift 6.4.2 universal capture build on SimLock a323 completing
in 14.125s with arm64+x86_64 Mach-O and no surviving observed descendants.
Compiler/clang/frontend/dsymutil children used distinct process groups. Direct
SIGTERM at 4s exited -15 with zero observed descendants at about 4.6s; this
is not canonical cancellation/crash proof and does not qualify Swift/xcodebuild
under the strict process-group contract. The exact qualified daemon invocation
is recorded below. Evidence is in the parent worktree verify-proof/
20261117T143101Z-workload-yvjlbl3l/profile.json, profile-build.log and cancel-profile.json.

Parent next observed installed Node + JS pnpm 10.34.6 `run build:daemon:run`
completing a full daemon build in 2.371s with all observed descendants in one PGID
and none surviving (node-js-profile.json). Native pnpm12/Turbo uses distinct
groups and remains unqualified. Parent subsequently proved matched serial/queued
pairs and canonical cancellation below; this is not a capacity increase.

## Parent real foreground workload proof (runner accepted)

Parent accepted runner `0c4bc1c82ff798e7014fc980ca1489a3b2bd8df5` and owns its
retained foreground-pilot install. Do not mutate, upgrade, delete or use that
root for new fitness. Parent independently read handoff-final and ran a fresh
stable-SimLock-worktree smoke operation; both succeeded without capacity held.

Exact qualified invocation: Node 22.23.4 plus installed JS pnpm 10.34.6,
`pnpm.cjs run build:daemon:run` on SimLock a323. All 12 matched builds passed,
three queued pairs never overlapped, and public compiler cancellation left no
surviving group members. A final queued build restored complete daemon output
(task124, parent-real-build-final-20261117, main.js SHA prefix50e9b035).
Median two-build manual serial3.796s vs queued5.035s: +1.239s / 32.6% overhead
for this short workload, not compiler speedup. Pressure normal, swap flat1084.44MiB.
Keep heavy1 and device caps4/4/1. This qualifies that exact invocation, not native
pnpm/Turbo, Swift, app artifacts, interactive T3 or device cancellation.
Proof: parent worktree `/Users/sree/.t3/worktrees/SreeStack/t3-6ff706bc-093e7ae59d9a288e`,
private Git verify-proof/20261117T143101Z-workload-yvjlbl3l/verdict.md,
comparison-summary.json, six raw batches, real-build-cancel.json and final-build.json.
Tasks4/6/7 still need broader app-build qualification, global adoption and
representative workload/capacity decisions.

## Parent-supported local Try integration (combined pilot accepted)

Parent accepted handoffs/diagnostics `8d4e9ec` after inspecting public seams and
independently using the combined install. Proof root:
`/Users/sree/Documents/Dev/SreeStack/.git/worktrees/t3-6ff706bc-093e7ae59d9a288e/verify-proof/20261117T150817Z-handoff-itpv54tw`.
The parent's `verdict.md` is being finalized there; the evidence below is reported
by parent, not independently rerun by this slice.

- `producer.json`: real qualified daemon build plus six independent pinned
  Appduct fixture hash checks; task63 succeeded, exit0, closed/released.
- `handoff.json`: manifest SHA256
  `219513ddf0be45baf7e0850eb3d15a387941e8bb897d5e0fef4405a48d88d706`
  binds daemon output and **prebuilt** APK/.app. `consumer.json`: task64's
  handoff-gated metadata/ZIP validation succeeded and released capacity.
  Both commands finished before device acquisition.
- Exact T3 device_open on `simlock-sree-mac` granted slim Pixel9:
  lease `395146f14a8b79b01010d00a9b95f52a`,
  device `dev_2f777801-c103-4f59-bc6b-c382febd6a0b`; and slim iPhone18Pro:
  lease `d01ce575b824825e91e93e438a78b8ba`,
  device `dev_29bac193-0479-42f6-b22f-6d81690e5efd`.
  The exact returned drivers installed sealed paths, opened each app and produced
  snapshots; Status-tab input visibly changed both UIs. iOS prepare succeeded.
  `android-before.png`, `android-after.png`, `ios-before.png` and `ios-after.png`
  retain the visual proof.
- Device_close with shutdown=true ended each session. `retirement.json` proves
  both devices deleted with zero owned leases. `handoff-after.json` retains the
  unchanged manifest.
- `android-live-report.json`/`.txt` and `ios-live-report.json`/`.txt` show command
  identity/timing/results, known lease IDs and timestamped normal pressure.
  These signals remain observation/correlation, not active-lease authority.

This proves qualified daemon build → prebuilt app verification/seal → supported
T3 interactive handoff and teardown. It does not rebuild Android/iOS apps,
qualify Gradle/Xcode or default Swift/native pnpm/Turbo, prove queued T3 boot/
cancellation, or add an external device_open admission hook. Global adoption,
old holds, rollout/publication and capacity increases remain outstanding.
Heavy1/global4/iOS4/Android1 stay unchanged. The earlier 12-build matched
measurement and real cancellation proof remain valid for identical functional
runner code. No runtime rebuild or install activation accompanies this record update.
