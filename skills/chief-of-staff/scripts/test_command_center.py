"""Drive the hosted command center in headless Chrome.

Chrome's debugging pipe needs no client package. A clock installed before the
page's script runs its timers on demand; everything else is the real page,
browser, and network. Without a usable Chrome the tests skip locally and fail in CI.
"""

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from urllib.parse import urlsplit

from serve_dashboard import DashboardHandler, DashboardServer
from test_render_dashboard import page_state


CHECK_INTERVAL = 20_000
DESKTOP = (1280, 800)
PHONE = (390, 844)
REPLY_TIMEOUT = 20
HELD_LIMIT = 120_000
VIEW_KEY_PREFIX = "command-center-view:"

# Each launch of branded macOS Chrome copies its signed app into a code_sign_clone
# folder under /var/folders, and the copy outlives the process, so it comes last.
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PLAYWRIGHT_CHROMES = (
    "chromium-*/chrome-mac*/*.app/Contents/MacOS/*",
    "chromium-*/chrome-linux*/chrome",
    "chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
)
PAGE_HARNESS = """
(() => {
  const realSetTimeout = setTimeout.bind(window);
  const timers = new Map();
  const pending = new Set();
  let nextTimer = 1;
  let now = 0;

  const track = promise => {
    pending.add(promise);
    const forget = () => pending.delete(promise);
    promise.then(forget, forget);
    return promise;
  };
  window.setTimeout = (callback, delay = 0) => {
    timers.set(nextTimer, {callback, at: now + delay});
    return nextTimer++;
  };
  window.clearTimeout = timer => timers.delete(timer);
  performance.now = () => now;

  window.clock = {
    async settled() {
      while (pending.size) await Promise.allSettled(pending);
      await new Promise(resolve => realSetTimeout(resolve));
    },
    async advance(milliseconds, settle) {
      const end = now + milliseconds;
      for (;;) {
        const [due] = [...timers].filter(([, timer]) => timer.at <= end).sort(([, a], [, b]) => a.at - b.at);
        if (!due) break;
        const [identity, timer] = due;
        now = timer.at;
        timers.delete(identity);
        timer.callback();
        if (settle) await clock.settled();
      }
      now = end;
      if (settle) await clock.settled();
    },
  };

  window.checks = {live: [], most: 0, count: 0};
  const realFetch = fetch.bind(window);
  window.fetch = (url, options) => {
    checks.live = checks.live.filter(signal => !signal.aborted);
    checks.live.push(options.signal);
    checks.most = Math.max(checks.most, checks.live.length);
    checks.count += 1;
    const release = () => { checks.live = checks.live.filter(signal => signal !== options.signal); };
    return track(realFetch(url, options).finally(release));
  };
  const realText = Response.prototype.text;
  Response.prototype.text = function () { return track(realText.call(this)); };

  window.pageErrors = [];
  addEventListener('error', event => pageErrors.push(event.message));

  window.lucide = {createIcons() {
    for (const mark of document.querySelectorAll('i[data-lucide]')) {
      const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      icon.setAttribute('class', mark.getAttribute('class'));
      mark.replaceWith(icon);
    }
  }};
})();
"""
BLOCK_STORAGE = """
Object.defineProperty(window, 'sessionStorage', {get() { throw new DOMException('denied', 'SecurityError'); }});
"""
HIDE = """
Object.defineProperty(document, 'hidden', {configurable: true, get: () => %(hidden)s});
Object.defineProperty(document, 'visibilityState', {configurable: true, get: () => %(state)s});
document.dispatchEvent(new Event('visibilitychange'));
"""


def playwright_chromes():
    """Playwright's cached Chromium builds, Chrome for Testing first, newest first."""
    default = "~/Library/Caches" if sys.platform == "darwin" else os.environ.get("XDG_CACHE_HOME", "~/.cache")
    root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or f"{default}/ms-playwright").expanduser()
    for pattern in PLAYWRIGHT_CHROMES:
        yield from sorted(root.glob(pattern), key=lambda path: int(path.relative_to(root).parts[0].rpartition("-")[2]),
                          reverse=True)


def chrome_path():
    candidates = (*map(str, playwright_chromes()), "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", MAC_CHROME)
    return next(filter(None, map(shutil.which, candidates)), None)


