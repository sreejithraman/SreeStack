"""Drive the command center's in-browser behavior in headless Chrome.

Chrome's debugging pipe needs no client package. Each test renders the page to a
file served from a loopback origin and opens it; a republish renders the file
again and reloads the page. These
tests cover tabs, selection, copy prompts, and the view kept across a reload, not
how a Claude artifact frame delivers a new version. Without a usable Chrome the
tests skip locally and fail in CI.
"""

import copy
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zlib

from render_dashboard import render
from render_dashboard import ISO_TIME, content_name, revision
from test_render_dashboard import decision, example, owner


DESKTOP = (1280, 800)
PHONE = (390, 844)
REPLY_TIMEOUT = 20
VIEW_KEY = "command-center-view"

# Each launch of branded macOS Chrome copies its signed app into a code_sign_clone
# folder under /var/folders, and the copy outlives the process, so it comes last.
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PLAYWRIGHT_CHROMES = (
    "chromium-*/chrome-mac*/*.app/Contents/MacOS/*",
    "chromium-*/chrome-linux*/chrome",
    "chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
)
PAGE_HARNESS = """
window.pageErrors = [];
addEventListener('error', event => pageErrors.push(event.message));
window.lucide = {createIcons() {
  for (const mark of document.querySelectorAll('i[data-lucide]')) {
    const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    icon.setAttribute('class', mark.getAttribute('class'));
    mark.replaceWith(icon);
  }
}};
"""
BLOCK_STORAGE = """
Object.defineProperty(window, 'sessionStorage', {get() { throw new DOMException('denied', 'SecurityError'); }});
"""
# A page database as the artifact runtime would serve it, kept in localStorage so it outlives a reload.
FAKE_DB = """
window.storedPicks = () => JSON.parse(localStorage.getItem('fake-db') || '{}');
window.wakeDoc = %(wake)s;
const writeDb = docs => localStorage.setItem('fake-db', JSON.stringify(docs));
const fakeDoc = (path, data) => ({id: path.split('/').pop(), exists: data !== undefined, data: () => data});
window.claude = {use: async name => name !== 'db' ? null : {
  doc: path => ({
    get: async () => fakeDoc(path, path === 'config/wake' ? wakeDoc ?? undefined : storedPicks()[path]),
    set: async data => {
      if (window.holdWrites) await new Promise(resolve => { window.releaseWrite = resolve; });
      if (%(refuse)s) throw {code: 'invalid_argument'};
      writeDb({...storedPicks(), [path]: data});
    },
  }),
  collection: path => ({get: async () => {
    if (window.holdReads) await new Promise(resolve => { window.releaseRead = resolve; });
    return {docs: Object.entries(storedPicks()).filter(([key]) => key.startsWith(path + '/')).map(([key, data]) => fakeDoc(key, data))};
  }}),
}};
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

    def click(self, selector):
        self.run(f"document.querySelector({json.dumps(selector)}).click()")

    def selected_tab(self):
        return self.run("document.querySelector('[role=tab][aria-selected=true]').id")

    def selected_decision(self):
        return self.run("document.querySelector('.inbox-row[aria-selected=true]')?.getAttribute('aria-controls') ?? null")

    def visible_panels(self):
        return self.run("[...document.querySelectorAll('[role=tabpanel]:not([hidden])')].map(panel => panel.id)")

    def text(self):
        return self.run("document.querySelector('main').innerText")

    def top_of(self, selector):
        return self.run(f"document.querySelector({json.dumps(selector)}).getBoundingClientRect().top")

    def bring_into_view(self, selector, top):
        self.run(f"document.scrollingElement.scrollTop += document.querySelector({json.dumps(selector)}).getBoundingClientRect().top - {top}")


class FreshPage(SimpleHTTPRequestHandler):
    """Serves each republish uncached, so a reload always gets the new file."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


browser = None
browser_profile = None
# Chrome gives file:// pages an opaque origin and sometimes drops their sessionStorage on reload.
site = None
server = None


def setUpModule():
    global browser, browser_profile, site, server
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
    site = tempfile.TemporaryDirectory()
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(FreshPage, directory=site.name))
    threading.Thread(target=server.serve_forever, daemon=True).start()


def tearDownModule():
    if server:
        server.shutdown()
        server.server_close()
        site.cleanup()
    browser.close()
    browser_profile.cleanup()



