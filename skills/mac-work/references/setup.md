# Private runtime qualification

This is a dependency/baseline qualification recipe. Use the
[canonical foreground runner](runner.md) for the approved pilot.

Use macOS, Python 3.12 and `uv`. The lock pins the official Block source archive
and all dependencies with hashes. FastMCP and Fakeredis need compatibility pins;
see [findings](fitness.md). This installs only in a new task-owned directory.
Do not install the candidate into shared tools, host profiles or the repository's
managed checker environment. Do not point qualification at live queue state.

From the source repository root:

```sh
skill="$PWD/skills/mac-work"
run=$(mktemp -d -t mac-work-runtime)
uv venv "$run/runtime" --python 3.12
uv pip sync --python "$run/runtime/bin/python" \
  "$skill/scripts/runtime.lock" --require-hashes
proof=$(git rev-parse --path-format=absolute --git-path verify-proof)
mkdir -p "$proof"
python3 "$skill/scripts/fitness.py" --runtime "$run/runtime" \
  --output "$proof/mac-work-$(date -u +%Y%m%dT%H%M%SZ)"
```

The current candidate is expected to exit 1. Inspect `verdicts.json`, each case's
`events.json`, process logs and MCP transcript. `events.json` comes from fixture
processes, independently of queue status. The tool removes its private state and
stops only the processes it starts. The proof and the private runtime remain;
remove the task-owned runtime directory after qualification. Never use `tq clear`
to recover a live permit.

`--case NAME` narrows a diagnostic rerun. All cases must pass to qualify a pin.
Reusing an output path is refused. Invalid or mismatched runtimes exit 2 before
queue invocation. Runtime identity includes every locked dependency version and
the three installed upstream module hashes. Receipts capture no environment dump;
fixture processes receive only a minimal test environment. Arbitrary commands can
print secrets, so the eventual production output contract still needs redaction
and retention decisions.

## Changing the candidate

Resolve versions into `scripts/runtime.lock` with:

```sh
uv pip compile --python-version 3.12 --generate-hashes \
  "$skill/scripts/runtime.in" --output-file "$skill/scripts/runtime.lock" --no-header
```

Treat that as a new candidate. Update the source hashes in `fitness.py` from the
reviewed official archive, create a fresh runtime, then run every gate. Keep the
old lock and proof in Git/history; never mutate an active runtime in place.
This workflow qualifies a dependency set; it is not a production upgrade or
rollback. Those operations remain task 5 in the plan. The existing live route
and holds are the rollback baseline because this slice activates nothing.

Repository tests need no queue installation:

```sh
python3 scripts/check.py
python3 scripts/check.py scripts/test_sync_hosts.py
python3 scripts/check.py skills/mac-work/scripts/test_fitness.py
```
