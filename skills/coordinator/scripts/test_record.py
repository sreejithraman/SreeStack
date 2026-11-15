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

from record import observe
from render_dashboard import assess, content_name, decision_prompt, observation, orphans, quoted, render, revision, validate
from test_render_dashboard import GIT_ENV, Program, decision, example, now_line, work


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
                                        "route": "`t3_thread_send` to the coordinator"})
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

    def test_start_keeps_a_recorded_owner_and_refuses_another_without_replace(self):
        self.commit(lambda s: work(s, "W4").update(owner={"name": "Progress owner", "start": "top-level", "route": "r",
                                                          "resources": "Preview on port 8100", "handled": ["msg 1"]}))
        self.refused("start", "--work", "W4", "--owner", "Someone else", message="already has owner Progress owner")
        _, after, _ = self.event("start", "--work", "W4", "--owner", "Progress owner", "--session", SESSION.format("w4"))
        self.assertEqual({key: work(after, "W4")["owner"].get(key) for key in ("resources", "handled", "session")},
                         {"resources": "Preview on port 8100", "handled": ["msg 1"], "session": SESSION.format("w4")})

    def test_a_failed_render_after_the_commit_says_the_record_changed(self):
        page = self.program.folder / "command-center.html"
        page.mkdir()
        result = self.run_record("wait", "--on", "CI", "--event", "Done")
        self.assertEqual(self.commits()[0], "wait: CI")
        self.assertIn("page: render failed after the record was saved", result.stdout)
        self.assertNotIn("refused", result.stderr)

    def test_start_drops_satisfied_edges_and_defaults_the_route_by_mode(self):
        self.commit(lambda s: work(s, "W4").update(blockedBy=["W0"]))
        changed, after, result = self.event("start", "--work", "W4", "--owner", "Helper", "--mode", "delegated")
        self.assertNotIn("blockedBy", work(after, "W4"))
        self.assertIn("work[W4].blockedBy", changed)
        self.assertEqual(work(after, "W4")["owner"]["route"], "End its turn with the report; the coordinator watches its PR")
        self.assertIn("dropped satisfied blockedBy W0", result.stdout)

    def test_answer_and_resolve_pick_the_status_from_who_answered(self):
        changed, after, _ = self.event("answer", "--decision", "W6-D1", "--option", "1", "--source", "User message 18:02")
        self.assertEqual(changed, {"decisions[W6-D1].status", "decisions[W6-D1].answer", "decisions[W6-D1].answerSource",
                                   "decisions[W6-D1].applied"})
        self.assertEqual((decision(after, "W6-D1")["status"], decision(after, "W6-D1")["answerSource"]),
                         ("answered", "User message 18:02"))
        self.assertEqual(self.commits()[0], "W6-D1 answered")
        open_need = next(row for row in after["decisions"] if row["status"] == "open")
        _, after, _ = self.event("resolve", "--decision", open_need["id"], "--text", "Keep it", "--basis", "The brief settles it")
        resolved = decision(after, open_need["id"])
        self.assertEqual((resolved["status"], resolved["basis"]), ("resolved", "The brief settles it"))
        self.assertNotIn("answerSource", resolved)
        self.refused("resolve", "--decision", open_need["id"], "--text", "Again", "--basis", "b", message="only an open decision")

    def test_a_user_answer_over_the_coordinators_call_keeps_the_call_in_its_rationale(self):
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
        self.assertEqual(changed, {"decisions[W6-D1].status", "decisions[W6-D1].answer", "decisions[W6-D1].answerSource",
                                   "decisions[W6-D1].applied"})

    def test_a_page_prompt_round_trips_a_label_the_page_reflows(self):
        self.commit(lambda s: decision(s, "W6-D1")["options"][1].update(label="Keep  links\nvisible"))
        need = decision(self.state, "W6-D1")
        prompt = decision_prompt(need, self.state, f'I choose option 2: {quoted(need["options"][1]["label"])}')
        _, after, _ = self.event("answer", "--pasted", "--source", "msg", stdin=prompt)
        self.assertEqual(decision(after, "W6-D1")["answer"], "Keep  links\nvisible", "the recorded option, not the pasted text")

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
    def test_a_shown_image_is_copied_into_the_program_and_committed_with_the_report(self):
        shot = self.program.folder.parent / "owner-screenshot.PNG"
        shot.write_bytes(b"\x89PNG history")
        name = content_name(shot.read_bytes(), ".PNG")
        self.write_report({"outcome": "W1", "state": "in-review", "shown": [
            {"label": "History view", "url": "https://example.com/previews/history", "image": str(shot)}]})
        changed, after, result = self.event("report", "--work", "W1")
        self.assertEqual(work(after, "W1")["results"], [{"label": "History view", "url": "https://example.com/previews/history", "image": name}])
        self.assertEqual((self.program.folder / name).read_bytes(), shot.read_bytes())
        tracked = subprocess.run(["git", "-C", str(self.program.folder), "show", "--name-only", "--format=", "HEAD"],
                                 capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(sorted(tracked), sorted([name, "program.json"]))
        self.assertIn(f"with {name} from beside it", result.stdout, "the page serves the committed copy itself")
        self.assertEqual([path.name for path in (self.program.folder / "files").iterdir()], [name.removeprefix("files/")])

    def test_a_failed_report_commit_leaves_no_image_and_a_retry_records_it(self):
        shot = self.program.folder.parent / "owner-screenshot.png"
        shot.write_bytes(b"\x89PNG history")
        name = content_name(shot.read_bytes(), ".png")
        self.write_report({"outcome": "W1", "state": "in-review", "shown": [
            {"label": "History view", "url": "https://example.com/previews/history", "image": str(shot)}]})
        hook = self.program.folder / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        before, record = self.commits(), self.program.source.read_text()
        self.assertEqual(self.run_record("report", "--work", "W1").returncode, 1)
        self.assertEqual((self.commits(), self.program.source.read_text()), (before, record))
        self.assertEqual(list((self.program.folder / "files").iterdir()), [])
        status = subprocess.run(["git", "-C", str(self.program.folder), "status", "--porcelain"], capture_output=True, text=True).stdout
        self.assertNotIn("files/", status)
        hook.unlink()
        self.event("report", "--work", "W1")
        self.assertEqual((self.program.folder / name).read_bytes(), b"\x89PNG history")

    def test_a_report_never_overwrites_an_edited_image(self):
        shot = self.program.folder.parent / "owner-screenshot.png"
        shot.write_bytes(b"\x89PNG history")
        edited = self.program.folder / content_name(shot.read_bytes(), ".png")
        edited.parent.mkdir()
        edited.write_bytes(b"\x89PNG edited by hand")
        self.write_report({"outcome": "W1", "state": "in-review", "shown": [
            {"label": "History view", "url": "https://example.com/previews/history", "image": str(shot)}]})
        before, record = self.commits(), self.program.source.read_text()
        result = self.run_record("report", "--work", "W1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not hold the bytes its name records", result.stderr)
        self.assertEqual((self.commits(), self.program.source.read_text()), (before, record))
        self.assertEqual(edited.read_bytes(), b"\x89PNG edited by hand")

    def test_a_shown_image_must_be_an_absolute_picture_path(self):
        before = self.commits()
        for image in ("owner-screenshot.png", "/tmp/notes.txt", "/nonexistent/shot.png"):
            self.write_report({"outcome": "W1", "state": "in-review",
                               "shown": [{"label": "View", "url": "https://example.com/v", "image": image}]})
            with self.subTest(image=image):
                result = self.run_record("report", "--work", "W1")
                self.assertEqual(result.returncode, 1)
                self.assertIn("refused:", result.stderr)
        self.assertEqual(self.commits(), before)
        self.assertFalse((self.program.folder / "files").exists())

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

    def test_a_report_leaves_merges_to_the_forge(self):
        layers = copy.deepcopy(work(self.state, "W1")["layers"])
        layers[1]["status"] = "merged"
        self.write_report({"outcome": "W1", "state": "in-review", "layers": layers})
        self.refused("report", "--work", "W1", message="report layer W1-L2 claims merged")

    def test_a_report_cannot_rewrite_a_merged_layer(self):
        self.commit(lambda s: work(s, "W1")["layers"][0].update(status="merged"))
        layers = copy.deepcopy(work(self.state, "W1")["layers"])
        layers[0] |= {"url": "https://example.com/exports/pull/999", "head": "fffffff"}
        self.write_report({"outcome": "W1", "state": "in-review", "layers": layers})
        self.refused("report", "--work", "W1", message="W1-L1 must repeat its merged record unchanged")
        self.write_report({"outcome": "W1", "state": "in-review", "layers": layers[1:]})
        self.refused("report", "--work", "W1", message="W1-L1 must repeat its merged record unchanged")

    def test_a_malformed_report_is_refused(self):
        self.refused("report", "--work", "W1", message="cannot read")
        self.write_report({"outcome": "W1", "state": "in-review"}, prose="")
        path = self.program.folder / "reports" / "W1.md"
        path.write_text("Prose first.\n\n" + path.read_text())
        self.refused("report", "--work", "W1", message="must start with a ```json block")
        for block, message in (({"outcome": "W2", "state": "building"}, "names outcome 'W2'"),
                               ({"outcome": "W1", "state": "blocked"}, "report state must be one of"),
                               ({"outcome": "W1", "state": "in-review", "proof": [{"assertion": "x", "verdict": "ok"}]}, "verdict"),
                               ({"outcome": "W1", "state": "landed"}, "cannot record landed"),
                               ({"outcome": "W1", "state": "in-review", "waits": [{"on": "CI"}]}, "waits[0].event must be")):
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


    def test_release_refuses_a_layer_stacked_on_unreleased_work(self):
        def stacked(state):
            ready(state)
            work(state, "W1")["layers"][1]["status"] = "open"
            work(state, "W1")["state"] = "in-review"
            row = work(state, "W4")
            row.update(state="ready", finishLine="land", owner=copy.deepcopy(work(state, "W1")["owner"]),
                       layers=[{"id": "W4-L1", "branch": "progress", "status": "ready", "url": "https://example.com/exports/pull/50",
                                "head": "abc1234", "base": "export-retry-cancel", "stackedOn": "W1-L2"}])
        self.commit(stacked)
        self.refused("land", "--work", "W4", "--target", "main", message="W4-L1 stacks on unmerged W1-L2 (W1)")

    def test_a_landing_whose_prs_merge_in_separate_runs_lands(self):
        def two(state):
            ready(state)
            row = work(state, "W4")
            row.update(state="ready", finishLine="land", owner={"name": "Progress owner", "start": "top-level", "route": "r"},
                       layers=[{"id": "W4-L1", "branch": "progress", "status": "ready", "url": "https://example.com/exports/pull/50",
                                "head": "abc1234", "base": "main"}])
        self.commit(two)
        self.event("land", "--work", "W1", "--work", "W4", "--lander", "Chief")
        w1 = {layer["url"]: layer for layer in work(self.state, "W1")["layers"]}
        merged = {url: {"state": "MERGED", "headRefOid": layer["head"], "baseRefName": layer["base"]} for url, layer in w1.items()}
        self.serve(prs=merged | {"https://example.com/exports/pull/50": {"state": "OPEN", "headRefOid": "abc1234", "baseRefName": "main"}})
        _, after, _ = self.event("status")
        self.assertEqual((work(after, "W1")["state"], after["landings"][-1]["state"]), ("landed", "released"))
        self.serve(prs={"https://example.com/exports/pull/50": {"state": "MERGED", "headRefOid": "abc1234", "baseRefName": "main"}})
        _, after, _ = self.event("status")
        self.assertEqual((work(after, "W4")["state"], after["landings"][-1]["state"]), ("landed", "landed"))


class StatusTests(RecordCase):
    def test_the_page_shows_the_verdict_and_counts_status_prints(self):
        self.serve(threads={"w1": {"status": "idle"}, "w2": {"status": "running"}, "w5": {"status": "idle"},
                            "w6": {"status": "idle"}})
        result = self.run_record("status", "--json")
        found = json.loads(result.stdout)
        page = (self.program.folder / "command-center.next.html").read_text()
        self.assertIn(f'class="health card {found["verdict"]}"', page)
        counts = {"running": len(found["working"])} | {
            key: sum(entry["kind"] == kind for entry in found["runnable"])
            for key, kind in (("idle", "idle owner"), ("start", "start"), ("land", "release"))}
        self.assertEqual(counts, {"running": 1, "idle": 2, "start": 0, "land": 0})
        for key, count in counts.items():
            self.assertIn(f'<dd data-count="{key}">{count}</dd>', page)

    def test_status_records_forge_facts_and_checks_only_what_it_read(self):
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={w1[0]["url"]: {"state": "OPEN", "isDraft": False, "headRefOid": "4d1c9e2" + "0" * 33, "baseRefName": "main"},
                        w1[1]["url"]: {"state": "OPEN", "isDraft": False, "headRefOid": "feed123" + "0" * 33,
                                       "baseRefName": "export-retry-queue"}})
        changed, after, result = self.event("status")
        changed = {path for path in changed if ".owner.seen." not in path}
        self.assertEqual(changed, {"work[W1].layers[W1-L2].head"}, "a row whose thread read failed keeps its checked time")
        self.assertEqual([layer["head"] for layer in work(after, "W1")["layers"]], ["4d1c9e2", "feed123" + "0" * 33])
        self.assertIn("W1: W1-L2 head moved to feed123", result.stdout)
        self.assertTrue(self.commits()[0].startswith("status: W1: W1-L2 head moved"))

    def test_status_records_each_owner_thread_as_running_idle_or_unknown(self):
        self.serve(threads={"w1": {"status": "idle"}, "w2": {"status": "running"}, "w6": {"status": "waiting"}})
        changed, after, _ = self.event("status")
        seen = {row["id"]: row["owner"].get("seen") for row in after["work"] if "owner" in row}
        at = seen["W1"]["at"]
        self.assertEqual(seen, {"W1": {"state": "idle", "at": at}, "W2": {"state": "running", "at": at},
                                "W5": {"state": "unknown", "at": at}, "W6": {"state": "running", "at": at},
                                "W3": None, "W0": work(self.state, "W0")["owner"].get("seen")})
        self.assertNotEqual(at, work(self.state, "W1")["owner"]["seen"]["at"])
        self.assertIn("work[W2].checkedAt", changed, "a read thread checks its row")
        self.assertNotIn("work[W5].checkedAt", changed, "a failed read leaves its checked time")

    def test_a_moved_head_takes_ready_work_back_to_review(self):
        self.commit(ready)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={w1[0]["url"]: {"state": "OPEN", "headRefOid": "4d1c9e2" + "0" * 33, "baseRefName": "main"},
                        w1[1]["url"]: {"state": "OPEN", "headRefOid": "0123456" + "0" * 33, "baseRefName": "export-retry-queue"}})
        _, after, result = self.event("status")
        self.assertEqual(work(after, "W1")["state"], "in-review")
        self.assertEqual([layer["status"] for layer in work(after, "W1")["layers"]], ["ready", "open"])
        self.assertIn("W1: ready -> in-review", result.stdout)

    def test_a_retargeted_base_takes_ready_work_back_to_review_and_flags_its_release(self):
        self.commit(ready)
        self.event("land", "--work", "W1")
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={w1[0]["url"]: {"state": "OPEN", "headRefOid": w1[0]["head"], "baseRefName": "release"},
                        w1[1]["url"]: {"state": "OPEN", "headRefOid": w1[1]["head"], "baseRefName": w1[1]["base"]}})
        _, after, result = self.event("status")
        self.assertEqual((work(after, "W1")["state"], work(after, "W1")["layers"][0]["base"]), ("in-review", "release"))
        self.assertIn("W1-L1 base moved to release", result.stdout)
        self.assertIn("L2: a released head or base moved; withdraw the release", result.stdout)

    def test_related_forge_facts_apply_whatever_the_row_order(self):
        def stack(order):
            state = example()
            parent = {"id": "P", "title": "Parent", "repo": "example/exports", "kind": "outcome", "finishLine": "land",
                      "state": "in-review", "owner": {"name": "Stack owner", "start": "top-level", "route": "r"},
                      "layers": [{"id": "P-L1", "branch": "parent", "status": "open", "url": "https://example.com/pull/1",
                                  "head": "aaaaaaa", "base": "main"}], "checkedAt": "2026-11-02T17:00:00Z"}
            child = copy.deepcopy(parent) | {"id": "C", "title": "Child"}
            child["layers"] = [{"id": "C-L1", "branch": "child", "status": "open", "url": "https://example.com/pull/2",
                                "head": "bbbbbbb", "base": "parent", "stackedOn": "P-L1"}]
            state["work"] += [parent, child] if order == "PC" else [child, parent]
            return validate(state)
        forge = {"https://example.com/pull/1": {"state": "CLOSED", "headRefOid": "aaaaaaa", "baseRefName": "main"},
                 "https://example.com/pull/2": {"state": "MERGED", "headRefOid": "bbbbbbb", "baseRefName": "parent"}}
        results = []
        for order in ("PC", "CP"):
            state = stack(order)
            observe(state, "2026-11-15T17:00:00Z", lambda url: forge.get(url) or {"state": "OPEN"}, {})
            results.append({row["id"]: (row["state"], row["layers"][0]["status"]) for row in state["work"] if row["id"] in "PC"})
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0], {"P": ("in-review", "closed"), "C": ("landed", "merged")})

    def test_a_first_recorded_head_needs_readiness_again(self):
        def headless(state):
            ready(state)
            for layer in work(state, "W1")["layers"]:
                layer.pop("head")
        self.commit(headless)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "OPEN", "headRefOid": "b" * 40, "baseRefName": layer["base"]} for layer in w1})
        _, after, result = self.event("status")
        self.assertEqual(work(after, "W1")["state"], "in-review")
        self.assertNotIn("release: W1", result.stdout)

    def test_readiness_lapses_even_when_the_moved_facts_need_a_hand(self):
        def retarget(state):
            ready(state)
            work(state, "W4").update(state="in-review", finishLine="land", owner=copy.deepcopy(work(state, "W1")["owner"]),
                                     layers=[{"id": "W4-L1", "branch": "feature-b", "status": "open",
                                              "url": "https://example.com/exports/pull/50", "head": "abc1234", "base": "main"}])
        self.commit(retarget)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={w1[0]["url"]: {"state": "OPEN", "headRefOid": w1[0]["head"], "baseRefName": "feature-b"},
                        w1[1]["url"]: {"state": "OPEN", "headRefOid": w1[1]["head"], "baseRefName": w1[1]["base"]},
                        "https://example.com/exports/pull/50": {"state": "OPEN", "headRefOid": "abc1234", "baseRefName": "main"}})
        _, after, result = self.event("status")
        self.assertEqual((work(after, "W1")["state"], work(after, "W1")["layers"][0]["base"]), ("in-review", "main"))
        self.assertIn("W1: recorded that its readiness lapsed from the forge; settle by hand", result.stdout)
        self.assertNotIn("release: W1", result.stdout)
        self.refused("land", "--work", "W1", message="W1 is not ready to land")

    def test_readiness_lapses_when_a_ready_base_closes_under_its_dependent(self):
        self.commit(ready)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "CLOSED", "headRefOid": layer["head"], "baseRefName": layer["base"]} for layer in w1})
        _, after, result = self.event("status")
        self.assertEqual(work(after, "W1")["state"], "in-review")
        self.assertIn("W1: recorded that its readiness lapsed from the forge; settle by hand", result.stdout)
        self.assertNotIn("release: W1", result.stdout)

    def test_an_owner_state_is_recorded_even_when_forge_facts_are_held_back(self):
        self.commit(ready)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "CLOSED", "headRefOid": layer["head"], "baseRefName": layer["base"]} for layer in w1},
                   threads={"w1": {"status": "running"}, "w2": {"status": "running"}})
        result = self.run_record("status", "--json")
        found = json.loads(result.stdout)
        self.assertIn("W1: recorded that its readiness lapsed", result.stderr)
        self.assertEqual(work(self.head(), "W1")["owner"]["seen"]["state"], "running")
        page = (self.program.folder / "command-center.next.html").read_text()
        self.assertIn(f'<dd data-count="running">{len(found["working"])}</dd>', page)
        self.assertIn(f'class="health card {found["verdict"]}"', page)

    def test_readiness_lapses_for_a_closed_draft_under_its_dependent(self):
        def drafted(state):
            ready(state)
            row = work(state, "W1")
            row["finishLine"] = "pr-draft"
            for layer in row["layers"]:
                layer["status"] = "draft"
        self.commit(drafted)
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "CLOSED", "headRefOid": layer["head"], "baseRefName": layer["base"]} for layer in w1})
        _, after, result = self.event("status")
        self.assertEqual(work(after, "W1")["state"], "in-review")
        self.assertIn("W1: recorded that its readiness lapsed", result.stdout)

    def test_a_rejected_change_holds_back_only_its_own_row(self):
        def program(order):
            state = example()
            held = []
            for identity in ("A", "C"):
                row = {"id": identity, "title": identity, "repo": "example/exports", "kind": "outcome", "finishLine": "land",
                       "state": "ready", "owner": {"name": f"Owner {identity}", "start": "top-level", "route": "r"},
                       "layers": [{"id": f"{identity}-L1", "branch": identity, "status": "ready", "url": f"https://example.com/pull/{identity}",
                                   "head": "aaaaaaa", "base": "main"}], "checkedAt": "2026-11-02T17:00:00Z"}
                held.append(row)
                state["decisions"].append({"id": f"{identity}-D1", "question": "Hold?", "date": "2026-11-02", "source": "msg",
                                           "status": "open", "blocks": [{"id": identity, "phase": "landing"}]})
            state["work"] += held if order == "AC" else held[::-1]
            return validate(state)
        forge = {"https://example.com/pull/A": {"state": "MERGED", "headRefOid": "a" * 40, "baseRefName": "main"},
                 "https://example.com/pull/C": {"state": "MERGED", "headRefOid": "a" * 40, "baseRefName": "main"},
                 "https://example.com/exports/pull/44": {"state": "OPEN", "headRefOid": "c" * 40, "baseRefName": "export-retry-queue"}}
        outcomes = []
        for order in ("AC", "CA"):
            state = program(order)
            notes = observe(state, "2026-11-15T17:00:00Z", lambda url: forge.get(url) or {"state": "OPEN", "headRefOid": "4d1c9e2"}, {})
            rows = {row["id"]: (row["state"], row["layers"][0]["status"], row["layers"][-1].get("head")) for row in state["work"]
                    if row["id"] in {"A", "C", "W1"}}
            blamed = sorted(note.split(":")[0] for note in notes if "settle by hand" in note)
            outcomes.append((rows, blamed))
        self.assertEqual(outcomes[0], outcomes[1])
        rows, blamed = outcomes[0]
        self.assertEqual(blamed, ["A", "C"])
        self.assertEqual((rows["A"][:2], rows["C"][:2]), (("ready", "merged"), ("ready", "merged")))
        self.assertEqual(rows["W1"][2], "c" * 40, "an unrelated row keeps its forge facts")

    def test_merged_layers_land_the_outcome_and_its_release(self):
        self.commit(ready)
        self.event("land", "--work", "W1")
        w1 = work(self.state, "W1")["layers"]
        self.serve(prs={layer["url"]: {"state": "MERGED", "headRefOid": layer["head"] + "0" * 33, "baseRefName": layer["base"]}
                        for layer in w1})
        _, after, result = self.event("status")
        self.assertEqual((work(after, "W1")["state"], after["landings"][-1]["state"]), ("landed", "landed"))
        self.assertIn("L2: landed", result.stdout)

    def test_a_forge_fact_the_rules_reject_waits_for_the_coordinator(self):
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
        self.assertTrue(any(line.startswith("idle owner: W2: API owner is idle with no recorded wait (") for line in lines), lines)
        self.assertIn("approval: W3: Support worker waits on an approval in its thread", lines)
        self.assertFalse(any(line.startswith("idle owner: W3") for line in lines), "a running owner is not idle")
        self.assertTrue(any(line.startswith("need: W6-D1: Should expired export links remain visible? (") for line in lines))
        self.assertTrue(lines[[line.startswith("verdict:") for line in lines].index(True)].startswith("verdict: runnable"))
        self.assertFalse(any(line.startswith("stale:") for line in lines))
        self.assertTrue(any(line.startswith("stale:") for line in self.run_record("status").stdout.splitlines()))


