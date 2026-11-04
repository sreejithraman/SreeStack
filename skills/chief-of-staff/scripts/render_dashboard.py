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
    "planned": "Planned", "building": "Building", "in-review": "In review",
    "mergeable": "Ready to merge", "merged": "Merged", "done": "Done", "closed": "Closed",
    "cancelled": "Cancelled", "unknown": "Unknown",
}
TERMINAL = {"merged", "done", "closed", "cancelled"}
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
    for row in work:
        path = f"work[{row['id']}]"
        for key in ("title", "repo"):
            text(row.get(key), f"{path}.{key}")
        text(row.get("state"), f"{path}.state")
        if row.get("state") not in STATES:
            raise ValueError(f"{path}.state must be one of {', '.join(STATES)}")
        text(row.get("kind"), f"{path}.kind")
        if row.get("kind") not in {"pr", "follow-up", "support"}:
            raise ValueError(f"{path}.kind must be pr, follow-up, or support")
        if row["kind"] == "pr" and row["state"] == "done":
            raise ValueError(f"{path}: PRs must use merged or mergeable, not done")
        if row["kind"] != "pr" and row["state"] in {"mergeable", "merged", "closed"}:
            raise ValueError(f"{path}: {row['state']} requires kind pr; promote a follow-up or support change to a PR row")
        if row["state"] in TERMINAL and (row.get("blockedBy") or row.get("blocked")):
            raise ValueError(f"{path}: terminal work cannot retain active blockers; keep history in the program record")
        timestamp(row.get("updatedAt"), f"{path}.updatedAt")
        for key in ("description", "owner", "blocked", "origin", "unknownReason"):
            if key in row:
                text(row[key], f"{path}.{key}")
        if "unknownReason" in row and row["state"] != "unknown":
            raise ValueError(f"{path}.unknownReason applies only to unknown state")
        if "url" in row and row["kind"] != "pr":
            raise ValueError(f"{path}.url is for a PR row; use tickets or evidence, or promote the row to a PR")
        for key in ("url", "sessionUrl"):
            if key in row:
                url(row[key], f"{path}.{key}")
        for key in ("tickets", "evidence"):
            links(row.get(key, []), f"{path}.{key}")
        if "required" in row and not isinstance(row["required"], bool):
            raise ValueError(f"{path}.required must be a boolean")
        if "stackedOn" in row:
            parent = text(row["stackedOn"], f"{path}.stackedOn")
            if row["kind"] != "pr" or parent == row["id"] or by_id.get(parent, {}).get("kind") != "pr":
                raise ValueError(f"{path}.stackedOn must name another PR row")
            if row["state"] not in TERMINAL and by_id[parent]["state"] in {"closed", "cancelled"}:
                raise ValueError(f"{path}.stackedOn names {by_id[parent]['state']} {parent}; record the restack or its blocker")
        for dependency in strings(row.get("blockedBy", []), f"{path}.blockedBy"):
            if dependency not in by_id:
                raise ValueError(f"{path}.blockedBy references missing work {dependency}")
    visiting, visited = set(), set()

    def visit(identity):
        if identity in visiting:
            raise ValueError(f"work dependency or stack cycle includes {identity}")
        if identity in visited:
            return
        visiting.add(identity)
        row = by_id[identity]
        for dependency in row.get("blockedBy", []) + ([row["stackedOn"]] if "stackedOn" in row else []):
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in by_id:
        visit(identity)
    for row in needs:
        path = f"needs[{row['id']}]"
        text(row.get("ask"), f"{path}.ask")
        text(row.get("status"), f"{path}.status")
        if row.get("status") not in {"open", "answered"}:
            raise ValueError(f"{path}.status must be open or answered")
        if row["status"] == "answered":
            text(row.get("answer"), f"{path}.answer")
        for key in ("recommendation", "answer"):
            if key in row:
                text(row[key], f"{path}.{key}")
        strings(row.get("context", []), f"{path}.context")
        for identity in strings(row.get("blocks", []), f"{path}.blocks"):
            if identity not in by_id:
                raise ValueError(f"{path}.blocks references missing work {identity}")
        if row["status"] == "open" and any(by_id[identity]["state"] in TERMINAL for identity in row.get("blocks", [])):
            raise ValueError(f"{path}: an open decision cannot block terminal work")
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
        links(row.get("links", []), f"{path}.links")
    for row in revisits:
        for key in ("title", "tradeoff", "revisit"):
            text(row.get(key), f"revisits[{row['id']}].{key}")
        if "source" in row:
            text(row["source"], f"revisits[{row['id']}].source")
    return state


