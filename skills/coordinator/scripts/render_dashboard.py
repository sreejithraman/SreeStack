#!/usr/bin/env python3
"""Check a program state file and render its command center."""

import argparse
from datetime import datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shlex
import subprocess
from urllib.parse import urlsplit


STATES = {
    "planned": "Planned", "building": "Building", "shown": "To try", "in-review": "In review",
    "ready": "Ready", "landed": "Landed", "done": "Done", "scrapped": "Scrapped", "unknown": "Unknown",
}
TERMINAL = {"landed", "done", "scrapped"}
ACTIVE = {"building", "shown", "in-review", "ready"}
PR_STATES = {"in-review", "ready"}
FINISH_LINES = {"land": "Land", "try": "Try", "pr-review": "Review-ready PR", "pr-draft": "Draft PR"}
READY_LABELS = {"land": "Ready to land", "pr-review": "Review-ready", "pr-draft": "Draft open"}
READY_LAYERS = {"land": ({"ready", "merged"}, "ready or merged"), "pr-review": ({"ready", "merged"}, "ready or merged"),
                "pr-draft": ({"draft", "merged"}, "a draft or merged")}
LAYER_STATES = {
    "local": "Local", "draft": "Draft", "open": "In review", "ready": "Ready",
    "merged": "Merged", "closed": "Closed without merge",
}
PHASES = ("start", "access", "proof", "acceptance", "landing")
HALTING = {"start", "access", "proof"}  # The others let building continue.
DAY = re.compile(r"\d{4}-\d{2}-\d{2}")
ENTRY = ("date", "source", "text")
START_MODES = ("top-level", "delegated", "adopted")
LANDING_STATES = ("released", "submitted", "cancelling", "landed", "withdrawn")
DECISION_STATES = ("open", "answered", "resolved", "withdrawn")
DISCOVERY_STATUSES = ("open", "routed")
DISCOVERY_IMPACTS = ("unrelated", "shared-contract", "requested-scope")
DISCOVERY_REPLIES = ("pending", "sent")
HISTORY = {"date", "source", "answerSource", "rationale", "applied", "stalePick", "picksRead"}  # Decision fields a copied answer never depends on.
PROGRAM_KEYS = ("title", "goal", "finishLine", "demo", "chief", "hosting", "next", "request", "grant", "corrections",
                "requirements", "approvals", "directions", "landingAuthority", "decisions", "work", "revisits",
                "discoveries", "landings", "waits")
GRANT = ("date", "source", "start", "resolve", "user")
DECISION_KEYS = ("id", "question", "date", "source", "status", "reopened", "context", "pictures", "meanwhile", "recommendation",
                 "options", "weight", "blocks", "links", "answer", "answerSource", "basis", "rationale", "applied", "stalePick", "picksRead")
OPTION_KEYS = ("label", "effect", "image", "recommended", "reversible")
PICTURE_SHAPES = {"side-by-side": (2, 3), "before-after": (2, 2), "sequence": (2, 8)}  # shape: (fewest, most) images
STALE_PICK = ("label", "revision", "at")
WORK_KEYS = ("id", "title", "repo", "kind", "state", "description", "scope", "sources", "tickets", "finishLine",
             "finishLineReason", "owner", "provisional", "layers", "results", "evidence", "acceptance", "blockedBy",
             "blocked", "unknownReason", "checkedAt", "required", "origin")
OWNER_KEYS = ("name", "session", "start", "route", "tasks", "workspace", "resources", "handled", "seen")
SEEN = ("running", "idle", "unknown")  # an owner thread as status last observed it
LAYER_KEYS = ("id", "branch", "status", "url", "head", "base", "stackedOn")
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "command-center.html"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")
IMAGE = re.compile(r"files/[0-9a-f]{16}(?:%s)" % "|".join(re.escape(suffix) for suffix in IMAGE_SUFFIXES))
ISO_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)")
# Reopening and replacing answers append these audit entries to rationale.
DECISION_HISTORY_ENTRY = re.compile(rf'{ISO_TIME.pattern}: (?:prior|replaced the earlier) (?:answered|resolved) answer "')


def text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a nonempty string")
    return value


def timestamp(value, path):
    text(value, path)
    try:
        if not ISO_TIME.fullmatch(value):
            raise ValueError
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{path} must be an ISO timestamp with a timezone, such as 2026-11-02T17:00:00Z") from None


def date(value, path):
    if isinstance(value, str) and DAY.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"{path} must be a date, such as 2026-11-02") from None
    else:
        timestamp(value, path)
    return value


def url(value, path):
    text(value, path)
    candidate = value[1:-1] if value.startswith("<") and value.endswith(">") else value
    parsed = urlsplit(candidate)
    if (parsed.scheme not in {"https", "http", "t3-thread"}
            or not parsed.netloc or any(c.isspace() for c in candidate)
            or any(ord(c) < 32 for c in candidate)):
        raise ValueError(f"{path} must be an http, https, or t3-thread URL")
    return candidate


def records(value, path):
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError(f"{path} must be a list of objects")
    return value


def strings(value, path):
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list of strings")
    for index, item in enumerate(value):
        text(item, f"{path}[{index}]")
    return value


def picture(value, path):
    """A picture committed in the program folder as files/<content name>."""
    if not (isinstance(value, str) and IMAGE.fullmatch(value)):
        raise ValueError(f"{path} must be files/ and its content name: the first 16 hex digits of its sha256 and one "
                         f"of {', '.join(IMAGE_SUFFIXES)}, such as files/0123456789abcdef.png")
    return value


def links(value, path):
    for index, item in enumerate(records(value, path)):
        known_keys(item, f"{path}[{index}]", ("label", "url"))
        text(item.get("label"), f"{path}[{index}].label")
        url(item.get("url"), f"{path}[{index}].url")


def obj(value, path):
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    return value


def known_keys(row, path, keys):
    for key in row:
        if key not in keys:
            raise ValueError(f"{path}.{key} is not a known field" if path else f"{key} is not a known field")
    return row


def fields(row, path, required=(), optional=()):
    for key in (*required, *(key for key in optional if key in row)):
        (date if key == "date" else text)(row.get(key), f"{path}.{key}" if path else key)
    return row


def unique_ids(rows, path):
    ids = [text(row.get("id"), f"{path}[{index}].id") for index, row in enumerate(rows)]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path} contains duplicate IDs")


def one_of(value, choices, path):
    text(value, path)
    if value not in choices:
        raise ValueError(f"{path} must be one of {', '.join(choices)}")
    return value


def effective_finish(row):
    """Provisional work never merges, so its Land becomes Try."""
    return "try" if "provisional" in row and row.get("finishLine") == "land" else row.get("finishLine")


def owner_name(row):
    return row.get("owner", {}).get("name")


def owned_by_another(row, other):
    return not (owner_name(row) and owner_name(row) == owner_name(other))


def validate_layers(row, path, layers):
    for index, layer in enumerate(records(row.get("layers", []), f"{path}.layers")):
        identity = text(layer.get("id"), f"{path}.layers[{index}].id")
        where = f"{path}.layers[{identity}]"
        known_keys(layer, where, LAYER_KEYS)
        if identity in layers:
            raise ValueError(f"layer {identity} appears more than once; layer IDs are unique across the program")
        layers[identity] = (layer, row)
        text(layer.get("branch"), f"{where}.branch")
        status = one_of(layer.get("status"), LAYER_STATES, f"{where}.status")
        if (status == "local") == ("url" in layer):
            raise ValueError(f"{where}: a local layer has no url, and a published layer needs its PR url")
        if "url" in layer:
            url(layer["url"], f"{where}.url")
        for key in ("head", "base", "stackedOn"):
            if key in layer:
                text(layer[key], f"{where}.{key}")
        if status == "merged" and "provisional" in row:
            raise ValueError(f"{where}: provisional work never merges; clear the condition before recording a merge")


def validate_owner(owner, path):
    known_keys(obj(owner, path), path, OWNER_KEYS)
    fields(owner, path, ("name", "route"), ("workspace", "resources"))
    one_of(owner.get("start"), START_MODES, f"{path}.start")
    if "session" in owner:
        url(owner["session"], f"{path}.session")
    for key in ("tasks", "handled"):
        strings(owner.get(key, []), f"{path}.{key}")
    if "seen" in owner:
        seen = known_keys(obj(owner["seen"], f"{path}.seen"), f"{path}.seen", ("state", "at", "approvals"))
        one_of(seen.get("state"), SEEN, f"{path}.seen.state")
        timestamp(seen.get("at"), f"{path}.seen.at")
        if "approvals" in seen and not (type(seen["approvals"]) is int and seen["approvals"] > 0):
            raise ValueError(f"{path}.seen.approvals must be a positive count")


