import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from record import orphans, revision
from test_render_dashboard import GIT_ENV, Program, decision, example, work


SCRIPT = Path(__file__).with_name("record.py")
FAKE = textwrap.dedent("""\
    import json, os, sys
    fixtures = json.load(open(os.environ["RECORD_FIXTURES"]))
    kind, key = ("prs", sys.argv[3]) if sys.argv[1] == "pr" else ("threads", sys.argv[-1])
    if key not in fixtures[kind]:
        sys.exit(f"{key} not found")
    print(json.dumps(fixtures[kind][key] if kind == "prs" else {"thread": fixtures[kind][key], "messages": []}))
""")
SESSION = "https://app.t3.codes/threads/env/thread%3A{}"


def changes(before, after, path=""):
    """Paths whose values differ, keyed by row ID inside lists of rows."""
    if isinstance(before, dict) and isinstance(after, dict):
        return {change for key in before.keys() | after.keys()
                for change in changes(before.get(key), after.get(key), f"{path}.{key}" if path else key)}
    if (isinstance(before, list) and isinstance(after, list) and all(isinstance(row, dict) and "id" in row for row in before + after)
            and before + after):
        old, new = {row["id"]: row for row in before}, {row["id"]: row for row in after}
        return {change for key in old.keys() | new.keys() for change in changes(old.get(key), new.get(key), f"{path}[{key}]")}
    return set() if before == after else {path}


def utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ready(state):
    """W1 at readiness for Land, with nothing holding it."""
    row = work(state, "W1")
    row["state"] = "ready"
    for layer in row["layers"]:
        layer["status"] = "ready"
    state["waits"] = [wait for wait in state["waits"] if wait.get("work") != "W1"]
    for need in state["decisions"]:
        if need["status"] == "open":
            need["blocks"] = [entry for entry in need.get("blocks", []) if entry["id"] != "W1"]


