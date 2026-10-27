"""Exercise the CI whitespace command against real Git histories."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).with_name("check_whitespace.py")


class WhitespaceCheckTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Whitespace tests")
        self.git("config", "user.email", "test@example.invalid")

    def git(self, *args):
        return subprocess.check_output(
            ["git", *args], cwd=self.repo, text=True, stderr=subprocess.STDOUT
        ).strip()

    def commit(self, text):
        (self.repo / "example.txt").write_text(text)
        self.git("add", "example.txt")
        self.git("commit", "--quiet", "-m", "Update example")
        return self.git("rev-parse", "HEAD")

    def check(self, base, event="push"):
        return subprocess.run(
            [sys.executable, str(CHECKER)], cwd=self.repo,
            env={**os.environ, "BASE_SHA": base, "GITHUB_EVENT_NAME": event},
            text=True, capture_output=True,
        )

    def test_missing_force_push_base_checks_current_tree(self):
        missing_base = self.commit("clean\n")
        self.git("commit", "--quiet", "--amend", "-m", "Rebased history")
        self.git("reflog", "expire", "--expire=now", "--all")
        self.git("gc", "--prune=now")
        absent = subprocess.run(
            ["git", "cat-file", "-e", missing_base], cwd=self.repo,
            capture_output=True,
        )
        self.assertNotEqual(absent.returncode, 0)
        clean = self.check(missing_base)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.commit("new trailing whitespace \n")
        dirty = self.check(missing_base)
        self.assertNotEqual(dirty.returncode, 0)
        self.assertIn("trailing whitespace", dirty.stdout)

    def test_reachable_bases_check_only_the_diff(self):
        base = self.commit("existing whitespace \n")
        self.commit("existing whitespace \nclean addition\n")
        for event in ("push", "pull_request"):
            with self.subTest(event=event):
                result = self.check(base, event)
                self.assertEqual(result.returncode, 0, result.stderr)
        self.commit("existing whitespace \nbad addition \n")
        for event in ("push", "pull_request"):
            with self.subTest(event=event):
                result = self.check(base, event)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("trailing whitespace", result.stdout)

    def test_new_branch_checks_the_root_commit(self):
        self.commit("clean\n")
        for base in ("", "0" * 40):
            with self.subTest(base=base):
                result = self.check(base)
                self.assertEqual(result.returncode, 0, result.stderr)
        self.commit("bad root content \n")
        self.commit("bad root content \nclean addition\n")
        for base in ("", "0" * 40):
            with self.subTest(base=base):
                result = self.check(base)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("trailing whitespace", result.stdout)

    def test_missing_pull_request_base_fails(self):
        self.commit("clean\n")
        result = self.check("1" * 40, "pull_request")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an available commit", result.stderr)

    def test_noncommit_or_invalid_base_fails_even_on_push(self):
        self.commit("clean\n")
        for base in (self.git("rev-parse", "HEAD:example.txt"), "invalid-base"):
            with self.subTest(base=base):
                result = self.check(base)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("BASE_SHA" if base == "invalid-base" else "not an available commit", result.stderr)

    def test_git_errors_are_not_replaced_by_fallback(self):
        result = self.check("1" * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Needed a single revision", result.stderr)


if __name__ == "__main__":
    unittest.main()