class CommandCenterCase(unittest.TestCase):
    def setUp(self):
        self.state = example()
        folder = tempfile.TemporaryDirectory(dir=site.name)
        self.addCleanup(folder.cleanup)
        self.page_file = Path(folder.name) / "command-center.html"
        self.page_url = f"http://127.0.0.1:{server.server_port}/{self.page_file.parent.name}/{self.page_file.name}"
        self.publish(self.state)

    def publish(self, state):
        self.page_file.write_text(render(state))

    def republish(self, page, state):
        """Publish a new version and reload the open page, as an artifact moves to it."""
        self.publish(state)
        page.reload()

    def open_page(self, size=DESKTOP, before_load="", context=None):
        if context is None:
            context = browser.send("Target.createBrowserContext")["browserContextId"]
            self.addCleanup(browser.send, "Target.disposeBrowserContext", browserContextId=context)
        target = browser.send("Target.createTarget", url="about:blank", browserContextId=context)["targetId"]
        session = browser.send("Target.attachToTarget", targetId=target, flatten=True)["sessionId"]
        page = Page(browser, context, session, self.page_url)
        page.send("Page.enable")
        page.set_viewport(size)
        page.send("Page.addScriptToEvaluateOnNewDocument", source=PAGE_HARNESS + before_load)
        page.navigate(page.url)
        return page

    def changed(self, update):
        state = copy.deepcopy(self.state)
        update(state)
        return state

    def retitled(self, title="Retitled program"):
        return self.changed(lambda state: state.update(title=title))

    def work(self, state, identity):
        return next(row for row in state["work"] if row["id"] == identity)

    def card(self, identity):
        return f"#work-card-{identity.encode().hex()}"

    def outcome(self, identity, stage, **fields):
        """A self-contained outcome row, with the published layer its stage needs."""
        row = {"id": identity, "title": f"Work {identity}", "repo": "example/exports", "kind": "outcome",
               "finishLine": "land", "state": stage, "owner": owner(f"Owner {identity}"), "checkedAt": "2026-11-02T16:00:00Z"}
        if stage in ("in-review", "ready", "landed"):
            status = {"landed": "merged", "ready": "ready"}.get(stage, "open")
            row["layers"] = [{"id": f"{identity}-L1", "branch": f"branch-{identity}", "status": status,
                              "url": f"https://example.com/exports/pull/{len(identity)}"}]
        return row | fields