class RecordCase(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        (Path(folder.name) / "program").mkdir()
        self.program = Program(Path(folder.name) / "program")
        self.state = example()
        self.program.write(self.state, "2026-11-02T17:00:00Z")
        self.bin = Path(folder.name) / "bin"
        self.bin.mkdir()
        for name in ("gh", "t3"):
            fake = self.bin / name
            fake.write_text(f"#!{sys.executable}\n{FAKE}")
            fake.chmod(0o755)
        self.fixtures = Path(folder.name) / "fixtures.json"
        self.serve()

    def serve(self, prs=None, threads=None):
        self.fixtures.write_text(json.dumps({"prs": prs or {}, "threads": threads or {}}))

    def run_record(self, *args, stdin=None):
        env = {**GIT_ENV, "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}", "T3CODE_CLI_PATH": str(self.bin / "t3"),
               "RECORD_FIXTURES": str(self.fixtures)}
        return subprocess.run([sys.executable, str(SCRIPT), args[0], "--state", str(self.program.source), *args[1:]],
                              capture_output=True, text=True, input=stdin, env=env)

    def head(self):
        return json.loads(subprocess.run(["git", "-C", str(self.program.folder), "show", "HEAD:program.json"],
                                         capture_output=True, text=True, check=True).stdout)

    def commits(self):
        return subprocess.run(["git", "-C", str(self.program.folder), "log", "--format=%s"],
                              capture_output=True, text=True, check=True).stdout.splitlines()

    def event(self, *args, stdin=None):
        """Run an event that must succeed; return what it changed in the committed record."""
        before = self.head()
        result = self.run_record(*args, stdin=stdin)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.head()
        self.assertEqual(json.loads(self.program.source.read_text()), after, "the working file is the commit")
        return changes(before, after), after, result

    def refused(self, *args, stdin=None, message=""):
        before, commits = self.program.source.read_text(), self.commits()
        result = self.run_record(*args, stdin=stdin)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(message, result.stderr)
        self.assertEqual((self.program.source.read_text(), self.commits()), (before, commits), "a refusal changes nothing")
        return result

    def commit(self, change):
        change(self.state)
        self.program.write(self.state, "2026-11-02T17:30:00Z")


class EventTests(RecordCase):
    def test_start_stamps_the_clock_and_changes_only_its_row(self):
        earlier = datetime.now(timezone.utc).replace(microsecond=0)
        changed, after, result = self.event("start", "--work", "W4", "--owner", "Progress owner",
                                            "--session", SESSION.format("w4"))
        later = datetime.now(timezone.utc)
        self.assertEqual(changed, {"work[W4].state", "work[W4].owner", "work[W4].checkedAt"})
        row = work(after, "W4")
        self.assertEqual(row["state"], "building")
        self.assertEqual(row["owner"], {"name": "Progress owner", "session": SESSION.format("w4"), "start": "top-level",
                                        "route": "`t3_thread_send` to the chief"})
        self.assertTrue(row["checkedAt"].endswith("Z"))
        self.assertTrue(earlier <= utc(row["checkedAt"]) <= later, row["checkedAt"])
        self.assertEqual(self.commits()[0], "W4 start: Progress owner")
        self.assertIn("page: behind record", result.stdout)

    def test_no_command_takes_a_time_from_its_caller(self):
        for args in (("start", "--work", "W4", "--owner", "X", "--now", "2030-01-01T00:00:00Z"),
                     ("wait", "--on", "CI", "--event", "done", "--date", "2030-01-01T00:00:00Z")):
            with self.subTest(command=args[0]):
                self.assertEqual(self.run_record(*args).returncode, 2)
        report = self.program.folder / "reports" / "W1.md"
        report.parent.mkdir()
        report.write_text('```json\n{"outcome": "W1", "state": "in-review", "checkedAt": "2030-01-01T00:00:00Z"}\n```\n')
        self.refused("report", "--work", "W1", message="checkedAt is not a known field")

    def test_an_uncommitted_change_stops_the_command_with_its_diff(self):
        self.state["next"] = "Hand edit"
        self.program.write(self.state)
        result = self.refused("wait", "--on", "CI", "--event", "Checks finish", message="uncommitted change")
        self.assertIn('+  "next": "Hand edit"', result.stderr)

    def test_an_event_that_breaks_a_rule_writes_nothing(self):
        self.refused("start", "--work", "W0", "--owner", "X", message="W0 is landed")
        self.refused("start", "--work", "W1", "--owner", "X", message="already has owner")
        self.refused("answer", "--decision", "W6-D1", "--option", "9", "--source", "msg", message="no option 9")
        self.commit(lambda s: work(s, "W4").update(blockedBy=["W2"]))
        self.refused("start", "--work", "W4", "--owner", "X", message="blocked by W2")

    def test_start_drops_satisfied_edges_and_defaults_the_route_by_mode(self):
        self.commit(lambda s: work(s, "W4").update(blockedBy=["W0"]))
        changed, after, result = self.event("start", "--work", "W4", "--owner", "Helper", "--mode", "delegated")
        self.assertNotIn("blockedBy", work(after, "W4"))
        self.assertIn("work[W4].blockedBy", changed)
        self.assertEqual(work(after, "W4")["owner"]["route"], "End its turn with the report; the chief watches its PR")
        self.assertIn("dropped satisfied blockedBy W0", result.stdout)

    def test_answer_and_resolve_pick_the_status_from_who_answered(self):
        changed, after, _ = self.event("answer", "--decision", "W6-D1", "--option", "1", "--source", "User message 18:02")
        self.assertEqual(changed, {"decisions[W6-D1].status", "decisions[W6-D1].answer", "decisions[W6-D1].answerSource"})
        self.assertEqual((decision(after, "W6-D1")["status"], decision(after, "W6-D1")["answerSource"]),
                         ("answered", "User message 18:02"))
        self.assertEqual(self.commits()[0], "W6-D1 answered")
        open_need = next(row for row in after["decisions"] if row["status"] == "open")
        _, after, _ = self.event("resolve", "--decision", open_need["id"], "--text", "Keep it", "--basis", "The brief settles it")
        resolved = decision(after, open_need["id"])
        self.assertEqual((resolved["status"], resolved["basis"]), ("resolved", "The brief settles it"))
        self.assertNotIn("answerSource", resolved)
        self.refused("resolve", "--decision", open_need["id"], "--text", "Again", "--basis", "b", message="only an open decision")

    def test_a_user_answer_over_the_chiefs_call_keeps_the_call_in_its_rationale(self):
        resolved = next(row for row in self.state["decisions"] if row["status"] == "resolved")
        _, after, _ = self.event("answer", "--decision", resolved["id"], "--text", "Do the other thing", "--source", "msg 9")
        row = decision(after, resolved["id"])
        self.assertEqual((row["status"], row["answer"]), ("answered", "Do the other thing"))
        self.assertNotIn("basis", row)
        self.assertIn(resolved["answer"], row["rationale"])
        self.assertIn(resolved["basis"], row["rationale"])

    def test_a_pasted_choice_counts_only_at_its_current_revision(self):
        need = decision(self.state, "W6-D1")
        prompt = (f'Decision "W6-D1" (revision {revision(need)}) in "{self.state["title"]}"\n'
                  f'Question: "{need["question"]}"\nI choose option 2: "{need["options"][1]["label"]}"\n')
        stale = prompt.replace(revision(need), "0000000000")
        self.refused("answer", "--pasted", "--source", "msg", stdin=stale, message="ask again: W6-D1")
        changed, after, _ = self.event("answer", "--pasted", "--source", "User message 18:05", stdin=prompt)
        self.assertEqual(decision(after, "W6-D1")["answer"], need["options"][1]["label"])
        self.assertEqual(changed, {"decisions[W6-D1].status", "decisions[W6-D1].answer", "decisions[W6-D1].answerSource"})

    def test_a_pasted_batch_records_the_lines_that_match_and_asks_again_about_the_rest(self):
        quick = [row for row in self.state["decisions"] if row["status"] == "open" and row.get("options")][:2]
        self.assertEqual(len(quick), 2)
        lines = [f'Decisions in "{self.state["title"]}"']
        for index, row in enumerate(quick):
            digest = revision(row) if index == 0 else "0000000000"
            lines.append(f'Decision "{row["id"]}" (revision {digest}): I choose option 1: "{row["options"][0]["label"]}"')
        result = self.run_record("answer", "--pasted", "--source", "msg", stdin="\n".join(lines))
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"ask again: {quick[1]['id']}", result.stdout)
        self.assertEqual([row["status"] for row in (decision(self.head(), row["id"]) for row in quick)], ["answered", "open"])

    def test_wait_adds_and_clears_one_entry(self):
        changed, after, _ = self.event("wait", "--on", "PR 44 review", "--event", "Review posts", "--work", "W1")
        self.assertEqual(changed, {"waits"})
        self.assertEqual(after["waits"][-1]["on"], "PR 44 review")
        changed, after, _ = self.event("wait", "--clear", "--on", "PR 44 review", "--work", "W1")
        self.assertEqual(after["waits"], self.state["waits"])
        self.refused("wait", "--clear", "--on", "Nothing", message="no wait")

    def test_next_rides_along_with_any_event(self):
        changed, after, _ = self.event("wait", "--on", "CI", "--event", "Done", "--next", "Check CI")
        self.assertEqual(changed, {"waits", "next"})
        self.assertEqual(after["next"], "Check CI")


