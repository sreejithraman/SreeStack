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

from render_dashboard import render
from render_dashboard import ISO_TIME, revision
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

    def test_resolved_selection_stays_selected_in_its_new_group(self):
        page = self.open_page()
        target = "decision-" + "W1-D2".encode().hex()
        page.click(f'.inbox-row[aria-controls="{target}"]')

        def resolve(state):
            need = next(row for row in state["decisions"] if row["id"] == "W1-D2")
            need.update(status="resolved", answer="Three retries", basis="Matches the recorded policy.")
        self.republish(page, self.changed(resolve))
        self.assertEqual(page.selected_decision(), target)
        self.assertEqual(page.run("document.querySelector('.inbox-row[aria-selected=true]').closest('.inbox-group').querySelector('.inbox-group-title').innerText").split()[0:2], ["Chief", "decided"])

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
