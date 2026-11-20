#!/usr/bin/env python3
"""Record program events in program.json, commit each one, and render the command center.

Each event command refuses an uncommitted program.json change, stamps the time
from this machine's clock, changes only what its event changes, validates,
commits, and renders. `status` reads PRs through `gh` and owner threads through
the T3 CLI. With --turn-end it commits nothing and fails while the verdict is
runnable, the record is dirty, an owner's thread state differs from the record,
or the page is behind. With --heartbeat it
commits nothing and says whether the coordinator should wake.
"""

import argparse
import contextlib
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from render_dashboard import (ACTIVE, DECISION_KEYS, DISCOVERY_IMPACTS, FINISH_LINES, GRANT, HALTING, IMAGE_SUFFIXES, LAYER_KEYS,
                              LIVE_LAYERS, OWNER_KEYS, OPTION_KEYS, PENDING_LANDINGS, PHASES, PICTURE_SHAPES,
                              PROGRAM_KEYS, READY_LAYERS, STALE_HOURS, STATES, TERMINAL, WORK_KEYS, assess,
                              check_pictures, committed, content_name, dead_base, effective_finish, fields, git,
                              hexed, invalid_base_work, known_keys, layout, now, observation, open_blocks, page_files,
                              pending_landing, place, quoted, records, revision, stage_page, unsatisfied, validate)


VERDICTS = ("pass", "fail", "blocked", "untested")
REPORT_KEYS = ("outcome", "state", "finishLine", "layers", "proof", "shown", "asks", "followups", "waits", "blocked")
ASK_KEYS = ("id", "question", "context", "pictures", "meanwhile", "recommendation", "options", "weight", "phase", "links")
FOLLOWUP_KEYS = ("id", "text", "evidence", "impact", "thread")
DISCOVERY_KEYS = ("id", "date", "origin", "work", "impact", "text", "evidence", "thread", "reply", "route", "status")
ROUTES = {
    "top-level": "`t3_thread_send` to the coordinator",
    "adopted": "`t3_thread_send` to the coordinator",
    "delegated": "End its turn with the report; the coordinator watches its PR",
}
REPORT_BLOCK = re.compile(r"\A\s*```json[ \t]*\n(.*?)\n```", re.S)
DECISION_LINE = re.compile(r'^Decision ("(?:[^"\\]|\\.)*") \(revision ([0-9a-f]+)\)(?:: (.*)| in .*)$')
CHOICE_LINE = re.compile(r'^I choose option (\d+): ("(?:[^"\\]|\\.)*")$')
DOCUMENT_ID = re.compile(r"[A-Za-z0-9_.~:@+-]+")  # one page-database path segment


class Refused(Exception):
    """The command changed nothing; its message says why."""



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



MAX_NEXT_CHARS = 280