def validate_work(row, layers):
    path = f"work[{row['id']}]"
    known_keys(row, path, WORK_KEYS)
    for key in ("title", "repo"):
        text(row.get(key), f"{path}.{key}")
    state = one_of(row.get("state"), STATES, f"{path}.state")
    kind = one_of(row.get("kind"), ("outcome", "follow-up", "support"), f"{path}.kind")
    timestamp(row.get("checkedAt"), f"{path}.checkedAt")
    fields(row, path, (), ("description", "scope", "finishLineReason", "acceptance", "blocked", "origin", "unknownReason"))
    strings(row.get("sources", []), f"{path}.sources")
    if "owner" in row:
        validate_owner(row["owner"], f"{path}.owner")
    if "unknownReason" in row and state != "unknown":
        raise ValueError(f"{path}.unknownReason applies only to unknown state")
    for key in ("tickets", "evidence"):
        links(row.get(key, []), f"{path}.{key}")
    for index, result in enumerate(records(row.get("results", []), f"{path}.results")):
        known_keys(result, f"{path}.results[{index}]", ("label", "url", "access", "image"))
        text(result.get("label"), f"{path}.results[{index}].label")
        url(result.get("url"), f"{path}.results[{index}].url")
        if "access" in result:
            text(result["access"], f"{path}.results[{index}].access")
        if "image" in result:
            picture(result["image"], f"{path}.results[{index}].image")
    if "required" in row and not isinstance(row["required"], bool):
        raise ValueError(f"{path}.required must be a boolean")
    if state in TERMINAL and (row.get("blockedBy") or row.get("blocked")):
        raise ValueError(f"{path}: terminal work cannot retain active blockers; keep their history in decisions or discoveries")
    if state in ACTIVE and "owner" not in row:
        raise ValueError(f"{path}: {state} work needs its owner")

    if kind == "support":
        for key in ("finishLine", "layers", "provisional"):
            if key in row:
                raise ValueError(f"{path}.{key}: support work has no finish line or layers; give a repository change its own outcome")
        if state not in {"planned", "building", "done", "scrapped", "unknown"}:
            raise ValueError(f"{path}: support work uses planned, building, done, scrapped, or unknown")
        return
    finish = one_of(row.get("finishLine"), FINISH_LINES, f"{path}.finishLine")
    if state == "done":
        raise ValueError(f"{path}: an outcome ends landed, at its shown Try, or at its PR state, not done")
    if "provisional" in row:
        provisional = known_keys(obj(row["provisional"], f"{path}.provisional"), f"{path}.provisional", ("basis", "clears", "on"))
        for key in ("basis", "clears"):
            text(provisional.get(key), f"{path}.provisional.{key}")
        strings(provisional.get("on", []), f"{path}.provisional.on")
    validate_layers(row, path, layers)
    effective = effective_finish(row)
    published = [layer for layer in row.get("layers", []) if "url" in layer]
    if finish == "try" and published:
        raise ValueError(f"{path}: Try stops before the PR; a published layer needs a PR or Land finish line")
    if state == "ready":
        if "provisional" in row and effective not in {"pr-draft", "pr-review"}:
            raise ValueError(f"{path}: provisional work is never ready; keep it in review until its condition clears")
        allowed, wording = READY_LAYERS[effective]
        if not row.get("layers") or any(layer["status"] not in allowed for layer in row["layers"]):
            raise ValueError(f"{path}: ready needs every layer {wording} for its finish line")
    if state == "shown" and (effective != "try" or not row.get("results")):
        raise ValueError(f"{path}: shown is a Try result, and needs results the user can open")
    if state in PR_STATES and not published:
        raise ValueError(f"{path}: {state} needs a published layer")
    if state == "landed" and (effective != "land" or not row.get("layers")
                              or any(layer["status"] != "merged" for layer in row["layers"])):
        raise ValueError(f"{path}: landed needs a Land finish line and every layer merged")


def held(decisions):
    """IDs of work an open decision holds at a phase that stops its work."""
    return {entry["id"] for decision in decisions if decision["status"] == "open"
            for entry in decision.get("blocks", []) if entry["phase"] in HALTING}


LIVE_LAYERS = {"local", "draft", "open", "ready"}


def dead_base(row):
    """Why work can no longer rest on this outcome: it was scrapped, or every layer closed before it landed."""
    if row["state"] == "scrapped":
        return "scrapped"
    layers = row.get("layers", [])
    if row["state"] != "landed" and layers and all(layer["status"] == "closed" for layer in layers):
        return "closed"
    return None


def bases(row, layers):
    """Outcomes this active work rests on, through provisional.on or an active stack edge."""
    if row["state"] in TERMINAL:
        return []
    found = list(row.get("provisional", {}).get("on", []))
    found += [layers[layer["stackedOn"]][1]["id"] for layer in row.get("layers", [])
              if "stackedOn" in layer and layer["status"] in LIVE_LAYERS]
    return [identity for identity in dict.fromkeys(found) if identity != row["id"]]


def invalid_base_work(work, by_id, layers):
    """Non-terminal work IDs resting on a dead base or an individually closed parent layer: {work_id: message}."""
    broken = {}
    for identity, (layer, row) in layers.items():
        if row["state"] in TERMINAL or "stackedOn" not in layer:
            continue
        parent, parent_row = layers[layer["stackedOn"]]
        if layer["status"] in LIVE_LAYERS and parent["status"] == "closed" and not dead_base(parent_row):
            broken.setdefault(
                row["id"],
                f"work[{row['id']}].layers[{identity}].stackedOn names closed {parent['id']}; "
                "record the restack or halt it with its decision",
            )
    for row in work:
        if row["state"] in TERMINAL:
            continue
        for identity in bases(row, layers):
            reason = dead_base(by_id[identity])
            if reason:
                broken.setdefault(
                    row["id"],
                    f"work[{row['id']}] rests on {reason} {identity}; "
                    "halt it with its scrap-or-rebase decision or record its new base",
                )
    return broken


def validate_edges(work, by_id, layers, halted):
    for row in work:
        path = f"work[{row['id']}]"
        for dependency in strings(row.get("blockedBy", []), f"{path}.blockedBy"):
            if dependency not in by_id:
                raise ValueError(f"{path}.blockedBy references missing work {dependency}")
        for identity in row.get("provisional", {}).get("on", []):
            if identity == row["id"] or identity not in by_id:
                raise ValueError(f"{path}.provisional.on must name other work; a decision names what it blocks")
    branches = {}
    for identity, (layer, row) in layers.items():
        branches.setdefault((row["repo"], layer["branch"]), []).append(identity)
    for identity, (layer, row) in layers.items():
        where = f"work[{row['id']}].layers[{identity}].stackedOn"
        if "stackedOn" in layer and (layer["stackedOn"] == identity or layer["stackedOn"] not in layers):
            raise ValueError(f"{where} must name another layer")
        below = [other for other in branches.get((row["repo"], layer.get("base")), []) if other != identity]
        if layer["status"] in LIVE_LAYERS and below and layer.get("stackedOn") not in below:
            raise ValueError(f"work[{row['id']}].layers[{identity}].base is {below[0]}'s branch; name {below[0]} in stackedOn")
        if "stackedOn" not in layer:
            continue
        parent, parent_row = layers[layer["stackedOn"]]
        if row["state"] not in TERMINAL and parent_row["repo"] != row["repo"]:
            raise ValueError(f"{where}: cannot stack {row['id']} ({row['repo']}) on {parent['id']} in {parent_row['repo']}")
        if (parent_row is not row and parent["status"] != "merged" and row["state"] not in TERMINAL
                and owned_by_another(row, parent_row)
                and parent_row["id"] not in row.get("provisional", {}).get("on", [])):
            raise ValueError(f"{where}: {parent['id']} is another owner's unmerged layer; mark this outcome provisional on {parent_row['id']}")
    for identity, message in invalid_base_work(work, by_id, layers).items():
        if identity not in halted:
            raise ValueError(message)

    def depends_on(row):
        found = list(row.get("blockedBy", []))
        found += row.get("provisional", {}).get("on", [])
        parents = [layers[layer["stackedOn"]][1] for layer in row.get("layers", []) if "stackedOn" in layer]
        return found + [parent["id"] for parent in parents if parent is not row]

    check_cycles({identity: depends_on(row) for identity, row in by_id.items()}, "work dependency")
    check_cycles({identity: [layer["stackedOn"]] if "stackedOn" in layer else [] for identity, (layer, _) in layers.items()}, "stack")


def check_cycles(graph, name):
    visiting, visited = set(), set()

    def visit(identity):
        if identity in visiting:
            raise ValueError(f"{name} cycle includes {identity}")
        if identity in visited:
            return
        visiting.add(identity)
        for neighbour in graph[identity]:
            visit(neighbour)
        visiting.remove(identity)
        visited.add(identity)

    for identity in graph:
        visit(identity)


