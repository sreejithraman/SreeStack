"""Compare two versions of a skill tree with `claude plugin eval`, then decide.

Usage:
  compare.py run OLD NEW --evals DIR --out DIR --target T [--required CASE ...] [-- EVAL OPTIONS]
  compare.py score OLD.json NEW.json --target T [--required CASE ...]

`run` wraps each skill tree (a folder of skill folders, or one skill folder) in an
identical plugin named skill-under-test with a copy of the same eval cases, runs
`claude plugin eval` on the old one and then the new one, and scores the pair.
Options after `--` pass through to `claude plugin eval`, for example
`-- --model haiku --runs 3 --max-cost-usd 2 --allow-tools Write`. The runner always
adds --no-publish and owns --json and --output-dir. `score` decides from two
existing `--json` result files.

Targets: score (overallScore), pass_rate (overallPassRate), cost_usd (mean agent
cost per plugin run, judge cost excluded) and turns (mean turns per plugin run).

Prints a JSON decision. Exit 0: the candidate beat the baseline on the target. Exit
1: no win, which includes equal results, a failed run of a required case, and a
target without telemetry. Exit 2: invalid evidence, such as a partial run, a missing
or failed run, skipped paid graders, or results that differ in cases, checks,
model, Claude version or ablation. No result is a significance test, and no result
shows equivalence.

Limits: `claude plugin eval` is experimental and runs only on Claude Code. It
reports no token counts and sandboxes shell tools, but not hooks or MCP servers.
The whole old suite runs before the new one, so order is not alternated.
"""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

PLUGIN_NAME = "skill-under-test"
OWNED_FLAGS = ("--json", "--output-dir", "--publish-report", "--no-publish")
TARGETS = {"score": "higher", "pass_rate": "higher", "cost_usd": "lower", "turns": "lower"}
NOTES = [
    "plugin eval reports no token counts",
    "observed results only: no significance test, and no difference is not equivalence",
]


def plugin_runs(result: dict) -> list[dict]:
    return [run for case in result["cases"] for run in case["arms"].get("with", [])]


def mean_of(result: dict, field: str) -> float | None:
    values = [run.get(field) for run in plugin_runs(result)]
    if not values or any(not isinstance(value, (int, float)) for value in values):
        return None
    return sum(values) / len(values)


def metric(result: dict, target: str) -> float | None:
    if target == "score":
        return result["aggregates"].get("overallScore")
    if target == "pass_rate":
        return result["aggregates"].get("overallPassRate")
    if target == "cost_usd":
        return mean_of(result, "costUsd")
    return mean_of(result, "turns")


def case_shape(case: dict) -> tuple:
    return case.get("promptMarkdown"), case.get("runsPerCase"), json.dumps(case.get("graders"), sort_keys=True)


def problems(old: dict, new: dict, required: list[str]) -> list[str]:
    found = []
    for label, result in (("old", old), ("new", new)):
        if result.get("schemaVersion") != 1:
            found.append(f"{label}: unsupported schemaVersion {result.get('schemaVersion')!r}")
            continue
        if result.get("partial"):
            found.append(f"{label}: partial run ({result.get('partialReason') or 'no reason given'})")
        if not result["suite"].get("plugins"):
            found.append(f"{label}: no plugin loaded")
        arms = ["with", "without"] if result["suite"].get("ablation") == "with-without" else ["with"]
        for case in result["cases"]:
            for arm in arms:
                runs = case["arms"].get(arm, [])
                if len(runs) != case["runsPerCase"]:
                    found.append(f"{label}: {case['name']} has {len(runs)} of {case['runsPerCase']} {arm} runs")
                for run in runs:
                    if run.get("error"):
                        found.append(f"{label}: {case['name']} {arm} run failed: {run['error']}")
                    if run.get("skippedPaidGraders"):
                        found.append(f"{label}: {case['name']} {arm} run skipped paid graders")
    if found:
        return found
    if old.get("claudeVersion") != new.get("claudeVersion"):
        found.append(f"claudeVersion differs: {old.get('claudeVersion')!r} vs {new.get('claudeVersion')!r}")
    for field in ("modelOverride", "ablation", "threshold"):
        if old["suite"].get(field) != new["suite"].get(field):
            found.append(f"suite.{field} differs: {old['suite'].get(field)!r} vs {new['suite'].get(field)!r}")
    old_cases = {case["name"]: case_shape(case) for case in old["cases"]}
    new_cases = {case["name"]: case_shape(case) for case in new["cases"]}
    if old_cases.keys() != new_cases.keys():
        found.append(f"case sets differ: {sorted(old_cases)} vs {sorted(new_cases)}")
    found += [f"{name}: prompt, runs or graders differ" for name in sorted(old_cases.keys() & new_cases.keys())
              if old_cases[name] != new_cases[name]]
    found += [f"required case {name!r} is not in the results" for name in required if name not in new_cases]
    return found


