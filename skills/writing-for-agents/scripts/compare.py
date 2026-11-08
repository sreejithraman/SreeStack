"""Run a controlled comparison of skill trees on a coding-agent host, then score it.

Usage:
  compare.py plan <eval-dir>                 print the planned matrix and its cost in sessions
  compare.py calibrate <eval-dir>            prove isolation and normal collection loading
  compare.py run <eval-dir> [--tasks a,b] [--replace-stale]
  compare.py blind <eval-dir>                write anonymized outputs for a judge
  compare.py score <eval-dir>                exit 0 win, 1 no win, 2 invalid evidence

<eval-dir>/manifest.json (version 1):
  {
    "version": 1,
    "host": {"adapter": "claude" | "codex", "model": "...", "effort": "low",
             "timeout_seconds": 600, "permission_mode": "acceptEdits", "max_budget_usd": 1},
    "variants": {"old": "variants/old", "new": "variants/new", "none": null},
    "baseline": "old", "candidate": "new", "repeats": 3,
    "target": {"metric": "pass_rate" | "task_pass" | "cost_usd" | "turns" | "tool_calls"
                         | "wall_seconds" | "tokens.<field>",
               "task": "<id, for task_pass>", "why": "the improvement this run must show"},
    "tasks": [{"id": "...", "prompt": "...", "fixture": "fixtures/x", "required": true,
               "checks": ["sh command run in the work dir; exit 0 passes"],
               "judge": "criteria for a blind judge, or omit"}]
  }

A variant path is a directory of skill folders, or null for no skills. Paths are
relative to <eval-dir>. Checks get EVAL_WORK and EVAL_OUT. Every input is hashed,
and a result counts only while its hashes match. Work dirs move into the evidence
folder after the checks; nothing here deletes a fixture or a result.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

import hosts

HARNESS = [Path(__file__).resolve(), Path(hosts.__file__).resolve()]
LOWER_IS_BETTER = {"cost_usd", "turns", "tool_calls", "wall_seconds"}


class InvalidEvidence(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_hash(path: Path | None) -> str | None:
    if path is None:
        return None
    if not path.exists():
        raise InvalidEvidence(f"missing input: {path}")
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        relative = item.relative_to(path).as_posix()
        if item.is_symlink():
            digest.update(f"L {relative} {os.readlink(item)}\n".encode())
        elif item.is_file():
            digest.update(f"F {relative} {os.access(item, os.X_OK)} {sha256(item.read_bytes())}\n".encode())
    return digest.hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class Eval:
    def __init__(self, directory: Path, adapter=None):
        self.dir = directory.resolve()
        self.manifest = json.loads((self.dir / "manifest.json").read_text())
        if self.manifest.get("version") != 1:
            raise InvalidEvidence("manifest.json needs \"version\": 1")
        self.host = self.manifest["host"]
        self.adapter = adapter or hosts.ADAPTERS[self.host["adapter"]]()
        self.variants = {name: (self.dir / path if path else None)
                         for name, path in self.manifest["variants"].items()}
        for role in ("baseline", "candidate"):
            if self.manifest[role] not in self.variants:
                raise InvalidEvidence(f"{role} {self.manifest[role]!r} is not a variant")
        self.tasks = {task["id"]: task for task in self.manifest["tasks"]}
        self.repeats = int(self.manifest.get("repeats", 3))
        self.target = self.manifest["target"]
        self._hashes = None

    def hashes(self) -> dict:
        if self._hashes is None:
            self._hashes = {
                "harness": sha256(b"".join(path.read_bytes() for path in HARNESS)),
                "host_version": self.adapter.version(),
                "settings": sha256(canonical(self.host).encode()),
                "variants": {name: tree_hash(path) for name, path in self.variants.items()},
                "fixtures": {task_id: tree_hash(self.fixture(task))
                             for task_id, task in self.tasks.items()},
            }
        return self._hashes

    def fixture(self, task) -> Path | None:
        return self.dir / task["fixture"] if task.get("fixture") else None

    def input_hash(self, task_id: str, variant: str) -> str:
        hashes = self.hashes()
        return sha256(canonical({
            "task": self.tasks[task_id], "fixture": hashes["fixtures"][task_id], "variant": hashes["variants"][variant],
            "settings": self.host, "host_version": hashes["host_version"], "harness": hashes["harness"],
        }).encode())

    def plan(self, only=None) -> list:
        """Every planned cell, with the variant order rotated per task and repeat."""
        names = list(self.variants)
        cells = []
        for repeat in range(self.repeats):
            for index, task_id in enumerate(self.tasks):
                if only and task_id not in only:
                    continue
                shift = (repeat + index) % len(names)
                for variant in names[shift:] + names[:shift]:
                    cells.append((task_id, variant, repeat))
        return cells

    def cell_dir(self, task_id, variant, repeat) -> Path:
        return self.dir / "runs" / task_id / variant / str(repeat)

    def calibration_key(self) -> str:
        hashes = self.hashes()
        return sha256(canonical({key: hashes[key] for key in ("harness", "host_version", "settings", "variants")}).encode())[:16]


def run_session(ev: Eval, skills: Path | None, prompt: str, fixture: Path | None, out: Path, variant: str):
    """One fresh session in its own work dir. The work dir ends inside `out`."""
    out.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="compare-"))
    work = scratch / "work"
    if fixture:
        shutil.copytree(fixture, work, symlinks=True)
    else:
        work.mkdir()
    started = time.monotonic()
    try:
        result = ev.adapter.run(skills=skills, prompt=prompt, work=work, out=out,
                                settings=ev.host, scratch=scratch, variant=variant)
    except Exception as error:  # A crashed adapter is a failed cell, kept with its reason.
        result = hosts.RunResult(status="error", error=f"{type(error).__name__}: {error}")
    result.wall_seconds = round(time.monotonic() - started, 3)
    return result, work, scratch


def keep_work(work: Path, scratch: Path, out: Path) -> None:
    if work.exists():
        shutil.move(str(work), str(out / "work"))
    shutil.rmtree(scratch, ignore_errors=True)


def run_checks(task, work: Path, out: Path) -> list:
    results = []
    env = {**os.environ, "EVAL_WORK": str(work), "EVAL_OUT": str(out)}
    for index, command in enumerate(task.get("checks", [])):
        done = subprocess.run(["sh", "-c", command], cwd=work, env=env, capture_output=True, text=True)
        (out / f"check-{index}.log").write_text(done.stdout + done.stderr)
        results.append({"command": command, "exit": done.returncode})
    return results


def listed_names(answer: str) -> set:
    return set(re.findall(r"[\w:.-]+", answer))


def calibrate(ev: Eval) -> bool:
    """Probe isolation with a disposable canary, then load each variant's collection normally."""
    key = ev.calibration_key()
    base = ev.dir / "calibration" / key
    if base.exists():
        base = base.with_name(f"{key}-{int(time.time())}")
    canary_name = f"calib-canary-{random.randrange(16**6):06x}"
    code = f"CANARY-{random.randrange(16**8):08x}"
    canary_tree = base / "canary-tree"
    (canary_tree / canary_name).mkdir(parents=True)
    (canary_tree / canary_name / "SKILL.md").write_text(
        f"---\nname: {canary_name}\ndescription: Use when asked for the {canary_name} code.\n---\n\nThe code is {code}.\n")
    empty_tree = base / "empty-tree"
    empty_tree.mkdir()
    installed = ev.adapter.installed_skill_names()
    listing = "Then, on a new line, list the name of every skill available to you, comma separated."

    def with_canary(r):
        return [(code in r.answer, f"answer quotes {code}, which only the canary copy holds"),
                (r.read_skill(canary_name), f"calls show {canary_name}/SKILL.md loaded")]

    def without_canary(r):
        leaked = sorted(installed & listed_names(r.answer))
        return [("NO-SKILL" in r.answer and code not in r.answer, "without the copy the agent has no canary"),
                (not leaked, f"no installed skill leaks in (leaked: {', '.join(leaked) or 'none'})")]

    def shell(r):
        return [("calib-42" in r.answer, "the agent runs a shell command"),
                (any("echo calib-" in (c.get("command") or "") for c in r.calls or []), "calls record the command")]

    def collection(expected):
        def check(r):
            missing = sorted(set(expected) - listed_names(r.answer))
            return [(not missing, f"every model-invoked skill in the tree is listed (missing: {', '.join(missing) or 'none'})")]
        return check

    probes = [
        ("skill", canary_tree, f"Use the {canary_name} skill and reply with the code it gives.", with_canary),
        ("none", empty_tree, f"If you have a skill named {canary_name}, reply with the code it gives; "
                             f"otherwise reply NO-SKILL. {listing}", without_canary),
        ("shell", empty_tree, "Run this shell command and reply with only its output: echo calib-$((6*7))", shell),
    ]
    probes += [(f"collection-{variant}", tree, "List the name of every skill available to you, comma separated.",
                collection(hosts.model_invocable(tree))) for variant, tree in ev.variants.items() if tree]
    passed = True
    report = []
    for probe_id, tree, prompt, checks in probes:
        result, work, scratch = run_session(ev, tree, prompt, None, base / probe_id, f"calibrate-{probe_id}")
        keep_work(work, scratch, base / probe_id)
        result.save(base / probe_id)
        outcomes = [(False, f"session {result.status}: {result.error}")] if result.status != "ok" else checks(result)
        for ok, what in outcomes:
            passed &= bool(ok)
            report.append({"probe": probe_id, "pass": bool(ok), "check": what})
            print(f"{'PASS' if ok else 'FAIL'} {probe_id}: {what}")
    (base / "calibration.json").write_text(json.dumps(
        {"key": key, "pass": passed, "hashes": ev.hashes(), "probes": report}, indent=2))
    if passed:
        (ev.dir / "calibration" / f"{key}.pass").write_text(str(base))
    print(f"calibration {'passed' if passed else 'failed'}; evidence in {base}")
    return passed


