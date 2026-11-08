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
             "timeout_seconds": 600, "check_timeout_seconds": 120,
             "permission_mode": "acceptEdits", "max_budget_usd": 1},
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
relative to <eval-dir>, outside the runner's output (runs, superseded, calibration,
judging, score.json), and names match [A-Za-z0-9][A-Za-z0-9._-]*. Everything else
in <eval-dir> is the experiment: changing any file, the target or the plan makes
every result stale. Every command first refuses a symlink anywhere in <eval-dir>,
then skill directories inside a fixture and duplicate or unsafe names. Checks get
only PATH, LANG, TMPDIR, HOME (the work dir), EVAL_WORK and EVAL_OUT. However a
cell ends, one sweep makes its folder safe to keep. It never follows a link and
never modifies an existing file, only replaces directory entries: symlinks become
notes, a file holding the values of environment variables named like KEY, TOKEN,
SECRET, PASSWORD or AUTH is replaced by a copy redacted by bytes, and a file that
can't be redacted is replaced by a note.

Accepted limits:
  - Keep checks self-contained in <eval-dir>. A change to a file outside it, such as
    a checker script elsewhere, is not detected and leaves results looking current.
  - A process that starts its own session escapes the cleanup of the host's group.
  - Secret values shorter than 8 characters, or JSON-escaped inside result.json,
    are not redacted.
  - Codex may refresh its login through the linked auth.json, as in normal use. The
    runner never copies, replaces or deletes it.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import sys
import tempfile
import time

import hosts
from hosts import InvalidEvidence, redact, write_atomic

