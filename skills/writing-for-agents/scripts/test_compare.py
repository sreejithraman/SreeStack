import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import compare
import hosts
from hosts import RunResult

SENTINEL = "sentinel-not-a-real-secret-7f3a"


class FakeAgent:
    """Answers calibration probes from the skill tree it is given, and tasks from `behavior`.

    A behavior is one outcome, or a list of outcomes for successive repeats.
    """

    telemetry_notes = "fake"

    def __init__(self, behavior=None, leak=False, crash=False, answer="ok"):
        self.behavior = behavior or {}
        self.leak = leak
        self.crash = crash
        self.answer = answer
        self.sessions = []

    def version(self):
        return "fake 1"

    def installed_skill_names(self):
        return {"installed-skill"}

    def run(self, *, skills, prompt, work, out, settings, scratch, variant):
        self.sessions.append((variant, prompt, sorted(p.name for p in work.iterdir())))
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
        if isinstance(outcome, list):
            outcome = outcome[sum(1 for s in self.sessions if s[:2] == (variant, prompt)) - 1]
        if outcome.get("pass", True):
            (work / "done.txt").write_text("done")
        return RunResult(answer=self.answer, calls=[{"name": "Bash", "command": self.answer}] * outcome.get("calls", 1),
                         cost_usd=outcome.get("cost", 0.01), turns=1, tokens={"output": 10})


def write_manifest(root: Path, **changes) -> None:
    path = root / "manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else {
        "version": 1, "host": {"adapter": "claude", "model": "fake"},
        "variants": {"old": "variants/old", "new": "variants/new"}, "baseline": "old", "candidate": "new"}
    manifest.update(changes)
    path.write_text(json.dumps(manifest))


def make_eval(root: Path, target=None, tasks=None) -> Path:
    for variant, text in (("old", "old rule"), ("new", "new rule")):
        skill = root / "variants" / variant / "helper"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"---\nname: helper\ndescription: Use when helping.\n---\n\n{text}\n")
    (root / "fixtures/repo").mkdir(parents=True)
    (root / "fixtures/repo/README").write_text("fixture")
    write_manifest(root, repeats=3, target=target or {"metric": "cost_usd", "why": "cheaper at the same quality"},
                   tasks=tasks or [
                       {"id": "required", "prompt": "do required", "fixture": "fixtures/repo", "required": True,
                        "checks": ["test -f done.txt"]},
                       {"id": "optional", "prompt": "do optional", "fixture": "fixtures/repo",
                        "checks": ["test -f done.txt"]},
                   ])
    return root


def cheaper():
    return {("new", p): {"cost": 0.005} for p in ("do required", "do optional")}


def one_late_required_failure():
    behavior = cheaper()
    behavior[("new", "do required")] = [{"cost": 0.005}, {"cost": 0.005}, {"pass": False, "cost": 0.005}]
    return behavior


class CompareTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.root = make_eval(self.directory())

    def directory(self):
        path = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, path)
        return path

    def evaluate(self, agent):
        return compare.Eval(self.root, adapter=agent)

    def run_all(self, agent, **options):
        compare.run(self.evaluate(agent), **options)
        return compare.score(self.evaluate(agent))

    def judged_eval(self):
        self.root = make_eval(self.directory(), tasks=[
            {"id": "prose", "prompt": "write it", "required": True, "judge": "Is it clear?"}])
        compare.run(self.evaluate(FakeAgent()))
        judging = compare.blind(self.evaluate(FakeAgent()))
        return judging, json.loads((judging / "packet.json").read_text())

    def assertRefusedBeforeSessions(self, pattern):
        agent = FakeAgent()
        with self.assertRaisesRegex(compare.InvalidEvidence, pattern):
            compare.run(compare.Eval(self.root, adapter=agent))
        self.assertEqual(agent.sessions, [])

    # Decisions

    def test_win_when_cheaper_and_every_case_passes(self):
        report = self.run_all(FakeAgent(cheaper()))
        self.assertTrue(report["decision"].startswith("win"), report["decision"])

    def test_a_failed_required_case_vetoes_a_cheaper_candidate(self):
        behavior = {("new", "do required"): {"pass": False, "cost": 0.001},
                    ("new", "do optional"): {"cost": 0.001}}
        report = self.run_all(FakeAgent(behavior))
        self.assertTrue(report["decision"].startswith("reject"), report["decision"])
        self.assertEqual(report["required_vetoes"], ["required/0", "required/1", "required/2"])

    def test_one_failed_required_repeat_vetoes(self):
        report = self.run_all(FakeAgent(one_late_required_failure()))
        self.assertTrue(report["decision"].startswith("reject"), report["decision"])
        self.assertEqual(report["required_vetoes"], ["required/2"])

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

    def test_a_corrected_failure_wins_when_every_repeat_passes(self):
        self.root = make_eval(self.directory(), target={"metric": "task_pass", "task": "optional"})
        report = self.run_all(FakeAgent({("old", "do optional"): {"pass": False}}))
        self.assertTrue(report["decision"].startswith("win"), report["decision"])

    def test_a_corrected_failure_with_mixed_repeats_is_no_win(self):
        self.root = make_eval(self.directory(), target={"metric": "task_pass", "task": "optional"})
        behavior = {("old", "do optional"): {"pass": False}, ("new", "do optional"): [{}, {}, {"pass": False}]}
        report = self.run_all(FakeAgent(behavior))
        self.assertEqual(report["tasks"]["optional"], {"old": "0/3", "new": "2/3"})
        self.assertTrue(report["decision"].startswith("no win"), report["decision"])

    def test_cheaper_with_a_lower_pass_rate_is_a_tradeoff(self):
        behavior = {("new", "do required"): {"cost": 0.001}, ("new", "do optional"): {"pass": False, "cost": 0.001}}
        report = self.run_all(FakeAgent(behavior))
        self.assertTrue(report["decision"].startswith("tradeoff"), report["decision"])

    def test_each_task_alternates_variant_order_across_repeats(self):
        plan = self.evaluate(FakeAgent()).plan()
        for task in ("required", "optional"):
            firsts = [next(v for t, v, r in plan if t == task and r == repeat) for repeat in range(3)]
            self.assertNotEqual(firsts[0], firsts[1])
            self.assertNotEqual(firsts[1], firsts[2])

    # Evidence

    def test_score_rejects_an_incomplete_matrix(self):
        compare.run(self.evaluate(FakeAgent()), only=["required"])
        with self.assertRaisesRegex(compare.InvalidEvidence, "missing cell optional/old/0"):
            compare.score(self.evaluate(FakeAgent()))

    def test_changed_inputs_make_results_stale(self):
        self.run_all(FakeAgent())
        (self.root / "fixtures/repo/README").write_text("changed fixture")
        with self.assertRaisesRegex(compare.InvalidEvidence, "stale cell"):
            compare.score(self.evaluate(FakeAgent()))
        with self.assertRaisesRegex(compare.InvalidEvidence, "earlier experiment"):
            compare.run(self.evaluate(FakeAgent()))
        compare.run(self.evaluate(FakeAgent()), replace_stale=True)
        self.assertTrue(list((self.root / "superseded").rglob("result.json")))
        compare.score(self.evaluate(FakeAgent()))

    def test_a_changed_checker_script_makes_results_stale(self):
        (self.root / "checker.sh").write_text("test -f done.txt\n")
        write_manifest(self.root, tasks=[{"id": "required", "prompt": "do required", "fixture": "fixtures/repo",
                                          "required": True, "checks": [f"sh {self.root}/checker.sh"]}])
        self.run_all(FakeAgent())
        (self.root / "checker.sh").write_text("exit 1\n")
        with self.assertRaisesRegex(compare.InvalidEvidence, "stale cell"):
            compare.score(self.evaluate(FakeAgent()))

    def test_retargeting_after_the_run_makes_results_stale(self):
        self.run_all(FakeAgent())
        write_manifest(self.root, target={"metric": "tool_calls"})
        with self.assertRaisesRegex(compare.InvalidEvidence, "stale cell"):
            compare.score(self.evaluate(FakeAgent()))

    def test_fewer_repeats_cannot_drop_a_recorded_required_failure(self):
        self.run_all(FakeAgent(one_late_required_failure()))
        write_manifest(self.root, repeats=2)
        with self.assertRaises(compare.InvalidEvidence):
            compare.score(self.evaluate(FakeAgent()))

    def test_malformed_results_are_invalid_evidence_with_exit_2(self):
        self.run_all(FakeAgent())
        cell = self.root / "runs/required/new/0/result.json"
        good = json.loads(cell.read_text())
        cell.write_text('{"identity": "trunc')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(compare.main(["score", str(self.root)], adapter=FakeAgent()), 2)
        cell.write_text(json.dumps({**good, "checks": [{"exit": "0"}]}))
        with self.assertRaisesRegex(compare.InvalidEvidence, "malformed result"):
            compare.score(self.evaluate(FakeAgent()))

    def test_results_outside_the_plan_are_invalid(self):
        self.run_all(FakeAgent())
        shutil.copytree(self.root / "runs/required/new/0", self.root / "runs/required/new/7")
        with self.assertRaisesRegex(compare.InvalidEvidence, "outside the plan"):
            compare.score(self.evaluate(FakeAgent()))

    def test_failed_sessions_keep_their_evidence_and_fixture(self):
        report = self.run_all(FakeAgent(crash=True))
        self.assertTrue(report["decision"].startswith("reject"), report["decision"])
        cell = self.root / "runs/required/new/0"
        stored = json.loads((cell / "result.json").read_text())
        self.assertEqual(stored["status"], "error")
        self.assertIn("host went away", stored["error"])
        self.assertEqual((cell / "work/README").read_text(), "fixture")

    def test_a_hung_check_times_out_as_a_failed_check(self):
        write_manifest(self.root, host={"adapter": "claude", "model": "fake", "check_timeout_seconds": 0.2},
                       tasks=[{"id": "slow", "prompt": "do it", "required": True, "checks": ["sleep 30"]}],
                       repeats=1)
        with mock.patch("hosts.GRACE_SECONDS", 0.2):
            report = self.run_all(FakeAgent())
        stored = json.loads((self.root / "runs/slow/new/0/result.json").read_text())
        self.assertEqual(stored["checks"][0]["exit"], "timeout")
        self.assertTrue(report["decision"].startswith("reject"), report["decision"])

    # Refusals before any session

    def test_symlinks_in_a_fixture_or_variant_are_refused(self):
        os.symlink("/etc/hosts", self.root / "fixtures/repo/hosts")
        self.assertRefusedBeforeSessions("symlink not allowed")
        os.unlink(self.root / "fixtures/repo/hosts")
        os.symlink(self.root / "fixtures", self.root / "variants/new/linked")
        self.assertRefusedBeforeSessions("symlink not allowed")

    def test_unsafe_names_are_refused(self):
        for name in ("../escape", "/tmp/abs", ".hidden"):
            write_manifest(self.root, tasks=[{"id": name, "prompt": "p"}])
            with self.assertRaisesRegex(compare.InvalidEvidence, "unsafe task id"):
                self.evaluate(FakeAgent())
        write_manifest(self.root, tasks=[{"id": "ok", "prompt": "p"}],
                       variants={"old": "variants/old", "../new": "variants/new"})
        with self.assertRaisesRegex(compare.InvalidEvidence, "unsafe variant name"):
            self.evaluate(FakeAgent())

    def test_outputs_cannot_leave_the_eval_dir(self):
        outside = self.directory()
        os.symlink(outside, self.root / "runs")
        with self.assertRaisesRegex(compare.InvalidEvidence, "symlink not allowed"):
            compare.run(self.evaluate(FakeAgent()))
        self.assertEqual(list(outside.iterdir()), [])

    def test_duplicate_task_ids_are_refused(self):
        write_manifest(self.root, tasks=[{"id": "same", "prompt": "a", "required": True},
                                         {"id": "same", "prompt": "b"}])
        with self.assertRaisesRegex(compare.InvalidEvidence, "unique"):
            self.evaluate(FakeAgent())

    def test_fixtures_holding_skill_directories_are_refused(self):
        for directory in (".claude/skills/extra", ".agents", "deep/.codex"):
            (self.root / "fixtures/repo" / directory).mkdir(parents=True)
            with self.assertRaisesRegex(compare.InvalidEvidence, "skill discovery"):
                self.evaluate(FakeAgent())
            shutil.rmtree(self.root / "fixtures/repo" / directory.split("/")[0])

    # Calibration

    def test_calibration_runs_in_a_real_task_fixture(self):
        agent = FakeAgent()
        self.assertTrue(compare.calibrate(self.evaluate(agent)))
        self.assertTrue(agent.sessions)
        self.assertTrue(all(contents == ["README"] for _, _, contents in agent.sessions))

    def test_a_leaking_host_fails_calibration_and_blocks_the_run(self):
        with self.assertRaisesRegex(compare.InvalidEvidence, "calibration failed"):
            compare.run(self.evaluate(FakeAgent(leak=True)))
        self.assertFalse((self.root / "runs").exists())

    def test_a_failed_recalibration_revokes_the_earlier_pass(self):
        self.assertTrue(compare.calibrate(self.evaluate(FakeAgent())))
        self.assertFalse(compare.calibrate(self.evaluate(FakeAgent(leak=True))))
        with self.assertRaisesRegex(compare.InvalidEvidence, "calibration failed"):
            compare.run(self.evaluate(FakeAgent(leak=True)))
        self.assertFalse((self.root / "runs").exists())

    def test_score_needs_calibration_of_this_experiment(self):
        self.run_all(FakeAgent())
        (self.root / "calibration/passed.json").write_text(json.dumps({"identity": "another experiment"}))
        with self.assertRaisesRegex(compare.InvalidEvidence, "no passing calibration"):
            compare.score(self.evaluate(FakeAgent()))

    # Judging

    def test_judged_tasks_need_current_blind_verdicts(self):
        judging, packet = self.judged_eval()
        self.assertNotIn("variant", json.dumps(packet))
        (judging / "verdicts.json").unlink(missing_ok=True)
        with self.assertRaisesRegex(compare.InvalidEvidence, "no current judge verdict"):
            compare.score(self.evaluate(FakeAgent()))
        (judging / "verdicts.json").write_text(json.dumps({item["id"]: {"pass": True} for item in packet}))
        report = compare.score(self.evaluate(FakeAgent()))
        self.assertEqual(report["tasks"]["prose"], {"old": "3/3", "new": "3/3"})

    def test_a_verdict_must_be_a_json_boolean(self):
        judging, packet = self.judged_eval()
        for verdict in ("false", 0, None):
            (judging / "verdicts.json").write_text(json.dumps({item["id"]: {"pass": verdict} for item in packet}))
            with self.assertRaisesRegex(compare.InvalidEvidence, "JSON boolean"):
                compare.score(self.evaluate(FakeAgent()))

    # Secrets

    def test_checks_get_an_allowlisted_environment_and_evidence_is_redacted(self):
        write_manifest(self.root, repeats=1, tasks=[{
            "id": "env", "prompt": "p", "required": True,
            "checks": [f'env > "$EVAL_OUT/env.txt"; echo "HOME=$HOME"; echo {SENTINEL}']}])
        with mock.patch.dict(os.environ, {"EVAL_TEST_API_KEY": SENTINEL}):
            self.run_all(FakeAgent(answer=f"leaked {SENTINEL}"))
        cell = self.root / "runs/env/new/0"
        names = {line.split("=", 1)[0] for line in (cell / "env.txt").read_text().splitlines()}
        self.assertLessEqual(names, {"PATH", "LANG", "TMPDIR", "HOME", "EVAL_WORK", "EVAL_OUT", "PWD", "SHLVL", "_"})
        self.assertRegex((cell / "check-0.log").read_text(), r"HOME=\S+/work\n")
        for path in cell.rglob("*"):
            if path.is_file():
                self.assertNotIn(SENTINEL, path.read_text(errors="replace"), path)
        self.assertIn("[REDACTED]", (cell / "answer.txt").read_text())
        self.assertIn("[REDACTED]", (cell / "check-0.log").read_text())

    def test_a_nested_runs_symlink_blocks_replace_stale_and_outside_data_stays(self):
        outside = self.directory()
        (outside / "old/0").mkdir(parents=True)
        (outside / "old/0/result.json").write_text(json.dumps({"identity": "earlier"}))
        (outside / "old/0/important.txt").write_text("keep me")
        (self.root / "runs").mkdir()
        os.symlink(outside, self.root / "runs/required")
        with self.assertRaisesRegex(compare.InvalidEvidence, "symlink not allowed"):
            compare.run(self.evaluate(FakeAgent()), replace_stale=True)
        self.assertEqual((outside / "old/0/important.txt").read_text(), "keep me")
        self.assertFalse((self.root / "superseded").exists())

    def test_inputs_cannot_overlap_the_runner_output(self):
        shutil.copytree(self.root / "variants/new", self.root / "judging/new")
        write_manifest(self.root, variants={"old": "variants/old", "new": "judging/new"})
        with self.assertRaisesRegex(compare.InvalidEvidence, "overlaps the runner's output"):
            self.evaluate(FakeAgent())
        write_manifest(self.root, variants={"old": "variants/old", "new": "variants/new"},
                       tasks=[{"id": "t", "prompt": "p", "fixture": "."}])
        with self.assertRaisesRegex(compare.InvalidEvidence, "overlaps the runner's output"):
            self.evaluate(FakeAgent())

    def test_dropped_check_evidence_is_invalid_through_the_cli(self):
        behavior = {("new", "do required"): {"pass": False, "cost": 0.001}, ("new", "do optional"): {"cost": 0.001}}
        self.run_all(FakeAgent(behavior))
        for repeat in range(3):
            cell = self.root / f"runs/required/new/{repeat}/result.json"
            cell.write_text(json.dumps({**json.loads(cell.read_text()), "checks": []}))
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(compare.main(["score", str(self.root)], adapter=FakeAgent()), 2)
        self.assertIn("don't match the manifest's checks", errors.getvalue())

    def test_a_malformed_calibration_record_is_invalid_through_the_cli(self):
        self.run_all(FakeAgent())
        (self.root / "calibration/passed.json").write_text("[]")
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(compare.main(["score", str(self.root)], adapter=FakeAgent()), 2)
        self.assertIn("malformed record", errors.getvalue())

    def test_secrets_a_host_writes_into_kept_work_are_redacted(self):
        class Writer(FakeAgent):
            def run(self, *, work, prompt, **rest):
                if prompt.startswith("do "):
                    (work / "tool-debug.log").write_text(f"KEY={os.environ['EVAL_TEST_API_KEY']}\n")
                return super().run(work=work, prompt=prompt, **rest)

        with mock.patch.dict(os.environ, {"EVAL_TEST_API_KEY": SENTINEL}):
            self.run_all(Writer())
        logs = list((self.root / "runs").rglob("tool-debug.log"))
        self.assertTrue(logs)
        for log in logs:
            self.assertEqual(log.read_text(), "KEY=[REDACTED]\n")

    def test_secrets_in_undecodable_work_files_are_redacted(self):
        class Writer(FakeAgent):
            def run(self, *, work, prompt, **rest):
                if prompt.startswith("do "):
                    (work / "tool-debug.bin").write_bytes(b"\xff\x00KEY=" + os.environ["EVAL_TEST_API_KEY"].encode())
                return super().run(work=work, prompt=prompt, **rest)

        with mock.patch.dict(os.environ, {"EVAL_TEST_API_KEY": SENTINEL}):
            self.run_all(Writer())
        kept = list((self.root / "runs").rglob("tool-debug.bin"))
        self.assertEqual(len(kept), 12)
        for path in kept:
            self.assertEqual(path.read_bytes(), b"\xff\x00KEY=[REDACTED]")

    def test_a_read_only_binary_work_file_is_redacted_and_keeps_its_mode(self):
        class Writer(FakeAgent):
            def run(self, *, work, prompt, **rest):
                if prompt.startswith("do "):
                    path = work / "tool-debug.bin"
                    path.write_bytes(b"\xff\x00KEY=" + os.environ["EVAL_TEST_API_KEY"].encode())
                    path.chmod(0o444)
                return super().run(work=work, prompt=prompt, **rest)

        with mock.patch.dict(os.environ, {"EVAL_TEST_API_KEY": SENTINEL}):
            self.run_all(Writer())
        kept = list((self.root / "runs").rglob("tool-debug.bin"))
        self.assertEqual(len(kept), 12)
        for path in kept:
            self.assertEqual(path.read_bytes(), b"\xff\x00KEY=[REDACTED]")
            self.assertEqual(path.stat().st_mode & 0o777, 0o444)

    def test_a_link_a_check_leaves_in_its_output_is_not_followed(self):
        original = self.root / "fixtures/repo/important.txt"
        original.write_bytes(f"keep this exact data: {SENTINEL}".encode())
        write_manifest(self.root, repeats=1, tasks=[{
            "id": "link", "prompt": "do it", "fixture": "fixtures/repo", "required": True,
            "checks": [f'ln -s {original} "$EVAL_OUT/diagnostic-link"']}])
        with mock.patch.dict(os.environ, {"EVAL_TEST_API_KEY": SENTINEL}):
            compare.run(self.evaluate(FakeAgent()))
        self.assertEqual(original.read_bytes(), f"keep this exact data: {SENTINEL}".encode())
        for variant in ("old", "new"):
            note = self.root / f"runs/link/{variant}/0/diagnostic-link"
            self.assertFalse(note.is_symlink())
            self.assertTrue(note.read_text().startswith("symlink to "))
        compare.score(self.evaluate(FakeAgent()))

    def test_a_file_that_cannot_be_redacted_is_removed_and_the_sweep_continues(self):
        class Writer(FakeAgent):
            def run(self, *, work, prompt, **rest):
                if prompt.startswith("do "):
                    for name in ("a-stuck.bin", "z-later.txt"):
                        (work / name).write_text(f"KEY={os.environ['EVAL_TEST_API_KEY']}")
                return super().run(work=work, prompt=prompt, **rest)

        rewrite = hosts._rewrite

        def stuck(path, data):
            if path.name == "a-stuck.bin":
                raise OSError("simulated failure")
            rewrite(path, data)

        with mock.patch.dict(os.environ, {"EVAL_TEST_API_KEY": SENTINEL}), mock.patch("hosts._rewrite", stuck):
            self.run_all(Writer())
        for cell in (self.root / "runs").glob("*/*/*"):
            self.assertEqual((cell / "work/a-stuck.bin").read_text(), "removed: could not redact\n")
            self.assertEqual((cell / "work/z-later.txt").read_text(), "KEY=[REDACTED]")

    def test_an_interrupted_session_keeps_its_work_redacted_and_stops_the_host(self):
        started, survivor, out = self.root / "started", self.root / "survivor", self.root / "out"
        host = (f'echo "$EVAL_TEST_API_KEY"; echo "$EVAL_TEST_API_KEY" > leak.txt; touch {started}; '
                f'sleep 1; touch {survivor}')
        program = f"""
import sys, types
from pathlib import Path
sys.path.insert(0, {str(Path(compare.__file__).parent)!r})
import compare, hosts
hosts.GRACE_SECONDS = 0.5

class Host:
    def run(self, *, work, out, **rest):
        hosts.execute(["sh", "-c", {host!r}], cwd=work, env=None, out=out, timeout=30)

ev = types.SimpleNamespace(adapter=Host(), host={{}})
compare.run_session(ev, None, "p", Path({str(self.root / "fixtures/repo")!r}), Path({str(out)!r}), "v")
"""
        env = {**os.environ, "EVAL_TEST_API_KEY": SENTINEL}
        runner = subprocess.Popen([sys.executable, "-c", program], env=env, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 10
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        runner.send_signal(signal.SIGINT)
        runner.wait(timeout=10)
        time.sleep(1.5)
        self.assertFalse(survivor.exists())
        self.assertEqual((out / "work/README").read_text(), "fixture")
        self.assertEqual((out / "work/leak.txt").read_text(), "[REDACTED]\n")
        retained = [path for path in out.rglob("*") if path.is_file()]
        for path in retained:
            self.assertNotIn(SENTINEL.encode(), path.read_bytes(), path)


if __name__ == "__main__":
    unittest.main()