def run(ev: Eval, only=None, replace_stale=False) -> None:
    cells = ev.plan(only)
    todo, stale = [], []
    for cell in cells:
        stored = ev.cell_dir(*cell) / "result.json"
        if not stored.exists():
            todo.append(cell)
        elif json.loads(stored.read_text())["input_hash"] != ev.input_hash(cell[0], cell[1]):
            stale.append(cell)
    if stale and not replace_stale:
        raise InvalidEvidence("results with changed inputs: " + ", ".join("/".join(map(str, c)) for c in stale)
                              + ". Rerun with --replace-stale to keep them under superseded/ and run again.")
    print(f"{len(todo) + len(stale)} sessions to run; {len(cells) - len(todo) - len(stale)} reused with matching hashes")
    if not todo and not stale:
        return
    if not (ev.dir / "calibration" / f"{ev.calibration_key()}.pass").exists() and not calibrate(ev):
        raise InvalidEvidence("calibration failed; fix the adapter or host settings first")
    stamp = time.strftime("%Y%m%dT%H%M%S")
    for cell in stale:
        kept = ev.dir / "superseded" / stamp / Path(*map(str, cell))
        kept.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ev.cell_dir(*cell)), str(kept))
    for task_id, variant, repeat in [c for c in cells if c in todo or c in stale]:
        task = ev.tasks[task_id]
        out = ev.cell_dir(task_id, variant, repeat)
        result, work, scratch = run_session(ev, ev.variants[variant], task["prompt"], ev.fixture(task), out, variant)
        result.checks = run_checks(task, work, out) if result.status == "ok" else []
        keep_work(work, scratch, out)
        result.save(out, extra={
            "task": task_id, "variant": variant, "repeat": repeat, "input_hash": ev.input_hash(task_id, variant),
            "inputs": {"model": ev.host.get("model"), "effort": ev.host.get("effort"), **ev.hashes(),
                       "variant_hash": ev.hashes()["variants"][variant]},
        })
        print(task_id, variant, repeat, result.status, f"{result.wall_seconds:.0f}s")