def validate_decision(row, by_id):
    path = f"decisions[{row['id']}]"
    known_keys(row, path, DECISION_KEYS)
    fields(row, path, ("question", "date", "source"), ("recommendation", "meanwhile", "answer", "rationale"))
    status = one_of(row.get("status"), DECISION_STATES, f"{path}.status")
    if status in {"answered", "resolved"}:
        text(row.get("answer"), f"{path}.answer")
    for key, owner in (("answerSource", "answered"), ("basis", "resolved")):
        if status == owner:
            text(row.get(key), f"{path}.{key}")
        elif key in row:
            raise ValueError(f"{path}.{key} applies only to {owner} decisions")
    if status == "withdrawn":
        text(row.get("rationale"), f"{path}.rationale")
    if "applied" in row and (row["applied"] is not False or status not in {"answered", "resolved"}):
        raise ValueError(f"{path}.applied is false on an answer not yet passed to its owners, and absent otherwise")
    if "reopened" in row and (type(row["reopened"]) is not int or row["reopened"] < 1):
        raise ValueError(f"{path}.reopened must be a positive integer")
    if row.get("weight", "judgment") not in {"quick", "judgment"}:
        raise ValueError(f"{path}.weight must be quick or judgment")
    strings(row.get("context", []), f"{path}.context")
    blocked = set()
    for index, entry in enumerate(records(row.get("blocks", []), f"{path}.blocks")):
        known_keys(entry, f"{path}.blocks[{index}]", ("id", "phase"))
        identity = text(entry.get("id"), f"{path}.blocks[{index}].id")
        phase = one_of(entry.get("phase"), PHASES, f"{path}.blocks[{index}].phase")
        if identity not in by_id:
            raise ValueError(f"{path}.blocks references missing work {identity}")
        if identity in blocked:
            raise ValueError(f"{path}.blocks names {identity} twice; record the earliest phase it blocks")
        blocked.add(identity)
        if status == "open" and by_id[identity]["state"] in TERMINAL:
            raise ValueError(f"{path}: an open decision cannot block terminal work")
        if status == "open" and phase == "start" and by_id[identity]["state"] != "planned":
            raise ValueError(f"{path}: {identity} has started; record the phase this decision blocks now")
    if "pictures" in row:
        validate_pictures(row["pictures"], f"{path}.pictures")
    if "stalePick" in row:
        stale = fields(known_keys(obj(row["stalePick"], f"{path}.stalePick"), f"{path}.stalePick", STALE_PICK),
                       f"{path}.stalePick", STALE_PICK)
        timestamp(stale["at"], f"{path}.stalePick.at")
    if "picksRead" in row and not (isinstance(row["picksRead"], list) and row["picksRead"]
                                   and all(isinstance(read, str) and read.strip() for read in row["picksRead"])):
        raise ValueError(f"{path}.picksRead must list the stored picks read, such as \"picks/<id> (version 1) 2026-11-02T18:00:00Z\"")
    for index, option in enumerate(records(row.get("options", []), f"{path}.options")):
        known_keys(option, f"{path}.options[{index}]", OPTION_KEYS)
        for key in ("label", "effect"):
            text(option.get(key), f"{path}.options.{key}")
        if "image" in option:
            picture(option["image"], f"{path}.options[{index}].image")
        for flag in ("recommended", "reversible"):
            if flag in option and not isinstance(option[flag], bool):
                raise ValueError(f"{path}.options.{flag} must be a boolean")
    recommended = sum(option.get("recommended", False) for option in row.get("options", []))
    if recommended > 1:
        raise ValueError(f"{path}: only one option can be recommended")
    if row.get("options") and row.get("recommendation") and not recommended:
        raise ValueError(f"{path}: mark the recommended option to attach its recommendation")
    if row.get("weight") == "quick" and (len(row.get("options", [])) < 2 or not recommended):
        raise ValueError(f"{path}: quick needs at least two options with one recommended")
    links(row.get("links", []), f"{path}.links")


def validate_pictures(value, path):
    pictures = known_keys(obj(value, path), path, ("shape", "images"))
    images = records(pictures.get("images"), f"{path}.images")
    for index, item in enumerate(images):
        known_keys(item, f"{path}.images[{index}]", ("image", "caption"))
        picture(item.get("image"), f"{path}.images[{index}].image")
        if "caption" in item:
            text(item["caption"], f"{path}.images[{index}].caption")
    if "shape" in pictures:
        fewest, most = PICTURE_SHAPES[one_of(pictures["shape"], PICTURE_SHAPES, f"{path}.shape")]
        if not fewest <= len(images) <= most:
            raise ValueError(f"{path}: {pictures['shape']} takes {fewest} to {most} images" if fewest != most
                             else f"{path}: {pictures['shape']} takes exactly {fewest} images")
    elif not 1 <= len(images) <= PICTURE_SHAPES["sequence"][1]:
        raise ValueError(f"{path} needs 1 to {PICTURE_SHAPES['sequence'][1]} images")


def validate_landing(row, by_id):
    path = f"landings[{row['id']}]"
    known_keys(row, path, ("id", "date", "chief", "lander", "target", "work", "prs", "state", "keep", "note"))
    fields(row, path, ("date", "chief", "lander", "target"), ("keep", "note"))
    one_of(row.get("state"), LANDING_STATES, f"{path}.state")
    if not row.get("work") or not row.get("prs"):
        raise ValueError(f"{path} needs its work and PRs")
    for identity in strings(row["work"], f"{path}.work"):
        known(identity, f"{path}.work", by_id)
    for index, pr in enumerate(records(row["prs"], f"{path}.prs")):
        known_keys(pr, f"{path}.prs[{index}]", ("url", "head", "base"))
        url(pr.get("url"), f"{path}.prs[{index}].url")
        fields(pr, f"{path}.prs[{index}]", ("head", "base"))


def known(identity, path, by_id):
    if identity not in by_id:
        raise ValueError(f"{path} names missing work {identity}")


def validate(state):
    known_keys(obj(state, "program"), "", PROGRAM_KEYS)
    fields(state, "", ("title", "goal", "chief", "next"), ("finishLine",))
    if "demo" in state and not isinstance(state["demo"], bool):
        raise ValueError("demo must be a boolean")
    if "hosting" in state:
        url(state["hosting"], "hosting")
    request = fields(known_keys(obj(state.get("request"), "request"), "request", ("text", "sources")), "request", ("text",))
    strings(request.get("sources", []), "request.sources")
    if "landingAuthority" in state:
        fields(known_keys(obj(state["landingAuthority"], "landingAuthority"), "landingAuthority", ENTRY), "landingAuthority", ENTRY)
    if "grant" in state:
        fields(known_keys(obj(state["grant"], "grant"), "grant", (*GRANT, "heartbeat", "wake")), "grant", GRANT, ("heartbeat", "wake"))

    work = records(state.get("work"), "work")
    decisions = records(state.get("decisions"), "decisions")
    for name in ("work", "decisions", "revisits", "approvals", "landings"):
        unique_ids(records(state.get(name, []), name), name)
    by_id = {row["id"]: row for row in work}
    layers = {}
    for row in work:
        validate_work(row, layers)
    for row in decisions:
        validate_decision(row, by_id)
    validate_edges(work, by_id, layers, held(decisions))
    for row in state.get("revisits", []):
        known_keys(row, f"revisits[{row['id']}]", ("id", "title", "tradeoff", "revisit", "source"))
        fields(row, f"revisits[{row['id']}]", ("title", "tradeoff", "revisit"), ("source",))
    for name, required, optional in (
        ("corrections", ENTRY, ()), ("requirements", ENTRY, ()),
        ("approvals", (*ENTRY, "id", "covers", "picks"), ()), ("directions", ENTRY, ("until",)),
        ("waits", ("date", "on", "event"), ("work",)),
        ("discoveries", ("date", "origin", "text", "route"), ("id", "work", "impact", "evidence", "thread", "reply", "status")),
    ):
        for index, row in enumerate(records(state.get(name, []), name)):
            known_keys(row, f"{name}[{index}]", (*required, *optional))
            fields(row, f"{name}[{index}]", required, optional)
            if "work" in row:
                known(row["work"], f"{name}[{index}].work", by_id)
            if name == "discoveries":
                if "status" in row:
                    one_of(row["status"], DISCOVERY_STATUSES, f"discoveries[{index}].status")
                    if row["status"] == "open":
                        text(row.get("id"), f"discoveries[{index}].id")
                if "impact" in row:
                    one_of(row["impact"], DISCOVERY_IMPACTS, f"discoveries[{index}].impact")
                if "reply" in row:
                    one_of(row["reply"], DISCOVERY_REPLIES, f"discoveries[{index}].reply")
                    if row["reply"] == "pending":
                        text(row.get("id"), f"discoveries[{index}].id")
                        text(row.get("thread"), f"discoveries[{index}].thread")
    discovery_ids = [row["id"] for row in state.get("discoveries", []) if "id" in row]
    if len(discovery_ids) != len(set(discovery_ids)):
        raise ValueError("discoveries contain duplicate ids")
    for row in state.get("landings", []):
        validate_landing(row, by_id)
    return state


# Program verdict: what status prints, derived from the record and each owner thread's facts.

SATISFIED = {"landed", "done"}
PENDING_LANDINGS = {"released", "submitted", "cancelling"}
LIVE_THREADS = {"running", "waiting"}  # waiting: on its own helpers
STALE_HOURS = 2


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00") if "T" in value else value + "T00:00:00+00:00")


