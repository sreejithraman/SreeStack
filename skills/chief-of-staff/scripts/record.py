#!/usr/bin/env python3
"""Record program events in program.json, commit each one, and render the command center.

Each event command refuses an uncommitted program.json change, stamps the time
from this machine's clock, changes only what its event changes, validates,
commits, and renders. `status` reads PRs through `gh` and owner threads through
the T3 CLI; with --turn-end it commits nothing and fails while work is orphaned
or the page is behind the record.
"""

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from render_dashboard import (ACTIVE, DECISION_KEYS, HALTING, LAYER_KEYS, OWNER_KEYS, PROGRAM_KEYS, READY_LAYERS, STATES,
                              TERMINAL, WORK_KEYS, committed, effective_finish, fields, git, known_keys, layout,
                              quoted, records, revision, stage_page, validate)


SATISFIED = {"landed", "done"}
PENDING_LANDINGS = {"released", "submitted"}
LIVE_THREADS = {"running", "waiting"}  # waiting: on its own helpers
VERDICTS = ("pass", "fail", "blocked", "untested")
REPORT_KEYS = ("outcome", "state", "finishLine", "layers", "proof", "shown", "asks", "waits", "blocked")
ASK_KEYS = ("id", "question", "context", "meanwhile", "recommendation", "options", "weight", "phase", "links")
ROUTES = {
    "top-level": "`t3_thread_send` to the chief",
    "adopted": "`t3_thread_send` to the chief",
    "delegated": "End its turn with the report; the chief watches its PR",
}
REPORT_BLOCK = re.compile(r"\A\s*```json[ \t]*\n(.*?)\n```", re.S)
DECISION_LINE = re.compile(r'^Decision ("(?:[^"\\]|\\.)*") \(revision ([0-9a-f]+)\)(?:: (.*)| in .*)$')
CHOICE_LINE = re.compile(r'^I choose option (\d+): ("(?:[^"\\]|\\.)*")$')
STALE_HOURS = 2


class Refused(Exception):
    """The command changed nothing; its message says why."""


def now():
    """The current time in UTC. Event times always come from this clock, never from the caller."""
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00") if "T" in value else value + "T00:00:00+00:00")