def decide(old: dict, new: dict, target: str, required: list[str]) -> tuple[int, dict]:
    report = {"target": target, "notes": NOTES}
    if found := problems(old, new, required):
        return 2, {**report, "decision": "invalid", "reasons": found}
    report["old"], report["new"] = metric(old, target), metric(new, target)
    report["suite_cost_usd"] = {"old": old.get("costUsd"), "new": new.get("costUsd")}
    failed = [case["name"] for case in new["cases"] if case["name"] in required
              and not all(run.get("passed") for run in case["arms"]["with"])]
    if failed:
        return 1, {**report, "decision": "rejected", "reasons": [f"required case failed: {name}" for name in failed]}
    if report["old"] is None or report["new"] is None:
        return 1, {**report, "decision": "unproven", "reasons": [f"{target} telemetry is missing"]}
    better = report["new"] > report["old"] if TARGETS[target] == "higher" else report["new"] < report["old"]
    if not better:
        return 1, {**report, "decision": "no win", "reasons": [f"{target} is not better"]}
    return 0, {**report, "decision": "win", "reasons": [f"{target} is better"]}


def wrap(skills: Path, evals: Path, plugin: Path) -> None:
    for folder in (skills, evals):
        if not folder.is_dir():
            raise SystemExit(f"not a directory: {folder}")
    target = plugin / "skills" / skills.resolve().name if (skills / "SKILL.md").is_file() else plugin / "skills"
    shutil.copytree(skills, target, symlinks=True)
    shutil.copytree(evals, plugin / "evals", symlinks=True, ignore=shutil.ignore_patterns("results"))
    (plugin / ".claude-plugin").mkdir()
    manifest = {"name": PLUGIN_NAME, "version": "0.0.0", "description": "Skill tree under comparison"}
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")


def evaluate(plugin: Path, result: Path, eval_args: list[str]) -> dict | None:
    command = ["claude", "plugin", "eval", str(plugin), "--no-publish", "--trust-plugin",
               "--json", str(result), "--output-dir", str(plugin.parent / "results"), *eval_args]
    code = subprocess.run(command).returncode
    if code not in (0, 1) or not result.is_file():
        print(f"claude plugin eval exited {code} for {plugin.parent.name}", file=sys.stderr)
    return json.loads(result.read_text()) if result.is_file() else None


def run(args: argparse.Namespace, eval_args: list[str]) -> tuple[int, dict]:
    if owned := [arg for arg in eval_args if arg.split("=")[0] in OWNED_FLAGS]:
        raise SystemExit(f"the runner owns {', '.join(owned)}")
    args.out.mkdir(parents=True, exist_ok=False)
    results = {}
    for label, skills in (("old", args.old), ("new", args.new)):
        plugin = args.out / label / "plugin"
        wrap(skills, args.evals, plugin)
        results[label] = evaluate(plugin, args.out / label / "result.json", eval_args)
        if results[label] is None or results[label].get("partial"):
            return 2, {"target": args.target, "decision": "invalid",
                       "reasons": [f"{label}: no complete result, so later runs were skipped"]}
    return decide(results["old"], results["new"], args.target, args.required)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    own, eval_args = (argv[:argv.index("--")], argv[argv.index("--") + 1:]) if "--" in argv else (argv, [])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                     allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", allow_abbrev=False)
    run_parser.add_argument("--evals", type=Path, required=True)
    run_parser.add_argument("--out", type=Path, required=True)
    score_parser = commands.add_parser("score", allow_abbrev=False)
    for sub in (run_parser, score_parser):
        sub.add_argument("old", type=Path)
        sub.add_argument("new", type=Path)
        sub.add_argument("--target", choices=TARGETS, required=True)
        sub.add_argument("--required", nargs="+", default=[], metavar="CASE")
    args = parser.parse_args(own)
    if args.command == "score":
        if eval_args:
            parser.error("score takes no eval options")
        code, report = decide(json.loads(args.old.read_text()), json.loads(args.new.read_text()),
                              args.target, args.required)
    else:
        code, report = run(args, eval_args)
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
