import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import compare

FIXTURES = Path(__file__).parent / "fixtures"
# Real `claude plugin eval --json` results for two versions of one skill. Both pass
# the codeword case; the new one fails one of two runs of the file case.
OLD = json.loads((FIXTURES / "old.json").read_text())
NEW = json.loads((FIXTURES / "new.json").read_text())
# The documented shape of a mock abort: the run records it with error null and score 0.
ABORT = {"server": "fixture", "tool": "lookup", "reason": "expect violation"}


def score(old, new, target, *required):
    return compare.decide(copy.deepcopy(old), copy.deepcopy(new), target, list(required))


class DecideTest(unittest.TestCase):
    def test_the_declared_target_decides(self):
        self.assertEqual(score(OLD, NEW, "score")[1]["decision"], "no win")
        code, report = score(NEW, OLD, "score")
        self.assertEqual((code, report["decision"], report["old"], report["new"]), (0, "win", 0.75, 1))
        code, report = score(OLD, NEW, "turns")
        self.assertEqual((code, report["decision"], report["old"], report["new"]), (1, "no win", 3.5, 3.75))
        self.assertEqual(score(NEW, OLD, "turns")[1]["decision"], "win")

    def test_a_failed_run_of_a_required_case_rejects_a_better_candidate(self):
        weaker = copy.deepcopy(NEW)
        weaker["aggregates"]["overallScore"] = 0.5
        self.assertEqual(score(weaker, NEW, "score")[1]["decision"], "win")
        code, report = score(weaker, NEW, "score", "file")
        self.assertEqual((code, report["decision"]), (1, "rejected"))
        self.assertEqual(score(weaker, NEW, "score", "codeword")[1]["decision"], "win")

    def test_one_failed_run_rejects_a_required_case_that_passes_on_average(self):
        candidate = copy.deepcopy(NEW)
        baseline = copy.deepcopy(NEW)
        for result in (candidate, baseline):
            result["suite"]["threshold"] = 0.5
        baseline["aggregates"]["overallScore"] = 0.5
        file_case = next(case for case in candidate["cases"] if case["name"] == "file")
        self.assertEqual([run["score"] for run in file_case["arms"]["with"]], [0, 1])
        self.assertGreaterEqual(file_case["aggregates"]["score"], candidate["suite"]["threshold"])
        self.assertEqual(score(baseline, candidate, "score")[1]["decision"], "win")
        code, report = score(baseline, candidate, "score", "file")
        self.assertEqual((code, report["decision"]), (1, "rejected"))

    def test_an_aborted_run_outside_the_required_cases_cannot_win_on_cost(self):
        candidate = copy.deepcopy(OLD)
        run = candidate["cases"][1]["arms"]["with"][0]
        run.update(aborted=ABORT, costUsd=0.0001, score=0, passed=False)
        code, report = score(OLD, candidate, "cost_usd", "codeword")
        self.assertEqual((code, report["decision"]), (2, "invalid"), report)

    def test_equal_results_are_no_win_and_never_equivalence(self):
        code, report = score(OLD, OLD, "pass_rate")
        self.assertEqual((code, report["decision"]), (1, "no win"))
        self.assertIn("no difference is not equivalence", " ".join(report["notes"]))

    def test_missing_cost_is_unproven_not_zero(self):
        cheaper = copy.deepcopy(OLD)
        for case in cheaper["cases"]:
            for run in case["arms"]["with"]:
                run["costUsd"] /= 10
        self.assertEqual(score(OLD, cheaper, "cost_usd")[1]["decision"], "win")
        del cheaper["cases"][0]["arms"]["with"][0]["costUsd"]
        code, report = score(OLD, cheaper, "cost_usd")
        self.assertEqual((code, report["decision"]), (1, "unproven"))

    def test_an_incomplete_result_set_is_invalid(self):
        def broken(change):
            result = copy.deepcopy(NEW)
            change(result)
            return result

        cases = {
            "partial": lambda r: r.update(partial=True, partialReason="max cost"),
            "missing run": lambda r: r["cases"][1]["arms"]["with"].pop(),
            "missing baseline run": lambda r: r["cases"][0]["arms"]["without"].pop(),
            "errored run": lambda r: r["cases"][0]["arms"]["with"][0].update(error="timeout"),
            "aborted baseline run": lambda r: r["cases"][0]["arms"]["without"][0].update(aborted=ABORT),
            "other max turns": lambda r: r["cases"][0].update(maxTurns=100),
            "other timeout": lambda r: r["cases"][0].update(timeoutSeconds=3600),
            "skipped graders": lambda r: r["cases"][0]["arms"]["with"][0].update(skippedPaidGraders=True),
            "missing case": lambda r: r["cases"].pop(),
            "changed grader": lambda r: r["cases"][0]["graders"][0]["config"].update(pattern="X"),
            "other model": lambda r: r["suite"].update(modelOverride="sonnet"),
            "no plugin": lambda r: r["suite"].update(plugins=[]),
            "unknown schema": lambda r: r.update(schemaVersion=2),
        }
        for name, change in cases.items():
            with self.subTest(name):
                code, report = score(OLD, broken(change), "score")
                self.assertEqual((code, report["decision"]), (2, "invalid"), report)
        self.assertEqual(score(OLD, NEW, "score", "absent")[1]["decision"], "invalid")

    def test_report_includes_compact_per_case_summary_and_baseline(self):
        new_diff = copy.deepcopy(NEW)
        new_diff["cases"][1]["aggregates"]["scoreWithout"] = 0.25
        new_diff["cases"][1]["aggregates"]["passRateWithout"] = 0.5
        code, report = score(OLD, new_diff, "score", "file")
        self.assertEqual((code, report["decision"]), (1, "rejected"))
        by_name = {case["name"]: case for case in report["cases"]}
        self.assertEqual(set(by_name), {"codeword", "file"})
        self.assertFalse(by_name["codeword"]["required"])
        self.assertTrue(by_name["file"]["required"])
        self.assertEqual(by_name["file"]["old"]["score"], 1)
        self.assertEqual(by_name["file"]["old"]["pass_rate"], 1)
        self.assertEqual(by_name["file"]["old"]["passed"], 2)
        self.assertEqual(by_name["file"]["old"]["turns"], 4.0)
        self.assertAlmostEqual(by_name["file"]["old"]["cost_usd"], (0.0019222 + 0.00188562) / 2)
        self.assertEqual(by_name["file"]["new"]["score"], 0.5)
        self.assertEqual(by_name["file"]["new"]["pass_rate"], 0.5)
        self.assertEqual(by_name["file"]["new"]["passed"], 1)
        self.assertEqual(by_name["file"]["new"]["runs"], 2)
        self.assertEqual(by_name["file"]["new"]["turns"], 4.0)
        self.assertAlmostEqual(by_name["file"]["new"]["cost_usd"], (0.00196633 + 0.00216384) / 2)
        self.assertEqual(
            by_name["file"]["without"],
            {"old_score": 0.5, "new_score": 0.25, "old_pass_rate": 0, "new_pass_rate": 0.5},
        )

    def test_without_baseline_is_omitted_when_without_runs_are_absent(self):
        for ablation in ("none", None):
            with self.subTest(ablation=ablation):
                old_with = copy.deepcopy(OLD)
                new_with = copy.deepcopy(NEW)
                for result in (old_with, new_with):
                    if ablation is None:
                        result["suite"].pop("ablation", None)
                    else:
                        result["suite"]["ablation"] = ablation
                    for case in result["cases"]:
                        case["arms"].pop("without", None)
                _, report = score(old_with, new_with, "score")
                for case in report["cases"]:
                    self.assertNotIn("without", case)

    def test_mixed_arm_cases_report_without_only_where_present(self):
        old_mixed = copy.deepcopy(OLD)
        new_mixed = copy.deepcopy(NEW)
        for result in (old_mixed, new_mixed):
            result["suite"].pop("ablation", None)
            result["cases"][0]["arms"].pop("without", None)
            result["cases"][0]["aggregates"].pop("scoreWithout", None)
            result["cases"][0]["aggregates"].pop("passRateWithout", None)
        code, report = score(old_mixed, new_mixed, "score", "file")
        self.assertEqual((code, report["decision"]), (1, "rejected"))
        by_name = {case["name"]: case for case in report["cases"]}
        self.assertNotIn("without", by_name["codeword"])
        self.assertEqual(by_name["file"]["without"]["old_score"], 0.5)
        new_mixed["cases"][1]["arms"].pop("without", None)
        self.assertEqual(score(old_mixed, new_mixed, "score")[1]["decision"], "invalid")

    def test_duplicate_case_names_are_invalid(self):
        old_dup = copy.deepcopy(OLD)
        new_dup = copy.deepcopy(NEW)
        for result in (old_dup, new_dup):
            for case in result["cases"]:
                case["name"] = "dup"
        old_dup["cases"][0]["promptMarkdown"] = "Different prompt"
        code, report = score(old_dup, new_dup, "turns")
        self.assertEqual((code, report["decision"]), (2, "invalid"))
        self.assertTrue(any("duplicate case name" in reason for reason in report["reasons"]))

    def test_missing_or_malformed_case_aggregates_preserve_decision(self):
        for label, mutate in (
            ("missing", lambda c: c.pop("aggregates")),
            ("null", lambda c: c.__setitem__("aggregates", None)),
            ("list", lambda c: c.__setitem__("aggregates", [])),
        ):
            with self.subTest(label):
                candidate = copy.deepcopy(NEW)
                mutate(candidate["cases"][1])
                code, report = score(OLD, candidate, "score", "file")
                self.assertEqual((code, report["decision"]), (1, "rejected"))
                file_case = next(c for c in report["cases"] if c["name"] == "file")
                self.assertIsNone(file_case["new"]["score"])
                self.assertIsNone(file_case["new"]["pass_rate"])
                self.assertEqual((file_case["new"]["passed"], file_case["new"]["runs"]), (1, 2))
                self.assertIsNone(file_case["without"]["new_score"])
                self.assertEqual(file_case["without"]["old_score"], 0.5)


class RunTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.root)
        for version in ("old", "new"):
            (self.root / version / "greeter").mkdir(parents=True)
            (self.root / version / "greeter" / "SKILL.md").write_text(f"---\nname: greeter\n---\n{version}\n")
        (self.root / "evals" / "codeword").mkdir(parents=True)
        (self.root / "evals" / "codeword" / "prompt.md").write_text("What is the codeword?\n")
        (self.root / "evals" / "results").mkdir()
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        # A stand-in CLI: records its arguments and the plugin it got, then writes a fixture result.
        (bin_dir / "claude").write_text(f"""#!/usr/bin/env python3
import json, pathlib, shutil, sys
args = sys.argv[1:]
plugin = pathlib.Path(args[2])
log = pathlib.Path({str(self.root / "calls.jsonl")!r})
with log.open("a") as f:
    f.write(json.dumps({{"args": args,
        "manifest": json.loads((plugin / ".claude-plugin/plugin.json").read_text()),
        "files": sorted(str(p.relative_to(plugin)) for p in plugin.rglob("*") if p.is_file())}}) + "\\n")
fixture = {str(FIXTURES)!r} + ("/old.json" if "old" in str(plugin) else "/new.json")
shutil.copy(fixture, args[args.index("--json") + 1])
print("Wrote result")
""")
        (bin_dir / "claude").chmod(0o755)
        self.enterContext(mock.patch.dict(os.environ, {"PATH": f"{bin_dir}:{os.environ['PATH']}"}))

    def compare(self, *extra, tree=""):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = compare.main(["run", str(self.root / "old" / tree), str(self.root / "new" / tree),
                                 "--evals", str(self.root / "evals"), "--out", str(self.root / "out"), *extra])
        return code, json.loads(out.getvalue())

    def calls(self):
        return [json.loads(line) for line in (self.root / "calls.jsonl").read_text().splitlines()]

    def test_each_tree_runs_as_the_same_plugin_without_publishing(self):
        code, report = self.compare("--target", "score", "--", "--model", "haiku")
        self.assertEqual((code, report["decision"]), (1, "no win"))
        calls = self.calls()
        self.assertEqual(len(calls), 2)
        for call in calls:
            self.assertEqual(call["args"][:2], ["plugin", "eval"])
            self.assertIn("--no-publish", call["args"])
            self.assertEqual(call["args"][-2:], ["--model", "haiku"])
            self.assertEqual(call["manifest"]["name"], compare.PLUGIN_NAME)
            self.assertEqual(call["files"], [".claude-plugin/plugin.json", "evals/codeword/prompt.md",
                                             "skills/greeter/SKILL.md"])
        old_skill = self.root / "out" / "old" / "plugin" / "skills" / "greeter" / "SKILL.md"
        self.assertIn("old", old_skill.read_text())

    def test_stdout_holds_only_the_decision(self):
        result = subprocess.run([sys.executable, compare.__file__, "run", str(self.root / "old"),
                                 str(self.root / "new"), "--evals", str(self.root / "evals"),
                                 "--out", str(self.root / "out"), "--target", "score"],
                                capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["decision"], "no win", result.stderr)
        self.assertIn("Wrote result", result.stderr)

    def test_one_skill_folder_becomes_the_plugin_skill(self):
        self.compare("--target", "score", tree="greeter")
        self.assertEqual(self.calls()[1]["files"], [".claude-plugin/plugin.json", "evals/codeword/prompt.md",
                                                    "skills/greeter/SKILL.md"])
        self.assertTrue((self.root / "out" / "new" / "plugin" / "skills" / "greeter" / "SKILL.md").is_file())

    def test_publishing_and_output_flags_stay_with_the_runner(self):
        for flag in ("--publish-report", "--json=x.json", "--output-dir"):
            with self.subTest(flag), self.assertRaises(SystemExit):
                self.compare("--target", "score", "--", flag)
        self.assertFalse((self.root / "calls.jsonl").exists())

    def test_a_partial_baseline_stops_before_the_candidate_runs(self):
        with mock.patch.object(compare, "evaluate", return_value={**OLD, "partial": True}) as evaluate:
            code, report = self.compare("--target", "score")
        self.assertEqual((code, report["decision"], evaluate.call_count), (2, "invalid", 1))


if __name__ == "__main__":
    unittest.main()
