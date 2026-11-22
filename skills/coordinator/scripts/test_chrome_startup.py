"""Unit tests for headless Chrome startup retries, cleanup, and serialization."""

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
        self.closed = False
        self.handshake_timeouts = []
        self.calls.append(self)

    def handshake(self, timeout=center.REPLY_TIMEOUT):
        self.handshake_timeouts.append(timeout)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def close(self):
        self.closed = True


class StartChromeTests(unittest.TestCase):
    def test_retries_transient_startup_failures_and_cleans_up_failed_attempts(self):
        calls = []
        outcomes = [
            TimeoutError("Browser.getVersion (pid=101, alive)"),
            ConnectionError("Chrome closed its debugging pipe (exit=1)"),
            {"product": "Chrome/159.0"},
        ]

        def launcher(executable, profile):
            return FakeChrome(executable, profile, outcomes, calls)

        browser, profile = center.start_chrome(
            "/usr/bin/google-chrome",
            timeouts=(12, 15, 20),
            launcher=launcher,
        )
        self.addCleanup(profile.cleanup)

        self.assertIs(browser, calls[2])
        self.assertEqual([c.handshake_timeouts for c in calls], [[12], [15], [20]])
        self.assertTrue(calls[0].closed)
        self.assertTrue(calls[1].closed)
        self.assertFalse(calls[2].closed)
        self.assertFalse(calls[0].profile.exists())
        self.assertFalse(calls[1].profile.exists())
        self.assertTrue(calls[2].profile.exists())

    def test_raises_last_error_when_all_startup_attempts_fail(self):
        calls = []
        outcomes = [
            TimeoutError("attempt 1 timed out"),
            TimeoutError("attempt 2 timed out"),
        ]

        def launcher(executable, profile):
            return FakeChrome(executable, profile, outcomes, calls)

        with self.assertRaisesRegex(TimeoutError, "attempt 2 timed out"):
            center.start_chrome(
                "/usr/bin/google-chrome",
                timeouts=(12, 20),
                launcher=launcher,
            )

        self.assertEqual(len(calls), 2)
        self.assertTrue(all(c.closed for c in calls))
        self.assertTrue(all(not c.profile.exists() for c in calls))

    def test_does_not_retry_permanent_launch_error(self):
        profiles = []

        def launcher(executable, profile):
            profiles.append(Path(profile))
            raise FileNotFoundError(executable)

        with self.assertRaises(FileNotFoundError):
            center.start_chrome(
                "/missing/chrome",
                timeouts=(12, 15, 20),
                launcher=launcher,
            )

        self.assertEqual(len(profiles), 1)
        self.assertFalse(profiles[0].exists())

    def test_serializes_concurrent_startups_across_processes_using_test_cache(self):
        script_dir = str(Path(center.__file__).resolve().parent)
        worker = (
            "import json, sys, time\n"
            f"sys.path.insert(0, {script_dir!r})\n"
            "import test_command_center as center\n"
            "events = []\n"
            "class HoldChrome:\n"
            "    def __init__(self, exe, profile): pass\n"
            "    def handshake(self, timeout=20):\n"
            "        events.append(('enter', time.monotonic()))\n"
            "        time.sleep(0.25)\n"
            "        events.append(('exit', time.monotonic()))\n"
            "    def close(self): pass\n"
            "browser, profile = center.start_chrome('/usr/bin/chrome', timeouts=(5,), launcher=HoldChrome)\n"
            "profile.cleanup()\n"
            "print(json.dumps(events))\n"
        )
        with tempfile.TemporaryDirectory() as cache_dir:
            env = {**os.environ, "_SREESTACK_TEST_CACHE": cache_dir}
            first = subprocess.Popen([sys.executable, "-c", worker], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            second = subprocess.Popen([sys.executable, "-c", worker], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out1, err1 = first.communicate(timeout=10)
            out2, err2 = second.communicate(timeout=10)
            self.assertEqual(first.returncode, 0, err1)
            self.assertEqual(second.returncode, 0, err2)
            (_, start1), (_, end1) = json.loads(out1)
            (_, start2), (_, end2) = json.loads(out2)
            # Intervals must not overlap: one exits before the other enters.
            earlier_end, later_start = (end1, start2) if start1 <= start2 else (end2, start1)
            self.assertGreaterEqual(later_start, earlier_end - 0.01)

    def test_chrome_isolates_stdin_enables_stderr_logging_and_reports_alive_diagnostic(self):
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

    def test_teardown_handles_partial_setup_and_resets_module_globals(self):
        saved = (center.browser, center.browser_profile, center.site, center.server)
        self.addCleanup(
            lambda: (
                setattr(center, "browser", saved[0]),
                setattr(center, "browser_profile", saved[1]),
                setattr(center, "site", saved[2]),
                setattr(center, "server", saved[3]),
            )
        )
        center.browser = None
        center.browser_profile = None
        center.site = None
        center.server = None
        center.tearDownModule()
        self.assertIsNone(center.browser)
        self.assertIsNone(center.browser_profile)
        self.assertIsNone(center.site)
        self.assertIsNone(center.server)


if __name__ == "__main__":
    unittest.main()
