import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import break_glass as bg


def quiet_plane(mode):
    idle = {"running": 0, "reserved": 0, "warm": 0}
    return {
        "daemon": {"health": "running", "mode": mode},
        "leases": [], "waiting": [], "installs": [], "queueDepth": 0, "physicalQueueDepth": 0,
        "capacity": {"ios": dict(idle), "android": dict(idle), "global": dict(idle)},
    }


AGENT_DEVICE_DAEMON = "5733 /usr/local/bin/node /lib/node_modules/agent-device/dist/src/internal/daemon.js --simlock-home=/Users/x/.simlock"


def fake_read(planes=None, whoami="Role:      admin\n", processes=AGENT_DEVICE_DAEMON):
    planes = planes or {"--local": quiet_plane("worker"), "--gateway": quiet_plane("gateway")}

    def read(*argv):
        if argv[0] == "simlock" and argv[1] == "whoami":
            return whoami
        if argv[0] == "simlock":
            return json.dumps(planes[argv[1]])
        if argv[0].endswith("launchctl"):
            return "\tstate = running\n\tpid = 14788\n"
        if argv[0].endswith("/ps"):
            return processes + "\n"
        if argv[0].endswith("/top"):
            return "CPU usage: 10.0% user, 5.0% sys, 85.0% idle\n"
        if argv[0].endswith("sysctl"):
            return "1\n"
        raise AssertionError(argv)

    return read


