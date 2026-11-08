#!/usr/bin/env python3
"""Render a checked program snapshot as a command center."""

import argparse
from datetime import datetime
import hashlib
from html import escape
import json
from pathlib import Path
import re
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
ISO_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)")


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


def links(value, path):
    for index, item in enumerate(records(value, path)):
        text(item.get("label"), f"{path}[{index}].label")
        url(item.get("url"), f"{path}[{index}].url")


def one_of(value, choices, path):
    text(value, path)
    if value not in choices:
        raise ValueError(f"{path} must be one of {', '.join(choices)}")
    return value


def effective_finish(row):
    return row.get("effectiveFinishLine", row.get("finishLine"))


def owned_by_another(row, other):
    return not (row.get("owner") and row.get("owner") == other.get("owner"))


def validate_layers(row, path, layers):
    for index, layer in enumerate(records(row.get("layers", []), f"{path}.layers")):
        identity = text(layer.get("id"), f"{path}.layers[{index}].id")
        where = f"{path}.layers[{identity}]"
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


def validate_work(row, layers):
    path = f"work[{row['id']}]"
    for key in ("title", "repo"):
        text(row.get(key), f"{path}.{key}")
    state = one_of(row.get("state"), STATES, f"{path}.state")
    kind = one_of(row.get("kind"), ("outcome", "follow-up", "support"), f"{path}.kind")
    timestamp(row.get("updatedAt"), f"{path}.updatedAt")
    for key in ("description", "owner", "blocked", "origin", "unknownReason"):
        if key in row:
            text(row[key], f"{path}.{key}")
    for key in ("url", "stackedOn"):
        if key in row:
            raise ValueError(f"{path}.{key}: record each PR and its stack parent on the outcome's layers")
    if "unknownReason" in row and state != "unknown":
        raise ValueError(f"{path}.unknownReason applies only to unknown state")
    if "sessionUrl" in row:
        url(row["sessionUrl"], f"{path}.sessionUrl")
    for key in ("tickets", "evidence"):
        links(row.get(key, []), f"{path}.{key}")
    for index, result in enumerate(records(row.get("results", []), f"{path}.results")):
        links([result], f"{path}.results[{index}]")
        if "access" in result:
            text(result["access"], f"{path}.results[{index}].access")
    if "required" in row and not isinstance(row["required"], bool):
        raise ValueError(f"{path}.required must be a boolean")
    if state in TERMINAL and (row.get("blockedBy") or row.get("blocked")):
        raise ValueError(f"{path}: terminal work cannot retain active blockers; keep history in the program record")
    if state in ACTIVE and "owner" not in row:
        raise ValueError(f"{path}: {state} work needs its owner")

    if kind == "support":
        for key in ("finishLine", "effectiveFinishLine", "layers", "provisional"):
            if key in row:
                raise ValueError(f"{path}.{key}: support work has no finish line or layers; give a repository change its own outcome")
        if state not in {"planned", "building", "done", "scrapped", "unknown"}:
            raise ValueError(f"{path}: support work uses planned, building, done, scrapped, or unknown")
        return
    finish = one_of(row.get("finishLine"), FINISH_LINES, f"{path}.finishLine")
    if state == "done":
        raise ValueError(f"{path}: an outcome ends landed, at its shown Try, or at its PR state, not done")
    if "provisional" in row:
        provisional = row["provisional"]
        if not isinstance(provisional, dict):
            raise ValueError(f"{path}.provisional must be an object")
        for key in ("basis", "clears"):
            text(provisional.get(key), f"{path}.provisional.{key}")
        strings(provisional.get("on", []), f"{path}.provisional.on")
        if finish == "land" and row.get("effectiveFinishLine") != "try":
            raise ValueError(f"{path}: provisional work never merges; set effectiveFinishLine to try")
    if "effectiveFinishLine" in row and not (
            "provisional" in row and finish == "land" and row["effectiveFinishLine"] == "try"):
        raise ValueError(f"{path}.effectiveFinishLine is only Try, for provisional work whose finish line is Land")
    validate_layers(row, path, layers)
    effective = effective_finish(row)
    published = [layer for layer in row.get("layers", []) if "url" in layer]
    if finish == "try" and published:
        raise ValueError(f"{path}: Try stops before the PR; a published layer needs a PR or Land finish line")
    if state == "ready":
        if "provisional" in row:
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