def outcome(identity, state, finish="land", **fields):
    """A self-contained outcome with an owner session and the layer its state needs."""
    row = {"id": identity, "title": f"Work {identity}", "repo": "example/app", "kind": "outcome", "finishLine": finish,
           "state": state, "checkedAt": "2026-11-15T12:00:00Z"}
    if state != "planned":
        row["owner"] = {"name": f"Owner {identity}", "session": SESSION.format(identity), "start": "top-level", "route": "r"}
    if state in {"in-review", "ready", "landed"}:
        status = {"in-review": "open", "ready": "ready", "landed": "merged"}[state]
        row["layers"] = [{"id": f"{identity}-L1", "branch": f"b-{identity}", "status": status,
                          "url": f"https://example.com/app/pull/{identity}", "head": "aaaaaaa", "base": "main"}]
    if state == "shown":
        row["results"] = [{"label": "Preview", "url": "https://example.com/preview"}]
    return row | fields


def need(identity, blocks, phase, reversible=None, **fields):
    row = {"id": identity, "question": f"Question {identity}?", "date": "2026-11-15T10:00:00Z", "source": "msg",
           "status": "open", "blocks": [{"id": blocks, "phase": phase}]}
    if reversible is not None:
        row |= {"weight": "quick", "options": [{"label": "Yes", "effect": "Bounded", "recommended": True}
                                               | ({"reversible": True} if reversible else {}),
                                               {"label": "No", "effect": "Other"}]}
    return row | fields


