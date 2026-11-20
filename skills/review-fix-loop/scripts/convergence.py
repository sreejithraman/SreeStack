#!/usr/bin/env python3
"""Deterministic convergence controller for review-fix-loop Pass 2+ rounds.

Reads git history from <pass1>..<head> (surviving context compaction with no extra state files)
and classifies the repair loop into CONVERGING, PREMISE_CUT, or DEFER_AND_FINISH.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

BLOAT_MIN_ADDED = 100
BLOAT_RATIO = 0.5
CONSECUTIVE_HIT_LIMIT = 2
TOTAL_HIT_LIMIT = 3


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def numstat(repo: Path, rev_range: str) -> dict[str, tuple[int, int]]:
    stats: dict[str, tuple[int, int]] = {}
    for line in run_git(repo, "diff", "--numstat", rev_range).splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        stats[path] = (int(added) if added.isdigit() else 0, int(deleted) if deleted.isdigit() else 0)
    return stats


def commit_files(repo: Path, rev_range: str) -> list[tuple[str, list[str]]]:
    commits = [sha for sha in run_git(repo, "rev-list", "--reverse", rev_range).splitlines() if sha]
    out: list[tuple[str, list[str]]] = []
    for sha in commits:
        files = [f for f in run_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines() if f]
        out.append((sha, files))
    return out


def is_test_file(path: str) -> bool:
    name = Path(path).name
    return name.startswith("test_") or name.endswith("_test.py") or ".test." in name or ".spec." in name


def trailing_streak(commits: list[tuple[str, list[str]]], path: str) -> int:
    streak = 0
    for _, files in reversed(commits):
        if path in files:
            streak += 1
        else:
            break
    return streak


def analyze(repo: Path, base: str, pass1: str, head: str = "HEAD", premise_cut_at: str | None = None) -> dict:
    base_sha = run_git(repo, "rev-parse", base).strip()
    pass1_sha = run_git(repo, "rev-parse", pass1).strip()
    head_sha = run_git(repo, "rev-parse", head).strip()

    initial = numstat(repo, f"{base_sha}..{pass1_sha}")
    repair_totals = numstat(repo, f"{pass1_sha}..{head_sha}")
    repairs = commit_files(repo, f"{pass1_sha}..{head_sha}")

    pass_num = len(repairs) + 1
    total_added = sum(a for a, _ in repair_totals.values())
    total_deleted = sum(d for _, d in repair_totals.values())

    hit_counts: dict[str, int] = {}
    for _, files in repairs:
        for path in files:
            hit_counts[path] = hit_counts.get(path, 0) + 1

    repeated: list[dict] = []
    bloated: list[dict] = []
    for path, (added, deleted) in sorted(repair_totals.items()):
        if is_test_file(path):
            continue
        streak = trailing_streak(repairs, path)
        hits = hit_counts.get(path, 0)
        init_churn = sum(initial.get(path, (0, 0)))
        if streak >= CONSECUTIVE_HIT_LIMIT or hits >= TOTAL_HIT_LIMIT:
            repeated.append({"file": path, "consecutive": streak, "total_hits": hits})
        if added >= BLOAT_MIN_ADDED and added > BLOAT_RATIO * max(init_churn, 1):
            bloated.append({"file": path, "repair_added": added, "repair_deleted": deleted, "pass1_churn": init_churn})

    post_cut_repeated: list[dict] = []
    post_cut_commits = 0
    if premise_cut_at:
        cut_sha = run_git(repo, "rev-parse", premise_cut_at).strip()
        post_repairs = commit_files(repo, f"{cut_sha}..{head_sha}")
        post_cut_commits = len(post_repairs)
        post_hits: dict[str, int] = {}
        for _, files in post_repairs:
            for path in files:
                if not is_test_file(path):
                    post_hits[path] = post_hits.get(path, 0) + 1
        for path, hits in sorted(post_hits.items()):
            streak = trailing_streak(post_repairs, path)
            if streak >= CONSECUTIVE_HIT_LIMIT or hits >= TOTAL_HIT_LIMIT:
                post_cut_repeated.append({"file": path, "consecutive": streak, "total_hits": hits})

    if not repairs:
        mode = "CONVERGING"
        action = "No repairs since Pass 1; proceed normally."
    elif premise_cut_at:
        if post_cut_commits == 0:
            mode = "CONVERGING"
            action = (
                f"Premise cut landed at {cut_sha[:8]}; run one tightly scoped verification pass on the cut "
                "before deciding next steps."
            )
        elif post_cut_repeated or post_cut_commits >= 4:
            mode = "DEFER_AND_FINISH"
            action = (
                "Loop is still oscillating after premise cut. Stop adding complexity: narrow or fail closed on "
                "remaining edge cases, Defer non-critical/synthetic items with 1-line factual premises, run one "
                "final scoped check, and finish."
            )
        else:
            mode = "CONVERGING"
            action = (
                "Post-cut repair is bounded; run one tightly scoped Pass 2+ verification "
                "(repairs, regressions, cumulative coherence; no fresh red-team fuzzing)."
            )
    elif len(repairs) >= 5 and repeated:
        mode = "DEFER_AND_FINISH"
        action = (
            "Loop is still oscillating. Stop adding complexity: narrow or fail closed on remaining edge cases, "
            "Defer non-critical/synthetic items with 1-line factual premises, run one final scoped check, and finish."
        )
    elif repeated or bloated:
        mode = "PREMISE_CUT"
        targets = sorted({item["file"] for item in repeated + bloated})
        action = (
            f"Additive patching forbidden on {', '.join(targets)}. Run Ponytail or Attack the Premise to delete or "
            "narrow the abstraction generating edge cases, commit the simplification, and pass --premise-cut-at <sha> next."
        )
    else:
        mode = "CONVERGING"
        action = "Run one tightly scoped Pass 2+ verification (repairs, regressions, cumulative coherence; no fresh red-team fuzzing)."

    top_files = sorted(repair_totals.items(), key=lambda kv: kv[1][0] + kv[1][1], reverse=True)[:5]
    return {
        "mode": mode,
        "pass": pass_num,
        "repair_commits": len(repairs),
        "repair_added": total_added,
        "repair_deleted": total_deleted,
        "repeated": repeated,
        "bloated": bloated,
        "post_cut_repeated": post_cut_repeated,
        "top_files": [{"file": p, "added": a, "deleted": d} for p, (a, d) in top_files],
        "action": action,
    }


def format_report(data: dict) -> str:
    lines = [
        f"mode: {data['mode']} (pass {data['pass']}, {data['repair_commits']} repair commit(s))",
        f"repair_churn: +{data['repair_added']} / -{data['repair_deleted']} since Pass 1",
    ]
    if data["repeated"]:
        rep = ", ".join(f"{r['file']} ({r['consecutive']} consecutive, {r['total_hits']} total)" for r in data["repeated"])
        lines.append(f"repeated: {rep}")
    if data["bloated"]:
        bl = ", ".join(f"{b['file']} (+{b['repair_added']} vs {b['pass1_churn']} Pass 1)" for b in data["bloated"])
        lines.append(f"bloated: {bl}")
    if data["top_files"]:
        top = ", ".join(f"{t['file']} (+{t['added']}/-{t['deleted']})" for t in data["top_files"][:3])
        lines.append(f"top_churn: {top}")
    lines.append(f"next: {data['action']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check review-fix-loop convergence from git history.")
    parser.add_argument("--base", required=True, help="Original base commit SHA")
    parser.add_argument("--pass1", required=True, help="Pass 1 snapshot commit SHA")
    parser.add_argument("--head", default="HEAD", help="Current snapshot commit SHA (default: HEAD)")
    parser.add_argument("--premise-cut-at", help="Commit SHA where a PREMISE_CUT simplification landed")
    parser.add_argument("--repo", default=".", help="Repository path (default: .)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)
    try:
        data = analyze(Path(args.repo), args.base, args.pass1, args.head, args.premise_cut_at)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_report(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