class PageTests(CommandCenterCase):
    def test_tabs_and_decisions_select_by_click_and_arrow_keys(self):
        page = self.open_page()
        page.click("#work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])
        page.run("document.querySelector('#work-tab').dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowRight', bubbles: true}))")
        self.assertEqual((page.selected_tab(), page.visible_panels()), ("needs-tab", ["needs-panel"]))
        rows = page.run("[...document.querySelectorAll('.inbox-row')].map(row => row.getAttribute('aria-controls'))")
        page.click(f'.inbox-row[aria-controls="{rows[1]}"]')
        self.assertEqual(page.selected_decision(), rows[1])
        self.assertEqual(page.run("[...document.querySelectorAll('.need.selected')].map(card => card.id)"), [rows[1]])
        page.run(f"document.querySelector('.inbox-row[aria-controls=\"{rows[1]}\"]').dispatchEvent(new KeyboardEvent('keydown', {{key: 'ArrowDown', bubbles: true}}))")
        self.assertEqual(page.selected_decision(), rows[2])
        self.assertEqual(page.run("pageErrors"), [])

    def test_times_in_prose_read_in_local_time(self):
        self.publish(self.changed(lambda state: self.work(state, "W1").update(description="Paused at 2026-11-02T17:00:00Z.")))
        page = self.open_page()
        page.click("#work-tab")
        title, shown = page.run("(time => [time.title, time.textContent])(document.querySelector('.work-description time'))")
        self.assertIn("2026", title)
        for text in (title, shown):
            self.assertNotIn("T17:00", text)
        self.assertEqual(page.run("pageErrors"), [])

    def test_no_utc_time_reaches_the_reader(self):
        stamp = "2026-11-02T17:00:00Z"
        self.publish(self.changed(lambda state: (
            self.work(state, "W1").update(description=f"Paused at {stamp}."), state.update(next=f"Recheck at {stamp}."))))
        page = self.open_page(PHONE, before_load="")
        page.send("Emulation.setTimezoneOverride", timezoneId="Pacific/Honolulu")
        page.reload()
        shown = page.run("""[document.querySelector('main').textContent,
            ...[...document.querySelectorAll('[title], [aria-label]')].flatMap(item => [item.title, item.getAttribute('aria-label') ?? ''])]""")
        leaks = [text for text in shown if ISO_TIME.search(text) or "UTC" in text or re.search(r"\d{4}-\d{2}-\d{2}", text)]
        self.assertEqual(leaks, [])
        day = "#row-decision-" + "W6-D1".encode().hex() + " time"
        self.assertTrue(page.run(f"document.querySelector('{day}').title").startswith("Monday, November 2, 2026"),
                        "a bare date stays its own day west of UTC")
        self.assertEqual(page.run("pageErrors"), [])

    def test_oldest_inbox_link_opens_its_decision_from_either_tab(self):
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.click("[data-oldest-wait] a")
        target = "decision-" + "W6-D1".encode().hex()
        self.assertEqual((page.selected_tab(), page.selected_decision()), ("needs-tab", target))
        self.assertTrue(page.run(f"document.getElementById('{target}').checkVisibility()"))

    def copy_answer(self, page, target):
        page.click(f"{target} .answer-action .copy-prompt")
        return page.run("new Promise(resolve => setTimeout(() => resolve(window.copied)))").splitlines()

    def test_answer_copies_the_picked_option_at_its_revision_or_offers_the_text(self):
        page = self.open_page(PHONE)
        need = decision(self.state, "W5-T")
        target = "#decision-" + "W5-T".encode().hex()
        heading = f'Decision "W5-T" (revision {revision(need)}) in "Export reliability"'
        page.run("navigator.clipboard.writeText = async text => { window.copied = text; }")
        self.assertEqual(page.run(f"document.querySelectorAll('{target} .copy-prompt').length"), 1, "one answer action per decision")
        self.assertTrue(page.run(f"document.querySelector('{target} .answer-action .copy-prompt').disabled"), "no option is recommended")
        page.click(f"{target} .pick:last-of-type input")
        self.assertEqual(self.copy_answer(page, target), [heading, f'Question: "{need["question"]}"', 'I choose option 3: "Scrap"'])
        page.click(f"{target} .pick:first-of-type input")
        self.assertEqual(self.copy_answer(page, target)[::2], [heading, 'I choose option 1: "Merge"'])
        page.run("navigator.clipboard.writeText = async () => { throw new Error('denied'); }")
        page.click(f"{target} .answer-action .copy-prompt")
        manual = page.run(f"new Promise(resolve => setTimeout(() => {{ const box = document.querySelector('{target} .manual-prompt'); resolve([box.hidden, box.value]); }}))")
        self.assertFalse(manual[0])
        self.assertEqual(manual[1].splitlines()[::2], [heading, 'I choose option 1: "Merge"'])
        page.click(f"{target} .pick:last-of-type input")
        self.assertEqual(page.run(f"document.querySelector('{target} .manual-prompt').value").splitlines()[::2],
                         [heading, 'I choose option 3: "Scrap"'], "the text to copy follows the pick")
        self.assertEqual(page.run("pageErrors"), [])

    def test_a_pick_survives_a_republish_until_its_decision_changes(self):
        page = self.open_page(PHONE)
        need = decision(self.state, "W1-D2")
        target = "#decision-" + "W1-D2".encode().hex()
        page.click(f"{target} .pick:last-of-type input")
        self.republish(page, self.retitled())
        page.run("navigator.clipboard.writeText = async text => { window.copied = text; }")
        self.assertEqual(self.copy_answer(page, target)[::2],
                         [f'Decision "W1-D2" (revision {revision(need)}) in "Retitled program"', 'I choose option 2: "Five attempts"'])

        def reworded(state):
            state["title"] = "Retitled program"
            decision(state, "W1-D2")["options"][1]["effect"] = "Reworded effect."
        changed = self.changed(reworded)
        self.republish(page, changed)
        page.run("navigator.clipboard.writeText = async text => { window.copied = text; }")
        self.assertEqual(self.copy_answer(page, target)[::2],
                         [f'Decision "W1-D2" (revision {revision(decision(changed, "W1-D2"))}) in "Retitled program"',
                          'I choose option 1: "Three attempts"'], "a changed decision starts at its recommendation")

    def test_recommended_option_is_picked_and_copied_first(self):
        page = self.open_page(PHONE)
        need = decision(self.state, "W1-D2")
        page.run("navigator.clipboard.writeText = async text => { window.copied = text; }")
        copied = self.copy_answer(page, "#decision-" + "W1-D2".encode().hex())
        self.assertEqual(copied[::2], [f'Decision "W1-D2" (revision {revision(need)}) in "Export reliability"', 'I choose option 1: "Three attempts"'])


EVIDENCE = "#toggle-evidence-" + "W1".encode().hex()


def tiny_png(red):
    """A valid one-pixel PNG, so the page can load and measure it."""
    def chunk(kind, data):
        return len(data).to_bytes(4, "big") + kind + data + zlib.crc32(kind + data).to_bytes(4, "big")
    header = (1).to_bytes(4, "big") * 2 + bytes([8, 2, 0, 0, 0])
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes([0, red, 0, 0]))) + chunk(b"IEND", b"")