class ReportTests(RecordCase):
    def write_report(self, block, prose="Prose for people below the block.\n"):
        path = self.program.folder / "reports" / "W1.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"```json\n{json.dumps(block, indent=2)}\n```\n\n{prose}")

    def test_the_report_block_replaces_only_the_fields_it_names(self):
        layers = copy.deepcopy(work(self.state, "W1")["layers"])
        layers[1] |= {"status": "ready", "head": "c0ffee1"}
        layers[0]["status"] = "ready"
        self.write_report({
            "outcome": "W1", "state": "ready", "layers": layers,
            "proof": [{"assertion": "Interrupted export resumes once", "verdict": "pass", "url": "https://example.com/run/8"},
                      {"assertion": "Burst timing", "verdict": "untested"}],
            "asks": [{"id": "W1-D9", "question": "Ship the burst fix later?", "phase": "landing",
                      "options": [{"label": "Later", "effect": "Lands now", "recommended": True},
                                  {"label": "Now", "effect": "Waits a day"}], "weight": "quick"}],
            "waits": [{"on": "PR 44 checks", "event": "Required checks finish"}],
        })
        earlier = datetime.now(timezone.utc).replace(microsecond=0)
        changed, after, result = self.event("report", "--work", "W1")
        self.assertEqual(changed, {"work[W1].state", "work[W1].layers[W1-L2].status", "work[W1].layers[W1-L2].head",
                                   "work[W1].evidence", "work[W1].acceptance",
                                   "work[W1].checkedAt", "decisions[W1-D9]"})
        row = work(after, "W1")
        self.assertEqual(row["evidence"], [{"label": "Interrupted export resumes once", "url": "https://example.com/run/8"}])
        self.assertEqual(row["acceptance"], "untested: Burst timing")
        need = decision(after, "W1-D9")
        self.assertEqual((need["status"], need["source"], need["blocks"]), ("open", "reports/W1.md", [{"id": "W1", "phase": "landing"}]))
        self.assertTrue(earlier <= utc(need["date"]) <= datetime.now(timezone.utc))
        self.assertEqual(after["waits"], self.state["waits"], "a wait the owner still reports keeps its first date")
        self.assertEqual(self.commits()[0], "W1 report: ready, asks W1-D9")
        self.assertIn("triage W1-D9", result.stdout)

    def test_a_report_without_waits_keeps_them_and_an_empty_list_clears_them(self):
        self.write_report({"outcome": "W1", "state": "in-review"})
        changed, after, _ = self.event("report", "--work", "W1")
        self.assertEqual(changed, {"work[W1].checkedAt"})
        self.write_report({"outcome": "W1", "state": "in-review", "waits": []})
        _, after, _ = self.event("report", "--work", "W1")
        self.assertNotIn("waits", after)

    def test_a_malformed_report_is_refused(self):
        self.refused("report", "--work", "W1", message="cannot read")
        self.write_report({"outcome": "W1", "state": "in-review"}, prose="")
        path = self.program.folder / "reports" / "W1.md"
        path.write_text("Prose first.\n\n" + path.read_text())
        self.refused("report", "--work", "W1", message="must start with a ```json block")
        for block, message in (({"outcome": "W2", "state": "building"}, "names outcome 'W2'"),
                               ({"outcome": "W1", "state": "blocked"}, "report state must be one of"),
                               ({"outcome": "W1", "state": "in-review", "proof": [{"assertion": "x", "verdict": "ok"}]}, "verdict"),
                               ({"outcome": "W1", "state": "landed"}, "landed needs")):
            self.write_report(block)
            with self.subTest(message=message):
                self.refused("report", "--work", "W1", message=message)


