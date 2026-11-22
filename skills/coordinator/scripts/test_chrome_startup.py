"""Unit tests for headless Chrome startup retries, cleanup, and serialization."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import test_command_center as center


class FakeChrome:
    """Minimal stand-in for Chrome during startup handshake tests."""

    def __init__(self, executable, profile, outcomes, calls):
        self.executable = executable
        self.profile = Path(profile)
        self.outcomes = outcomes
        self.calls = calls
        self.close_calls = []
        self.handshake_timeouts = []
        self.calls.append(self)

    def handshake(self, timeout=center.REPLY_TIMEOUT):
        self.handshake_timeouts.append(timeout)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def close(self, force=False):
        self.close_calls.append(force)


class StartChromeTests(unittest.TestCase):
    def setUp(self):
        # Isolate from check.py's live cache/lock so unit tests never contend with real Chrome launches.
        env_patch = mock.patch.dict(os.environ, {}, clear=False)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        os.environ.pop("_SREESTACK_TEST_CACHE", None)

    def test_retries_transient_startup_failures_force_kills_and_records_notes(self):
        calls = []
        outcomes = [
            TimeoutError("Browser.getVersion (pid=101, alive)"),
            ConnectionError("Chrome closed its debugging pipe (exit=1)"),
            {"product": "Chrome/159.0"},
        ]

        def launcher(executable, profile):
            return FakeChrome(executable, profile, outcomes, calls)

        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as cache_dir:
            os.environ["_SREESTACK_TEST_CACHE"] = cache_dir
            with contextlib.redirect_stderr(stderr):
                browser, profile = center.start_chrome(
                    "/usr/bin/google-chrome",
                    timeouts=(10, 12, 15),
                    launcher=launcher,
                )
            self.addCleanup(profile.cleanup)
            notes = (Path(cache_dir) / "notes.log").read_text(encoding="utf-8")

        self.assertIs(browser, calls[2])
        self.assertEqual([c.handshake_timeouts for c in calls], [[10], [12], [15]])
        self.assertEqual(calls[0].close_calls, [True])
        self.assertEqual(calls[1].close_calls, [True])
        self.assertEqual(calls[2].close_calls, [])
        self.assertFalse(calls[0].profile.exists())
        self.assertFalse(calls[1].profile.exists())
        self.assertTrue(calls[2].profile.exists())
        self.assertIn("attempt 1/3 failed", notes)
        self.assertIn("attempt 2/3 failed", notes)
        self.assertIn("recovered on attempt 3/3", notes)

    def test_clean_first_attempt_leaves_no_startup_notes(self):
        calls = []
        outcomes = [{"product": "Chrome/159.0"}]

        def launcher(executable, profile):
            return FakeChrome(executable, profile, outcomes, calls)

        with tempfile.TemporaryDirectory() as cache_dir:
            os.environ["_SREESTACK_TEST_CACHE"] = cache_dir
            browser, profile = center.start_chrome(
                "/usr/bin/google-chrome",
                timeouts=(10, 15),
                launcher=launcher,
            )
            self.addCleanup(profile.cleanup)
            self.assertFalse((Path(cache_dir) / "notes.log").exists())
        self.assertIs(browser, calls[0])

    def test_raises_last_error_when_all_startup_attempts_fail(self):
        calls = []
        outcomes = [
            TimeoutError("attempt 1 timed out"),
            TimeoutError("attempt 2 timed out"),
        ]

        def launcher(executable, profile):
            return FakeChrome(executable, profile, outcomes, calls)

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(TimeoutError, "attempt 2 timed out"):
                center.start_chrome(
                    "/usr/bin/google-chrome",
                    timeouts=(10, 15),
                    launcher=launcher,
                )

        self.assertEqual(len(calls), 2)
        self.assertEqual([c.close_calls for c in calls], [[True], [True]])
        self.assertTrue(all(not c.profile.exists() for c in calls))

    def test_does_not_retry_permanent_launch_or_non_transient_handshake_error(self):
        profiles = []

        def missing_launcher(executable, profile):
            profiles.append(Path(profile))
            raise FileNotFoundError(executable)

        with self.assertRaises(FileNotFoundError):
            center.start_chrome("/missing/chrome", timeouts=(10, 15), launcher=missing_launcher)
        self.assertEqual(len(profiles), 1)
        self.assertFalse(profiles[0].exists())

        calls = []
        outcomes = [RuntimeError("Browser.getVersion: unsupported")]

        def runtime_launcher(executable, profile):
            return FakeChrome(executable, profile, outcomes, calls)

        with self.assertRaisesRegex(RuntimeError, "unsupported"):
            center.start_chrome("/usr/bin/google-chrome", timeouts=(10, 15), launcher=runtime_launcher)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].close_calls, [True])
        self.assertFalse(calls[0].profile.exists())

    def test_serializes_concurrent_startups_across_processes_using_test_cache(self):
        script_dir = str(Path(center.__file__).resolve().parent)
        worker = (
            "import json, pathlib, sys, time\n"
            f"sys.path.insert(0, {script_dir!r})\n"
            "import test_command_center as center\n"
            "ready_dir = pathlib.Path(sys.argv[1])\n"
            "worker_id = sys.argv[2]\n"
            "(ready_dir / f'{worker_id}.ready').write_text('1')\n"
            "deadline = time.monotonic() + 5\n"
            "while len(list(ready_dir.glob('*.ready'))) < 2 and time.monotonic() < deadline:\n"
            "    time.sleep(0.01)\n"
            "events = []\n"
            "class HoldChrome:\n"
            "    def __init__(self, exe, profile): pass\n"
            "    def handshake(self, timeout=20):\n"
            "        events.append(('enter', time.monotonic()))\n"
            "        time.sleep(0.25)\n"
            "        events.append(('exit', time.monotonic()))\n"
            "    def close(self, force=False): pass\n"
            "browser, profile = center.start_chrome('/usr/bin/chrome', timeouts=(5,), launcher=HoldChrome)\n"
            "profile.cleanup()\n"
            "print(json.dumps(events))\n"
        )
        with tempfile.TemporaryDirectory() as cache_dir, tempfile.TemporaryDirectory() as ready_dir:
            env = {**os.environ, "_SREESTACK_TEST_CACHE": cache_dir}
            procs = [
                subprocess.Popen(
                    [sys.executable, "-c", worker, ready_dir, str(i)],
                    env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                )
                for i in (1, 2)
            ]

            def reap():
                for proc in procs:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()

            self.addCleanup(reap)
            outputs = []
            for proc in procs:
                out, err = proc.communicate(timeout=10)
                self.assertEqual(proc.returncode, 0, err)
                outputs.append(json.loads(out))

            (_, start1), (_, end1) = outputs[0]
            (_, start2), (_, end2) = outputs[1]
            earlier_end, later_start = (end1, start2) if start1 <= start2 else (end2, start1)
            self.assertGreaterEqual(later_start, earlier_end - 0.01)

    def test_chrome_stdin_logging_diagnostics_broken_pipe_and_idempotent_close(self):
        with tempfile.TemporaryDirectory() as profile:
            fake_proc = mock.Mock()
            fake_proc.pid = 4242
            fake_proc.poll.return_value = None
            fake_proc.wait.return_value = 0
            with mock.patch.object(center.subprocess, "Popen", return_value=fake_proc) as popen:
                chrome = center.Chrome("/usr/bin/google-chrome", profile)
                self.addCleanup(chrome.close)
                args, kwargs = popen.call_args
                cmd = args[0]
                self.assertEqual(kwargs.get("stdin"), subprocess.DEVNULL)
                self.assertIn("--enable-logging=stderr", cmd)
                self.assertIn("--log-level=2", cmd)
                self.assertEqual(chrome._diagnostic(), " (pid=4242, alive)")

                fake_proc.poll.return_value = 139
                chrome.stderr_path.write_text("line1\nfatal startup error\n", encoding="utf-8")
                self.assertIn("exit=139", chrome._diagnostic())
                self.assertIn("fatal startup error", chrome._diagnostic())

                with mock.patch.object(center.os, "write", side_effect=BrokenPipeError("broken")):
                    with self.assertRaisesRegex(BrokenPipeError, r"(?s)exit=139.*fatal startup error"):
                        chrome.handshake(timeout=1)

                # Force-close kills immediately instead of waiting on SIGTERM, closes both fds, and is idempotent.
                real_close = os.close
                closed_fds = []

                def flaky_close(fd):
                    closed_fds.append(fd)
                    real_close(fd)
                    if len(closed_fds) == 1:
                        raise OSError("already closed")

                with mock.patch.object(center.os, "close", side_effect=flaky_close):
                    chrome.close(force=True)
                fake_proc.kill.assert_called_once()
                fake_proc.terminate.assert_not_called()
                self.assertEqual(len(closed_fds), 2)
                self.assertIsNone(chrome.commands)
                self.assertIsNone(chrome.replies)
                # Second close is a safe no-op for descriptors.
                chrome.close()

    def test_teardown_and_setup_cleanup_isolate_errors_and_reset_globals(self):
        saved = (center.browser, center.browser_profile, center.site, center.server)
        self.addCleanup(
            lambda: (
                setattr(center, "browser", saved[0]),
                setattr(center, "browser_profile", saved[1]),
                setattr(center, "site", saved[2]),
                setattr(center, "server", saved[3]),
            )
        )

        # Partial setup (only browser + profile) cleans both and clears globals.
        partial_browser = mock.Mock()
        partial_profile = mock.Mock()
        center.browser = partial_browser
        center.browser_profile = partial_profile
        center.site = None
        center.server = None
        center.tearDownModule()
        partial_browser.close.assert_called_once()
        partial_profile.cleanup.assert_called_once()
        self.assertIsNone(center.browser)
        self.assertIsNone(center.browser_profile)

        # Error in server.shutdown still closes server socket, site, browser, and profile and resets globals.
        failing_server = mock.Mock()
        failing_server.shutdown.side_effect = RuntimeError("shutdown boom")
        full_site = mock.Mock()
        full_browser = mock.Mock()
        full_profile = mock.Mock()
        center.server = failing_server
        center.site = full_site
        center.browser = full_browser
        center.browser_profile = full_profile
        with self.assertRaisesRegex(RuntimeError, "shutdown boom"):
            center.tearDownModule()
        failing_server.server_close.assert_called_once()
        full_site.cleanup.assert_called_once()
        full_browser.close.assert_called_once()
        full_profile.cleanup.assert_called_once()
        self.assertEqual((center.server, center.site, center.browser, center.browser_profile), (None, None, None, None))

        # setUpModule cleans up browser + profile if HTTP server creation fails.
        setup_browser = mock.Mock()
        setup_profile = mock.Mock()
        with (
            mock.patch.object(center, "chrome_path", return_value="/usr/bin/google-chrome"),
            mock.patch.object(center, "start_chrome", return_value=(setup_browser, setup_profile)),
            mock.patch.object(center, "ThreadingHTTPServer", side_effect=OSError("bind failed")),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            with self.assertRaisesRegex(OSError, "bind failed"):
                center.setUpModule()
        setup_browser.close.assert_called_once()
        setup_profile.cleanup.assert_called_once()
        self.assertEqual((center.server, center.site, center.browser, center.browser_profile), (None, None, None, None))


if __name__ == "__main__":
    unittest.main()