def halted_by_need(needs):
    """IDs of work an open Need holds at a phase that stops its work."""
    return {entry["id"] for need in needs if need["status"] == "open"
            for entry in need.get("blocks", []) if entry["phase"] in HALTING}


def validate_edges(work, by_id, layers, halted):
    for row in work:
        path = f"work[{row['id']}]"
        for dependency in strings(row.get("blockedBy", []), f"{path}.blockedBy"):
            if dependency not in by_id:
                raise ValueError(f"{path}.blockedBy references missing work {dependency}")
        for identity in row.get("provisional", {}).get("on", []):
            if identity == row["id"] or identity not in by_id:
                raise ValueError(f"{path}.provisional.on must name other work; a decision names what it blocks")
            if by_id[identity]["state"] == "scrapped" and row["id"] not in halted:
                raise ValueError(f"{path} rests on scrapped {identity}; halt it with its scrap-or-rebase Need or record its new base")
    for identity, (layer, row) in layers.items():
        if "stackedOn" not in layer:
            continue
        where = f"work[{row['id']}].layers[{identity}].stackedOn"
        if layer["stackedOn"] == identity or layer["stackedOn"] not in layers:
            raise ValueError(f"{where} must name another layer")
        parent, parent_row = layers[layer["stackedOn"]]
        active = layer["status"] not in {"merged", "closed"} and row["state"] not in TERMINAL
        if active and parent_row["state"] == "scrapped" and row["id"] not in halted:
            raise ValueError(f"{where}: {path} rests on scrapped {parent_row['id']}; halt it with its scrap-or-rebase Need or record its new base")
        if layer["status"] not in {"merged", "closed"} and parent["status"] == "closed" and row["id"] not in halted:
            raise ValueError(f"{where} names closed {parent['id']}; record the restack or halt it with its Need")
        if (parent_row is not row and parent["status"] != "merged" and row["state"] not in TERMINAL
                and owned_by_another(row, parent_row)
                and parent_row["id"] not in row.get("provisional", {}).get("on", [])):
            raise ValueError(f"{where}: {parent['id']} is another owner's unmerged layer; mark this outcome provisional on {parent_row['id']}")

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


def validate_need(row, by_id):
    path = f"needs[{row['id']}]"
    text(row.get("ask"), f"{path}.ask")
    status = one_of(row.get("status"), ("open", "answered", "resolved"), f"{path}.status")
    if status != "open":
        text(row.get("answer"), f"{path}.answer")
    if status == "resolved":
        text(row.get("basis"), f"{path}.basis")
    elif "basis" in row:
        raise ValueError(f"{path}.basis applies only to resolved decisions")
    for key in ("recommendation", "answer", "meanwhile"):
        if key in row:
            text(row[key], f"{path}.{key}")
    if row.get("weight", "judgment") not in {"quick", "judgment"}:
        raise ValueError(f"{path}.weight must be quick or judgment")
    strings(row.get("context", []), f"{path}.context")
    blocked = set()
    for index, entry in enumerate(records(row.get("blocks", []), f"{path}.blocks")):
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
    for option in records(row.get("options", []), f"{path}.options"):
        for key in ("label", "effect"):
            text(option.get(key), f"{path}.options.{key}")
        if "recommended" in option and not isinstance(option["recommended"], bool):
            raise ValueError(f"{path}.options.recommended must be a boolean")
    recommended = sum(option.get("recommended", False) for option in row.get("options", []))
    if recommended > 1:
        raise ValueError(f"{path}: only one option can be recommended")
    if row.get("options") and row.get("recommendation") and not recommended:
        raise ValueError(f"{path}: mark the recommended option to attach its recommendation")
    if row.get("weight") == "quick" and (len(row.get("options", [])) < 2 or not recommended):
        raise ValueError(f"{path}: quick needs at least two options with one recommended")
    links(row.get("links", []), f"{path}.links")