class LandingTests(RecordCase):
    def test_release_records_the_set_at_its_recorded_heads(self):
        self.commit(ready)
        changed, after, result = self.event("land", "--work", "W1")
        self.assertEqual(changed, {"landings[L2]"})
        landing = after["landings"][-1]
        self.assertEqual({key: landing[key] for key in ("lander", "target", "work", "state", "chief")},
                         {"lander": "Retry owner", "target": "main", "work": ["W1"], "state": "released",
                          "chief": self.state["chief"]})
        self.assertEqual(landing["prs"], [{"url": layer["url"], "head": layer["head"], "base": layer["base"]}
                                          for layer in work(after, "W1")["layers"]])
        self.assertIn("resume Retry owner with landing L2", result.stdout)
        self.refused("land", "--work", "W1", message="already has pending landing L2")
        self.refused("land", "--landing", "L2", "--to", "withdrawn", message="needs --note")
        _, after, _ = self.event("land", "--landing", "L2", "--to", "withdrawn", "--note", "Head moved")
        self.assertEqual(after["landings"][-1]["state"], "withdrawn")

    def test_release_refuses_work_that_is_not_ready(self):
        self.refused("land", "--work", "W1", message="W1 is not ready to land")

    def test_landed_needs_the_forge_to_show_every_pr_merged(self):
        self.commit(ready)
        self.event("land", "--work", "W1")
        urls = [layer["url"] for layer in work(self.state, "W1")["layers"]]
        self.serve(prs={urls[0]: {"state": "MERGED"}, urls[1]: {"state": "OPEN"}})
        self.refused("land", "--landing", "L2", "--to", "landed", message="not merged on the forge")
        self.serve(prs={url: {"state": "MERGED"} for url in urls})
        _, after, _ = self.event("land", "--landing", "L2", "--to", "landed")
        self.assertEqual((work(after, "W1")["state"], after["landings"][-1]["state"]), ("landed", "landed"))


