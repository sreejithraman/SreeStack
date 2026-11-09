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

from serve_dashboard import DashboardServer
from test_render_dashboard import page_state


SCRIPT = Path(__file__).with_name("serve_dashboard.py")


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.state = page_state()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.program = self.folder / "program.json"
        self.enterContext(contextlib.redirect_stderr(io.StringIO()))

    def start(self):
        server = DashboardServer(self.program)
        self.addCleanup(server.server_close)
        threading.Thread(target=server.serve_forever, args=(.01,), daemon=True).start()
        self.addCleanup(server.shutdown)
        self.port = server.server_port
        return server

    def write(self, state):
        staging = self.folder / ".program.json.tmp"
        staging.write_text(json.dumps(state))
        os.replace(staging, self.program)

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

    def test_binds_only_to_loopback(self):
        self.write(self.state)
        self.assertEqual(self.start().server_address[0], "127.0.0.1")

    def test_each_request_renders_the_current_file(self):
        self.write(self.changed("First write"))
        self.start()
        status, headers, page = self.get()
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(self.title(page), "First write")
        self.write(self.changed("Second write"))
        self.assertEqual(self.title(self.get()[2]), "Second write")
        self.assertEqual(sorted(path.name for path in self.folder.iterdir()), ["program.json"])

    def test_invalid_file_serves_the_last_good_page_with_a_banner_until_fixed(self):
        self.write(self.changed("Good state"))
        self.start()
        good = self.get()[2]
        bad = copy.deepcopy(self.state)
        bad["work"][0]["state"] = "finished"
        for broken, reason in ((json.dumps(bad), "state must be one of"), ("{not json", "Expecting property name"), (None, "FileNotFoundError")):
            with self.subTest(reason=reason):
                if broken is None:
                    self.program.unlink()
                else:
                    self.program.write_text(broken)
                status, _, page = self.get()
                self.assertEqual(status, 200)
                self.assertEqual(self.title(page), "Good state")
                self.assertIn('<p class="state-error" role="alert">', page)
                self.assertIn(reason, page)
                self.assertNotEqual(re.search(r'data-snapshot="(\w+)"', page).group(1), re.search(r'data-snapshot="(\w+)"', good).group(1))
        self.write(self.changed("Fixed state"))
        page = self.get()[2]
        self.assertEqual(self.title(page), "Fixed state")
        self.assertNotIn("state-error", page.split("<main>")[1])

    def test_without_a_good_state_it_serves_an_error_page(self):
        self.program.write_text("{not json")
        self.start()
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
        for path in ("/program.json", "/secret.txt", "/index.html", "/../program.json", "//program.json", "/reports/W1.md"):
            with self.subTest(path=path):
                status, _, body = self.get(path)
                self.assertEqual(status, 404)
                self.assertNotIn("private", body)
                self.assertNotIn('"record"', body)
        self.assertEqual(self.get("/?tab=work")[0], 200)
        self.assertEqual(self.get(method="POST")[0], 501)

    def test_cli_prints_its_loopback_url_and_serves_the_file(self):
        self.write(self.changed("From the command line"))
        process = subprocess.Popen([sys.executable, str(SCRIPT), "--state", str(self.program)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(process.wait, 10)
        self.addCleanup(process.terminate)
        address = process.stdout.readline().strip()
        self.assertRegex(address, r"^http://127\.0\.0\.1:\d+/$")
        self.port = int(address.rsplit(":", 1)[1].rstrip("/"))
        self.assertEqual(self.title(self.get()[2]), "From the command line")


if __name__ == "__main__":
    unittest.main()