def validate(state):
    if not isinstance(state, dict):
        raise ValueError("state must be an object")
    for key in ("title", "goal"):
        text(state.get(key), key)
    timestamp(state.get("updatedAt"), "updatedAt")
    if "finishLine" in state:
        text(state["finishLine"], "finishLine")
    if "demo" in state and not isinstance(state["demo"], bool):
        raise ValueError("demo must be a boolean")
    work = records(state.get("work"), "work")
    needs = records(state.get("needs"), "needs")
    revisits = records(state.get("revisits", []), "revisits")
    for name, rows in (("work", work), ("needs", needs), ("revisits", revisits)):
        ids = [text(row.get("id"), f"{name}[{i}].id") for i, row in enumerate(rows)]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{name} contains duplicate IDs")
    by_id = {row["id"]: row for row in work}
    layers = {}
    for row in work:
        validate_work(row, layers)
    for row in needs:
        validate_need(row, by_id)
    validate_edges(work, by_id, layers, halted_by_need(needs))
    for row in revisits:
        for key in ("title", "tradeoff", "revisit"):
            text(row.get(key), f"revisits[{row['id']}].{key}")
        if "source" in row:
            text(row["source"], f"revisits[{row['id']}].source")
    return state


STAGE_ORDER = ("planned", "building", "shown", "in-review", "landed", "done", "unknown", "scrapped")
ICONS = {
    "planned": "circle-dashed", "building": "hammer", "shown": "hand", "in-review": "scan-eye",
    "ready": "circle-check", "landed": "git-merge", "done": "check-check",
    "scrapped": "ban", "unknown": "circle-question-mark", "provisional": "git-branch",
    "blocked": "triangle-alert", "waits": "hourglass", "copy": "copy", "copied": "check",
    "decision": "message-circle-question-mark", "quick": "zap", "resolved": "badge-check", "reopen": "rotate-ccw",
    "recommended": "star", "pr": "git-pull-request", "finish": "flag", "snapshot": "clock", "tradeoff": "scale",
    "result": "external-link",
}


def e(value):
    return escape(str(value), quote=True)


def link(label, target, cls="", icon_name=None):
    attribute = f' class="{cls}"' if cls else ""
    mark = icon(icon_name) if icon_name else ""
    return f'<a{attribute} href="{e(url(target, "link"))}" target="_blank" rel="noopener noreferrer">{mark}{e(label)}</a>'


def link_list(rows):
    return '<p class="links">' + "".join(link(row["label"], row["url"]) for row in rows) + "</p>" if rows else ""


def icon(name):
    return f'<i class="icon" data-lucide="{ICONS[name]}" aria-hidden="true"></i>'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def hexed(identity):
    return identity.encode().hex()


def when(value, age=False):
    return f'<time datetime="{e(value)}"{" data-age" if age else ""}>{e(value)}</time>'


def quoted(value):
    return json.dumps(" ".join(value.split()), ensure_ascii=False)


def revision(need):
    """Digest of the decision content a copied choice answers."""
    return digest(json.dumps(need, sort_keys=True))[:10]


def display_stage(row):
    """The stage a row reads under; a ready outcome stays in review and adds a readiness badge."""
    return "in-review" if row["state"] == "ready" else row["state"]


def collapsible(heading_id, title, count, body, *, level=2, state="", mark="", alert=""):
    """A section whose heading stays visible, and whose count stays readable, when collapsed."""
    return (
        f'<section class="collapsible{" " + state if state else ""}" aria-labelledby="{heading_id}"><details open>'
        f'<summary class="section-toggle" id="toggle-{heading_id}"><h{level} id="{heading_id}" class="section-title">{mark}{e(title)} <span class="count">{count}</span>{alert}</h{level}></summary>'
        f"{body}</details></section>"
    )


def decision_prompt(row, state, action):
    return (
        f'Decision {json.dumps(row["id"], ensure_ascii=False)} (revision {revision(row)}) in {quoted(state["title"])}\n'
        f'Question: {quoted(row["ask"])}\n'
        f'{action}'
    )