class StatusTests(RecordCase):
    def test_status_records_forge_facts_and_checks_only_what_it_read(self):
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={w1[0]["url"]: {"state": "OPEN", "isDraft": False, "headRefOid": "4d1c9e2" + "0" * 33, "baseRefName": "main"},
                        w1[1]["url"]: {"state": "OPEN", "isDraft": False, "headRefOid": "feed123" + "0" * 33,
                                       "baseRefName": "export-retry-queue"}})
        changed, after, result = self.event("status")
        self.assertEqual(changed, {"work[W1].layers[W1-L2].head", "work[W1].checkedAt"}, "rows with nothing to read keep their checked time")
        self.assertEqual([layer["head"] for layer in work(after, "W1")["layers"]], ["4d1c9e2", "feed123" + "0" * 33])
        self.assertIn("W1: W1-L2 head moved to feed123", result.stdout)
        self.assertTrue(self.commits()[0].startswith("status: W1: W1-L2 head moved"))

    def test_a_moved_head_takes_ready_work_back_to_review(self):
        self.commit(ready)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={w1[0]["url"]: {"state": "OPEN", "headRefOid": "4d1c9e2" + "0" * 33, "baseRefName": "main"},
                        w1[1]["url"]: {"state": "OPEN", "headRefOid": "0123456" + "0" * 33, "baseRefName": "export-retry-queue"}})
        _, after, result = self.event("status")
        self.assertEqual(work(after, "W1")["state"], "in-review")
        self.assertEqual([layer["status"] for layer in work(after, "W1")["layers"]], ["ready", "open"])
        self.assertIn("W1: ready -> in-review", result.stdout)

    def test_merged_layers_land_the_outcome_and_its_release(self):
        self.commit(ready)
        self.event("land", "--work", "W1")
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "MERGED", "headRefOid": layer["head"] + "0" * 33, "baseRefName": layer["base"]}
                        for layer in w1})
        _, after, result = self.event("status")
        self.assertEqual((work(after, "W1")["state"], after["landings"][-1]["state"]), ("landed", "landed"))
        self.assertIn("L2: landed", result.stdout)

    def test_a_forge_fact_the_rules_reject_waits_for_the_chief(self):
        def merged_with_open_need(state):
            ready(state)
            state["decisions"].append({"id": "W1-D8", "question": "Hold it?", "date": "2026-11-02", "source": "msg",
                                       "status": "open", "blocks": [{"id": "W1", "phase": "landing"}]})
        self.commit(merged_with_open_need)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "MERGED", "headRefOid": layer["head"], "baseRefName": layer["base"]} for layer in w1})
        _, after, result = self.event("status")
        self.assertEqual(work(after, "W1")["state"], "ready")
        self.assertEqual({layer["status"] for layer in work(after, "W1")["layers"]}, {"merged"})
        self.assertIn("W1: recorded its forge facts from the forge; settle by hand", result.stdout)

    def test_a_failed_read_keeps_the_old_checked_time(self):
        changed, _, result = self.event("status")
        self.assertNotIn("work[W1].checkedAt", changed)
        self.assertIn("W1: could not read", result.stdout)

    def test_status_lists_what_to_do_now(self):
        def program(state):
            work(state, "W4")["required"] = True
            work(state, "W2")["owner"]["session"] = SESSION.format("w2")
            work(state, "W3")["owner"]["session"] = SESSION.format("w3")
        self.commit(program)
        self.serve(threads={"thread:w2": {"status": "idle", "updatedAt": "2026-11-02T15:00:00Z", "pendingRequestCount": 0},
                            "thread:w3": {"status": "running", "pendingRequestCount": 1}})
        result = self.run_record("status", "--stale-hours", "100000")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertIn("start: W4: Improve export progress estimates", lines)
        self.assertTrue(any(line.startswith("idle owners: W2: API owner idle for ") for line in lines), lines)
        self.assertIn("approvals: W3: Support worker waits on an approval in its thread", lines)
        self.assertFalse(any(line.startswith("idle owners: W3") for line in lines), "a running owner is not idle")
        self.assertTrue(any(line.startswith("needs open: W6-D1: waiting ") for line in lines))
        self.assertFalse(any(line.startswith("stale:") for line in lines))
        self.assertTrue(any(line.startswith("stale:") for line in self.run_record("status").stdout.splitlines()))