class PictureTests(CommandCenterCase):
    def with_pictures(self, state):
        """W3-D1 gets a three-step sequence and W6-D1's second option a picture, all served beside the page."""
        names = []
        for red in (10, 20, 30, 40):
            content = tiny_png(red)
            names.append(content_name(content, ".png"))
            (self.page_file.parent / "files").mkdir(exist_ok=True)
            (self.page_file.parent / names[-1]).write_bytes(content)
        decision(state, "W3-D1")["pictures"] = {"shape": "sequence", "images": [
            {"image": names[0], "caption": "Open export"}, {"image": names[1], "caption": "Pick a range"}, {"image": names[2]}]}
        decision(state, "W6-D1")["options"][1]["image"] = names[3]
        self.publish(state)
        return names

    def viewer(self, page):
        return page.run("""(() => { const viewer = document.querySelector('.viewer');
            return {open: viewer.open, count: viewer.querySelector('.viewer-count').textContent,
                    caption: viewer.querySelector('figcaption').textContent,
                    src: viewer.querySelector('img').getAttribute('src'), nav: !viewer.querySelector('.viewer-nav').hidden}; })()""")

    def test_a_picture_opens_larger_in_the_page_and_pages_through_its_group(self):
        names = self.with_pictures(self.state)
        page = self.open_page(PHONE)
        target = "#decision-" + "W3-D1".encode().hex()
        loaded = page.run(f"Promise.all([...document.querySelectorAll('{target} .picture img')].map(image => {{ image.loading = 'eager'; return image.decode().then(() => image.naturalWidth); }}))")
        self.assertEqual(loaded, [1, 1, 1], "the page loads its own files")
        page.click(f"{target} .picture")
        shown = self.viewer(page)
        self.assertEqual(shown, {"open": True, "count": "1 of 3", "caption": "Step 1: Open export", "src": names[0], "nav": True})
        page.click(".viewer-next")
        self.assertEqual(self.viewer(page)["caption"], "Step 2: Pick a range")
        page.click(".viewer-previous")
        page.click(".viewer-previous")
        self.assertEqual(self.viewer(page)["count"], "3 of 3", "the group wraps around")
        page.click(".viewer-close")
        self.assertFalse(self.viewer(page)["open"])

        option = "#decision-" + "W6-D1".encode().hex()
        width = page.run(f"document.querySelector('{option} .pick:last-of-type .picture').getBoundingClientRect().width")
        self.assertGreater(width, 200, "an option's picture keeps its width before its lazy image loads")
        page.click(f"{option} .pick:last-of-type .picture")
        self.assertEqual(self.viewer(page), {"open": True, "count": "", "caption": "Hide expired entries", "src": names[3], "nav": False})
        self.assertFalse(page.run(f"document.querySelector('{option} .pick:last-of-type input').checked"),
                         "opening an option's picture does not pick it")
        page.run("document.querySelector('.viewer').dispatchEvent(new MouseEvent('click', {bubbles: true}))")
        self.assertFalse(self.viewer(page)["open"], "tapping outside the picture closes it")
        self.assertEqual(page.run("pageErrors"), [])