def blind(ev: Eval) -> Path:
    judging = ev.dir / "judging"
    items, key = [], {}
    for task_id, variant, repeat in ev.plan():
        task = ev.tasks[task_id]
        if not task.get("judge"):
            continue
        stored = load_cell(ev, task_id, variant, repeat)
        blind_id = f"item-{random.randrange(16**8):08x}"
        items.append({"id": blind_id, "task": task["prompt"], "criteria": task["judge"], "answer": stored["answer"]})
        key[blind_id] = {"task": task_id, "variant": variant, "repeat": repeat, "input_hash": stored["input_hash"]}
    random.shuffle(items)
    judging.mkdir(exist_ok=True)
    (judging / "packet.json").write_text(json.dumps(items, indent=2))
    (judging / "key.json").write_text(json.dumps(key, indent=2))
    print(f"Give a fresh judge only {judging / 'packet.json'}. It writes {judging / 'verdicts.json'} "
          'as {"<id>": {"pass": true, "reason": "..."}}. Keep key.json from the judge.')
    return judging


def load_cell(ev: Eval, task_id, variant, repeat) -> dict:
    stored = ev.cell_dir(task_id, variant, repeat) / "result.json"
    if not stored.exists():
        raise InvalidEvidence(f"missing cell {task_id}/{variant}/{repeat}")
    data = json.loads(stored.read_text())
    if data["input_hash"] != ev.input_hash(task_id, variant):
        raise InvalidEvidence(f"stale cell {task_id}/{variant}/{repeat}: its inputs changed")
    return data


