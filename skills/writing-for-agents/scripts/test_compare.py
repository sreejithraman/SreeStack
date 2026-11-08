import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

import compare
from hosts import RunResult


class FakeAgent:
    """Answers calibration probes from the skill tree it is given, and tasks from `behavior`."""

    telemetry_notes = "fake"

    def __init__(self, behavior=None, leak=False, crash=False):
        self.behavior = behavior or {}
        self.leak = leak
        self.crash = crash
        self.sessions = []

    def version(self):
        return "fake 1"

    def installed_skill_names(self):
        return {"installed-skill"}

    def run(self, *, skills, prompt, work, out, settings, scratch, variant):
        self.sessions.append((variant, prompt))
        names = sorted(p.name for p in skills.iterdir()) if skills else []
        listing = ", ".join(names + (["installed-skill"] if self.leak else []))
        canary = re.search(r"calib-canary-\w+", prompt)
        if prompt.startswith("Use the") and canary:
            body = (skills / canary.group() / "SKILL.md").read_text()
            return RunResult(answer=re.search(r"CANARY-\w+", body).group(),
                             calls=[{"name": "Skill", "skill": canary.group()}])
        if "NO-SKILL" in prompt:
            return RunResult(answer=f"NO-SKILL\n{listing}", calls=[])
        if "echo calib-" in prompt:
            return RunResult(answer="calib-42", calls=[{"name": "Bash", "command": "echo calib-$((6*7))"}])
        if prompt.startswith("List the name"):
            return RunResult(answer=listing, calls=[])
        if self.crash:
            raise RuntimeError("host went away")
        outcome = self.behavior.get((variant, prompt), {})
        if outcome.get("pass", True):
            (work / "done.txt").write_text("done")
        return RunResult(answer="ok", calls=[{"name": "Bash"}] * outcome.get("calls", 1),
                         cost_usd=outcome.get("cost", 0.01), turns=1, tokens={"output": 10})


def make_eval(root: Path, target=None, tasks=None) -> Path:
    for variant, text in (("old", "old rule"), ("new", "new rule")):
        skill = root / "variants" / variant / "helper"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"---\nname: helper\ndescription: Use when helping.\n---\n\n{text}\n")
    (root / "fixtures/repo").mkdir(parents=True)
    (root / "fixtures/repo/README").write_text("fixture")
    (root / "manifest.json").write_text(json.dumps({
        "version": 1,
        "host": {"adapter": "claude", "model": "fake"},
        "variants": {"old": "variants/old", "new": "variants/new"},
        "baseline": "old", "candidate": "new", "repeats": 3,
        "target": target or {"metric": "cost_usd", "why": "cheaper at the same quality"},
        "tasks": tasks or [
            {"id": "required", "prompt": "do required", "fixture": "fixtures/repo", "required": True,
             "checks": ["test -f done.txt"]},
            {"id": "optional", "prompt": "do optional", "fixture": "fixtures/repo", "checks": ["test -f done.txt"]},
        ],
    }))
    return root


class CompareTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.root = make_eval(self.directory())

    def directory(self):
        path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, path)
        return path

    def evaluate(self, agent):
        return compare.Eval(self.root, adapter=agent)

    def run_all(self, agent, **options):
        compare.run(self.evaluate(agent), **options)
        return compare.score(self.evaluate(agent))

    def test_win_when_cheaper_and_every_case_passes(self):
        cheaper = {("new", p): {"cost": 0.005} for p in ("do required", "do optional")}
        report = self.run_all(FakeAgent(cheaper))
        self.assertTrue(report["decision"].startswith("win"), report["decision"])

    def test_score_rejects_an_incomplete_matrix(self):
        compare.run(self.evaluate(FakeAgent()), only=["required"])
        with self.assertRaisesRegex(compare.InvalidEvidence, "missing cell optional/old/0"):
            compare.score(self.evaluate(FakeAgent()))

    def test_changed_inputs_make_results_stale(self):
        self.run_all(FakeAgent())
        (self.root / "fixtures/repo/README").write_text("changed fixture")
        with self.assertRaisesRegex(compare.InvalidEvidence, "stale cell"):
            compare.score(self.evaluate(FakeAgent()))
        with self.assertRaisesRegex(compare.InvalidEvidence, "changed inputs"):
            compare.run(self.evaluate(FakeAgent()))
        compare.run(self.evaluate(FakeAgent()), replace_stale=True)
        self.assertTrue(list((self.root / "superseded").rglob("result.json")))
        compare.score(self.evaluate(FakeAgent()))

    def test_a_failed_required_case_vetoes_a_cheaper_candidate(self):
        behavior = {("new", "do required"): {"pass": False, "cost": 0.001},
                    ("new", "do optional"): {"cost": 0.001}}
        report = self.run_all(FakeAgent(behavior))
        self.assertTrue(report["decision"].startswith("reject"), report["decision"])
        self.assertEqual(report["required_vetoes"], ["required/0", "required/1", "required/2"])

    def test_equal_results_are_no_win(self):
        report = self.run_all(FakeAgent())
        self.assertTrue(report["decision"].startswith("no win"), report["decision"])
        self.assertIn("equal", report["decision"])

    def test_equal_pass_rates_are_no_win(self):
        self.root = make_eval(self.directory(), target={"metric": "pass_rate"})
        report = self.run_all(FakeAgent())
        self.assertTrue(report["decision"].startswith("no win"), report["decision"])

    def test_missing_cost_telemetry_is_unproven_not_zero(self):
        no_cost = {(v, p): {"cost": None} for v in ("old", "new") for p in ("do required", "do optional")}
        report = self.run_all(FakeAgent(no_cost))
        self.assertTrue(report["decision"].startswith("unproven"), report["decision"])
        self.assertEqual(report["unavailable_telemetry"]["cost_usd"], {"old": "6/6 runs", "new": "6/6 runs"})
        self.assertIsNone(report["summary"]["new"]["cost_usd"])

    def test_a_corrected_failure_wins_only_when_every_repeat_passes(self):
        self.root = make_eval(self.directory(), target={"metric": "task_pass", "task": "optional"})
        report = self.run_all(FakeAgent({("old", "do optional"): {"pass": False}}))
        self.assertTrue(report["decision"].startswith("win"), report["decision"])

    def test_cheaper_with_a_lower_pass_rate_is_a_tradeoff(self):
        behavior = {("new", "do required"): {"cost": 0.001}, ("new", "do optional"): {"pass": False, "cost": 0.001}}
        report = self.run_all(FakeAgent(behavior))
        self.assertTrue(report["decision"].startswith("tradeoff"), report["decision"])

    def test_variant_order_alternates(self):
        plan = self.evaluate(FakeAgent()).plan()
        firsts = [plan[i][1] for i in range(0, len(plan), 2)]
        self.assertEqual(set(firsts), {"old", "new"})

    def test_failed_sessions_keep_their_evidence_and_fixture(self):
        report = self.run_all(FakeAgent(crash=True))
        self.assertTrue(report["decision"].startswith("reject"), report["decision"])
        cell = self.root / "runs/required/new/0"
        stored = json.loads((cell / "result.json").read_text())
        self.assertEqual(stored["status"], "error")
        self.assertIn("host went away", stored["error"])
        self.assertEqual((cell / "work/README").read_text(), "fixture")

    def test_a_leaking_host_fails_calibration_and_blocks_the_run(self):
        with self.assertRaisesRegex(compare.InvalidEvidence, "calibration failed"):
            compare.run(self.evaluate(FakeAgent(leak=True)))
        self.assertFalse((self.root / "runs").exists())

    def test_judged_tasks_need_current_blind_verdicts(self):
        self.root = make_eval(self.directory(), tasks=[
            {"id": "prose", "prompt": "write it", "required": True, "judge": "Is it clear?"}])
        compare.run(self.evaluate(FakeAgent()))
        with self.assertRaisesRegex(compare.InvalidEvidence, "no current judge verdict"):
            compare.score(self.evaluate(FakeAgent()))
        judging = compare.blind(self.evaluate(FakeAgent()))
        packet = json.loads((judging / "packet.json").read_text())
        self.assertNotIn("variant", json.dumps(packet))
        (judging / "verdicts.json").write_text(json.dumps({item["id"]: {"pass": True} for item in packet}))
        report = compare.score(self.evaluate(FakeAgent()))
        self.assertEqual(report["tasks"]["prose"], {"old": "3/3", "new": "3/3"})


if __name__ == "__main__":
    unittest.main()
