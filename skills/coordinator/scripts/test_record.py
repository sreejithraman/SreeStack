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

from record import Refused, answer_stored, gh_pr, observe, stored_picks
from render_dashboard import assess, content_name, decision_prompt, observation, orphans, quoted, render, revision, validate
from test_render_dashboard import GIT_ENV, Program, decision, example, now_line, work


SCRIPT = Path(__file__).with_name("record.py")
FAKE = textwrap.dedent("""\
    import json, os, sys
    GH_PR_VIEW_ALLOWED = {
        "additions", "assignees", "author", "autoMergeRequest", "baseRefName", "baseRefOid", "body",
        "changedFiles", "closed", "closedAt", "closingIssuesReferences", "comments", "commits", "createdAt",
        "deletions", "files", "fullDatabaseId", "headRefName", "headRefOid", "headRepository",
        "headRepositoryOwner", "id", "isCrossRepository", "isDraft", "labels", "latestReviews",
        "maintainerCanModify", "mergeCommit", "mergeStateStatus", "mergeable", "mergedAt", "mergedBy",
        "milestone", "number", "potentialMergeCommit", "projectCards", "projectItems", "reactionGroups",
        "reviewDecision", "reviewRequests", "reviews", "state", "statusCheckRollup", "title", "updatedAt", "url",
    }
    fixtures = json.load(open(os.environ["RECORD_FIXTURES"]))
    if sys.argv[1:3] == ["api", "graphql"]:
        host = None
        variables = {}
        index = 3
        while index < len(sys.argv):
            arg = sys.argv[index]
            if arg == "--hostname":
                host = sys.argv[index + 1]
                index += 2
            elif arg in {"-f", "-F"}:
                key, value = sys.argv[index + 1].split("=", 1)
                variables[key] = value
                index += 2
            else:
                index += 1
        if not host or "query" not in variables or not {"owner", "name", "number"} <= set(variables):
            sys.exit("invalid graphql invocation: missing --hostname or required variables")
        url = f"https://{host}/{variables['owner']}/{variables['name']}/pull/{variables['number']}"
        if url not in fixtures["prs"]:
            sys.exit(f"{url} not found")
        print(json.dumps({"data": {"repository": {"pullRequest": fixtures["prs"][url]}}}))
        sys.exit(0)
    if sys.argv[1] == "pr":
        if "--json" in sys.argv:
            requested = sys.argv[sys.argv.index("--json") + 1].split(",")
            unknown = [field for field in requested if field not in GH_PR_VIEW_ALLOWED]
            if unknown:
                sys.exit(f'Unknown JSON field: "{unknown[0]}"')
        key = sys.argv[3]
        if key not in fixtures["prs"]:
            sys.exit(f"{key} not found")
        print(json.dumps(fixtures["prs"][key]))
        sys.exit(0)
    key = sys.argv[-1]
    if key not in fixtures["threads"]:
        sys.exit(f"{key} not found")
    print(json.dumps({"thread": fixtures["threads"][key], "messages": []}))
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
                                                          "resources": "Preview on port 8100", "handled": ["msg 1"],
                                                          "seen": {"state": "idle", "at": "2026-11-02T16:00:00Z"}}))
        self.refused("start", "--work", "W4", "--owner", "Someone else", message="already has owner Progress owner")
        _, after, _ = self.event("start", "--work", "W4", "--owner", "Progress owner", "--session", SESSION.format("w4"))
        self.assertEqual({key: work(after, "W4")["owner"].get(key) for key in ("resources", "handled", "session")},
                         {"resources": "Preview on port 8100", "handled": ["msg 1"], "session": SESSION.format("w4")})
        self.assertNotIn("seen", work(after, "W4")["owner"], "a new session has not been read")

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
        self.refused("wait", "--on", "CI2", "--event", "Done", "--next", "x" * 281, message="at most 280 characters")
        self.refused("wait", "--on", "CI2", "--event", "Done", "--next", "Line 1\nLine 2", message="one short line")


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
        subprocess.run(["git", "-C", str(self.program.folder), "add", "files"], check=True)
        self.write_report({"outcome": "W1", "state": "in-review", "shown": [
            {"label": "History view", "url": "https://example.com/previews/history", "image": str(shot)}]})
        before, record = self.commits(), self.program.source.read_text()
        result = self.run_record("report", "--work", "W1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not hold the bytes its name records", result.stderr)
        self.assertEqual((self.commits(), self.program.source.read_text()), (before, record))
        self.assertEqual(edited.read_bytes(), b"\x89PNG edited by hand")
        staged = subprocess.run(["git", "-C", str(self.program.folder), "diff", "--cached", "--name-only"],
                                capture_output=True, text=True).stdout.split()
        self.assertEqual(staged, [edited.relative_to(self.program.folder).as_posix()], "a refusal leaves the index alone")

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
        self.refused("land", "--landing", "L2", "--to", "withdrawn", "--note", "Head moved",
                     message="move it to --to cancelling first")
        self.event("land", "--landing", "L2", "--to", "cancelling", "--note", "Head moved")
        self.serve(prs={
            layer["url"]: {"state": "OPEN", "isDraft": False, "headRefOid": layer["head"], "baseRefName": layer["base"],
                           "autoMergeRequest": None, "isInMergeQueue": False}
            for layer in work(after, "W1")["layers"]
        })
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
        unreadable = {"state": "unknown", "at": "2026-11-02T16:00:00Z"}
        self.commit(lambda state: work(state, "W5")["owner"].update(seen=unreadable))
        _, again, _ = self.event("status")
        self.assertEqual(work(again, "W5")["owner"]["seen"], unreadable, "a thread still unreadable keeps when it became so")

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
        self.assertIn("L2: a released head or base moved; move it to --to cancelling before notifying", result.stdout)

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
        self.run_record("status")
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


class PictureTests(RecordCase):
    def picture_file(self, name, content):
        path = self.program.folder.parent / name
        path.write_bytes(content)
        return path

    def committed_files(self):
        return sorted(subprocess.run(["git", "-C", str(self.program.folder), "show", "--name-only", "--format=", "HEAD"],
                                     capture_output=True, text=True, check=True).stdout.split())

    def test_an_owners_ask_carries_its_pictures_into_the_inbox(self):
        before, after, option = (self.picture_file(f"{label}.png", f"\x89PNG {label}".encode()) for label in ("before", "after", "option"))
        names = {path: content_name(path.read_bytes(), ".png") for path in (before, after, option)}
        ReportTests.write_report(self, {"outcome": "W1", "state": "building", "asks": [{
            "id": "W1-D9", "question": "Which empty state?", "pictures": {"shape": "before-after", "images": [
                {"image": str(before)}, {"image": str(after), "caption": "With the hint"}]},
            "options": [{"label": "Hint", "effect": "Shows a hint.", "image": str(option), "recommended": True},
                        {"label": "Blank", "effect": "Stays blank."}]}]})
        _, record, _ = self.event("report", "--work", "W1")
        need = decision(record, "W1-D9")
        self.assertEqual(need["pictures"], {"shape": "before-after", "images": [
            {"image": names[before]}, {"image": names[after], "caption": "With the hint"}]})
        self.assertEqual(need["options"][0]["image"], names[option])
        self.assertEqual(self.committed_files(), sorted([*names.values(), "program.json"]))
        page = (self.program.folder / "command-center.next.html").read_text()
        self.assertIn('class="pictures before-after"', page)
        for name in names.values():
            self.assertEqual((self.program.folder / name).read_bytes(), next(path.read_bytes() for path in names if names[path] == name))

    def test_a_repeated_ask_needs_none_of_its_old_pictures(self):
        gone = self.program.folder.parent / "deleted-preview.png"
        ReportTests.write_report(self, {"outcome": "W1", "state": "building", "asks": [{
            "id": "W1-D2", "question": "Repeated", "pictures": {"images": [{"image": str(gone)}]},
            "options": [{"label": "A", "effect": "a", "image": str(gone)}, {"label": "B", "effect": "b"}]}]})
        _, record, result = self.event("report", "--work", "W1")
        self.assertIn("decision W1-D2 is already recorded", result.stdout)
        self.assertEqual(self.committed_files(), ["program.json"], "an ignored ask adds no picture")

    def test_picture_sets_an_open_decisions_pictures_or_one_options(self):
        first, second = self.picture_file("one.png", b"\x89PNG one"), self.picture_file("two.png", b"\x89PNG two")
        changed, record, result = self.event("picture", "--decision", "W5-T", "--shape", "before-after",
                                             "--image", str(first), "--image", str(second), "--caption", "After the fix")
        self.assertEqual(changed, {"decisions[W5-T].pictures"})
        self.assertEqual(decision(record, "W5-T")["pictures"], {"shape": "before-after", "images": [
            {"image": content_name(b"\x89PNG one", ".png")}, {"image": content_name(b"\x89PNG two", ".png"), "caption": "After the fix"}]})
        self.assertIn("page: behind record", result.stdout)
        changed, record, _ = self.event("picture", "--decision", "W5-T", "--option", "3", "--image", str(first))
        self.assertEqual(changed, {"decisions[W5-T].options"})
        self.assertEqual(decision(record, "W5-T")["options"][2]["image"], content_name(b"\x89PNG one", ".png"))
        _, record, _ = self.event("picture", "--decision", "W5-T", "--image", str(second))
        self.assertEqual(decision(record, "W5-T")["pictures"], {"images": [{"image": content_name(b"\x89PNG two", ".png")}]},
                         "a new set replaces the old one")
        self.refused("picture", "--decision", "W5-T", "--shape", "before-after", "--image", str(first), message="takes exactly 2 images")
        self.refused("picture", "--decision", "W0-D1", "--image", str(first), message="pictures go on open decisions")
        self.refused("picture", "--decision", "W5-T", "--option", "1", "--image", str(first), "--image", str(second),
                     message="an option takes one picture")
        self.refused("picture", "--decision", "W5-T", "--image", str(self.program.folder.parent / "missing.png"), message="cannot read")

    def test_a_record_that_names_a_missing_picture_is_refused(self):
        self.event("picture", "--decision", "W5-T", "--image", str(self.picture_file("one.png", b"\x89PNG one")))
        (self.program.folder / content_name(b"\x89PNG one", ".png")).unlink()
        self.refused("wait", "--on", "PR 44 checks", "--event", "Checks finish", message="is missing from")


def stored(*picks, version=3, saved="2026-11-02T18:00:00Z"):
    """db_query output for the page's picks collection: a summary line, then one document per line, wrapped."""
    lines = [json.dumps({"count": len(picks), "nextCursor": None}), "<untrusted-document-1a2b>"]
    lines += [json.dumps({"id": f"{pick['decision'].encode().hex()}-{pick['revision']}", "data": pick, "version": version,
                          "updatedAt": saved}) for pick in picks]
    return "\n".join([*lines, "</untrusted-document-1a2b>", ""])


class StoredPickTests(RecordCase):
    def answer_stored(self, *picks, documents=None):
        path = self.program.folder.parent / "picks.jsonl"
        path.write_text(documents if documents is not None else stored(*picks))
        return ["answer", "--stored", str(path)]

    def pick(self, identity, option, digest=None, label=None):
        need = decision(self.head(), identity)
        return {"decision": identity, "revision": digest or revision(need), "option": option,
                "label": label or need["options"][option - 1]["label"]}

    def test_a_pick_at_the_current_revision_records_the_users_answer_and_names_its_cleanup(self):
        pick = self.pick("W6-D1", 2)
        changed, record, result = self.event(*self.answer_stored(pick))
        need = decision(record, "W6-D1")
        path = f"picks/{'W6-D1'.encode().hex()}-{pick['revision']}"
        self.assertEqual((need["status"], need["answer"]), ("answered", "Hide expired entries"))
        self.assertEqual(need["answerSource"], f"The user's pick on the command center, stored at {path} (version 3)")
        self.assertEqual(changed, {"decisions[W6-D1].status", "decisions[W6-D1].answer", "decisions[W6-D1].answerSource",
                                   "decisions[W6-D1].applied", "decisions[W6-D1].picksRead"})
        self.assertEqual(need["picksRead"], [f"{path} (version 3) 2026-11-02T18:00:00Z"])
        self.assertIn(f"note: delete: {path} (version 3)", result.stdout.splitlines())
        self.assertEqual(self.commits()[0], "W6-D1 answered from the page")

    def test_a_stale_revision_never_applies_and_the_inbox_asks_again(self):
        stale = self.pick("W6-D1", 2, digest="0123456789")
        changed, record, result = self.event(*self.answer_stored(stale))
        need = decision(record, "W6-D1")
        self.assertEqual(need["status"], "open")
        self.assertNotIn("answer", need)
        self.assertEqual(changed, {"decisions[W6-D1].stalePick", "decisions[W6-D1].picksRead"})
        self.assertEqual(need["stalePick"]["label"], "Hide expired entries")
        self.assertIn("note: stale: W6-D1 changed since the page showed it; the Inbox asks again", result.stdout)
        self.assertIn("pick again", (self.program.folder / "command-center.next.html").read_text())

        renamed = self.pick("W5-T", 1, label="Merge it now")
        _, record, _ = self.event(*self.answer_stored(renamed))
        self.assertEqual(decision(record, "W5-T")["status"], "open", "a label that is not the option's never applies")

        _, record, _ = self.event(*self.answer_stored(documents=stored(self.pick("W6-D1", 1), saved="2026-11-02T18:10:00Z")))
        self.assertEqual(decision(record, "W6-D1")["answer"], "Keep the entry")
        self.assertNotIn("stalePick", decision(record, "W6-D1"), "a current answer clears the stale pick")

    def test_a_pick_for_a_settled_decision_becomes_a_reopen_request(self):
        same = {"decision": "W0-D1", "revision": "0123456789", "option": 1, "label": "Keep the original job ID."}
        changed, record, result = self.event(*self.answer_stored(same))
        self.assertEqual(changed, {"decisions[W0-D1].picksRead"}, "a pick that matches the recorded answer is only read")
        self.assertIn("W0-D1 already records", result.stdout)

        changed, record, result = self.event(
            *self.answer_stored(documents=stored(dict(same, label="Use a new job ID"), saved="2026-11-02T18:10:00Z")))
        self.assertEqual(changed, {"decisions[W0-D1].stalePick", "decisions[W0-D1].picksRead"})
        self.assertEqual(decision(record, "W0-D1")["status"], "answered", "the recorded answer stands until the reopen")
        self.assertIn('reopen request: the user picked "Use a new job ID" after W0-D1 was answered', result.stdout)
        verdict = assess(record, "2026-11-02T18:00:00Z", {})
        self.assertIn(("reopen request", "W0-D1"), [(entry["kind"], entry["id"]) for entry in verdict["runnable"]])

    def test_untrusted_documents_are_ignored(self):
        pick = self.pick("W6-D1", 1)
        documents = "\n".join([
            json.dumps({"count": 4, "nextCursor": ""}), "not json", json.dumps(["a list"]),
            json.dumps({"id": "renamed-0123456789", "data": pick, "version": 1, "updatedAt": "2026-11-02T18:00:00Z"}),
            json.dumps({"id": f"{'W6-D1'.encode().hex()}-{pick['revision']}", "data": dict(pick, option="1"), "version": 2, "updatedAt": "2026-11-02T18:00:00Z"}),
            json.dumps({"id": f"{'W9-D1'.encode().hex()}-{pick['revision']}", "data": dict(pick, decision="W9-D1"), "version": 3, "updatedAt": "2026-11-02T18:00:00Z"}),
            json.dumps({"id": f"{'W2-D1'.encode().hex()}-{pick['revision']}", "data": dict(pick, decision="W2-D1"), "version": 4, "updatedAt": "2026-11-02T18:00:00Z"}),
        ])
        result = self.run_record(*self.answer_stored(documents=documents))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.commits()), 1)
        self.assertEqual(result.stdout.count("not a pick the page writes"), 2)
        self.assertIn("W9-D1 is not recorded", result.stdout)
        self.assertIn("W2-D1 is withdrawn", result.stdout)
        self.assertEqual(result.stdout.count("delete: picks/"), 4, "every stored document is cleaned up")
        self.refused("answer", "--stored", str(self.program.folder.parent / "picks.jsonl"), "--source", "msg",
                     message="takes its decisions and source from the stored picks")

    def test_a_current_pick_wins_over_stale_ones_in_any_order(self):
        current, stale = self.pick("W6-D1", 1), self.pick("W6-D1", 2, digest="0123456789")
        outcomes = []
        for documents in ((current, stale), (stale, current)):
            record = self.head()
            answer_stored(record, "2026-11-02T18:00:00Z", stored_picks(stored(*documents)))
            need = decision(record, "W6-D1")
            outcomes.append((need["status"], need["answer"], "stalePick" in need,
                             [entry["kind"] for entry in assess(record, "2026-11-02T18:00:00Z", {})["runnable"]
                              if entry["id"] == "W6-D1"]))
        self.assertEqual(outcomes[0], outcomes[1])
        self.assertEqual(outcomes[0], ("answered", "Keep the entry", False, ["apply answer"]))

    def test_a_document_id_that_is_not_one_path_segment_is_never_cleaned_up(self):
        documents = "\n".join([json.dumps({"count": 1, "nextCursor": ""}),
                               json.dumps({"id": "../config/wake", "data": {"decision": "W6-D1"}, "version": 1,
                                           "updatedAt": "2026-11-02T18:00:00Z"})])
        result = self.run_record(*self.answer_stored(documents=documents))
        self.assertIn('ignored "../config/wake": not a document ID', result.stdout)
        self.assertNotIn("delete:", result.stdout)

    def test_a_lost_or_partial_save_is_refused_rather_than_skipped(self):
        pick = self.pick("W6-D1", 1)
        whole = stored(pick)
        lost = "\n".join(line for line in whole.splitlines() if not line.startswith('{"id"'))
        for text, message in ((lost, "holds 0 documents but db_query counted 1"),
                              (whole.replace('"nextCursor": null', '"nextCursor": "next"'), "one page of several"),
                              (whole.splitlines()[2], "with its one summary line"),
                              (whole.replace(', "updatedAt": "2026-11-02T18:00:00Z"', ""), "lacks its version and save time")):
            with self.subTest(message=message), self.assertRaises(Refused) as refused:
                stored_picks(text)
            self.assertIn(message, str(refused.exception))

    def test_the_users_message_supersedes_picks_saved_before_it(self):
        need = decision(self.head(), "W6-D1")
        earlier, other = self.pick("W6-D1", 1), self.pick("W1-D2", 2)
        prompt = decision_prompt(need, self.head(), f'I choose option 2: {quoted(need["options"][1]["label"])}')
        _, record, result = self.event(*self.answer_stored(earlier, other), "--pasted", "--source", "User message 18:05",
                                       stdin=prompt)
        path = f"picks/{'W6-D1'.encode().hex()}-{earlier['revision']}"
        self.assertEqual(decision(record, "W6-D1")["answer"], "Hide expired entries", "the copied answer came later")
        self.assertEqual(decision(record, "W6-D1")["answerSource"], "User message 18:05")
        self.assertEqual(decision(record, "W6-D1")["picksRead"], [f"{path} (version 3) 2026-11-02T18:00:00Z"])
        self.assertNotIn("stalePick", decision(record, "W6-D1"))
        self.assertEqual(decision(record, "W1-D2")["answer"], "Five attempts", "other decisions' picks still apply")
        self.assertIn("note: superseded: the user's message replaces W6-D1's page pick", result.stdout)
        self.assertIn(f"note: delete: {path} (version 3)", result.stdout)
        self.assertEqual(self.commits()[0], "W6-D1 answered; W1-D2 answered from the page")

        _, record, _ = self.event("answer", "--decision", "W3-D1", "--option", "2", "--source", "msg",
                                  *self.answer_stored(self.pick("W3-D1", 1))[1:])
        self.assertEqual(decision(record, "W3-D1")["answer"], "Between test classes")

    def test_a_pick_read_again_after_a_failed_cleanup_changes_nothing(self):
        applied, displaced = self.pick("W6-D1", 1), self.pick("W6-D1", 2, digest="0123456789")
        superseded = self.pick("W1-D2", 1)
        agreeing = {"decision": "W0-D1", "revision": "0123456789", "option": 1, "label": "Keep the original job ID."}
        self.event(*self.answer_stored(applied, displaced, agreeing))
        self.event("answer", "--decision", "W6-D1", "--option", "2", "--source", "msg")
        self.event("answer", "--decision", "W0-D1", "--text", "Use a new job ID", "--source", "msg")
        self.event("answer", "--decision", "W1-D2", "--option", "2", "--source", "msg", *self.answer_stored(superseded)[1:])
        before = self.commits()
        result = self.run_record(*self.answer_stored(applied, displaced, agreeing, superseded))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commits(), before, "no pick read before becomes a reopen request")
        self.assertEqual(result.stdout.count("already read picks/"), 4)

        rewritten = stored(applied, version=1, saved="2026-11-02T19:00:00Z")
        result = self.run_record(*self.answer_stored(documents=rewritten))
        self.assertIn("reopen request: the user picked \"Keep the entry\" after W6-D1 was answered", result.stdout,
                      "a pick saved again later is a new pick")

    def test_copy_answer_still_answers_after_a_stale_pick(self):
        self.event(*self.answer_stored(self.pick("W6-D1", 2, digest="0123456789")))
        need = decision(self.head(), "W6-D1")
        prompt = decision_prompt(need, self.head(), f'I choose option 2: {quoted(need["options"][1]["label"])}')
        _, record, _ = self.event("answer", "--pasted", "--source", "User message 18:05", stdin=prompt)
        self.assertEqual(decision(record, "W6-D1")["answer"], "Hide expired entries")
        self.assertNotIn("stalePick", decision(record, "W6-D1"))


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
        self.run_record("status")
        self.publish()
        self.assertEqual(self.turn_end().returncode, 0)

        self.serve(threads=live | {"thread:W3": {"status": "idle", "updatedAt": "2026-11-02T16:00:00Z"}})
        result = self.turn_end()
        self.assertEqual(result.returncode, 1)
        self.assertIn("idle owner: W3: Support worker is idle with no recorded wait", result.stdout)
        self.assertIn("unrecorded: the owner state of W3 moved since status recorded it", result.stdout)

        self.event("wait", "--on", "Fixture repair", "--event", "Owner reports", "--work", "W3")
        self.publish()  # the page shows the wait
        result = self.turn_end()
        self.assertEqual(result.returncode, 1, "the page still shows W3 running")
        self.assertNotIn("idle owner", result.stdout)
        self.run_record("status")
        self.publish()
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


