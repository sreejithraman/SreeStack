"""Run the repository checks with pinned dependencies from any worktree.

The first run for a set of requirements builds a virtual environment in the
clone's shared Git directory. Later runs in every worktree only read it, so they
need no network and work in sandboxes that can write only to the worktree.
Requirements name each environment, so branches with different pins can coexist.
Builds take turns and a finished one moves into place in one step, so a run sees
a whole environment or none.

With arguments, run them with the environment's Python instead of the checks.
Environment overrides for the full suite: CHECK_WORKERS, CHECK_SEED,
CHECK_CHANGED_SINCE, and CHECK_PUSH_REFS.
"""

import contextlib
import fcntl
import hashlib
import importlib
import json
import os
from pathlib import Path
import queue
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "scripts/requirements-checks.txt"
TEST_DIRS = (
    "scripts",
    "skills/agent-login/scripts",
    "skills/coordinator/scripts",
    "skills/create-image/scripts",
    "skills/mac-work/scripts",
    "skills/pr/scripts",
    "skills/review-fix-loop/scripts",
    "skills/simulator-lifecycle/scripts",
    "skills/writing-for-agents/scripts",
)
SCRIPT_CHECKS = (
    ("scripts/check_skills.py",),
    ("scripts/check_whitespace.py",),
)


def environment_path() -> Path:
    git_directory = subprocess.check_output(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT, text=True,
    ).strip()
    digest = hashlib.sha256()
    for requirements in sorted(REQUIREMENTS.parent.glob("requirements-*.txt")):
        digest.update(requirements.read_bytes())
    return Path(git_directory) / "sreestack-check-env" / digest.hexdigest()[:16]


def usable(environment: Path) -> bool:
    """Importing pip proves the interpreter runs and still sees its site-packages."""
    python = environment / "bin/python"
    return python.exists() and subprocess.run(
        [str(python), "-I", "-c", "import pip"], capture_output=True,
    ).returncode == 0


