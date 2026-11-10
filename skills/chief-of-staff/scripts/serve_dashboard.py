#!/usr/bin/env python3
"""Serve the command center on loopback, rendering the program state file on each request."""

import argparse
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
from urllib.parse import urlsplit

from render_dashboard import TEMPLATE, render, with_error


ERROR_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta http-equiv="refresh" content="20">
<title>Command center unavailable</title></head>
<body style="font: 15px/1.5 system-ui, sans-serif; margin: 2rem 16px; max-inline-size: 62ch">
<h1 style="font-size: 1.4rem">Command center unavailable</h1>
<p>The program file failed to load, and there is no earlier good state to show. This page retries every 20 seconds.</p>
<p><code>{error}</code></p>
</body></html>
"""


class DashboardServer(ThreadingHTTPServer):
    def __init__(self, state_path):
        self.state_path = Path(state_path)
        self.last_good = None
        self.last_error = None
        self.page_template = TEMPLATE.read_text()  # Read once, so the page always matches the code this process loaded.
        self.lock = threading.Lock()  # One request at a time, so an older read never replaces a newer page.
        super().__init__(("127.0.0.1", 0), DashboardHandler)  # The OS picks an unused port.
        self.page()

    def page(self):
        """Return (status, html) for the current file, falling back to the last page that rendered."""
        with self.lock:
            try:
                page = render(json.loads(self.state_path.read_text()), self.page_template)
            except Exception as error:  # Any failure to read or render keeps the last good page up.
                message = f"{type(error).__name__}: {error}" if not isinstance(error, ValueError) else str(error)
                if message != self.last_error:
                    print(f"{self.state_path}: {message}", file=sys.stderr, flush=True)
                    self.last_error = message
                if self.last_good is None:
                    return HTTPStatus.SERVICE_UNAVAILABLE, ERROR_PAGE.format(error=escape(message))
                return HTTPStatus.OK, with_error(self.last_good, message)
            self.last_good, self.last_error = page, None
            return HTTPStatus.OK, page


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        status, page = self.server.page()
        self.reply(status, page.encode())

    def reply(self, status, body, content_type="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path, help="The program state file, such as program.json")
    args = parser.parse_args()
    server = DashboardServer(args.state.resolve())
    print(f"http://127.0.0.1:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
