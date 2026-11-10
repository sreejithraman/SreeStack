from colorsys import rgb_to_hsv
import copy
from html.parser import HTMLParser
from itertools import combinations
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

from render_dashboard import render, revision, url, validate


SCRIPT = Path(__file__).with_name("render_dashboard.py")
EXAMPLE = SCRIPT.parents[1] / "assets" / "example-state.json"
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "Test",
           "GIT_AUTHOR_EMAIL": "test@example.com", "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com"}


def example():
    return json.loads(EXAMPLE.read_text())


def work(state, identity):
    return next(row for row in state["work"] if row["id"] == identity)


def decision(state, identity):
    return next(row for row in state["decisions"] if row["id"] == identity)


def owner(name):
    return {"name": name, "start": "top-level", "route": "`t3_thread_send` to the chief"}


class Program:
    """A program folder: its git repository and state file."""

    def __init__(self, directory):
        self.folder = Path(directory)
        self.source = self.folder / "program.json"
        self.git("init", "-q")

    def git(self, *args, env=GIT_ENV):
        subprocess.run(["git", "-C", str(self.folder), *args], check=True, capture_output=True, env=env)

    def write(self, state, committed_at=None):
        """Write the state file, and commit it when given a commit time."""
        self.source.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
        if committed_at:
            self.git("add", "program.json")
            self.git("commit", "-q", "-m", "write", "program.json", env={**GIT_ENV, "GIT_COMMITTER_DATE": committed_at})

    def run(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--state", str(self.source), *args], capture_output=True, text=True)


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        self.elements.append((tag, dict(attributes)))


class Text(HTMLParser):
    """Visible text of the main content, whitespace-normalized."""

    def __init__(self, html):
        super().__init__()
        self.parts, self.skip = [], 0
        self.feed(html)
        self.value = " ".join(" ".join(self.parts).split())

    def handle_starttag(self, tag, attributes):
        self.skip += tag in ("style", "script", "textarea")

    def handle_endtag(self, tag):
        self.skip -= tag in ("style", "script", "textarea")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def text_of(html):
    return Text(html).value


def card(html, identity):
    """The work card's HTML."""
    return html.split(f'aria-labelledby="work-{identity.encode().hex()}"')[1].split("</article>")[0]


def badges(html, identity):
    return re.findall(r'<span class="state ([a-z-]+)">', card(html, identity))


def copy_prompts(html):
    return [attrs["data-prompt"] for _, attrs in Elements(html).elements if attrs.get("class") == "copy-prompt"]


def decision_prompts(html, identity):
    return [prompt for prompt in copy_prompts(html) if prompt.startswith(f"Decision {json.dumps(identity)} ")]


def scrap_choice(identity, phase):
    return {"id": f"{identity}-S", "question": "Scrap or rebase?", "date": "2026-11-03", "source": "Chief",
            "status": "open", "blocks": [{"id": identity, "phase": phase}]}


def answered(need):
    return need | {"status": "answered", "answer": "Rebase onto W5", "answerSource": "Chat message 2026-11-03"}


def rebased_onto_scrapped_w5(s):
    work(s, "W1").update(state="scrapped")
    s["decisions"].append(answered(scrap_choice("W2", "proof")))
    work(s, "W2")["provisional"].update(on=["W5"])
    work(s, "W2")["layers"][0].update(stackedOn="W5-L1")
    work(s, "W5").update(state="scrapped")
    decision(s, "W5-T").pop("blocks")


def rebased_onto_main(s):
    """The answer retargets W2 to main; its head stays the old one until the owner's restack report."""
    work(s, "W1").update(state="scrapped")
    s["decisions"].append(answered(scrap_choice("W2", "proof")) | {"answer": "Rebase onto main"})
    provisional = work(s, "W2")["provisional"]
    provisional["on"].remove("W1")
    if not provisional["on"]:
        work(s, "W2").pop("provisional")
    layer = work(s, "W2")["layers"][0]
    layer.pop("stackedOn")
    layer.update(base="main", head="9e4b1a7")


def rebased_onto_w5(s):
    work(s, "W1").update(state="scrapped")
    s["decisions"].append(answered(scrap_choice("W2", "proof")))
    work(s, "W2")["provisional"].update(on=["W5"], basis="W5-L1, the History owner's unshipped layer.", clears="W5 lands.")
    work(s, "W2")["layers"][0].update(stackedOn="W5-L1", base="export-history")


def rebased_onto_w5_branch_only(s):
    """T3: the answer drops the stack edge and names W5's branch only in base."""
    work(s, "W1").update(state="scrapped")
    s["decisions"].append(answered(scrap_choice("W2", "proof")))
    work(s, "W2").pop("provisional")
    work(s, "W2")["layers"][0].pop("stackedOn")
    work(s, "W2")["layers"][0].update(base="export-history")


def scrapped_w5(s):
    work(s, "W5").update(state="scrapped")
    decision(s, "W5-T").pop("blocks")


def rebased_onto_main_beside_live_w5(s):
    work(s, "W2")["provisional"].update(on=["W1", "W5"])
    rebased_onto_main(s)
    assert work(s, "W2")["provisional"]["on"] == ["W5"]


def merged(layer):
    layer.update(status="merged", url=layer.get("url", "https://example.com/exports/pull/60"))


# One violation per validator rule: (rule, change to the example, expected error).
RULES = [
    ("program facts are nonempty text", lambda s: s.pop("chief"), r"^chief must be a nonempty string"),
    ("the program has only known fields", lambda s: s.update(record={}), r"^record is not a known field"),
    ("each object has only known fields", lambda s: work(s, "W1")["owner"].update(report="reports/W1.md"), r"^work\[W1\]\.owner\.report is not a known field"),
    ("the request has its text", lambda s: s["request"].pop("text"), r"request\.text"),
    ("hosting is a link", lambda s: s.update(hosting="javascript:alert(1)"), r"hosting must be an http"),
    ("demo is a boolean", lambda s: s.update(demo="yes"), r"demo must be a boolean"),
    ("work IDs are unique", lambda s: s["work"].append(copy.deepcopy(s["work"][0])), r"work contains duplicate IDs"),
    ("decision IDs are unique", lambda s: s["decisions"].append(copy.deepcopy(s["decisions"][0])), r"decisions contains duplicate IDs"),
    ("approval IDs are unique", lambda s: s["approvals"].append(copy.deepcopy(s["approvals"][0])), r"approvals contains duplicate IDs"),
    ("observation times carry a timezone", lambda s: work(s, "W1").update(checkedAt="2026-11-02T17:00:00"), r"checkedAt must be an ISO timestamp"),
    ("entries are dated", lambda s: s["corrections"][0].update(date="yesterday"), r"corrections\[0\]\.date"),
    ("work states are known", lambda s: work(s, "W1").update(state="finished"), r"work\[W1\]\.state must be one of"),
    ("an owner has a start mode", lambda s: work(s, "W1")["owner"].update(start="self"), r"owner\.start must be one of"),
    ("an owner has a return route", lambda s: work(s, "W1")["owner"].pop("route"), r"owner\.route"),
    ("an owner session is a link", lambda s: work(s, "W1")["owner"].update(session="file:///tmp/x"), r"owner\.session must be"),
    ("a local layer has no PR", lambda s: work(s, "W5")["layers"][0].update(url="https://example.com/pull/1"), r"a local layer has no url"),
    ("layer IDs are unique across the program", lambda s: work(s, "W5")["layers"][0].update(id="W1-L1"), r"more than once"),
    ("PRs live on layers", lambda s: work(s, "W1").update(url="https://example.com/exports/pull/42"), r"work\[W1\]\.url is not a known field"),
    ("only unknown work explains its state", lambda s: work(s, "W1").update(unknownReason="x"), r"unknownReason applies only"),
    ("finished work keeps no blockers", lambda s: work(s, "W0").update(blockedBy=["W4"]), r"terminal work cannot retain"),
    ("active work has an owner", lambda s: work(s, "W1").pop("owner"), r"in-review work needs its owner"),
    ("support has no finish line", lambda s: work(s, "W3").update(finishLine="land"), r"support work has no finish line"),
    ("support never delivers", lambda s: work(s, "W3").update(state="shown"), r"support work uses"),
    ("an outcome has a finish line", lambda s: work(s, "W1").pop("finishLine"), r"work\[W1\]\.finishLine must be"),
    ("an outcome is never done", lambda s: work(s, "W1").update(state="done"), r"not done"),
    ("provisional work never merges", lambda s: merged(work(s, "W6")["layers"][0]), r"never merges; clear the condition"),
    ("Try stops before the PR", lambda s: work(s, "W5")["layers"][0].update(status="open", url="https://example.com/exports/pull/50"), r"Try stops before the PR"),
    ("provisional work is never ready", lambda s: work(s, "W1").update(
        state="ready", provisional={"basis": "x", "clears": "y"},
        layers=[dict(layer, status="ready") for layer in work(s, "W1")["layers"]]), r"provisional work is never ready"),
    ("ready means every layer is ready", lambda s: work(s, "W1").update(state="ready"), r"ready needs every layer ready or merged"),
    ("shown Try has results", lambda s: work(s, "W5").pop("results"), r"shown is a Try result"),
    ("a PR state needs a published layer", lambda s: work(s, "W6").update(state="in-review"), r"in-review needs a published layer"),
    ("landed means every layer merged", lambda s: work(s, "W1").update(state="landed"), r"landed needs a Land finish line"),
    ("dependencies exist", lambda s: work(s, "W4").update(blockedBy=["W9"]), r"blockedBy references missing work W9"),
    ("provisional work rests on other work", lambda s: work(s, "W2")["provisional"].update(on=["W2"]), r"provisional\.on must name other work"),
    ("a stack parent exists", lambda s: work(s, "W1")["layers"][1].update(stackedOn="W9-L1"), r"must name another layer"),
    ("a live layer leaves a closed parent", lambda s: work(s, "W1")["layers"][1].update(status="closed"), r"names closed W1-L2; record the restack"),
    ("another owner's unmerged layer is provisional", lambda s: work(s, "W2")["provisional"].update(on=[]), r"another owner's unmerged layer"),
    ("work on a dead base halts", lambda s: work(s, "W1").update(state="scrapped"), r"work\[W2\] rests on scrapped W1"),
    ("an answered decision no longer holds work", lambda s: (
        work(s, "W1").update(state="scrapped"), s["decisions"].append(answered(scrap_choice("W2", "start")))), r"work\[W2\] rests on scrapped W1"),
    ("a landed rebase ends the hold", rebased_onto_scrapped_w5, r"work\[W2\] rests on scrapped W5"),
    ("a base on another layer's branch names it in stackedOn", rebased_onto_w5_branch_only,
     r"layers\[W2-L1\]\.base is W5-L1's branch; name W5-L1 in stackedOn"),
    ("a rebase onto a scrapped outcome's branch names its layer (T2)", lambda s: (
        scrapped_w5(s), rebased_onto_w5_branch_only(s)), r"layers\[W2-L1\]\.base is W5-L1's branch"),
    ("a base on another layer's branch cannot hide its later scrap (T3b)", lambda s: (
        rebased_onto_w5_branch_only(s), scrapped_w5(s)), r"layers\[W2-L1\]\.base is W5-L1's branch"),
    ("an external blocker does not hold work on a dead base", lambda s: (
        work(s, "W1").update(state="scrapped"), work(s, "W2").update(blocked="Waiting on CI quota; infra team.")),
        r"work\[W2\] rests on scrapped W1"),
    ("an external blocker does not hold a live layer on a closed parent", lambda s: (
        work(s, "W1")["layers"][1].update(status="closed"), work(s, "W2").update(blocked="Waiting on CI quota; infra team.")),
        r"names closed W1-L2; record the restack"),
    ("dependencies have no cycle", lambda s: work(s, "W1").update(blockedBy=["W2"]), r"work dependency cycle"),
    ("stacks have no cycle", lambda s: work(s, "W1")["layers"][0].update(stackedOn="W1-L2"), r"stack cycle"),
    ("a decision is dated", lambda s: decision(s, "W6-D1").pop("date"), r"decisions\[W6-D1\]\.date"),
    ("decision states are known", lambda s: decision(s, "W6-D1").update(status="closed"), r"status must be one of"),
    ("an answer is recorded", lambda s: decision(s, "W6-D1").update(status="answered"), r"W6-D1\]\.answer must be"),
    ("an answer names its message", lambda s: decision(s, "W0-D1").pop("answerSource"), r"W0-D1\]\.answerSource must be"),
    ("only an answer has an answer source", lambda s: decision(s, "W6-D1").update(answerSource="x"), r"answerSource applies only to answered"),
    ("a chief's call has its basis", lambda s: decision(s, "W6-D1").update(status="resolved", answer="Keep"), r"\.basis must be"),
    ("only a chief's call has a basis", lambda s: decision(s, "W0-D1").update(basis="x"), r"basis applies only to resolved"),
    ("a withdrawal says why", lambda s: decision(s, "W2-D1").pop("rationale"), r"W2-D1\]\.rationale must be"),
    ("weights are known", lambda s: decision(s, "W6-D1").update(weight="urgent"), r"weight must be quick or judgment"),
    ("blocked work exists", lambda s: decision(s, "W6-D1")["blocks"].append({"id": "W9", "phase": "landing"}), r"blocks references missing work W9"),
    ("phases are known", lambda s: decision(s, "W6-D1")["blocks"][0].update(phase="later"), r"phase must be one of"),
    ("a decision blocks work once", lambda s: decision(s, "W6-D1")["blocks"].append({"id": "W6", "phase": "landing"}), r"names W6 twice"),
    ("an open decision leaves finished work alone", lambda s: decision(s, "W6-D1")["blocks"].append({"id": "W0", "phase": "landing"}), r"cannot block terminal work"),
    ("start applies before work starts", lambda s: decision(s, "W6-D1")["blocks"][0].update(phase="start"), r"W6 has started"),
    ("one option is recommended", lambda s: decision(s, "W6-D1")["options"][1].update(recommended=True), r"only one option"),
    ("a recommendation names its option", lambda s: (decision(s, "W6-D1").update(recommendation="x"),
                                                    decision(s, "W6-D1")["options"][0].pop("recommended")), r"mark the recommended option"),
    ("a quick pick has a recommended option", lambda s: decision(s, "W1-D2")["options"][0].pop("recommended"), r"quick needs at least two options"),
    ("an option's recommendation is a boolean", lambda s: decision(s, "W6-D1")["options"][0].update(recommended="yes"), r"recommended must be a boolean"),
    ("required is a boolean", lambda s: work(s, "W4").update(required="no"), r"required must be a boolean"),
    ("provisional work says what clears it", lambda s: work(s, "W2")["provisional"].pop("clears"), r"provisional\.clears"),
    ("results say how to open them", lambda s: work(s, "W5")["results"][0].update(access=""), r"results\[0\]\.access"),
    ("landing authority is a dated entry", lambda s: s["landingAuthority"].pop("source"), r"landingAuthority\.source"),
    ("tradeoffs say when to revisit", lambda s: s["revisits"][0].pop("revisit"), r"revisits\[R1\]\.revisit"),
    ("waits name existing work", lambda s: s["waits"][0].update(work="W9"), r"waits\[0\]\.work names missing work W9"),
    ("a landing names its work and PRs", lambda s: s["landings"][0].update(prs=[]), r"needs its work and PRs"),
    ("a landing names existing work", lambda s: s["landings"][0].update(work=["W9"]), r"landings\[L1\]\.work names missing work W9"),
    ("a landing records each PR's head", lambda s: s["landings"][0]["prs"][0].pop("head"), r"prs\[0\]\.head"),
    ("landing states are known", lambda s: s["landings"][0].update(state="queued"), r"landings\[L1\]\.state must be one of"),
]

# Programs at each rule's edge that it must accept.
ACCEPTED = [
    ("planned work may wait for an owner", lambda s: None),
    ("a settled decision may name finished work", lambda s: (
        decision(s, "W0-D1").update(status="resolved", basis="Earlier rule."), decision(s, "W0-D1").pop("answerSource"))),
    ("an open halting decision holds work on a dead base", lambda s: (
        work(s, "W1").update(state="scrapped"), s["decisions"].append(scrap_choice("W2", "proof")))),
    ("a recorded rebase answer moves work off its dead base before the restack", rebased_onto_main),
    ("a rebase onto another outcome stacks on its layer and stays provisional", rebased_onto_w5),
    ("a rebase onto main keeps provisional for a second live base", rebased_onto_main_beside_live_w5),
    ("an open halting decision holds a live layer on a closed parent", lambda s: (
        work(s, "W1")["layers"][1].update(status="closed"), s["decisions"].append(scrap_choice("W2", "proof")))),
    ("an unrelated closed layer leaves a live base alone", lambda s: work(s, "W1")["layers"].append(
        {"id": "W1-L3", "branch": "docs", "status": "closed", "url": "https://example.com/exports/pull/45", "stackedOn": "W1-L2"})),
    ("finished work does not rest on a scrapped base", lambda s: (
        work(s, "W1").update(state="scrapped"), work(s, "W2").update(state="scrapped"))),
    ("an owner's own unmerged layer is not provisional", lambda s: work(s, "W4").update(
        owner=copy.deepcopy(work(s, "W1")["owner"]), state="building",
        layers=[{"id": "W4-L1", "branch": "progress", "status": "local", "stackedOn": "W1-L2"}])),
    ("a published Land outcome keeps its PR when it becomes provisional", lambda s: work(s, "W1").update(
        provisional={"basis": "W1-D2's recommended option.", "clears": "W1-D2 is answered."})),
]


class RuleTests(unittest.TestCase):
    def test_example_is_valid(self):
        validate(example())

    def test_each_rule_rejects_its_violation(self):
        for rule, change, message in RULES:
            state = example()
            change(state)
            with self.subTest(rule=rule), self.assertRaisesRegex(ValueError, message):
                validate(state)

    def test_each_rule_accepts_its_edge(self):
        for case, change in ACCEPTED:
            state = example()
            change(state)
            with self.subTest(case=case):
                validate(state)

    def test_every_object_rejects_an_unknown_field(self):
        def objects(value):
            if isinstance(value, dict):
                yield value
            for child in value.values() if isinstance(value, dict) else value if isinstance(value, list) else ():
                yield from objects(child)

        count = sum(1 for _ in objects(example()))
        for index in range(count):
            state = example()
            target = list(objects(state))[index]
            target["typo"] = "x"
            with self.subTest(fields=sorted(target)), self.assertRaisesRegex(ValueError, r"(^|\.)typo is not a known field$"):
                validate(state)

    def test_a_program_is_an_object_with_work_and_decision_lists(self):
        for state in ([], example() | {"work": {}}, example() | {"decisions": None}):
            with self.subTest(state=type(state).__name__), self.assertRaises(ValueError):
                validate(state)

    def test_unsafe_link_schemes_are_rejected(self):
        for target in ("javascript:alert(1)", "data:text/html,test", "file:///tmp/test", "https://example.test/\npath", "t3-other://x/y"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                url(target, "url")
        self.assertEqual(url("<t3-thread://v2/env/thread>", "url"), "t3-thread://v2/env/thread")


class PageTests(unittest.TestCase):
    def setUp(self):
        self.state = example()

    def test_needs_you_opens_first_and_work_waits_behind_its_tab(self):
        panels = [attrs for _, attrs in Elements(render(self.state)).elements if attrs.get("role") == "tabpanel"]
        self.assertEqual([(panel["id"], "hidden" in panel) for panel in panels], [("needs-panel", False), ("work-panel", True)])

    def test_untrusted_text_cannot_create_elements(self):
        payload = '</script><script>alert("x")</script><img src=x onerror=alert(1)>'
        self.state["title"] = payload
        decision(self.state, "W6-D1").update(question=payload, meanwhile=payload)
        row = work(self.state, "W5")
        row["title"] = row["description"] = payload
        row["results"][0].update(label=payload, access=payload)
        row["layers"][0]["branch"] = payload
        row["owner"]["name"] = payload
        html = render(self.state)
        tags = [tag for tag, _ in Elements(html).elements]
        self.assertEqual(tags.count("script"), 2)
        self.assertNotIn("img", tags)

    def test_history_and_plumbing_stay_off_the_page(self):
        base = render(self.state)
        changes = {
            "chief": lambda s: s.update(chief="Another thread"),
            "next": lambda s: s.update(next="Something else"),
            "request": lambda s: s["request"].update(text="Reworded"),
            "landings": lambda s: s["landings"][0].update(state="withdrawn"),
            "waits": lambda s: s.pop("waits"),
            "owner plumbing": lambda s: work(s, "W1")["owner"].update(route="Ends its turn", handled=["msg-1"]),
            "outcome scope": lambda s: work(s, "W1").update(scope="Reworded", finishLineReason="Reworded", acceptance="All proved"),
            "decision history": lambda s: decision(s, "W6-D1").update(date="2026-11-03", source="Another report", rationale="Earlier reasoning."),
            "answer source": lambda s: decision(s, "W0-D1").update(answerSource="Another message"),
            "a withdrawn decision": lambda s: decision(s, "W2-D1").update(question="Reworded"),
        }
        for name, change in changes.items():
            state = example()
            change(state)
            with self.subTest(change=name):
                self.assertEqual(render(state), base)
        self.assertNotIn("Paginate history", text_of(base))

    def test_provisional_land_reads_as_try(self):
        html = render(self.state)
        self.assertIn("Finish line Land → Try while provisional", text_of(card(html, "W2")))
        self.assertIn("Finish line Land", text_of(card(html, "W1")))
        self.assertNotIn("while provisional", text_of(card(html, "W1")))

    def test_updated_time_shows_only_when_given(self):
        self.assertNotIn("Updated", text_of(render(self.state)))
        page = text_of(render(self.state, "2026-11-03T09:30:00Z"))
        self.assertIn("Updated 2026-11-03T09:30:00Z", page)
        self.assertLess(page.index("Updated"), page.index("Needs you"))

    def test_halting_phases_block_work_and_later_phases_let_it_continue(self):
        html = render(self.state)
        self.assertEqual(badges(html, "W5"), ["shown"])
        self.assertIn("Waits on W5-T Decision · blocks landing", text_of(card(html, "W5")))
        decision(self.state, "W6-D1")["blocks"] = [{"id": "W6", "phase": "access"}, {"id": "W4", "phase": "start"}]
        html = render(self.state)
        self.assertEqual(badges(html, "W6"), ["building", "provisional", "blocked"])
        self.assertIn("Blocked by W6-D1 Decision · blocks start", text_of(card(html, "W4")))
        decision(self.state, "W6-D1").update(status="answered", answer="Keep the entry", answerSource="Chat message")
        self.assertEqual(badges(render(self.state), "W6"), ["building", "provisional"])

    def test_dead_and_halted_bases_show_once_on_the_dependent(self):
        work(self.state, "W1").update(state="scrapped")
        self.state["decisions"].append(scrap_choice("W2", "proof"))
        page = text_of(card(render(self.state), "W2"))
        self.assertEqual(page.count("Scrapped base"), 1)
        self.assertNotIn("Closed base", page)
        state = example()
        state["decisions"].append(scrap_choice("W1", "proof"))
        self.assertIn("W1 Blocked base", text_of(card(render(state), "W2")))

    def test_choice_prompt_names_one_option_at_its_revision(self):
        target = decision(self.state, "W6-D1")
        target["options"][1]["label"] = 'Hide "it" <b>'
        prompts = decision_prompts(render(self.state), "W6-D1")
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[1].splitlines(), [
            f'Decision "W6-D1" (revision {revision(target)}) in "Export reliability"',
            'Question: "Should expired export links remain visible?"',
            'I choose option 2: "Hide \\"it\\" <b>"',
        ])

    def test_revision_follows_what_the_page_shows(self):
        target = decision(self.state, "W6-D1")
        before = revision(target)
        target.update(date="2026-11-04", source="Another report", rationale="History.")
        self.assertEqual(revision(target), before)
        target["options"][0]["effect"] = "Changed."
        self.assertNotEqual(revision(target), before)

    def test_reopen_prompt_names_one_resolved_decision(self):
        prompts = decision_prompts(render(self.state), "W5-D2")
        self.assertEqual(len(prompts), 1)
        self.assertTrue(prompts[0].endswith("Reopen this decision."))

    def test_batch_prompt_takes_each_recommended_quick_pick(self):
        lines = next(prompt for prompt in copy_prompts(render(self.state)) if prompt.startswith("Decisions in")).splitlines()
        self.assertEqual(lines[1:], [
            f'Decision "W1-D2" (revision {revision(decision(self.state, "W1-D2"))}): I choose option 1: "Three attempts"',
            f'Decision "W3-D1" (revision {revision(decision(self.state, "W3-D1"))}): I choose option 2: "Between test classes"',
        ])
        decision(self.state, "W3-D1").update(status="answered", answer="Between test classes", answerSource="Chat message")
        self.assertFalse(any(prompt.startswith("Decisions in") for prompt in copy_prompts(render(self.state))))

    def test_pr_numbers_come_only_from_pull_request_paths(self):
        layer = work(self.state, "W1")["layers"][0]
        for target, label in (("https://example.com/exports/pull/42", "PR #42"), ("https://example.com/exports/actions/runs/42", "Open PR")):
            layer["url"] = target
            with self.subTest(target=target):
                self.assertIn(label, text_of(card(render(self.state), "W1")))

    def test_status_colors_are_distinct_and_readable(self):
        html = render(self.state)
        colors = {name: [tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)) for value in pair]
                  for name, *pair in re.findall(r"--([a-z-]+): light-dark\(#(\w{6}), #(\w{6})\)", html)}

        def luminance(color):
            red, green, blue = (c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in color)
            return .2126 * red + .7152 * green + .0722 * blue

        lifecycle = ("planned", "building", "shown", "in-review", "ready", "landed")
        for theme, surface in enumerate(((1, 1, 1), (.11, .11, .118))):
            for name in (*lifecycle, "scrapped", "unknown"):
                lighter, darker = sorted((luminance(colors[name][theme]), luminance(surface)), reverse=True)
                self.assertGreaterEqual((lighter + .05) / (darker + .05), 4.5, (name, theme))
            hues = {name: rgb_to_hsv(*colors[name][theme]) for name in lifecycle}
            self.assertLess(hues.pop("planned")[1], .1)
            for (first, a), (second, b) in combinations(hues.items(), 2):
                separation = abs(a[0] - b[0]) * 360
                self.assertGreater(min(separation, 360 - separation), 25, (first, second, theme))


class CommandTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.program = Program(folder.name)
        self.state = example()

    def test_check_reads_the_working_file_and_writes_nothing(self):
        self.program.write(self.state)
        self.assertEqual(self.program.run("--check").returncode, 0)
        work(self.state, "W1")["state"] = "finished"
        self.program.write(self.state)
        self.assertIn("work[W1].state must be one of", self.program.run("--check").stderr)
        self.program.source.write_text("{not json")
        self.assertEqual(self.program.run("--check").returncode, 2)
        self.assertEqual(sorted(path.name for path in self.program.folder.iterdir()), [".git", "program.json"])

    def test_check_holds_the_file_to_one_value_per_line_and_names_the_fix(self):
        self.state["goal"] = "Ship exports — résumé ✓"
        source = self.program.folder / "program file.json"
        check = [sys.executable, str(SCRIPT), "--check", "--state", str(source)]
        for layout in (json.dumps(self.state), json.dumps(self.state, indent=4, ensure_ascii=False)):
            source.write_text(layout)
            failed = subprocess.run(check, capture_output=True, text=True)
            self.assertIn("not one value per line", failed.stderr)
        fix = failed.stderr.split("rewrite it with: ", 1)[1].strip().replace("python3", shlex.quote(sys.executable), 1)
        subprocess.run(fix, shell=True, check=True)
        self.assertEqual(json.loads(source.read_text()), self.state)
        self.assertEqual(subprocess.run(check, capture_output=True).returncode, 0)

    def test_page_stages_head_until_it_is_published(self):
        page = self.program.folder / "command-center.html"
        staged = self.program.folder / "command-center.next.html"

        def render_page():
            result = self.program.run("--page", str(page))
            return result.stdout.strip() or result.stderr

        def updated(path):
            return re.search(r'<time id="updated" datetime="([^"]+)"', path.read_text())[1]

        def record_only(note):
            self.state["next"] = note
            return self.state

        self.assertIn("HEAD", render_page(), "a program with no commit has nothing to render")
        self.program.write(self.state, "2026-11-02T17:00:00Z")
        self.assertEqual(render_page(), "changed")
        self.assertEqual(updated(staged), "2026-11-02T17:00:00Z")
        staged.replace(page)
        self.assertEqual(render_page(), "unchanged")

        self.program.write(record_only("Record only."), "2026-11-02T18:00:00Z")
        self.assertEqual(render_page(), "unchanged")
        self.assertFalse(staged.exists())
        self.state["title"] = "Not committed"
        self.program.write(self.state)
        self.assertEqual(render_page(), "unchanged", "the page shows HEAD, not the edit buffer")

        self.program.write(self.state, "2026-11-03T09:30:00Z")
        self.assertEqual(render_page(), "changed")
        self.program.write(record_only("Publish skipped."), "2026-11-03T10:00:00Z")
        self.assertEqual(render_page(), "changed", "an unpublished change stays changed")
        self.assertEqual(updated(staged), "2026-11-03T09:30:00Z", "the time is the commit that changed the page")
        staged.replace(page)
        self.assertIn("<title>Not committed</title>", page.read_text())
        self.assertEqual(render_page(), "unchanged")

    def test_page_never_overwrites_the_state_file(self):
        self.program.write(self.state, "2026-11-02T17:00:00Z")
        alias = self.program.folder / "alias.html"
        alias.symlink_to(self.program.source)
        for target in (self.program.source, alias):
            result = self.program.run("--page", str(target))
            with self.subTest(target=target.name):
                self.assertEqual(result.returncode, 2)
                self.assertIn("would overwrite the state file", result.stderr)
        self.assertEqual(json.loads(self.program.source.read_text()), self.state)
        self.assertEqual(sorted(path.name for path in self.program.folder.iterdir()), [".git", "alias.html", "program.json"])

    def test_revision_reads_head(self):
        self.program.write(self.state, "2026-11-02T17:00:00Z")
        committed = revision(decision(self.state, "W6-D1"))
        decision(self.state, "W6-D1")["question"] = "Uncommitted edit"
        self.program.write(self.state)
        self.assertEqual(self.program.run("--revision", "W6-D1").stdout.strip(), committed)
        self.program.source.write_text("{not json")
        self.assertEqual(self.program.run("--revision", "W6-D1").stdout.strip(), committed)
        self.assertIn("no decision", self.program.run("--revision", "W9-D1").stderr)


if __name__ == "__main__":
    unittest.main()
