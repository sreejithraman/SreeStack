"""Publish committed pages to static output and navigate them in real Chrome."""

from datetime import datetime, timedelta, timezone
import functools
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from urllib.parse import urlsplit

import test_command_center as center
from test_render_dashboard import Program, example


PREPARE = Path(__file__).with_name("prepare_sites.py")


class PublishedFiles(center.FreshPage):
    requests = []
    responses = {}

    def do_GET(self):
        path = urlsplit(self.path).path
        self.requests.append((path, self.headers))
        response = self.responses.get(path)
        if callable(response):
            response = response(self)
        if response:
            status, content_type, body, headers = response
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # An aborted hidden-page or timed-out request closes its socket.
        else:
            super().do_GET()


def setUpModule():
    center.setUpModule()
    center.server.RequestHandlerClass = functools.partial(PublishedFiles, directory=center.site.name)


def tearDownModule():
    center.tearDownModule()


class SitesRefreshTests(center.CommandCenterCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(dir=center.site.name)
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        (self.folder / "program").mkdir()
        self.program = Program(self.folder / "program")
        self.publications = 0
        self.state = example()
        self.page_file = self.folder / "dist/index.html"
        self.page_url = f"http://127.0.0.1:{center.server.server_port}/{self.folder.name}/dist/"
        self.publish(self.state)

    def publish(self, state):
        self.publications += 1
        stamp = datetime(2026, 11, 10, tzinfo=timezone.utc) + timedelta(seconds=self.publications)
        self.program.write(state, stamp.isoformat())
        marker = self.program.folder / "command-center.html"
        rendered = self.program.run("--page", str(marker))
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        page = marker.with_name("command-center.next.html")
        result = subprocess.run([sys.executable, str(PREPARE), "--page", str(page),
                                 "--output", str(self.page_file.parent)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def wait_until(self, condition, timeout=5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if condition():
                return
            time.sleep(.05)
        self.fail("Published content did not reach the open page before the deadline")

    def requests_for(self, name):
        path = urlsplit(self.page_url).path + name
        return [headers for requested, headers in PublishedFiles.requests if requested == path]

    def documents(self):
        return [headers for headers in self.requests_for("") if headers.get("Sec-Fetch-Dest") == "document"]

    def respond(self, name, status=200, content_type="application/json", body=b"{}", headers=None):
        path = urlsplit(self.page_url).path + name
        PublishedFiles.responses[path] = (status, content_type, body, headers or {})
        self.addCleanup(PublishedFiles.responses.pop, path, None)

    def focus(self, page):
        page.run("dispatchEvent(new Event('focus'))")

    def assert_unchanged(self, page):
        self.assertEqual(len(self.documents()), 1)
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertNotIn("Automatically published program", page.text())
        self.assertEqual(page.run("pageErrors"), [])

    def test_visible_page_picks_up_publication_and_restores_its_view(self):
        page = self.open_page(center.PHONE)
        page.click("#work-tab")
        page.click(center.EVIDENCE)
        page.click("#toggle-stage-planned")
        page.bring_into_view(self.card("W1"), 100)
        before = page.top_of(self.card("W1"))
        started = time.monotonic()
        self.publish(self.retitled("Automatically published program"))
        self.wait_until(lambda: "Automatically published program" in page.text(), timeout=32)
        self.assertLess(time.monotonic() - started, 30)
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertTrue(page.run(f"document.querySelector('{center.EVIDENCE}').parentElement.open"))
        self.assertFalse(page.run("document.querySelector('.collapsible.planned details').open"))
        self.assertAlmostEqual(page.top_of(self.card("W1")), before, delta=1)
        self.assertEqual(len(self.documents()), 2, "The browser must really navigate over HTTP")
        self.assertEqual(page.run("pageErrors"), [])

    def test_focus_keeps_unchanged_page_then_updates_selected_decision(self):
        page = self.open_page()
        selected = page.run("document.querySelectorAll('.inbox-row')[3].getAttribute('aria-controls')")
        page.click(f'.inbox-row[aria-controls="{selected}"]')
        page.run("window.visitMarker = 'same document'")
        self.focus(page)
        time.sleep(.2)
        self.assertEqual(page.run("window.visitMarker"), "same document")
        self.assertEqual(len(self.documents()), 1)
        self.publish(self.retitled("Automatically published program"))
        self.focus(page)
        self.wait_until(lambda: "Automatically published program" in page.text())
        self.assertEqual(page.selected_decision(), selected)
        self.assertEqual(len(self.documents()), 2)

    def test_hidden_page_stops_requests_and_updates_immediately_on_return(self):
        page = self.open_page()
        page.click("#work-tab")
        page.set_visible(False)
        time.sleep(.2)
        before = len(self.requests_for("chief-version.json"))
        self.publish(self.retitled("Automatically published program"))
        time.sleep(21)
        self.assertEqual(len(self.requests_for("chief-version.json")), before)
        self.focus(page)
        time.sleep(.2)
        self.assertEqual(len(self.requests_for("chief-version.json")), before)
        self.assert_unchanged(page)
        page.set_visible(True)
        self.focus(page)
        self.wait_until(lambda: "Automatically published program" in page.text())
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertEqual(len(self.documents()), 2)

    def test_failed_checks_and_login_responses_leave_page_available_then_recover(self):
        page = self.open_page()
        page.click("#work-tab")
        self.publish(self.retitled("Automatically published program"))
        version = (self.page_file.parent / "chief-version.json").read_bytes()
        for status, content_type, body, headers in (
            (503, "application/json", version, {}),
            (401, "application/json", version, {}),
            (200, "text/html", b"<html>Sign in</html>", {}),
            (200, "application/json", b"not json", {}),
            (200, "application/json", b"null", {}),
            (200, "application/json", b'{"version":"https://evil.invalid/"}', {}),
            (302, "text/html", b"", {"Location": "/signin-with-chatgpt"}),
            (302, "text/html", b"", {"Location": "https://example.invalid/login"}),
        ):
            with self.subTest(status=status, body=body, headers=headers):
                self.respond("chief-version.json", status, content_type, body, headers)
                before = len(self.requests_for("chief-version.json"))
                self.focus(page)
                self.wait_until(lambda: len(self.requests_for("chief-version.json")) > before)
                time.sleep(.1)
                self.assert_unchanged(page)
        PublishedFiles.responses.pop(urlsplit(self.page_url).path + "chief-version.json")
        for status, body, headers in (
            (401, b"Sign in", {}), (200, b"<html>Sign in</html>", {}),
            (302, b"", {"Location": "/signin-with-chatgpt"}),
        ):
            with self.subTest(page_status=status):
                self.respond("", status, "text/html", body, headers)
                before = len(self.requests_for(""))
                self.focus(page)
                self.wait_until(lambda: len(self.requests_for("")) > before)
                time.sleep(.1)
                self.assert_unchanged(page)
        PublishedFiles.responses.pop(urlsplit(self.page_url).path)
        self.focus(page)
        self.wait_until(lambda: "Automatically published program" in page.text())
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertFalse(any(path == "/signin-with-chatgpt" for path, _ in PublishedFiles.requests))

    def test_mismatched_cached_html_waits_for_matching_publication(self):
        page = self.open_page()
        page.click("#work-tab")
        stale = self.page_file.read_bytes()
        self.publish(self.retitled("Automatically published program"))
        self.respond("", content_type="text/html", body=stale)
        self.focus(page)
        time.sleep(.3)
        self.assert_unchanged(page)
        PublishedFiles.responses.pop(urlsplit(self.page_url).path)
        self.focus(page)
        self.wait_until(lambda: "Automatically published program" in page.text())
        self.assertEqual(page.selected_tab(), "work-tab")

    def test_stale_navigation_response_does_not_reload_in_a_loop(self):
        page = self.open_page()
        page.click("#work-tab")
        stale = self.page_file.read_bytes()
        self.publish(self.retitled("Automatically published program"))
        fresh = self.page_file.read_bytes()
        path = urlsplit(self.page_url).path
        PublishedFiles.responses[path] = lambda request: (
            200, "text/html", stale if request.headers.get("Sec-Fetch-Dest") == "document" else fresh, {})
        self.addCleanup(PublishedFiles.responses.pop, path, None)
        self.focus(page)
        self.wait_until(lambda: len(self.documents()) == 2)
        self.wait_until(lambda: page.run("document.readyState") == "complete")
        for _ in range(3):
            self.focus(page)
            time.sleep(.15)
        self.assertEqual(len(self.documents()), 2)
        self.assertEqual(page.selected_tab(), "work-tab")
        # A later publication can still advance beyond the failed one.
        PublishedFiles.responses.pop(path)
        self.publish(self.retitled("Next publication after stale navigation"))
        self.focus(page)
        self.wait_until(lambda: "Next publication after stale navigation" in page.text())

    def test_slow_request_is_bounded_and_overlapping_focus_does_not_duplicate_it(self):
        page = self.open_page()
        page.click("#work-tab")
        self.publish(self.retitled("Automatically published program"))
        release = threading.Event()
        self.addCleanup(release.set)
        version = (self.page_file.parent / "chief-version.json").read_bytes()
        path = urlsplit(self.page_url).path + "chief-version.json"

        def slow(request):
            release.wait(8)
            return 200, "application/json", version, {}

        PublishedFiles.responses[path] = slow
        self.addCleanup(PublishedFiles.responses.pop, path, None)
        before = len(self.requests_for("chief-version.json"))
        self.focus(page)
        self.wait_until(lambda: len(self.requests_for("chief-version.json")) > before)
        for _ in range(4):
            self.focus(page)
        time.sleep(.2)
        self.assertEqual(len(self.requests_for("chief-version.json")), before + 1)
        time.sleep(5.1)
        self.assert_unchanged(page)
        PublishedFiles.responses.pop(path)
        self.focus(page)
        self.wait_until(lambda: "Automatically published program" in page.text())
        release.set()

    def test_hiding_aborts_a_pending_check_and_return_does_not_wait_for_it(self):
        page = self.open_page()
        page.click("#work-tab")
        self.publish(self.retitled("Automatically published program"))
        release = threading.Event()
        self.addCleanup(release.set)
        version = (self.page_file.parent / "chief-version.json").read_bytes()
        path = urlsplit(self.page_url).path + "chief-version.json"
        before = len(self.requests_for("chief-version.json"))

        def first_slow(request):
            if len(self.requests_for("chief-version.json")) == before + 1:
                release.wait(8)
            return 200, "application/json", version, {}

        PublishedFiles.responses[path] = first_slow
        self.addCleanup(PublishedFiles.responses.pop, path, None)
        self.focus(page)
        self.wait_until(lambda: len(self.requests_for("chief-version.json")) > before)
        page.set_visible(False)
        page.set_visible(True)
        self.wait_until(lambda: "Automatically published program" in page.text(), timeout=3)
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertEqual(len(self.documents()), 2)
        release.set()


class PreparationTests(unittest.TestCase):
    def test_preparing_output_is_repeatable_and_leaves_record_marker_and_manifest_alone(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "program").mkdir()
            program = Program(root / "program")
            state = example()
            program.write(state, "2026-11-10T12:00:00Z")
            marker = program.folder / "command-center.html"
            self.assertEqual(program.run("--page", str(marker)).returncode, 0)
            rendered = marker.with_name("command-center.next.html")
            marker.write_text("last successful publication")
            site = root / "site"
            (site / ".openai").mkdir(parents=True)
            manifest = site / ".openai/hosting.json"
            manifest.write_text('{"project_id":"existing-private-site","static":{"directory":"dist"}}')
            originals = {path: path.read_bytes() for path in (program.source, marker, rendered, manifest)}
            command = [sys.executable, str(PREPARE), "--page", str(rendered), "--output", str(site / "dist")]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            files = {path.name: path.read_bytes() for path in (site / "dist").iterdir()}
            self.assertEqual(set(files), {"index.html", "chief-refresh.js", "chief-version.json"})
            self.assertEqual({path: path.read_bytes() for path in originals}, originals)
            again = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertEqual(first.stdout, again.stdout)
            self.assertEqual({path.name: path.read_bytes() for path in (site / "dist").iterdir()}, files)
            rendered.write_text(rendered.read_text().replace("Export reliability", "New published title"))
            changed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(changed.returncode, 0, changed.stderr)
            self.assertNotEqual(changed.stdout, first.stdout)


if __name__ == "__main__":
    unittest.main()
