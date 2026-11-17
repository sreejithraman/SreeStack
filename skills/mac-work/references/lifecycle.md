# Reproduce the lifecycle candidate

This is a dependency/baseline qualification recipe. Use the
[canonical foreground runner](runner.md) for the approved pilot.

Use a new private directory and leave live admission/device state alone. These
commands build a dependency experiment; they install nothing into host tools or
the repository checker. Read the [ownership boundary](repair.md) first.

From the repository root:

```sh
run=$(mktemp -d -t mac-work-lifecycle)
python3 skills/mac-work/scripts/build_runtime.py build --root "$run/candidate"
runtime="$run/candidate/runtime"
python3 skills/mac-work/scripts/build_runtime.py verify --runtime "$runtime"
```

The recipe requires `uv` and uses Python 3.12.12. It verifies the official archive,
patch, runtime lock, build lock, base modules and patched modules. It then builds
with the pinned backend and fixed SOURCE_DATE_EPOCH, installs the wheel into a
private environment, and writes `build-receipt.json`. `candidate.json` is the
single pin manifest. Use `--archive PATH` to reuse the exact archive offline;
`--patch PATH` is accepted only when its digest matches the manifest. Changed
inputs, schema, package versions or installed source fail closed.

Keep proof under this worktree's private Git directory:

```sh
proof=$(git rev-parse --path-format=absolute --git-path verify-proof)
mkdir -p "$proof"
python3 skills/mac-work/scripts/lifecycle_fitness.py --runtime "$runtime" \
  --output "$proof/lifecycle-policy-$(date -u +%Y%m%dT%H%M%SZ)" \
  --case foreground-quarantine --case quarantine-cancel --case quarantine-crash \
  --case quarantine-success --case quarantine-no-release --case boot-recovery-fixture
python3 skills/mac-work/scripts/lifecycle_fitness.py --runtime "$runtime" \
  --contract process-group \
  --output "$proof/lifecycle-group-$(date -u +%Y%m%dT%H%M%SZ)" \
  --case atomic-cold-start --case mixed-client-wait --case cli-cancel-running \
  --case cli-crash --case mcp-cancel-and-read --case mcp-crash-restart \
  --case group-recovery --case queue-deadline --case config-mismatch \
  --case corrupt-init --case identity-mismatch
```

Every case has private state; no persisted policy is changed between contracts.
The first suite proves conservative blocking, including after fresh-client
restart, not automatic availability. The boot case edits only an offline-style
private fixture's recorded old identity; an actual reboot remains untested.
Group recovery kills the exact fixture-owned lingering process, then checks that
a fresh observation of closure releases the queued successor. Identity mismatch
checks that an unverified group stays alive and retains capacity.

Also run the original automatic-availability cases with `--contract process-group`
and `--case mcp-cancel-detached --case cli-success-lingering --case mcp-success-lingering`.
The detached universal assertion still fails; the two lingering cases block their
successor until closure. Keep these gaps alongside passing policy results.
A quarantined successor's observation timeout is not a passing availability test.
The original unpatched gate and counterexamples remain in [fitness findings](fitness.md).

Run `--help` for all case names. Outputs include verdicts, contract, expectation
category, runtime/harness identity, fixture events, client transcripts and logs.
Never sum policy passes into a claim that universal automatic cleanup passed.
Repeat the cold-start, mixed-client and cancellation/crash probes against the
same immutable build before accepting a new patch. Original baseline comparison
uses `--original` with the unpatched runtime from [setup](setup.md).

After the run, fixture processes/state are removed by the harness. Keep retained
proof, then remove only the task-owned `run` directory. No runtime is needed to
open the JSON evidence. The original source archive's license and
[modification notice](../NOTICE.md) accompany the local patch. Production
activation, actual reboot proof, arbitrary detached cleanup and hardware work
remain outside this local Try.

## Runtime integrity prerequisite

The build recipe copies its managed CPython base into the private version and
installs dependencies with copy mode. One typed inventory covers both interpreter/
standard-library and venv trees: regular bytes, directories, links, modes and the
complete file set. Shared hardlinks, escaping links and special files refuse.
Code directories are read-only so ordinary Python imports cannot create unlisted
bytecode. Existing bytecode is hashed; no cache subtree is exempt. Verification
uses the host standard library and never executes the candidate interpreter.

The trusted build establishes this baseline from pinned source/dependency inputs
and the selected managed Python. The installed bootstrap must bind its build
receipt in configuration and verify it before candidate startup. The host OS,
fixed system Python `/usr/bin/python3` (3.9+) and its standard library, `/usr/bin/env`
with `-S`, and initial installer/uv are prerequisites. This is drift refusal on a
cooperatively maintained filesystem, not protection against a compromised host,
a malicious initial builder or concurrent hostile filesystem replacement.