def program(work_rows, decisions=(), waits=()):
    state = {"title": "Small", "goal": "Goal", "chief": "c", "next": "n", "request": {"text": "r"},
             "decisions": list(decisions), "work": list(work_rows)}
    if waits:
        state["waits"] = list(waits)
    return validate(state)


class VerdictTests(unittest.TestCase):
    AT = "2026-11-15T14:00:00Z"

    def verdict(self, state, threads=None):
        return assess(state, self.AT, threads or {}, 100000)

    def test_runnable_names_each_kind_of_work_the_coordinator_must_act_on(self):
        state = program([outcome("A", "planned"), outcome("B", "ready"), outcome("C", "building"),
                         outcome("D", "in-review")],
                        [need("D-D1", "D", "landing", status="answered", answer="Yes", answerSource="msg", applied=False)])
        result = self.verdict(state, {"C": {"status": "idle", "updatedAt": "2026-11-15T11:00:00Z"},
                                      "D": {"status": "running"}})
        self.assertEqual(result["verdict"], "runnable", "runnable wins over a running owner")
        self.assertEqual({(entry["kind"], entry["id"]) for entry in result["runnable"]},
                         {("start", "A"), ("release", "B"), ("idle owner", "C"), ("apply answer", "D-D1")})
        self.assertEqual(next(entry for entry in result["runnable"] if entry["id"] == "C")["age"], "3h00m")

    def test_working_when_an_owner_runs_and_nothing_is_runnable(self):
        state = program([outcome("A", "building"), outcome("B", "planned", blockedBy=["A"])])
        result = self.verdict(state, {"A": {"status": "running"}})
        self.assertEqual((result["verdict"], result["runnable"]), ("working", []))

    def test_waiting_lists_each_need_and_wait_with_its_age(self):
        state = program([outcome("A", "building"), outcome("B", "in-review")], [need("A-D1", "A", "proof")],
                        [{"date": "2026-11-15T13:30:00Z", "on": "PR B checks", "event": "CI finishes", "work": "B"}])
        result = self.verdict(state, {"A": {"status": "idle"}, "B": {"status": "completed"}})
        self.assertEqual(result["verdict"], "waiting", "working wins over waiting only while an owner runs")
        self.assertEqual([(entry["kind"], entry["id"], entry["age"]) for entry in result["waiting"]],
                         [("need", "A-D1", "4h00m"), ("wait", "B", "30m")])

    def test_done_when_every_outcome_is_terminal_or_at_its_stop(self):
        state = program([outcome("A", "landed"), outcome("B", "ready", finish="pr-review"), outcome("P", "planned", required=False)])
        self.assertEqual(self.verdict(state)["verdict"], "done")
        with_choice = program([outcome("A", "landed"), outcome("C", "shown", finish="try")], [need("C-T", "C", "landing")])
        self.assertEqual(self.verdict(with_choice)["verdict"], "waiting", "a shown Try's open choice wins over done")
        no_choice = self.verdict(program([outcome("A", "landed"), outcome("C", "shown", finish="try")]))
        self.assertEqual((no_choice["verdict"], [entry["kind"] for entry in no_choice["runnable"]]), ("runnable", ["orphan"]),
                         "a shown Try needs its choice recorded")
        program_wait = program([outcome("A", "landed")], waits=[{"date": "2026-11-15T12:00:00Z", "on": "Release CI", "event": "Green"}])
        self.assertEqual(self.verdict(program_wait)["verdict"], "waiting", "waiting wins over done")

    def test_a_reversible_halting_need_is_runnable_until_work_builds_on_it(self):
        state = program([outcome("A", "building")], [need("A-D1", "A", "proof", reversible=True)])
        result = self.verdict(state, {"A": {"status": "running"}})
        self.assertEqual(result["verdict"], "runnable")
        self.assertEqual([(entry["kind"], entry["id"]) for entry in result["runnable"]], [("provisional start", "A")])
        unmarked = program([outcome("A", "building")], [need("A-D1", "A", "proof", reversible=False)])
        self.assertEqual(self.verdict(unmarked, {"A": {"status": "running"}})["verdict"], "working",
                         "a quick pick is not reversible unless its recommended option says so")
        def built_on(basis):
            return program([outcome("A", "building", provisional={"basis": basis, "clears": "It is answered."})],
                           [need("A-D1", "A", "proof", reversible=True)])
        self.assertEqual(self.verdict(built_on("A-D1's recommended option."), {"A": {"status": "running"}})["runnable"], [])
        self.assertEqual([entry["id"] for entry in self.verdict(built_on("A-D10's recommended option."),
                                                                {"A": {"status": "running"}})["runnable"]], ["A"],
                         "A-D10 is not A-D1")
        login = program([outcome("A", "planned")], [need("A-D1", "A", "start", reversible=True), need("A-LOGIN", "A", "access")])
        self.assertEqual(self.verdict(login)["verdict"], "waiting", "a halting Need that is not reversible still holds it")
        for gate in ({"required": False}, {"blocked": "Needs a login"}):
            gated = program([outcome("A", "planned", **gate)], [need("A-D1", "A", "start", reversible=True)])
            with self.subTest(gate=gate):
                self.assertNotIn("provisional start", [entry["kind"] for entry in self.verdict(gated)["runnable"]])

    def now_line(self, state, identity, threads):
        """The page's now line for a row, after status records these thread facts."""
        for row in state["work"]:
            if row["id"] in threads:
                row["owner"]["seen"] = observation(threads[row["id"]], self.AT)
        return now_line(render(state), identity)

    def test_the_now_line_follows_what_status_finds_before_raw_holds(self):
        planned = program([outcome("A", "planned")], [need("A-D1", "A", "start", reversible=True)])
        self.assertEqual(self.now_line(planned, "A", {}), "Ready to start provisionally on A-D1's recommended option.")
        built_on = program([outcome("A", "building", provisional={"basis": "A-D1's recommended option.", "clears": "It is answered."})],
                           [need("A-D1", "A", "proof", reversible=True)])
        self.assertTrue(self.now_line(built_on, "A", {"A": {"status": "running"}}).startswith("Owner A is working."))
        idle = program([outcome("A", "building")], [need("A-D1", "A", "acceptance")])
        self.assertTrue(self.now_line(idle, "A", {"A": {"status": "idle"}}).startswith("Owner A is idle with no recorded wait."),
                        "an idle owner who owes work outranks a Need that lets work continue")
        held = program([outcome("A", "building")], [need("A-D1", "A", "proof")])
        self.assertTrue(self.now_line(held, "A", {"A": {"status": "idle"}}).startswith("Held until you answer A-D1."))

    def test_a_recorded_approval_shows_on_the_page_as_status_finds_it(self):
        state = program([outcome("A", "building")])
        thread = {"status": "running", "pendingRequestCount": 2}
        self.assertEqual(observation(thread, self.AT), {"state": "running", "at": self.AT, "approvals": 2})
        self.assertIn("approval", [entry["kind"] for entry in self.verdict(state, {"A": thread})["attention"]])
        self.assertTrue(self.now_line(state, "A", {"A": thread}).startswith("Owner A waits on an approval in its thread."))

    def test_a_blocked_idle_owner_waits_instead_of_running(self):
        state = program([outcome("A", "building", blocked="Needs the user's App Store login")])
        result = self.verdict(state, {"A": {"status": "idle"}})
        self.assertEqual((result["verdict"], [entry["kind"] for entry in result["waiting"]]), ("waiting", ["blocked"]))

    def test_the_digest_follows_facts_not_the_clock(self):
        state = program([outcome("A", "building")], [need("A-D1", "A", "proof")])
        first = self.verdict(state)
        later = assess(state, "2026-11-16T09:00:00Z", {}, 100000)
        self.assertEqual(first["digest"], later["digest"])
        self.assertNotEqual(first["waiting"][0]["age"], later["waiting"][0]["age"])
        state["decisions"].append(need("A-D2", "A", "access"))
        self.assertNotEqual(self.verdict(state)["digest"], first["digest"])
        review = program([outcome("B", "in-review")], waits=[{"date": "2026-11-15T13:00:00Z", "on": "CI", "event": "Green", "work": "B"}])
        before = self.verdict(review)["digest"]
        review["work"][0]["layers"][0]["status"] = "closed"
        self.assertNotEqual(self.verdict(review)["digest"], before, "a forge change under a wait changes the digest")
        for current in ("building", "unknown"):
            fields = {"unknownReason": "Owner went quiet"} if current == "unknown" else {}
            unread = program([outcome("C", current, **fields)])
            with self.subTest(state=current):
                self.assertEqual(self.verdict(unread, {"C": "could not read its thread: timeout"})["digest"],
                                 self.verdict(unread, {"C": "could not read its thread: refused"})["digest"])
                self.assertNotEqual(self.verdict(unread, {"C": "could not read its thread: timeout"})["digest"],
                                    self.verdict(unread, {"C": {"status": "running"}})["digest"])


