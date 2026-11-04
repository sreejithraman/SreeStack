"""Exercise the check runner against small Git repositories."""

import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).parent
PASSING_TEST = """\
import unittest


class Passing(unittest.TestCase):
    def test_passes(self):
        pass
"""
PRINT_PYTHON = "import sys; print(sys.prefix)"


class CheckRunnerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(os.path.realpath(directory.name))
        self.repo = self.base / "repo"
        for name, content in {
            "scripts/requirements-checks.txt": "# no packages, so tests need no network\n",
            "scripts/check_skills.py": 'print("ran skills")\n',
            "scripts/check_whitespace.py": 'print("ran whitespace")\n',
            "scripts/test_fixture.py": PASSING_TEST,
            "skills/chief-of-staff/scripts/test_fixture.py": PASSING_TEST,
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

    def run_checks(self, *args, root=None, cwd=None, code=0):
        result = subprocess.run([*self.runner(root), *args], cwd=cwd, text=True, capture_output=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def environment(self, root=None, cwd=None):
        return Path(self.run_checks("-c", PRINT_PYTHON, root=root, cwd=cwd).stdout.strip())

    def test_worktrees_share_one_environment_outside_their_files(self):
        environment = self.environment()
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))

        self.assertEqual(self.environment(root=worktree), environment)
        self.assertTrue(environment.is_relative_to(self.repo / ".git"))
        self.assertEqual(self.git("status", "--porcelain", cwd=worktree), "")

    def test_changed_requirements_get_their_own_environment(self):
        original = self.environment()
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
        environment = self.environment()
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
        environment = self.environment()
        (environment / "marker").touch()
        finished = self.base / "finished"
        environment.rename(finished)
        with open(environment.parent / "build.lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            waiting = subprocess.Popen([*self.runner(), "-c", "pass"], text=True, stderr=subprocess.PIPE)
            waiting.stderr.readline()  # The run found no environment and reached the lock.
            finished.rename(environment)
        _, stderr = waiting.communicate(timeout=60)

        self.assertEqual(waiting.returncode, 0, stderr)
        self.assertTrue((environment / "marker").exists())

    def test_runs_every_check_and_fails_when_any_check_fails(self):
        self.assertIn("ran whitespace", self.run_checks().stdout)
        self.write("scripts/check_skills.py", "raise SystemExit(3)\n")

        result = self.run_checks(code=1)

        self.assertIn("ran whitespace", result.stdout)
        self.assertIn("scripts/check_skills.py", result.stderr)

    def test_arguments_run_with_the_environment_python_and_keep_its_exit_status(self):
        self.run_checks("-c", "raise SystemExit(7)", code=7)


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