def build(environment: Path) -> None:
    print(f"Preparing the check environment at {environment}", file=sys.stderr)
    environment.parent.mkdir(exist_ok=True)
    with open(environment.parent / "build.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if usable(environment):  # Another run finished while this one waited.
            return
        with tempfile.TemporaryDirectory(dir=environment.parent, prefix=".build-") as directory:
            draft = Path(directory) / "environment"
            subprocess.run([sys.executable, "-I", "-m", "venv", str(draft)], check=True)
            subprocess.run(
                [str(draft / "bin/python"), "-I", "-m", "pip", "install", "--quiet",
                 "--disable-pip-version-check", "-r", str(REQUIREMENTS)],
                check=True,
            )
            shutil.rmtree(environment, ignore_errors=True)
            draft.rename(environment)


def checks_python() -> str:
    environment = environment_path()
    if not usable(environment):
        try:
            build(environment)
        except (OSError, subprocess.CalledProcessError) as error:
            sys.exit(f"Could not build {environment}: {error}\n"
                     "If that is a network or permission failure, rerun with network access "
                     "and write access to the Git directory.")
    return str(environment / "bin/python")


def stable_clone_off_main() -> Path | None:
    """Return the primary checkout when a worktree finds it off main.

    Host sync stops without a sound once that checkout leaves main, so skills silently
    go stale. CI and the primary checkout itself run with no linked worktree to speak for it.
    """
    listing = subprocess.check_output(
        ["git", "worktree", "list", "--porcelain"], cwd=ROOT, text=True,
    ).split("\n\n")[0].splitlines()
    primary = Path(listing[0].removeprefix("worktree "))
    if primary.resolve() == ROOT or "branch refs/heads/main" in listing:
        return None
    return primary


def _evict_repo_modules() -> None:
    root_path = ROOT.resolve()
    git_dir = root_path / ".git"
    venv_prefix = Path(sys.prefix).resolve()
    for name, module in list(sys.modules.items()):
        if name == "__main__":
            continue
        origin = getattr(module, "__file__", None)
        if not origin:
            continue
        resolved = Path(origin).resolve()
        if (resolved.is_relative_to(root_path)
                and not resolved.is_relative_to(git_dir)
                and not resolved.is_relative_to(venv_prefix)):
            sys.modules.pop(name, None)


def _detach_protocol_stdout():
    proto_fd = os.dup(1)
    os.set_inheritable(proto_fd, False)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    os.close(devnull)
    return os.fdopen(proto_fd, "w", encoding="utf-8")


def _iter_test_cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_test_cases(item)
        else:
            yield item


def _has_own_fixture(cls, names) -> bool:
    for base in cls.__mro__:
        if base is unittest.TestCase:
            break
        if any(name in base.__dict__ for name in names):
            return True
    return False


def select_test_dirs(changed_since: str) -> tuple[tuple[str, ...], str]:
    """Return the TEST_DIRS reachable from changes since changed_since, or all TEST_DIRS."""
    try:
        diff_committed = subprocess.check_output(
            ["git", "diff", "-z", "--no-renames", "--name-only", f"{changed_since}...HEAD"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).split("\0")
        diff_working = subprocess.check_output(
            ["git", "diff", "-z", "--no-renames", "--name-only", "HEAD"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).split("\0")
        untracked = subprocess.check_output(
            ["git", "ls-files", "-z", "--others", "--exclude-standard"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).split("\0")
    except subprocess.CalledProcessError:
        return TEST_DIRS, f"could not diff against {changed_since}; running full suite"

    changed = sorted({p for p in (*diff_committed, *diff_working, *untracked) if p})
    if not changed:
        return TEST_DIRS, f"no changed files since {changed_since}; running full suite"

    outside = next((p for p in changed if not p.startswith("skills/")), None)
    if outside:
        return TEST_DIRS, f"full suite triggered by {outside}"

    changed_skills = {Path(path).parts[1] for path in changed}
    selected = tuple(d for d in TEST_DIRS if d.startswith("skills/") and Path(d).parts[1] in changed_skills)
    return selected, f"selected {len(selected)}/{len(TEST_DIRS)} test dirs for skills {', '.join(sorted(changed_skills))}"


def check_push_refs(push_refs: str) -> str | None:
    """Return an error message if any non-deletion pushed SHA differs from HEAD."""
    lines = [line.strip() for line in push_refs.splitlines() if line.strip()]
    if not lines:
        return None
    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            continue
        local_ref, local_sha = parts[0], parts[1]
        if set(local_sha) == {"0"}:
            continue
        peeled = subprocess.run(
            ["git", "rev-parse", "--verify", f"{local_sha}^{{commit}}"],
            cwd=ROOT, text=True, capture_output=True,
        )
        target_sha = peeled.stdout.strip() if peeled.returncode == 0 else local_sha
        if target_sha != head_sha:
            return (f"pre-push checks validate HEAD ({head_sha[:12]}), "
                    f"but push updates {local_ref} ({local_sha[:12]}). "
                    "Check out that branch or run full checks before pushing.")
    return None


def _discover_mode() -> int:
    os.environ.pop("_SREESTACK_CHECK_DISCOVER", None)
    selected_env = os.environ.pop("_SREESTACK_SELECTED_DIRS", None)
    test_dirs = tuple(json.loads(selected_env)) if selected_env is not None else TEST_DIRS
    proto_out = _detach_protocol_stdout()
    base_path = list(sys.path)
    root_resolved = ROOT.resolve()
    discovered_files = []
    discovered_tests = []
    module_units = []
    class_units = []
    file_tests = {}
    errors = []

    for start_dir in test_dirs:
        folder = ROOT / start_dir
        _evict_repo_modules()
        sys.path[:] = [str(folder), *[p for p in base_path if p != str(folder)]]
        try:
            suite = unittest.TestLoader().discover(str(folder), pattern="test_*.py", top_level_dir=str(folder))
            cases = list(_iter_test_cases(suite))
        except Exception:
            errors.append(f"Discovery failed for {start_dir}:\n{traceback.format_exc()}")
            continue

        dir_errors = len(errors)
        by_module = {}
        for case in cases:
            if case.__class__.__name__ == "_FailedTest":
                probe = unittest.TestResult()
                case.run(probe)
                detail = "\n".join(tb for _, tb in (*probe.errors, *probe.failures)) or case.id()
                errors.append(f"Load error in {start_dir} ({case.id()}):\n{detail}")
                continue
            mod_name = case.__class__.__module__
            module = sys.modules.get(mod_name)
            origin = getattr(module, "__file__", None)
            if not origin:
                errors.append(f"Could not locate file for module {mod_name} in {start_dir}")
                continue
            rel_file = Path(origin).resolve().relative_to(root_resolved).as_posix()
            by_module.setdefault((rel_file, mod_name), []).append(case)

        if not by_module and len(errors) == dir_errors:
            errors.append(f"No test_*.py files found in {start_dir}")
            continue

        for (rel_file, mod_name), mod_cases in sorted(by_module.items()):
            discovered_files.append(rel_file)
            module = sys.modules[mod_name]
            atomic_module = any(hasattr(module, hook) for hook in ("setUpModule", "tearDownModule", "load_tests"))
            file_test_ids = []
            by_class = {}
            for case in mod_cases:
                tid = case.id()
                full_id = f"{rel_file}::{tid}"
                discovered_tests.append(full_id)
                file_test_ids.append((tid, full_id))
                by_class.setdefault(case.__class__, []).append((tid, full_id))
            if atomic_module:
                module_units.append({
                    "kind": "module",
                    "start_dir": start_dir,
                    "file": rel_file,
                    "module": mod_name,
                    "targets": [tid for tid, _ in file_test_ids],
                })
            else:
                free_tests = []
                for cls, items in by_class.items():
                    if _has_own_fixture(cls, ("setUpClass", "tearDownClass")):
                        class_units.append({
                            "kind": "class",
                            "start_dir": start_dir,
                            "file": rel_file,
                            "module": mod_name,
                            "targets": [tid for tid, _ in items],
                        })
                    else:
                        free_tests.extend(tid for tid, _ in items)
                if free_tests:
                    file_tests[rel_file] = {
                        "start_dir": start_dir,
                        "file": rel_file,
                        "module": mod_name,
                        "targets": free_tests,
                    }

    proto_out.write(json.dumps({
        "files": discovered_files,
        "tests": discovered_tests,
        "module_units": module_units,
        "class_units": class_units,
        "file_tests": list(file_tests.values()),
        "errors": errors,
    }))
    proto_out.close()
    return 1 if errors else 0


class _RecordingResult(unittest.TestResult):
    def __init__(self, rel_file: str):
        super().__init__()
        self.rel_file = rel_file
        self.executed = []
        self.fixture_skipped = False

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if test.__class__.__name__ == "_ErrorHolder":
            self.fixture_skipped = True

    def stopTest(self, test):
        super().stopTest(test)
        self.executed.append(f"{self.rel_file}::{test.id()}")


def _worker_mode() -> int:
    os.environ.pop("_SREESTACK_CHECK_WORKER", None)
    proto_out = _detach_protocol_stdout()
    base_path = list(sys.path)
    current_key = None

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        unit = json.loads(line)
        start_dir = unit["start_dir"]
        rel_file = unit["file"]
        mod_name = unit["module"]
        kind = unit["kind"]
        targets = unit["targets"]
        folder = str(ROOT / start_dir)
        key = (start_dir, mod_name)
        if key != current_key:
            _evict_repo_modules()
            sys.path[:] = [folder, *[p for p in base_path if p != folder]]
            current_key = key

        started = time.perf_counter()
        result = _RecordingResult(rel_file)
        load_error = None
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as capture:
            try:
                with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                    module = importlib.import_module(mod_name)
                    loader = unittest.TestLoader()
                    if kind == "module":
                        suite = loader.loadTestsFromModule(module, pattern="test_*.py")
                    else:
                        suite = loader.loadTestsFromNames(
                            [t[len(mod_name) + 1:] if t.startswith(mod_name + ".") else t for t in targets],
                            module,
                        )
                    suite.run(result)
            except Exception:
                load_error = traceback.format_exc()
            finally:
                os.chdir(ROOT)
            capture.seek(0)
            captured = capture.read()

        duration = time.perf_counter() - started
        failures = [(str(test), tb) for test, tb in result.failures]
        for test in result.unexpectedSuccesses:
            failures.append((str(test), "Unexpected success"))
        errors = [(str(test), tb) for test, tb in result.errors]
        if load_error:
            errors.append((rel_file, load_error))
        if not result.wasSuccessful() and not failures and not errors:
            failures.append((rel_file, "unittest reported failure"))

        executed_set = set(result.executed)
        skipped_tests = (
            [fid for t in targets if (fid := f"{rel_file}::{t}") not in executed_set]
            if (result.fixture_skipped and not failures and not errors) else []
        )
        skipped = len(skipped_tests) + sum(
            1 for test, _ in result.skipped if test.__class__.__name__ != "_ErrorHolder"
        )
        proto_out.write(json.dumps({
            "file": rel_file,
            "executed": result.executed,
            "skipped_tests": skipped_tests,
            "skipped": skipped,
            "failures": failures,
            "errors": errors,
            "duration": duration,
            "output": captured if (failures or errors) else "",
        }) + "\n")
        proto_out.flush()
    proto_out.close()
    return 0


def _build_units(discovery: dict, rng: random.Random, workers: int) -> list[dict]:
    module_units = list(discovery["module_units"])
    rng.shuffle(module_units)
    fine_units = list(discovery["class_units"])
    for entry in discovery["file_tests"]:
        targets = list(entry["targets"])
        rng.shuffle(targets)
        chunk_size = min(4, len(targets) // (workers * 2) or 1)
        for start in range(0, len(targets), chunk_size):
            fine_units.append({
                "kind": "chunk",
                "start_dir": entry["start_dir"],
                "file": entry["file"],
                "module": entry["module"],
                "targets": targets[start:start + chunk_size],
            })
    rng.shuffle(fine_units)
    return module_units + fine_units


def _run_parallel_checks(python: str) -> int:
    started = time.perf_counter()
    push_refs = os.environ.get("CHECK_PUSH_REFS", "")
    if push_refs.strip():
        push_error = check_push_refs(push_refs)
        if push_error:
            print(f"Failed: {push_error}", file=sys.stderr)
            return 1

    changed_since = os.environ.get("CHECK_CHANGED_SINCE", "").strip()
    if changed_since:
        selected_dirs, reason = select_test_dirs(changed_since)
        print(f"Selection ({changed_since}): {reason}", flush=True)
    else:
        selected_dirs = TEST_DIRS

    discover_env = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "_SREESTACK_CHECK_DISCOVER": "1",
        "_SREESTACK_SELECTED_DIRS": json.dumps(list(selected_dirs)),
    }
    discover_proc = subprocess.run(
        [python, str(Path(__file__).resolve())],
        cwd=ROOT, env=discover_env, capture_output=True, text=True,
    )
    if discover_proc.stderr:
        sys.stderr.write(discover_proc.stderr)
    if not discover_proc.stdout.strip():
        print("Failed: test discovery produced no output", file=sys.stderr)
        return 1
    discovery = json.loads(discover_proc.stdout)
    discovery_errors = list(discovery["errors"])
    if discover_proc.returncode and not discovery_errors:
        discovery_errors.append(f"Test discovery exited with code {discover_proc.returncode}")

    seed_env = os.environ.get("CHECK_SEED")
    seed = int(seed_env) if seed_env else random.SystemRandom().randrange(1 << 32)
    rng = random.Random(seed)

    total_tests = len(discovery["tests"])
    workers_env = os.environ.get("CHECK_WORKERS")
    default_workers = min(os.cpu_count() or 1, max(1, total_tests // 10))
    workers = max(1, int(workers_env) if workers_env else default_workers)
    units = _build_units(discovery, rng, workers)
    workers = min(workers, len(units)) if units else 0

    work_queue: queue.Queue = queue.Queue()
    for unit in units:
        work_queue.put(unit)

    results_lock = threading.Lock()
    executed_files: set[str] = set()
    executed_tests: set[str] = set()
    skipped_tests: set[str] = set()
    file_durations: dict[str, float] = {}
    all_failures: list[tuple[str, str, str, str]] = []
    skipped_count = 0
    worker_errors: list[str] = []

    with tempfile.TemporaryDirectory(prefix="sreestack-check-cache-") as cache_dir:
        def run_worker_thread():
            nonlocal skipped_count
            worker_env = {k: v for k, v in os.environ.items() if not k.startswith("CHECK_")}
            worker_env["PYTHONDONTWRITEBYTECODE"] = "1"
            worker_env["_SREESTACK_CHECK_WORKER"] = "1"
            worker_env["_SREESTACK_TEST_CACHE"] = cache_dir
            proc = subprocess.Popen(
                [python, str(Path(__file__).resolve())],
                cwd=ROOT, env=worker_env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True,
            )
            try:
                while True:
                    try:
                        unit = work_queue.get_nowait()
                    except queue.Empty:
                        break
                    try:
                        proc.stdin.write(json.dumps(unit) + "\n")
                        proc.stdin.flush()
                    except OSError as error:
                        with results_lock:
                            worker_errors.append(f"Worker pipe error while sending {unit['file']}: {error}")
                        break
                    reply_line = proc.stdout.readline()
                    if not reply_line:
                        with results_lock:
                            worker_errors.append(f"Worker exited while running {unit['file']}")
                        break
                    reply = json.loads(reply_line)
                    with results_lock:
                        rel_file = reply["file"]
                        executed_files.add(rel_file)
                        executed_tests.update(reply["executed"])
                        skipped_tests.update(reply["skipped_tests"])
                        file_durations[rel_file] = file_durations.get(rel_file, 0.0) + reply["duration"]
                        skipped_count += reply["skipped"]
                        unit_output = reply["output"]
                        for test_name, tb in reply["failures"]:
                            all_failures.append(("FAIL", f"{rel_file} {test_name}", tb, unit_output))
                            unit_output = ""
                        for test_name, tb in reply["errors"]:
                            all_failures.append(("ERROR", f"{rel_file} {test_name}", tb, unit_output))
                            unit_output = ""
            finally:
                if proc.stdin:
                    try:
                        proc.stdin.close()
                    except OSError:
                        pass
                rc = proc.wait()
                if rc != 0:
                    with results_lock:
                        worker_errors.append(f"Worker exited with code {rc}")

        script_results: dict[tuple[str, ...], subprocess.CompletedProcess] = {}

        def run_script_thread(check_cmd):
            proc = subprocess.run([python, *check_cmd], cwd=ROOT, capture_output=True, text=True)
            with results_lock:
                script_results[check_cmd] = proc

        threads = [threading.Thread(target=run_worker_thread) for _ in range(workers)]
        for check_cmd in SCRIPT_CHECKS:
            threads.append(threading.Thread(target=run_script_thread, args=(check_cmd,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    failed_scripts = []
    for check_cmd in SCRIPT_CHECKS:
        proc = script_results[check_cmd]
        if proc.stdout:
            sys.stdout.write(proc.stdout)
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        if proc.returncode:
            failed_scripts.append(check_cmd)

    for err in discovery_errors:
        print(err, file=sys.stderr)
    for kind, label, tb, output in all_failures:
        print(f"{'=' * 70}\n{kind}: {label}\n{'-' * 70}\n{tb}", file=sys.stderr)
        if output:
            print(f"Captured output:\n{output}", file=sys.stderr)
    for err in worker_errors:
        print(err, file=sys.stderr)

    expected_files = set(discovery["files"])
    expected_tests = set(discovery["tests"])
    missing_files = sorted(expected_files - executed_files)
    missing_tests = sorted(expected_tests - executed_tests - skipped_tests)
    if missing_files:
        print(f"Failed: coverage proof missed files: {', '.join(missing_files)}", file=sys.stderr)
    if missing_tests and not all_failures and not worker_errors:
        print(f"Failed: coverage proof missed {len(missing_tests)} tests: {', '.join(missing_tests[:5])}",
              file=sys.stderr)

    for check_cmd in failed_scripts:
        print(f"Failed: {' '.join(check_cmd)}", file=sys.stderr)

    elapsed = time.perf_counter() - started
    skip_note = f" (skipped={skipped_count})" if skipped_count else ""
    print(f"Ran {len(executed_tests)} tests across {len(executed_files)} files in {elapsed:.2f}s "
          f"with {workers} workers (seed={seed}){skip_note}", flush=True)
    if file_durations:
        slowest = sorted(file_durations.items(), key=lambda item: -item[1])[:5]
        summary = ", ".join(f"{name}={dur:.1f}s" for name, dur in slowest)
        print(f"Slowest test files (wall): {summary}", flush=True)

    off_main = stable_clone_off_main()
    if off_main:
        print(f"Failed: stable clone {off_main} is not on main, so installed skills "
              "stopped updating. Switch it back to main.", file=sys.stderr)

    failed = bool(discovery_errors or all_failures or worker_errors or failed_scripts
                  or missing_files or missing_tests or off_main)
    return 1 if failed else 0


def main() -> int:
    if os.environ.get("_SREESTACK_CHECK_DISCOVER") == "1":
        return _discover_mode()
    if os.environ.get("_SREESTACK_CHECK_WORKER") == "1":
        return _worker_mode()
    python = checks_python()
    if len(sys.argv) > 1:
        return subprocess.run([python, *sys.argv[1:]]).returncode
    return _run_parallel_checks(python)


if __name__ == "__main__":
    sys.exit(main())
