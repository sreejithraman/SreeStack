import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from convergence import analyze, format_report

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


class ConvergenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git("init", "-q")
        self.write("app.py", "def run():\n    return 1\n")
        self.base = self.commit("base")

    def git(self, *args: str) -> str:
        return subprocess.check_output(["git", "-C", str(self.repo), *args], env=GIT_ENV, text=True).strip()

    def write(self, rel: str, content: str) -> None:
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def commit(self, msg: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def test_converging_after_single_small_repair(self):
        self.write("app.py", "\n".join(f"line_{i} = {i}" for i in range(40)) + "\n")
        self.write("other.py", "x = 1\n")
        pass1 = self.commit("pass 1")
        self.write("other.py", "x = 2\n")
        head = self.commit("repair 1")
        data = analyze(self.repo, self.base, pass1, head)
        self.assertEqual(data["mode"], "CONVERGING")
        self.assertEqual(data["pass"], 2)
        self.assertEqual(data["repeated"], [])
        self.assertEqual(data["bloated"], [])
        self.assertIn("mode: CONVERGING", format_report(data))

    def test_premise_cut_on_consecutive_hits_to_same_production_file(self):
        self.write("app.py", "x = 1\n")
        pass1 = self.commit("pass 1")
        self.write("app.py", "x = 2\n")
        self.commit("repair 1")
        self.write("app.py", "x = 3\n")
        head = self.commit("repair 2")
        data = analyze(self.repo, self.base, pass1, head)
        self.assertEqual(data["mode"], "PREMISE_CUT")
        self.assertEqual(data["repeated"][0]["file"], "app.py")
        self.assertEqual(data["repeated"][0]["consecutive"], 2)
        self.assertIn("Additive patching forbidden on app.py", data["action"])

    def test_premise_cut_on_repair_bloat(self):
        self.write("app.py", "\n".join(f"a{i} = {i}" for i in range(120)) + "\n")
        pass1 = self.commit("pass 1")
        # Single repair adding >100 lines and >50% of Pass 1 churn triggers PREMISE_CUT.
        self.write("app.py", "\n".join(f"a{i} = {i}" for i in range(240)) + "\n")
        head = self.commit("repair bloat")
        data = analyze(self.repo, self.base, pass1, head)
        self.assertEqual(data["mode"], "PREMISE_CUT")
        self.assertEqual(data["bloated"][0]["file"], "app.py")

    def test_defer_and_finish_when_oscillation_persists_after_premise_cut(self):
        self.write("app.py", "x = 1\n")
        pass1 = self.commit("pass 1")
        self.write("app.py", "x = 2\n")
        self.commit("repair 1")
        self.write("app.py", "x = 3\n")
        cut = self.commit("premise cut")
        self.write("app.py", "x = 4\n")
        self.commit("post-cut 1")
        self.write("app.py", "x = 5\n")
        head = self.commit("post-cut 2")
        data = analyze(self.repo, self.base, pass1, head, premise_cut_at=cut)
        self.assertEqual(data["mode"], "DEFER_AND_FINISH")
        self.assertEqual(data["post_cut_repeated"][0]["file"], "app.py")

    def test_test_only_file_repeats_do_not_trigger_premise_cut(self):
        self.write("app.py", "x = 1\n")
        self.write("test_app.py", "t = 1\n")
        pass1 = self.commit("pass 1")
        self.write("test_app.py", "t = 2\n")
        self.commit("test fix 1")
        self.write("test_app.py", "t = 3\n")
        head = self.commit("test fix 2")
        data = analyze(self.repo, self.base, pass1, head)
        self.assertEqual(data["mode"], "CONVERGING")


if __name__ == "__main__":
    unittest.main()