HARNESS = [Path(__file__).resolve(), Path(hosts.__file__).resolve()]
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
OUTPUTS = {"runs", "superseded", "calibration", "judging", "score.json"}
DISCOVERY = {".claude", ".agents", ".codex"}
LOWER_IS_BETTER = {"cost_usd", "turns", "tool_calls", "wall_seconds"}
TARGETS = {"pass_rate", "task_pass"} | LOWER_IS_BETTER
STATUSES = {"ok", "error", "timeout"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise InvalidEvidence(f"{path}: {error}") from None


def require(condition, message: str) -> None:
    if not condition:
        raise InvalidEvidence(message)


def tree_hash(root: Path, skip=(), files=True) -> str:
    """Hash file contents under root, or with files=False only walk it. Any symlink is refused."""
    require(not root.is_symlink(), f"symlink not allowed: {root}")
    digest = hashlib.sha256()
    for directory, folders, names in os.walk(root):
        here = Path(directory)
        if here == root:
            folders[:] = [f for f in folders if f not in skip]
            names = [f for f in names if f not in skip]
        folders.sort()
        for name in folders + sorted(names):
            require(not (here / name).is_symlink(), f"symlink not allowed: {here / name}")
        for name in sorted(names) if files else []:
            path = here / name
            relative = path.relative_to(root).as_posix()
            digest.update(f"{relative} {os.access(path, os.X_OK)} {sha256(path.read_bytes())}\n".encode())
    return digest.hexdigest()


class Eval:
    def __init__(self, directory: Path, adapter=None):
        self.dir = directory.resolve()
        try:
            self._load(read_json(self.dir / "manifest.json"), adapter)
        except (KeyError, TypeError, AttributeError, ValueError) as error:
            raise InvalidEvidence(f"manifest.json: {type(error).__name__}: {error}") from None
        self._identity = None
        tree_hash(self.dir, files=False)

    def _load(self, manifest, adapter) -> None:
        require(manifest["version"] == 1, 'manifest.json needs "version": 1')
        self.manifest = manifest
        self.host = manifest["host"]
        require(isinstance(self.host["model"], str), "host.model must be a string")
        self.adapter = adapter or hosts.ADAPTERS[self.host["adapter"]]()
        self.variants = {}
        for name, path in manifest["variants"].items():
            require(NAME.match(name), f"unsafe variant name {name!r}")
            self.variants[name] = None if path is None else self.input_dir(path)
        ids = [task["id"] for task in manifest["tasks"]]
        require(ids and len(ids) == len(set(ids)), "task ids must be present and unique")
        self.tasks = {}
        for task in manifest["tasks"]:
            require(NAME.match(task["id"]), f"unsafe task id {task['id']!r}")
            require(isinstance(task["prompt"], str), f"task {task['id']} needs a prompt")
            require(all(isinstance(c, str) for c in task.get("checks", [])), f"task {task['id']}: checks are strings")
            if task.get("fixture"):
                fixture = self.input_dir(task["fixture"])
                found = [p for p in fixture.rglob("*") if p.name in DISCOVERY]
                require(not found, f"fixture holds skill discovery directories: {', '.join(map(str, found))}")
            self.tasks[task["id"]] = task
        for role in ("baseline", "candidate"):
            require(manifest[role] in self.variants, f"{role} {manifest[role]!r} is not a variant")
        require(manifest["baseline"] != manifest["candidate"], "baseline and candidate must differ")
        self.repeats = manifest.get("repeats", 3)
        require(isinstance(self.repeats, int) and self.repeats >= 1, "repeats must be a positive integer")
        self.target = manifest["target"]
        metric = self.target["metric"]
        require(metric in TARGETS or metric.startswith("tokens."), f"unknown target metric {metric}")
        require(metric != "task_pass" or self.target.get("task") in self.tasks, "task_pass needs a planned task")

    def inside(self, path: Path) -> Path:
        require(path.resolve().is_relative_to(self.dir), f"{path} leaves {self.dir}")
        return path

    def input_dir(self, relative: str) -> Path:
        path = self.inside(self.dir / relative)
        parts = path.resolve().relative_to(self.dir).parts
        require(parts and parts[0] not in OUTPUTS, f"{relative} overlaps the runner's output")
        require(path.is_dir() and not path.is_symlink(), f"{path} must be a directory, not a symlink")
        return path

    def identity(self) -> str:
        """The experiment: harness, host version, and every input file in the eval dir."""
        if self._identity is None:
            self._identity = sha256(canonical({
                "harness": sha256(b"".join(path.read_bytes() for path in HARNESS)),
                "host_version": self.adapter.version(),
                "inputs": tree_hash(self.dir, skip=OUTPUTS),
            }).encode())
        return self._identity

    def fixture(self, task) -> Path | None:
        return self.dir / task["fixture"] if task.get("fixture") else None

    def plan(self, only=None) -> list:
        """Every planned cell, with the variant order rotated per task and repeat."""
        names = list(self.variants)
        cells = []
        for repeat in range(self.repeats):
            for index, task_id in enumerate(self.tasks):
                if only and task_id not in only:
                    continue
                shift = (repeat + index) % len(names)
                cells += [(task_id, variant, repeat) for variant in names[shift:] + names[:shift]]
        return cells

    def output(self, *parts) -> Path:
        return self.inside(self.dir.joinpath(*map(str, parts)))

    def recorded(self) -> list:
        return sorted(self.output("runs").glob("*/*/*/result.json"))


def run_session(ev: Eval, skills: Path | None, prompt: str, fixture: Path | None, out: Path, variant: str,
                task=None) -> hosts.RunResult:
    """One fresh session in its own work dir, then the task's checks. Its evidence is kept however it ends."""
    out.mkdir(parents=True)
    scratch = Path(tempfile.mkdtemp(prefix="compare-"))
    work = scratch / "work"
    try:
        if fixture:
            shutil.copytree(fixture, work)
        else:
            work.mkdir()
        started = time.monotonic()
        try:
            result = ev.adapter.run(skills=skills, prompt=prompt, work=work, out=out,
                                    settings=ev.host, scratch=scratch, variant=variant)
        except Exception as error:  # A crashed adapter is a failed cell, kept with its reason.
            result = hosts.RunResult(status="error", error=f"{type(error).__name__}: {error}")
        result.wall_seconds = round(time.monotonic() - started, 3)
        if task is not None and result.status == "ok":
            result.checks = run_checks(ev, task, work, out)
        return result
    finally:  # Also on KeyboardInterrupt.
        keep_work(work, scratch, out)


def keep_work(work: Path, scratch: Path, out: Path) -> None:
    """Keep the work dir in `out`, then make the whole cell folder safe to keep."""
    if os.path.lexists(work):
        hosts.sanitize(work)
        shutil.move(str(work), str(out / "work"))
    shutil.rmtree(scratch, ignore_errors=True)
    hosts.sanitize(out)


def run_checks(ev: Eval, task, work: Path, out: Path) -> list:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": os.environ.get("LANG", "C.UTF-8"),
           "TMPDIR": tempfile.gettempdir(), "HOME": str(work), "EVAL_WORK": str(work), "EVAL_OUT": str(out)}
    results = []
    for index, command in enumerate(task.get("checks", [])):
        log = out / f"check-{index}.log"
        try:
            with open(log, "w") as stream:
                code = hosts.run_group(["sh", "-c", command], cwd=work, env=env, stdout=stream, stderr=stream,
                                       timeout=ev.host.get("check_timeout_seconds", 120))
        finally:
            hosts.redact_file(log)
        results.append({"command": command, "exit": "timeout" if code is None else code})
    return results