def copy_control(prompt, status_id, aria_label, idle, mark="copy"):
    return (
        f'<button type="button" class="copy-prompt" data-prompt="{e(prompt)}" '
        f'aria-label="{e(aria_label)}" aria-describedby="{e(status_id)}">'
        f'<span class="idle">{icon(mark)}{e(idle)}</span><span class="done">{icon("copied")}Copied</span></button>'
        f'<span class="copy-status" id="{e(status_id)}" role="status"></span>'
        f'<textarea class="manual-prompt" aria-label="{e("Prompt: " + aria_label)}" readonly hidden></textarea>'
    )


def choice(row, option, index, state):
    prompt = decision_prompt(row, state, f'I choose option {index + 1}: {quoted(option["label"])}')
    recommended = option.get("recommended", False)
    content = f'<li class="{"recommended" if recommended else "choice"}"><div class="choice-body"><p class="choice-heading"><strong>{e(option["label"])}</strong>'
    if recommended:
        content += f'<span class="recommended-label">{icon("recommended")}Recommended</span>'
    content += f'</p><p class="choice-effect">{e(option["effect"])}</p>'
    if recommended and row.get("recommendation"):
        content += f'<p class="choice-rationale">{e(row["recommendation"])}</p>'
    status_id = f'prompt-{hexed(row["id"])}-{index}'
    return content + f'</div>{copy_control(prompt, status_id, "Copy prompt: " + option["label"], "Copy prompt")}</li>'


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
        "resolved": ("Chief decided", "resolved"),
    }.get(row["status"], ("Quick pick", "quick") if row.get("weight") == "quick" else ("Decision", "decision"))
    content = f'<span class="need-id{" settled" if settled else ""}">{icon(mark)}{name} {e(row["id"])}</span>'
    if row.get("blocks"):
        content += f'<span>{"Affected" if settled else "Blocks"} {e(blocked_work(row))}</span>'
    return content


def tradeoff_label(row):
    content = f'<span class="need-id settled">{icon("tradeoff")}Tradeoff {e(row["id"])}</span>'
    if row.get("source"):
        content += f'<span>Source: {e(row["source"])}</span>'
    return content


def need_card(row, state, selected=False):
    classes = "card need" + (" quick" if row["status"] == "open" and row.get("weight") == "quick" else "") + (" selected" if selected else "")
    content = f'<article id="{card_id("decision", row)}" class="{classes}"><p class="need-meta">{decision_label(row)}</p><h3>{e(row["ask"])}</h3>'
    if row.get("context"):
        content += '<ul class="context">' + "".join(f"<li>{e(item)}</li>" for item in row["context"]) + "</ul>"
    if row["status"] == "open" and row.get("meanwhile"):
        content += f'<p class="meanwhile"><span class="answer-label">Meanwhile</span> {e(row["meanwhile"])}</p>'
    if row["status"] == "answered":
        content += f'<div class="answer"><p class="answer-label">Your answer</p><p>{e(row["answer"])}</p></div>'
    elif row["status"] == "resolved":
        content += f'<div class="answer"><p class="answer-label">Chief\'s call</p><p>{e(row["answer"])}</p><p class="answer-label">Basis</p><p>{e(row["basis"])}</p></div>'
        reopen = copy_control(decision_prompt(row, state, "Reopen this decision."), f'prompt-{hexed(row["id"])}-reopen', f'Copy prompt to reopen {row["id"]}', "Copy to reopen", "reopen")
        content += f'<div class="reopen">{reopen}</div>'
    elif row.get("options"):
        content += '<ul class="options">' + "".join(choice(row, option, index, state) for index, option in enumerate(row["options"])) + "</ul>"
    elif row.get("recommendation"):
        content += f'<div class="suggested-answer"><p class="answer-label">Suggested answer</p><p>{e(row["recommendation"])}</p></div>'
    return content + link_list(row.get("links", [])) + "</article>"