class TurnEndTests(RecordCase):
    def turn_end(self):
        before = self.commits()
        result = self.run_record("status", "--turn-end")
        self.assertEqual(self.commits(), before, "the turn-end check writes nothing")
        return result

    def publish(self):
        staged = self.program.folder / "command-center.next.html"
        if staged.exists():
            staged.replace(self.program.folder / "command-center.html")

    def covered(self, state):
        """Every open row has a live owner, a wait, an open decision, or a blocker."""
        for row in state["work"]:
            if row["state"] not in {"landed", "done", "scrapped", "planned"}:
                row["owner"]["session"] = SESSION.format(row["id"])
        work(state, "W4")["blockedBy"] = ["W1"]

    def test_turn_end_fails_on_an_orphaned_item_and_passes_once_it_is_covered(self):
        self.commit(self.covered)
        live = {f"thread:{row['id']}": {"status": "running"} for row in self.state["work"]}
        self.serve(threads=live)
        self.turn_end()
        self.publish()
        self.assertEqual(self.turn_end().returncode, 0)

        self.serve(threads=live | {"thread:W3": {"status": "idle", "updatedAt": "2026-11-02T16:00:00Z"}})
        result = self.turn_end()
        self.assertEqual(result.returncode, 1)
        self.assertIn("orphaned: W3 (building): owner idle", result.stdout)

        self.event("wait", "--on", "Fixture repair", "--event", "Owner reports", "--work", "W3")
        self.assertEqual(self.turn_end().returncode, 0, "a recorded wait covers an idle owner")

        self.event("answer", "--decision", "W6-D1", "--option", "1", "--source", "msg")
        result = self.turn_end()
        self.assertEqual(result.returncode, 1)
        self.assertIn("page: behind record", result.stdout)
        self.publish()
        self.assertEqual(self.turn_end().returncode, 0)

    def test_orphans_name_each_uncovered_row(self):
        state = example()
        work(state, "W4")["required"] = True
        found = orphans(state, {})
        self.assertEqual(found, ["W2 (building): owner has no session to read", "W3 (building): owner has no session to read",
                                 "W4 (planned): not started"])
        state["waits"].append({"date": "2026-11-02", "on": "Fixture", "event": "Repaired", "work": "W3"})
        work(state, "W4")["blocked"] = "Needs a design pass"
        self.assertEqual(orphans(state, {"W2": {"status": "running"}}), [])
        landing = copy.deepcopy(state)
        ready(landing)
        self.assertEqual(orphans(landing, {"W2": {"status": "running"}, "W1": {"status": "idle"}}),
                         ["W1 (ready): ready with no landing release"])
        work(landing, "W1")["finishLine"] = "pr-review"
        self.assertEqual(orphans(landing, {"W2": {"status": "running"}}), [], "a requested PR state is a stop for the user")


if __name__ == "__main__":
    unittest.main()