def listed_names(answer: str) -> set:
    return set(re.findall(r"[\w:.-]+", answer))


def calibrated(ev: Eval) -> bool:
    marker = ev.output("calibration", "passed.json")
    if not marker.exists():
        return False
    record = read_json(marker)
    require(isinstance(record, dict) and isinstance(record.get("identity"), str), f"{marker}: malformed record")
    return record["identity"] == ev.identity()


def calibrate(ev: Eval) -> bool:
    """Probe isolation in a real task fixture with a canary, then load each variant's collection."""
    ev.identity()
    marker = ev.output("calibration", "passed.json")
    marker.unlink(missing_ok=True)
    base = ev.output("calibration", time.strftime("%Y%m%dT%H%M%S") + f"-{random.randrange(16**4):04x}")
    fixture = ev.fixture(next(iter(ev.tasks.values())))
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
        result = run_session(ev, tree, prompt, fixture, base / probe_id, f"calibrate-{probe_id}")
        result.save(base / probe_id)
        outcomes = [(False, f"session {result.status}: {result.error}")] if result.status != "ok" else checks(result)
        for ok, what in outcomes:
            passed &= bool(ok)
            report.append({"probe": probe_id, "pass": bool(ok), "check": what})
            print(f"{'PASS' if ok else 'FAIL'} {probe_id}: {what}")
    write_atomic(base / "calibration.json", json.dumps(
        {"identity": ev.identity(), "pass": passed, "probes": report}, indent=2))
    if passed:
        write_atomic(marker, json.dumps({"identity": ev.identity(), "evidence": str(base)}))
    print(f"calibration {'passed' if passed else 'failed'}; evidence in {base}")
    return passed


def supersede(ev: Eval, folder: Path, stamp: str) -> None:
    runs = (ev.dir / "runs").resolve()
    require(not folder.is_symlink() and folder.resolve().is_relative_to(runs), f"{folder} is not inside {runs}")
    kept = ev.output("superseded", stamp, folder.relative_to(ev.dir / "runs"))
    kept.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(folder), str(kept))


def run(ev: Eval, only=None, replace_stale=False) -> None:
    ev.identity()
    for task_id in only or []:
        require(task_id in ev.tasks, f"unknown task {task_id}")
    stale = [path.parent for path in ev.recorded() if read_json(path).get("identity") != ev.identity()]
    if stale and not replace_stale:
        raise InvalidEvidence(f"{len(stale)} results belong to an earlier experiment (inputs, plan or target "
                              "changed). Use a fresh eval dir, or --replace-stale to move them to superseded/.")
    stamp = time.strftime("%Y%m%dT%H%M%S")
    for folder in stale:
        supersede(ev, folder, stamp)
    todo = [cell for cell in ev.plan(only) if not ev.output("runs", *cell, "result.json").exists()]
    print(f"{len(todo)} sessions to run")
    if todo and not calibrated(ev) and not calibrate(ev):
        raise InvalidEvidence("calibration failed; fix the adapter or host settings first")
    for task_id, variant, repeat in todo:
        out = ev.output("runs", task_id, variant, repeat)
        if out.exists():  # An interrupted cell: keep it, start over.
            supersede(ev, out, stamp)
        task = ev.tasks[task_id]
        result = run_session(ev, ev.variants[variant], task["prompt"], ev.fixture(task), out, variant, task)
        tree = ev.variants[variant]
        result.save(out, extra={
            "task": task_id, "variant": variant, "repeat": repeat, "identity": ev.identity(),
            "inputs": {"model": ev.host.get("model"), "effort": ev.host.get("effort"),
                       "host_version": ev.adapter.version(), "variant_hash": tree and tree_hash(tree)},
        })
        print(task_id, variant, repeat, result.status, f"{result.wall_seconds:.0f}s")