def judge_verdicts(ev: Eval) -> dict:
    judging = ev.dir / "judging"
    if not (judging / "key.json").exists():
        return {}
    key = json.loads((judging / "key.json").read_text())
    verdicts = json.loads((judging / "verdicts.json").read_text()) if (judging / "verdicts.json").exists() else {}
    mapped = {}
    for blind_id, cell in key.items():
        if blind_id in verdicts and cell["input_hash"] == ev.input_hash(cell["task"], cell["variant"]):
            mapped[(cell["task"], cell["variant"], cell["repeat"])] = bool(verdicts[blind_id]["pass"])
    return mapped


def metric(cell: dict, name: str):
    if name == "tool_calls":
        return len(cell["calls"]) if cell.get("calls") is not None else None
    if name.startswith("tokens."):
        return (cell.get("tokens") or {}).get(name.split(".", 1)[1])
    return cell.get(name)


def mean(values):
    return sum(values) / len(values)


def score(ev: Eval) -> dict:
    """Verify the whole matrix, then judge the declared target. Never claims equivalence or significance."""
    problems, cells = [], {}
    for task_id, variant, repeat in ev.plan():
        try:
            cells[(task_id, variant, repeat)] = load_cell(ev, task_id, variant, repeat)
        except InvalidEvidence as error:
            problems.append(str(error))
    verdicts = judge_verdicts(ev)
    for (task_id, variant, repeat), cell in cells.items():
        judged = ev.tasks[task_id].get("judge")
        if judged and (task_id, variant, repeat) not in verdicts:
            problems.append(f"no current judge verdict for {task_id}/{variant}/{repeat}")
        cell["pass"] = (cell["status"] == "ok" and all(c["exit"] == 0 for c in cell["checks"])
                        and (not judged or verdicts.get((task_id, variant, repeat), False)))
    if not (ev.dir / "calibration" / f"{ev.calibration_key()}.pass").exists():
        problems.append("no passing calibration for these hashes")
    if problems:
        raise InvalidEvidence("; ".join(problems))

    baseline, candidate = ev.manifest["baseline"], ev.manifest["candidate"]
    by_variant = {name: [c for (t, v, r), c in cells.items() if v == name] for name in ev.variants}
    table = {task_id: {name: f"{sum(c['pass'] for (t, v, r), c in cells.items() if t == task_id and v == name)}/{ev.repeats}"
                       for name in ev.variants} for task_id in ev.tasks}
    vetoes = sorted({f"{t}/{r}" for (t, v, r), c in cells.items()
                     if v == candidate and ev.tasks[t].get("required") and not c["pass"]})
    metrics = ["pass_rate", "cost_usd", "turns", "tool_calls", "wall_seconds",
               *sorted({f"tokens.{k}" for c in cells.values() for k in (c.get("tokens") or {})})]
    summary, unavailable = {}, {}
    for name in ev.variants:
        rows = by_variant[name]
        summary[name] = {"pass_rate": sum(c["pass"] for c in rows) / len(rows)}
        for m in metrics[1:]:
            values = [metric(c, m) for c in rows]
            known = [v for v in values if v is not None]
            summary[name][m] = mean(known) if len(known) == len(values) else None
            if len(known) < len(values):
                unavailable.setdefault(m, {})[name] = f"{len(values) - len(known)}/{len(values)} runs"

    target = ev.target["metric"]
    old, new = summary[baseline], summary[candidate]
    tradeoffs = []
    if target == "task_pass":
        rows = {name: [c["pass"] for (t, v, r), c in cells.items() if t == ev.target["task"] and v == name]
                for name in (baseline, candidate)}
        improved = all(rows[candidate]) and sum(rows[candidate]) > sum(rows[baseline])
        equal = sum(rows[candidate]) == sum(rows[baseline])
    elif target not in metrics:
        raise InvalidEvidence(f"unknown target metric {target}")
    elif old.get(target) is None or new.get(target) is None:
        improved = equal = False
    else:
        lower = target in LOWER_IS_BETTER or target.startswith("tokens.")
        improved = new[target] < old[target] if lower else new[target] > old[target]
        equal = new[target] == old[target]
    if target != "pass_rate" and new["pass_rate"] < old["pass_rate"]:
        tradeoffs.append(f"pass rate fell from {old['pass_rate']:.2f} to {new['pass_rate']:.2f}")
    if target != "cost_usd" and None not in (old["cost_usd"], new["cost_usd"]) and new["cost_usd"] > old["cost_usd"]:
        tradeoffs.append(f"cost per run rose from {old['cost_usd']:.4f} to {new['cost_usd']:.4f} USD")

    if vetoes:
        decision = "reject: a required case failed for the candidate"
    elif target in unavailable or (target != "task_pass" and old.get(target) is None):
        decision = f"unproven: {target} telemetry is unavailable"
    elif not improved:
        decision = "no win: the candidate did not beat the baseline on the target" + (" (equal results)" if equal else "")
    elif tradeoffs:
        decision = "tradeoff: the target improved, and the user decides the costs listed"
    else:
        decision = "win: the candidate beat the baseline on the declared target in this sample"
    return {"decision": decision, "target": ev.target, "baseline": baseline, "candidate": candidate,
            "summary": summary, "tasks": table, "required_vetoes": vetoes, "tradeoffs": tradeoffs,
            "unavailable_telemetry": unavailable, "repeats": ev.repeats,
            "limits": "A sample this size shows direction, not significance; equal results do not show equivalence.",
            "telemetry_notes": ev.adapter.telemetry_notes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["plan", "calibrate", "run", "blind", "score"])
    parser.add_argument("eval_dir", type=Path)
    parser.add_argument("--tasks", help="comma-separated task ids, for a pilot")
    parser.add_argument("--replace-stale", action="store_true")
    args = parser.parse_args(argv)
    try:
        ev = Eval(args.eval_dir)
        if args.command == "plan":
            cells = ev.plan(args.tasks and args.tasks.split(","))
            print(f"{len(cells)} sessions: {len(ev.variants)} variants x {len(ev.tasks)} tasks x {ev.repeats} repeats")
            for cell in cells:
                print("/".join(map(str, cell)))
        elif args.command == "calibrate":
            return 0 if calibrate(ev) else 1
        elif args.command == "run":
            run(ev, args.tasks and args.tasks.split(","), args.replace_stale)
        elif args.command == "blind":
            blind(ev)
        else:
            report = score(ev)
            (ev.dir / "score.json").write_text(json.dumps(report, indent=2))
            print(json.dumps(report, indent=2))
            return 0 if report["decision"].startswith("win") else 1
    except InvalidEvidence as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