class Chrome:
    """A Chrome process spoken to over --remote-debugging-pipe."""

    def __init__(self, executable, profile):
        self.next_id = 0
        self.buffer = b""
        self.events = []
        commands_read, self.commands = os.pipe()
        self.replies, replies_write = os.pipe()

        def connect_debugging_pipe():
            os.dup2(commands_read, 3)
            os.dup2(replies_write, 4)
            os.set_inheritable(3, True)
            os.set_inheritable(4, True)

        self.process = subprocess.Popen(
            [executable, "--headless=new", "--remote-debugging-pipe", "--no-sandbox", "--no-first-run",
             "--no-default-browser-check", "--disable-background-networking", f"--user-data-dir={profile}",
             "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1", "about:blank"],
            preexec_fn=connect_debugging_pipe, close_fds=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        os.close(commands_read)
        os.close(replies_write)

    def read_messages(self, timeout):
        ready, _, _ = select.select([self.replies], [], [], timeout)
        if not ready:
            return []
        chunk = os.read(self.replies, 1 << 16)
        if not chunk:
            raise ConnectionError("Chrome closed its debugging pipe")
        self.buffer += chunk
        *complete, self.buffer = self.buffer.split(b"\0")
        return [json.loads(message) for message in complete]

    def receive(self, wanted, label):
        deadline = time.monotonic() + REPLY_TIMEOUT
        while time.monotonic() < deadline:
            for index, message in enumerate(self.events):
                if wanted(message):
                    return self.events.pop(index)
            self.events.extend(self.read_messages(.05))
        raise TimeoutError(label)

    def send(self, method, session=None, **params):
        self.next_id += 1
        identity = self.next_id
        message = {"id": identity, "method": method, "params": params}
        if session:
            message["sessionId"] = session
        os.write(self.commands, json.dumps(message).encode() + b"\0")
        reply = self.receive(lambda message: message.get("id") == identity, method)
        if "error" in reply:
            raise RuntimeError(f"{method}: {reply['error']}")
        return reply["result"]

    def wait_for_event(self, method, session):
        return self.receive(lambda message: message.get("method") == method and message.get("sessionId") == session, method)

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        os.close(self.commands)
        os.close(self.replies)


class Page:
    """One tab in its own browser context."""

    def __init__(self, chrome, context, session, url):
        self.chrome, self.context, self.session, self.url = chrome, context, session, url

    def send(self, method, **params):
        return self.chrome.send(method, self.session, **params)

    def run(self, expression):
        """The JSON value of an expression, awaiting a promise."""
        reply = self.send("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in reply:
            raise RuntimeError(reply["exceptionDetails"])
        return reply["result"].get("value")

    def advance(self, milliseconds, settle=True):
        """Run the page's timers, by default waiting out each check they start."""
        self.run(f"clock.advance({milliseconds}, {json.dumps(settle)})")

    def wait_for_load(self):
        self.chrome.wait_for_event("Page.loadEventFired", self.session)

    def navigate(self, url):
        self.send("Page.navigate", url=url)
        self.wait_for_load()

    def reload(self):
        self.send("Page.reload")
        self.wait_for_load()

    def set_viewport(self, size):
        self.send("Emulation.setDeviceMetricsOverride", width=size[0], height=size[1], deviceScaleFactor=1, mobile=False)

    def set_visible(self, visible):
        self.run(HIDE % {"hidden": json.dumps(not visible), "state": json.dumps("visible" if visible else "hidden")})

    def press_key(self):
        self.send("Input.dispatchKeyEvent", type="rawKeyDown", key="Shift")
        self.send("Input.dispatchKeyEvent", type="keyUp", key="Shift")

    def click(self, selector):
        self.run(f"document.querySelector({json.dumps(selector)}).click()")

    def keep_quiet(self):
        """Move past the pause the page leaves after input, short of its next check."""
        self.finish_frame()
        self.advance(CHECK_INTERVAL // 4)

    def finish_frame(self):
        """Scroll events reach the page with the next rendered frame."""
        self.run("new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

    def selected_tab(self):
        return self.run("document.querySelector('[role=tab][aria-selected=true]').id")

    def selected_decision(self):
        return self.run("document.querySelector('.inbox-row[aria-selected=true]')?.getAttribute('aria-controls') ?? null")

    def visible_panels(self):
        return self.run("[...document.querySelectorAll('[role=tabpanel]:not([hidden])')].map(panel => panel.id)")

    def text(self):
        return self.run("document.querySelector('main').innerText")

    def scroll_to(self, y):
        self.run(f"document.scrollingElement.scrollTop = {y}")

    def top_of(self, selector):
        return self.run(f"document.querySelector({json.dumps(selector)}).getBoundingClientRect().top")

    def bring_into_view(self, selector, top):
        self.run(f"document.scrollingElement.scrollTop += document.querySelector({json.dumps(selector)}).getBoundingClientRect().top - {top}")

    def identity(self):
        """Marks the current DOM; it reads true until the page replaces its content."""
        self.run("document.querySelector('main').dataset.testMark = 'same'")
        return "document.querySelector('main').dataset.testMark === 'same'"


class Host(DashboardServer):
    """The dashboard server with test hooks: faults, stale navigations, and template shipping."""

    def __init__(self, folder, state):
        self.page_requests = 0
        self.fault = None
        self.stale_navigations = None
        program = folder / "program.json"
        program.write_text(json.dumps(state))
        super().__init__(program)
        self.RequestHandlerClass = HostHandler

    def handle_error(self, request, client_address):
        """Aborted checks close their connections mid-response by design."""

    def publish(self, state):
        """Write the program file as the chief does."""
        staging = self.state_path.with_name(".program.json.tmp")
        staging.write_text(json.dumps(state))
        os.replace(staging, self.state_path)

    def ship_template(self):
        """Serve pages from a changed template, as a restarted server would after a skill update."""
        self.page_template = self.page_template.replace("<body>", '<body data-shipped="yes">', 1)


class HostHandler(DashboardHandler):
    def do_GET(self):
        host = self.server
        if urlsplit(self.path).path == "/":
            host.page_requests += 1
            navigation = self.headers.get("Sec-Fetch-Mode") == "navigate"
            if navigation and host.stale_navigations:
                return self.reply(200, host.stale_navigations.encode())
            if host.fault and not navigation:
                return host.fault(self)
        super().do_GET()


def current_page(handler):
    return handler.server.page()[1].encode()


def server_error(handler):
    handler.reply(503, current_page(handler))


def dropped_connection(handler):
    handler.close_connection = True
    handler.connection.close()


def login_page(handler):
    handler.reply(200, b"<!doctype html><html><body><main>Sign in</main></body></html>")


def truncated_page(handler):
    page = current_page(handler)
    handler.reply(200, page[:page.index(b'id="work-panel"') + 200])


def not_html(handler):
    handler.reply(200, b'{"status": "ok"}', "application/json")


browser = None
browser_profile = None


def setUpModule():
    global browser, browser_profile
    required = os.environ.get("CI")
    executable = chrome_path()
    if not executable:
        if required:
            raise RuntimeError("CI needs Chrome for the command center tests")
        raise unittest.SkipTest("Chrome is not installed")
    print(f"command center tests use {executable}", file=sys.stderr)
    browser_profile = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    browser = Chrome(executable, browser_profile.name)
    try:
        browser.send("Browser.getVersion")
    except OSError as error:
        tearDownModule()
        if required:
            raise
        raise unittest.SkipTest(f"Chrome did not start: {error}")


def tearDownModule():
    browser.close()
    browser_profile.cleanup()


class CommandCenterCase(unittest.TestCase):
    def setUp(self):
        self.state = page_state()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.host = Host(Path(folder.name), self.state)
        self.addCleanup(self.host.server_close)
        threading.Thread(target=self.host.serve_forever, args=(.01,), daemon=True).start()
        self.addCleanup(self.host.shutdown)

    def open_page(self, size=DESKTOP, before_load="", context=None):
        if context is None:
            context = browser.send("Target.createBrowserContext")["browserContextId"]
            self.addCleanup(browser.send, "Target.disposeBrowserContext", browserContextId=context)
        target = browser.send("Target.createTarget", url="about:blank", browserContextId=context)["targetId"]
        session = browser.send("Target.attachToTarget", targetId=target, flatten=True)["sessionId"]
        page = Page(browser, context, session, f"http://127.0.0.1:{self.host.server_port}/")
        page.send("Page.enable")
        page.set_viewport(size)
        page.send("Page.addScriptToEvaluateOnNewDocument", source=PAGE_HARNESS + before_load)
        page.navigate(page.url)
        return page

    def changed(self, update):
        state = copy.deepcopy(self.state)
        update(state)
        return state

    def publish_retitled(self, title="Retitled snapshot"):
        self.host.publish(self.changed(lambda state: state.update(title=title)))

    def work(self, state, identity):
        return next(row for row in state["work"] if row["id"] == identity)

    def outcome(self, identity, stage, **fields):
        """A self-contained outcome row, with the published layer its stage needs."""
        row = {"id": identity, "title": f"Work {identity}", "repo": "example/exports", "kind": "outcome",
               "finishLine": "land", "state": stage, "owner": f"Owner {identity}", "updatedAt": "2026-11-02T16:00:00Z"}
        if stage in ("in-review", "ready", "landed"):
            status = {"landed": "merged", "ready": "ready"}.get(stage, "open")
            row["layers"] = [{"id": f"{identity}-L1", "branch": f"branch-{identity}", "status": status,
                              "url": f"https://example.com/exports/pull/{len(identity)}"}]
        return row | fields


class PublicationTests(CommandCenterCase):
    def test_checks_the_same_url_every_twenty_seconds_while_visible(self):
        page = self.open_page()
        before = self.host.page_requests
        page.advance(CHECK_INTERVAL - 500)
        self.assertEqual(self.host.page_requests, before)
        page.advance(1000)
        self.assertEqual(self.host.page_requests, before + 1)
        page.advance(CHECK_INTERVAL * 3)
        self.assertEqual(self.host.page_requests, before + 4)

    def test_new_publication_appears_without_a_reload(self):
        page = self.open_page()
        page.run("window.neverReloaded = true")
        self.publish_retitled()
        page.advance(CHECK_INTERVAL + 500)
        self.assertIn("Retitled snapshot", page.text())
        self.assertEqual(page.run("document.title"), "Retitled snapshot")
        self.assertTrue(page.run("window.neverReloaded"))
        self.assertIn("Snapshot updated", page.run("document.getElementById('snapshot-status').textContent"))
        same_dom = page.identity()
        page.advance(CHECK_INTERVAL * 2)
        self.assertTrue(page.run(same_dom))

    def test_unchanged_publication_leaves_the_screen_alone(self):
        page = self.open_page()
        same_dom = page.identity()
        self.host.publish(self.state)
        page.advance(CHECK_INTERVAL * 3 + 500)
        self.assertTrue(page.run(same_dom))

    def test_hidden_page_stops_checking_and_checks_at_once_when_it_returns(self):
        page = self.open_page()
        page.set_visible(False)
        before = self.host.page_requests
        self.publish_retitled()
        page.advance(CHECK_INTERVAL * 3)
        self.assertEqual(self.host.page_requests, before)
        page.set_visible(True)
        page.advance(500)
        self.assertEqual(self.host.page_requests, before + 1)
        self.assertIn("Retitled snapshot", page.text())

    def test_restored_page_checks_at_once(self):
        page = self.open_page()
        before = self.host.page_requests
        self.publish_retitled()
        page.run("dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))")
        page.advance(500)
        self.assertEqual(self.host.page_requests, before + 1)
        self.assertIn("Retitled snapshot", page.text())

    def test_replaced_content_keeps_working_controls_icons_and_times(self):
        page = self.open_page()
        self.publish_retitled()
        page.advance(CHECK_INTERVAL + 500)
        page.click("#work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])
        page.click("#needs-tab")
        rows = page.run("[...document.querySelectorAll('.inbox-row')].map(row => row.getAttribute('aria-controls'))")
        page.click(f'.inbox-row[aria-controls="{rows[1]}"]')
        self.assertEqual(page.selected_decision(), rows[1])
        self.assertTrue(page.run(f"document.getElementById({json.dumps(rows[1])}).classList.contains('selected')"))
        self.assertEqual(page.run("document.querySelectorAll('i[data-lucide]').length"), 0)
        snapshot_time = page.run("document.querySelector('time[data-age]').textContent")
        self.assertNotIn("T17:00:00Z", snapshot_time)
        page.run("navigator.clipboard.writeText = async text => { window.copied = text; }")
        page.click(".copy-prompt")
        self.assertIn("Decision", page.run("window.copied"))
        self.assertIn("Retitled snapshot", page.run("window.copied"))

    def test_changed_page_template_reloads_once_and_keeps_the_view(self):
        page = self.open_page()
        page.click("#work-tab")
        page.keep_quiet()
        self.host.ship_template()
        page.set_visible(True)
        page.wait_for_load()
        self.assertEqual(page.run("document.body.dataset.shipped"), "yes")
        self.assertEqual(page.selected_tab(), "work-tab")
        loads = self.host.page_requests
        page.advance(CHECK_INTERVAL * 2 + 500)
        self.assertEqual(self.host.page_requests, loads + 2)
        self.assertEqual(page.run("performance.getEntriesByType('navigation')[0].type"), "reload")

    def test_open_page_flags_a_bad_write_until_it_is_fixed(self):
        page = self.open_page()
        self.publish_retitled("Written once")
        page.advance(CHECK_INTERVAL + 500)
        self.assertIn("Written once", page.text())
        self.host.state_path.write_text("{broken")
        with contextlib.redirect_stderr(io.StringIO()):
            page.advance(CHECK_INTERVAL)
        self.assertIn("Showing the last good state.", page.text())
        self.assertIn("Written once", page.text())
        self.publish_retitled("Written again")
        page.advance(CHECK_INTERVAL)
        self.assertIn("Written again", page.text())
        self.assertNotIn("Showing the last good state.", page.text())

    def test_reload_that_returns_the_old_template_keeps_the_old_page_without_looping(self):
        page = self.open_page()
        page.click("#work-tab")
        page.keep_quiet()
        self.host.stale_navigations = self.host.page()[1]
        self.host.ship_template()
        self.host.publish(self.changed(lambda state: state.update(title="Newer content")))
        page.set_visible(True)
        page.wait_for_load()
        page.run("window.stayed = true")
        page.advance(CHECK_INTERVAL * 3)
        self.assertTrue(page.run("window.stayed"))
        self.assertNotIn("Newer content", page.text())
        page.click("#needs-tab")
        self.assertEqual(page.visible_panels(), ["needs-panel"])
        self.host.stale_navigations = None
        self.host.publish(self.changed(lambda state: state.update(title="Newest content")))
        page.set_visible(True)
        page.wait_for_load()
        self.assertIn("Newest content", page.text())


EVIDENCE = "#toggle-evidence-" + "W1".encode().hex()


class ViewTests(CommandCenterCase):
    def prepare_view(self, page):
        page.click("#work-tab")
        page.run("document.querySelector('.collapsible.planned details').querySelector('summary').click()")
        page.click(EVIDENCE)
        page.keep_quiet()

    def assert_view(self, page):
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])
        self.assertFalse(page.run("document.querySelector('.collapsible.planned details').open"))
        self.assertTrue(page.run(f"document.querySelector('{EVIDENCE}').parentElement.open"))

    def test_update_keeps_tab_sections_and_evidence(self):
        page = self.open_page()
        self.prepare_view(page)
        self.publish_retitled()
        page.advance(CHECK_INTERVAL)
        self.assertIn("Retitled snapshot", page.text())
        self.assert_view(page)

    def test_reload_keeps_tab_sections_and_evidence(self):
        page = self.open_page()
        self.prepare_view(page)
        page.reload()
        self.assert_view(page)

    def test_update_and_reload_keep_the_selected_decision(self):
        page = self.open_page()
        target = page.run("document.querySelectorAll('.inbox-row')[3].getAttribute('aria-controls')")
        page.click(f'.inbox-row[aria-controls="{target}"]')
        page.keep_quiet()
        self.publish_retitled()
        page.advance(CHECK_INTERVAL)
        self.assertIn("Retitled snapshot", page.text())
        self.assertEqual(page.selected_decision(), target)
        self.assertTrue(page.run(f"document.getElementById({json.dumps(target)}).checkVisibility()"))
        page.reload()
        self.assertEqual(page.selected_decision(), target)
        self.assertTrue(page.run(f"document.getElementById({json.dumps(target)}).checkVisibility()"))

    def test_removed_decision_falls_back_to_the_first_open_decision(self):
        page = self.open_page()
        rows = page.run("[...document.querySelectorAll('.inbox-row')].map(row => row.getAttribute('aria-controls'))")
        page.click(f'.inbox-row[aria-controls="{rows[2]}"]')
        page.keep_quiet()
        self.host.publish(self.changed(lambda state: state["needs"].pop(2)))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.selected_decision(), rows[0])
        self.assertTrue(page.run(f"document.getElementById({json.dumps(rows[0])}).checkVisibility()"))
        self.assertEqual(page.run("document.querySelectorAll('.inbox-row[tabindex=\"0\"]').length"), 1)

    def test_last_decisions_removed_leaves_a_working_empty_state(self):
        page = self.open_page()
        page.keep_quiet()
        self.host.publish(self.changed(lambda state: state.update(needs=[], revisits=[])))
        page.advance(CHECK_INTERVAL)
        self.assertIn("Nothing needs you", page.text())
        self.assertIsNone(page.selected_decision())
        page.click("#work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])

    def test_resolved_selection_stays_selected_in_its_new_group(self):
        page = self.open_page()
        target = "decision-" + "W1-D2".encode().hex()
        page.click(f'.inbox-row[aria-controls="{target}"]')
        page.keep_quiet()

        def resolve(state):
            need = next(row for row in state["needs"] if row["id"] == "W1-D2")
            need.update(status="resolved", answer="Three retries", basis="Matches the recorded policy.")
        self.host.publish(self.changed(resolve))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.selected_decision(), target)
        self.assertEqual(page.run("document.querySelector('.inbox-row[aria-selected=true]').closest('.inbox-group').querySelector('.inbox-group-title').innerText").split()[0:2], ["Chief", "decided"])

    def test_removed_section_keeps_the_others_as_saved(self):
        page = self.open_page()
        self.prepare_view(page)

        def finish_planned(state):
            state["work"] = [row for row in state["work"] if row["state"] != "planned"]
            for need in state["needs"]:
                need["blocks"] = [entry for entry in need.get("blocks", []) if entry["id"] != "W4"]
        self.host.publish(self.changed(finish_planned))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.run("document.querySelectorAll('.collapsible.planned').length"), 0)
        self.assertTrue(page.run(f"document.querySelector('{EVIDENCE}').parentElement.open"))
        self.assertEqual(page.selected_tab(), "work-tab")

    def test_storage_keeps_each_dashboard_url_apart(self):
        page = self.open_page()
        page.click("#work-tab")
        page.keep_quiet()
        page.navigate(page.url + "?program=other")
        self.assertEqual(page.selected_tab(), "needs-tab")

    def test_leaving_the_tab_saves_the_view(self):
        page = self.open_page()
        page.click("#work-tab")
        page.set_visible(False)
        saved = page.run(f"JSON.parse(sessionStorage.getItem({json.dumps(VIEW_KEY_PREFIX + page.url)})).tab")
        self.assertEqual(saved, "work-tab")

    def test_new_visit_starts_at_needs_you(self):
        page = self.open_page()
        page.click("#work-tab")
        page.reload()
        self.assertEqual(page.selected_tab(), "work-tab")
        second_visit = self.open_page(context=page.context)
        self.assertEqual(second_visit.selected_tab(), "needs-tab")

    def test_corrupt_storage_is_ignored_and_replaced(self):
        for saved in ("{not json", "[]", "null", '"text"', '{"tab": 7, "decision": {}, "sections": 3, "scroll": 4}',
                      '{"tab": "<img>", "sections": {"x": "y"}, "scroll": {"page": {"position": "x", "anchors": 5}}}',
                      '{"scroll": {"page": {"position": 9, "anchors": [1, {"id": 7}, {"id": "needs-tab", "offset": "y"}]}}}',
                      '{"scroll": {"page": {"position": {"toString": null}, "anchors": [{"id": {"toString": null}}]}}}',
                      '{"scroll": {"inbox": {"position": 5, "anchors": [{"id": "x", "offset": {"valueOf": null}}]}}}'):
            with self.subTest(saved=saved):
                seed = (f"if (!sessionStorage.getItem('seeded')) {{ sessionStorage.setItem('seeded', '1'); "
                        f"sessionStorage.setItem({json.dumps(VIEW_KEY_PREFIX)} + location.href, {json.dumps(saved)}); }}")
                page = self.open_page(before_load=seed)
                self.assertEqual(page.selected_tab(), "needs-tab")
                self.assertEqual(page.run("pageErrors"), [])
                self.publish_retitled(f"Published after {saved}")
                page.advance(CHECK_INTERVAL)
                self.assertEqual(page.run("document.title"), f"Published after {saved}")
                page.click("#work-tab")
                page.keep_quiet()
                page.reload()
                self.assertEqual(page.selected_tab(), "work-tab")

    def test_view_survives_updates_when_storage_is_unavailable(self):
        full_storage = "Storage.prototype.setItem = () => { throw new DOMException('full', 'QuotaExceededError'); };"
        for storage_failure in (BLOCK_STORAGE, full_storage):
            with self.subTest(storage_failure=storage_failure):
                page = self.open_page(before_load=storage_failure)
                self.prepare_view(page)
                page.set_visible(False)
                page.set_visible(True)
                page.run("clock.settled()")
                self.publish_retitled()
                page.advance(CHECK_INTERVAL)
                self.assertIn("Retitled snapshot", page.text())
                self.assert_view(page)
                self.assertEqual(page.run("pageErrors"), [])


class ScrollTests(CommandCenterCase):
    def long_state(self):
        def lengthen(state):
            for index in range(10, 45):
                state["work"].append(self.outcome(f"W{index}", ("building", "planned", "in-review")[index % 3], title=f"Extra work {index}"))
        self.state = self.changed(lengthen)
        self.host.publish(self.state)

    def card(self, identity):
        return f"#work-card-{identity.encode().hex()}"

    def read_in_work(self, page, identity, top=120):
        page.click("#work-tab")
        page.bring_into_view(self.card(identity), top)
        page.keep_quiet()

    def test_phone_reading_position_follows_its_card_when_content_is_added_above(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W20")
        before = page.top_of(self.card("W20"))

        def add_above(state):
            for index in range(50, 54):
                state["work"].insert(0, self.outcome(f"W{index}", "planned", title=f"New work {index}"))
        self.host.publish(self.changed(add_above))
        page.advance(CHECK_INTERVAL)
        self.assertIn("New work 50", page.text())
        self.assertAlmostEqual(page.top_of(self.card("W20")), before, delta=1)

    def lane_of(self, page, identity):
        return page.run(f"document.querySelector({json.dumps(self.card(identity))}).closest('.collapsible').className")

    def test_phone_reading_position_moves_to_a_neighbour_when_its_card_is_removed(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W20", top=0)
        neighbour = page.run(f"document.querySelector({json.dumps(self.card('W20'))}).nextElementSibling.id")
        before = page.top_of("#" + neighbour)

        def remove(state):
            state["work"] = [row for row in state["work"] if row["id"] != "W20"]
        self.host.publish(self.changed(remove))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.run(f"document.querySelectorAll({json.dumps(self.card('W20'))}).length"), 0)
        self.assertAlmostEqual(page.top_of("#" + neighbour), before, delta=1)

    def test_reading_position_skips_a_card_that_moved_into_a_collapsed_section(self):
        self.long_state()
        page = self.open_page(PHONE)
        page.click("#toggle-stage-planned")
        self.read_in_work(page, "W20", top=0)
        neighbour = page.run(f"document.querySelector({json.dumps(self.card('W20'))}).nextElementSibling.id")
        before = page.top_of("#" + neighbour)
        self.host.publish(self.changed(lambda state: self.work(state, "W20").update(state="planned", title="Parked card")))
        page.advance(CHECK_INTERVAL)
        self.assertAlmostEqual(page.top_of("#" + neighbour), before, delta=1)

    def test_every_anchor_gone_clamps_to_the_page_that_remains(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W35")
        self.host.publish(self.changed(lambda state: state.update(work=[self.outcome("W2", "building")], needs=[], revisits=[])))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.run("document.querySelectorAll('.work').length"), 1)
        self.assertLessEqual(page.run("scrollY + innerHeight"), page.run("document.documentElement.scrollHeight"))
        self.assertEqual(page.selected_tab(), "work-tab")

    def test_top_of_the_page_stays_at_the_top(self):
        page = self.open_page(PHONE)
        page.keep_quiet()
        self.host.publish(self.changed(lambda state: state.update(goal=state["goal"] + " " + "Longer goal. " * 30)))
        page.advance(CHECK_INTERVAL)
        self.assertIn("Longer goal", page.text())
        self.assertEqual(page.run("scrollY"), 0)

    def test_reload_follows_a_card_that_moved_since_the_last_check(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W20", top=0)
        before = page.top_of(self.card("W20"))
        self.host.publish(self.changed(lambda state: (state.update(title="Moved while away"), self.work(state, "W20").update(state="building"))))
        page.reload()
        self.assertEqual(page.run("document.title"), "Moved while away")
        self.assertIn("building", self.lane_of(page, "W20"))
        self.assertAlmostEqual(page.top_of(self.card("W20")), before, delta=1)

    def test_phone_position_ignores_cards_in_a_collapsed_section(self):
        self.long_state()
        page = self.open_page(PHONE)
        page.click("#work-tab")
        page.click("#toggle-stage-planned")
        self.read_in_work(page, "W20", top=120)
        before = page.top_of(self.card("W20"))

        def add_above(state):
            for index in range(50, 54):
                state["work"].insert(0, dict(copy.deepcopy(self.work(state, "W3")), id=f"W{index}", title=f"New work {index}", state="building", blockedBy=[]))
        self.host.publish(self.changed(add_above))
        page.advance(CHECK_INTERVAL)
        self.assertIn("New work 50", page.text())
        self.assertAlmostEqual(page.top_of(self.card("W20")), before, delta=1)

    def test_phone_position_holds_when_a_hidden_card_leaves_a_collapsed_section(self):
        self.long_state()
        page = self.open_page(PHONE)
        page.click("#work-tab")
        page.click("#toggle-stage-planned")
        self.read_in_work(page, "W20", top=120)
        before = page.top_of(self.card("W20"))
        self.host.publish(self.changed(lambda state: self.work(state, "W22").update(self.outcome("W22", "in-review"))))
        page.advance(CHECK_INTERVAL)
        self.assertIn("in-review", self.lane_of(page, "W22"))
        self.assertAlmostEqual(page.top_of(self.card("W20")), before, delta=1)

    def test_desktop_page_follows_a_card_when_the_board_has_one_lane(self):
        def one_lane(state):
            state["needs"] = []
            state["revisits"] = []
            state["work"] = [dict(copy.deepcopy(self.work(state, "W3")), id=f"W{index}", title=f"Task {index}", blockedBy=[]) for index in range(30)]
        self.state = self.changed(one_lane)
        self.host.publish(self.state)
        page = self.open_page(DESKTOP)
        self.read_in_work(page, "W12", top=0)
        before = page.top_of(self.card("W12"))
        self.host.publish(self.changed(lambda state: state["work"].insert(0, dict(copy.deepcopy(state["work"][0]), id="ADDED", title="New card"))))
        page.advance(CHECK_INTERVAL)
        self.assertIn("New card", page.text())
        self.assertAlmostEqual(page.top_of(self.card("W12")), before, delta=1)

    def test_board_keeps_its_lane_in_place(self):
        self.wide_board()
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.run("document.querySelector('.stage-board').scrollLeft = 300")
        page.keep_quiet()
        lane = ".stage-board .collapsible.landed"
        before = page.run(f"document.querySelector('{lane}').getBoundingClientRect().left")
        self.host.publish(self.changed(lambda state: state["work"].append(self.outcome("X9", "unknown", unknownReason="Forge unavailable"))))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.run("document.querySelectorAll('.work').length"), 11)
        self.assertGreater(page.run("document.querySelector('.stage-board').scrollLeft"), 0)
        self.assertAlmostEqual(page.run(f"document.querySelector('{lane}').getBoundingClientRect().left"), before, delta=1)
        page.reload()
        self.assertAlmostEqual(page.run(f"document.querySelector('{lane}').getBoundingClientRect().left"), before, delta=1)

    def wide_board(self):
        self.state["work"] += [dict(copy.deepcopy(self.work(self.state, "W3")), id=f"X{index}", state=state)
                               for index, state in enumerate(("done", "scrapped"))]
        self.state["work"].append(self.outcome("X2", "scrapped"))
        self.host.publish(self.state)

    def test_board_position_survives_updates_and_reloads_from_the_other_tab(self):
        self.wide_board()
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.run("document.querySelector('.stage-board').scrollLeft = 300")
        page.click("#needs-tab")
        page.keep_quiet()
        self.publish_retitled()
        page.advance(CHECK_INTERVAL)
        self.assertIn("Retitled snapshot", page.text())
        page.click("#work-tab")
        self.assertEqual(page.run("document.querySelector('.stage-board').scrollLeft"), 300)
        page.click("#needs-tab")
        page.reload()
        page.click("#work-tab")
        self.assertEqual(page.run("document.querySelector('.stage-board').scrollLeft"), 300)

    def long_decision_list(self):
        self.state["needs"] += [dict(copy.deepcopy(self.state["needs"][0]), id=f"N{index}", ask=f"Extra decision {index}") for index in range(20)]
        self.host.publish(self.state)

    def test_decision_list_keeps_its_row_when_a_decision_is_added_above_it(self):
        self.long_decision_list()
        page = self.open_page(DESKTOP)
        page.run("document.querySelector('.inbox-list').scrollTop = 400")
        page.keep_quiet()
        row = "#row-decision-" + "N10".encode().hex()
        before = page.top_of(row)

        def add_above(state):
            state["needs"].insert(0, dict(copy.deepcopy(state["needs"][0]), id="NEWEST", ask="A newer decision"))
        self.host.publish(self.changed(add_above))
        page.advance(CHECK_INTERVAL)
        self.assertIn("A newer decision", page.text())
        self.assertAlmostEqual(page.top_of(row), before, delta=1)

    def test_desktop_page_stays_put_when_a_card_moves_to_another_lane(self):
        self.long_state()
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.run("document.scrollingElement.scrollTop = 1500")
        page.keep_quiet()
        mover = page.run("[...document.querySelectorAll('.collapsible.planned .work')].find(card => card.getBoundingClientRect().bottom > 0).id")
        watched = page.run("[...document.querySelectorAll('.collapsible.in-review .work')].find(card => card.getBoundingClientRect().top > 0).id")
        before = page.top_of("#" + watched)
        identity = bytes.fromhex(mover.removeprefix("work-card-")).decode()
        landed = {"state": "landed", "layers": [{"id": f"{identity}-L1", "branch": "landed", "status": "merged", "url": "https://example.test/pull/9"}]}
        self.host.publish(self.changed(lambda state: self.work(state, identity).update(landed)))
        page.advance(CHECK_INTERVAL)
        self.assertIn("landed", page.run(f"document.getElementById({json.dumps(mover)}).closest('.collapsible').className"))
        self.assertAlmostEqual(page.top_of("#" + watched), before, delta=1)


class MorningViewTests(CommandCenterCase):
    def card(self, identity):
        return f"#work-card-{identity.encode().hex()}"

    def card_text(self, page, identity):
        return page.run(f"document.querySelector({json.dumps(self.card(identity))}).innerText")

    def test_phone_work_view_fits_and_shows_results_layers_and_provisional_state(self):
        page = self.open_page(PHONE)
        page.click("#work-tab")
        self.assertLessEqual(page.run("document.scrollingElement.scrollWidth"), PHONE[0])
        outside = page.run("[...document.querySelectorAll('.work, .layer, .results, .provisional-note, .blocker')]"
                           ".filter(node => node.getBoundingClientRect().right > innerWidth + .5).length")
        self.assertEqual(outside, 0)
        try_card = self.card_text(page, "W5")
        self.assertIn("Preview build", try_card)
        self.assertIn("Tailnet only. Stays up until you choose.", try_card)
        self.assertIn("Waits on", try_card)
        self.assertNotIn("Blocked", try_card)
        provisional = self.card_text(page, "W2")
        self.assertIn("It never lands while provisional.", provisional)
        self.assertIn("on W1-L2 (W1)", provisional)
        targets = page.run("[...document.querySelectorAll('.work .pr-link, .work .result-link')].map(link => link.getBoundingClientRect().height)")
        self.assertEqual(len(targets), 5)
        self.assertTrue(all(height >= 44 for height in targets), targets)

    def test_phone_decision_cards_say_what_they_block_and_copy_one_try_choice(self):
        page = self.open_page(PHONE)
        self.assertLessEqual(page.run("document.scrollingElement.scrollWidth"), PHONE[0])
        first = page.run("document.querySelector('.need').innerText")
        self.assertIn("Blocks W6 acceptance", first)
        self.assertIn("W6 builds on keeping the entry", first)
        target = "decision-" + "W5-T".encode().hex()
        labels = page.run(f"[...document.querySelectorAll('#{target} .options .copy-prompt')].map(button => button.getAttribute('aria-label'))")
        self.assertEqual(labels, ["Copy prompt: Merge", "Copy prompt: Changes", "Copy prompt: Scrap"])
        page.run("navigator.clipboard.writeText = async text => { window.copied = text; }")
        page.click(f"#{target} .options li:last-child .copy-prompt")
        page.run("clock.settled()")
        copied = page.run("window.copied").splitlines()
        self.assertTrue(copied[0].startswith('Decision "W5-T" (revision '))
        self.assertEqual(copied[-1], 'I choose option 3: "Scrap"')

    def test_update_keeps_a_focused_layer_link_in_place_as_the_program_grows(self):
        page = self.open_page(PHONE)
        page.click("#work-tab")
        link = 'a[href="https://example.com/exports/pull/44"]'
        page.bring_into_view(self.card("W1"), 120)
        page.run(f"document.querySelector({json.dumps(link)}).focus({{preventScroll: true}})")
        before = page.top_of(link)
        page.keep_quiet()

        def grow(state):
            self.work(state, "W1")["layers"].append({"id": "W1-L3", "branch": "export-retry-docs", "status": "open",
                                                     "url": "https://example.com/exports/pull/45", "stackedOn": "W1-L2"})
            state["work"].insert(0, self.outcome("W9", "planned", title="Newly planned outcome"))
        self.host.publish(self.changed(grow))
        page.advance(CHECK_INTERVAL)
        self.assertIn("Newly planned outcome", page.text())
        self.assertIn("3 layers, bottom first", self.card_text(page, "W1"))
        self.assertEqual(page.run("document.activeElement.getAttribute('href')"), "https://example.com/exports/pull/44")
        self.assertAlmostEqual(page.top_of(link), before, delta=1)

    def test_phone_follows_a_kept_try_into_review(self):
        page = self.open_page(PHONE)
        page.click("#work-tab")
        page.bring_into_view(self.card("W5"), 0)
        page.keep_quiet()
        before = page.top_of(self.card("W5"))

        def keep(state):
            self.work(state, "W5").update(finishLine="land", state="in-review", layers=[
                {"id": "W5-L1", "branch": "export-history", "status": "open", "url": "https://example.com/exports/pull/50"}])
            next(need for need in state["needs"] if need["id"] == "W5-T").update(status="answered", answer="Merge")
        self.host.publish(self.changed(keep))
        page.advance(CHECK_INTERVAL)
        self.assertIn("in-review", page.run(f"document.querySelector({json.dumps(self.card('W5'))}).closest('.collapsible').className"))
        self.assertIn("PR #50", self.card_text(page, "W5"))
        self.assertAlmostEqual(page.top_of(self.card("W5")), before, delta=1)
        self.assertEqual(page.selected_tab(), "work-tab")


class FailureTests(CommandCenterCase):
    def assert_still_usable(self, page):
        self.assertTrue(page.run("document.querySelector('main').isConnected"))
        page.click("#work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])
        page.click("#needs-tab")
        self.assertEqual(page.visible_panels(), ["needs-panel"])

    def test_bad_responses_leave_the_page_alone_and_later_checks_recover(self):
        for fault in (server_error, dropped_connection, login_page, truncated_page, not_html):
            with self.subTest(fault=fault.__name__):
                page = self.open_page()
                page.run("history.replaceState({reloadedFor: 'an earlier publication'}, '')")
                same_dom = page.identity()
                self.publish_retitled(f"Recovered from {fault.__name__}")
                self.host.fault = fault
                before = self.host.page_requests
                page.advance(CHECK_INTERVAL * 2 + 500)
                self.assertEqual(self.host.page_requests, before + 2)
                self.assertTrue(page.run(same_dom))
                self.assert_still_usable(page)
                self.host.fault = None
                page.advance(CHECK_INTERVAL * 2)
                self.assertIn(f"Recovered from {fault.__name__}", page.text())

    def test_stalled_check_is_abandoned_and_retried_without_overlap(self):
        page = self.open_page()
        release = threading.Event()
        self.addCleanup(release.set)
        self.host.fault = lambda handler: (release.wait(REPLY_TIMEOUT), dropped_connection(handler))
        page.advance(CHECK_INTERVAL + 5000, settle=False)
        self.assertEqual(page.run("checks.count"), 1)
        self.assertEqual(page.run("checks.live.length"), 1)
        page.advance(10_000, settle=False)
        self.assertEqual(page.run("checks.live.length"), 0)
        page.advance(CHECK_INTERVAL, settle=False)
        self.assertEqual(page.run("[checks.count, checks.most]"), [2, 1])
        release.set()
        self.host.fault = None
        self.publish_retitled()
        page.advance(CHECK_INTERVAL * 2)
        self.assertIn("Retitled snapshot", page.text())

    def test_returning_repeatedly_keeps_one_check_in_flight(self):
        page = self.open_page()
        release = threading.Event()
        self.addCleanup(release.set)
        self.host.fault = lambda handler: (release.wait(REPLY_TIMEOUT), dropped_connection(handler))
        for _ in range(4):
            page.set_visible(False)
            page.set_visible(True)
        self.assertEqual(page.run("[checks.count, checks.most]"), [4, 1])
        self.assertEqual(page.run("checks.live.length"), 1)
        release.set()
        self.host.fault = None
        self.assert_still_usable(page)


class InteractionTests(CommandCenterCase):
    def select_goal(self, page):
        page.keep_quiet()
        page.run("getSelection().selectAllChildren(document.querySelector('.goal'))")
        page.press_key()

    def test_update_waits_for_a_text_selection_and_then_applies(self):
        page = self.open_page()
        self.select_goal(page)
        selected = page.run("getSelection().toString()")
        self.publish_retitled()
        page.advance(CHECK_INTERVAL * 2)
        self.assertEqual(page.run("getSelection().toString()"), selected)
        self.assertNotIn("Retitled snapshot", page.text())
        page.run("getSelection().removeAllRanges()")
        page.advance(CHECK_INTERVAL + 500)
        self.assertIn("Retitled snapshot", page.text())

    def test_update_waits_for_the_manual_copy_box_and_then_applies(self):
        page = self.open_page()
        page.run("navigator.clipboard.writeText = async () => { throw new Error('denied'); }")
        page.click(".options .copy-prompt")
        page.run("clock.settled()")
        page.press_key()
        page.advance(CHECK_INTERVAL // 4)
        self.assertTrue(page.run("document.activeElement.matches('textarea.manual-prompt')"))
        self.publish_retitled()
        page.advance(CHECK_INTERVAL * 2)
        self.assertTrue(page.run("document.activeElement.matches('textarea.manual-prompt')"))
        self.assertNotIn("Retitled snapshot", page.text())
        page.run("document.activeElement.blur()")
        page.advance(CHECK_INTERVAL + 500)
        self.assertIn("Retitled snapshot", page.text())

    def test_update_waits_for_a_held_pointer(self):
        page = self.open_page()
        page.keep_quiet()
        page.send("Input.dispatchMouseEvent", type="mousePressed", x=200, y=200, button="left", clickCount=1)
        self.publish_retitled()
        page.advance(CHECK_INTERVAL * 2)
        self.assertNotIn("Retitled snapshot", page.text())
        page.send("Input.dispatchMouseEvent", type="mouseReleased", x=200, y=200, button="left", clickCount=1)
        page.advance(CHECK_INTERVAL + 500)
        self.assertIn("Retitled snapshot", page.text())

    def test_update_waits_for_a_resting_finger_but_not_forever(self):
        page = self.open_page(PHONE)
        page.send("Emulation.setTouchEmulationEnabled", enabled=True)
        page.keep_quiet()
        page.send("Input.dispatchTouchEvent", type="touchStart", touchPoints=[{"x": 200, "y": 200}])
        page.finish_frame()
        self.publish_retitled()
        page.advance(CHECK_INTERVAL * 2)
        self.assertNotIn("Retitled snapshot", page.text())
        page.advance(HELD_LIMIT)
        self.assertIn("Retitled snapshot", page.text())
        page.send("Input.dispatchTouchEvent", type="touchEnd", touchPoints=[])

    def test_update_waits_for_scrolling_to_settle(self):
        page = self.open_page(PHONE)
        page.keep_quiet()
        self.publish_retitled()
        page.scroll_to(200)
        page.finish_frame()
        page.advance(100)
        page.set_visible(True)
        page.advance(100)
        self.assertNotIn("Retitled snapshot", page.text())
        page.advance(CHECK_INTERVAL)
        self.assertIn("Retitled snapshot", page.text())

    def test_update_returns_keyboard_focus_to_the_same_control(self):
        page = self.open_page()
        target = page.run("document.querySelectorAll('.inbox-row')[1].id")
        page.run(f"document.getElementById({json.dumps(target)}).focus()")
        page.keep_quiet()
        self.publish_retitled()
        page.advance(CHECK_INTERVAL)
        self.assertIn("Retitled snapshot", page.text())
        self.assertEqual(page.run("document.activeElement.id"), target)

    def test_update_keeps_focus_on_the_same_choice_when_another_is_added_before_it(self):
        page = self.open_page()
        buttons = ".need.selected .options .copy-prompt"
        page.run(f"document.querySelectorAll('{buttons}')[1].focus()")
        expected = page.run("document.activeElement.getAttribute('aria-label')")
        page.keep_quiet()

        def add_option(state):
            state["needs"][0]["options"].insert(0, {"label": "A new first choice", "effect": "It shifts the others down."})
        self.host.publish(self.changed(add_option))
        page.advance(CHECK_INTERVAL)
        self.assertEqual(page.run(f"document.querySelectorAll('{buttons}').length"), len(self.state["needs"][0]["options"]) + 1)
        self.assertEqual(page.run("document.activeElement.getAttribute('aria-label')"), expected)

    def test_reload_paints_no_focus_ring_on_a_control_the_mouse_touched(self):
        page = self.open_page()
        box = page.run("(() => { const box = document.querySelector('#work-tab').getBoundingClientRect(); return [box.x + 10, box.y + 10]; })()")
        for kind in ("mousePressed", "mouseReleased"):
            page.send("Input.dispatchMouseEvent", type=kind, x=box[0], y=box[1], button="left", clickCount=1)
        page.reload()
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertEqual(page.run("document.querySelectorAll(':focus-visible').length"), 0)

    def test_update_returns_focus_to_a_link_inside_a_card(self):
        page = self.open_page()
        page.click("#work-tab")
        page.run("document.querySelector('.pr-link').focus()")
        expected = page.run("document.activeElement.getAttribute('href')")
        page.keep_quiet()
        self.publish_retitled()
        page.advance(CHECK_INTERVAL)
        self.assertIn("Retitled snapshot", page.text())
        self.assertEqual(page.run("document.activeElement.getAttribute('href')"), expected)

    def test_click_during_a_check_is_kept_when_the_answer_arrives(self):
        page = self.open_page()
        page.keep_quiet()
        self.publish_retitled()
        self.host.fault = lambda handler: (time.sleep(.3), DashboardHandler.do_GET(handler))
        page.advance(CHECK_INTERVAL - CHECK_INTERVAL // 4 + 100, settle=False)
        page.click("#work-tab")
        self.host.fault = None
        page.run("clock.settled()")
        self.assertIn("Retitled snapshot", page.text())
        self.assertEqual(page.selected_tab(), "work-tab")


if __name__ == "__main__":
    unittest.main()
