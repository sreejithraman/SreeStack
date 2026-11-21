"""Run the repository checks with pinned dependencies from any worktree.

The first run for a set of requirements builds a virtual environment in the
clone's shared Git directory. Later runs in every worktree only read it, so they
need no network and work in sandboxes that can write only to the worktree.
Requirements name each environment, so branches with different pins can coexist.
Builds take turns and a finished one moves into place in one step, so a run sees
a whole environment or none.

With arguments, run them with the environment's Python instead of the checks.
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
CHECKS = (
    *(("-m", "unittest", "discover", "-s", directory, "-p", "test_*.py") for directory in TEST_DIRS),
    *SCRIPT_CHECKS,
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
    root_str = str(ROOT.resolve())
    for name, module in list(sys.modules.items()):
        if name == "__main__":
            continue
        origin = getattr(module, "__file__", None)
        if origin and str(Path(origin).resolve()).startswith(root_str):
            sys.modules.pop(name, None)


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


def _discover_mode() -> int:
    os.environ.pop("_SREESTACK_CHECK_DISCOVER", None)
    base_path = list(sys.path)
    discovered_files = []
    discovered_tests = []
    module_units = []
    class_units = []
    file_tests = {}
    errors = []

    for start_dir in TEST_DIRS:
        folder = ROOT / start_dir
        files = sorted(folder.glob("test_*.py"))
        if not files:
            errors.append(f"No test_*.py files found in {start_dir}")
            continue
        for file_path in files:
            rel_file = file_path.relative_to(ROOT).as_posix()
            discovered_files.append(rel_file)
            mod_name = file_path.stem
            _evict_repo_modules()
            sys.path[:] = [str(folder), *[p for p in base_path if p != str(folder)]]
            try:
                module = importlib.import_module(mod_name)
                suite = unittest.TestLoader().loadTestsFromModule(module)
                cases = list(_iter_test_cases(suite))
            except Exception:
                errors.append(f"Discovery failed for {rel_file}:\n{traceback.format_exc()}")
                continue
            has_module_hooks = hasattr(module, "setUpModule") or hasattr(module, "tearDownModule")
            file_test_ids = []
            by_class = {}
            for case in cases:
                if case.__class__.__name__ == "_FailedTest":
                    errors.append(f"Load error in {rel_file}: {case.id()}")
                    continue
                tid = case.id()
                full_id = f"{rel_file}::{tid}"
                discovered_tests.append(full_id)
                file_test_ids.append((tid, full_id))
                by_class.setdefault(case.__class__, []).append((tid, full_id))
            if has_module_hooks:
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

    sys.stdout.write(json.dumps({
        "files": discovered_files,
        "tests": discovered_tests,
        "module_units": module_units,
        "class_units": class_units,
        "file_tests": list(file_tests.values()),
        "errors": errors,
    }))
    return 1 if errors else 0


class _RecordingResult(unittest.TestResult):
    def __init__(self, rel_file: str):
        super().__init__()
        self.rel_file = rel_file
        self.executed = []

    def stopTest(self, test):
        super().stopTest(test)
        self.executed.append(f"{self.rel_file}::{test.id()}")


def _worker_mode() -> int:
    os.environ.pop("_SREESTACK_CHECK_WORKER", None)
    proto_fd = os.dup(1)
    os.set_inheritable(proto_fd, False)
    proto_out = os.fdopen(proto_fd, "w", encoding="utf-8")
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    os.close(devnull)

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

        os.chdir(ROOT)
        started = time.perf_counter()
        result = _RecordingResult(rel_file)
        load_error = None
        output = ""
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as capture:
            try:
                with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                    module = importlib.import_module(mod_name)
                    loader = unittest.TestLoader()
                    if kind == "module":
                        suite = loader.loadTestsFromModule(module)
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
            output = capture.read()

        duration = time.perf_counter() - started
        failures = [(str(test), tb) for test, tb in result.failures]
        errors = [(str(test), tb) for test, tb in result.errors]
        if load_error:
            errors.append((rel_file, load_error))
        proto_out.write(json.dumps({
            "file": rel_file,
            "executed": result.executed,
            "skipped": len(result.skipped),
            "failures": failures,
            "errors": errors,
            "duration": duration,
            "output": output,
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
        chunk_size = max(1, min(4, len(targets) // max(1, workers * 2) or 1))
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
    discover_env = {**os.environ, "_SREESTACK_CHECK_DISCOVER": "1"}
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
    if discovery["errors"] or discover_proc.returncode:
        for err in discovery["errors"]:
            print(err, file=sys.stderr)
        return 1

    seed_env = os.environ.get("CHECK_SEED")
    seed = int(seed_env) if seed_env else random.SystemRandom().randrange(1 << 32)
    rng = random.Random(seed)

    total_tests = len(discovery["tests"])
    workers_env = os.environ.get("CHECK_WORKERS")
    default_workers = min(os.cpu_count() or 1, max(1, total_tests // 10))
    workers = int(workers_env) if workers_env else default_workers
    units = _build_units(discovery, rng, max(1, workers))
    workers = min(max(1, workers), len(units)) if units else 0

    work_queue: queue.Queue = queue.Queue()
    for unit in units:
        work_queue.put(unit)

    results_lock = threading.Lock()
    executed_files: set[str] = set()
    executed_tests: set[str] = set()
    file_durations: dict[str, float] = {}
    all_failures: list[tuple[str, str, str]] = []
    skipped_count = 0
    worker_errors: list[str] = []

    def run_worker_thread():
        worker_env = {**os.environ, "_SREESTACK_CHECK_WORKER": "1"}
        proc = subprocess.Popen(
            [python, str(Path(__file__).resolve())],
            cwd=ROOT, env=worker_env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True,
        )
        try:
            while True:
                try:
                    unit = work_queue.get_nowait()
                except queue.Empty:
                    break
                proc.stdin.write(json.dumps(unit) + "\n")
                proc.stdin.flush()
                reply_line = proc.stdout.readline()
                if not reply_line:
                    err = proc.stderr.read()
                    with results_lock:
                        worker_errors.append(f"Worker exited while running {unit['file']}: {err}")
                    break
                reply = json.loads(reply_line)
                with results_lock:
                    rel_file = reply["file"]
                    executed_files.add(rel_file)
                    executed_tests.update(reply["executed"])
                    file_durations[rel_file] = file_durations.get(rel_file, 0.0) + reply["duration"]
                    skipped_count_local = reply["skipped"]
                    nonlocal skipped_count
                    skipped_count += skipped_count_local
                    for test_name, tb in reply["failures"]:
                        all_failures.append(("FAIL", f"{rel_file} {test_name}", tb))
                    for test_name, tb in reply["errors"]:
                        all_failures.append(("ERROR", f"{rel_file} {test_name}", tb))
        finally:
            if proc.stdin:
                proc.stdin.close()
            stderr_tail = proc.stderr.read() if proc.stderr else ""
            rc = proc.wait()
            if rc != 0:
                with results_lock:
                    worker_errors.append(f"Worker exited with code {rc}: {stderr_tail}")

    script_results: list[tuple[tuple[str, ...], subprocess.CompletedProcess]] = []

    def run_script_thread(check_cmd):
        proc = subprocess.run([python, *check_cmd], cwd=ROOT, capture_output=True, text=True)
        with results_lock:
            script_results.append((check_cmd, proc))

    threads = [threading.Thread(target=run_worker_thread) for _ in range(workers)]
    for check_cmd in SCRIPT_CHECKS:
        threads.append(threading.Thread(target=run_script_thread, args=(check_cmd,)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Preserve deterministic output order for standalone script checks.
    by_cmd = {cmd: proc for cmd, proc in script_results}
    failed_scripts = []
    for check_cmd in SCRIPT_CHECKS:
        proc = by_cmd[check_cmd]
        if proc.stdout:
            sys.stdout.write(proc.stdout)
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        if proc.returncode:
            failed_scripts.append(check_cmd)

    for kind, label, tb in all_failures:
        print(f"{'=' * 70}\n{kind}: {label}\n{'-' * 70}\n{tb}", file=sys.stderr)
    for err in worker_errors:
        print(err, file=sys.stderr)

    expected_files = set(discovery["files"])
    expected_tests = set(discovery["tests"])
    missing_files = sorted(expected_files - executed_files)
    missing_tests = sorted(expected_tests - executed_tests)
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
        print(f"Slowest test files (CPU): {summary}", flush=True)

    off_main = stable_clone_off_main()
    if off_main:
        print(f"Failed: stable clone {off_main} is not on main, so installed skills "
              "stopped updating. Switch it back to main.", file=sys.stderr)

    failed = bool(all_failures or worker_errors or failed_scripts or missing_files
                  or (missing_tests and not all_failures and not worker_errors) or off_main)
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