STAGE_ORDER = ("planned", "building", "in-review", "merged", "done", "unknown", "closed", "cancelled")
ICONS = {
    "planned": "circle-dashed", "building": "hammer", "in-review": "scan-eye",
    "mergeable": "circle-check", "merged": "git-merge", "done": "check-check",
    "closed": "circle-x", "cancelled": "ban", "unknown": "circle-question-mark",
    "blocked": "triangle-alert", "copy": "copy", "copied": "check", "decision": "message-circle-question-mark",
    "recommended": "star", "pr": "git-pull-request", "finish": "flag", "snapshot": "clock", "tradeoff": "scale",
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


def when(value, age=False):
    return f'<time datetime="{e(value)}"{" data-age" if age else ""}>{e(value)}</time>'


def quoted(value):
    return json.dumps(" ".join(value.split()), ensure_ascii=False)


def revision(need):
    """Digest of the decision content a copied choice answers."""
    return hashlib.sha256(json.dumps(need, sort_keys=True).encode()).hexdigest()[:10]


def display_stage(row):
    """The stage a row reads under; a mergeable PR stays in review and adds a readiness badge."""
    return "in-review" if row["state"] == "mergeable" else row["state"]


def state_label(row):
    if row["state"] == "closed":
        return "Closed without merge"
    return STATES[display_stage(row)]


def collapsible(heading_id, title, count, body, *, level=2, state="", mark="", alert=""):
    """A section whose heading stays visible, and whose count stays readable, when collapsed."""
    return (
        f'<section class="collapsible" aria-labelledby="{heading_id}"><details open>'
        f'<summary class="section-toggle {state}"><h{level} id="{heading_id}" class="section-title">{mark}{e(title)} <span class="count">{count}</span>{alert}</h{level}></summary>'
        f"{body}</details></section>"
    )


def choice(row, option, index, state):
    prompt = (
        f'Decision {json.dumps(row["id"], ensure_ascii=False)} (revision {revision(row)}) in {quoted(state["title"])}\n'
        f'Question: {quoted(row["ask"])}\n'
        f'I choose option {index + 1}: {quoted(option["label"])}'
    )
    status_id = f'prompt-{row["id"].encode().hex()}-{index}'
    recommended = option.get("recommended", False)
    content = f'<li class="{"recommended" if recommended else "choice"}"><div class="choice-body"><p class="choice-heading"><strong>{e(option["label"])}</strong>'
    if recommended:
        content += f'<span class="recommended-label">{icon("recommended")}Recommended</span>'
    content += f'</p><p class="choice-effect">{e(option["effect"])}</p>'
    if recommended and row.get("recommendation"):
        content += f'<p class="choice-rationale">{e(row["recommendation"])}</p>'
    content += (
        f'</div><button type="button" class="copy-prompt" data-prompt="{e(prompt)}" '
        f'aria-label="{e("Copy prompt: " + option["label"])}" aria-describedby="{e(status_id)}">'
        f'<span class="idle">{icon("copy")}Copy prompt</span><span class="done">{icon("copied")}Copied</span></button>'
        f'<span class="copy-status" id="{e(status_id)}" role="status"></span>'
        f'<textarea class="manual-prompt" aria-label="{e("Prompt: " + option["label"])}" readonly hidden></textarea></li>'
    )
    return content


def need_card(row, state):
    answered = row["status"] == "answered"
    content = f'<article class="card need"><p class="need-meta"><span class="need-id{" settled" if answered else ""}">{icon("decision")}{"Answered" if answered else "Decision"} {e(row["id"])}</span>'
    if row.get("blocks"):
        content += f'<span>{"Affected" if answered else "Blocks"} {e(", ".join(row["blocks"]))}</span>'
    content += f'</p><h3>{e(row["ask"])}</h3>'
    if row.get("context"):
        content += '<ul class="context">' + "".join(f"<li>{e(item)}</li>" for item in row["context"]) + "</ul>"
    if answered:
        content += f'<div class="answer"><p class="answer-label">Your answer</p><p>{e(row["answer"])}</p></div>'
    elif row.get("options"):
        content += '<ul class="options">' + "".join(choice(row, option, index, state) for index, option in enumerate(row["options"])) + "</ul>"
    elif row.get("recommendation"):
        content += f'<div class="suggested-answer"><p class="answer-label">Suggested answer</p><p>{e(row["recommendation"])}</p></div>'
    return content + link_list(row.get("links", [])) + "</article>"


def revisit_card(row):
    content = f'<article class="card need"><p class="need-meta"><span class="need-id settled">{icon("tradeoff")}Tradeoff {e(row["id"])}</span>'
    if row.get("source"):
        content += f'<span>Source: {e(row["source"])}</span>'
    return content + f'</p><h3>{e(row["title"])}</h3><p class="context">{e(row["tradeoff"])}</p><div class="answer"><p class="answer-label">Revisit</p><p>{e(row["revisit"])}</p></div></article>'


def pending_parent(row, by_id):
    """The unmerged PR an active stacked row lands after."""
    parent = by_id.get(row.get("stackedOn"))
    return parent if parent and row["state"] not in TERMINAL and parent["state"] != "merged" else None


def blockers(row, needs, by_id):
    items = [("Decision", need["id"], need["ask"]) for need in needs if need["status"] == "open" and row["id"] in need.get("blocks", [])]
    items += [(STATES[by_id[identity]["state"]], identity, by_id[identity]["title"]) for identity in row.get("blockedBy", [])]
    if row.get("blocked"):
        items.append(("Other", "", row["blocked"]))
    parent = pending_parent(row, by_id)
    if parent and blockers(parent, needs, by_id):
        items.append(("Blocked parent", parent["id"], parent["title"]))
    return items


def pr_link(target):
    match = re.search(r"/(?:pull|pulls|merge_requests|pull-requests)/(\d+)/?$", urlsplit(url(target, "url")).path)
    return link(f"PR #{match[1]}" if match else "Open PR", target, "pr-link", "pr")


def work_card(row, needs, by_id):
    reasons = blockers(row, needs, by_id)
    heading_id = "work-" + row["id"].encode().hex()
    content = f'<article class="card work" aria-labelledby="{heading_id}"><div class="work-top"><p class="work-id"><strong>{e(row["id"])}</strong> {e(row["repo"])}</p><p class="badges">'
    primary = display_stage(row)
    content += f'<span class="state {e(primary)}">{icon(primary)}{e(state_label(row))}</span>'
    if row["state"] == "mergeable":
        content += f'<span class="state mergeable">{icon("mergeable")}{e(STATES["mergeable"])}</span>'
    if reasons:
        content += f'<span class="state blocked">{icon("blocked")}Blocked</span>'
    content += "</p></div>"
    tags = {"support": "Support", "follow-up": "Follow-up"}.get(row["kind"], "")
    tags = [tags] if tags else []
    if row.get("required") is False:
        tags.append("Proposed · outside committed scope")
    parent = pending_parent(row, by_id)
    if parent:
        tags.append(f'Lands after {parent["id"]}')
    if tags or row.get("tickets"):
        content += '<p class="tags">' + "".join(f'<span class="tag">{e(tag)}</span>' for tag in tags) + "".join(link(t["label"], t["url"], "ticket") for t in row.get("tickets", [])) + "</p>"
    content += f'<h4 id="{heading_id}" class="work-title">{e(row["title"])}</h4>'
    if row.get("description"):
        content += f'<p class="work-description">{e(row["description"])}</p>'
    if row.get("unknownReason"):
        content += f'<p class="state-note">{icon("unknown")}{e(row["unknownReason"])}</p>'
    if reasons:
        content += f'<div class="blocker"><p class="blocker-label">{icon("blocked")}Blocked by</p><ul>'
        for kind, identity, text_value in reasons:
            prefix = f'<span class="blocker-id">{e(identity)}</span> ' if identity else ""
            content += f'<li>{prefix}<span class="blocker-kind">{e(kind)}</span> {e(text_value)}</li>'
        content += "</ul></div>"
    if row.get("origin") or row.get("evidence"):
        content += '<details class="work-context"><summary class="section-toggle">Evidence and history</summary><div class="section-body">'
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
    if row.get("url"):
        content += pr_link(row["url"])
    return content + "</div></article>"


def overview(work):
    total = len(work)
    merged = sum(row["state"] == "merged" for row in work)
    counts = [(key, sum(display_stage(row) == key for row in work)) for key in STAGE_ORDER]
    counts = [(key, count) for key, count in counts if count]
    summary = ", ".join(f"{count} {STATES[key].lower()}" for key, count in counts)
    bar = "".join(f'<span class="segment {e(key)}" style="flex-grow:{count}"></span>' for key, count in counts)
    return (
        f'<div class="overview"><p class="work-count">{total} work item{"" if total == 1 else "s"} · {merged} merged</p>'
        f'<div class="progress" role="img" aria-label="{e(summary or "No work")}">{bar}</div>'
        "</div>"
    )


def render(state):
    validate(state)
    open_needs = [row for row in state["needs"] if row["status"] == "open"]
    answered = [row for row in state["needs"] if row["status"] == "answered"]
    by_id = {row["id"]: row for row in state["work"]}

    needs_html = "".join(need_card(row, state) for row in open_needs) or '<p class="empty">Nothing needs you in this snapshot.</p>'
    if state.get("revisits"):
        cards = "".join(revisit_card(row) for row in state["revisits"])
        needs_html += collapsible("revisits-heading", "Worth a second look", len(state["revisits"]), f'<div class="section-body">{cards}</div>')
    if answered:
        cards = "".join(need_card(row, state) for row in answered)
        needs_html += collapsible("answered-heading", "Answered decisions", len(answered), f'<div class="section-body">{cards}</div>')

    stages = ""
    for key in STAGE_ORDER:
        rows = [row for row in state["work"] if display_stage(row) == key]
        if rows:
            blocked = sum(bool(blockers(row, state["needs"], by_id)) for row in rows)
            alert = f'<span class="state blocked"><span class="sr-only">, </span>{icon("blocked")}{blocked} blocked</span>' if blocked else ""
            cards = "".join(work_card(row, state["needs"], by_id) for row in rows)
            stages += collapsible(f"stage-{key}", STATES[key], len(rows), f'<div class="section-body stage-cards">{cards}</div>', level=3, state=key, mark=icon(key), alert=alert)
    work_html = (overview(state["work"]) + stages) if stages else '<p class="empty">No work recorded in this snapshot.</p>'

    facts = ""
    if state.get("finishLine"):
        facts += f'<p class="fact">{icon("finish")}<span><span class="fact-label">Finish line</span> {e(state["finishLine"])}</span></p>'
    facts += f'<p class="fact">{icon("snapshot")}<span><span class="fact-label">Snapshot</span> {when(state["updatedAt"], age=True)}</span></p>'
    demo = '<span class="demo" title="Fictional work, not live project status.">Illustrative example</span>' if state.get("demo") else ""
    content = f'<header class="masthead"><p class="eyebrow"><span>Chief of Staff</span>{demo}</p><h1>{e(state["title"])}</h1><p class="goal">{e(state["goal"])}</p><div class="facts">{facts}</div></header>'
    needs_badge = f'<span class="tab-count{" attention" if open_needs else ""}">{len(open_needs)}</span>'
    content += (
        '<nav class="navigation" aria-label="Program views"><div class="tabs" role="tablist" aria-label="Command center">'
        f'<button id="needs-tab" role="tab" aria-selected="true" aria-controls="needs-panel" tabindex="0">Needs you {needs_badge}</button>'
        f'<button id="work-tab" role="tab" aria-selected="false" aria-controls="work-panel" tabindex="-1">Work <span class="tab-count">{len(state["work"])}</span></button>'
        "</div></nav>"
        f'<section id="needs-panel" role="tabpanel" aria-labelledby="needs-tab" tabindex="0"><h2 class="sr-only">Needs you</h2>{needs_html}</section>'
        f'<section id="work-panel" role="tabpanel" aria-labelledby="work-tab" tabindex="0" hidden><h2 class="sr-only">Work</h2>{work_html}</section>'
    )
    template = (Path(__file__).resolve().parents[1] / "assets" / "command-center.html").read_text()
    return template.replace("<!--TITLE-->", e(state["title"])).replace("<!--CONTENT-->", content)


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