def age(since, at):
    minutes = max(0, int((parse_time(at) - parse_time(since)).total_seconds() // 60))
    days, minutes = divmod(minutes, 1440)
    hours, minutes = divmod(minutes, 60)
    return f"{days}d{hours}h" if days else f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"

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

def live(thread):
    return isinstance(thread, dict) and thread.get("status") in LIVE_THREADS


UNOBSERVED = {"status": "not observed yet"}  # an owner session that status has not read yet


def observation(thread, at):
    """What status records of an owner thread read at a time: its facts, or the error string from a failed read."""
    state = "running" if live(thread) else "unknown" if isinstance(thread, str) else "idle"
    approvals = thread.get("pendingRequestCount", 0) if isinstance(thread, dict) else 0
    return {"state": state, "at": at} | ({"approvals": approvals} if approvals else {})


def recorded_threads(state):
    """The owner thread facts status last recorded, in the form assess reads them live."""
    threads = {}
    for row in state["work"]:
        owner = row.get("owner", {})
        if row["state"] in TERMINAL or "session" not in owner:
            continue
        seen = owner.get("seen")
        threads[row["id"]] = (UNOBSERVED if not seen else "its thread could not be read" if seen["state"] == "unknown"
                              else {"status": seen["state"], "pendingRequestCount": seen.get("approvals", 0)})
    return threads


def orphans(state, threads):
    """Open work with no live owner, recorded wait, holding Need, or blocker."""
    return [f"{identity} ({current}): {why}" for identity, current, why, _ in orphaned(state, threads)]


def orphaned(state, threads):
    waits = {row.get("work") for row in state.get("waits", [])}
    found = []
    for row in state["work"]:
        proposed = row["state"] == "planned" and row.get("required") is False
        at_pr_state = row["state"] == "ready" and effective_finish(row) != "land"  # stopped for the user
        if row["state"] in TERMINAL or proposed or at_pr_state:
            continue
        if (live(threads.get(row["id"])) or threads.get(row["id"]) is UNOBSERVED or row["id"] in waits or waits_on_need(state, row)
                or unsatisfied(state, row) or row.get("blocked")):
            continue
        thread = threads.get(row["id"])
        landing = pending_landing(state, row["id"])
        why = ("not started" if row["state"] == "planned"
               else "ready with no landing release" if row["state"] == "ready" and not landing
               else "owner thread could not be read" if isinstance(thread, str) else f"owner {thread['status']}" if thread
               else "owner has no session to read" if "owner" in row else "no owner")
        if landing:
            why += f" with landing {landing['id']} {landing['state']}"
        found.append((row["id"], row["state"], why, thread if isinstance(thread, str) else None))
    return found

def item(kind, identity, text, since=None, detail=None):
    """One status line; since and detail stay out of the digest."""
    return ({"kind": kind, "id": identity, "text": text} | ({"since": since} if since else {})
            | ({"detail": detail} if detail else {}))


def names(text, identity):
    return re.search(rf"(?<![\w-]){re.escape(identity)}(?![\w-])", text) is not None


def reversible(decision):
    return any(option.get("recommended") and option.get("reversible") for option in decision.get("options", []))


def reversible_halts(state):
    """Open Needs whose recommended option is reversible and halts startable work not yet built on it.

    Work qualifies only when every Need that halts it is reversible, so building on the recommendations
    is all it still lacks.
    """
    found, halts = [], {}
    by_id = {row["id"]: row for row in state["work"]}
    for decision in state["decisions"]:
        if decision["status"] == "open":
            for entry in decision.get("blocks", []):
                if entry["phase"] in HALTING:
                    halts.setdefault(entry["id"], []).append(decision)
    for decision in state["decisions"]:
        if decision["status"] != "open" or not reversible(decision):
            continue
        for entry in decision.get("blocks", []):
            row = by_id[entry["id"]]
            provisional = row.get("provisional", {})
            on_it = names(f"{provisional.get('basis', '')} {provisional.get('clears', '')}", decision["id"])
            startable = (row.get("required") is not False and not unsatisfied(state, row) and not row.get("blocked")
                         and all(reversible(other) for other in halts.get(row["id"], [])))
            if entry["phase"] in HALTING and row["state"] not in TERMINAL and startable and not on_it:
                found.append(item("provisional start", row["id"],
                                  f"build on {decision['id']}'s recommended option provisionally; it halts {entry['phase']}"))
    return found


def at_stop(row):
    """Terminal, or stopped for the user at its finish line."""
    return (row["state"] in TERMINAL or row["state"] == "shown"
            or (row["state"] == "ready" and effective_finish(row) != "land")
            or (row["state"] == "planned" and row.get("required") is False))


def assess(state, at, threads, stale_hours=STALE_HOURS):
    """The program verdict and the items behind it."""
    waits = {row.get("work") for row in state.get("waits", [])}
    runnable, working, waiting, attention = [], [], [], []
    for row in state["work"]:
        identity, current = row["id"], row["state"]
        if current in TERMINAL:
            continue
        thread = threads.get(identity)
        if live(thread):
            working.append(item("running", identity, f"{row['owner']['name']} is working", detail=thread["status"]))
        if (current == "planned" and row.get("required") is not False and not unsatisfied(state, row)
                and not row.get("blocked") and not open_blocks(state, identity, HALTING)):
            runnable.append(item("start", identity, row["title"]))
        if (current == "ready" and effective_finish(row) == "land" and not open_blocks(state, identity)
                and not unsatisfied(state, row) and not row.get("blocked") and not pending_landing(state, identity)):
            runnable.append(item("release", identity, row["title"]))
        owes = current in {"building", "in-review"} or (current == "ready" and pending_landing(state, identity))
        covered = identity in waits or waits_on_need(state, row) or unsatisfied(state, row) or row.get("blocked")
        if owes and not live(thread) and thread is not UNOBSERVED and not covered:
            if isinstance(thread, dict):
                runnable.append(item("idle owner", identity, f"{row['owner']['name']} is {thread['status']} with no recorded wait",
                                     thread.get("updatedAt")))
            elif thread:
                runnable.append(item("idle owner", identity, f"{row['owner']['name']}'s thread could not be read", detail=thread))
            else:
                runnable.append(item("idle owner", identity, f"{row['owner']['name']} has no session to read"))
        if isinstance(thread, dict) and thread.get("pendingRequestCount"):
            attention.append(item("approval", identity, f"{row['owner']['name']} waits on an approval in its thread"))
        if row.get("blocked"):
            waiting.append(item("blocked", identity, row["blocked"]))
        if not at_stop(row) and (needs := unsatisfied(state, row)):
            waiting.append(item("dependency", identity, f"needs {', '.join(needs)}"))
        if (parse_time(at) - parse_time(row["checkedAt"])).total_seconds() > stale_hours * 3600:
            attention.append(item("stale", identity, "not observed recently", row["checkedAt"]))
    runnable += reversible_halts(state)
    listed = {entry["id"] for entry in runnable}
    runnable += [item("orphan", identity, f"({current}) {why}", detail=detail)
                 for identity, current, why, detail in orphaned(state, threads) if identity not in listed]
    for decision in state["decisions"]:
        if decision["status"] in {"answered", "resolved"} and "stalePick" in decision:
            runnable.append(item("reopen request", decision["id"],
                                 f"the user picked {quoted(decision['stalePick']['label'])} after it was {decision['status']}; "
                                 "reopen it under references/decisions.md#reopen"))
        if decision["status"] == "open":
            waiting.append(item("need", decision["id"], decision["question"], decision["date"]))
        elif decision.get("applied") is False:
            affected = ", ".join(entry["id"] for entry in decision.get("blocks", [])) or "the owners it affects"
            runnable.append(item("apply answer", decision["id"], f"pass {'the user' + chr(39) + 's answer' if decision['status'] == 'answered' else 'your call'} to {affected}, then run applied"))
    for discovery in state.get("discoveries", []):
        if discovery.get("status") == "open":
            impact = f"[{discovery['impact']}] " if discovery.get("impact") else ""
            runnable.append(item("route discovery", discovery["id"], f"{impact}{discovery['text']}", discovery["date"]))
        elif discovery.get("status") == "routed" and discovery.get("reply") == "pending":
            target = discovery.get("work") or "PR owner"
            runnable.append(item(
                "send deferred reply", discovery["id"],
                f"send recorded route ({discovery['route']}) to {target} for thread {discovery['thread']}, then run discovery --reply-sent",
                discovery["date"],
            ))
    open_rows = {row["id"] for row in state["work"] if row["state"] not in TERMINAL}
    for wait in state.get("waits", []):
        if wait.get("work", "program") in open_rows | {"program"}:
            waiting.append(item("wait", wait.get("work", "program"), f"{wait['on']} until {wait['event']}", wait["date"]))
    done = all(at_stop(row) for row in state["work"]) and not waiting
    verdict = "runnable" if runnable else "working" if working else "done" if done else "waiting"
    rows = [[row["id"], row["state"], [[layer["id"], layer["status"], layer.get("head"), layer.get("base")]
                                       for layer in row.get("layers", [])]]
            for row in state["work"] if row["id"] in open_rows]
    facts = [{key: value for key, value in entry.items() if key not in {"since", "detail"}}
             for entry in (*runnable, *working, *waiting, *(entry for entry in attention if entry["kind"] != "stale"))]
    digest = hashlib.sha256(json.dumps([verdict, facts, rows], sort_keys=True).encode()).hexdigest()[:12]
    for entry in (*runnable, *working, *waiting, *attention):
        if "since" in entry:
            entry["age"] = age(entry["since"], at)
    return {"verdict": verdict, "digest": digest, "runnable": runnable, "working": working, "waiting": waiting,
            "attention": attention}


STAGE_ORDER = ("planned", "building", "shown", "in-review", "landed", "done", "unknown", "scrapped")
ICONS = {
    "planned": "circle-dashed", "building": "hammer", "shown": "hand", "in-review": "scan-eye",
    "ready": "circle-check", "landed": "git-merge", "done": "check-check",
    "scrapped": "ban", "unknown": "circle-question-mark", "provisional": "git-branch",
    "blocked": "triangle-alert", "waits": "hourglass", "copy": "copy", "copied": "check",
    "decision": "message-circle-question-mark", "quick": "zap", "resolved": "badge-check", "reopen": "rotate-ccw",
    "recommended": "star", "pr": "git-pull-request", "finish": "flag", "record": "git-commit-horizontal",
    "tradeoff": "scale", "result": "external-link", "asked": "clock", "next": "arrow-right", "finished": "archive",
    "runnable": "play", "working": "activity", "waiting": "hourglass", "enlarge": "maximize-2", "send": "send",
    "wake": "bell-ring", "stale": "history",
}


def e(value):
    return escape(str(value), quote=True)


def anchor(target, content, cls=""):
    attribute = f' class="{cls}"' if cls else ""
    return f'<a{attribute} href="{e(url(target, "link"))}" target="_blank" rel="noopener noreferrer">{content}</a>'


def link(label, target, cls="", icon_name=None):
    return anchor(target, (icon(icon_name) if icon_name else "") + e(label), cls)


def link_list(rows):
    return '<p class="links">' + "".join(link(row["label"], row["url"]) for row in rows) + "</p>" if rows else ""


def icon(name):
    return f'<i class="icon" data-lucide="{ICONS[name]}" aria-hidden="true"></i>'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def hexed(identity):
    return identity.encode().hex()


def when(value, form=""):
    """A time the page shows in local time; form "age" adds how long ago, and "relative" shows only that."""
    return f'<time datetime="{e(value)}"{f" data-{form}" if form else ""}>{e(value)}</time>'


def prose(value):
    """Escaped text whose ISO timestamps become time elements, so the page shows them in local time."""
    return ISO_TIME.sub(lambda match: when(match[0]), e(value))


STAMP = re.compile(r'<span id="record-stamp">.*?</span>')


def record_stamp(commit, at):
    return f'<span id="record-stamp"><code>{e(commit)}</code> · {when(at, "age")}</span>'


def quoted(value):
    return json.dumps(" ".join(value.split()), ensure_ascii=False)


def revision(decision):
    """Digest of the decision content a copied choice answers."""
    return digest(json.dumps({key: value for key, value in decision.items() if key not in HISTORY}, sort_keys=True))[:10]


def display_stage(row):
    """The stage a row reads under; a ready outcome stays in review and adds a readiness badge."""
    return "in-review" if row["state"] == "ready" else row["state"]


def collapsible(heading_id, title, count, body, *, level=2, state="", mark="", alert="", closed=False):
    """A section whose heading stays visible, and whose count stays readable, when collapsed."""
    return (
        f'<section class="collapsible{" " + state if state else ""}" aria-labelledby="{heading_id}"><details{"" if closed else " open"}>'
        f'<summary class="section-toggle" id="toggle-{heading_id}"><h{level} id="{heading_id}" class="section-title">{mark}{e(title)} <span class="count">{count}</span>{alert}</h{level}></summary>'
        f"{body}</details></section>"
    )


def decision_prompt(row, state, action):
    return (
        f'Decision {json.dumps(row["id"], ensure_ascii=False)} (revision {revision(row)}) in {quoted(state["title"])}\n'
        f'Question: {quoted(row["question"])}\n'
        f'{action}'
    )


def copy_control(prompt, status_id, aria_label, idle, mark="copy"):
    return (
        f'<button type="button" class="copy-prompt" data-prompt="{e(prompt)}"{"" if prompt else " disabled"} '
        f'aria-label="{e(aria_label)}" aria-describedby="{e(status_id)}">'
        f'<span class="idle">{icon(mark)}{e(idle)}</span><span class="done">{icon("copied")}Copied</span></button>'
        f'<span class="copy-status" id="{e(status_id)}" role="status"></span>'
        f'<textarea class="manual-prompt" aria-label="{e("Prompt: " + aria_label)}" readonly hidden></textarea>'
    )


def choice_prompt(row, state, index):
    return decision_prompt(row, state, f'I choose option {index + 1}: {quoted(row["options"][index]["label"])}')


def picture_button(image, group, name, caption):
    """A thumbnail that opens its picture larger inside the page; pictures in one group page through together."""
    return (
        f'<button type="button" class="picture" data-group="{e(group)}" data-caption="{e(caption)}" aria-label="{e("Enlarge " + name)}">'
        f'<img src="{e(image)}" alt="" loading="lazy">{icon("enlarge")}</button>'
    )


def shape_of(pictures):
    count = len(pictures["images"])
    return pictures.get("shape") or ("single" if count == 1 else "side-by-side" if count <= 3 else "sequence")


def pictures_view(row):
    """A decision's pictures: one, a side-by-side, a before and after, or a numbered sequence strip."""
    if "pictures" not in row:
        return ""
    shape, images, group = shape_of(row["pictures"]), row["pictures"]["images"], f'pictures-{hexed(row["id"])}'
    figures = ""
    for index, item in enumerate(images):
        caption = item.get("caption") or (("Before", "After")[index] if shape == "before-after" else "")
        step = f"Step {index + 1}" if shape == "sequence" else ""
        title = ": ".join(part for part in (step, caption) if part)
        legend = (f'<span class="step">{index + 1}</span>' if step else "") + e(caption)
        name = title or f"picture {index + 1} for {row['id']}"
        figures += (f'<figure>{picture_button(item["image"], group, name, title)}'
                    + (f"<figcaption>{legend}</figcaption>" if legend else "") + "</figure>")
    return f'<div class="pictures {shape}" role="group" aria-label="{e(PICTURE_LABELS[shape])}">{figures}</div>'


PICTURE_LABELS = {"single": "Picture", "side-by-side": "Pictures side by side", "before-after": "Before and after",
                  "sequence": "Sequence"}


def pick(row, option, index, state):
    recommended = option.get("recommended", False)
    content = (
        f'<div class="pick"><label class="pick-choice"><input type="radio" name="pick-{hexed(row["id"])}" autocomplete="off" '
        f'value="{index + 1}" data-prompt="{e(choice_prompt(row, state, index))}" data-label="{e(option["label"])}"'
        f'{" checked" if recommended else ""}><span class="pick-body"><span class="pick-heading"><strong>{e(option["label"])}</strong>'
    )
    if recommended:
        content += f'<span class="recommended-label">{icon("recommended")}Recommended</span>'
    content += f'</span><span class="pick-effect">{prose(option["effect"])}</span>'
    if recommended and row.get("recommendation"):
        content += f'<span class="pick-rationale">{prose(row["recommendation"])}</span>'
    content += "</span></label>"
    if "image" in option:
        content += picture_button(option["image"], f'options-{hexed(row["id"])}', f'option {index + 1}: {option["label"]}', option["label"])
    return content + "</div>"


def send_control(row, picked):
    """Tap-to-answer: hidden until the page's database and the coordinator's wake link are available."""
    status_id = f'send-{hexed(row["id"])}'
    return (
        f'<button type="button" class="send-answer" aria-describedby="{status_id}"{"" if picked else " disabled"} hidden>{icon("send")}Send answer</button>'
        f'<a class="wake-link" target="_blank" rel="noopener noreferrer" hidden>{icon("wake")}Wake the coordinator</a>'
        f'<span class="send-status" id="{status_id}" role="status"></span>'
    )


def picks(row, state):
    """The options as one pick list, with one action that sends the pick or copies its prompt."""
    chosen = next((index for index, option in enumerate(row["options"]) if option.get("recommended")), None)
    prompt, label = ("", "Pick an option first") if chosen is None else (
        choice_prompt(row, state, chosen), "Copy answer: " + row["options"][chosen]["label"])
    action = copy_control(prompt, f'prompt-{hexed(row["id"])}', label, "Copy answer")
    return (
        f'<fieldset class="picks" data-decision="{e(row["id"])}" data-revision="{revision(row)}"><legend class="sr-only">Options for {e(row["id"])}</legend>'
        + "".join(pick(row, option, index, state) for index, option in enumerate(row["options"]))
        + f'</fieldset><div class="answer-action">{send_control(row, chosen is not None)}{action}</div>'
    )


def stale_pick_note(row):
    """A stored pick that answered an earlier version of this decision, so it was never applied."""
    if "stalePick" not in row:
        return ""
    stale = row["stalePick"]
    if row["status"] == "open":
        message = f'You picked “{e(stale["label"])}” {when(stale["at"], "relative")}, on an earlier version of this question. It has changed since, so pick again.'
    else:
        message = f'You picked “{e(stale["label"])}” {when(stale["at"], "relative")}, after this was settled. The coordinator will reopen it so you can pick again.'
    return f'<p class="stale-pick">{icon("stale")}<span>{message}</span></p>'


def recommended_choice(row):
    return next((index, option) for index, option in enumerate(row["options"]) if option.get("recommended"))


def batch_view(quick, state):
    """One prompt that takes every recommendation, naming each decision it answers."""
    lines, summary = [f'Decisions in {quoted(state["title"])}'], []
    for row in quick:
        index, option = recommended_choice(row)
        lines.append(f'Decision {json.dumps(row["id"], ensure_ascii=False)} (revision {revision(row)}): I choose option {index + 1}: {quoted(option["label"])}')
        summary.append(f'<li><strong>{e(row["id"])}</strong> {e(option["label"])}</li>')
    return (
        f'<div class="card batch"><div class="batch-summary"><p class="answer-label">Take every recommended pick</p><ul>{"".join(summary)}</ul></div>'
        f'{copy_control(chr(10).join(lines), "prompt-batch", f"Copy all {len(quick)} recommended picks", "Copy all recommended")}</div>'
    )


def card_id(kind, row):
    return f'{kind}-{hexed(row["id"])}'


def blocked_work(row):
    return ", ".join(f'{entry["id"]} {entry["phase"]}' for entry in row["blocks"])


def decision_label(row):
    settled = row["status"] != "open"
    name, mark = {
        "answered": ("Answered", "decision"),
        "resolved": ("Coordinator decided", "resolved"),
    }.get(row["status"], ("Quick pick", "quick") if row.get("weight") == "quick" else ("Decision", "decision"))
    content = f'<span class="need-id{" settled" if settled else ""}">{icon(mark)}{name} {e(row["id"])}</span>'
    if not settled:
        content += f'<span class="asked">{icon("asked")}<span>Asked {when(row["date"], "relative")}</span></span>'
    if row.get("blocks"):
        content += f'<span>{"Affected" if settled else "Blocks"} {e(blocked_work(row))}</span>'
    return content


def tradeoff_label(row):
    content = f'<span class="need-id settled">{icon("tradeoff")}Tradeoff {e(row["id"])}</span>'
    if row.get("source"):
        content += f'<span>Source: {e(row["source"])}</span>'
    return content


def settled_decision(row, state, context):
    resolved = row["status"] == "resolved"
    label = "Coordinator's call" if resolved else "Your answer"
    answer = row["answer"]
    answer_text = f'<p class="answer-label">{label}</p><p class="decision-text">{prose(answer)}</p>'
    rationale = row.get("rationale", "")
    has_history = bool(DECISION_HISTORY_ENTRY.search(rationale))
    content = f'<p class="decision-lead">{prose(rationale)}</p>' if rationale and not has_history else ""
    short_answer = len(answer) <= 240 and all(len(word) <= 60 for word in answer.split())
    if short_answer:
        content += f'<div class="answer">{answer_text}</div>'
    content += (
        f'<details class="decision-details"><summary id="details-{card_id("decision", row)}">Technical details'
        f'<span class="sr-only"> for {e(row["id"])}</span></summary><div class="decision-body">{answer_text}'
    )
    if resolved:
        content += f'<p class="answer-label">Basis</p><p class="decision-text">{prose(row["basis"])}</p>'
    if has_history:
        content += f'<p class="answer-label">Decision history</p><p class="decision-text">{prose(rationale)}</p>'
    if context:
        content += '<p class="answer-label">Context</p>' + context
    content += pictures_view(row) + link_list(row.get("links", [])) + '</div></details>' + stale_pick_note(row)
    if resolved:
        reopen = copy_control(decision_prompt(row, state, "Reopen this decision."), f'prompt-{hexed(row["id"])}-reopen', f'Copy prompt to reopen {row["id"]}', "Copy to reopen", "reopen")
        content += f'<div class="reopen">{reopen}</div>'
    return content


def need_card(row, state, selected=False):
    classes = "card need" + (" quick" if row["status"] == "open" and row.get("weight") == "quick" else "") + (" selected" if selected else "")
    content = f'<article id="{card_id("decision", row)}" class="{classes}"><p class="need-meta">{decision_label(row)}</p><h3>{prose(row["question"])}</h3>'
    context = ""
    if row.get("context"):
        context = '<ul class="context">' + "".join(f"<li>{prose(item)}</li>" for item in row["context"]) + "</ul>"
    if row["status"] in {"answered", "resolved"}:
        return content + settled_decision(row, state, context) + "</article>"
    content += context + pictures_view(row) + stale_pick_note(row)
    if row["status"] == "open" and row.get("meanwhile"):
        content += f'<p class="meanwhile"><span class="answer-label">Meanwhile</span> {prose(row["meanwhile"])}</p>'
    if row.get("options"):
        content += picks(row, state)
    elif row.get("recommendation"):
        content += f'<div class="suggested-answer"><p class="answer-label">Suggested answer</p><p>{prose(row["recommendation"])}</p></div>'
    return content + link_list(row.get("links", [])) + "</article>"


def revisit_card(row):
    return f'<article id="{card_id("tradeoff", row)}" class="card need"><p class="need-meta">{tradeoff_label(row)}</p><h3>{prose(row["title"])}</h3><p class="context">{prose(row["tradeoff"])}</p><div class="answer"><p class="answer-label">Revisit</p><p>{prose(row["revisit"])}</p></div></article>'


def inbox_row(target, identity, title, selected=False, asked=None):
    age = f' · {when(asked, "relative")}' if asked else ""
    return (
        f'<button type="button" class="inbox-row" id="row-{target}" role="option" aria-selected="{str(selected).lower()}" aria-controls="{target}">'
        f'<span class="inbox-row-title">{e(title)}</span><span class="inbox-row-id">{e(identity)}{age}</span></button>'
    )


def inbox_group(heading_id, title, tone, rows):
    return (
        f'<div id="group-{heading_id}" class="inbox-group {tone}" role="group" aria-labelledby="{heading_id}">'
        f'<span id="{heading_id}" class="inbox-group-title">{e(title)} <span class="count-pill{" attention" if tone == "open" else ""}">{len(rows)}</span></span>'
        f'<div class="inbox-group-rows">{"".join(rows)}</div></div>'
    )


def needs_view(state, judgment, quick, resolved, answered):
    """Decision cards in reading order, with the list that shows one card at a time in the dual-pane inbox."""
    empty = '<p class="empty">Your Inbox is empty.</p>'
    revisits = state.get("revisits", [])
    open_needs = judgment + quick
    if not (open_needs or resolved or revisits or answered):
        return empty
    selected = open_needs[0] if open_needs else None
    batch = batch_view(quick, state) if len(quick) > 1 else ""
    cards = (
        "".join(need_card(row, state, selected=row is selected) for row in judgment) + batch
        + "".join(need_card(row, state, selected=row is selected) for row in quick)
    )
    groups = ""
    for heading_id, title, rows in (("judgment-list", "Judgment calls", judgment), ("quick-list", "Quick picks", quick)):
        if rows:
            groups += inbox_group(heading_id, title, "open", [inbox_row(card_id("decision", row), row["id"], row["question"], selected=row is selected, asked=row["date"]) for row in rows])
    if resolved:
        groups += inbox_group("resolved-list", "Coordinator decided", "answered", [inbox_row(card_id("decision", row), row["id"], row["question"]) for row in resolved])
        cards += collapsible("resolved-heading", "Coordinator decided", len(resolved), f'<div class="section-body">{"".join(need_card(row, state) for row in resolved)}</div>', closed=True)
    if revisits:
        groups += inbox_group("revisits-list", "Worth a second look", "revisit", [inbox_row(card_id("tradeoff", row), row["id"], row["title"]) for row in revisits])
        cards += collapsible("revisits-heading", "Worth a second look", len(revisits), f'<div class="section-body">{"".join(revisit_card(row) for row in revisits)}</div>', closed=True)
    if answered:
        groups += inbox_group("answered-list", "Answered decisions", "answered", [inbox_row(card_id("decision", row), row["id"], row["question"]) for row in answered])
        cards += collapsible("answered-heading", "Answered decisions", len(answered), f'<div class="section-body">{"".join(need_card(row, state) for row in answered)}</div>', closed=True)
    return (empty if not open_needs else "") + f'<div class="inbox"><div class="inbox-list" role="listbox" aria-label="Decisions">{groups}</div><div class="inbox-detail">{cards}</div></div>'


class Program:
    """Lookups the work board needs across outcomes, layers, and decisions."""

    def __init__(self, state):
        self.decisions = state["decisions"]
        self.by_id = {row["id"]: row for row in state["work"]}
        self.layers = {layer["id"]: (layer, row) for row in state["work"] for layer in row.get("layers", [])}

    def foreign_parents(self, row):
        """Unmerged layers of other outcomes that this active outcome's layers stack on."""
        if row["state"] in TERMINAL:
            return []
        parents = [self.layers[layer["stackedOn"]] for layer in row.get("layers", []) if "stackedOn" in layer]
        return [(layer, owner) for layer, owner in parents if owner is not row and layer["status"] != "merged"]

    def blockers(self, row):
        """(halts, kind, identity, text) for each open blocker; waits let building continue."""
        items = []
        for decision in self.decisions:
            entry = next((entry for entry in decision.get("blocks", []) if entry["id"] == row["id"]), None)
            if decision["status"] == "open" and entry:
                items.append((entry["phase"] in HALTING, f'Decision · blocks {entry["phase"]}', decision["id"], decision["question"]))
        items += [(True, STATES[self.by_id[identity]["state"]], identity, self.by_id[identity]["title"]) for identity in row.get("blockedBy", [])]
        if row.get("blocked"):
            items.append((True, "Other", "", row["blocked"]))
        dead = {identity: dead_base(self.by_id[identity]) for identity in bases(row, self.layers)}
        dead = {identity: reason for identity, reason in dead.items() if reason}
        for identity, reason in dead.items():
            items.append((True, f"{reason.title()} base", identity, self.by_id[identity]["title"]))
        for layer in row.get("layers", []):
            parent, parent_row = self.layers.get(layer.get("stackedOn"), ({}, None))
            if parent.get("status") == "closed" and layer["status"] in LIVE_LAYERS and parent_row["id"] not in dead:
                items.append((True, "Closed base", parent["id"], parent_row["title"]))
        for _, parent in self.foreign_parents(row):
            if parent["id"] not in dead and self.halted(parent):
                items.append((True, "Blocked base", parent["id"], parent["title"]))
        return items

    def halted(self, row):
        return any(halts for halts, *_ in self.blockers(row))


def state_badges(row, program):
    primary = display_stage(row)
    content = f'<span class="state {e(primary)}">{icon(primary)}{e(STATES[primary])}</span>'
    if row["state"] == "ready":
        content += f'<span class="state ready">{icon("ready")}{e(READY_LABELS[effective_finish(row)])}</span>'
    if "provisional" in row:
        content += f'<span class="state provisional">{icon("provisional")}Provisional</span>'
    if program.halted(row):
        content += f'<span class="state blocked">{icon("blocked")}Blocked</span>'
    return content


def finish_line(row):
    if "finishLine" not in row:
        return ""
    value = FINISH_LINES[row["finishLine"]]
    if effective_finish(row) != row["finishLine"]:
        value += f' → {FINISH_LINES[effective_finish(row)]} while provisional'
    return f'<p class="finish">{icon("finish")}<span><span class="fact-label">Finish line</span> {e(value)}</span></p>'


def provisional_note(row):
    if "provisional" not in row:
        return ""
    provisional = row["provisional"]
    return (
        f'<div class="provisional-note"><p class="note-label">{icon("provisional")}Provisional</p>'
        f'<p><strong>Rests on</strong> {prose(provisional["basis"])}</p><p><strong>Clears when</strong> {prose(provisional["clears"])}</p>'
        '<p class="note-rule">It never lands while provisional.</p></div>'
    )


def result_card(result):
    """A result as a card: its image's thumbnail when it has one, otherwise a link mark and the host it opens."""
    if "image" in result:
        media = f'<img class="result-thumb" src="{e(result["image"])}" alt="" loading="lazy">'
    else:
        media = f'<span class="result-mark">{icon("result")}</span>'
    host = urlsplit(url(result["url"], "url")).netloc
    content = f'{media}<span class="result-text"><span class="result-label">{e(result["label"])}</span><span class="result-host">{e(host)}</span></span>'
    access = f'<span class="result-access">{prose(result["access"])}</span>' if result.get("access") else ""
    return f'<li>{anchor(result["url"], content, "result-card" + (" has-image" if "image" in result else ""))}{access}</li>'


def results_view(row):
    if not row.get("results"):
        return ""
    items = "".join(result_card(result) for result in row["results"])
    return f'<div class="results"><p class="note-label">Results</p><ul>{items}</ul></div>'


def pr_link(target):
    match = re.search(r"/(?:pull|pulls|merge_requests|pull-requests)/(\d+)/?$", urlsplit(url(target, "url")).path)
    return link(f"PR #{match[1]}" if match else "Open PR", target, "pr-link", "pr")


def layers_view(row, program):
    if not row.get("layers"):
        return ""
    items = ""
    for layer in row["layers"]:
        items += f'<li class="layer" id="layer-{hexed(layer["id"])}"><div class="layer-name"><code>{e(layer["branch"])}</code><span class="layer-meta">{e(layer["id"])} · {e(LAYER_STATES[layer["status"]])}'
        if "stackedOn" in layer:
            parent, parent_row = program.layers[layer["stackedOn"]]
            items += f' · on {e(parent["id"])}' + (f' ({e(parent_row["id"])})' if parent_row is not row else "")
        items += "</span></div>"
        if "url" in layer:
            items += pr_link(layer["url"])
        items += "</li>"
    label = "Layer" if len(row["layers"]) == 1 else f'{len(row["layers"])} layers, bottom first'
    return f'<div class="layers"><p class="note-label">{e(label)}</p><ol>{items}</ol></div>'


def blocker_list(items, label, mark, cls):
    if not items:
        return ""
    content = f'<div class="{cls}"><p class="blocker-label">{icon(mark)}{e(label)}</p><ul>'
    for kind, identity, text_value in items:
        prefix = f'<span class="blocker-id">{e(identity)}</span> ' if identity else ""
        content += f'<li>{prefix}<span class="blocker-kind">{e(kind)}</span> {prose(text_value)}</li>'
    return content + "</ul></div>"


LIVE_LABELS = {"running": ("Owner running", "seen"), "idle": ("Owner idle", "seen"),
               "unknown": ("Owner thread unreadable", "since")}


def now_sentence(row, state, found):
    """One sentence on what is happening to this work, or what it waits on, from the facts status uses.

    What status finds for the row comes first: a running owner or a provisional start supersedes a
    halting Need, and an idle owner who owes work supersedes a Need that lets work continue.
    """
    kinds = {entry["kind"]: entry for entry in reversed(found)}
    owner = row.get("owner", {}).get("name", "The owner")
    halting = open_blocks(state, row["id"], HALTING)
    later = [identity for identity in open_blocks(state, row["id"]) if identity not in halting]
    landing = pending_landing(state, row["id"])
    if "approval" in kinds:
        return f"{owner} waits on an approval in its thread."
    if "running" in kinds:
        return f"{owner} is working."
    if "provisional start" in kinds:
        return f"Ready to start provisionally on {', '.join(halting)}'s recommended option."
    if halting:
        return f"Held until you answer {', '.join(halting)}."
    if "dependency" in kinds:
        return f"Waits for {', '.join(unsatisfied(state, row))} to finish first."
    if "blocked" in kinds:
        return f"Blocked: {row['blocked']}"
    if "wait" in kinds:
        return f"Waits on {kinds['wait']['text']}."
    for kind in ("idle owner", "orphan"):
        if kind in kinds:
            return f"{kinds[kind]['text']}."
    if later:
        return f"Waits on your answer to {', '.join(later)}."
    if "release" in kinds:
        return "Ready to land once the coordinator releases it."
    if landing:
        return f"Landing {landing['id']} is {landing['state']}; {landing['lander']} lands it."
    if "start" in kinds:
        return "Ready to start."
    if row["state"] == "unknown":
        return row.get("unknownReason", "Its state could not be read.")
    if row["state"] == "planned" and row.get("required") is False:
        return "Proposed, outside the committed scope."
    if row["state"] == "ready" and effective_finish(row) != "land":
        return f"At its finish line: {READY_LABELS[effective_finish(row)].lower()}."
    return {"planned": "Not started.", "building": "Building.", "shown": "Shown; waits on your merge, changes, or scrap choice.",
            "in-review": "In review.", "ready": "Ready.", "landed": "Landed.", "done": "Done.", "scrapped": "Scrapped."}[row["state"]]


def live_view(row):
    """The owner's thread state as status last observed it."""
    owner = row.get("owner")
    if not owner or row["state"] in TERMINAL:
        return ""
    seen = owner.get("seen") if "session" in owner else None
    state = seen["state"] if seen else "unknown"
    label, since = LIVE_LABELS[state]
    if not seen:
        label = "Owner not observed yet" if "session" in owner else "Owner state unknown"
    observed = f' · {since} {when(seen["at"], "relative")}' if seen else ""
    return f'<p class="live {state}"><span class="live-dot" aria-hidden="true"></span><span>{e(label)}{observed}</span></p>'


def now_view(row, state, found):
    return f'<div class="now"><p class="now-text">{prose(now_sentence(row, state, found))}</p>{live_view(row)}</div>'


def work_card(row, program, state, found):
    reasons = program.blockers(row)
    heading_id = "work-" + hexed(row["id"])
    content = f'<article class="card work" id="{card_id("work-card", row)}" aria-labelledby="{heading_id}"><div class="work-top"><p class="work-id"><strong>{e(row["id"])}</strong> {e(row["repo"])}</p><p class="badges">{state_badges(row, program)}</p></div>'
    tags = [{"support": "Support", "follow-up": "Follow-up"}[row["kind"]]] if row["kind"] != "outcome" else []
    if row.get("required") is False:
        tags.append("Proposed · outside committed scope")
    if tags or row.get("tickets"):
        content += '<p class="tags">' + "".join(f'<span class="tag">{e(tag)}</span>' for tag in tags) + "".join(link(t["label"], t["url"], "ticket") for t in row.get("tickets", [])) + "</p>"
    content += f'<h4 id="{heading_id}" class="work-title">{prose(row["title"])}</h4>' + now_view(row, state, found)
    if row.get("description"):
        content += f'<p class="work-description">{prose(row["description"])}</p>'
    content += finish_line(row)
    if row.get("unknownReason"):
        content += f'<p class="state-note">{icon("unknown")}{prose(row["unknownReason"])}</p>'
    content += blocker_list([item[1:] for item in reasons if item[0]], "Blocked by", "blocked", "blocker")
    content += blocker_list([item[1:] for item in reasons if not item[0]], "Waits on", "waits", "blocker waits")
    content += results_view(row) + provisional_note(row) + layers_view(row, program)
    if row.get("origin") or row.get("evidence"):
        content += '<details class="work-context"><summary class="section-toggle" id="' + card_id("toggle-evidence", row) + '">Evidence and history</summary><div class="section-body">'
        if row.get("origin"):
            content += f'<p><strong>Origin</strong> {prose(row["origin"])}</p>'
        content += link_list(row.get("evidence", []))
        content += "</div></details>"
    content += '<div class="work-footer"><div class="assignee">'
    if "owner" in row:
        owner = row["owner"]
        content += f'<p class="owner">{link(owner["name"], owner["session"]) if "session" in owner else e(owner["name"])}</p>'
    content += f'<p class="observation">Checked {when(row["checkedAt"])}</p></div>'
    return content + "</div></article>"


def plural(count, word):
    return f'{count} {word}{"" if count == 1 else "s"}'


def overview(work):
    outcomes = [row for row in work if row["kind"] != "support"]
    landed = sum(row["state"] == "landed" for row in outcomes)
    support = len(work) - len(outcomes)
    counts = [(key, sum(display_stage(row) == key for row in work)) for key in STAGE_ORDER]
    counts = [(key, count) for key, count in counts if count]
    summary = ", ".join(f"{count} {STATES[key].lower()}" for key, count in counts)
    bar = "".join(f'<span class="segment {e(key)}" style="flex-grow:{count}"></span>' for key, count in counts)
    tally = f'{plural(len(outcomes), "outcome")} · {landed} landed' + (f' · {plural(support, "support task")}' if support else "")
    return (
        f'<div class="overview"><p class="work-count">{tally}</p>'
        f'<div class="progress" role="img" aria-label="{e(summary or "No work")}">{bar}</div>'
        "</div>"
    )


VERDICT_NOTES = {
    "runnable": "The coordinator has work to act on now.",
    "working": "Owners are working; the coordinator waits on them.",
    "waiting": "Everything left waits on you or on an outside event.",
    "done": "Every outcome is at its finish line.",
}
TALLIES = (  # (key, label, the status findings it counts)
    ("running", "Running", lambda found: found["working"]),
    ("idle", "Idle, owing work", lambda found: [entry for entry in found["runnable"] if entry["kind"] == "idle owner"]),
    ("start", "Ready to start", lambda found: [entry for entry in found["runnable"] if entry["kind"] == "start"]),
    ("land", "Ready to land", lambda found: [entry for entry in found["runnable"] if entry["kind"] == "release"]),
)


def health_view(state, found):
    """The program verdict and its counts, from the status findings for the rendered record."""
    verdict = found["verdict"]
    tallies = ""
    for key, label, select in TALLIES:
        count = len(select(found))
        tone = " attention" if key == "idle" and count else " zero" if not count else ""
        tallies += f'<div class="tally{tone}"><dt>{e(label)}</dt><dd data-count="{key}">{count}</dd></div>'
    content = (
        f'<section class="health card {verdict}" aria-labelledby="health-heading"><div class="health-top">'
        f'<h2 id="health-heading" class="verdict">{icon(verdict)}<span class="sr-only">Program </span>{verdict.title()}</h2>'
        f'<p class="verdict-note">{VERDICT_NOTES[verdict]}</p></div><dl class="tallies">{tallies}</dl><div class="health-lines">'
    )
    waiting = [row for row in state["decisions"] if row["status"] == "open"]
    if waiting:
        oldest = min(waiting, key=lambda row: parse_time(row["date"]))
        target = card_id("decision", oldest)
        content += (f'<p class="health-line" data-oldest-wait>{icon("asked")}<span><span class="fact-label">Oldest Inbox item</span> '
                    f'<a href="#{target}">{e(oldest["id"])}</a>, asked {when(oldest["date"], "relative")}</span></p>')
    else:
        content += f'<p class="health-line" data-oldest-wait>{icon("asked")}<span><span class="fact-label">Inbox</span> Empty</span></p>'
    content += f'<p class="health-line">{icon("next")}<span><span class="fact-label">Next</span> {prose(state["next"])}</span></p>'
    return content + "</div></section>"


def now():
    """The current time in UTC. Event times always come from this clock, never from the caller."""
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def render(state, stamp=None):
    """Validate the program and render its page; stamp is the (commit, commit time) of the record it renders."""
    validate(state)
    found = assess(state, stamp[1] if stamp else now(), recorded_threads(state))
    by_work = {}
    for group in ("runnable", "working", "waiting", "attention"):
        for entry in found[group]:
            by_work.setdefault(entry["id"], []).append(entry)
    decisions = state["decisions"]
    open_needs = [row for row in decisions if row["status"] == "open"]
    judgment = [row for row in open_needs if row.get("weight") != "quick"]
    quick = [row for row in open_needs if row.get("weight") == "quick"]
    resolved = [row for row in decisions if row["status"] == "resolved"]
    answered = [row for row in decisions if row["status"] == "answered"]
    program = Program(state)

    needs_html = needs_view(state, judgment, quick, resolved, answered)

    def cards(rows):
        return f'<div class="section-body stage-cards">{"".join(work_card(row, program, state, by_work.get(row["id"], [])) for row in rows)}</div>'

    stages = ""
    for key in STAGE_ORDER:
        rows = [row for row in state["work"] if display_stage(row) == key]
        if rows and key not in TERMINAL:
            blocked = sum(program.halted(row) for row in rows)
            alert = f'<span class="state blocked"><span class="sr-only">, </span>{icon("blocked")}{blocked} blocked</span>' if blocked else ""
            stages += collapsible(f"stage-{key}", STATES[key], len(rows), cards(rows), level=3, state=key, mark=icon(key), alert=alert)
    finished = [row for key in STAGE_ORDER if key in TERMINAL for row in state["work"] if row["state"] == key]
    if finished:
        stages += collapsible("stage-finished", "Finished", len(finished), cards(finished), level=3, state="finished",
                              mark=icon("finished"), closed=True)
    work_html = f'{overview(state["work"])}<div class="stage-board">{stages}</div>' if stages else '<p class="empty">No work recorded yet.</p>'

    facts = ""
    if state.get("finishLine"):
        facts += f'<p class="fact">{icon("finish")}<span><span class="fact-label">Finish line</span> {prose(state["finishLine"])}</span></p>'
    if stamp:
        facts += f'<p class="fact">{icon("record")}<span><span class="fact-label">Record</span> {record_stamp(*stamp)}</span></p>'
    demo = '<span class="demo" title="Fictional work, not live project status.">Illustrative example</span>' if state.get("demo") else ""
    content = f'<header class="masthead"><p class="eyebrow"><span>Coordinator</span>{demo}</p><h1>{e(state["title"])}</h1><p class="goal">{prose(state["goal"])}</p><div class="facts">{facts}</div></header>'
    content += health_view(state, found)
    needs_badge = f'<span class="count-pill{" attention" if open_needs else ""}">{len(open_needs)}</span>'
    content += (
        '<nav class="navigation" aria-label="Program views"><div class="tabs" role="tablist" aria-label="Command center">'
        f'<button id="needs-tab" role="tab" aria-selected="true" aria-controls="needs-panel" tabindex="0">Inbox {needs_badge}</button>'
        f'<button id="work-tab" role="tab" aria-selected="false" aria-controls="work-panel" tabindex="-1">Work <span class="count-pill">{len(state["work"])}</span></button>'
        "</div></nav>"
        f'<section id="needs-panel" role="tabpanel" aria-labelledby="needs-tab" tabindex="0"><h2 class="sr-only">Inbox</h2>{needs_html}</section>'
        f'<section id="work-panel" role="tabpanel" aria-labelledby="work-tab" tabindex="0" hidden><h2 class="sr-only">Work</h2>{work_html}</section>'
    )
    return TEMPLATE.read_text().replace("<!--TITLE-->", e(state["title"])).replace("<!--CONTENT-->", content)


def layout(state):
    """The program file's one-value-per-line text."""
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"


def git(state_file, *args):
    result = subprocess.run(["git", "-C", str(state_file.parent), *args], capture_output=True, encoding="utf-8")
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"git {args[0]} exited with status {result.returncode}")
    return result.stdout


def committed(state_file):
    """The state file's program at HEAD of its git repository."""
    return json.loads(git(state_file, "show", f"HEAD:./{state_file.name}"))


def content_name(content, suffix):
    """The files/ path for a picture, named by its content, so a changed picture gets a new name."""
    return f"files/{hashlib.sha256(content).hexdigest()[:16]}{suffix.lower()}"


def place(target, content):
    """Write content-named bytes at target; return whether it wrote. Other bytes already there are refused."""
    if target.exists():
        if target.read_bytes() != content:
            raise ValueError(f"{target} does not hold the bytes its name records; restore it with git checkout or remove it")
        return False
    target.parent.mkdir(exist_ok=True)
    try:
        target.write_bytes(content)
    except OSError:
        target.unlink(missing_ok=True)
        raise
    return True


def pictures_in(state):
    """Every picture the record names: result thumbnails, Inbox pictures, and option pictures, each once."""
    names = [result["image"] for row in state["work"] for result in row.get("results", []) if "image" in result]
    for row in state["decisions"]:
        names += [item["image"] for item in row.get("pictures", {}).get("images", [])]
        names += [option["image"] for option in row.get("options", []) if "image" in option]
    return list(dict.fromkeys(names))


def check_pictures(folder, state):
    """Refuse a record that names a picture its folder lacks, or one whose bytes don't match its name."""
    for path in pictures_in(state):
        try:
            content = (folder / path).read_bytes()
        except OSError:
            raise ValueError(f"{path} is missing from {folder}; copy the picture there under its content name") from None
        if (name := content_name(content, Path(path).suffix)) != path:
            raise ValueError(f"{path} is not its content's name; name it {name}")


def stage_images(state_file, state, folder):
    """Write each picture at HEAD into folder's files/, under its content name."""
    for path in pictures_in(state):
        blob = subprocess.run(["git", "-C", str(state_file.parent), "cat-file", "blob", f"HEAD:./{path}"], capture_output=True)
        if blob.returncode:
            raise ValueError(f"{path} is not committed in the program folder; commit it with the record")
        if (name := content_name(blob.stdout, Path(path).suffix)) != path:
            raise ValueError(f"{path} is not its content's name; name it {name}")
        place(folder / path, blob.stdout)


def page_files(page):
    """The files beside the page that it shows, as paths relative to the page."""
    return sorted(set(re.findall(r'<img [^>]*src="(files/[^"]+)"', page)))


def stage_page(state_file, page_file):
    """Render HEAD to page_file's .next sibling; return whether it differs from page_file, ignoring the record stamp.

    The stamp names HEAD's commit and its time, or the staged page's when it already holds this content.
    Pictures go beside the page under files/.
    """
    staged = page_file.with_name(f"{page_file.stem}.next{page_file.suffix}")
    if state_file.resolve() in (page_file.resolve(), staged.resolve()):
        raise ValueError(f"{page_file}: the page would overwrite the state file")
    state = validate(committed(state_file))
    stage_images(state_file, state, page_file.parent)
    page = render(state, git(state_file, "log", "-1", "--format=%h %cI").split())

    def holds(path):
        return path.exists() and STAMP.sub(lambda _: STAMP.search(page)[0], path.read_text(), count=1) == page

    if holds(page_file):
        staged.unlink(missing_ok=True)
        return False
    if not holds(staged):
        staged.write_text(page)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true",
                        help="Validate the working state file and the pictures it names; write nothing")
    action.add_argument("--revision", metavar="DECISION_ID", help="Print a decision's revision at HEAD")
    action.add_argument("--page", type=Path, metavar="FILE",
                        help="Render HEAD to FILE's .next sibling; print changed when it differs from FILE")
    args = parser.parse_args()
    try:
        if args.page:
            changed = stage_page(args.state, args.page)
            print("changed" if changed else "unchanged")
            shown = args.page.with_name(f"{args.page.stem}.next{args.page.suffix}") if changed else args.page
            for name in page_files(shown.read_text()):
                print(f"file: {name}")
        elif args.check:
            text = args.state.read_text()
            state = json.loads(text)
            render(state)
            check_pictures(args.state.parent, state)
            if text != layout(state):
                path = shlex.quote(str(args.state))
                raise ValueError(f"{args.state}: not one value per line; rewrite it with: "
                                 f"python3 -m json.tool --indent 2 --no-ensure-ascii {path} > {path}.fmt && mv {path}.fmt {path}")
            print(f"{args.state}: valid")
        else:
            state = validate(committed(args.state))
            print(revision(next(row for row in state["decisions"] if row["id"] == args.revision)))
    except StopIteration:
        parser.error(f"no decision {args.revision}")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