def load_cell(ev: Eval, task_id, variant, repeat) -> dict:
    path = ev.output("runs", task_id, variant, repeat, "result.json")
    require(path.exists(), f"missing cell {task_id}/{variant}/{repeat}")
    data = read_json(path)
    require(isinstance(data, dict) and data.get("identity") == ev.identity(),
            f"stale cell {task_id}/{variant}/{repeat}: it belongs to an earlier experiment")
    number = (int, float)
    valid = (data.get("status") in STATUSES and isinstance(data.get("answer"), str)
             and isinstance(data.get("checks"), list)
             and all(isinstance(c, dict) and (c.get("exit") == "timeout" or type(c.get("exit")) is int)
                     for c in data["checks"])
             and (data.get("calls") is None or isinstance(data["calls"], list))
             and (data.get("tokens") is None or isinstance(data["tokens"], dict))
             and all(data.get(k) is None or isinstance(data[k], number) for k in ("cost_usd", "turns"))
             and isinstance(data.get("wall_seconds"), number))
    require(valid, f"{path}: malformed result")
    expected = [redact(c) for c in ev.tasks[task_id].get("checks", [])] if data["status"] == "ok" else []
    require([c.get("command") for c in data["checks"]] == expected and all(set(c) == {"command", "exit"}
            for c in data["checks"]), f"{path}: checks don't match the manifest's checks for {task_id}")
    return data


def blind(ev: Eval) -> Path:
    judging = ev.output("judging")
    items, key = [], {}
    for task_id, variant, repeat in ev.plan():
        task = ev.tasks[task_id]
        if not task.get("judge"):
            continue
        stored = load_cell(ev, task_id, variant, repeat)
        blind_id = f"item-{random.randrange(16**8):08x}"
        items.append({"id": blind_id, "task": task["prompt"], "criteria": task["judge"], "answer": stored["answer"]})
        key[blind_id] = {"task": task_id, "variant": variant, "repeat": repeat, "identity": ev.identity()}
    random.shuffle(items)
    judging.mkdir(exist_ok=True)
    write_atomic(judging / "packet.json", json.dumps(items, indent=2))
    write_atomic(judging / "key.json", json.dumps(key, indent=2))
    print(f"Give a fresh judge only {judging / 'packet.json'}. It writes {judging / 'verdicts.json'} "
          'as {"<id>": {"pass": true, "reason": "..."}}. Keep key.json from the judge.')
    return judging


def judge_verdicts(ev: Eval) -> dict:
    judging = ev.output("judging")
    if not (judging / "key.json").exists():
        return {}
    key = read_json(judging / "key.json")
    verdicts = read_json(judging / "verdicts.json") if (judging / "verdicts.json").exists() else {}
    require(isinstance(key, dict) and isinstance(verdicts, dict), "judging files must hold JSON objects")
    mapped = {}
    for blind_id, verdict in verdicts.items():
        require(isinstance(verdict, dict) and type(verdict.get("pass")) is bool,
                f"verdict {blind_id}: pass must be a JSON boolean")
        cell = key.get(blind_id)
        require(isinstance(cell, dict), f"verdict {blind_id} is not in key.json")
        if cell.get("identity") == ev.identity():
            mapped[(cell["task"], cell["variant"], cell["repeat"])] = verdict["pass"]
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
    planned = ev.plan()
    unplanned = sorted({str(p.parent.relative_to(ev.dir)) for p in ev.recorded()}
                       - {str(Path("runs", *map(str, cell))) for cell in planned})
    problems = [] if calibrated(ev) else ["no passing calibration for this experiment"]
    if unplanned:
        problems.append(f"results outside the plan: {', '.join(unplanned)}")
    cells = {}
    for cell in planned:
        try:
            cells[cell] = load_cell(ev, *cell)
        except InvalidEvidence as error:
            problems.append(str(error))
    verdicts = judge_verdicts(ev)
    for (task_id, variant, repeat), cell in cells.items():
        judged = ev.tasks[task_id].get("judge")
        if judged and (task_id, variant, repeat) not in verdicts:
            problems.append(f"no current judge verdict for {task_id}/{variant}/{repeat}")
        cell["pass"] = (cell["status"] == "ok" and all(c["exit"] == 0 for c in cell["checks"])
                        and (not judged or verdicts.get((task_id, variant, repeat), False)))
    require(not problems, "; ".join(problems))

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
    elif target != "task_pass" and (old.get(target) is None or new.get(target) is None):
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


def main(argv=None, adapter=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["plan", "calibrate", "run", "blind", "score"])
    parser.add_argument("eval_dir", type=Path)
    parser.add_argument("--tasks", help="comma-separated task ids, for a pilot")
    parser.add_argument("--replace-stale", action="store_true")
    args = parser.parse_args(argv)
    try:
        ev = Eval(args.eval_dir, adapter)
        ev.identity()  # Refuse symlinks and unreadable inputs before anything runs.
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
            write_atomic(ev.output("score.json"), json.dumps(report, indent=2))
            print(redact(json.dumps(report, indent=2)))
            return 0 if report["decision"].startswith("win") else 1
    except (InvalidEvidence, KeyError, TypeError, ValueError) as error:
        print(f"invalid: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