class SendAnswerTests(CommandCenterCase):
    WAKE = "https://wake.example/hooks/coordinator"
    TARGET = "#decision-" + "W1-D2".encode().hex()

    def open_with_db(self, wake=None, refuse=False, before_load=""):
        page = self.open_page(PHONE, before_load + FAKE_DB % {"wake": json.dumps({"url": wake or self.WAKE}),
                                                               "refuse": json.dumps(refuse)})
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        return page

    def action(self, page):
        return page.run(f"""(() => {{ const action = document.querySelector('{self.TARGET} .answer-action');
            return {{sendable: action.classList.contains('can-send'), send: !action.querySelector('.send-answer').hidden,
                     wake: action.querySelector('.wake-link').hidden ? null : action.querySelector('.wake-link').href,
                     status: action.querySelector('.send-status').textContent,
                     copy: !action.querySelector('.copy-prompt').disabled}}; }})()""")

    def test_without_the_page_database_only_copy_answer_shows(self):
        page = self.open_page(PHONE)
        self.assertEqual(self.action(page), {"sendable": False, "send": False, "wake": None, "status": "", "copy": True})
        page = self.open_with_db(wake="http://wake.example/plain")
        self.assertEqual(self.action(page)["send"], False, "a wake link must be https")

    def test_send_saves_the_pick_by_decision_and_revision_then_offers_the_wake_link(self):
        page = self.open_with_db()
        self.assertEqual(self.action(page), {"sendable": True, "send": True, "wake": None, "status": "", "copy": True})
        page.click(f"{self.TARGET} .pick:last-of-type input")
        page.click(f"{self.TARGET} .send-answer")
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        need = decision(self.state, "W1-D2")
        key = f"picks/{'W1-D2'.encode().hex()}-{revision(need)}"
        self.assertEqual(page.run("storedPicks()"), {key: {"decision": "W1-D2", "revision": revision(need), "option": 2,
                                                          "label": "Five attempts"}})
        sent = self.action(page)
        self.assertEqual((sent["send"], sent["wake"], sent["copy"]), (False, self.WAKE, True))
        self.assertIn("Saved “Five attempts”", sent["status"])

        page.reload()
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        self.assertEqual(self.action(page)["wake"], self.WAKE, "a saved pick still offers the wake link after a reload")
        self.assertTrue(page.run(f"document.querySelector('{self.TARGET} .pick:last-of-type input').checked"))
        page.click(f"{self.TARGET} .pick:first-of-type input")
        self.assertEqual(self.action(page)["send"], True, "a new pick needs sending again")
        self.assertEqual(page.run("pageErrors"), [])

    def test_a_pick_cannot_change_while_its_save_is_pending(self):
        page = self.open_with_db()
        page.run("window.holdWrites = true")
        page.click(f"{self.TARGET} .pick:last-of-type input")
        page.click(f"{self.TARGET} .send-answer")
        page.click(f"{self.TARGET} .pick:first-of-type input")
        page.click(f"{self.TARGET} .send-answer")
        self.assertTrue(page.run(f"document.querySelector('{self.TARGET} .pick:last-of-type input').checked"),
                        "the pick being saved stays picked")
        page.run("window.holdWrites = false; window.releaseWrite(); new Promise(resolve => setTimeout(resolve, 50))")
        stored = page.run("storedPicks()")
        self.assertEqual([pick["label"] for pick in stored.values()], ["Five attempts"], "one save, of the shown pick")
        sent = self.action(page)
        self.assertEqual((sent["send"], sent["wake"]), (False, self.WAKE))
        page.click(f"{self.TARGET} .pick:first-of-type input")
        self.assertTrue(self.action(page)["send"], "after the save settles, a new pick can be sent")

    def test_send_appears_only_after_saved_picks_are_shown(self):
        need = decision(self.state, "W1-D2")
        saved = {f"picks/{'W1-D2'.encode().hex()}-{revision(need)}": {
            "decision": "W1-D2", "revision": revision(need), "option": 2, "label": "Five attempts"}}
        page = self.open_with_db(before_load=f"localStorage.setItem('fake-db', {json.dumps(json.dumps(saved))}); "
                                             "window.holdReads = true;")
        self.assertEqual(self.action(page), {"sendable": False, "send": False, "wake": None, "status": "", "copy": True},
                         "nothing to send while saved picks are still loading")
        page.run("window.releaseRead(); new Promise(resolve => setTimeout(resolve, 50))")
        restored = self.action(page)
        self.assertEqual((restored["sendable"], restored["send"], restored["wake"]), (True, False, self.WAKE))
        self.assertIn("Saved “Five attempts”", restored["status"])
        self.assertTrue(page.run(f"document.querySelector('{self.TARGET} .pick:last-of-type input').checked"))

    def test_send_turns_off_once_the_wake_link_is_gone_and_follows_a_new_one(self):
        page = self.open_with_db()
        page.run("window.wakeDoc = {url: 'https://wake.example/hooks/new'}")
        page.click(f"{self.TARGET} .send-answer")
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        self.assertEqual(self.action(page)["wake"], "https://wake.example/hooks/new")

        page.run("window.wakeDoc = null")
        page.click(f"{self.TARGET} .pick:first-of-type input")
        page.click(f"{self.TARGET} .send-answer")
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        self.assertEqual(self.action(page), {
            "sendable": False, "send": False, "wake": None, "copy": True,
            "status": "Send answer is off for now. Copy the answer and paste it to the coordinator instead."})
        self.assertEqual(len(page.run("storedPicks()")), 1, "nothing more is saved once the wake link is gone")
        page.click(f"{self.TARGET} .pick:last-of-type input")
        self.assertFalse(self.action(page)["send"], "a new pick does not bring Send back")
        self.assertEqual(page.run("pageErrors"), [])

    def test_a_shown_wake_link_follows_the_database_on_return_to_the_page(self):
        page = self.open_with_db()
        page.click(f"{self.TARGET} .send-answer")
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        page.run("window.wakeDoc = {url: 'https://wake.example/hooks/new'}")
        page.run(HIDE % {"hidden": "false", "state": "'visible'"} + "; new Promise(resolve => setTimeout(resolve, 50))")
        self.assertEqual(self.action(page)["wake"], "https://wake.example/hooks/new")
        page.run("window.wakeDoc = null")
        page.run(HIDE % {"hidden": "false", "state": "'visible'"} + "; new Promise(resolve => setTimeout(resolve, 50))")
        self.assertEqual(self.action(page), {"sendable": False, "send": False, "wake": None, "status": "", "copy": True})
        self.assertEqual(page.run("pageErrors"), [])

    def test_a_save_that_lands_after_send_turned_off_keeps_copy_answer(self):
        page = self.open_with_db()
        page.run("window.holdWrites = true")
        page.click(f"{self.TARGET} .send-answer")
        page.run("new Promise(resolve => (function held() { window.releaseWrite ? resolve() : setTimeout(held, 10); })())")
        page.run("window.wakeDoc = null")
        page.run(HIDE % {"hidden": "false", "state": "'visible'"} + "; new Promise(resolve => setTimeout(resolve, 50))")
        page.run("window.holdWrites = false; window.releaseWrite(); new Promise(resolve => setTimeout(resolve, 50))")
        self.assertEqual(self.action(page), {
            "sendable": False, "send": False, "wake": None, "copy": True,
            "status": "Send answer is off for now. Copy the answer and paste it to the coordinator instead."})

    def test_a_refused_save_points_to_copy_answer(self):
        page = self.open_with_db(refuse=True)
        page.click(f"{self.TARGET} .send-answer")
        page.run("new Promise(resolve => setTimeout(resolve, 50))")
        failed = self.action(page)
        self.assertEqual((failed["send"], failed["wake"], failed["copy"]), (True, None, True))
        self.assertEqual(failed["status"], "Not saved. Copy the answer and paste it to the coordinator instead.")
        self.assertEqual(page.run("storedPicks()"), {})


