import contextlib
import copy
import http.client
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

from render_dashboard import render
from serve_dashboard import DashboardServer
from test_render_dashboard import page_state


SCRIPT = Path(__file__).with_name("serve_dashboard.py")
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "Test",
           "GIT_AUTHOR_EMAIL": "test@example.com", "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com"}


def git(folder, *args):
    subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True, env=GIT_ENV)


def commit(folder, text):
    (folder / "program.json").write_text(text)
    git(folder, "add", "program.json")
    git(folder, "commit", "-q", "--allow-empty", "-m", "write")


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.state = page_state()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.program = self.folder / "program.json"
        git(self.folder, "init", "-q")
        self.enterContext(contextlib.redirect_stderr(io.StringIO()))

    def start(self):
        server = DashboardServer(self.folder)
        self.addCleanup(server.server_close)
        threading.Thread(target=server.serve_forever, args=(.01,), daemon=True).start()
        self.addCleanup(server.shutdown)
        self.port = server.server_port
        return server

    def write(self, state):
        commit(self.folder, json.dumps(state))

    def changed(self, title):
        state = copy.deepcopy(self.state)
        state["title"] = title
        return state

    def get(self, path="/", method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        self.addCleanup(connection.close)
        connection.request(method, path)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read().decode()

    def title(self, page):
        return re.search(r"<title>(.*)</title>", page).group(1)

    def snapshot(self, page):
        return re.search(r'data-snapshot="(\w+)"', page).group(1)

    def test_binds_only_to_loopback(self):
        self.write(self.state)
        self.assertEqual(self.start().server_address[0], "127.0.0.1")

    def test_each_request_renders_the_last_commit_and_ignores_the_working_file(self):
        self.write(self.changed("First write"))
        self.start()
        status, headers, page = self.get()
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(self.title(page), "First write")
        for edit in (json.dumps(self.changed("Uncommitted edit")), "{not json"):
            self.program.write_text(edit)
            self.assertEqual(self.get()[2], page, edit)
        self.write(self.changed("Second write"))
        self.assertEqual(self.title(self.get()[2]), "Second write")
        self.assertEqual(sorted(path.name for path in self.folder.iterdir()), [".git", "program.json"])

    def test_invalid_commit_serves_the_last_good_page_with_a_banner_until_fixed(self):
        self.write(self.changed("Good state"))
        self.start()
        good = self.get()[2]
        bad = copy.deepcopy(self.state)
        bad["work"][0]["state"] = "finished"
        for broken, reason in ((json.dumps(bad), "state must be one of"), ("{not json", "Expecting property name"), (None, "does not exist in")):
            with self.subTest(reason=reason):
                if broken is None:
                    git(self.folder, "rm", "-q", "program.json")
                    git(self.folder, "commit", "-q", "-m", "remove")
                else:
                    commit(self.folder, broken)
                status, _, page = self.get()
                self.assertEqual(status, 200)
                self.assertEqual(self.title(page), "Good state")
                self.assertIn('<p class="state-error" role="alert">', page)
                self.assertIn(reason, page)
                self.assertNotEqual(self.snapshot(page), self.snapshot(good))
        self.write(self.changed("Fixed state"))
        page = self.get()[2]
        self.assertEqual(self.title(page), "Fixed state")
        self.assertNotIn("state-error", page.split("<main>")[1])

    def test_render_failure_serves_the_last_good_page_with_a_banner_until_it_clears(self):
        self.write(self.changed("Good state"))
        self.start()
        good = self.get()[2]
        with mock.patch("serve_dashboard.render", side_effect=RuntimeError("renderer failed during hosting")):
            status, _, page = self.get()
        self.assertEqual(status, 200)
        self.assertEqual(self.title(page), "Good state")
        self.assertIn('<p class="state-error" role="alert">', page)
        self.assertIn("renderer failed during hosting", page)
        self.assertNotEqual(self.snapshot(page), self.snapshot(good))
        self.assertEqual(self.get()[2], good)

    def test_template_is_read_once_at_startup(self):
        self.write(self.state)
        self.start()
        before = self.get()[2]
        read_text = Path.read_text

        def template_changed(path, *args, **kwargs):
            text = read_text(path, *args, **kwargs)
            return text.replace("<main>", "<main>Changed template", 1) if path.name == "command-center.html" else text

        with mock.patch.object(Path, "read_text", template_changed):
            self.assertEqual(self.get()[2], before)

    def test_an_older_request_never_replaces_a_newer_page(self):
        self.write(self.changed("Older state"))
        server = self.start()
        older_rendering, resume_older, newer_waits_or_ends = threading.Event(), threading.Event(), threading.Event()
        self.addCleanup(resume_older.set)

        def render_pausing_older(state, template):
            if state["title"] == "Older state" and not older_rendering.is_set():
                older_rendering.set()
                resume_older.wait(10)
            return render(state, template)

        class SignalingLock:
            def __enter__(self):
                if not lock.acquire(blocking=False):
                    newer_waits_or_ends.set()
                    lock.acquire()

            def __exit__(self, *error):
                lock.release()

        lock, server.lock = server.lock, SignalingLock()
        pages = {}
        with mock.patch("serve_dashboard.render", render_pausing_older):
            older = threading.Thread(target=lambda: pages.update(older=server.page()))
            older.start()
            self.assertTrue(older_rendering.wait(10))
            self.write(self.changed("Newer state"))
            newer = threading.Thread(target=lambda: (pages.update(newer=server.page()), newer_waits_or_ends.set()))
            newer.start()
            self.assertTrue(newer_waits_or_ends.wait(10))
            self.assertNotIn("newer", pages, "the newer request finished while the older one was still rendering")
            resume_older.set()
            older.join(10)
            newer.join(10)
        self.assertEqual(self.title(pages["older"][1]), "Older state")
        self.assertEqual(self.title(pages["newer"][1]), "Newer state")
        commit(self.folder, "{not json")
        self.assertEqual(self.title(self.get()[2]), "Newer state")

    def test_without_a_good_state_it_serves_an_error_page(self):
        self.start()
        self.assertEqual(self.get()[0], 503, "no commit yet")
        commit(self.folder, "{not json")
        status, _, page = self.get()
        self.assertEqual(status, 503)
        self.assertIn("Command center unavailable", page)
        self.assertIn("Expecting property name", page)
        self.write(self.state)
        self.assertEqual(self.get()[0], 200)

    def test_serves_only_the_page(self):
        self.write(self.state)
        (self.folder / "secret.txt").write_text("private")
        self.start()
        for path in ("/program.json", "/secret.txt", "/index.html", "/../program.json", "//program.json", "/reports/W1.md", "/.git/HEAD"):
            with self.subTest(path=path):
                status, _, body = self.get(path)
                self.assertEqual(status, 404)
                self.assertNotIn("private", body)
                self.assertNotIn('"record"', body)
        self.assertEqual(self.get("/?tab=work")[0], 200)
        self.assertEqual(self.get(method="POST")[0], 501)

    def test_cli_prints_its_loopback_url_and_serves_the_last_commit(self):
        self.write(self.changed("From the command line"))
        process = subprocess.Popen([sys.executable, str(SCRIPT), "--program", str(self.folder)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(process.wait, 10)
        self.addCleanup(process.terminate)
        address = process.stdout.readline().strip()
        self.assertRegex(address, r"^http://127\.0\.0\.1:\d+/$")
        self.port = int(address.rsplit(":", 1)[1].rstrip("/"))
        self.assertEqual(self.title(self.get()[2]), "From the command line")


if __name__ == "__main__":
    unittest.main()