class VerdictCommandTests(RecordCase):
    def test_exit_codes_and_json_carry_the_verdict(self):
        cases = {"done": program([outcome("A", "landed")]),
                 "waiting": program([outcome("A", "building")], [need("A-D1", "A", "proof")]),
                 "working": program([outcome("A", "building")]),
                 "runnable": program([outcome("A", "planned")])}
        for verdict, state in cases.items():
            self.program.write(state, "2026-11-15T13:00:00Z")
            self.serve(prs={"https://example.com/app/pull/A": {"state": "MERGED", "headRefOid": "aaaaaaa", "baseRefName": "main"}},
                       threads={"thread:A": {"status": "running" if verdict == "working" else "idle"}})
            result = self.run_record("status", "--json", "--exit-code")
            with self.subTest(verdict=verdict):
                self.assertEqual(json.loads(result.stdout)["verdict"], verdict, result.stderr)
                self.assertEqual(result.returncode, {"done": 0, "waiting": 3, "working": 4, "runnable": 5}[verdict])
                self.assertIn(f"verdict: {verdict}", result.stderr, "human output moves to stderr with --json")
                self.assertEqual(self.run_record("status").returncode, 0, "without --exit-code status exits 0")

    def test_a_waiting_status_says_what_it_waits_on_with_ages(self):
        state = program([outcome("A", "building", blocked="Needs the user's App Store login")],
                        [need("A-D1", "A", "proof")],
                        waits=[{"date": "2026-11-15T13:00:00Z", "on": "CI on #44", "event": "checks finish", "work": "A"}])
        self.program.write(state, "2026-11-15T13:00:00Z")
        self.serve(threads={"thread:A": {"status": "idle"}})
        line = next(text for text in self.run_record("status").stdout.splitlines() if text.startswith("say: "))
        self.assertRegex(line, r"^say: Waiting on A: Needs the user's App Store login; Inbox A-D1 \([0-9dhm]+\); "
                               r"A: CI on #44 until checks finish \([0-9dhm]+\)\. Nothing is runnable\.$")

    def heartbeat(self, *extra):
        before = self.commits()
        result = self.run_record("status", "--heartbeat", "--json", *extra)
        self.assertEqual((result.returncode, self.commits()), (0, before), "a heartbeat tick commits nothing")
        self.assertEqual(json.loads(self.program.source.read_text()), self.head(), "nor touches the record")
        return json.loads(result.stdout)["heartbeat"], result.stderr

    def test_a_heartbeat_stays_quiet_until_the_facts_change_and_wakes_on_runnable_work(self):
        self.program.write(program([outcome("A", "building")], [need("A-D1", "A", "acceptance")]), "2026-11-15T13:00:00Z")
        self.serve(threads={"thread:A": {"status": "running"}})
        self.assertEqual(self.heartbeat()[0], "wake", "the first tick has no digest to compare")
        tick, output = self.heartbeat()
        self.assertEqual(tick, "quiet")
        self.assertIn("End the turn without a message", output)
        self.serve(threads={"thread:A": {"status": "idle"}})
        tick, output = self.heartbeat()
        self.assertEqual(tick, "wake", "an owner that went idle while owing work")
        self.assertRegex(output, r"Re-read \S+/coordinator/SKILL\.md, run status")
        self.assertEqual(self.heartbeat()[0], "wake", "runnable work wakes every tick")

    def test_a_passing_turn_end_is_the_baseline_a_heartbeat_compares(self):
        self.program.write(program([outcome("A", "building")], [need("A-D1", "A", "proof")]), "2026-11-15T13:00:00Z")
        self.serve(threads={"thread:A": {"status": "running"}})
        self.run_record("status", "--turn-end")
        (self.program.folder / "command-center.next.html").replace(self.program.folder / "command-center.html")
        self.assertEqual(self.run_record("status", "--turn-end", "--stale-hours", "1000000").returncode, 0)
        self.assertEqual(self.heartbeat("--stale-hours", "1000000")[0], "quiet")

    def test_a_heartbeat_on_a_done_program_says_to_remove_itself(self):
        self.program.write(program([outcome("A", "landed")]), "2026-11-15T13:00:00Z")
        self.serve(prs={"https://example.com/app/pull/A": {"state": "MERGED", "headRefOid": "aaaaaaa", "baseRefName": "main"}})
        tick, output = self.heartbeat()
        self.assertEqual(tick, "done")
        self.assertIn("Delete the scheduled task in the record's grant.heartbeat", output)

    def test_a_live_owner_moving_between_running_and_waiting_keeps_the_heartbeat_quiet(self):
        self.program.write(program([outcome("A", "building")]), "2026-11-15T13:00:00Z")
        self.serve(threads={"thread:A": {"status": "running"}})
        self.heartbeat()
        self.serve(threads={"thread:A": {"status": "waiting"}})
        self.assertEqual(self.heartbeat()[0], "quiet", "waiting on its own helpers is still working")

    def test_a_base_closing_under_provisional_work_wakes_the_coordinator_once(self):
        base = outcome("A", "in-review")
        built = outcome("B", "building", provisional={"basis": "A's layer A-L1", "clears": "A lands", "on": ["A"]},
                        layers=[{"id": "B-L1", "branch": "b-B", "status": "open", "url": "https://example.com/app/pull/B",
                                 "head": "bbbbbbb", "base": "b-A", "stackedOn": "A-L1"}])
        self.program.write(program([base, built], waits=[{"date": "2026-11-15T13:00:00Z", "on": "CI", "event": "Green",
                                                          "work": "A"}]), "2026-11-15T13:00:00Z")
        threads = {"thread:A": {"status": "running"}, "thread:B": {"status": "running"}}
        pr = {"state": "OPEN", "headRefOid": "aaaaaaa", "baseRefName": "main"}
        self.serve(prs={"https://example.com/app/pull/A": pr,
                        "https://example.com/app/pull/B": pr | {"headRefOid": "bbbbbbb", "baseRefName": "b-A"}},
                   threads=threads)
        self.heartbeat()
        self.assertEqual(self.heartbeat()[0], "quiet")
        self.serve(prs={"https://example.com/app/pull/A": pr | {"state": "CLOSED"},
                        "https://example.com/app/pull/B": pr | {"headRefOid": "bbbbbbb", "baseRefName": "b-A"}},
                   threads=threads)
        tick, output = self.heartbeat()
        self.assertEqual(tick, "wake", "the record rejects the closed base, so only the note shows it")
        self.assertIn("settle by hand", output)
        self.assertEqual(self.heartbeat()[0], "quiet", "a note already seen does not wake again")

    def test_a_last_merge_the_heartbeat_finds_wakes_the_coordinator_to_record_it(self):
        row = outcome("A", "ready")
        state = program([row])
        state["landings"] = [{"id": "L1", "date": "2026-11-15T13:00:00Z", "chief": "c", "lander": "Owner A", "target": "main",
                              "work": ["A"], "prs": [{"url": "https://example.com/app/pull/A", "head": "aaaaaaa", "base": "main"}],
                              "state": "submitted"}]
        self.program.write(state, "2026-11-15T13:00:00Z")
        self.serve(prs={"https://example.com/app/pull/A": {"state": "MERGED", "headRefOid": "aaaaaaa", "baseRefName": "main"}},
                   threads={"thread:A": {"status": "running"}})
        tick, output = self.heartbeat()
        self.assertEqual(tick, "wake", "done waits until the record shows it")
        self.assertIn("note: L1: landed", output)

    def test_a_failing_read_wakes_once_and_again_when_its_row_goes_stale(self):
        self.program.write(program([outcome("A", "in-review")], waits=[{"date": "2026-11-15T13:00:00Z", "on": "CI",
                                                                        "event": "Green", "work": "A"}]), "2026-11-15T13:00:00Z")
        self.serve(threads={"thread:A": {"status": "running"}})
        fresh = ("--stale-hours", "1000000")
        tick, output = self.heartbeat(*fresh)
        self.assertEqual(tick, "wake")
        self.assertIn("note: A: could not read https://example.com/app/pull/A", output)
        self.assertEqual(self.heartbeat(*fresh)[0], "quiet", "the same failure does not wake every tick")
        tick, output = self.heartbeat()
        self.assertEqual(tick, "wake", "a row the heartbeat cannot see goes stale")
        self.assertIn("note: A: not observed since 2026-11-15T12:00:00Z", output)
        self.assertEqual(self.heartbeat()[0], "quiet")

    def test_proposed_work_waiting_on_a_stopped_outcome_lets_the_program_finish(self):
        state = program([outcome("A", "ready", finish="pr-review"),
                         outcome("B", "planned", required=False, blockedBy=["A"])])
        self.assertEqual(assess(state, VerdictTests.AT, {"A": {"status": "idle"}})["verdict"], "done")

    def test_a_dependency_alone_still_names_what_the_program_waits_on(self):
        self.program.write(program([outcome("A", "ready", finish="pr-review"), outcome("B", "planned", blockedBy=["A"])]),
                           "2026-11-15T13:00:00Z")
        self.serve(prs={"https://example.com/app/pull/A": {"state": "OPEN", "headRefOid": "aaaaaaa", "baseRefName": "main"}},
                   threads={"thread:A": {"status": "idle"}})
        self.assertIn("say: Waiting on B: needs A. Nothing is runnable.", self.run_record("status").stdout)

    def test_applied_clears_an_answer_once_its_owners_have_it(self):
        self.event("answer", "--decision", "W6-D1", "--option", "1", "--source", "msg")
        self.assertIn("apply answer: W6-D1", self.run_record("status").stdout)
        changed, after, _ = self.event("applied", "--decision", "W6-D1")
        self.assertEqual(changed, {"decisions[W6-D1].applied"})
        self.assertNotIn("apply answer", self.run_record("status").stdout)
        self.refused("applied", "--decision", "W6-D1", message="no answer waiting to be applied")