class LifecycleMutationTests(RecordCase):
    def test_init_creates_git_repo_and_initial_commit(self):
        fresh = self.program.folder.parent / "fresh-program" / "program.json"
        env = {**GIT_ENV, "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}", "T3CODE_CLI_PATH": str(self.bin / "t3"),
               "RECORD_FIXTURES": str(self.fixtures)}
        result = subprocess.run([
            sys.executable, str(SCRIPT), "init", "--state", str(fresh),
            "--title", "Payments", "--goal", "Ship retries", "--chief", SESSION.format("chief"),
            "--request", "Ship retries cleanly", "--request-source", "User msg 1", "--next", "Add outcomes",
        ], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((fresh.parent / "reports").is_dir())
        state = json.loads(fresh.read_text())
        committed_state = json.loads(subprocess.run(
            ["git", "-C", str(fresh.parent), "show", "HEAD:program.json"],
            capture_output=True, text=True, check=True,
        ).stdout)
        self.assertEqual(state, committed_state)
        self.assertEqual((state["title"], state["next"], state["work"], state["decisions"]),
                         ("Payments", "Add outcomes", [], []))
        self.assertEqual(state["request"], {"text": "Ship retries cleanly", "sources": ["User msg 1"]})
        again = subprocess.run([
            sys.executable, str(SCRIPT), "init", "--state", str(fresh),
            "--title", "Payments", "--goal", "Ship retries", "--chief", SESSION.format("chief"),
            "--request", "Ship retries cleanly",
        ], capture_output=True, text=True, env=env)
        self.assertEqual(again.returncode, 1)
        self.assertIn("already exists", again.stderr)

        # Failed commit during init leaves neither file nor staged index entry.
        broken = self.program.folder.parent / "broken-init" / "program.json"
        broken.parent.mkdir()
        subprocess.run(["git", "-C", str(broken.parent), "init", "-q"], check=True, env=env)
        hook = broken.parent / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        failed = subprocess.run([
            sys.executable, str(SCRIPT), "init", "--state", str(broken),
            "--title", "Broken", "--goal", "Fail commit", "--chief", SESSION.format("chief"),
            "--request", "Fail commit",
        ], capture_output=True, text=True, env=env)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(broken.exists())
        staged = subprocess.run(["git", "-C", str(broken.parent), "ls-files"],
                                capture_output=True, text=True, check=True, env=env).stdout.strip()
        self.assertEqual(staged, "")

    def test_grant_updates_grant_landing_authority_and_hosting(self):
        _, after, _ = self.event(
            "grant", "--source", "User msg 2", "--start", "All program outcomes",
            "--resolve", "Settled reversible choices", "--user", "Merges and scope",
            "--heartbeat", "10m task T1", "--wake", "Webhook task T2",
            "--landing", "Scoped PRs once green", "--hosting", "https://claude.ai/artifacts/abc",
        )
        self.assertEqual(after["grant"]["start"], "All program outcomes")
        self.assertEqual(after["grant"]["heartbeat"], "10m task T1")
        self.assertEqual(after["grant"]["wake"], "Webhook task T2")
        self.assertEqual(after["landingAuthority"]["text"], "Scoped PRs once green")
        self.assertEqual(after["hosting"], "https://claude.ai/artifacts/abc")

        _, after, _ = self.event("grant", "--heartbeat", "20m task T1")
        self.assertEqual(after["grant"]["heartbeat"], "20m task T1")
        self.assertEqual(after["grant"]["start"], "All program outcomes")
        self.refused("grant", "--landing", "Need source", message="needs --source")
        self.refused("grant", "--start", "Widen without source", message="needs --source")
        self.refused("grant", "--resolve", "Widen without source", message="needs --source")
        self.refused("grant", "--next", "line1\u2028line2", "--heartbeat", "10m", message="one short line")
        self.refused("grant", message="at least one field")

    def test_work_add_and_update(self):
        _, after, _ = self.event(
            "work", "--id", "W9", "--add", "--title", "Add webhook", "--repo", "acme/app",
            "--finish-line", "land", "--finish-line-reason", "Settled and reversible",
            "--description", "Emit signed webhooks", "--scope", "src/webhooks/**",
            "--blocked-by", "W1", "--source", "Issue #9", "--optional",
        )
        row = work(after, "W9")
        self.assertEqual((row["state"], row["finishLine"], row["required"], row["blockedBy"]),
                         ("planned", "land", False, ["W1"]))
        self.refused("work", "--id", "W9", "--add", "--title", "Dup", "--repo", "acme/app", message="already exists")

        _, after, _ = self.event("work", "--id", "W9", "--required", "--clear-blocked-by",
                                 "--provisional-basis", "Waiting on W1", "--provisional-clears", "W1 lands",
                                 "--provisional-on", "W1")
        row = work(after, "W9")
        self.assertNotIn("required", row)
        self.assertNotIn("blockedBy", row)
        self.assertEqual(row["provisional"]["on"], ["W1"])
        self.refused("work", "--id", "W9", message="at least one field")

    def test_work_scrap_and_rebase_answer_decision_atomically(self):
        # W2 stacks on W1-L2 and is provisional on W1; scrap W1, then resolve W2's dead-base decision atomically.
        self.commit(lambda s: (
            work(s, "W1").update(state="scrapped"),
            work(s, "W1").pop("blocked", None),
            s["decisions"].append({
                "id": "W2-D9", "question": "W1 was scrapped. Scrap or rebase W2?",
                "date": "2026-11-02T17:10:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Rebase onto main", "effect": "Drop W1 layer", "recommended": True, "reversible": True},
                    {"label": "Scrap W2", "effect": "Close W2", "reversible": False},
                ],
                "blocks": [{"id": "W2", "phase": "proof"}],
            }),
        ))
        _, after, _ = self.event(
            "work", "--id", "W2", "--rebase-onto", "main",
            "--decision", "W2-D9", "--option", "1", "--answer-source", "User msg 10",
        )
        w2 = work(after, "W2")
        self.assertEqual(w2["layers"][0]["base"], "main")
        self.assertNotIn("stackedOn", w2["layers"][0])
        self.assertNotIn("provisional", w2)
        self.assertEqual(decision(after, "W2-D9")["status"], "answered")

    def test_work_scrap_clears_blockers_and_answers_decision(self):
        self.commit(lambda s: decision(s, "W6-D1").update(
            question="Keep or scrap W6?",
            options=[
                {"label": "Rebase W6 onto main", "effect": "Keep W6", "recommended": True, "reversible": True},
                {"label": "Scrap W6", "effect": "Close W6", "reversible": False},
            ],
        ))
        # Opposing option choice is refused.
        self.refused(
            "work", "--id", "W6", "--scrap",
            "--decision", "W6-D1", "--option", "1", "--answer-source", "User msg 11",
            message="not unambiguously authorized",
        )
        # Unrelated decision is refused.
        self.refused(
            "work", "--id", "W1", "--scrap",
            "--decision", "W6-D1", "--option", "2", "--answer-source", "User msg 11",
            message="does not block W1",
        )
        _, after, _ = self.event(
            "work", "--id", "W6", "--scrap",
            "--decision", "W6-D1", "--option", "2", "--answer-source", "User msg 11",
        )
        self.assertEqual(work(after, "W6")["state"], "scrapped")
        self.assertNotIn("blocked", work(after, "W6"))
        self.assertEqual(decision(after, "W6-D1")["status"], "answered")

    def test_work_rebase_demotes_readiness_refreshes_provisional_and_handles_inbox_picks(self):
        # 1. Rebasing a ready row invalidates stale readiness.
        self.commit(ready)
        self.refused("work", "--id", "W1", "--stack-on", "W2-L1", "--scope", "x", message="--stack-on requires --rebase-onto")
        _, rebased, _ = self.event("work", "--id", "W1", "--rebase-onto", "release")
        w1 = work(rebased, "W1")
        self.assertEqual(w1["state"], "in-review")
        self.assertTrue(all(layer["status"] != "ready" for layer in w1["layers"]))

        # 2. Dead-base stored pick in mixed batch leaves dead-base pick for atomic work --decision --stored.
        self.commit(lambda s: (
            work(s, "W1").update(state="scrapped"),
            work(s, "W1").pop("blocked", None),
            s["work"].append({
                "id": "W9", "title": "Alt parent", "repo": "example/exports", "kind": "outcome",
                "state": "in-review", "finishLine": "land", "checkedAt": "2026-11-02T17:00:00Z",
                "owner": {"name": "Alt owner", "start": "top-level", "route": "t3"},
                "layers": [{"id": "W9-L1", "branch": "feat/w9", "status": "open", "url": "https://github.com/example/exports/pull/99", "base": "main"}],
            }),
            s["decisions"].append({
                "id": "W2-D8", "question": "W1 was scrapped. Scrap or rebase W2?",
                "date": "2026-11-02T17:10:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Rebase onto feat/w9", "effect": "Stack W2 on W9", "recommended": True, "reversible": True},
                    {"label": "Scrap W2", "effect": "Close W2", "reversible": False},
                ],
                "blocks": [{"id": "W2", "phase": "proof"}],
            }),
        ))
        current = self.head()
        d8 = decision(current, "W2-D8")
        d6 = decision(current, "W6-D1")
        picks_file = self.program.folder.parent / "picks.jsonl"
        doc_d8 = {
            "id": f"{d8['id'].encode().hex()}-{revision(d8)}", "version": 1, "updatedAt": "2026-11-02T17:20:00Z",
            "data": {"decision": "W2-D8", "revision": revision(d8), "option": 1, "label": "Rebase onto feat/w9"},
        }
        doc_d6 = {
            "id": f"{d6['id'].encode().hex()}-{revision(d6)}", "version": 1, "updatedAt": "2026-11-02T17:20:00Z",
            "data": {"decision": "W6-D1", "revision": revision(d6), "option": 1, "label": d6["options"][0]["label"]},
        }
        picks_file.write_text("\n".join([json.dumps(doc_d8), json.dumps(doc_d6), json.dumps({"count": 2})]) + "\n")

        _, after_batch, batch_res = self.event("answer", "--stored", str(picks_file))
        self.assertEqual(decision(after_batch, "W6-D1")["status"], "answered")
        self.assertEqual(decision(after_batch, "W2-D8")["status"], "open")
        self.assertIn("atomic work transition needed for W2-D8", batch_res.stdout)

        # Now apply W2-D8 atomically via work --rebase-onto --stack-on --decision --stored; provisional text refreshes!
        _, after_rebase, rebase_res = self.event(
            "work", "--id", "W2", "--rebase-onto", "feat/w9", "--stack-on", "W9-L1",
            "--decision", "W2-D8", "--stored", str(picks_file),
        )
        w2 = work(after_rebase, "W2")
        self.assertEqual(w2["provisional"]["on"], ["W9"])
        self.assertIn("W9", w2["provisional"]["basis"])
        self.assertIn("W9", w2["provisional"]["clears"])
        self.assertNotIn("W1", w2["provisional"]["clears"])
        self.assertEqual(decision(after_rebase, "W2-D8")["status"], "answered")
        self.assertIn("delete:", rebase_res.stdout)

    def test_reopen_bumps_revision_rejecting_prior_opening_picks(self):
        d6 = decision(self.head(), "W6-D1")
        old_rev = revision(d6)
        _, _, _ = self.event("answer", "--decision", "W6-D1", "--option", "1", "--source", "User msg 1")
        _, reopened, _ = self.event("reopen", "--decision", "W6-D1", "--why", "Reconsider")
        new_d6 = decision(reopened, "W6-D1")
        self.assertEqual(new_d6["reopened"], 1)
        self.assertNotEqual(old_rev, revision(new_d6))
        stale_prompt = f'Decision "W6-D1" (revision {old_rev}): I choose option 1: {quoted(d6["options"][0]["label"])}\n'
        self.refused("answer", "--pasted", "--source", "Old copy", stdin=stale_prompt, message="ask again")

    def test_reopen_and_withdraw_preserve_history(self):
        resolved = next(row for row in self.state["decisions"] if row["status"] == "resolved")
        _, after, result = self.event("reopen", "--decision", resolved["id"], "--why", "User wants to revisit",
                                      "--block", "W1:landing")
        row = decision(after, resolved["id"])
        self.assertEqual(row["status"], "open")
        self.assertNotIn("basis", row)
        self.assertNotIn("answer", row)
        self.assertNotIn("applied", row)
        self.assertIn(resolved["answer"], row["rationale"])
        self.assertIn("reopened: User wants to revisit", row["rationale"])
        self.assertEqual(row["blocks"], [{"id": "W1", "phase": "landing"}])
        self.assertIn("move it to --to cancelling first", result.stdout)
        self.refused("reopen", "--decision", resolved["id"], "--why", "Again", message="only a resolved or answered decision")

        _, after, _ = self.event("withdraw", "--decision", resolved["id"], "--why", "Superseded by W9")
        row = decision(after, resolved["id"])
        self.assertEqual(row["status"], "withdrawn")
        self.assertIn("withdrawn: Superseded by W9", row["rationale"])
        self.refused("withdraw", "--decision", resolved["id"], "--why", "Again", message="already withdrawn")

    def test_move_transfers_chief_and_live_owner_routes_without_publish_prompt(self):
        new_chief = SESSION.format("new-chief")
        _, after, result = self.event("move", "--chief", new_chief)
        self.assertEqual(after["chief"], new_chief)
        for row in after["work"]:
            if row["state"] not in {"landed", "done", "scrapped"} and "owner" in row:
                self.assertEqual(row["owner"]["route"], "`t3_thread_send` to the coordinator")
        self.assertIn("do not publish from this thread", result.stdout)
        self.assertNotIn("Publish ", result.stdout)

    def test_move_refuses_pending_landing_release(self):
        self.commit(ready)
        _, _, _ = self.event("land", "--work", "W1")
        self.refused("move", "--chief", SESSION.format("new-chief"), message="pending landing")

    def test_pass2_edge_cases_closed_layer_precedence_targets_and_provisional_draft(self):
        # 1. Empty --next and trailing newline are rejected at CLI boundary; staged deletion blocks init.
        self.refused("grant", "--heartbeat", "10m", "--next", "", message="one short line")
        self.refused("grant", "--heartbeat", "10m", "--next", "hello\n", message="one short line")
        deleted_repo = self.program.folder.parent / "staged-del" / "program.json"
        deleted_repo.parent.mkdir()
        env = {**GIT_ENV, "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}", "T3CODE_CLI_PATH": str(self.bin / "t3"),
               "RECORD_FIXTURES": str(self.fixtures)}
        subprocess.run([
            sys.executable, str(SCRIPT), "init", "--state", str(deleted_repo),
            "--title", "Keep", "--goal", "Keep", "--chief", SESSION.format("chief"), "--request", "Keep",
        ], capture_output=True, text=True, check=True, env=env)
        subprocess.run(["git", "-C", str(deleted_repo.parent), "rm", "-q", "program.json"], check=True, env=env)
        reinit = subprocess.run([
            sys.executable, str(SCRIPT), "init", "--state", str(deleted_repo),
            "--title", "Overwrite", "--goal", "No", "--chief", SESSION.format("chief"), "--request", "No",
        ], capture_output=True, text=True, env=env)
        self.assertEqual(reinit.returncode, 1)
        self.assertIn("HEAD", reinit.stderr)

        # 2. Individually closed parent layer W1-L2 (while W1-L1 stays open) holds atomic pick without breaking W6 batch;
        #    ambiguous/wrong-target options are refused; newer chat answer supersedes older stored scrap pick.
        self.commit(lambda s: (
            work(s, "W1")["layers"][1].update(status="closed"),
            s["decisions"].append({
                "id": "W2-D7", "question": "W1-L2 closed. Scrap or rebase W2?",
                "date": "2026-11-02T17:10:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Rebase W2 onto main instead of scrapping it", "effect": "Rebase", "recommended": True, "reversible": True},
                    {"label": "Scrap W2", "effect": "Close W2", "reversible": False},
                ],
                "blocks": [{"id": "W2", "phase": "proof"}],
            }),
        ))
        cur = self.head()
        d7 = decision(cur, "W2-D7")
        d6 = decision(cur, "W6-D1")
        picks_file = self.program.folder.parent / "mixed-closed.jsonl"
        picks_file.write_text("\n".join([
            json.dumps({"id": f"{d7['id'].encode().hex()}-{revision(d7)}", "version": 1, "updatedAt": "2026-11-02T17:20:00Z",
                        "data": {"decision": "W2-D7", "revision": revision(d7), "option": 2, "label": "Scrap W2"}}),
            json.dumps({"id": f"{d6['id'].encode().hex()}-{revision(d6)}", "version": 1, "updatedAt": "2026-11-02T17:20:00Z",
                        "data": {"decision": "W6-D1", "revision": revision(d6), "option": 1, "label": d6["options"][0]["label"]}}),
            json.dumps({"count": 2}),
        ]) + "\n")
        _, after_batch, res_batch = self.event("answer", "--stored", str(picks_file))
        self.assertEqual(decision(after_batch, "W6-D1")["status"], "answered")
        self.assertEqual(decision(after_batch, "W2-D7")["status"], "open")
        self.assertIn("atomic work transition needed for W2-D7", res_batch.stdout)

        # Opposing negated label ("instead of scrapping") refused for --scrap; wrong target refused for --rebase-onto.
        self.refused("work", "--id", "W2", "--scrap", "--decision", "W2-D7", "--option", "1",
                     "--answer-source", "User", message="not unambiguously authorized")
        self.refused("work", "--id", "W2", "--rebase-onto", "release", "--decision", "W2-D7", "--option", "1",
                     "--answer-source", "User", message="does not match target")

        # Newer chat rebase answer supersedes older stored scrap pick in the same atomic commit!
        _, after_super, res_super = self.event(
            "work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D7", "--option", "1",
            "--answer-source", "User chat override", "--stored", str(picks_file),
        )
        self.assertEqual(decision(after_super, "W2-D7")["answer"], "Rebase W2 onto main instead of scrapping it")
        self.assertIn("superseded", res_super.stdout)
        self.assertNotIn("stalePick", decision(after_super, "W2-D7"))

        # 3. Requested provisional pr-draft can mark state=ready and stop cleanly without landing.
        self.commit(lambda s: (
            work(s, "W2").update(
                finishLine="pr-draft",
                state="ready",
                provisional={"basis": "Waiting on W1", "clears": "W1 lands", "on": ["W1"]},
                layers=[dict(work(s, "W2")["layers"][0], status="draft", url="https://github.com/example/exports/pull/22")],
            ),
        ))
        found_draft = assess(self.head(), "2026-11-02T18:00:00Z", {})
        self.assertFalse(any(e["id"] == "W2" and e["kind"] in {"idle owner", "release"} for e in found_draft["runnable"]))

        # 4. Copied reopen prompt validates settled revision.
        resolved = next(r for r in self.head()["decisions"] if r["status"] == "resolved")
        good_reopen = decision_prompt(resolved, self.head(), "Reopen this decision.")
        bad_reopen = good_reopen.replace(revision(resolved), "0000000000")
        self.refused("answer", "--pasted", "--source", "Copy", stdin=bad_reopen, message="stale reopen prompt")
        self.refused("answer", "--pasted", "--source", "Copy", stdin=good_reopen, message="verified reopen request")

        # 5. Followup impact escalation reopens a previously routed discovery.
        rep = self.program.folder / "reports" / "W1.md"
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text("```json\n" + json.dumps({
            "outcome": "W1", "state": "in-review",
            "followups": [{"id": "W1-F9", "text": "Timeout differs", "impact": "unrelated"}],
        }) + "\n```\n")
        self.event("report", "--work", "W1")
        self.event("discovery", "--id", "W1-F9", "--route", "Snip #1")
        rep.write_text("```json\n" + json.dumps({
            "outcome": "W1", "state": "in-review",
            "followups": [{"id": "W1-F9", "text": "Timeout differs", "impact": "shared-contract", "thread": "PRRT_1"}],
        }) + "\n```\n")
        _, esc, esc_res = self.event("report", "--work", "W1")
        f9 = next(r for r in esc["discoveries"] if r.get("id") == "W1-F9")
        self.assertEqual((f9["status"], f9["impact"], f9["thread"], f9["reply"]), ("open", "shared-contract", "PRRT_1", "pending"))
        self.assertIn("reopened", esc_res.stdout)

    def test_pass3_typed_actions_coexisting_holds_cross_repo_closed_layer_and_reply_handoff(self):
        # 1. P3-01: Formatted backtick targets, case-sensitive branch names, close-PR phrasing, and typed option actions.
        self.commit(lambda s: (
            work(s, "W1")["layers"][1].update(status="closed"),
            s["decisions"].append({
                "id": "W2-D6", "question": "W1-L2 closed. How should W2 proceed?",
                "date": "2026-11-02T17:10:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Rebase W2 onto `release`", "effect": "Rebase", "recommended": True, "reversible": True},
                    {"label": "Rebase W2 onto Release", "effect": "Case test", "reversible": True},
                    {"label": "Close the obsolete W2 pull request and continue the work", "effect": "Continue", "reversible": True},
                    {"label": "Drop branch cleanly", "effect": "Typed scrap", "reversible": False,
                     "action": {"type": "scrap", "work": "W2"}},
                    {"label": "Move onto main", "effect": "Typed rebase", "reversible": True,
                     "action": {"type": "rebase", "work": "W2", "onto": "main"}},
                ],
                "blocks": [{"id": "W2", "phase": "proof"}],
            }),
            # Coexisting unrelated access hold on W2 (P3-02).
            s["decisions"].append({
                "id": "W2-D5", "question": "Sign in to staging?",
                "date": "2026-11-02T17:11:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Done — access is ready", "effect": "Unblock access", "recommended": True, "reversible": True},
                    {"label": "Defer this outcome", "effect": "Wait", "reversible": True},
                ],
                "blocks": [{"id": "W2", "phase": "access"}],
            }),
        ))
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D6", "--option", "1",
                     "--answer-source", "User", message="does not match target")
        self.refused("work", "--id", "W2", "--rebase-onto", "release", "--decision", "W2-D6", "--option", "2",
                     "--answer-source", "User", message="does not match target")
        self.refused("work", "--id", "W2", "--scrap", "--decision", "W2-D6", "--option", "3",
                     "--answer-source", "User", message="not unambiguously authorized")
        # Typed action rejects wrong target and wrong transition type.
        self.refused("work", "--id", "W2", "--rebase-onto", "release", "--decision", "W2-D6", "--option", "5",
                     "--answer-source", "User", message="does not match typed option target")
        self.refused("work", "--id", "W2", "--scrap", "--decision", "W2-D6", "--option", "5",
                     "--answer-source", "User", message="conflicts with typed option action")

        # 2. P3-02: With two halting decisions on W2, unrelated access hold settles normally while base-repair pick defers!
        cur = self.head()
        d5, d6 = decision(cur, "W2-D5"), decision(cur, "W2-D6")
        picks = self.program.folder.parent / "coexist.jsonl"
        picks.write_text("\n".join([
            json.dumps({"id": f"{d5['id'].encode().hex()}-{revision(d5)}", "version": 1, "updatedAt": "2026-11-02T17:20:00Z",
                        "data": {"decision": "W2-D5", "revision": revision(d5), "option": 1, "label": "Done — access is ready"}}),
            json.dumps({"id": f"{d6['id'].encode().hex()}-{revision(d6)}", "version": 1, "updatedAt": "2026-11-02T17:20:00Z",
                        "data": {"decision": "W2-D6", "revision": revision(d6), "option": 5, "label": "Move onto main"}}),
            json.dumps({"count": 2}),
        ]) + "\n")
        _, after_co, co_res = self.event("answer", "--stored", str(picks))
        self.assertEqual(decision(after_co, "W2-D5")["status"], "answered")
        self.assertEqual(decision(after_co, "W2-D6")["status"], "open")
        self.assertIn("atomic work transition needed for W2-D6", co_res.stdout)

        # 3. P3-03: Same-command --repo change cannot create a cross-repo stack edge.
        self.refused("work", "--id", "W2", "--repo", "other/repo", "--rebase-onto", "feat/exports-schema",
                     "--stack-on", "W1-L1", "--decision", "W2-D6", "--option", "5", "--answer-source", "User",
                     message="cannot stack W2 (other/repo)")

        # 4. P3-04: Rebase off closed W1-L2 onto live sibling W1-L1 with coexisting W3 refreshes stale W1-L2 text!
        self.commit(lambda s: (
            work(s, "W2").update(provisional={
                "basis": "Staged on W1-L2; also needs W3",
                "clears": "W1-L2 merges and W3 lands",
                "on": ["W1", "W3"],
            }),
            decision(s, "W2-D6")["options"].append({
                "label": "Restack on W1-L1", "effect": "Use live sibling", "reversible": True,
                "action": {"type": "rebase", "work": "W2", "onto": work(s, "W1")["layers"][0]["branch"], "stackOn": "W1-L1"},
            }),
        ))
        w1_l1_branch = work(self.head(), "W1")["layers"][0]["branch"]
        _, after_sib, _ = self.event(
            "work", "--id", "W2", "--rebase-onto", w1_l1_branch, "--stack-on", "W1-L1",
            "--decision", "W2-D6", "--option", "6", "--answer-source", "User msg",
        )
        w2_prov = work(after_sib, "W2")["provisional"]
        self.assertNotIn("W1-L2", w2_prov["basis"])
        self.assertNotIn("W1-L2", w2_prov["clears"])
        self.assertEqual(sorted(w2_prov["on"]), ["W1", "W3"])

        # 5. P3-06: Attaching a GitHub thread to an already-routed discovery makes reply handoff runnable until --reply-sent.
        rep = self.program.folder / "reports" / "W1.md"
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text("```json\n" + json.dumps({
            "outcome": "W1", "state": "in-review",
            "followups": [{"id": "W1-F10", "text": "Pre-existing lint debt", "impact": "unrelated"}],
        }) + "\n```\n")
        self.event("report", "--work", "W1")
        self.event("discovery", "--id", "W1-F10", "--route", "Snip #77")
        rep.write_text("```json\n" + json.dumps({
            "outcome": "W1", "state": "in-review",
            "followups": [{"id": "W1-F10", "text": "Pre-existing lint debt", "impact": "unrelated", "thread": "PRRT_77"}],
        }) + "\n```\n")
        _, with_thread, thread_res = self.event("report", "--work", "W1")
        self.assertIn("--reply-sent", thread_res.stdout)
        self.assertNotIn("--route ...", thread_res.stdout)
        found_reply = assess(with_thread, "2026-11-02T18:00:00Z", {})
        self.assertTrue(any(e["kind"] == "send deferred reply" and e["id"] == "W1-F10" for e in found_reply["runnable"]))
        _, sent, _ = self.event("discovery", "--id", "W1-F10", "--reply-sent")
        found_done = assess(sent, "2026-11-02T18:05:00Z", {})
        self.assertFalse(any(e["kind"] == "send deferred reply" and e["id"] == "W1-F10" for e in found_done["runnable"]))

    def test_pass4_shared_atomic_guard_text_binding_merged_sibling_cancelling_and_escalated_reply(self):
        # 1. P4-01 & P4-02: Direct answer, resolve, and transition-free work --decision all enforce atomic guard;
        #    --text resolves typed option and quoted legacy ref parses full target.
        self.commit(lambda s: (
            work(s, "W1")["layers"][1].update(status="closed"),
            s["decisions"].append({
                "id": "W2-D4", "question": "W1-L2 closed. How should W2 proceed?",
                "date": "2026-11-02T17:10:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Rebase W2", "effect": "Rebase onto release", "recommended": True, "reversible": True,
                     "action": {"type": "rebase", "work": "W2", "onto": "release"}},
                    {"label": "Rebase W2 onto `release+hotfix`", "effect": "Plus target", "reversible": True},
                    {"label": "Scrap W2", "effect": "Drop W2", "reversible": False,
                     "action": {"type": "scrap", "work": "W2"}},
                ],
                "blocks": [{"id": "W2", "phase": "proof"}],
            }),
            s["decisions"].append({
                "id": "W2-D3", "question": "Access ready?",
                "date": "2026-11-02T17:11:00Z", "source": "Coordinator", "status": "open",
                "options": [
                    {"label": "Done — access is ready", "effect": "Unblock", "recommended": True, "reversible": True},
                    {"label": "Defer", "effect": "Wait", "reversible": True},
                ],
                "blocks": [{"id": "W2", "phase": "access"}],
            }),
        ))
        self.refused("answer", "--decision", "W2-D4", "--option", "1", "--source", "User", message="atomic work transition needed")
        self.refused("resolve", "--decision", "W2-D4", "--option", "1", "--basis", "Policy", message="atomic work transition needed")
        self.refused("work", "--id", "W2", "--decision", "W2-D4", "--option", "1", "--answer-source", "User",
                     message="pass --scrap or --rebase-onto")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D4", "--text", "Rebase W2",
                     "--answer-source", "User", message="does not match typed option target")
        self.refused("work", "--id", "W2", "--rebase-onto", "release", "--decision", "W2-D4", "--option", "2",
                     "--answer-source", "User", message="release+hotfix")
        # Unrelated access decision still settles independently!
        _, after_acc, _ = self.event("answer", "--decision", "W2-D3", "--option", "1", "--source", "User")
        self.assertEqual(decision(after_acc, "W2-D3")["status"], "answered")

        # 2. P4-03: Rebasing W2 off closed W1-L2 onto merged W1-L1 clears stale W1 from provisional.on!
        self.commit(lambda s: (
            work(s, "W1")["layers"][0].update(status="merged"),
            decision(s, "W2-D4")["options"].append({
                "label": "Rebase onto merged W1-L1", "effect": "Use merged anchor", "reversible": True,
                "action": {"type": "rebase", "work": "W2", "onto": work(s, "W1")["layers"][0]["branch"], "stackOn": "W1-L1"},
            }),
        ))
        w1_l1_branch = work(self.head(), "W1")["layers"][0]["branch"]
        _, after_merged, _ = self.event(
            "work", "--id", "W2", "--rebase-onto", w1_l1_branch, "--stack-on", "W1-L1",
            "--decision", "W2-D4", "--option", "4", "--answer-source", "User",
        )
        self.assertNotIn("provisional", work(after_merged, "W2"))

        # 3. P4-04 & P5-01 & P5-02: Cancelling is monotonic, checks forge before withdrawn, and handles late merge with open hold.
        self.commit(ready)
        _, rel, _ = self.event("land", "--work", "W1")
        lid = rel["landings"][-1]["id"]
        w1_prs = {layer["url"]: {"state": "OPEN", "isDraft": False, "headRefOid": layer["head"], "baseRefName": layer["base"],
                                 "autoMergeRequest": None, "isInMergeQueue": False}
                  for layer in work(rel, "W1")["layers"]}
        self.event("land", "--landing", lid, "--to", "cancelling", "--note", "Cancelling before takeover")
        self.refused("land", "--landing", lid, "--to", "submitted", message="is cancelling")
        self.refused("move", "--chief", SESSION.format("new-chief"), message="pending landing")
        # Incomplete auto-merge/queue facts block finalizing withdrawn!
        incomplete = {url: {"state": "OPEN", "isDraft": False, "headRefOid": info["headRefOid"], "baseRefName": info["baseRefName"]}
                      for url, info in w1_prs.items()}
        self.serve(prs=incomplete)
        self.refused("land", "--landing", lid, "--to", "withdrawn", "--note", "Try incomplete",
                     message="missing definite auto-merge or merge-queue facts")
        # Armed auto-merge or merge-queue blocks finalizing withdrawn!
        armed = {url: {**info, "autoMergeRequest": {"enabledAt": "2026-11-02T17:30:00Z"}} for url, info in w1_prs.items()}
        self.serve(prs=armed)
        self.refused("land", "--landing", lid, "--to", "withdrawn", "--note", "Try early", message="auto-merge")
        queued = {url: {**info, "isInMergeQueue": True} for url, info in w1_prs.items()}
        self.serve(prs=queued)
        self.refused("land", "--landing", lid, "--to", "withdrawn", "--note", "Try queued", message="merge-queue")
        # Confirmed stopped on forge allows withdrawn and move!
        self.serve(prs=w1_prs)
        self.event("land", "--landing", lid, "--to", "withdrawn", "--note", "Forge cancellation confirmed")
        self.event("move", "--chief", SESSION.format("new-chief"))

        # Late merge while an open decision blocks W1 still reconciles cleanly and keeps decision open!
        _, rel2, _ = self.event("land", "--work", "W1")
        lid2 = rel2["landings"][-1]["id"]
        rel2["decisions"].append({
            "id": "W1-D9", "question": "Follow up on retry header?",
            "date": "2026-11-02T17:40:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Add header", "effect": "New PR", "recommended": True, "reversible": True},
                {"label": "Skip header", "effect": "Done", "reversible": True},
            ],
            "blocks": [{"id": "W1", "phase": "landing"}],
        })
        self.program.write(rel2, "2026-11-02T17:40:00Z")
        self.event("land", "--landing", lid2, "--to", "cancelling", "--note", "New hold opened")
        merged_prs = {url: {**info, "state": "MERGED"} for url, info in w1_prs.items()}
        self.serve(prs=merged_prs)
        self.refused("land", "--landing", lid2, "--to", "withdrawn", "--note", "Try withdraw merged", message="already merged")
        _, landed_late, late_res = self.event("land", "--landing", lid2, "--to", "landed", "--note", "Merged before cancel")
        self.assertEqual(work(landed_late, "W1")["state"], "landed")
        self.assertEqual(decision(landed_late, "W1-D9")["status"], "open")
        self.assertNotIn("blocks", decision(landed_late, "W1-D9"))
        self.assertIn("already merged while W1-D9 stayed open", late_res.stdout)

        # 4. P5-03: Duplicate option labels refused via --text; quoted article-like branch name enforced exactly.
        cur4 = self.head()
        cur4["decisions"].append({
            "id": "W2-D8", "question": "Pick target?",
            "date": "2026-11-02T17:45:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Rebase W2", "effect": "Release", "recommended": True, "reversible": True,
                 "action": {"type": "rebase", "work": "W2", "onto": "release"}},
                {"label": "Rebase W2", "effect": "Staging", "reversible": True,
                 "action": {"type": "rebase", "work": "W2", "onto": "staging"}},
                {"label": "Rebase W2 onto `new`", "effect": "Branch named new", "reversible": True},
            ],
            "blocks": [{"id": "W2", "phase": "proof"}],
        })
        self.program.write(cur4, "2026-11-02T17:45:00Z")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--text", "Rebase W2",
                     "--answer-source", "User", message="multiple options match")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--text", "rebase W2",
                     "--answer-source", "User", message="multiple options match")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--text", "Rebase W2.",
                     "--answer-source", "User", message="multiple options match")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--text", "Please rebase W2",
                     "--answer-source", "User", message="must name the target branch")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--text", "Please rebase W2 onto a new base",
                     "--answer-source", "User", message="ambiguous or conditional")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--text", "Please rebase W2 onto Main",
                     "--answer-source", "User", message="does not match target")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D8", "--option", "3",
                     "--answer-source", "User", message="does not match target 'new'")

        # 5. P4-05: Escalating an already-acknowledged discovery with a held thread resets reply to pending on report!
        rep = self.program.folder / "reports" / "W2.md"
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text("```json\n" + json.dumps({
            "outcome": "W2", "state": "building",
            "followups": [{"id": "W2-F11", "text": "Timeout bug", "impact": "unrelated", "thread": "PRRT_11"}],
        }) + "\n```\n")
        self.event("report", "--work", "W2")
        self.event("discovery", "--id", "W2-F11", "--route", "Snip #11", "--reply-sent")
        rep.write_text("```json\n" + json.dumps({
            "outcome": "W2", "state": "building",
            "followups": [{"id": "W2-F11", "text": "Timeout bug", "impact": "shared-contract", "thread": "PRRT_11"}],
        }) + "\n```\n")
        _, reopened_rep, _ = self.event("report", "--work", "W2")
        self.assertEqual(next(r for r in reopened_rep["discoveries"] if r.get("id") == "W2-F11")["reply"], "pending")
        _, rerouted, reroute_res = self.event("discovery", "--id", "W2-F11", "--route", "W4")
        f11 = next(r for r in rerouted["discoveries"] if r.get("id") == "W2-F11")
        self.assertEqual(f11["reply"], "pending")
        self.assertIn("--reply-sent", reroute_res.stdout)
        found_esc = assess(rerouted, "2026-11-02T18:10:00Z", {})
        self.assertTrue(any(e["kind"] == "send deferred reply" and e["id"] == "W2-F11" for e in found_esc["runnable"]))

    def test_report_followups_trigger_runnable_until_routed_by_discovery(self):
        report_file = self.program.folder / "reports" / "W1.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(
            "```json\n"
            + json.dumps({
                "outcome": "W1",
                "state": "in-review",
                "followups": [
                    {
                        "id": "W1-F1",
                        "text": "Shared retry helper also swallows timeout errors in W2",
                        "evidence": "retry.py:42",
                        "impact": "shared-contract",
                    }
                ],
            })
            + "\n```\n\nDeferred out-of-scope finding.\n"
        )
        _, after, result = self.event("report", "--work", "W1")
        self.assertIn("followups W1-F1", result.stdout)
        entries = [row for row in after.get("discoveries", []) if row.get("id") == "W1-F1"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["status"], "open")
        self.assertEqual(entries[0]["route"], "pending")
        self.assertEqual(entries[0]["impact"], "shared-contract")

        found = assess(after, "2026-11-02T18:00:00Z", {})
        self.assertEqual(found["verdict"], "runnable")
        self.assertTrue(any(entry["kind"] == "route discovery" and entry["id"] == "W1-F1"
                            for entry in found["runnable"]))

        # Re-reporting the same followup ID is idempotent.
        _, after_repeat, repeat_res = self.event("report", "--work", "W1")
        self.assertIn("already recorded", repeat_res.stdout)
        self.assertEqual(len([row for row in after_repeat.get("discoveries", []) if row.get("id") == "W1-F1"]), 1)

        # Routing the discovery resolves the runnable trigger.
        self.refused("discovery", "--id", "W1-F1", "--route", "pending", message="concrete destination")
        _, routed, _ = self.event("discovery", "--id", "W1-F1", "--route", "Sent to W2 owner")
        entry = next(row for row in routed["discoveries"] if row.get("id") == "W1-F1")
        self.assertEqual(entry["status"], "routed")
        self.assertEqual(entry["route"], "Sent to W2 owner")
        found_after = assess(routed, "2026-11-02T18:05:00Z", {})
        self.assertFalse(any(entry["kind"] == "route discovery" and entry["id"] == "W1-F1"
                             for entry in found_after["runnable"]))
        self.refused("discovery", "--id", "W1-F1", "--route", "Again", message="already routed")

        # Conflicting followup ID from another owner is refused.
        w2_report = self.program.folder / "reports" / "W2.md"
        w2_report.write_text(
            "```json\n"
            + json.dumps({
                "outcome": "W2", "state": "in-review",
                "followups": [{"id": "W1-F1", "text": "Different finding colliding on ID"}],
            })
            + "\n```\n"
        )
        self.refused("report", "--work", "W2", message="already belongs to another discovery")

        # Coordinator can add an open discovery without --id; it gets an auto-allocated routable ID.
        _, opened, _ = self.event("discovery", "--add", "--origin", "PR #10 review",
                                  "--text", "Needs routing later", "--impact", "unrelated")
        auto_d = next(row for row in opened["discoveries"] if row["text"] == "Needs routing later")
        self.assertTrue(auto_d["id"].startswith("D"))
        self.assertEqual(auto_d["status"], "open")
        _, routed_auto, _ = self.event("discovery", "--id", auto_d["id"], "--route", "Snip #43")
        self.assertEqual(next(row for row in routed_auto["discoveries"] if row.get("id") == auto_d["id"])["status"], "routed")

        # Coordinator can also add an already-routed discovery directly.
        _, added, _ = self.event("discovery", "--add", "--id", "D99", "--origin", "PR #10 review",
                                 "--text", "Clean up unused flag", "--impact", "unrelated",
                                 "--route", "Snip #42")
        d99 = next(row for row in added["discoveries"] if row.get("id") == "D99")
        self.assertEqual(d99["status"], "routed")
        self.assertEqual(d99["route"], "Snip #42")

    def test_pass6_graphql_pr_reader_partial_merge_cancel_status_reconcile_and_free_text(self):
        # 1. P6-01: gh_pr uses gh api graphql for standard GitHub & GHE PR URLs and returns definite queue/auto-merge facts.
        gh_url = "https://github.com/org/repo/pull/42"
        ghe_url = "https://ghe.example.com/org/repo/pull/7"
        self.serve(prs={
            gh_url: {"state": "OPEN", "isDraft": False, "headRefOid": "a" * 40, "baseRefName": "main",
                     "autoMergeRequest": None, "isInMergeQueue": False},
            ghe_url: {"state": "OPEN", "isDraft": False, "headRefOid": "b" * 40, "baseRefName": "main",
                      "autoMergeRequest": None, "isInMergeQueue": True},
        })
        old_path, old_fix = os.environ.get("PATH"), os.environ.get("RECORD_FIXTURES")
        try:
            os.environ["PATH"] = f"{self.bin}{os.pathsep}{old_path or ''}"
            os.environ["RECORD_FIXTURES"] = str(self.fixtures)
            pr_gh = gh_pr(gh_url)
            self.assertEqual(pr_gh["state"], "OPEN")
            self.assertIs(pr_gh["isInMergeQueue"], False)
            self.assertIsNone(pr_gh["autoMergeRequest"])
            pr_ghe = gh_pr(ghe_url)
            self.assertIs(pr_ghe["isInMergeQueue"], True)
        finally:
            if old_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = old_path
            if old_fix is None:
                os.environ.pop("RECORD_FIXTURES", None)
            else:
                os.environ["RECORD_FIXTURES"] = old_fix

        # 2. P6-02 & P6-04: Partially merged release reconciles cleanly during cancelling -> withdrawn,
        #    unblocking move and requiring a fresh release for the stopped remainder.
        def two_ready(state):
            ready(state)
            work(state, "W1")["layers"][0]["url"] = "https://github.com/org/exports/pull/101"
            work(state, "W1")["layers"][1]["url"] = "https://github.com/org/exports/pull/102"
            row = work(state, "W4")
            row.update(state="ready", finishLine="land", owner=copy.deepcopy(work(state, "W1")["owner"]),
                       layers=[{"id": "W4-L1", "branch": "progress", "status": "ready",
                                "url": "https://github.com/org/exports/pull/103",
                                "head": "abc1234", "base": "main"}])
        self.commit(two_ready)
        _, rel, _ = self.event("land", "--work", "W1", "--work", "W4", "--lander", "Retry owner")
        lid = rel["landings"][-1]["id"]
        # P6-04: submitted -> withdrawn is also refused without cancelling first!
        self.event("land", "--landing", lid, "--to", "submitted")
        self.refused("land", "--landing", lid, "--to", "withdrawn", "--note", "Skip fence",
                     message="move it to --to cancelling first")
        # Open a hold on W1 before partial merge cancellation.
        cur = self.head()
        cur["decisions"].append({
            "id": "W1-D10", "question": "Post-merge follow-up?",
            "date": "2026-11-02T18:00:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Follow up", "effect": "New PR", "recommended": True, "reversible": True},
                {"label": "Skip", "effect": "None", "reversible": True},
            ],
            "blocks": [{"id": "W1", "phase": "landing"}, {"id": "W2", "phase": "proof"}],
        })
        self.program.write(cur, "2026-11-02T18:00:00Z")
        self.event("land", "--landing", lid, "--to", "cancelling", "--note", "Cancel after hold")
        # W1's two PRs merged; W4's PR stopped cleanly!
        w1_layers = work(self.head(), "W1")["layers"]
        self.serve(prs={
            w1_layers[0]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_layers[0]["head"], "baseRefName": w1_layers[0]["base"],
                                  "autoMergeRequest": None, "isInMergeQueue": False},
            w1_layers[1]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_layers[1]["head"], "baseRefName": w1_layers[1]["base"],
                                  "autoMergeRequest": None, "isInMergeQueue": False},
            "https://github.com/org/exports/pull/103": {"state": "OPEN", "isDraft": False, "headRefOid": "abc1234", "baseRefName": "main",
                                                        "autoMergeRequest": None, "isInMergeQueue": False},
        })
        _, partial_after, partial_res = self.event("land", "--landing", lid, "--to", "withdrawn", "--note", "W1 merged, W4 stopped")
        self.assertEqual(partial_after["landings"][-1]["state"], "withdrawn")
        self.assertEqual(work(partial_after, "W1")["state"], "landed")
        self.assertEqual(work(partial_after, "W4")["state"], "ready")
        self.assertEqual(decision(partial_after, "W1-D10")["status"], "open")
        self.assertEqual(decision(partial_after, "W1-D10")["blocks"], [{"id": "W2", "phase": "proof"}])
        self.assertIn("partially merged before cancellation", partial_res.stdout)
        # Move now succeeds, and W4 can get a fresh release!
        self.event("move", "--chief", SESSION.format("chief-2"))
        _, rel_w4, _ = self.event("land", "--work", "W4")
        lid_w4 = rel_w4["landings"][-1]["id"]

        # 3. P6-03: Ordinary status running FIRST when a cancelling release merges with an open hold
        #    atomically lands W4, lands the release, detaches W4 from the open decision, and keeps other blocks!
        cur2 = self.head()
        cur2["decisions"].append({
            "id": "W4-D1", "question": "Metrics tag?",
            "date": "2026-11-02T18:05:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Add tag", "effect": "New PR", "recommended": True, "reversible": True},
                {"label": "Leave", "effect": "Done", "reversible": True},
            ],
            "blocks": [{"id": "W4", "phase": "landing"}, {"id": "W2", "phase": "proof"}],
        })
        self.program.write(cur2, "2026-11-02T18:05:00Z")
        self.event("land", "--landing", lid_w4, "--to", "cancelling", "--note", "Hold before merge")
        self.serve(prs={
            "https://github.com/org/exports/pull/103": {"state": "MERGED", "isDraft": False, "headRefOid": "abc1234", "baseRefName": "main",
                                                        "autoMergeRequest": None, "isInMergeQueue": False},
        })
        _, status_after, status_res = self.event("status")
        self.assertEqual(work(status_after, "W4")["state"], "landed")
        self.assertEqual(status_after["landings"][-1]["state"], "landed")
        self.assertEqual(decision(status_after, "W4-D1")["status"], "open")
        self.assertEqual(decision(status_after, "W4-D1")["blocks"], [{"id": "W2", "phase": "proof"}])
        self.assertIn("W4 already merged while W4-D1 stayed open", status_res.stdout)
        self.assertNotIn("settle by hand", status_res.stdout)

        # 4. P6-05: Normalized single typed option binds its target; free-text rebase with explicit exact target succeeds.
        cur3 = self.head()
        cur3["decisions"].append({
            "id": "W2-D9", "question": "Rebase W2?",
            "date": "2026-11-02T18:10:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Rebase W2", "effect": "Onto release", "recommended": True, "reversible": True,
                 "action": {"type": "rebase", "work": "W2", "onto": "release"}},
                {"label": "Scrap W2", "effect": "Drop", "reversible": False,
                 "action": {"type": "scrap", "work": "W2"}},
            ],
            "blocks": [{"id": "W2", "phase": "proof"}],
        })
        self.program.write(cur3, "2026-11-02T18:10:00Z")
        # Normalized case/punctuation variant binds to the single typed option and refuses wrong target!
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D9", "--text", "rebase W2.",
                     "--answer-source", "User", message="does not match typed option target 'release'")
        # Explicit free-text rebase naming the exact destination succeeds!
        _, free_after, _ = self.event("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D9",
                                      "--text", "Please rebase W2 onto main", "--answer-source", "User")
        self.assertEqual(decision(free_after, "W2-D9")["status"], "answered")

    def test_pass7_status_reconcile_fallback_hostname_retargeted_withdraw_and_ambiguous_target(self):
        # 1. P7-01: Reconciling a cancelling landing in status while an unrelated held outcome falls back
        #    must not crash with KeyError and must persist both cleanly in one batch.
        def two_held_outcomes(state):
            ready(state)
            work(state, "W1")["layers"][0]["url"] = "https://github.com/org/exports/pull/201"
            work(state, "W1")["layers"][1]["url"] = "https://github.com/org/exports/pull/202"
            w4 = work(state, "W4")
            w4.update(state="ready", finishLine="land", owner=copy.deepcopy(work(state, "W1")["owner"]),
                      layers=[{"id": "W4-L1", "branch": "progress", "status": "ready",
                               "url": "https://github.com/org/exports/pull/203", "head": "abc1234", "base": "main"}])
        self.commit(two_held_outcomes)
        _, rel, _ = self.event("land", "--work", "W1")
        lid = rel["landings"][-1]["id"]
        cur = self.head()
        cur["decisions"].extend([
            {
                "id": "W1-D11", "question": "Hold on W1?", "date": "2026-11-02T18:20:00Z", "source": "Coordinator", "status": "open",
                "options": [{"label": "Keep", "effect": "New PR", "recommended": True, "reversible": True},
                            {"label": "Skip", "effect": "None", "reversible": True}],
                "blocks": [{"id": "W1", "phase": "landing"}],
            },
            {
                "id": "W4-D11", "question": "Unrelated hold on W4?", "date": "2026-11-02T18:21:00Z", "source": "Coordinator", "status": "open",
                "options": [{"label": "Keep", "effect": "New PR", "recommended": True, "reversible": True},
                            {"label": "Skip", "effect": "None", "reversible": True}],
                "blocks": [{"id": "W4", "phase": "landing"}],
            },
        ])
        self.program.write(cur, "2026-11-02T18:21:00Z")
        self.event("land", "--landing", lid, "--to", "cancelling", "--note", "Hold on W1")
        w1_layers = work(self.head(), "W1")["layers"]
        self.serve(prs={
            w1_layers[0]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_layers[0]["head"], "baseRefName": w1_layers[0]["base"],
                                  "autoMergeRequest": None, "isInMergeQueue": False},
            w1_layers[1]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_layers[1]["head"], "baseRefName": w1_layers[1]["base"],
                                  "autoMergeRequest": None, "isInMergeQueue": False},
            "https://github.com/org/exports/pull/203": {"state": "MERGED", "isDraft": False, "headRefOid": "abc1234", "baseRefName": "main",
                                                        "autoMergeRequest": None, "isInMergeQueue": False},
        })
        _, batch_after, batch_res = self.event("status")
        self.assertEqual(work(batch_after, "W1")["state"], "landed")
        self.assertEqual(batch_after["landings"][-1]["state"], "landed")
        self.assertEqual(decision(batch_after, "W1-D11")["status"], "open")
        self.assertNotIn("blocks", decision(batch_after, "W1-D11"))
        self.assertEqual(work(batch_after, "W4")["state"], "ready")
        self.assertIn("W4: recorded its forge facts from the forge; settle by hand", batch_res.stdout)

        # 2. P7-02: Public github.com URL always passes --hostname github.com even when GH_HOST is overridden.
        old_path, old_fix, old_host = os.environ.get("PATH"), os.environ.get("RECORD_FIXTURES"), os.environ.get("GH_HOST")
        self.serve(prs={
            "https://github.com/org/repo/pull/99": {
                "state": "OPEN", "isDraft": False, "headRefOid": "c" * 40, "baseRefName": "main",
                "autoMergeRequest": None, "isInMergeQueue": False,
            },
        })
        try:
            os.environ["PATH"] = f"{self.bin}{os.pathsep}{old_path or ''}"
            os.environ["RECORD_FIXTURES"] = str(self.fixtures)
            os.environ["GH_HOST"] = "example.invalid"
            pr = gh_pr("https://github.com/org/repo/pull/99")
            self.assertEqual(pr["headRefOid"], "c" * 40)
        finally:
            for key, val in (("PATH", old_path), ("RECORD_FIXTURES", old_fix), ("GH_HOST", old_host)):
                if val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = val

        # 3. P7-03 & empty autoMergeRequest: Partial withdrawal with a retargeted stopped PR whose new base
        #    matches another tracked layer (C-L1) still withdraws, lands merged work, lapses stopped readiness,
        #    and unblocks move and rebase!
        def retarget_setup(state):
            ready(state)
            work(state, "W1")["layers"][0]["url"] = "https://github.com/org/exports/pull/301"
            work(state, "W1")["layers"][1]["url"] = "https://github.com/org/exports/pull/302"
            w4 = work(state, "W4")
            w4.update(state="ready", finishLine="land", owner=copy.deepcopy(work(state, "W1")["owner"]),
                      layers=[{"id": "W4-L1", "branch": "progress", "status": "ready",
                               "url": "https://github.com/org/exports/pull/303", "head": "abc1234", "base": "main"}])
            w6 = work(state, "W6")
            w6.update(state="in-review", finishLine="land",
                      layers=[{"id": "W6-L1", "branch": "tracked-c", "status": "open",
                               "url": "https://github.com/org/exports/pull/304", "head": "def5678", "base": "main"}])
        self.commit(retarget_setup)
        _, rel_ret, _ = self.event("land", "--work", "W1", "--work", "W4", "--lander", "Retry owner")
        lid_ret = rel_ret["landings"][-1]["id"]
        self.event("land", "--landing", lid_ret, "--to", "cancelling", "--note", "W4 retargeted")
        w1_l = work(self.head(), "W1")["layers"]
        # Empty dict autoMergeRequest ({}) is non-None and must be refused as armed!
        self.serve(prs={
            w1_l[0]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_l[0]["head"], "baseRefName": w1_l[0]["base"],
                             "autoMergeRequest": None, "isInMergeQueue": False},
            w1_l[1]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_l[1]["head"], "baseRefName": w1_l[1]["base"],
                             "autoMergeRequest": None, "isInMergeQueue": False},
            "https://github.com/org/exports/pull/303": {"state": "OPEN", "isDraft": False, "headRefOid": "abc1234", "baseRefName": "tracked-c",
                                                        "autoMergeRequest": {}, "isInMergeQueue": False},
        })
        self.refused("land", "--landing", lid_ret, "--to", "withdrawn", "--note", "Try empty autoMergeRequest", message="auto-merge")
        self.serve(prs={
            w1_l[0]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_l[0]["head"], "baseRefName": w1_l[0]["base"],
                             "autoMergeRequest": None, "isInMergeQueue": False},
            w1_l[1]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_l[1]["head"], "baseRefName": w1_l[1]["base"],
                             "autoMergeRequest": None, "isInMergeQueue": False},
            "https://github.com/org/exports/pull/303": {"state": "OPEN", "isDraft": False, "headRefOid": "abc1234", "baseRefName": "tracked-c",
                                                        "autoMergeRequest": None, "isInMergeQueue": False},
        })
        _, ret_after, ret_res = self.event("land", "--landing", lid_ret, "--to", "withdrawn", "--note", "W1 merged, W4 stopped after retarget")
        self.assertEqual(ret_after["landings"][-1]["state"], "withdrawn")
        self.assertEqual(work(ret_after, "W1")["state"], "landed")
        self.assertEqual(work(ret_after, "W4")["state"], "in-review")
        self.assertEqual(work(ret_after, "W4")["layers"][0]["status"], "open")
        self.assertIn("settle by hand", ret_res.stdout)
        self.refused("land", "--work", "W4", message="not ready to land")
        self.event("move", "--chief", SESSION.format("chief-3"))
        self.event("work", "--id", "W4", "--rebase-onto", "tracked-c", "--stack-on", "W6-L1")

        # 4. P7-05: All-stopped withdrawal with a closed PR at a new head invalidates readiness and blocks stale re-release.
        self.commit(lambda s: (
            work(s, "W4").update(state="ready", finishLine="land",
                                 layers=[{"id": "W4-L1", "branch": "progress", "status": "ready",
                                          "url": "https://github.com/org/exports/pull/303", "head": "abc1234", "base": "main"}]),
        ))
        _, rel_stop, _ = self.event("land", "--work", "W4")
        lid_stop = rel_stop["landings"][-1]["id"]
        self.event("land", "--landing", lid_stop, "--to", "cancelling", "--note", "PR closed")
        self.serve(prs={
            "https://github.com/org/exports/pull/303": {"state": "CLOSED", "isDraft": False, "headRefOid": "9999999" + "0" * 33, "baseRefName": "main",
                                                        "autoMergeRequest": None, "isInMergeQueue": False},
        })
        _, stop_after, _ = self.event("land", "--landing", lid_stop, "--to", "withdrawn", "--note", "Closed without merge")
        self.assertEqual(stop_after["landings"][-1]["state"], "withdrawn")
        self.assertEqual(work(stop_after, "W4")["state"], "in-review")
        self.assertEqual(work(stop_after, "W4")["layers"][0]["status"], "closed")
        self.refused("land", "--work", "W4", message="not ready to land")

        # 5. P7-04: Ambiguous free-text destinations and normalized-colliding option labels are refused.
        cur4 = self.head()
        cur4["decisions"].append({
            "id": "W2-D10", "question": "Rebase W2 where?", "date": "2026-11-02T18:30:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Rebase W2", "effect": "Onto release", "recommended": True, "reversible": True,
                 "action": {"type": "rebase", "work": "W2", "onto": "release"}},
                {"label": "rebase W2.", "effect": "Onto staging", "reversible": True,
                 "action": {"type": "rebase", "work": "W2", "onto": "staging"}},
            ],
            "blocks": [{"id": "W2", "phase": "proof"}],
        })
        self.program.write(cur4, "2026-11-02T18:30:00Z")
        self.refused("work", "--id", "W2", "--rebase-onto", "release", "--decision", "W2-D10", "--text", "Rebase W2",
                     "--answer-source", "User", message="multiple options match")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D10",
                     "--text", "Please rebase W2 onto main or release", "--answer-source", "User", message="ambiguous or conditional destination")
        self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D10",
                     "--text", "Rebase W2 onto main then rebase onto release", "--answer-source", "User", message="multiple destinations")

    def test_pass8_fail_closed_free_text_status_terminal_guards_and_blocked_late_merge(self):
        # 1. P8-01: Fail-closed unbound free-text rebase refuses lists, slash-alternatives, conditionals, and questions,
        #    preserving HEAD unchanged on refusal while accepting unconditional single-target answers.
        cur = self.head()
        cur["decisions"].append({
            "id": "W2-D11", "question": "Rebase W2 where?", "date": "2026-11-02T18:40:00Z", "source": "Coordinator", "status": "open",
            "options": [
                {"label": "Rebase W2", "effect": "Onto release", "recommended": True, "reversible": True,
                 "action": {"type": "rebase", "work": "W2", "onto": "release"}},
                {"label": "Scrap W2", "effect": "Drop", "reversible": False,
                 "action": {"type": "scrap", "work": "W2"}},
            ],
            "blocks": [{"id": "W2", "phase": "proof"}],
        })
        self.program.write(cur, "2026-11-02T18:40:00Z")
        before_head = subprocess.check_output(["git", "-C", str(self.program.folder), "rev-parse", "HEAD"], text=True).strip()
        for phrase in (
            "Please rebase W2 onto main, release, or staging",
            "Please rebase W2 onto main /release",
            "Please rebase W2 onto main, release",
            "Rebase W2 onto main if tests pass",
            "If CI is red, rebase W2 onto main",
            "Could we rebase W2 onto main?",
            "Rebase W2 onto main?",
        ):
            self.refused("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D11",
                         "--text", phrase, "--answer-source", "User", message="ambiguous or conditional")
            self.assertEqual(subprocess.check_output(["git", "-C", str(self.program.folder), "rev-parse", "HEAD"], text=True).strip(), before_head)
        _, ok_after, _ = self.event("work", "--id", "W2", "--rebase-onto", "main", "--decision", "W2-D11",
                                    "--text", "Please rebase W2 onto `main`, please.", "--answer-source", "User")
        self.assertEqual(decision(ok_after, "W2-D11")["status"], "answered")

        # 2. P8-02: Generic --status scrapped and --status landed are refused so terminal changes cannot bypass
        #    the pending-landing fence or forge merge verification.
        def ready_w4(state):
            ready(state)
            work(state, "W1")["layers"][0]["url"] = "https://github.com/org/exports/pull/401"
            work(state, "W1")["layers"][1]["url"] = "https://github.com/org/exports/pull/402"
            w4 = work(state, "W4")
            w4.update(state="ready", finishLine="land", owner=copy.deepcopy(work(state, "W1")["owner"]),
                      layers=[{"id": "W4-L1", "branch": "progress", "status": "ready",
                               "url": "https://github.com/org/exports/pull/403", "head": "abc1234", "base": "main"}])
        self.commit(ready_w4)
        _, rel, _ = self.event("land", "--work", "W1", "--work", "W4", "--lander", "Retry owner")
        lid = rel["landings"][-1]["id"]
        before_scrap = subprocess.check_output(["git", "-C", str(self.program.folder), "rev-parse", "HEAD"], text=True).strip()
        self.refused("work", "--id", "W4", "--status", "scrapped", message="use --scrap")
        self.refused("work", "--id", "W4", "--status", "landed", message="not --status landed")
        self.refused("work", "--id", "W4", "--scrap", message="pending landing")
        self.assertEqual(subprocess.check_output(["git", "-C", str(self.program.folder), "rev-parse", "HEAD"], text=True).strip(), before_scrap)

        # 3. P8-03: Partial withdrawal where fully merged work carries a direct --blocked or --blocked-by blocker
        #    still lands the merged work, moves the obsolete blocker into a durable runnable open discovery,
        #    and terminalizes the withdrawal cleanly.
        self.event("work", "--id", "W1", "--blocked", "Waiting on external security sign-off")
        self.event("land", "--landing", lid, "--to", "cancelling", "--note", "External blocker raised")
        w1_l = work(self.head(), "W1")["layers"]
        self.serve(prs={
            w1_l[0]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_l[0]["head"], "baseRefName": w1_l[0]["base"],
                             "autoMergeRequest": None, "isInMergeQueue": False},
            w1_l[1]["url"]: {"state": "MERGED", "isDraft": False, "headRefOid": w1_l[1]["head"], "baseRefName": w1_l[1]["base"],
                             "autoMergeRequest": None, "isInMergeQueue": False},
            "https://github.com/org/exports/pull/403": {"state": "OPEN", "isDraft": False, "headRefOid": "abc1234", "baseRefName": "main",
                                                        "autoMergeRequest": None, "isInMergeQueue": False},
        })
        _, after_w, res_w = self.event("land", "--landing", lid, "--to", "withdrawn", "--note", "W1 merged while blocked; W4 stopped")
        self.assertEqual(after_w["landings"][-1]["state"], "withdrawn")
        self.assertEqual(work(after_w, "W1")["state"], "landed")
        self.assertNotIn("blocked", work(after_w, "W1"))
        self.assertIn("moved blocker to open discovery", res_w.stdout)
        late_disc = next(d for d in after_w.get("discoveries", []) if d.get("work") == "W1" and d.get("status") == "open")
        self.assertIn("Waiting on external security sign-off", late_disc["text"])
        found = assess(after_w, "2026-11-02T18:45:00Z", {})
        self.assertEqual(found["verdict"], "runnable")
        self.assertTrue(any(e["kind"] == "route discovery" and e["id"] == late_disc["id"] for e in found["runnable"]))


if __name__ == "__main__":
    unittest.main()