class ViewTests(CommandCenterCase):
    def prepare_view(self, page):
        page.click("#work-tab")
        page.run("document.querySelector('.collapsible.planned details').querySelector('summary').click()")
        page.click(EVIDENCE)

    def assert_view(self, page):
        self.assertEqual(page.selected_tab(), "work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])
        self.assertFalse(page.run("document.querySelector('.collapsible.planned details').open"))
        self.assertTrue(page.run(f"document.querySelector('{EVIDENCE}').parentElement.open"))

    def test_republish_keeps_tab_sections_and_evidence(self):
        page = self.open_page()
        self.prepare_view(page)
        self.republish(page, self.retitled())
        self.assertIn("Retitled program", page.text())
        self.assert_view(page)

    def test_republish_keeps_the_selected_decision(self):
        page = self.open_page()
        target = page.run("document.querySelectorAll('.inbox-row')[3].getAttribute('aria-controls')")
        page.click(f'.inbox-row[aria-controls="{target}"]')
        self.republish(page, self.retitled())
        self.assertIn("Retitled program", page.text())
        self.assertEqual(page.selected_decision(), target)
        self.assertTrue(page.run(f"document.getElementById({json.dumps(target)}).checkVisibility()"))

    def test_removed_decision_falls_back_to_the_first_open_decision(self):
        page = self.open_page()
        rows = page.run("[...document.querySelectorAll('.inbox-row')].map(row => row.getAttribute('aria-controls'))")
        page.click(f'.inbox-row[aria-controls="{rows[2]}"]')
        self.republish(page, self.changed(lambda state: state["decisions"].pop(2)))
        self.assertEqual(page.selected_decision(), rows[0])
        self.assertTrue(page.run(f"document.getElementById({json.dumps(rows[0])}).checkVisibility()"))
        self.assertEqual(page.run("document.querySelectorAll('.inbox-row[tabindex=\"0\"]').length"), 1)

    def test_last_decisions_removed_leaves_a_working_empty_state(self):
        page = self.open_page()
        self.republish(page, self.changed(lambda state: state.update(decisions=[], revisits=[])))
        self.assertIn("Your Inbox is empty", page.text())
        self.assertIsNone(page.selected_decision())
        page.click("#work-tab")
        self.assertEqual(page.visible_panels(), ["work-panel"])

    def test_settled_details_stay_open_across_republish_on_desktop_and_phone(self):
        rationale = "The shared table already has the required controls."
        basis = "The shared component supports every export history column."
        state = self.changed(lambda state: state.update(
            decisions=[row for row in state["decisions"] if row["status"] in {"answered", "resolved"}]))
        decision(state, "W5-D2").update(rationale=rationale, basis=basis)
        self.publish(state)
        target = "decision-" + "W5-D2".encode().hex()
        summary = f"#{target} .decision-details > summary"
        for size, selector in ((DESKTOP, f"#row-{target}"), (PHONE, "#toggle-resolved-heading")):
            with self.subTest(size=size):
                page = self.open_page(size)
                self.assertIn("Your Inbox is empty", page.text())
                page.click(selector)
                self.assertIn(rationale, page.text())
                self.assertNotIn(basis, page.text())
                self.assertTrue(page.run(f"document.querySelector('{summary}').checkVisibility()"))
                self.assertIn("Technical details", page.run(f"document.querySelector('{summary}').innerText"))
                page.click(summary)
                self.assertIn(basis, page.text())
                self.republish(page, state | {"title": "Republished decisions"})
                self.assertIn("Republished decisions", page.text())
                self.assertIn(basis, page.text())
                self.publish(state)

    def test_resolved_selection_stays_selected_in_its_new_group(self):
        page = self.open_page()
        target = "decision-" + "W1-D2".encode().hex()
        page.click(f'.inbox-row[aria-controls="{target}"]')

        def resolve(state):
            need = next(row for row in state["decisions"] if row["id"] == "W1-D2")
            need.update(status="resolved", answer="Three retries", basis="Matches the recorded policy.")
        self.republish(page, self.changed(resolve))
        self.assertEqual(page.selected_decision(), target)
        self.assertEqual(page.run("document.querySelector('.inbox-row[aria-selected=true]').closest('.inbox-group').querySelector('.inbox-group-title').innerText").split()[0:2], ["Coordinator", "decided"])

    def test_removed_section_keeps_the_others_as_saved(self):
        page = self.open_page()
        self.prepare_view(page)

        def finish_planned(state):
            state["work"] = [row for row in state["work"] if row["state"] != "planned"]
            for need in state["decisions"]:
                need["blocks"] = [entry for entry in need.get("blocks", []) if entry["id"] != "W4"]
        self.republish(page, self.changed(finish_planned))
        self.assertEqual(page.run("document.querySelectorAll('.collapsible.planned').length"), 0)
        self.assertTrue(page.run(f"document.querySelector('{EVIDENCE}').parentElement.open"))
        self.assertEqual(page.selected_tab(), "work-tab")

    def test_leaving_the_tab_saves_the_view(self):
        page = self.open_page()
        page.click("#work-tab")
        page.set_visible(False)
        saved = page.run(f"JSON.parse(sessionStorage.getItem({json.dumps(VIEW_KEY)})).tab")
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
                        f"sessionStorage.setItem({json.dumps(VIEW_KEY)}, {json.dumps(saved)}); }}")
                page = self.open_page(before_load=seed)
                self.assertEqual(page.selected_tab(), "needs-tab")
                self.assertEqual(page.run("pageErrors"), [])
                page.click("#work-tab")
                page.reload()
                self.assertEqual(page.selected_tab(), "work-tab")

    def test_page_works_when_storage_is_unavailable(self):
        full_storage = "Storage.prototype.setItem = () => { throw new DOMException('full', 'QuotaExceededError'); };"
        for storage_failure in (BLOCK_STORAGE, full_storage):
            with self.subTest(storage_failure=storage_failure):
                page = self.open_page(before_load=storage_failure)
                self.prepare_view(page)
                page.set_visible(False)
                page.set_visible(True)
                self.republish(page, self.retitled())
                self.assertIn("Retitled program", page.text())
                self.assertEqual(page.selected_tab(), "needs-tab")
                self.assertEqual(page.run("pageErrors"), [])


