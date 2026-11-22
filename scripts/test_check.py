"""Exercise the check runner against small Git repositories."""

import atexit
import fcntl
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).parent
_FALLBACK_CACHE = None
EMPTY_REQUIREMENTS = "# no packages, so tests need no network\n"
PASSING_TEST = """\
import unittest


class Passing(unittest.TestCase):
    def test_passes(self):
        pass
"""
PRINT_PYTHON = "import sys; print(sys.prefix)"


def cached_template(name, build):
    global _FALLBACK_CACHE
    root = os.environ.get("_SREESTACK_TEST_CACHE")
    if not root:
        if _FALLBACK_CACHE is None:
            _FALLBACK_CACHE = tempfile.TemporaryDirectory()
            atexit.register(_FALLBACK_CACHE.cleanup)
        root = _FALLBACK_CACHE.name
    cache_dir = Path(root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / name
    with open(cache_dir / f"{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not target.exists():
            with tempfile.TemporaryDirectory(dir=cache_dir) as tmp:
                draft = Path(os.path.realpath(tmp)) / name
                build(draft)
                draft.rename(target)
    return target


def _build_empty_env(dest):
    repo = dest.parent / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts/requirements-checks.txt").write_text(EMPTY_REQUIREMENTS)
    shutil.copyfile(SCRIPTS / "check.py", repo / "scripts/check.py")
    subprocess.run(["git", "init", "--quiet", "--initial-branch=main"], cwd=repo, check=True)
    result = subprocess.run([sys.executable, str(repo / "scripts/check.py"), "-c", PRINT_PYTHON],
                            text=True, capture_output=True, check=True)
    Path(result.stdout.strip()).rename(dest)


class CheckRunnerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(os.path.realpath(directory.name))
        self.repo = self.base / "repo"
        for name, content in {
            "scripts/requirements-checks.txt": EMPTY_REQUIREMENTS,
            "scripts/check_skills.py": 'print("ran skills")\n',
            "scripts/check_whitespace.py": 'print("ran whitespace")\n',
            "scripts/test_fixture.py": PASSING_TEST,
            "skills/agent-login/scripts/test_fixture.py": PASSING_TEST,
            "skills/coordinator/scripts/test_fixture.py": PASSING_TEST,
            "skills/create-image/scripts/test_fixture.py": PASSING_TEST,
            "skills/mac-work/scripts/test_fixture.py": PASSING_TEST,
            "skills/pr/scripts/test_fixture.py": PASSING_TEST,
            "skills/review-fix-loop/scripts/test_fixture.py": PASSING_TEST,
            "skills/simulator-lifecycle/scripts/test_fixture.py": PASSING_TEST,
            "skills/writing-for-agents/scripts/test_fixture.py": PASSING_TEST,
        }.items():
            self.write(name, content)
        shutil.copyfile(SCRIPTS / "check.py", self.repo / "scripts/check.py")
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "commit", "--quiet", "-m", "initial")

    def write(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, text=True,
                              capture_output=True, check=True).stdout

    def runner(self, root=None):
        return [sys.executable, str((root or self.repo) / "scripts/check.py")]

    def clean_env(self, extra=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("CHECK_")}
        if extra:
            env.update(extra)
        return env

    def run_checks(self, *args, root=None, cwd=None, code=0, env=None):
        result = subprocess.run(
            [*self.runner(root), *args], cwd=cwd, text=True, capture_output=True,
            env=self.clean_env(env),
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def environment(self, root=None, cwd=None):
        return Path(self.run_checks("-c", PRINT_PYTHON, root=root, cwd=cwd).stdout.strip())

    def preseed_environment(self):
        digest = hashlib.sha256()
        for requirements in sorted((self.repo / "scripts").glob("requirements-*.txt")):
            digest.update(requirements.read_bytes())
        env_hash = digest.hexdigest()[:16]
        template = cached_template(f"check-empty-env-{env_hash}", _build_empty_env)
        dest = self.repo / ".git/sreestack-check-env" / env_hash
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(template, dest, symlinks=True)
        return dest

    def test_worktrees_share_one_environment_outside_their_files(self):
        environment = self.environment()
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))

        self.assertEqual(self.environment(root=worktree), environment)
        self.assertTrue(environment.is_relative_to(self.repo / ".git"))
        self.assertEqual(self.git("status", "--porcelain", cwd=worktree), "")

    def test_worktree_fails_when_the_stable_clone_leaves_main(self):
        self.preseed_environment()
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))
        self.run_checks(root=worktree)

        self.git("switch", "--quiet", "-c", "stray")

        result = self.run_checks(root=worktree, code=1)
        self.assertIn(f"stable clone {self.repo} is not on main", result.stderr)
        self.assertIn("ran skills", result.stdout)
        self.run_checks()

    def test_changed_requirements_get_their_own_environment(self):
        original = self.preseed_environment()
        self.write("scripts/requirements-checks.txt", "# a changed pin\n")

        self.assertNotEqual(self.environment(), original)
        self.assertTrue((original / "bin/python").exists())

    def test_failed_build_leaves_nothing_and_a_later_run_recovers(self):
        requirements = (self.repo / "scripts/requirements-checks.txt").read_text()
        self.write("scripts/requirements-checks.txt", "./missing-package.whl\n")

        result = self.run_checks(code=1)

        self.assertIn("network access", result.stderr)
        self.assertNotIn("ran skills", result.stdout)
        built = (self.repo / ".git/sreestack-check-env").iterdir()
        self.assertEqual([path.name for path in built], ["build.lock"])
        self.write("scripts/requirements-checks.txt", requirements)
        self.run_checks()

    def test_environment_that_lost_its_interpreter_or_packages_is_rebuilt(self):
        environment = self.preseed_environment()
        python = environment / "bin/python"
        python.unlink()
        python.symlink_to(self.base / "removed-python")

        self.assertEqual(self.environment(), environment)
        shutil.rmtree(environment / "lib")

        self.run_checks("-c", "import pip")

    def test_failed_rebuild_keeps_the_existing_environment(self):
        self.write("scripts/requirements-checks.txt", "-r ../outside-the-environment-name.txt\n")
        self.write("outside-the-environment-name.txt", "")
        environment = self.environment()
        shutil.rmtree(environment / "lib")
        (self.repo / "outside-the-environment-name.txt").unlink()

        self.run_checks(code=1)

        self.assertTrue((environment / "bin/python").exists())

    def test_working_directory_modules_cannot_affect_the_environment(self):
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        for module in ("pip.py", "venv.py"):
            (elsewhere / module).write_text("raise SystemExit(1)\n")

        environment = self.environment(cwd=elsewhere)
        (environment / "marker").touch()
        self.run_checks("-c", "pass", cwd=elsewhere)

        self.assertTrue((environment / "marker").exists())

    def test_run_waiting_for_a_build_keeps_the_finished_environment(self):
        environment = self.preseed_environment()
        (environment / "marker").touch()
        finished = self.base / "finished"
        environment.rename(finished)
        with open(environment.parent / "build.lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            waiting = subprocess.Popen([*self.runner(), "-c", "pass"], text=True, stderr=subprocess.PIPE)
            waiting.stderr.readline()  # The run found no environment and is heading for the lock.
            finished.rename(environment)
        _, stderr = waiting.communicate(timeout=60)

        self.assertEqual(waiting.returncode, 0, stderr)
        self.assertTrue((environment / "marker").exists())

    def test_runs_every_check_and_fails_when_any_check_fails(self):
        self.preseed_environment()
        self.assertIn("ran whitespace", self.run_checks().stdout)
        self.write("scripts/check_skills.py", "raise SystemExit(3)\n")

        result = self.run_checks(code=1)

        self.assertIn("ran whitespace", result.stdout)
        self.assertIn("scripts/check_skills.py", result.stderr)

    def test_arguments_run_with_the_environment_python_and_keep_its_exit_status(self):
        self.preseed_environment()
        self.run_checks("-c", "raise SystemExit(7)", code=7)

    def test_parallel_runner_reports_seed_workers_and_proves_every_file_ran(self):
        self.preseed_environment()
        result = self.run_checks()
        self.assertIn("Ran 9 tests across 9 files", result.stdout)
        self.assertIn("seed=", result.stdout)

        seeded = self.run_checks(env={"CHECK_SEED": "42", "CHECK_WORKERS": "2"})
        self.assertIn("with 2 workers (seed=42)", seeded.stdout)

        # Nested package discovery matches stock unittest discover.
        self.write("skills/pr/scripts/nested/__init__.py", "")
        self.write("skills/pr/scripts/nested/test_nested.py", PASSING_TEST)
        nested = self.run_checks()
        self.assertIn("Ran 10 tests across 10 files", nested.stdout)

        # Notes written to _SREESTACK_TEST_CACHE/notes.log surface even when tests pass.
        self.write(
            "skills/pr/scripts/nested/test_nested.py",
            "import os, pathlib, unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_note(self):\n"
            "        (pathlib.Path(os.environ['_SREESTACK_TEST_CACHE']) / 'notes.log').write_text('retry-note\\n')\n",
        )
        noted = self.run_checks()
        self.assertIn("Ran 10 tests across 10 files", noted.stdout)
        self.assertIn("retry-note", noted.stderr)

        # setUpModule SkipTest skips cleanly without failing coverage proof.
        self.write("skills/pr/scripts/nested/test_nested.py",
                   "import unittest\ndef setUpModule(): raise unittest.SkipTest('no chrome')\n" + PASSING_TEST)
        skipped = self.run_checks()
        self.assertIn("Ran 9 tests across 10 files", skipped.stdout)
        self.assertIn("(skipped=1)", skipped.stdout)

        # Unexpected success fails and failure output is surfaced.
        self.write("skills/pr/scripts/nested/test_nested.py",
                   "import unittest\nclass U(unittest.TestCase):\n"
                   "    @unittest.expectedFailure\n"
                   "    def test_x(self): print('diag-marker')\n")
        unexpected = self.run_checks(code=1)
        self.assertIn("Unexpected success", unexpected.stderr)
        self.assertIn("diag-marker", unexpected.stderr)

        # Import error surfaces its traceback without hiding remaining tests or script checks.
        self.write("skills/pr/scripts/nested/test_nested.py", "import nonexistent_module_xyz\n")
        broken_import = self.run_checks(code=1)
        self.assertIn("ModuleNotFoundError", broken_import.stderr)
        self.assertIn("nonexistent_module_xyz", broken_import.stderr)
        self.assertIn("ran skills", broken_import.stdout)
        self.assertIn("ran whitespace", broken_import.stdout)
        self.assertIn("Ran 9 tests across 9 files", broken_import.stdout)

        (self.repo / "skills/pr/scripts/nested/test_nested.py").unlink()
        (self.repo / "scripts/test_fixture.py").unlink()
        missing = self.run_checks(code=1)
        self.assertIn("No test_*.py files found in scripts", missing.stderr)

    def test_changed_since_selects_touched_skills_reruns_all_on_core_and_catches_hidden_change(self):
        self.preseed_environment()
        # Seed a failing coordinator test on main so it is NOT in the branch diff.
        self.write("skills/coordinator/scripts/test_fixture.py",
                   "import unittest\nclass Broken(unittest.TestCase):\n    def test_fail(self): self.fail('hidden')\n")
        self.git("add", "skills/coordinator/scripts/test_fixture.py")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "commit", "--quiet", "-m", "seed hidden coordinator failure on main")

        # 1. Skill-only change selects only that skill's tests (passes despite hidden coordinator failure).
        self.git("switch", "--quiet", "-c", "feature")
        self.write("skills/pr/scripts/note.txt", "touched\n")
        self.git("add", "skills/pr/scripts/note.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "commit", "--quiet", "-m", "touch pr skill")

        narrowed = self.run_checks(env={"CHECK_CHANGED_SINCE": "main"})
        self.assertIn("selected 1/9 test dirs for skills pr", narrowed.stdout)
        self.assertIn("Ran 1 tests across 1 files", narrowed.stdout)

        # 2. Cross-skill rename selects both source and destination skills (--no-renames).
        self.git("switch", "--quiet", "-c", "rename-feature")
        self.git("mv", "skills/pr/scripts/note.txt", "skills/mac-work/scripts/note.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "commit", "--quiet", "-m", "move note across skills")
        renamed = self.run_checks(env={"CHECK_CHANGED_SINCE": "feature"})
        self.assertIn("selected 2/9 test dirs for skills mac-work, pr", renamed.stdout)
        self.assertIn("Ran 2 tests across 2 files", renamed.stdout)

        # 3. Core/shared path change reruns all 9 test dirs and catches the hidden coordinator failure.
        self.git("switch", "--quiet", "main")
        self.git("switch", "--quiet", "-c", "core-feature")
        self.write("scripts/shared_helper.py", "VALUE = 1\n")
        core = self.run_checks(code=1, env={"CHECK_CHANGED_SINCE": "main"})
        self.assertIn("full suite triggered by scripts/shared_helper.py", core.stdout)
        self.assertIn("Ran 9 tests across 9 files", core.stdout)
        self.assertIn("hidden", core.stderr)

        # 4. Docs-only skill change selects 0 test dirs yet still runs check_skills.py and fails on it.
        (self.repo / "scripts/shared_helper.py").unlink()
        self.git("switch", "--quiet", "main")
        self.write("scripts/check_skills.py", "raise SystemExit('broken link')\n")
        self.git("add", "scripts/check_skills.py")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "commit", "--quiet", "-m", "seed failing check_skills on main")
        self.git("switch", "--quiet", "-c", "docs-feature")
        self.write("skills/docs-only/SKILL.md", "---\nname: docs-only\n---\n")
        docs_only = self.run_checks(code=1, env={"CHECK_CHANGED_SINCE": "main"})
        self.assertIn("selected 0/9 test dirs for skills docs-only", docs_only.stdout)
        self.assertIn("Ran 0 tests across 0 files", docs_only.stdout)
        self.assertIn("broken link", docs_only.stderr)

        # 5. Non-HEAD pre-push ref update is refused cleanly; annotated tag on HEAD passes.
        main_sha = self.git("rev-parse", "main").strip()
        head_sha = self.git("rev-parse", "feature").strip()
        non_head = self.run_checks(
            code=1,
            env={"CHECK_CHANGED_SINCE": "main",
                 "CHECK_PUSH_REFS": f"refs/heads/feature {head_sha} refs/heads/feature {main_sha}\n"},
        )
        self.assertIn("pre-push checks validate HEAD", non_head.stderr)
        self.git("switch", "--quiet", "feature")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "tag", "-a", "v1.0", "-m", "release")
        tag_sha = self.git("rev-parse", "v1.0").strip()
        tagged = self.run_checks(
            env={"CHECK_CHANGED_SINCE": "main",
                 "CHECK_PUSH_REFS": f"refs/tags/v1.0 {tag_sha} refs/tags/v1.0 {'0' * 40}\n"},
        )
        self.assertIn("Ran 1 tests across 1 files", tagged.stdout)


class BarePythonTests(unittest.TestCase):
    def test_missing_dependency_names_the_runner(self):
        for command in (["scripts/check_skills.py"],
                        ["-m", "unittest", "discover", "-s", "scripts", "-p", "test_sync_hosts.py"]):
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, "-E", "-S", *command], cwd=SCRIPTS.parent,
                                        text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("python3 scripts/check.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