def revisit_card(row):
    return f'<article id="{card_id("tradeoff", row)}" class="card need"><p class="need-meta">{tradeoff_label(row)}</p><h3>{e(row["title"])}</h3><p class="context">{e(row["tradeoff"])}</p><div class="answer"><p class="answer-label">Revisit</p><p>{e(row["revisit"])}</p></div></article>'


def inbox_row(target, identity, title, selected=False):
    return (
        f'<button type="button" class="inbox-row" id="row-{target}" role="option" aria-selected="{str(selected).lower()}" aria-controls="{target}">'
        f'<span class="inbox-row-title">{e(title)}</span><span class="inbox-row-id">{e(identity)}</span></button>'
    )


def inbox_group(heading_id, title, tone, rows):
    return (
        f'<div class="inbox-group {tone}" role="group" aria-labelledby="{heading_id}"><span id="{heading_id}" class="inbox-group-title">{e(title)} <span class="count-pill{" attention" if tone == "open" else ""}">{len(rows)}</span></span>'
        + "".join(rows) + "</div>"
    )


def needs_view(state, judgment, quick, resolved, answered):
    """Decision cards in reading order, with the list that shows one card at a time in the dual-pane inbox."""
    empty = '<p class="empty">Nothing needs you in this snapshot.</p>'
    revisits = state.get("revisits", [])
    open_needs = judgment + quick
    if not (open_needs or resolved or revisits or answered):
        return empty
    selected = open_needs[0] if open_needs else None
    batch = batch_view(quick, state) if len(quick) > 1 else ""
    cards = (
        "".join(need_card(row, state, selected=row is selected) for row in judgment) + batch
        + "".join(need_card(row, state, selected=row is selected) for row in quick)
    ) or empty
    groups = ""
    for heading_id, title, rows in (("judgment-list", "Judgment calls", judgment), ("quick-list", "Quick picks", quick)):
        if rows:
            groups += inbox_group(heading_id, title, "open", [inbox_row(card_id("decision", row), row["id"], row["ask"], selected=row is selected) for row in rows])
    if resolved:
        groups += inbox_group("resolved-list", "Chief decided", "answered", [inbox_row(card_id("decision", row), row["id"], row["ask"]) for row in resolved])
        cards += collapsible("resolved-heading", "Chief decided", len(resolved), f'<div class="section-body">{"".join(need_card(row, state) for row in resolved)}</div>')
    if revisits:
        groups += inbox_group("revisits-list", "Worth a second look", "revisit", [inbox_row(card_id("tradeoff", row), row["id"], row["title"]) for row in revisits])
        cards += collapsible("revisits-heading", "Worth a second look", len(revisits), f'<div class="section-body">{"".join(revisit_card(row) for row in revisits)}</div>')
    if answered:
        groups += inbox_group("answered-list", "Answered decisions", "answered", [inbox_row(card_id("decision", row), row["id"], row["ask"]) for row in answered])
        cards += collapsible("answered-heading", "Answered decisions", len(answered), f'<div class="section-body">{"".join(need_card(row, state) for row in answered)}</div>')
    return f'<div class="inbox"><div class="inbox-list" role="listbox" aria-label="Decisions">{groups}</div><div class="inbox-detail">{cards}</div></div>'