LINE_SEPARATORS = ("\n", "\r", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")


def check_next(value):
    stripped = value.strip()
    if not stripped or any(sep in value for sep in LINE_SEPARATORS) or len(stripped) > MAX_NEXT_CHARS:
        raise Refused(
            f"next must be one short line (at most {MAX_NEXT_CHARS} characters) stating what happens next, "
            "not a history log; keep history in git commits, work rows, or reports"
        )
    return stripped


def set_next(state, value):
    if value is not None:
        state["next"] = check_next(value)


def build_init_state(title, goal, chief, request_text, next_action=None, request_sources=None, finish_line=None, hosting=None):
    """Build a fresh, validated program record."""
    request = {"text": request_text}
    if request_sources:
        request["sources"] = list(request_sources)
    state = {"title": title, "goal": goal}
    if finish_line:
        state["finishLine"] = finish_line
    state["chief"] = chief
    if hosting:
        state["hosting"] = hosting
    state["next"] = check_next(next_action) if next_action is not None else "Start ready outcomes"
    state["request"] = request
    state["decisions"] = []
    state["work"] = []
    return validate(state)


def update_grant(state, at, source=None, start_rule=None, resolve_rule=None, user_rule=None,
                 heartbeat_rule=None, wake_rule=None, landing_rule=None, hosting=None, finish_line=None):
    """Set or update program grant, landing authority, hosting URL, or program finish line."""
    authority_values = (("start", start_rule), ("resolve", resolve_rule), ("user", user_rule))
    grant_values = (*authority_values, ("heartbeat", heartbeat_rule), ("wake", wake_rule))
    touched_authority = any(value is not None for _, value in authority_values) or finish_line is not None
    touched_grant = any(value is not None for _, value in grant_values) or (source is not None and landing_rule is None)
    if not (touched_grant or landing_rule is not None or hosting is not None or finish_line is not None):
        raise Refused("grant needs at least one field to set (--start, --resolve, --user, --heartbeat, --wake, --landing, --hosting, or --finish-line)")
    if (touched_authority or landing_rule is not None) and not source:
        raise Refused("changing grant authority (--start, --resolve, --user, --landing, or --finish-line) needs --source: the user's message that authorized it")
    parts = []
    if touched_grant:
        grant = copy.deepcopy(state.get("grant", {}))
        order = (*GRANT, "heartbeat", "wake")
        if "date" not in grant or source is not None:
            put(grant, "date", at, order)
        if source is not None:
            put(grant, "source", source, order)
        for key, value in grant_values:
            if value is not None:
                put(grant, key, value, order)
        put(state, "grant", grant, PROGRAM_KEYS)
        parts.append("grant")
    if landing_rule is not None:
        put(state, "landingAuthority", {"date": at, "source": source, "text": landing_rule}, PROGRAM_KEYS)
        parts.append("landingAuthority")
    if hosting is not None:
        put(state, "hosting", hosting, PROGRAM_KEYS)
        parts.append("hosting")
    if finish_line is not None:
        put(state, "finishLine", finish_line, PROGRAM_KEYS)
        parts.append("finishLine")
    return f"update {', '.join(parts)}", []


def parse_blocks(entries):
    blocks = []
    for raw in entries:
        if ":" not in raw:
            raise Refused(f"--block {raw!r} must be WORK_ID:PHASE (phase: {', '.join(PHASES)})")
        work_id, phase = raw.rsplit(":", 1)
        blocks.append({"id": work_id, "phase": phase})
    return blocks


def archive_decision_history(row, at, note):
    """Move any settled answer and basis/source into rationale with the new note."""
    pieces = []
    if row.get("rationale"):
        pieces.append(row["rationale"])
    if "answer" in row:
        earlier = f"{at}: prior {row['status']} answer {json.dumps(row.pop('answer'), ensure_ascii=False)}"
        if "basis" in row:
            earlier += f" (basis: {row.pop('basis')})."
        elif "answerSource" in row:
            earlier += f" (source: {row.pop('answerSource')})."
        else:
            earlier += "."
        pieces.append(earlier)
    else:
        row.pop("basis", None)
        row.pop("answerSource", None)
    pieces.append(f"{at}: {note}")
    put(row, "rationale", " ".join(pieces), DECISION_KEYS)


def reopen_decision(state, at, identity, why, blocks=None):
    """Reopen a resolved or answered decision; keep its prior answer in rationale."""
    row = decision_row(state, identity)
    if row["status"] not in {"resolved", "answered"}:
        raise Refused(f"{identity} is {row['status']}; only a resolved or answered decision can be reopened")
    archive_decision_history(row, at, f"reopened: {why}")
    row["status"] = "open"
    put(row, "reopened", row.get("reopened", 0) + 1, DECISION_KEYS)
    row.pop("applied", None)
    row.pop("stalePick", None)
    by_id = {item["id"]: item for item in state["work"]}
    notes = []
    if blocks is not None:
        put(row, "blocks", parse_blocks(blocks), DECISION_KEYS)
    elif "blocks" in row:
        landed = [entry["id"] for entry in row["blocks"] if by_id.get(entry["id"], {}).get("state") in TERMINAL]
        kept = [entry for entry in row["blocks"] if entry["id"] not in landed]
        if kept:
            row["blocks"] = kept
        else:
            row.pop("blocks", None)
        if landed:
            notes.append(f"dropped terminal blocks ({', '.join(landed)}); add a follow-up outcome if landed work needs changes")
    affected = ", ".join(entry["id"] for entry in row.get("blocks", []))
    notes.append(f"notify affected owners ({affected or 'if any'}) and withdraw any affected landing release")
    return f"{identity} reopened", notes


def withdraw_decision(state, at, identity, why):
    """Withdraw a decision and preserve its history in rationale."""
    row = decision_row(state, identity)
    if row["status"] == "withdrawn":
        raise Refused(f"{identity} is already withdrawn")
    archive_decision_history(row, at, f"withdrawn: {why}")
    row["status"] = "withdrawn"
    row.pop("applied", None)
    row.pop("stalePick", None)
    return f"{identity} withdrawn", ["reconcile any blockers or work that depended on this decision"]


def move_coordinator(state, chief):
    """Transfer program ownership to a new coordinator thread and update live owner routes."""
    pending = [row["id"] for row in state.get("landings", []) if row["state"] in PENDING_LANDINGS]
    if pending:
        raise Refused(
            f"pending landing(s) {', '.join(pending)} are still active under the current coordinator; "
            "withdraw each release and confirm forge cancellation (or record merged) before moving"
        )
    state["chief"] = chief
    updated = []
    for row in state["work"]:
        if row["state"] not in TERMINAL and "owner" in row:
            put(row["owner"], "route", ROUTES["top-level"], OWNER_KEYS)
            updated.append(row["id"])
    notes = ["do not publish from this thread; delete your heartbeat and send the handoff to the new coordinator"]
    if updated:
        notes.append(f"updated owner.route for {', '.join(updated)}")
    return f"move coordinator to {chief}", notes


SCRAP_VERBS = re.compile(r"\bscrap(?:ping|ped)?\b")
REBASE_VERBS = re.compile(r"\b(rebase|restack|retarget)\b")
NEGATED_SCRAP = re.compile(r"\b(instead of|rather than|do not|don't|not)\s+(scrapping|scrap)\b")
NEGATED_REBASE = re.compile(r"\b(instead of|rather than|do not|don't|not)\s+(rebasing|rebase|restacking|restack|retargeting|retarget)\b")
ONTO_TARGET = re.compile(r"\bonto\s+(?:`([^`]+)`|\"([^\"]+)\"|'([^']+)'|(\S+))", re.I)


def is_base_repair_decision(row):
    """True when this decision's options represent a scrap-or-rebase base-repair choice."""
    options = row.get("options", [])
    if any(isinstance(opt.get("action"), dict) and opt["action"].get("type") in {"scrap", "rebase"} for opt in options):
        return True
    has_scrap = any(SCRAP_VERBS.search(opt.get("label", "").lower()) and not NEGATED_SCRAP.search(opt.get("label", "").lower())
                    for opt in options)
    has_rebase = any(REBASE_VERBS.search(opt.get("label", "").lower()) and not NEGATED_REBASE.search(opt.get("label", "").lower())
                     for opt in options)
    return has_scrap and has_rebase


def atomic_halting_work(state, decision_id):
    """Active work IDs with an invalid base that require atomic work handling when decision_id is answered."""
    by_id = {row["id"]: row for row in state["work"]}
    layers = {layer["id"]: (layer, row) for row in state["work"] for layer in row.get("layers", [])}
    broken = invalid_base_work(state["work"], by_id, layers)
    target = next((row for row in state["decisions"] if row["id"] == decision_id), None)
    base_repair = is_base_repair_decision(target) if target else False
    affected = []
    for work_id in broken:
        halting = open_blocks(state, work_id, HALTING)
        if decision_id in halting and (len(halting) == 1 or base_repair):
            affected.append(work_id)
    return affected


def check_work_decision_action(chosen, scrap, rebase_onto, stack_on=None, work_id=None, option=None):
    """Verify the chosen option unambiguously authorizes --scrap or --rebase-onto (and its exact target)."""
    action = option.get("action") if isinstance(option, dict) else None
    if isinstance(action, dict):
        if "work" in action and work_id is not None and action["work"] != work_id:
            raise Refused(f"chosen option action targets {action['work']}, not {work_id}")
        if scrap:
            if action.get("type") != "scrap":
                raise Refused(f"--scrap conflicts with typed option action {action.get('type')!r}")
            return
        if rebase_onto is not None:
            if action.get("type") != "rebase":
                raise Refused(f"--rebase-onto conflicts with typed option action {action.get('type')!r}")
            if action.get("onto") != rebase_onto:
                raise Refused(f"--rebase-onto {rebase_onto!r} does not match typed option target {action.get('onto')!r}")
            if action.get("stackOn") != stack_on:
                raise Refused(f"--stack-on {stack_on!r} does not match typed option stackOn {action.get('stackOn')!r}")
            return
    lower = chosen.lower()
    if scrap:
        if (not SCRAP_VERBS.search(lower) or NEGATED_SCRAP.search(lower)
                or REBASE_VERBS.search(lower) or re.search(r"\b(keep|continue)\b", lower)):
            raise Refused(f"--scrap is not unambiguously authorized by chosen option {chosen!r}")
    if rebase_onto is not None:
        if (not REBASE_VERBS.search(lower) or NEGATED_REBASE.search(lower)
                or (SCRAP_VERBS.search(lower) and not NEGATED_SCRAP.search(lower))):
            raise Refused(f"--rebase-onto is not unambiguously authorized by chosen option {chosen!r}")
        match = ONTO_TARGET.search(chosen)
        if match:
            quoted_target = match[4] is None
            raw_named = next(g for g in match.groups() if g is not None)
            named = raw_named if quoted_target else raw_named.rstrip(".,;:)")
            allowed = {rebase_onto} | ({stack_on} if stack_on else set())
            if named not in allowed and (quoted_target or named.lower() not in {"a", "an", "the", "new", "another"}):
                raise Refused(f"--rebase-onto {rebase_onto!r} does not match target {named!r} in chosen option {chosen!r}")


def mutate_work(state, at, identity, add=False, title=None, repo=None, kind=None, work_state=None,
                unknown_reason=None, description=None, scope=None, finish_line=None, finish_line_reason=None,
                origin=None, blocked=None, clear_blocked=False, blocked_by=None, clear_blocked_by=False,
                sources=None, optional=False, required=False, prov_basis=None, prov_clears=None, prov_on=None,
                clear_provisional=False, scrap=False, rebase_onto=None, stack_on=None,
                decision_id=None, decision_option=None, decision_text=None, answer_source=None,
                pasted_text=None, stored_documents=None):
    """Add, update, scrap, or rebase a work row, optionally answering its decision in the same commit."""
    if scrap and rebase_onto is not None:
        raise Refused("choose either --scrap or --rebase-onto, not both")
    if stack_on is not None and rebase_onto is None:
        raise Refused("--stack-on requires --rebase-onto")
    existing = next((row for row in state["work"] if row["id"] == identity), None)
    notes = []
    if add:
        if existing is not None:
            raise Refused(f"work {identity} already exists; omit --add to update it")
        if not title or not repo:
            raise Refused("work --add needs --title and --repo")
        row = {"id": identity, "title": title, "repo": repo, "kind": kind or "outcome",
               "state": work_state or "planned", "checkedAt": at}
        state["work"].append(row)
        action = f"{identity} add: {title}"
    else:
        if existing is None:
            raise Refused(f"no work {identity}; pass --add to create it")
        row = existing
        action = f"{identity} update"

    layers_by_id = {layer["id"]: (layer, owner_row) for owner_row in state["work"]
                    for layer in owner_row.get("layers", [])}
    effective_repo = repo if (repo is not None and not add) else row["repo"]
    if stack_on is not None:
        if stack_on not in layers_by_id:
            raise Refused(f"no layer {stack_on} to stack on")
        parent_layer, parent_row = layers_by_id[stack_on]
        if parent_row["repo"] != effective_repo:
            raise Refused(f"cannot stack {identity} ({effective_repo}) on {stack_on} in {parent_row['repo']}")
        if parent_layer["branch"] != rebase_onto:
            raise Refused(f"--rebase-onto {rebase_onto!r} does not match {stack_on}'s branch {parent_layer['branch']!r}")

    if decision_id is not None:
        target_decision = decision_row(state, decision_id)
        if target_decision["status"] != "open":
            raise Refused(f"{decision_id} is {target_decision['status']}; work --decision only answers an open decision")
        if not any(entry["id"] == identity for entry in target_decision.get("blocks", [])):
            raise Refused(f"{decision_id} does not block {identity}")
        if not scrap and rebase_onto is None and atomic_halting_work(state, decision_id):
            raise Refused(
                f"{decision_id} authorizes a base repair on {identity}; pass --scrap or --rebase-onto in the same command"
            )
        options = target_decision.get("options", [])
        extra_receipt, extra_delete = None, None
        if pasted_text is not None:
            if not answer_source:
                raise Refused("--decision with --pasted needs --answer-source")
            choices = [c for c in pasted_choices(pasted_text, state) if c[0] == decision_id]
            if not choices:
                raise Refused(f"pasted text contains no choice for {decision_id}")
            _, digest, number, label = choices[-1]
            if (revision(target_decision) != digest or not 1 <= number <= len(options)
                    or quoted(options[number - 1]["label"]) != quoted(label)):
                raise Refused(f"{decision_id} changed since the page showed it; ask again")
            opt_obj = options[number - 1]
            chosen, source_used = opt_obj["label"], answer_source
        elif decision_option is not None or decision_text is not None:
            if not answer_source:
                raise Refused("--decision with --option or --text needs --answer-source")
            if decision_option is not None:
                chosen = option_label(target_decision, decision_option)
                opt_obj = options[decision_option - 1]
            else:
                chosen = decision_text
                matches = [opt for opt in options if quoted(opt["label"]) == quoted(chosen)]
                if len(matches) > 1:
                    raise Refused(f"multiple options match {chosen!r}; pass --option <number>")
                opt_obj = matches[0] if len(matches) == 1 else None
            source_used = answer_source
        elif stored_documents is not None:
            matched = []
            for document in stored_documents:
                if not DOCUMENT_ID.fullmatch(document["id"]) or document["id"] in {".", ".."}:
                    continue
                path, data = f"picks/{document['id']}", document["data"]
                if data.get("decision") != decision_id:
                    continue
                name = f"{path} (version {document['version']})"
                digest, number, label = (data.get(key) for key in ("revision", "option", "label"))
                if not (isinstance(digest, str) and type(number) is int and isinstance(label, str)
                        and label.strip() and document["id"] == f"{hexed(decision_id)}-{digest}"):
                    continue
                receipt = f"{name} {document['updatedAt']}"
                if receipt in target_decision.get("picksRead", []):
                    continue
                if (revision(target_decision) == digest and 1 <= number <= len(options)
                        and quoted(options[number - 1]["label"]) == quoted(label)):
                    matched.append((name, options[number - 1], receipt))
            if not matched:
                raise Refused(f"no current-revision stored pick for {decision_id}")
            name, opt_obj, extra_receipt = matched[-1]
            chosen = opt_obj["label"]
            source_used = f"The user's pick on the command center, stored at {name}"
            extra_delete = f"delete: {name}"
        else:
            raise Refused("--decision on work needs --option, --text, --pasted (with --answer-source), or --stored")
        check_work_decision_action(chosen, scrap, rebase_onto, stack_on, identity, opt_obj)
        _, answer_notes = settle(state, at, decision_id, chosen, "answered", source=source_used, allow_atomic=True)
        if extra_receipt:
            put(target_decision, "picksRead", target_decision.get("picksRead", []) + [extra_receipt], DECISION_KEYS)
        notes.extend(answer_notes)
        if extra_delete:
            notes.append(extra_delete)
        elif stored_documents is not None:
            _, stored_notes = answer_stored(state, at, stored_documents, answered=[decision_id])
            notes.extend(stored_notes)

    for key, value in (
        ("title", title if not add else None), ("repo", repo if not add else None),
        ("kind", kind if not add else None), ("description", description), ("scope", scope),
        ("finishLine", finish_line), ("finishLineReason", finish_line_reason), ("origin", origin),
        ("unknownReason", unknown_reason),
    ):
        if value is not None:
            put(row, key, value, WORK_KEYS)
    if work_state is not None and not add:
        row["state"] = work_state
        if work_state != "unknown":
            row.pop("unknownReason", None)
    if sources is not None:
        replace_list(row, "sources", sources)
    if clear_blocked:
        row.pop("blocked", None)
    elif blocked is not None:
        put(row, "blocked", blocked, WORK_KEYS)
    if clear_blocked_by:
        row.pop("blockedBy", None)
    elif blocked_by is not None:
        replace_list(row, "blockedBy", blocked_by)
    if optional:
        put(row, "required", False, WORK_KEYS)
    elif required:
        row.pop("required", None)

    if clear_provisional:
        row.pop("provisional", None)
    elif prov_basis is not None or prov_clears is not None or prov_on is not None:
        provisional = copy.deepcopy(row.get("provisional", {}))
        if prov_basis is not None:
            put(provisional, "basis", prov_basis, ("basis", "clears", "on"))
        if prov_clears is not None:
            put(provisional, "clears", prov_clears, ("basis", "clears", "on"))
        if prov_on is not None:
            put(provisional, "on", prov_on, ("basis", "clears", "on"))
        put(row, "provisional", provisional, WORK_KEYS)

    if scrap:
        if pending_landing(state, identity):
            raise Refused(f"{identity} has pending landing {pending_landing(state, identity)['id']}; withdraw it before scrapping")
        row["state"] = "scrapped"
        row.pop("blockedBy", None)
        row.pop("blocked", None)
        row.pop("unknownReason", None)
        action = f"{identity} scrapped"

    if rebase_onto is not None:
        if pending_landing(state, identity):
            raise Refused(f"{identity} has pending landing {pending_landing(state, identity)['id']}; withdraw it before rebasing")
        dead_ids = {item["id"] for item in state["work"] if dead_base(item)}
        live_layers = [layer for layer in row.get("layers", []) if layer["status"] in LIVE_LAYERS]
        bottom_layers = [layer for layer in live_layers
                         if "stackedOn" not in layer or layers_by_id.get(layer["stackedOn"], (None, {}))[1].get("id") != identity]
        target_layers = bottom_layers or live_layers[:1]
        removed_layer_ids = [layer["stackedOn"] for layer in target_layers
                             if "stackedOn" in layer and layer["stackedOn"] != stack_on]
        for layer in target_layers:
            put(layer, "base", rebase_onto, LAYER_KEYS)
            if stack_on is not None:
                put(layer, "stackedOn", stack_on, LAYER_KEYS)
            else:
                layer.pop("stackedOn", None)
        # Rebasing invalidates readiness earned on the previous base until proof and checks refresh.
        if row["state"] == "ready":
            row["state"] = "in-review"
            row.pop("acceptance", None)
        for layer in live_layers:
            if layer["status"] == "ready":
                layer["status"] = "open" if layer.get("url") else "local"
        unmerged_parent = (
            layers_by_id[stack_on][1]
            if (stack_on is not None and layers_by_id[stack_on][1]["id"] != identity
                and layers_by_id[stack_on][0]["status"] != "merged")
            else None
        )
        remaining_unmerged_stack_owners = {
            layers_by_id[layer["stackedOn"]][1]["id"]
            for layer in live_layers
            if "stackedOn" in layer and layer["stackedOn"] in layers_by_id
            and layers_by_id[layer["stackedOn"]][1]["id"] != identity
            and layers_by_id[layer["stackedOn"]][0]["status"] != "merged"
        }
        detached_owners = {
            layers_by_id[lid][1]["id"]
            for lid in removed_layer_ids
            if lid in layers_by_id and layers_by_id[lid][1]["id"] not in remaining_unmerged_stack_owners
        }
        drop_ids = dead_ids | detached_owners
        if unmerged_parent is not None:
            provisional = copy.deepcopy(row.get("provisional", {}))
            old_on = provisional.get("on", [])
            removed_tokens = [item for item in old_on if item in drop_ids] + removed_layer_ids
            kept_on = [item for item in old_on if item not in drop_ids and item != unmerged_parent["id"]]
            new_on = [*kept_on, unmerged_parent["id"]]
            stale_basis = any(re.search(rf"\b{re.escape(tok)}\b", provisional.get("basis", "")) for tok in removed_tokens)
            stale_clears = any(re.search(rf"\b{re.escape(tok)}\b", provisional.get("clears", "")) for tok in removed_tokens)
            only_dropped = bool(old_on) and not kept_on
            default_basis = (f"Stacked on {unmerged_parent['id']} ({stack_on})" if not kept_on
                             else f"Rested on {', '.join(new_on)} (stacked on {stack_on})")
            default_clears = f"{', '.join(new_on)} land" if len(new_on) > 1 else f"{unmerged_parent['id']} lands"
            basis_val = prov_basis or (default_basis if (only_dropped or stale_basis) else provisional.get("basis")) or default_basis
            clears_val = prov_clears or (default_clears if (only_dropped or stale_clears) else provisional.get("clears")) or default_clears
            put(provisional, "basis", basis_val, ("basis", "clears", "on"))
            put(provisional, "clears", clears_val, ("basis", "clears", "on"))
            put(provisional, "on", new_on, ("basis", "clears", "on"))
            put(row, "provisional", provisional, WORK_KEYS)
        elif "provisional" in row and not clear_provisional:
            old_on = row["provisional"].get("on", [])
            removed_tokens = [item for item in old_on if item in drop_ids] + removed_layer_ids
            kept_on = [item for item in old_on if item not in drop_ids]
            if kept_on:
                row["provisional"]["on"] = kept_on
                if prov_basis is None and any(re.search(rf"\b{re.escape(tok)}\b", row["provisional"].get("basis", "")) for tok in removed_tokens):
                    row["provisional"]["basis"] = f"Rested on {', '.join(kept_on)}"
                if prov_clears is None and any(re.search(rf"\b{re.escape(tok)}\b", row["provisional"].get("clears", "")) for tok in removed_tokens):
                    row["provisional"]["clears"] = f"{', '.join(kept_on)} land" if len(kept_on) > 1 else f"{kept_on[0]} lands"
            elif "on" in row["provisional"]:
                if prov_basis is not None or prov_clears is not None:
                    row["provisional"].pop("on", None)
                else:
                    row.pop("provisional", None)
        action = f"{identity} rebased onto {rebase_onto}"

    if not add and not any((
        title, repo, kind, work_state, unknown_reason, description, scope, finish_line, finish_line_reason,
        origin, blocked, clear_blocked, blocked_by, clear_blocked_by, sources, optional, required,
        prov_basis, prov_clears, prov_on, clear_provisional, scrap, rebase_onto, decision_id,
    )):
        raise Refused("work needs at least one field to update, or --add to create a row")
    row["checkedAt"] = at
    return action, notes


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
    if session:
        record.pop("seen", None)
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


def adopt_picture(value, path, files):
    """The files/ name of a copy of the picture at an absolute path; files gains its record path and content."""
    source = Path(value) if isinstance(value, str) else Path()
    if not source.is_absolute() or source.suffix.lower() not in IMAGE_SUFFIXES:
        raise Refused(f"{path} must be an absolute path to a {', '.join(IMAGE_SUFFIXES)} file")
    try:
        content = source.read_bytes()
    except OSError as error:
        raise Refused(f"cannot read {source}: {error.strerror}") from None
    name = content_name(content, source.suffix)
    files[name] = content
    return name


def shown_pictures(block, files):
    """Point each shown picture at a copy in the program's files folder, named by its content."""
    for index, item in enumerate(block.get("shown") or []):
        if isinstance(item, dict) and "image" in item:
            item["image"] = adopt_picture(item["image"], f"report shown[{index}].image", files)


def ask_pictures(ask, number, files):
    """Point each picture of a new ask, its own and its options', at a copy in the program's files folder."""
    pictures = ask.get("pictures")
    images = pictures.get("images") if isinstance(pictures, dict) else None
    for index, item in enumerate(images if isinstance(images, list) else []):
        if isinstance(item, dict) and "image" in item:
            item["image"] = adopt_picture(item["image"], f"report asks[{number}].pictures.images[{index}].image", files)
    for index, option in enumerate(ask.get("options") if isinstance(ask.get("options"), list) else []):
        if isinstance(option, dict) and "image" in option:
            option["image"] = adopt_picture(option["image"], f"report asks[{number}].options[{index}].image", files)


def report(state, at, work, block, source, files):
    """Apply an owner report block: each field it names replaces that part of the record.

    files gains each picture the report adopts: its record path and content, for the commit that records it.
    """
    only(block, REPORT_KEYS, "block")
    row = work_row(state, work)
    if block.get("outcome") != work:
        raise Refused(f"the report block names outcome {block.get('outcome')!r}, not {work}")
    if block.get("state") not in STATES:
        raise Refused(f"report state must be one of {', '.join(STATES)}")
    if block["state"] in TERMINAL:
        raise Refused(f"a report cannot record {block['state']}: run status, which reads merges at the forge, "
                      "or record a scrap by hand")
    merged = {layer["id"]: layer for layer in row.get("layers", []) if layer["status"] == "merged"}
    if "layers" in block:
        reported = {layer.get("id"): layer for layer in objects(block["layers"], "layers")}
        for identity, layer in reported.items():
            if layer.get("status") == "merged" and identity not in merged:
                raise Refused(f"report layer {identity} claims merged; report it ready and run status, "
                              "which reads merges at the forge")
        for identity, layer in merged.items():
            if reported.get(identity) != layer:
                raise Refused(f"report layer {identity} must repeat its merged record unchanged; the forge owns it")
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
        shown_pictures(block, files)
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
        ask_pictures(ask, index, files)
        decision = {"id": ask.get("id"), "question": ask.get("question"), "date": at, "source": source, "status": "open"}
        decision |= {key: ask[key] for key in ("context", "pictures", "meanwhile", "recommendation", "options", "weight")
                     if key in ask}
        decision["blocks"] = [{"id": work, "phase": ask.get("phase", "acceptance")}]
        if "links" in ask:
            decision["links"] = ask["links"]
        state["decisions"].append({key: decision[key] for key in DECISION_KEYS if key in decision})
        asked.append(ask.get("id"))
    followed, to_route, to_reply = [], [], []
    discoveries = list(state.get("discoveries", []))
    existing_by_id = {entry["id"]: entry for entry in discoveries if entry.get("id")}
    for index, entry in enumerate(objects(block.get("followups", []), "followups")):
        only(entry, FOLLOWUP_KEYS, f"followups[{index}]")
        fields(entry, f"followups[{index}]", ("id", "text"), ("evidence", "impact", "thread"))
        if "impact" in entry and entry["impact"] not in DISCOVERY_IMPACTS:
            raise Refused(f"followups[{index}].impact must be one of {', '.join(DISCOVERY_IMPACTS)}")
        existing_entry = existing_by_id.get(entry["id"])
        if existing_entry is not None:
            if existing_entry.get("work") != work or existing_entry.get("text") != entry["text"]:
                raise Refused(
                    f"followup ID {entry['id']!r} already belongs to another discovery "
                    f"({existing_entry.get('work') or existing_entry.get('origin')}); prefix owner followup IDs with {work}-"
                )
            changed = []
            for key in ("impact", "evidence", "thread"):
                if key in entry and entry[key] != existing_entry.get(key):
                    put(existing_entry, key, entry[key], DISCOVERY_KEYS)
                    changed.append(key)
            if "thread" in entry and existing_entry.get("reply") is None:
                put(existing_entry, "reply", "pending", DISCOVERY_KEYS)
                changed.append("reply")
            if not changed:
                notes.append(f"followup {entry['id']} is already recorded; left as it is")
                continue
            if "thread" in changed:
                put(existing_entry, "reply", "pending", DISCOVERY_KEYS)
            if "impact" in changed and existing_entry.get("status") == "routed":
                prior = existing_entry["route"]
                existing_entry["route"] = "pending"
                put(existing_entry, "status", "open", DISCOVERY_KEYS)
                if existing_entry.get("thread"):
                    put(existing_entry, "reply", "pending", DISCOVERY_KEYS)
                notes.append(f"followup {entry['id']} impact changed ({existing_entry['impact']}); reopened from {prior!r} for re-routing")
                to_route.append(entry["id"])
            elif existing_entry.get("status") == "routed" and existing_entry.get("reply") == "pending":
                notes.append(
                    f"followup {entry['id']} attached thread {existing_entry['thread']} to routed home "
                    f"({existing_entry['route']}); send it to {work} and run `discovery --id {entry['id']} --reply-sent`"
                )
                to_reply.append(entry["id"])
            else:
                notes.append(f"followup {entry['id']} updated ({', '.join(changed)})")
                if existing_entry.get("status") == "open":
                    to_route.append(entry["id"])
            followed.append(entry["id"])
            continue
        item_row = {
            "id": entry["id"], "date": at, "origin": f"{work} report ({source})",
            "work": work, "text": entry["text"], "route": "pending", "status": "open",
        }
        for key in ("impact", "evidence", "thread"):
            if key in entry:
                item_row[key] = entry[key]
        if "thread" in entry:
            item_row["reply"] = "pending"
        ordered = {key: item_row[key] for key in DISCOVERY_KEYS if key in item_row}
        existing_by_id[entry["id"]] = ordered
        discoveries.append(ordered)
        followed.append(entry["id"])
        to_route.append(entry["id"])
    if followed:
        replace_list(state, "discoveries", discoveries, PROGRAM_KEYS)
    row["checkedAt"] = at
    message = f"{work} report: {block['state']}"
    if asked:
        message += f", asks {', '.join(asked)}"
        notes.append(f"triage {', '.join(asked)}: resolve it with `resolve`, or ask the user")
    if followed:
        message += f", followups {', '.join(followed)}"
        if to_route:
            notes.append(f"route {', '.join(to_route)} with `discovery --id <ID> --route ...`")
    return message, notes


def replace_list(row, key, value, order=WORK_KEYS):
    if value:
        put(row, key, value, order)
    else:
        row.pop(key, None)


def settle(state, at, identity, answer, status, source=None, basis=None, allow_atomic=False):
    """Record an answer: answered when it is the user's, resolved when it is the coordinator's call."""
    row = decision_row(state, identity)
    if row["status"] == "withdrawn":
        raise Refused(f"{identity} was withdrawn")
    if status == "resolved" and row["status"] != "open":
        raise Refused(f"{identity} is {row['status']}; only an open decision can be resolved")
    if not allow_atomic and row["status"] == "open":
        broken = atomic_halting_work(state, identity)
        if broken:
            raise Refused(
                f"atomic work transition needed for {identity} (invalid base on {', '.join(broken)}): "
                f"run work --id {broken[0]} --scrap|--rebase-onto <branch> --decision {identity} ..."
            )
    if row["status"] != "open":
        earlier = f"{at}: replaced the earlier {row['status']} answer {json.dumps(row['answer'], ensure_ascii=False)}"
        earlier += f" (basis: {row.pop('basis')})." if "basis" in row else f" (source: {row.pop('answerSource')})."
        put(row, "rationale", f"{row['rationale']} {earlier}" if row.get("rationale") else earlier, DECISION_KEYS)
    row["status"] = status
    row.pop("stalePick", None)
    put(row, "answer", answer, DECISION_KEYS)
    if status == "answered":
        put(row, "answerSource", source, DECISION_KEYS)
    else:
        put(row, "basis", basis, DECISION_KEYS)
    put(row, "applied", False, DECISION_KEYS)
    affected = ", ".join(f"{entry['id']} ({entry['phase']})" for entry in row.get("blocks", []))
    return f"{identity} {status}", [f"update the owners of {affected or 'the work it affects'}, then run applied"]


def option_label(row, number):
    options = row.get("options", [])
    if not 1 <= number <= len(options):
        raise Refused(f"{row['id']} has no option {number}")
    return options[number - 1]["label"]


def pasted_choices(text, state=None):
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
            identity, digest = pending
            if state is not None:
                row = next((r for r in state["decisions"] if r["id"] == identity), None)
                if row is None or row["status"] not in {"resolved", "answered"} or revision(row) != digest:
                    raise Refused(f"{identity}: stale reopen prompt (revision {digest} does not match current settled revision); ask again")
            raise Refused(f"{identity}: verified reopen request (revision {digest}); run record.py reopen --decision {identity} --why \"...\"")
    if not choices:
        raise Refused("no decision choice found in the pasted text")
    return choices


def answer_pasted(state, at, text, source, allow_atomic_only=False):
    """Record each pasted choice that matches its open decision's current revision; return the rest to ask again."""
    recorded, stale, atomic = [], [], []
    for identity, digest, number, label in pasted_choices(text, state):
        row = next((row for row in state["decisions"] if row["id"] == identity), None)
        options = row.get("options", []) if row else []
        if (row is None or row["status"] != "open" or revision(row) != digest
                or not 1 <= number <= len(options) or quoted(options[number - 1]["label"]) != quoted(label)):
            stale.append(identity)
            continue
        broken_work = atomic_halting_work(state, identity)
        if broken_work:
            atomic.append((identity, broken_work))
            continue
        settle(state, at, identity, options[number - 1]["label"], "answered", source=source)
        recorded.append(identity)
    notes = [f"ask again: {identity} changed or closed since the page showed it" for identity in stale]
    for identity, works in atomic:
        notes.append(
            f"atomic work transition needed for {identity} (invalid base on {', '.join(works)}): "
            f"run work --id {works[0]} --scrap|--rebase-onto <branch> --decision {identity} --pasted --answer-source ..."
        )
    if not recorded:
        if allow_atomic_only and atomic and not stale:
            return "pasted choices deferred for atomic work transition", notes, []
        raise Refused("; ".join(notes))
    affected = sorted({entry["id"] for identity in recorded for entry in decision_row(state, identity).get("blocks", [])})
    notes.append(f"update the owners of {', '.join(affected) or 'the work it affects'}, then run applied")
    return f"{', '.join(recorded)} answered", notes, recorded


def stored_picks(text):
    """Each pick document in saved db_query output: one JSON object per line with its id and data.

    The wrapping tags are skipped. The summary line's count must match the documents read, so a pick lost in
    saving is never skipped quietly. Every document is untrusted.
    """
    found, summaries = [], []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and isinstance(value.get("id"), str) and isinstance(value.get("data"), dict):
            if not (isinstance(value.get("updatedAt"), str) and value["updatedAt"] and type(value.get("version")) is int):
                raise Refused(f"document {json.dumps(value['id'])} lacks its version and save time; save the db_query output unchanged")
            found.append(value)
        elif isinstance(value, dict) and type(value.get("count")) is int:
            summaries.append(value)
    if len(summaries) != 1:
        raise Refused("save the db_query output unchanged, with its one summary line")
    if summaries[0].get("nextCursor"):
        raise Refused("db_query returned one page of several; query again with a larger limit")
    if len(found) != summaries[0]["count"]:
        raise Refused(f"the saved output holds {len(found)} documents but db_query counted {summaries[0]['count']}; "
                      "save its output unchanged")
    return found


NOTHING_STORED = "stored picks: nothing to record"


def answer_stored(state, at, documents, answered=()):
    """Record each stored page pick that matches its open decision's current revision.

    Each decision gets one outcome, judged against the record as it stood before this import: a pick at its
    current revision wins over picks for earlier ones. A pick for an earlier revision is never applied: it
    marks the decision's stalePick, which asks again on an open decision and makes a reopen request of a
    settled one. Picks for the decisions in answered, which the user's message just answered, were saved
    before that message was read, so it supersedes them. Each decision's picksRead names every pick read for
    it by path, version, and save time, so reading one again after a failed cleanup changes nothing.
    """
    before = {row["id"]: row for row in state["decisions"]}  # each row changes only after all its picks are read
    notes, cleanup, found, superseded, receipts = [], [], {}, set(), {}
    for document in documents:
        if not DOCUMENT_ID.fullmatch(document["id"]) or document["id"] in {".", ".."}:
            notes.append(f"ignored {json.dumps(document['id'])}: not a document ID")
            continue
        path, data = f"picks/{document['id']}", document["data"]
        name = f"{path} (version {document['version']})"
        cleanup.append(f"delete: {name}")
        identity, digest, number, label = (data.get(key) for key in ("decision", "revision", "option", "label"))
        if not (isinstance(identity, str) and isinstance(digest, str) and type(number) is int
                and isinstance(label, str) and label.strip() and document["id"] == f"{hexed(identity)}-{digest}"):
            notes.append(f"ignored {path}: not a pick the page writes")
            continue
        row = before.get(identity)
        if row is None or row["status"] == "withdrawn":
            notes.append(f"ignored {path}: {identity} is {'withdrawn' if row else 'not recorded'}")
            continue
        receipt = f"{name} {document['updatedAt']}"
        if receipt in row.get("picksRead", []):
            notes.append(f"{identity} already read {path}")
            continue
        receipts.setdefault(identity, []).append(receipt)
        if identity in answered:
            superseded.add(identity)
            continue
        options = row.get("options", [])
        chosen = options[number - 1]["label"] if 1 <= number <= len(options) else None
        current = (row["status"] == "open" and revision(row) == digest
                   and chosen is not None and quoted(chosen) == quoted(label))
        found.setdefault(identity, []).append((name, label, digest, chosen if current else None))
    recorded, stale = [], []
    for identity, picks in found.items():
        row = before[identity]
        current = next((pick for pick in picks if pick[3] is not None), None)
        if current:
            broken_work = atomic_halting_work(state, identity)
            if broken_work:
                # Keep the stored pick unread and undeleted so `work --decision --stored` can apply it atomically.
                receipts.pop(identity, None)
                cleanup = [line for line in cleanup if line != f"delete: {current[0]}"]
                notes.append(
                    f"atomic work transition needed for {identity} (invalid base on {', '.join(broken_work)}; "
                    f"user picked {quoted(current[3])}): run work --id {broken_work[0]} --scrap|--rebase-onto <branch> "
                    f"--decision {identity} --stored <file>"
                )
                continue
            settle(state, at, identity, current[3], "answered",
                   source=f"The user's pick on the command center, stored at {current[0]}")
            recorded.append(identity)
            continue
        differing = [pick for pick in sorted(picks)
                     if row["status"] == "open" or quoted(row["answer"]) != quoted(pick[1])]
        if not differing:
            notes.append(f"{identity} already records {quoted(row['answer'])}")
            continue
        _, label, digest, _ = differing[-1]
        put(decision_row(state, identity), "stalePick", {"label": label, "revision": digest, "at": at}, DECISION_KEYS)
        stale.append(identity)
        notes.append(f"stale: {identity} changed since the page showed it; the Inbox asks again" if row["status"] == "open"
                     else f"reopen request: the user picked {quoted(label)} after {identity} was {row['status']}; "
                          "reopen it under references/decisions.md#reopen")
    for identity in superseded:
        notes.append(f"superseded: the user's message replaces {identity}'s page pick")
    for identity, read in receipts.items():
        row = decision_row(state, identity)
        put(row, "picksRead", row.get("picksRead", []) + read, DECISION_KEYS)
    if recorded:
        affected = sorted({entry["id"] for identity in recorded for entry in decision_row(state, identity).get("blocks", [])})
        notes.append(f"update the owners of {', '.join(affected) or 'the work it affects'}, then run applied")
    if not documents:
        notes.append("no stored picks")
    parts = [f"{', '.join(recorded)} answered from the page"] if recorded else []
    parts += [f"{', '.join(stale)} stale page pick"] if stale else []
    return "; ".join(parts) or ("stored picks read" if receipts else NOTHING_STORED), notes + cleanup


def set_pictures(state, identity, images, option=None, shape=None):
    """Give an open decision its pictures, or one option its picture; images are (files/ name, caption) pairs."""
    row = decision_row(state, identity)
    if row["status"] != "open":
        raise Refused(f"{identity} is {row['status']}; pictures go on open decisions")
    if option is not None:
        if len(images) != 1 or images[0][1] or shape:
            raise Refused("an option takes one picture, captioned by the option's label, and no shape")
        options = row.get("options", [])
        if not 1 <= option <= len(options):
            raise Refused(f"{identity} has no option {option}")
        put(options[option - 1], "image", images[0][0], OPTION_KEYS)
        return f"{identity} picture for option {option}", []
    pictures = ({"shape": shape} if shape else {}) | {
        "images": [{"image": name} | ({"caption": caption} if caption else {}) for name, caption in images]}
    put(row, "pictures", pictures, DECISION_KEYS)
    return f"{identity} pictures: {shape or 'default shape'}, {len(images)} {'image' if len(images) == 1 else 'images'}", []


def applied(state, identities):
    """The coordinator passed these answers to the owners they affect."""
    for identity in identities:
        row = decision_row(state, identity)
        if row.pop("applied", None) is not False:
            raise Refused(f"{identity} has no answer waiting to be applied")
    return f"{', '.join(identities)} applied", []


def next_discovery_id(discoveries):
    numbers = [int(m[1]) for row in discoveries if (m := re.fullmatch(r"D(\d+)", row.get("id", "")))]
    return f"D{max(numbers, default=0) + 1}"


def record_discovery(state, at, identity=None, add=False, origin=None, work=None, text=None,
                     evidence=None, impact=None, route=None, reply_sent=False):
    """Add a discovery, record its disposition route, or mark a held deferred PR reply sent."""
    discoveries = list(state.get("discoveries", []))
    if work:
        work_row(state, work)
    if add:
        if not origin or not text:
            raise Refused("discovery --add needs --origin and --text")
        if identity and any(row.get("id") == identity for row in discoveries):
            raise Refused(f"discovery {identity} already exists")
        routed = bool(route and route.strip() and route.strip().lower() != "pending")
        assigned_id = identity or (None if routed else next_discovery_id(discoveries))
        entry = {
            "date": at, "origin": origin, "text": text,
            "route": route.strip() if routed else "pending",
            "status": "routed" if routed else "open",
        }
        if assigned_id:
            entry["id"] = assigned_id
        if work:
            entry["work"] = work
        if impact:
            entry["impact"] = impact
        if evidence:
            entry["evidence"] = evidence
        discoveries.append({key: entry[key] for key in DISCOVERY_KEYS if key in entry})
        replace_list(state, "discoveries", discoveries, PROGRAM_KEYS)
        label = assigned_id or origin
        return f"discovery {label}: {entry['route']}", []
    if reply_sent and not route:
        if not identity:
            raise Refused("discovery --reply-sent needs --id")
        target = next((row for row in discoveries if row.get("id") == identity), None)
        if target is None:
            raise Refused(f"no discovery {identity}")
        if target.get("status") != "routed":
            raise Refused(f"discovery {identity} must be routed before marking its deferred reply sent")
        if target.get("reply") != "pending":
            raise Refused(f"discovery {identity} has no pending deferred PR reply")
        put(target, "reply", "sent", DISCOVERY_KEYS)
        replace_list(state, "discoveries", discoveries, PROGRAM_KEYS)
        return f"discovery {identity} reply sent", []
    if not identity or not route or not route.strip():
        raise Refused("discovery needs --id and --route (or --reply-sent, or --add with --origin and --text)")
    target = next((row for row in discoveries if row.get("id") == identity), None)
    if target is None:
        raise Refused(f"no discovery {identity}")
    if target.get("status") == "routed":
        raise Refused(f"discovery {identity} is already routed ({target['route']})")
    if route.strip().lower() == "pending":
        raise Refused("routing a discovery needs a concrete destination, not 'pending'")
    target["route"] = route.strip()
    put(target, "status", "routed", DISCOVERY_KEYS)
    notes = []
    if target.get("thread"):
        put(target, "reply", "sent" if reply_sent else "pending", DISCOVERY_KEYS)
        if not reply_sent:
            notes.append(f"send recorded route ({target['route']}) to {target.get('work') or 'PR owner'} "
                         f"for thread {target['thread']}, then run `discovery --id {identity} --reply-sent`")
    replace_list(state, "discoveries", discoveries, PROGRAM_KEYS)
    return f"discovery {identity} routed: {target['route']}", notes


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
    if landing["state"] == "cancelling" and to == "submitted":
        raise Refused(f"{identity} is cancelling; confirm stopped (--to withdrawn) or merged (--to landed)")
    if to in {"withdrawn", "cancelling"} and not note:
        raise Refused(f"moving a landing to {to} needs --note: why")
    notes = []
    if to == "withdrawn" and landing["state"] in {"submitted", "cancelling"}:
        for pr in landing["prs"]:
            forge_pr = read_pr(pr["url"])
            if forge_pr.get("state") == "MERGED":
                raise Refused(f"{pr['url']} already merged on the forge; record --to landed instead")
            if forge_pr.get("autoMergeRequest") or forge_pr.get("isInMergeQueue"):
                raise Refused(f"{pr['url']} still has auto-merge or merge-queue armed on the forge; cancel it first")
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
                for decision in state.get("decisions", []):
                    if decision["status"] == "open" and any(b["id"] == work for b in decision.get("blocks", [])):
                        kept = [b for b in decision["blocks"] if b["id"] != work]
                        if kept:
                            decision["blocks"] = kept
                        else:
                            decision.pop("blocks", None)
                        notes.append(
                            f"{work} already merged while {decision['id']} stayed open; "
                            f"create a follow-up outcome and block it on {decision['id']} if changes are needed"
                        )
            row["checkedAt"] = at
    landing["state"] = to
    if note:
        put(landing, "note", note, ("id", "date", "chief", "lander", "target", "work", "prs", "state", "keep", "note"))
    return f"{identity} {to}", notes


# Status: facts from the forge and the host.

def gh_pr(target):
    gh = shutil.which("gh")
    if not gh:
        raise OSError("gh is not installed")
    result = subprocess.run(
        [gh, "pr", "view", target, "--json", "state,isDraft,headRefOid,baseRefName,autoMergeRequest,isInMergeQueue"],
        capture_output=True, text=True, timeout=60,
    )
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


def lapsed(row, facts):
    """The recorded row, with readiness withdrawn from each layer whose observed facts no longer support it."""
    unready = copy.deepcopy(row)
    observed = {layer["id"]: layer for layer in facts.get("layers", [])}
    allowed = READY_LAYERS.get(effective_finish(row), (set(),))[0]
    unsupported = [layer for layer in unready.get("layers", []) if observed[layer["id"]]["status"] not in allowed]
    for layer in unsupported:
        if layer["status"] == "ready":
            layer["status"] = "open"
    if unready["state"] == "ready" and unsupported:
        unready["state"] = "in-review"
    return unready


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


def seen_moved(row, thread, at):
    """Whether a thread read tells something other than the owner state the record holds, whenever each was read."""
    recorded = row["owner"].get("seen", {})
    return {key: value for key, value in observation(thread, at).items() if key != "at"} != {
        key: value for key, value in recorded.items() if key != "at"}


def observe(state, at, read_pr, threads):
    """Apply forge facts and owner thread states to open work and pending landings; return notes on what changed or needs a hand."""
    notes, forge, candidates, kept = [], {}, {}, {}
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
            labels = ((derived, None), (facts, "its forge facts"), (lapsed(row, facts), "that its readiness lapsed"),
                      (row, "nothing"))
            unique = [(option, label) for position, (option, label) in enumerate(labels)
                      if option is row or option not in [other for other, _ in labels[position + 1:]]]
            candidates[index] = [option for option, _ in unique]
            kept[index] = {id(option): label for option, label in unique}
    reasons = first_valid(state, candidates)
    for index, (*_, original) in candidates.items():
        row = state["work"][index]
        if index in reasons:
            notes.append(f"{row['id']}: recorded {kept[index][id(row)]} from the forge; settle by hand: {reasons[index]}")
        elif row["state"] != original["state"]:
            notes.append(f"{row['id']}: {original['state']} -> {row['state']}")
    for row in state["work"]:  # an owner's thread state stands whichever forge facts were kept
        if row["id"] in threads and (isinstance(threads[row["id"]], dict) or seen_moved(row, threads[row["id"]], at)):
            put(row["owner"], "seen", observation(threads[row["id"]], at), OWNER_KEYS)
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



VERDICT_EXIT = {"done": 0, "waiting": 3, "working": 4, "runnable": 5}
QUIET = {"waiting", "working"}  # a heartbeat stays quiet on these while the digest holds



def waiting_line(assessment):
    """The one line a waiting coordinator ends its turn with."""
    parts = [(f"Inbox {entry['id']}" if entry["kind"] == "need" else f"{entry['id']}: {entry['text']}")
             + (f" ({entry['age']})" if "age" in entry else "") for entry in assessment["waiting"]]
    return f"Waiting on {'; '.join(parts)}. Nothing is runnable."


def show(assessment):
    print(f"verdict: {assessment['verdict']} (digest {assessment['digest']})")
    for group in ("runnable", "working", "waiting", "attention"):
        for entry in assessment[group]:
            since = f" ({entry['age']})" if "age" in entry else ""
            print(f"{entry['kind']}: {entry['id']}: {entry['text']}{since}")
    if assessment["verdict"] == "waiting":
        print(f"say: {waiting_line(assessment)}")


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

    def seen_file(self):
        """What the coordinator last saw. It lives in the git directory, so it never shows as a record change."""
        return Path(self.git("rev-parse", "--absolute-git-dir").strip()) / "coordinator-seen.json"

    def seen(self):
        """The digest and forge notes the coordinator last saw."""
        try:
            return json.loads(self.seen_file().read_text())
        except (OSError, ValueError):
            return {"digest": None, "notes": []}

    def remember(self, digest, notes=None):
        """Record what was seen; notes default to those already seen, since only a heartbeat observes them."""
        seen = {"digest": digest, "notes": self.seen()["notes"] if notes is None else notes}
        self.seen_file().write_text(json.dumps(seen) + "\n")

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

    def create(self, state, message):
        """Initialize a new git-backed program record; a failure leaves no state file or staged entry."""
        if self.file.exists():
            raise Refused(f"{self.file} already exists")
        validate(state)
        self.file.parent.mkdir(parents=True, exist_ok=True)
        (self.file.parent / "reports").mkdir(exist_ok=True)
        if not (self.file.parent / ".git").exists():
            self.git("init", "-q")
        else:
            if self.git("ls-files", "--", self.file.name).strip():
                raise Refused(f"{self.file.name} is already tracked or staged in git")
            in_head = subprocess.run(["git", "-C", str(self.file.parent), "cat-file", "-e", f"HEAD:{self.file.name}"],
                                     capture_output=True)
            if in_head.returncode == 0:
                raise Refused(f"{self.file.name} already exists in HEAD (staged deletion); settle it instead of running init")
        staged = False
        try:
            self.file.write_text(layout(state))
            self.git("add", "--", self.file.name)
            staged = True
            self.git("commit", "-q", "-m", message, "--", self.file.name)
        except (Refused, ValueError, OSError):
            if staged:
                with contextlib.suppress(ValueError):
                    self.git("rm", "-q", "-f", "--cached", "--ignore-unmatch", "--", self.file.name)
            self.file.unlink(missing_ok=True)
            raise
        print(f"committed: {message}")

    def save(self, state, message, files=None):
        """Commit state with files (record path: content) written into the program folder; a failure changes nothing."""
        validate(state)
        files = files or {}
        previous = self.file.read_text()
        created, staged = [], False
        try:
            for name, content in files.items():
                if place(target := self.file.parent / name, content):
                    created.append(target)
            check_pictures(self.file.parent, state)
            self.file.write_text(layout(state))
            if files:
                staged = True
                self.git("add", "--", *files)
            self.git("commit", "-q", "-m", message, "--", self.file.name, *files)
        except (Refused, ValueError, OSError):
            self.file.write_text(previous)
            if staged:
                with contextlib.suppress(ValueError):
                    self.git("reset", "-q", "--", *files)
            for target in created:
                target.unlink(missing_ok=True)
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
            files = page_files(staged.read_text())
            beside = f" with {', '.join(files)} from beside it" if files else ""
            print(f"page: behind record {head}. Publish {staged}{beside}, then move it over {self.page}.")
            return False
        print(f"page: published page matches record {head}")
        return True


class PictureArgument(argparse.Action):
    """--image adds a picture and --caption captions the picture before it, so each caption keeps its picture."""

    def __call__(self, parser, namespace, value, option_string=None):
        images = list(getattr(namespace, self.dest) or [])
        if option_string == "--image":
            images.append([value, None])
        elif not images or images[-1][1] is not None:
            parser.error("--caption follows the --image it describes")
        else:
            images[-1][1] = value
        setattr(namespace, self.dest, images)


def arguments():
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--state", required=True, type=Path, help="The program.json file")
    shared.add_argument("--page", type=Path, help="The last published page; default command-center.html beside the state")
    shared.add_argument("--next", help="Also set the program's next action")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    command = commands.add_parser("init", parents=[shared], help="Create and commit a new program record")
    command.add_argument("--title", required=True)
    command.add_argument("--goal", required=True)
    command.add_argument("--chief", required=True, help="The current coordinator thread link")
    command.add_argument("--request", required=True, help="The original user request")
    command.add_argument("--request-source", action="append", help="A source reference for the request; repeatable")
    command.add_argument("--finish-line", help="Program-wide finish-line note")
    command.add_argument("--hosting", help="Initial published command center URL")

    command = commands.add_parser("grant", parents=[shared], help="Set or update the grant, landing authority, or hosting URL")
    command.add_argument("--source", help="The user's message that authorized the grant or landing authority")
    command.add_argument("--start", dest="start_rule", help="Which owners and support tasks the coordinator may start")
    command.add_argument("--resolve", dest="resolve_rule", help="Which decisions the coordinator settles itself")
    command.add_argument("--user", dest="user_rule", help="What stays with the user")
    command.add_argument("--heartbeat", dest="heartbeat_rule", help="Heartbeat timing policy and scheduled task ID, or why none")
    command.add_argument("--wake", dest="wake_rule", help="Answer wake scheduled task ID, or why none")
    command.add_argument("--landing", dest="landing_rule", help="Agreed landing scope and gates (sets landingAuthority)")
    command.add_argument("--hosting", help="Current published command center URL")
    command.add_argument("--finish-line", help="Program-wide finish-line note")

    command = commands.add_parser("work", parents=[shared], help="Add, update, scrap, or rebase a work row")
    command.add_argument("--id", required=True, help="Work ID, such as W1")
    command.add_argument("--add", action="store_true", help="Create a new work row")
    command.add_argument("--title")
    command.add_argument("--repo")
    command.add_argument("--kind", choices=("outcome", "follow-up", "support"))
    command.add_argument("--status", dest="work_state", choices=tuple(STATES), help="Work row state")
    command.add_argument("--unknown-reason")
    command.add_argument("--description")
    command.add_argument("--scope")
    command.add_argument("--finish-line", choices=tuple(FINISH_LINES))
    command.add_argument("--finish-line-reason")
    command.add_argument("--origin")
    command.add_argument("--source", dest="sources", action="append", help="Source reference; repeatable")
    command.add_argument("--blocked")
    command.add_argument("--clear-blocked", action="store_true")
    command.add_argument("--blocked-by", action="append", help="Logical dependency work ID; repeatable")
    command.add_argument("--clear-blocked-by", action="store_true")
    req = command.add_mutually_exclusive_group()
    req.add_argument("--optional", action="store_true", help="Mark proposed work outside committed scope")
    req.add_argument("--required", action="store_true", help="Mark work as required")
    command.add_argument("--provisional-basis")
    command.add_argument("--provisional-clears")
    command.add_argument("--provisional-on", action="append", help="Outcome ID this provisional work rests on; repeatable")
    command.add_argument("--clear-provisional", action="store_true")
    transition = command.add_mutually_exclusive_group()
    transition.add_argument("--scrap", action="store_true", help="Scrap this work row and clear active blockers")
    transition.add_argument("--rebase-onto", help="Move live layers' base onto this branch (and clear or retarget dead-base provisional state)")
    command.add_argument("--stack-on", help="Layer ID to set as stackedOn when rebasing onto another unmerged layer")
    command.add_argument("--decision", dest="decision_id", help="Decision ID to answer in the same commit as --scrap or --rebase-onto")
    choice = command.add_mutually_exclusive_group()
    choice.add_argument("--option", dest="decision_option", type=int)
    choice.add_argument("--text", dest="decision_text")
    choice.add_argument("--pasted", dest="decision_pasted", action="store_true", help="Read a copied page prompt for --decision from stdin")
    command.add_argument("--stored", dest="decision_stored", type=Path, metavar="FILE",
                         help="Read stored page picks from saved db_query output (alone to apply a pick, or with --option/--text/--pasted so the newer user message supersedes older picks)")
    command.add_argument("--answer-source", help="User message that answered --decision")

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
    command.add_argument("--source", help="The user's message that answered")
    command.add_argument("--decision")
    choice = command.add_mutually_exclusive_group()
    choice.add_argument("--option", type=int, help="The chosen option's number")
    choice.add_argument("--text", help="The answer in the user's words")
    choice.add_argument("--pasted", action="store_true", help="Read a copied page prompt from stdin")
    command.add_argument("--stored", type=Path, metavar="FILE",
                         help="Read picks the page stored, from saved db_query output of its picks collection; "
                              "with an answer from the user's message, that answer supersedes its decisions' picks")

    command = commands.add_parser("picture", parents=[shared], help="Set an open decision's pictures, or one option's")
    command.add_argument("--decision", required=True)
    command.add_argument("--image", dest="images", action=PictureArgument, required=True,
                         help="An absolute path to a picture; repeat it, in order, for several")
    command.add_argument("--caption", dest="images", action=PictureArgument, help="A caption for the --image before it")
    command.add_argument("--option", type=int, help="Give this option its one picture instead")
    command.add_argument("--shape", choices=tuple(PICTURE_SHAPES), help="How the decision's pictures sit together")

    command = commands.add_parser("resolve", parents=[shared], help="The coordinator settled a decision under triage")
    command.add_argument("--decision", required=True)
    command.add_argument("--basis", required=True, help="The recorded source that settles it, and why it is reversible")
    choice = command.add_mutually_exclusive_group(required=True)
    choice.add_argument("--option", type=int)
    choice.add_argument("--text")

    command = commands.add_parser("reopen", parents=[shared], help="Reopen a resolved or answered decision")
    command.add_argument("--decision", required=True)
    command.add_argument("--why", required=True)
    command.add_argument("--block", dest="blocks", action="append", help="Unlanded outcome and phase as WORK_ID:PHASE; repeatable")

    command = commands.add_parser("withdraw", parents=[shared], help="Withdraw a decision and preserve its history")
    command.add_argument("--decision", required=True)
    command.add_argument("--why", required=True)

    command = commands.add_parser("move", parents=[shared], help="Transfer coordinator ownership and live owner routes")
    command.add_argument("--chief", required=True, help="The new coordinator thread link")

    command = commands.add_parser("applied", parents=[shared], help="You passed answers to the owners they affect")
    command.add_argument("--decision", action="append", required=True)

    command = commands.add_parser("land", parents=[shared], help="Release a merge set, or move a landing")
    command.add_argument("--work", action="append", help="Release these ready rows as one set")
    command.add_argument("--lander")
    command.add_argument("--target")
    command.add_argument("--keep")
    command.add_argument("--landing", help="Move this landing instead")
    command.add_argument("--to", choices=("submitted", "cancelling", "landed", "withdrawn"))
    command.add_argument("--note")

    command = commands.add_parser("wait", parents=[shared], help="Record or clear a wait")
    command.add_argument("--on", required=True)
    command.add_argument("--event", help="What ends the wait")
    command.add_argument("--work")
    command.add_argument("--clear", action="store_true")

    command = commands.add_parser("discovery", parents=[shared], help="Add or route a discovery / deferred follow-up")
    command.add_argument("--id", help="Discovery ID (to route an open item, or assign on --add)")
    command.add_argument("--add", action="store_true", help="Record a new discovery")
    command.add_argument("--origin", help="Where the discovery came from (with --add)")
    command.add_argument("--work", help="Originating work ID, if any")
    command.add_argument("--text", help="What was discovered or deferred (with --add)")
    command.add_argument("--evidence", help="Location or evidence note (with --add)")
    command.add_argument("--impact", choices=DISCOVERY_IMPACTS, help="unrelated, shared-contract, or requested-scope")
    command.add_argument("--route", help="Disposition: work ID, snip ID, issue URL, or declined reason")
    command.add_argument("--reply-sent", action="store_true", help="Mark a routed discovery's held deferred PR reply sent to its PR owner")

    command = commands.add_parser("status", parents=[shared], help="Read PRs and owner threads; list what to do now")
    mode = command.add_mutually_exclusive_group()
    mode.add_argument("--turn-end", action="store_true",
                      help="Commit nothing; fail while the verdict is runnable, the record is dirty, an owner's thread state moved, or the page is behind")
    mode.add_argument("--heartbeat", action="store_true",
                      help="Commit nothing; print heartbeat: quiet, wake, or done against what was last seen")
    mode.add_argument("--exit-code", action="store_true", help="Exit 0 done, 3 waiting, 4 working, 5 runnable")
    command.add_argument("--stale-hours", type=float, default=STALE_HOURS)
    command.add_argument("--json", action="store_true", help="Print one JSON object on stdout; other output goes to stderr")
    return parser


def event(args, state, at, files):
    """Apply the command's event to state; files gains each file the commit must add: its record path and content."""
    if args.command == "grant":
        return update_grant(state, at, args.source, args.start_rule, args.resolve_rule, args.user_rule,
                            args.heartbeat_rule, args.wake_rule, args.landing_rule, args.hosting, args.finish_line)
    if args.command == "work":
        pasted = sys.stdin.read() if args.decision_pasted else None
        stored = stored_picks(args.decision_stored.read_text()) if args.decision_stored else None
        return mutate_work(state, at, args.id, args.add, args.title, args.repo, args.kind, args.work_state,
                           args.unknown_reason, args.description, args.scope, args.finish_line, args.finish_line_reason,
                           args.origin, args.blocked, args.clear_blocked, args.blocked_by, args.clear_blocked_by,
                           args.sources, args.optional, args.required, args.provisional_basis, args.provisional_clears,
                           args.provisional_on, args.clear_provisional, args.scrap, args.rebase_onto, args.stack_on,
                           args.decision_id, args.decision_option, args.decision_text, args.answer_source,
                           pasted, stored)
    if args.command == "reopen":
        return reopen_decision(state, at, args.decision, args.why, args.blocks)
    if args.command == "withdraw":
        return withdraw_decision(state, at, args.decision, args.why)
    if args.command == "move":
        return move_coordinator(state, args.chief)
    if args.command == "start":
        return start(state, at, args.work, args.owner, args.mode, args.session, args.route, args.workspace, args.replace)
    if args.command == "report":
        block, path = read_report(args.state, args.work)
        return report(state, at, args.work, block, f"reports/{path.name}", files)
    if args.command == "picture":
        images = [(adopt_picture(path, "--image", files), caption) for path, caption in args.images]
        return set_pictures(state, args.decision, images, args.option, args.shape)
    if args.command == "answer":
        documents = stored_picks(args.stored.read_text()) if args.stored else None
        if documents is not None and not (args.pasted or args.option or args.text):
            if args.source or args.decision:
                raise Refused("answer --stored alone takes its decisions and source from the stored picks")
            return answer_stored(state, at, documents)
        if not args.source:
            raise Refused("answer needs --source: the user's message that answered")
        if args.pasted:
            message, notes, answered = answer_pasted(state, at, sys.stdin.read(), args.source,
                                                     allow_atomic_only=documents is not None)
        elif args.decision and (args.option or args.text):
            row = decision_row(state, args.decision)
            message, notes = settle(state, at, args.decision, option_label(row, args.option) if args.option else args.text,
                                    "answered", source=args.source)
            answered = [args.decision]
        else:
            raise Refused("answer needs --decision with --option or --text, --pasted, or --stored")
        if documents is None:
            return message, notes
        stored_message, stored_notes = answer_stored(state, at, documents, answered)
        return message if stored_message == NOTHING_STORED else f"{message}; {stored_message}", notes + stored_notes
    if args.command == "resolve":
        row = decision_row(state, args.decision)
        return settle(state, at, args.decision, option_label(row, args.option) if args.option else args.text,
                      "resolved", basis=args.basis)
    if args.command == "applied":
        return applied(state, args.decision)
    if args.command == "land":
        if args.landing:
            if not args.to:
                raise Refused("moving a landing needs --to")
            return move_landing(state, at, args.landing, args.to, gh_pr, args.note)
        if not args.work:
            raise Refused("land needs --work to release, or --landing with --to")
        return release(state, at, args.work, args.lander, args.target, args.keep, args.note)
    if args.command == "discovery":
        return record_discovery(state, at, args.id, args.add, args.origin, args.work,
                                args.text, args.evidence, args.impact, args.route, args.reply_sent)
    return wait(state, at, args.on, args.event, args.work, args.clear)


def status(args, record, read_pr=gh_pr, read_thread=t3_thread):
    human = sys.stderr if args.json else sys.stdout
    with contextlib.redirect_stdout(human):
        result = check_status(args, record, read_pr, read_thread)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    if args.turn_end:
        return 0 if result["passes"] else 1
    return VERDICT_EXIT[result["verdict"]] if args.exit_code else 0


def check_status(args, record, read_pr, read_thread):
    at = now()
    if args.heartbeat:
        return heartbeat(args, record, read_pr, read_thread, at)
    if args.turn_end:
        state = validate(committed(record.file))
        threads = read_owners(state, read_thread)
        result = assess(state, at, threads, args.stale_hours)
        show(result)
        dirty = bool(record.dirty())
        if dirty:
            print(f"uncommitted: {record.file.name} has a change; settle it before the turn ends")
        moved = [row["id"] for row in state["work"] if row["id"] in threads and seen_moved(row, threads[row["id"]], at)]
        if moved:
            print(f"unrecorded: the owner state of {', '.join(moved)} moved since status recorded it; run status and publish")
        result |= {"uncommitted": dirty, "unrecorded": moved, "notes": [],
                   "page": "current" if record.render() else "behind"}
        result["passes"] = result["page"] == "current" and not dirty and not moved and result["verdict"] != "runnable"
        if result["passes"]:
            record.remember(result["digest"])
        else:
            print("Before ending the turn, act on each runnable line, and publish the page.")
        return result
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
    result = assess(state, at, threads, args.stale_hours)
    show(result)
    return result | {"notes": notes, "page": "current" if record.render() else "behind"}


def heartbeat(args, record, read_pr, read_thread, at):
    """One heartbeat tick: observe without committing, and compare with what the coordinator last saw.

    It wakes on runnable work, a changed digest, or a note not seen before: a forge fact the digest
    leaves alone, such as a base closing under provisional work, a failed read, or a row gone stale
    because reads keep failing. It says done only when the committed record is done too, so the
    woken coordinator records the last merges first.
    """
    committed_state = validate(committed(record.file))
    threads = read_owners(committed_state, read_thread)
    state = copy.deepcopy(committed_state)
    observed = {re.sub(r"(could not read \S+): .*", r"\1", note) for note in observe(state, at, read_pr, threads)}
    result = assess(state, at, threads, args.stale_hours)
    stale = {f"{entry['id']}: not observed since {entry['since']}" for entry in result["attention"] if entry["kind"] == "stale"}
    notes = sorted(observed | stale)
    seen = record.seen()
    fresh = [note for note in notes if note not in seen["notes"]]
    record.remember(result["digest"], notes)
    skill = Path(__file__).resolve().parents[1] / "SKILL.md"
    done = (result["verdict"] == "done" and not fresh
            and assess(committed_state, at, threads, args.stale_hours)["verdict"] == "done")
    if done:
        tick = "done"
        print("heartbeat: done. Delete the scheduled task in the record's grant.heartbeat, then finish the program "
              f"under {skill}.")
    elif fresh or result["verdict"] not in QUIET or seen["digest"] != result["digest"]:
        tick = "wake"
        print(f"heartbeat: wake. Re-read {skill}, run status, and act on what it lists.")
        for note in fresh:
            print(f"note: {note}")
        show(result)
    else:
        tick = "quiet"
        print(f"heartbeat: quiet ({result['verdict']}, digest {result['digest']}). End the turn without a message.")
    return result | {"heartbeat": tick, "notes": fresh}


def main():
    args = arguments().parse_args()
    record = Record(args.state, args.page)
    try:
        if args.command == "status":
            return status(args, record)
        if args.command == "init":
            state = build_init_state(args.title, args.goal, args.chief, args.request,
                                     args.next, args.request_source, args.finish_line, args.hosting)
            record.create(state, f"init: {args.title}")
            record.render()
            return 0
        state = record.load()
        before = copy.deepcopy(state)
        files = {}
        message, notes = event(args, state, now(), files)
        set_next(state, args.next)
        if state == before:
            print(f"unchanged: {message}")
        else:
            record.save(state, message, files)
        for note in notes:
            print(f"note: {note}")
        if args.command != "move":
            record.render()
        return 1 if any(note.startswith("ask again") for note in notes) else 0
    except (Refused, OSError, ValueError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