class StateCase(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        state = Path(directory.name) / "state"
        for name, value in (("STATE", state), ("CLAIM", state / "claim"), ("OWNER", state / "claim/owner.json"), ("LOG", state / "log.jsonl"), ("LOCK", state / "lock")):
            patcher = mock.patch.object(bg, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def log(self, event, age=0, **details):
        bg.STATE.mkdir(exist_ok=True)
        with bg.LOG.open("a") as log:
            log.write(json.dumps({"at": int(time.time() - age), "event": event, "thread": "t", **details}) + "\n")


class Claim(StateCase):
    def test_second_session_cannot_claim(self):
        bg.take_claim("a", time.time())
        with self.assertRaises(FileExistsError):
            bg.take_claim("b", time.time())

    def test_stale_claim_can_be_replaced(self):
        bg.take_claim("a", time.time() - bg.STALE_CLAIM_SECONDS - 1)
        self.assertEqual(bg.take_claim("b", time.time())["thread"], "b")

    def test_other_errors_are_not_read_as_another_owner(self):
        bg.STATE.mkdir()
        bg.STATE.chmod(0o500)
        self.addCleanup(bg.STATE.chmod, 0o700)
        with self.assertRaises(PermissionError):
            bg.take_claim("a", time.time())

    def test_a_contender_that_read_a_stale_age_cannot_steal_a_fresh_claim(self):
        bg.take_claim("a", time.time() - bg.STALE_CLAIM_SECONDS - 1)
        bg.take_claim("b", time.time())
        with self.assertRaises(FileExistsError):
            bg.take_claim("c", time.time())
        self.assertEqual(bg.owner()["thread"], "b")

    def test_ownerless_claim_goes_stale_by_directory_age(self):
        bg.STATE.mkdir()
        bg.CLAIM.mkdir()
        old = time.time() - bg.STALE_CLAIM_SECONDS - 1
        os.utime(bg.CLAIM, (old, old))
        self.assertEqual(bg.take_claim("b", time.time())["thread"], "b")

    def test_only_the_owner_releases(self):
        bg.take_claim("a", time.time())
        with self.assertRaises(bg.Refused):
            bg.release_claim("b")
        self.assertTrue(bg.CLAIM.exists())


class Log(StateCase):
    def test_empty_log_allows_a_restart(self):
        self.assertIsNone(bg.refusal(time.time()))

    def test_recent_restart_refuses(self):
        self.log("restart-attempt", age=3600)
        self.log("finished", age=3500, result="acquired")
        self.assertIn("6 hours", bg.refusal(time.time()))

    def test_old_restart_allows(self):
        self.log("restart-attempt", age=bg.RESTART_SPACING_SECONDS + 10)
        self.log("finished", age=bg.RESTART_SPACING_SECONDS + 5, result="acquired")
        self.assertIsNone(bg.refusal(time.time()))

    def test_failed_restart_refuses_until_cleared(self):
        self.log("restart-attempt", age=bg.RESTART_SPACING_SECONDS + 10)
        self.log("finished", age=bg.RESTART_SPACING_SECONDS + 5, result="failed")
        self.assertIn("clear", bg.refusal(time.time()))
        self.log("cleared")
        self.assertIsNone(bg.refusal(time.time()))

    def test_owner_that_died_after_the_kill_counts_as_failed(self):
        self.log("restart-attempt", age=bg.RESTART_SPACING_SECONDS + 10)
        self.assertIn("clear", bg.refusal(time.time()))

    def test_abort_after_an_attempt_still_refuses(self):
        self.log("restart-attempt", age=bg.RESTART_SPACING_SECONDS + 10)
        self.log("aborted", age=bg.ABORT_SPACING_SECONDS + 10, reason="crash")
        self.assertIn("clear", bg.refusal(time.time()))

    def test_malformed_log_refuses_and_leaves_no_claim(self):
        bg.STATE.mkdir()
        bg.LOG.write_text('{"at": 1, "event"\n')
        with self.assertRaises(bg.Refused):
            bg.take_claim("a", time.time())
        self.assertFalse(bg.CLAIM.exists())

    def test_recent_abort_refuses(self):
        self.log("aborted", age=60, reason="silent session")
        self.assertIn("aborted", bg.refusal(time.time()))


class Gate(StateCase):
    def gate(self, **read_options):
        with mock.patch.object(bg, "read", fake_read(**read_options)), mock.patch.object(bg, "is_service", return_value=True):
            return bg.gate(0)

    def test_quiet_machine_passes_with_idle_agent_device_daemons(self):
        self.assertTrue(self.gate()["go"])

    def test_each_busy_signal_fails(self):
        for field, value in (("leases", [{}]), ("waiting", [{}]), ("installs", [{}]), ("queueDepth", 1), ("physicalQueueDepth", 1)):
            with self.subTest(field):
                plane = quiet_plane("worker") | {field: value}
                self.assertFalse(self.gate(planes={"--local": plane, "--gateway": quiet_plane("gateway")})["go"])

    def test_warm_device_fails(self):
        plane = quiet_plane("gateway")
        plane["capacity"]["ios"]["warm"] = 1
        self.assertFalse(self.gate(planes={"--local": quiet_plane("worker"), "--gateway": plane})["go"])

    def test_booted_simulator_fails(self):
        self.assertFalse(self.gate(processes="900 /sbin/launchd_sim bootstrap")["go"])

    def test_idle_simlock_processes_pass(self):
        for row in ("902 /usr/bin/xcrun simctl --set /tmp/devices list -j", "903 /usr/bin/xcrun simctl list devices"):
            with self.subTest(row):
                self.assertTrue(self.gate(processes=row)["go"])

    def test_active_drivers_fail(self):
        for row in ("904 /usr/bin/xcrun simctl --set /tmp/devices boot ABC", "905 node /bin/agent-device open --platform ios"):
            with self.subTest(row):
                self.assertFalse(self.gate(processes=row)["go"])

    def test_empty_process_list_fails(self):
        self.assertFalse(self.gate(processes="")["go"])

    def test_high_cpu_fails(self):
        def busy(*argv):
            if argv[0].endswith("/top"):
                return "CPU usage: 50.0% user, 5.0% sys, 45.0% idle\n"
            return fake_read()(*argv)

        with mock.patch.object(bg, "read", busy), mock.patch.object(bg, "is_service", return_value=True):
            self.assertFalse(bg.gate(0)["go"])

    def test_memory_pressure_fails(self):
        def pressed(*argv):
            return "2\n" if argv[0].endswith("sysctl") else fake_read()(*argv)

        with mock.patch.object(bg, "read", pressed), mock.patch.object(bg, "is_service", return_value=True):
            self.assertFalse(bg.gate(0)["go"])

    def test_wrong_service_process_fails(self):
        with mock.patch.object(bg, "read", fake_read()), mock.patch.object(bg, "is_service", return_value=False):
            self.assertFalse(bg.gate(0)["go"])

    def test_other_agents_test_run_fails(self):
        self.assertFalse(self.gate(processes="901 /usr/bin/xcodebuild test -scheme App")["go"])

    def test_non_admin_fails(self):
        self.assertFalse(self.gate(whoami="Role:      agent\n")["go"])

    def test_open_t3_session_fails(self):
        with mock.patch.object(bg, "read", fake_read()), mock.patch.object(bg, "is_service", return_value=True):
            self.assertFalse(bg.gate(1)["go"])

    def test_failed_read_fails(self):
        with mock.patch.object(bg, "read", side_effect=subprocess.TimeoutExpired("simlock", 20)):
            self.assertFalse(bg.gate(0)["go"])


class Restart(StateCase):
    def test_logs_the_attempt_before_the_kill(self):
        bg.take_claim("a", time.time())
        seen = {}

        def kill(argv, **options):
            seen["argv"] = argv
            seen["logged"] = [entry["event"] for entry in bg.events()]
            return subprocess.CompletedProcess(argv, 0, "", "")

        with mock.patch.object(bg, "gate", return_value={"go": True, "pid": 7}), mock.patch.object(bg.subprocess, "run", kill), mock.patch.object(bg, "is_service", return_value=False):
            outcome = bg.restart("a", 0)
        self.assertEqual(seen["logged"], ["restart-attempt"])
        self.assertEqual(seen["argv"][:3], ["/bin/launchctl", "kill", "SIGTERM"])
        self.assertTrue(outcome["oldPidExited"])

    def kills(self, thread="a"):
        def kill(argv, **options):
            return subprocess.CompletedProcess(argv, 0, "", "")

        with mock.patch.object(bg, "gate", return_value={"go": True, "pid": 7}), mock.patch.object(bg.subprocess, "run", side_effect=kill) as run, mock.patch.object(bg, "is_service", return_value=False):
            try:
                bg.restart(thread, 0)
            except bg.Refused:
                pass
        return run.call_count

    def test_second_restart_under_one_claim_never_kills(self):
        bg.take_claim("a", time.time())
        self.assertEqual(self.kills(), 1)
        self.assertEqual(self.kills(), 0)

    def test_hold_running_out_during_the_gate_never_kills(self):
        bg.take_claim("a", time.time())

        def slow_gate(_):
            claim = bg.owner()
            claim["holdUntil"] = int(time.time()) + 60
            bg.OWNER.write_text(json.dumps(claim))
            return {"go": True, "pid": 7}

        with mock.patch.object(bg, "gate", slow_gate), mock.patch.object(bg.subprocess, "run") as run, self.assertRaises(bg.Refused):
            bg.restart("a", 0)
        run.assert_not_called()
        self.assertEqual(bg.events(), [])

    def test_expired_hold_refuses(self):
        bg.take_claim("a", time.time() - bg.HOLD_SECONDS - 1)
        with mock.patch.object(bg, "gate") as gate, self.assertRaises(bg.Refused):
            bg.restart("a", 0)
        gate.assert_not_called()

    def test_failed_gate_never_kills(self):
        bg.take_claim("a", time.time())
        with mock.patch.object(bg, "gate", return_value={"go": False}), mock.patch.object(bg.subprocess, "run") as run, self.assertRaises(bg.Refused):
            bg.restart("a", 0)
        run.assert_not_called()
        self.assertEqual(bg.events(), [])

    def test_another_owner_refuses(self):
        bg.take_claim("a", time.time())
        with self.assertRaises(bg.Refused):
            bg.restart("b", 0)


class Commands(StateCase):
    def run_command(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(sys, "argv", ["break_glass.py", *argv]):
            return bg.main()

    def test_a_late_contender_reads_the_last_result_under_the_claim(self):
        self.log("restart-attempt", age=60)
        self.log("finished", age=30, result="acquired")
        self.assertEqual(self.run_command("claim", "--thread", "b"), 3)
        self.assertFalse(bg.CLAIM.exists())

    def test_owner_still_acquiring_keeps_a_stale_claim(self):
        bg.take_claim("a", time.time() - bg.STALE_CLAIM_SECONDS - 1)
        self.log("restart-attempt", age=60)
        self.assertEqual(self.run_command("claim", "--thread", "b"), 3)
        self.assertEqual(self.run_command("finish", "--thread", "a", "--result", "acquired"), 0)

    def test_pid_reports_a_missing_service_without_crashing(self):
        with mock.patch.object(bg, "read", return_value="\tstate = waiting\n"):
            self.assertEqual(self.run_command("pid"), 0)

    def test_held_claim_returns_the_owner_code(self):
        self.run_command("claim", "--thread", "a")
        self.assertEqual(self.run_command("claim", "--thread", "b"), 2)

    def test_finish_and_abort_release_the_claim(self):
        for command, extra in (("finish", ("--result", "acquired")), ("abort", ("--reason", "silent"))):
            with self.subTest(command):
                bg.CLAIM.mkdir(parents=True)
                bg.OWNER.write_text(json.dumps({"thread": "a", "claimedAt": int(time.time()), "holdUntil": int(time.time()) + 60}))
                self.assertEqual(self.run_command(command, "--thread", "a", *extra), 0)
                self.assertFalse(bg.CLAIM.exists())

    def test_finish_logs_its_result(self):
        self.run_command("claim", "--thread", "a")
        self.run_command("finish", "--thread", "a", "--result", "failed")
        self.assertEqual(bg.events()[-1]["result"], "failed")

    def test_abort_logs_its_reason(self):
        self.run_command("claim", "--thread", "a")
        self.run_command("abort", "--thread", "a", "--reason", "silent")
        self.assertEqual(bg.events()[-1]["reason"], "silent")

    def test_kill_that_fails_exits_4(self):
        bg.take_claim("a", time.time())
        outcome = {"launchctlExit": 1, "oldPid": 7, "oldPidExited": False}
        with mock.patch.object(bg, "restart", return_value=outcome):
            self.assertEqual(self.run_command("restart", "--thread", "a", "--t3-open-sessions", "0"), 4)

    def test_wait_returns_when_the_claim_is_gone(self):
        bg.wait()

    def test_wait_returns_at_the_deadline_with_the_claim_held(self):
        bg.take_claim("a", time.time() - bg.HOLD_SECONDS - 1)
        bg.wait()
        self.assertTrue(bg.CLAIM.exists())

    def test_wait_is_bounded_when_the_owner_file_is_missing(self):
        bg.STATE.mkdir()
        bg.CLAIM.mkdir()
        old = time.time() - bg.HOLD_SECONDS - 1
        os.utime(bg.CLAIM, (old, old))
        bg.wait()


if __name__ == "__main__":
    unittest.main()