class Program:
    """Lookups the work board needs across outcomes, layers, and decisions."""

    def __init__(self, state):
        self.needs = state["needs"]
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
        for need in self.needs:
            entry = next((entry for entry in need.get("blocks", []) if entry["id"] == row["id"]), None)
            if need["status"] == "open" and entry:
                items.append((entry["phase"] in HALTING, f'Decision · blocks {entry["phase"]}', need["id"], need["ask"]))
        items += [(True, STATES[self.by_id[identity]["state"]], identity, self.by_id[identity]["title"]) for identity in row.get("blockedBy", [])]
        if row.get("blocked"):
            items.append((True, "Other", "", row["blocked"]))
        bases = list(row.get("provisional", {}).get("on", []))
        if row["state"] not in TERMINAL:
            bases += [self.layers[layer["stackedOn"]][1]["id"] for layer in row.get("layers", [])
                      if "stackedOn" in layer and layer["status"] not in {"merged", "closed"}]
        for identity in dict.fromkeys(bases):
            if identity != row["id"] and self.by_id[identity]["state"] == "scrapped":
                items.append((True, "Scrapped base", identity, self.by_id[identity]["title"]))
        for layer in row.get("layers", []):
            parent, parent_row = self.layers.get(layer.get("stackedOn"), ({}, None))
            if parent.get("status") == "closed" and layer["status"] not in {"merged", "closed"}:
                items.append((True, "Closed base", parent["id"], parent_row["title"]))
        for _, parent in self.foreign_parents(row):
            if parent["state"] != "scrapped" and self.halted(parent):
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
    if "effectiveFinishLine" in row:
        value += f' → {FINISH_LINES[row["effectiveFinishLine"]]} while provisional'
    return f'<p class="finish">{icon("finish")}<span><span class="fact-label">Finish line</span> {e(value)}</span></p>'


def provisional_note(row):
    if "provisional" not in row:
        return ""
    provisional = row["provisional"]
    return (
        f'<div class="provisional-note"><p class="note-label">{icon("provisional")}Provisional</p>'
        f'<p><strong>Rests on</strong> {e(provisional["basis"])}</p><p><strong>Clears when</strong> {e(provisional["clears"])}</p>'
        '<p class="note-rule">It never lands while provisional.</p></div>'
    )


def results_view(row):
    if not row.get("results"):
        return ""
    items = "".join(
        f'<li>{link(result["label"], result["url"], "result-link", "result")}'
        + (f'<span class="result-access">{e(result["access"])}</span>' if result.get("access") else "") + "</li>"
        for result in row["results"]
    )
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
        content += f'<li>{prefix}<span class="blocker-kind">{e(kind)}</span> {e(text_value)}</li>'
    return content + "</ul></div>"


def work_card(row, program):
    reasons = program.blockers(row)
    heading_id = "work-" + hexed(row["id"])
    content = f'<article class="card work" id="{card_id("work-card", row)}" aria-labelledby="{heading_id}"><div class="work-top"><p class="work-id"><strong>{e(row["id"])}</strong> {e(row["repo"])}</p><p class="badges">{state_badges(row, program)}</p></div>'
    tags = [{"support": "Support", "follow-up": "Follow-up"}[row["kind"]]] if row["kind"] != "outcome" else []
    if row.get("required") is False:
        tags.append("Proposed · outside committed scope")
    if tags or row.get("tickets"):
        content += '<p class="tags">' + "".join(f'<span class="tag">{e(tag)}</span>' for tag in tags) + "".join(link(t["label"], t["url"], "ticket") for t in row.get("tickets", [])) + "</p>"
    content += f'<h4 id="{heading_id}" class="work-title">{e(row["title"])}</h4>'
    if row.get("description"):
        content += f'<p class="work-description">{e(row["description"])}</p>'
    content += finish_line(row)
    if row.get("unknownReason"):
        content += f'<p class="state-note">{icon("unknown")}{e(row["unknownReason"])}</p>'
    content += blocker_list([item[1:] for item in reasons if item[0]], "Blocked by", "blocked", "blocker")
    content += blocker_list([item[1:] for item in reasons if not item[0]], "Waits on", "waits", "blocker waits")
    content += results_view(row) + provisional_note(row) + layers_view(row, program)
    if row.get("origin") or row.get("evidence"):
        content += '<details class="work-context"><summary class="section-toggle" id="' + card_id("toggle-evidence", row) + '">Evidence and history</summary><div class="section-body">'
        if row.get("origin"):
            content += f'<p><strong>Origin</strong> {e(row["origin"])}</p>'
        content += link_list(row.get("evidence", []))
        content += "</div></details>"
    content += '<div class="work-footer"><div class="assignee">'
    if row.get("owner"):
        owner = link(row["owner"], row["sessionUrl"]) if row.get("sessionUrl") else e(row["owner"])
        content += f'<p class="owner">{owner}</p>'
    elif row.get("sessionUrl"):
        content += f'<p class="owner">{link("Owner session", row["sessionUrl"])}</p>'
    content += f'<p class="observation">Checked {when(row["updatedAt"])}</p></div>'
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