class TurnEndTests(RecordCase):
    def turn_end(self):
        before = self.commits()
        result = self.run_record("status", "--turn-end")
        self.assertEqual(self.commits(), before, "the turn-end check commits nothing")
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
        self.assertIn("idle owner: W3: Support worker is idle with no recorded wait", result.stdout)

        self.event("wait", "--on", "Fixture repair", "--event", "Owner reports", "--work", "W3")
        self.publish()  # the page shows the wait
        self.assertEqual(self.turn_end().returncode, 0, "a recorded wait covers an idle owner")

        self.event("answer", "--decision", "W6-D1", "--option", "1", "--source", "msg")
        result = self.turn_end()
        self.assertEqual(result.returncode, 1)
        self.assertIn("apply answer: W6-D1", result.stdout)
        self.assertIn("page: behind record", result.stdout)
        self.event("applied", "--decision", "W6-D1")
        self.publish()
        self.assertEqual(self.turn_end().returncode, 0)

    def test_a_released_landing_with_an_idle_owner_is_orphaned(self):
        state = example()
        ready(state)
        state["waits"].append({"date": "2026-11-02", "on": "Fixture", "event": "Repaired", "work": "W3"})
        state["landings"].append({"id": "L2", "date": "2026-11-02", "chief": "c", "lander": "Retry owner", "target": "main",
                                  "work": ["W1"], "prs": [{"url": "https://example.com/exports/pull/42", "head": "4d1c9e2", "base": "main"}],
                                  "state": "released"})
        work(state, "W1")["owner"]["session"] = SESSION.format("w1")
        threads = {"W2": {"status": "running"}, "W6": {"status": "running"}, "W1": {"status": "idle"}}
        self.assertEqual(orphans(state, threads), ["W1 (ready): owner idle with landing L2 released"])
        self.assertEqual(orphans(state, threads | {"W1": {"status": "running"}}), [])

    def test_a_need_that_lets_work_continue_does_not_cover_an_idle_owner(self):
        state = example()
        work(state, "W6")["owner"]["session"] = SESSION.format("w6")
        threads = {"W6": {"status": "idle"}}
        self.assertIn("W6 (building): owner idle", orphans(state, threads))
        decision(state, "W6-D1")["blocks"] = [{"id": "W6", "phase": "proof"}]
        self.assertNotIn("W6 (building): owner idle", orphans(state, threads), "a halting Need covers it")

    def test_turn_end_fails_while_the_verdict_is_runnable(self):
        self.program.write(program([outcome("A", "building")], [need("A-D1", "A", "proof", reversible=True)]), "2026-11-15T13:00:00Z")
        self.serve(threads={"thread:A": {"status": "running"}})
        self.turn_end()
        self.publish()
        result = self.turn_end()
        self.assertEqual(result.returncode, 1)
        self.assertIn("provisional start: A: build on A-D1's recommended option provisionally", result.stdout)
        self.assertNotIn("orphaned:", result.stdout)

    def test_turn_end_fails_while_the_record_has_an_uncommitted_change(self):
        self.state["next"] = "Hand edit in progress"
        self.program.write(self.state)
        self.assertIn("uncommitted: program.json has a change", self.turn_end().stdout)

    def test_orphans_name_each_uncovered_row(self):
        state = example()
        work(state, "W4")["required"] = True
        found = orphans(state, {})
        self.assertEqual(found, ["W2 (building): owner has no session to read", "W6 (building): owner has no session to read",
                                 "W3 (building): owner has no session to read", "W4 (planned): not started"],
                         "W6's open Need blocks only acceptance, so its owner should still be building")
        state["waits"].append({"date": "2026-11-02", "on": "Fixture", "event": "Repaired", "work": "W3"})
        work(state, "W4")["blocked"] = "Needs a design pass"
        self.assertEqual(orphans(state, {"W2": {"status": "running"}, "W6": {"status": "running"}}), [])
        landing = copy.deepcopy(state)
        ready(landing)
        self.assertEqual(orphans(landing, {"W2": {"status": "running"}, "W6": {"status": "running"}, "W1": {"status": "idle"}}),
                         ["W1 (ready): ready with no landing release"])
        work(landing, "W1")["finishLine"] = "pr-review"
        self.assertEqual(orphans(landing, {"W2": {"status": "running"}, "W6": {"status": "running"}}), [], "a requested PR state is a stop for the user")


if __name__ == "__main__":
    unittest.main()