def age(since, at):
    minutes = max(0, int((parse_time(at) - parse_time(since)).total_seconds() // 60))
    days, minutes = divmod(minutes, 1440)
    hours, minutes = divmod(minutes, 60)
    return f"{days}d{hours}h" if days else f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


def put(row, key, value, order):
    """Set a field; a new one goes where the schema lists it, so the diff adds one line."""
    if key not in row:
        rank = {name: index for index, name in enumerate(order)}
        items = list(row.items())
        position = next((index for index, (name, _) in enumerate(items) if rank.get(name, len(order)) > rank[key]),
                        len(items))
        items.insert(position, (key, value))
        row.clear()
        row.update(items)
    else:
        row[key] = value


def work_row(state, identity):
    row = next((row for row in state["work"] if row["id"] == identity), None)
    if row is None:
        raise Refused(f"no work {identity}")
    return row


def decision_row(state, identity):
    row = next((row for row in state["decisions"] if row["id"] == identity), None)
    if row is None:
        raise Refused(f"no decision {identity}")
    return row


def open_blocks(state, identity, phases=None):
    """Open decisions that hold this work, at any phase or only the given ones."""
    return [decision["id"] for decision in state["decisions"] if decision["status"] == "open"
            for entry in decision.get("blocks", []) if entry["id"] == identity and (phases is None or entry["phase"] in phases)]


def waits_on_need(state, row):
    """An open Need that halts this work, or that it waits on at its stop (a shown Try or ready work)."""
    phases = None if row["state"] in {"shown", "ready"} else HALTING
    return open_blocks(state, row["id"], phases)


def unsatisfied(state, row):
    by_id = {other["id"]: other for other in state["work"]}
    return [identity for identity in row.get("blockedBy", []) if by_id[identity]["state"] not in SATISFIED]


def pending_landing(state, identity):
    return next((landing for landing in state.get("landings", [])
                 if landing["state"] in PENDING_LANDINGS and identity in landing["work"]), None)


def set_next(state, value):
    if value:
        state["next"] = value


# Events. Each takes the committed program and returns the commit message and notes to print.

def start(state, at, work, owner, mode="top-level", session=None, route=None, workspace=None, replace=False):
    row = work_row(state, work)
    if row["state"] in TERMINAL:
        raise Refused(f"{work} is {row['state']}")
    recorded = row.get("owner", {})
    if recorded and recorded["name"] != owner and not replace:
        raise Refused(f"{work} already has owner {recorded['name']}; reconcile it, then pass --replace")
    if recorded and row["state"] in ACTIVE and not replace:
        raise Refused(f"{work} is already {row['state']} under {owner}")
    waiting = unsatisfied(state, row)
    if waiting:
        raise Refused(f"{work} is blocked by {', '.join(waiting)}; start it when they land, or record a provisional base")
    held = open_blocks(state, work, HALTING)
    if held:
        raise Refused(f"{work} is held by open decision {', '.join(held)}")
    notes = []
    if "blockedBy" in row:
        notes.append(f"dropped satisfied blockedBy {', '.join(row.pop('blockedBy'))}")
    record = {} if replace else copy.deepcopy(recorded)
    record["name"] = owner
    for key, value in (("session", session), ("start", mode), ("route", route or ROUTES[mode]), ("workspace", workspace)):
        if value:
            put(record, key, value, OWNER_KEYS)
    put(row, "owner", record, WORK_KEYS)
    if row["state"] in {"planned", "unknown"}:
        row["state"] = "building"
        row.pop("unknownReason", None)
    row["checkedAt"] = at
    return f"{work} start: {owner}", notes


def read_report(state_file, work):
    path = state_file.parent / "reports" / f"{work}.md"
    try:
        content = path.read_text()
    except OSError as error:
        raise Refused(f"cannot read {path}: {error.strerror}") from None
    match = REPORT_BLOCK.match(content)
    if not match:
        raise Refused(f"{path} must start with a ```json block; see references/program-state.md#owner-reports")
    try:
        block = json.loads(match[1])
    except json.JSONDecodeError as error:
        raise Refused(f"{path}: the report block is not JSON: {error}") from None
    if not isinstance(block, dict):
        raise Refused(f"{path}: the report block must be an object")
    return block, path


def objects(value, path):
    return records(value, f"report {path}")


def only(item, keys, path):
    known_keys(item, f"report {path}", keys)


def report(state, at, work, block, source):
    """Apply an owner report block: each field it names replaces that part of the record."""
    only(block, REPORT_KEYS, "block")
    row = work_row(state, work)
    if block.get("outcome") != work:
        raise Refused(f"the report block names outcome {block.get('outcome')!r}, not {work}")
    if block.get("state") not in STATES:
        raise Refused(f"report state must be one of {', '.join(STATES)}")
    if block["state"] in TERMINAL:
        raise Refused(f"a report cannot record {block['state']}: run status, which reads merges at the forge, "
                      "or record a scrap by hand")
    merged = {layer["id"] for layer in row.get("layers", []) if layer["status"] == "merged"}
    for layer in objects(block.get("layers", []), "layers"):
        if layer.get("status") == "merged" and layer.get("id") not in merged:
            raise Refused(f"report layer {layer.get('id')} claims merged; report it ready and run status, "
                          "which reads merges at the forge")
    notes = []
    row["state"] = block["state"]
    if block["state"] != "unknown":
        row.pop("unknownReason", None)
    if "finishLine" in block:
        if "finishLine" not in row:
            put(row, "finishLine", block["finishLine"], WORK_KEYS)
        elif block["finishLine"] != row["finishLine"]:
            notes.append(f"the owner reports finish line {block['finishLine']}; the record keeps {row['finishLine']}")
    if "layers" in block:
        replace_list(row, "layers", objects(block["layers"], "layers"))
    if "proof" in block:
        proof = objects(block["proof"], "proof")
        for index, item in enumerate(proof):
            only(item, ("assertion", "verdict", "url"), f"proof[{index}]")
            if item.get("verdict") not in VERDICTS or not isinstance(item.get("assertion"), str):
                raise Refused(f"report proof[{index}] needs an assertion and a verdict: {', '.join(VERDICTS)}")
        replace_list(row, "evidence", [{"label": item["assertion"], "url": item["url"]} for item in proof if "url" in item])
        gaps = "; ".join(f"{item['verdict']}: {item['assertion']}" for item in proof if item["verdict"] != "pass")
        if gaps:
            put(row, "acceptance", gaps, WORK_KEYS)
        else:
            row.pop("acceptance", None)
    if "shown" in block:
        replace_list(row, "results", objects(block["shown"], "shown"))
    if "blocked" in block:
        if block["blocked"] is None:
            row.pop("blocked", None)
        else:
            put(row, "blocked", block["blocked"], WORK_KEYS)
    if "waits" in block:
        reported = objects(block["waits"], "waits")
        for index, item in enumerate(reported):
            fields(known_keys(item, f"report waits[{index}]", ("on", "event")), f"report waits[{index}]", ("on", "event"))
        kept = {(wait["on"], wait["event"]) for wait in reported}
        waits = [wait for wait in state.get("waits", []) if wait.get("work") != work or (wait["on"], wait["event"]) in kept]
        have = {(wait["on"], wait["event"]) for wait in waits if wait.get("work") == work}
        waits += [{"date": at, "work": work, "on": wait["on"], "event": wait["event"]}
                  for wait in reported if (wait["on"], wait["event"]) not in have]
        replace_list(state, "waits", waits, PROGRAM_KEYS)
    asked = []
    for index, ask in enumerate(objects(block.get("asks", []), "asks")):
        only(ask, ASK_KEYS, f"asks[{index}]")
        if any(decision["id"] == ask.get("id") for decision in state["decisions"]):
            notes.append(f"decision {ask.get('id')} is already recorded; left as it is")
            continue
        decision = {"id": ask.get("id"), "question": ask.get("question"), "date": at, "source": source, "status": "open"}
        decision |= {key: ask[key] for key in ("context", "meanwhile", "recommendation", "options", "weight") if key in ask}
        decision["blocks"] = [{"id": work, "phase": ask.get("phase", "acceptance")}]
        if "links" in ask:
            decision["links"] = ask["links"]
        state["decisions"].append({key: decision[key] for key in DECISION_KEYS if key in decision})
        asked.append(ask.get("id"))
    row["checkedAt"] = at
    message = f"{work} report: {block['state']}"
    if asked:
        message += f", asks {', '.join(asked)}"
        notes.append(f"triage {', '.join(asked)}: resolve it with `resolve`, or ask the user")
    return message, notes


def replace_list(row, key, value, order=WORK_KEYS):
    if value:
        put(row, key, value, order)
    else:
        row.pop(key, None)


def settle(state, at, identity, answer, status, source=None, basis=None):
    """Record an answer: answered when it is the user's, resolved when it is the chief's call."""
    row = decision_row(state, identity)
    if row["status"] == "withdrawn":
        raise Refused(f"{identity} was withdrawn")
    if status == "resolved" and row["status"] != "open":
        raise Refused(f"{identity} is {row['status']}; only an open decision can be resolved")
    if row["status"] != "open":
        earlier = f"{at}: replaced the earlier {row['status']} answer {json.dumps(row['answer'], ensure_ascii=False)}"
        earlier += f" (basis: {row.pop('basis')})." if "basis" in row else f" (source: {row.pop('answerSource')})."
        put(row, "rationale", f"{row['rationale']} {earlier}" if row.get("rationale") else earlier, DECISION_KEYS)
    row["status"] = status
    put(row, "answer", answer, DECISION_KEYS)
    if status == "answered":
        put(row, "answerSource", source, DECISION_KEYS)
    else:
        put(row, "basis", basis, DECISION_KEYS)
    affected = ", ".join(f"{entry['id']} ({entry['phase']})" for entry in row.get("blocks", []))
    return f"{identity} {status}", [f"update the owners of {affected}"] if affected else []


def option_label(row, number):
    options = row.get("options", [])
    if not 1 <= number <= len(options):
        raise Refused(f"{row['id']} has no option {number}")
    return options[number - 1]["label"]


def pasted_choices(text):
    """(decision ID, revision, option number, label) for each choice in a pasted page prompt."""
    choices, pending = [], None
    for line in (line.strip() for line in text.splitlines()):
        decision = DECISION_LINE.match(line)
        if decision:
            pending = (json.loads(decision[1]), decision[2])
            choice = CHOICE_LINE.match(decision[3] or "")
            if choice:
                choices.append((*pending, int(choice[1]), json.loads(choice[2])))
                pending = None
            elif decision[3]:
                raise Refused(f"cannot read the choice in: {line}")
            continue
        choice = CHOICE_LINE.match(line)
        if choice and pending:
            choices.append((*pending, int(choice[1]), json.loads(choice[2])))
            pending = None
        elif line == "Reopen this decision." and pending:
            raise Refused(f"{pending[0]}: a reopen request; reopen it under references/decisions.md#reopen")
    if not choices:
        raise Refused("no decision choice found in the pasted text")
    return choices


def answer_pasted(state, at, text, source):
    """Record each pasted choice that matches its open decision's current revision; return the rest to ask again."""
    recorded, stale = [], []
    for identity, digest, number, label in pasted_choices(text):
        row = next((row for row in state["decisions"] if row["id"] == identity), None)
        options = row.get("options", []) if row else []
        if (row is None or row["status"] != "open" or revision(row) != digest
                or not 1 <= number <= len(options) or quoted(options[number - 1]["label"]) != quoted(label)):
            stale.append(identity)
            continue
        settle(state, at, identity, options[number - 1]["label"], "answered", source=source)
        recorded.append(identity)
    notes = [f"ask again: {identity} changed or closed since the page showed it" for identity in stale]
    if not recorded:
        raise Refused("; ".join(notes))
    affected = sorted({entry["id"] for identity in recorded for entry in decision_row(state, identity).get("blocks", [])})
    if affected:
        notes.append(f"update the owners of {', '.join(affected)}")
    return f"{', '.join(recorded)} answered", notes


def wait(state, at, on, event=None, work=None, clear=False):
    if work:
        work_row(state, work)
    waits = state.get("waits", [])
    if clear:
        kept = [row for row in waits if not (row["on"] == on and row.get("work") == work)]
        if len(kept) == len(waits):
            raise Refused(f"no wait on {on!r}" + (f" for {work}" if work else ""))
        replace_list(state, "waits", kept, PROGRAM_KEYS)
        return f"wait cleared: {on}" + (f" ({work})" if work else ""), []
    if not event:
        raise Refused("a wait needs --event: what ends it")
    entry = {"date": at, "on": on, "event": event} | ({"work": work} if work else {})
    replace_list(state, "waits", [*waits, entry], PROGRAM_KEYS)
    return f"wait: {on}" + (f" ({work})" if work else ""), []


def release(state, at, works, lander=None, target=None, keep=None, note=None):
    """Release one merge set at the heads and bases the record holds."""
    rows = [work_row(state, identity) for identity in works]
    for row in rows:
        if row["state"] != "ready" or effective_finish(row) != "land":
            raise Refused(f"{row['id']} is not ready to land")
        held = open_blocks(state, row["id"])
        if held or unsatisfied(state, row) or row.get("blocked"):
            raise Refused(f"{row['id']} is held by {', '.join(held) or row.get('blocked') or 'its blockedBy'}")
        if pending_landing(state, row["id"]):
            raise Refused(f"{row['id']} already has pending landing {pending_landing(state, row['id'])['id']}")
    layers = [layer for row in rows for layer in row["layers"] if layer["status"] != "merged"]
    owners_of = {layer["id"]: (layer, row) for row in state["work"] for layer in row.get("layers", [])}
    unmerged = {layer["id"] for layer in layers}
    for layer in layers:
        below = owners_of.get(layer.get("stackedOn"))
        if below and below[0]["status"] != "merged" and below[0]["id"] not in unmerged:
            raise Refused(f"{layer['id']} stacks on unmerged {below[0]['id']} ({below[1]['id']}); release them together")
    for layer in layers:
        if not layer.get("head") or not layer.get("base"):
            raise Refused(f"layer {layer['id']} has no recorded head and base; run status first")
    owners = {row["owner"]["name"] for row in rows}
    lander = lander or (owners.pop() if len(owners) == 1 else None)
    if not lander:
        raise Refused("the set spans owners; name its one --lander")
    bottoms = {layer["base"] for layer in layers if layer.get("stackedOn") not in unmerged}
    target = target or (bottoms.pop() if len(bottoms) == 1 else None)
    if not target:
        raise Refused("name the --target branch")
    repos = {row["repo"] for row in rows}
    for landing in state.get("landings", []):
        if (landing["state"] in PENDING_LANDINGS and landing["target"] == target
                and repos & {work_row(state, identity)["repo"] for identity in landing["work"]}):
            raise Refused(f"landing {landing['id']} is still pending on {target}; one pending landing per target")
    numbers = [int(match[1]) for landing in state.get("landings", []) if (match := re.fullmatch(r"L(\d+)", landing["id"]))]
    identity = f"L{max(numbers, default=0) + 1}"
    entry = {"id": identity, "date": at, "chief": state["chief"], "lander": lander, "target": target, "work": works,
             "prs": [{"url": layer["url"], "head": layer["head"], "base": layer["base"]} for layer in layers],
             "state": "released"}
    entry |= {key: value for key, value in (("keep", keep), ("note", note)) if value}
    replace_list(state, "landings", [*state.get("landings", []), entry], PROGRAM_KEYS)
    return f"{identity} released: {', '.join(works)} to {target}", [f"resume {lander} with landing {identity}"]


def move_landing(state, at, identity, to, read_pr, note=None):
    landing = next((row for row in state.get("landings", []) if row["id"] == identity), None)
    if landing is None:
        raise Refused(f"no landing {identity}")
    if landing["state"] in {"landed", "withdrawn"}:
        raise Refused(f"{identity} is already {landing['state']}")
    if to == "withdrawn" and not note:
        raise Refused("a withdrawal needs --note: why")
    if to == "landed":
        for pr in landing["prs"]:
            if read_pr(pr["url"]).get("state") != "MERGED":
                raise Refused(f"{pr['url']} is not merged on the forge")
        for work in landing["work"]:
            row = work_row(state, work)
            for layer in row.get("layers", []):
                if any(pr["url"] == layer.get("url") for pr in landing["prs"]):
                    layer["status"] = "merged"
            if all(layer["status"] == "merged" for layer in row.get("layers", [])):
                row["state"] = "landed"
            row["checkedAt"] = at
    landing["state"] = to
    if note:
        put(landing, "note", note, ("id", "date", "chief", "lander", "target", "work", "prs", "state", "keep", "note"))
    return f"{identity} {to}", []


# Status: facts from the forge and the host.

def gh_pr(target):
    gh = shutil.which("gh")
    if not gh:
        raise OSError("gh is not installed")
    result = subprocess.run([gh, "pr", "view", target, "--json", "state,isDraft,headRefOid,baseRefName"],
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise OSError(result.stderr.strip() or f"gh exited with status {result.returncode}")
    return json.loads(result.stdout)


def t3_thread(identity):
    cli = os.environ.get("T3CODE_CLI_PATH") or shutil.which("t3")
    if not cli:
        raise OSError("no T3 CLI: T3CODE_CLI_PATH is unset and t3 is not on PATH")
    result = subprocess.run([cli, "thread", "show", "--json", "--messages", "1", identity],
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise OSError(result.stderr.strip() or f"t3 exited with status {result.returncode}")
    return json.loads(result.stdout)["thread"]


def thread_id(session):
    parts = urlsplit(session)
    segments = [segment for segment in (parts.netloc if parts.scheme == "t3-thread" else "", *parts.path.split("/")) if segment]
    return unquote(segments[-1]) if segments else None


def read_owners(state, read_thread):
    """Thread facts per open work row with an owner session: {work ID: thread or error string}."""
    found, cache = {}, {}
    for row in state["work"]:
        session = row.get("owner", {}).get("session")
        if row["state"] in TERMINAL or not session:
            continue
        identity = thread_id(session)
        if identity not in cache:
            try:
                cache[identity] = read_thread(identity)
            except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
                cache[identity] = f"could not read its thread: {error}"
        found[row["id"]] = cache[identity]
    return found


def live(thread):
    return isinstance(thread, dict) and thread.get("status") in LIVE_THREADS


def read_layers(row, read_pr, forge, notes):
    """Apply forge facts to a copy of the row's layers; return it and whether every read succeeded."""
    facts, reads, failed = copy.deepcopy(row), 0, 0
    for layer in facts.get("layers", []):
        if "url" not in layer or layer["status"] == "merged":
            continue
        reads += 1
        try:
            pr = forge[layer["url"]] = read_pr(layer["url"])
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            failed += 1
            notes.append(f"{row['id']}: could not read {layer['url']}: {error}")
            continue
        moved = False
        for key, value in (("head", pr.get("headRefOid", "")), ("base", pr.get("baseRefName", ""))):
            recorded = layer.get(key, "")
            if value and not (recorded and (value.startswith(recorded) if key == "head" else value == recorded)):
                put(layer, key, value, LAYER_KEYS)
                moved = True
                if recorded:
                    notes.append(f"{row['id']}: {layer['id']} {key} moved to {value[:7] if key == 'head' else value}")
        status = {"MERGED": "merged", "CLOSED": "closed"}.get(pr.get("state"))
        status = status or ("draft" if pr.get("isDraft") else "ready" if layer["status"] == "ready" and not moved else "open")
        if status != layer["status"]:
            if status == "closed":
                notes.append(f"{row['id']}: {layer['id']} closed without merge")
            layer["status"] = status
    return facts, reads, failed


def derived_state(row):
    """The state the row's layers now imply, or its current one."""
    layers = row.get("layers", [])
    if layers and all(layer["status"] == "merged" for layer in layers) and effective_finish(row) == "land":
        return "landed"
    if row["state"] == "ready" and any(layer["status"] not in READY_LAYERS[effective_finish(row)][0] for layer in layers):
        return "in-review"
    return row["state"]


def first_valid(state, candidates):
    """Raise each row from its original toward its best candidate while the whole program stays valid.

    Rows go in ID order and passes repeat until none moves, so a row stays back only when its own
    change fails against everything else that was accepted. Return why each row stayed back.
    """
    levels = {index: len(options) - 1 for index, options in candidates.items()}
    reasons = {}

    def accepts(trial):
        for index, level in trial.items():
            state["work"][index] = candidates[index][level]
        try:
            validate(state)
            return None
        except ValueError as error:
            return error

    order = sorted(candidates, key=lambda index: candidates[index][-1]["id"])
    moved = True
    while moved:
        moved = False
        for index in order:
            for level in range(levels[index]):
                problem = accepts(levels | {index: level})
                if problem is None:
                    levels[index], moved = level, True
                    reasons.pop(index, None)
                    break
                if level == 0:
                    reasons[index] = problem
    accepts(levels)
    return {index: reasons[index] for index in candidates if levels[index] > 0}


def observe(state, at, read_pr, threads):
    """Apply forge facts to open work and pending landings; return notes on what changed or needs a hand."""
    notes, forge, candidates = [], {}, {}
    for index, row in enumerate(state["work"]):
        if row["state"] in TERMINAL:
            continue
        facts, reads, failed = read_layers(row, read_pr, forge, notes)
        if thread := threads.get(row["id"]):
            reads += 1
            failed += isinstance(thread, str)
        if reads and not failed:
            facts["checkedAt"] = at
        derived = copy.deepcopy(facts) | {"state": derived_state(facts)}
        if derived != row:
            candidates[index] = [derived, *([facts] if facts != derived else []), row]
    reasons = first_valid(state, candidates)
    for index, (*_, original) in candidates.items():
        row = state["work"][index]
        if index in reasons:
            kept = "nothing" if row is original else "its forge facts"
            notes.append(f"{row['id']}: recorded {kept} from the forge; settle by hand: {reasons[index]}")
        elif row["state"] != original["state"]:
            notes.append(f"{row['id']}: {original['state']} -> {row['state']}")
    merged = {layer["url"] for row in state["work"] for layer in row.get("layers", [])
              if layer["status"] == "merged" and "url" in layer}
    for landing in state.get("landings", []):
        if landing["state"] not in PENDING_LANDINGS:
            continue
        if all(entry["url"] in merged or forge.get(entry["url"], {}).get("state") == "MERGED" for entry in landing["prs"]):
            landing["state"] = "landed"
            notes.append(f"{landing['id']}: landed")
            continue
        for entry in landing["prs"]:
            pr = forge.get(entry["url"])
            if pr and pr.get("state") != "MERGED" and (
                    not pr.get("headRefOid", "").startswith(entry["head"])
                    or (not re.fullmatch(r"[0-9a-f]{7,40}", entry["base"]) and pr.get("baseRefName") != entry["base"])):
                notes.append(f"{landing['id']}: a released head or base moved; withdraw the release before telling {landing['lander']}")
                break
    return notes


def orphans(state, threads):
    """Open work with no live owner, recorded wait, holding Need, or blocker."""
    waits = {row.get("work") for row in state.get("waits", [])}
    found = []
    for row in state["work"]:
        proposed = row["state"] == "planned" and row.get("required") is False
        at_pr_state = row["state"] == "ready" and effective_finish(row) != "land"  # stopped for the user
        if row["state"] in TERMINAL or proposed or at_pr_state:
            continue
        if (live(threads.get(row["id"])) or row["id"] in waits or waits_on_need(state, row)
                or unsatisfied(state, row) or row.get("blocked")):
            continue
        thread = threads.get(row["id"])
        landing = pending_landing(state, row["id"])
        why = ("not started" if row["state"] == "planned"
               else "ready with no landing release" if row["state"] == "ready" and not landing
               else thread if isinstance(thread, str) else f"owner {thread['status']}" if thread
               else "owner has no session to read" if "owner" in row else "no owner")
        if landing:
            why += f" with landing {landing['id']} {landing['state']}"
        found.append(f"{row['id']} ({row['state']}): {why}")
    return found


def todo(state, at, threads, stale_hours=STALE_HOURS):
    """What the chief should do now, grouped by kind."""
    waits = {row.get("work") for row in state.get("waits", [])}
    groups = {name: [] for name in ("start", "release", "idle owners", "approvals", "stale", "needs open", "needs answered")}
    for row in state["work"]:
        identity, current = row["id"], row["state"]
        if current in TERMINAL:
            continue
        held = open_blocks(state, identity)
        if (current == "planned" and row.get("required") is not False and not unsatisfied(state, row)
                and not row.get("blocked") and not open_blocks(state, identity, HALTING)):
            groups["start"].append(f"{identity}: {row['title']}")
        if (current == "ready" and effective_finish(row) == "land" and not held and not unsatisfied(state, row)
                and not row.get("blocked") and not pending_landing(state, identity)):
            groups["release"].append(f"{identity}: {row['title']}")
        thread = threads.get(identity)
        if isinstance(thread, dict) and thread.get("pendingRequestCount"):
            groups["approvals"].append(f"{identity}: {row['owner']['name']} waits on an approval in its thread")
        owes = current in {"building", "in-review"} or (current == "ready" and pending_landing(state, identity))
        if owes and not live(thread) and identity not in waits and not waits_on_need(state, row):
            if isinstance(thread, dict):
                idle = f" for {age(thread['updatedAt'], at)}" if thread.get("updatedAt") else ""
                why = f"{thread['status']}{idle} with no recorded wait"
            else:
                why = thread or "has no session to read"
            groups["idle owners"].append(f"{identity}: {row['owner']['name']} {why}")
        if (parse_time(at) - parse_time(row["checkedAt"])).total_seconds() > stale_hours * 3600:
            groups["stale"].append(f"{identity}: checked {age(row['checkedAt'], at)} ago")
    for decision in state["decisions"]:
        affected = [entry["id"] for entry in decision.get("blocks", [])
                    if work_row(state, entry["id"])["state"] not in TERMINAL]
        if decision["status"] == "open":
            groups["needs open"].append(f"{decision['id']}: waiting {age(decision['date'], at)}: {decision['question']}")
        elif decision["status"] == "answered" and affected:
            groups["needs answered"].append(f"{decision['id']}: confirm {', '.join(affected)} follow the answer")
    return {name: rows for name, rows in groups.items() if rows}


# Command line.

class Record:
    """One program folder: its state file in git, and the page rendered from HEAD."""

    def __init__(self, state_file, page=None):
        self.file = state_file.absolute()
        self.page = (page or self.file.with_name("command-center.html")).absolute()

    def git(self, *args):
        return git(self.file, *args)

    def dirty(self):
        return self.git("status", "--porcelain", "--", self.file.name).strip()

    def load(self):
        """The committed program. An uncommitted change stops the command with its diff."""
        self.git("ls-files", "--error-unmatch", "--", self.file.name)
        if self.dirty():
            raise Refused(f"{self.file} has an uncommitted change. Settle it with the user first: to keep it, check it "
                          f"with render_dashboard.py --check and commit it; otherwise run "
                          f"git -C {self.file.parent} checkout HEAD -- {self.file.name}\n"
                          + self.git("diff", "HEAD", "--", self.file.name))
        text = self.file.read_text()
        state = validate(json.loads(text))
        if text != layout(state):
            raise Refused(f"{self.file} is not one value per line; run render_dashboard.py --check for the fix")
        return state

    def save(self, state, message):
        validate(state)
        previous = self.file.read_text()
        self.file.write_text(layout(state))
        try:
            self.git("commit", "-q", "-m", message, "--", self.file.name)
        except (Refused, ValueError):
            self.file.write_text(previous)
            raise
        print(f"committed: {message}")

    def render(self):
        """Stage HEAD's page and say whether the published page is behind it."""
        try:
            head = self.git("rev-parse", "--short", "HEAD").strip()
            behind = stage_page(self.file, self.page)
        except (OSError, ValueError) as error:
            print(f"page: render failed after the record was saved: {error}. Retry with render_dashboard.py --page.")
            return False
        if behind:
            staged = self.page.with_name(f"{self.page.stem}.next{self.page.suffix}")
            print(f"page: behind record {head}. Publish {staged}, then move it over {self.page}.")
            return False
        print(f"page: published page matches record {head}")
        return True


def arguments():
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--state", required=True, type=Path, help="The program.json file")
    shared.add_argument("--page", type=Path, help="The last published page; default command-center.html beside the state")
    shared.add_argument("--next", help="Also set the program's next action")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    command = commands.add_parser("start", parents=[shared], help="An owner started on a work row")
    command.add_argument("--work", required=True)
    command.add_argument("--owner", required=True, help="The owner's name")
    command.add_argument("--session", help="The owner's thread link")
    command.add_argument("--mode", choices=tuple(ROUTES), default="top-level")
    command.add_argument("--route", help="Default follows --mode")
    command.add_argument("--workspace")
    command.add_argument("--replace", action="store_true", help="Replace a reconciled active owner")

    command = commands.add_parser("report", parents=[shared], help="Apply reports/<work>.md's block")
    command.add_argument("--work", required=True)

    command = commands.add_parser("answer", parents=[shared], help="The user answered a decision")
    command.add_argument("--source", required=True, help="The user's message that answered")
    command.add_argument("--decision")
    choice = command.add_mutually_exclusive_group()
    choice.add_argument("--option", type=int, help="The chosen option's number")
    choice.add_argument("--text", help="The answer in the user's words")
    command.add_argument("--pasted", action="store_true", help="Read a copied page prompt from stdin")

    command = commands.add_parser("resolve", parents=[shared], help="The chief settled a decision under triage")
    command.add_argument("--decision", required=True)
    command.add_argument("--basis", required=True, help="The recorded source that settles it, and why it is reversible")
    choice = command.add_mutually_exclusive_group(required=True)
    choice.add_argument("--option", type=int)
    choice.add_argument("--text")

    command = commands.add_parser("land", parents=[shared], help="Release a merge set, or move a landing")
    command.add_argument("--work", action="append", help="Release these ready rows as one set")
    command.add_argument("--lander")
    command.add_argument("--target")
    command.add_argument("--keep")
    command.add_argument("--landing", help="Move this landing instead")
    command.add_argument("--to", choices=("submitted", "landed", "withdrawn"))
    command.add_argument("--note")

    command = commands.add_parser("wait", parents=[shared], help="Record or clear a wait")
    command.add_argument("--on", required=True)
    command.add_argument("--event", help="What ends the wait")
    command.add_argument("--work")
    command.add_argument("--clear", action="store_true")

    command = commands.add_parser("status", parents=[shared], help="Read PRs and owner threads; list what to do now")
    command.add_argument("--turn-end", action="store_true",
                         help="Commit nothing; fail while open work is orphaned or the page is behind")
    command.add_argument("--stale-hours", type=float, default=STALE_HOURS)
    return parser


def event(args, state, at):
    if args.command == "start":
        return start(state, at, args.work, args.owner, args.mode, args.session, args.route, args.workspace, args.replace)
    if args.command == "report":
        block, path = read_report(args.state, args.work)
        return report(state, at, args.work, block, f"reports/{path.name}")
    if args.command == "answer":
        if args.pasted:
            return answer_pasted(state, at, sys.stdin.read(), args.source)
        if not args.decision or not (args.option or args.text):
            raise Refused("answer needs --decision with --option or --text, or --pasted")
        row = decision_row(state, args.decision)
        return settle(state, at, args.decision, option_label(row, args.option) if args.option else args.text,
                      "answered", source=args.source)
    if args.command == "resolve":
        row = decision_row(state, args.decision)
        return settle(state, at, args.decision, option_label(row, args.option) if args.option else args.text,
                      "resolved", basis=args.basis)
    if args.command == "land":
        if args.landing:
            if not args.to:
                raise Refused("moving a landing needs --to")
            return move_landing(state, at, args.landing, args.to, gh_pr, args.note)
        if not args.work:
            raise Refused("land needs --work to release, or --landing with --to")
        return release(state, at, args.work, args.lander, args.target, args.keep, args.note)
    return wait(state, at, args.on, args.event, args.work, args.clear)


def status(args, record, read_pr=gh_pr, read_thread=t3_thread):
    at = now()
    if args.turn_end:
        state = validate(committed(record.file))
        found = orphans(state, read_owners(state, read_thread))
        if record.dirty():
            found.append(f"{record.file.name} has an uncommitted change; settle it before the turn ends")
        for line in found:
            print(f"orphaned: {line}")
        current = record.render()
        if found:
            print("Before ending the turn, start, message, or recover an owner, or record a wait or decision.")
        return 0 if current and not found else 1
    state = record.load()
    before = copy.deepcopy(state)
    threads = read_owners(state, read_thread)
    notes = observe(state, at, read_pr, threads)
    set_next(state, args.next)
    if state != before:
        summary = "; ".join(notes[:3]) + (f"; {len(notes) - 3} more" if len(notes) > 3 else "")
        record.save(state, f"status: {summary or 'checked'}")
    for line in notes:
        print(f"note: {line}")
    groups = todo(state, at, threads, args.stale_hours)
    for name, rows in groups.items():
        for row in rows:
            print(f"{name}: {row}")
    if not groups:
        print("now: nothing waits on the chief")
    record.render()
    return 0


def main():
    args = arguments().parse_args()
    record = Record(args.state, args.page)
    try:
        if args.command == "status":
            return status(args, record)
        state = record.load()
        message, notes = event(args, state, now())
        set_next(state, args.next)
        record.save(state, message)
        for note in notes:
            print(f"note: {note}")
        record.render()
        return 1 if any(note.startswith("ask again") for note in notes) else 0
    except (Refused, OSError, ValueError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