def render(state):
    validate(state)
    open_needs = [row for row in state["needs"] if row["status"] == "open"]
    judgment = [row for row in open_needs if row.get("weight") != "quick"]
    quick = [row for row in open_needs if row.get("weight") == "quick"]
    resolved = [row for row in state["needs"] if row["status"] == "resolved"]
    answered = [row for row in state["needs"] if row["status"] == "answered"]
    program = Program(state)

    needs_html = needs_view(state, judgment, quick, resolved, answered)

    stages = ""
    for key in STAGE_ORDER:
        rows = [row for row in state["work"] if display_stage(row) == key]
        if rows:
            blocked = sum(program.halted(row) for row in rows)
            alert = f'<span class="state blocked"><span class="sr-only">, </span>{icon("blocked")}{blocked} blocked</span>' if blocked else ""
            cards = "".join(work_card(row, program) for row in rows)
            stages += collapsible(f"stage-{key}", STATES[key], len(rows), f'<div class="section-body stage-cards">{cards}</div>', level=3, state=key, mark=icon(key), alert=alert)
    work_html = f'{overview(state["work"])}<div class="stage-board">{stages}</div>' if stages else '<p class="empty">No work recorded in this snapshot.</p>'

    facts = ""
    if state.get("finishLine"):
        facts += f'<p class="fact">{icon("finish")}<span><span class="fact-label">Finish line</span> {e(state["finishLine"])}</span></p>'
    facts += f'<p class="fact">{icon("snapshot")}<span><span class="fact-label">Snapshot</span> {when(state["updatedAt"], age=True)}</span></p>'
    demo = '<span class="demo" title="Fictional work, not live project status.">Illustrative example</span>' if state.get("demo") else ""
    content = f'<header class="masthead"><p class="eyebrow"><span>Chief of Staff</span>{demo}</p><h1>{e(state["title"])}</h1><p class="goal">{e(state["goal"])}</p><div class="facts">{facts}</div></header>'
    needs_badge = f'<span class="count-pill{" attention" if open_needs else ""}">{len(open_needs)}</span>'
    content += (
        '<nav class="navigation" aria-label="Program views"><div class="tabs" role="tablist" aria-label="Command center">'
        f'<button id="needs-tab" role="tab" aria-selected="true" aria-controls="needs-panel" tabindex="0">Needs you {needs_badge}</button>'
        f'<button id="work-tab" role="tab" aria-selected="false" aria-controls="work-panel" tabindex="-1">Work <span class="count-pill">{len(state["work"])}</span></button>'
        "</div></nav>"
        f'<section id="needs-panel" role="tabpanel" aria-labelledby="needs-tab" tabindex="0"><h2 class="sr-only">Needs you</h2>{needs_html}</section>'
        f'<section id="work-panel" role="tabpanel" aria-labelledby="work-tab" tabindex="0" hidden><h2 class="sr-only">Work</h2>{work_html}</section>'
    )
    template = (Path(__file__).resolve().parents[1] / "assets" / "command-center.html").read_text()
    page = template.replace("<!--TITLE-->", e(state["title"])).replace("<!--CONTENT-->", content)
    return page.replace("<!--SNAPSHOT-->", digest(page)).replace("<!--TEMPLATE-->", digest(template))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--revision", metavar="DECISION_ID", help="Print a decision's current revision")
    args = parser.parse_args()
    if args.revision is not None:
        try:
            state = validate(json.loads(args.state.read_text()))
            print(revision(next(row for row in state["needs"] if row["id"] == args.revision)))
        except StopIteration:
            parser.error(f"no decision {args.revision}")
        except (OSError, ValueError) as error:
            parser.error(str(error))
        return
    if args.state.resolve() == args.output.resolve():
        parser.error("--output must differ from --state")
    try:
        result = render(json.loads(args.state.read_text()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(args.output.resolve())


if __name__ == "__main__":
    main()