class ScrollTests(CommandCenterCase):
    def long_state(self):
        def lengthen(state):
            for index in range(10, 45):
                state["work"].append(self.outcome(f"W{index}", ("building", "planned", "in-review")[index % 3], title=f"Extra work {index}"))
        self.state = self.changed(lengthen)
        self.publish(self.state)

    def read_in_work(self, page, identity, top=120):
        page.click("#work-tab")
        page.bring_into_view(self.card(identity), top)

    def lane_of(self, page, identity):
        return page.run(f"document.querySelector({json.dumps(self.card(identity))}).closest('.collapsible').className")

    def test_phone_reading_position_follows_its_card_when_content_is_added_above(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W20")
        before = page.top_of(self.card("W20"))

        def add_above(state):
            for index in range(50, 54):
                state["work"].insert(0, self.outcome(f"W{index}", "planned", title=f"New work {index}"))
        self.republish(page, self.changed(add_above))
        self.assertIn("New work 50", page.text())
        self.assertAlmostEqual(page.top_of(self.card("W20")), before, delta=1)

    def test_phone_reading_position_moves_to_a_neighbour_when_its_card_is_removed(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W20", top=0)
        neighbour = page.run(f"document.querySelector({json.dumps(self.card('W20'))}).nextElementSibling.id")
        before = page.top_of("#" + neighbour)

        def remove(state):
            state["work"] = [row for row in state["work"] if row["id"] != "W20"]
        self.republish(page, self.changed(remove))
        self.assertEqual(page.run(f"document.querySelectorAll({json.dumps(self.card('W20'))}).length"), 0)
        self.assertAlmostEqual(page.top_of("#" + neighbour), before, delta=1)

    def test_reading_position_skips_a_card_that_moved_into_a_collapsed_section(self):
        self.long_state()
        page = self.open_page(PHONE)
        page.click("#toggle-stage-planned")
        self.read_in_work(page, "W20", top=0)
        neighbour = page.run(f"document.querySelector({json.dumps(self.card('W20'))}).nextElementSibling.id")
        before = page.top_of("#" + neighbour)
        self.republish(page, self.changed(lambda state: self.work(state, "W20").update(state="planned", title="Parked card")))
        self.assertAlmostEqual(page.top_of("#" + neighbour), before, delta=1)

    def test_every_anchor_gone_clamps_to_the_page_that_remains(self):
        self.long_state()
        page = self.open_page(PHONE)
        self.read_in_work(page, "W35")
        self.republish(page, self.changed(lambda state: state.update(
            work=[self.outcome("W2", "building")], decisions=[], revisits=[], landings=[], waits=[])))
        self.assertEqual(page.run("document.querySelectorAll('.work').length"), 1)
        self.assertLessEqual(page.run("scrollY + innerHeight"), page.run("document.documentElement.scrollHeight"))
        self.assertEqual(page.selected_tab(), "work-tab")

    def wide_board(self):
        self.state["work"] += [dict(copy.deepcopy(self.work(self.state, "W3")), id=f"X{index}", state=state)
                               for index, state in enumerate(("done", "scrapped"))]
        self.state["work"].append(self.outcome("X2", "scrapped"))
        self.publish(self.state)

    def test_board_keeps_its_lane_in_place(self):
        self.wide_board()
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.run("document.querySelector('.stage-board').scrollLeft = 200")
        lane = ".stage-board .collapsible.in-review"
        before = page.run(f"document.querySelector('{lane}').getBoundingClientRect().left")
        self.republish(page, self.changed(lambda state: state["work"].append(self.outcome("X9", "unknown", unknownReason="Forge unavailable"))))
        self.assertEqual(page.run("document.querySelectorAll('.work').length"), 11)
        self.assertGreater(page.run("document.querySelector('.stage-board').scrollLeft"), 0)
        self.assertAlmostEqual(page.run(f"document.querySelector('{lane}').getBoundingClientRect().left"), before, delta=1)

    def test_board_position_survives_a_republish_from_the_other_tab(self):
        self.wide_board()
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.run("document.querySelector('.stage-board').scrollLeft = 200")
        page.click("#needs-tab")
        self.republish(page, self.retitled())
        self.assertIn("Retitled program", page.text())
        page.click("#work-tab")
        self.assertEqual(page.run("document.querySelector('.stage-board').scrollLeft"), 200)

    def test_decision_list_keeps_its_row_when_a_decision_is_added_above_it(self):
        self.state["decisions"] += [dict(copy.deepcopy(self.state["decisions"][0]), id=f"N{index}", question=f"Extra decision {index}") for index in range(20)]
        self.publish(self.state)
        page = self.open_page(DESKTOP)
        page.run("document.querySelector('.inbox-list').scrollTop = 400")
        row = "#row-decision-" + "N10".encode().hex()
        before = page.top_of(row)

        def add_above(state):
            state["decisions"].insert(0, dict(copy.deepcopy(state["decisions"][0]), id="NEWEST", question="A newer decision"))
        self.republish(page, self.changed(add_above))
        self.assertIn("A newer decision", page.text())
        self.assertAlmostEqual(page.top_of(row), before, delta=1)

    def test_settled_history_keeps_its_row_when_a_decision_is_added_above_it(self):
        for identity, heading in (("W5-D2", "resolved-list"), ("W0-D1", "answered-list")):
            with self.subTest(group=heading):
                original = decision(self.state, identity)
                state = self.changed(lambda state: state["decisions"].extend(
                    [dict(original, id=f"HISTORY-{i}", question=f"History decision {i}?") for i in range(24)]))
                self.publish(state)
                page = self.open_page(DESKTOP)
                target = "decision-" + "HISTORY-15".encode().hex()
                row = f"#row-{target}"
                page.run(f"document.querySelector('{row}').scrollIntoView({{block: 'center'}})")
                page.click(row)
                before = page.top_of(row) - page.top_of(f"#{heading}")
                self.assertLess(before, 300)

                state["decisions"].insert(0, dict(original, id="HISTORY-NEW", question="New history decision?"))
                self.republish(page, state)
                self.assertIn("New history decision?", page.text())
                self.assertEqual(page.selected_decision(), target)
                self.assertAlmostEqual(page.top_of(row) - page.top_of(f"#{heading}"), before, delta=1)

    def test_desktop_page_stays_put_when_a_card_moves_to_another_lane(self):
        self.long_state()
        page = self.open_page(DESKTOP)
        page.click("#work-tab")
        page.run("document.scrollingElement.scrollTop = 1500")
        mover = page.run("[...document.querySelectorAll('.collapsible.planned .work')].find(card => card.getBoundingClientRect().bottom > 0).id")
        watched = page.run("[...document.querySelectorAll('.collapsible.in-review .work')].find(card => card.getBoundingClientRect().top > 0).id")
        before = page.top_of("#" + watched)
        identity = bytes.fromhex(mover.removeprefix("work-card-")).decode()
        landed = {"state": "landed", "layers": [{"id": f"{identity}-L1", "branch": "landed", "status": "merged", "url": "https://example.test/pull/9"}]}
        self.republish(page, self.changed(lambda state: self.work(state, identity).update(landed)))
        self.assertIn("finished", page.run(f"document.getElementById({json.dumps(mover)}).closest('.collapsible').className"))
        self.assertAlmostEqual(page.top_of("#" + watched), before, delta=1)


if __name__ == "__main__":
    unittest.main()
