from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "showroom" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from showroom_lib.adapters.ios import (  # noqa: E402
    CommandFailure,
    CommandResult,
    DiscoveryError,
    IOSConfiguration,
    IOSShowroomRequest,
    IOSSimulatorAdapter,
    OwnershipDrift,
    SimulatorOwnership,
    SubprocessRecordingRunner,
)


TEMPLATE = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
CLONE_ONE = "BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB"
CLONE_TWO = "CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC"
DEVICE_TYPE = "com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro"
RUNTIME = "com.apple.CoreSimulator.SimRuntime.iOS-26-0"


class FakeOwnership:
    def __init__(self) -> None:
        self.records: dict[str, SimulatorOwnership] = {}

    def list_ios_simulators(self):
        return tuple(self.records.values())

    def get_ios_simulator(self, udid):
        return self.records.get(udid)

    def save_ios_simulator(self, record):
        self.records[record.udid] = record

    def remove_ios_simulator(self, udid):
        self.records.pop(udid, None)


class FakeRunner:
    def __init__(self, *, fail_build: bool = False) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.call_cwds: list[Path | None] = []
        self.devices: dict[str, dict[str, object]] = {}
        self.clone_ids = iter((CLONE_ONE, CLONE_TWO))
        self.fail_build = fail_build
        self.frame_ready = False

    def run(self, argv, *, cwd=None):
        command = tuple(str(item) for item in argv)
        self.calls.append(command)
        self.call_cwds.append(Path(cwd) if cwd is not None else None)
        if cwd is not None and not Path(cwd).is_dir():
            raise FileNotFoundError(cwd)
        if command == ("xcrun", "simctl", "list", "devicetypes", "runtimes", "--json"):
            return self.ok(
                {
                    "devicetypes": [{"name": "iPhone 17 Pro", "identifier": DEVICE_TYPE}],
                    "runtimes": [
                        {
                            "name": "iOS 26.0",
                            "version": "26.0",
                            "identifier": RUNTIME,
                            "isAvailable": True,
                        }
                    ],
                }
            )
        if command == ("xcrun", "simctl", "list", "devices", "--json"):
            return self.ok({"devices": {RUNTIME: list(self.devices.values())}})
        if command[0:3] == ("xcrun", "simctl", "create"):
            self.devices[TEMPLATE] = self.device(TEMPLATE, "showroom template", "Shutdown")
            return CommandResult(0, TEMPLATE + "\n", "")
        if command[0:3] == ("xcrun", "simctl", "clone"):
            clone = next(self.clone_ids)
            self.devices[clone] = self.device(clone, command[-1], "Shutdown")
            return CommandResult(0, clone + "\n", "")
        if command[0] == "xcodebuild" and "-list" in command:
            return self.ok({"project": {"schemes": ["Demo"]}})
        if command[0] == "xcodebuild" and "-showdestinations" in command:
            clones = [udid for udid in self.devices if udid != TEMPLATE]
            return CommandResult(
                0,
                "\n".join(
                    f"{{ platform:iOS Simulator, id:{clone} }}" for clone in clones
                ),
                "",
            )
        if command[0] == "xcodebuild" and "-showBuildSettings" in command:
            derived = Path(command[command.index("-derivedDataPath") + 1])
            return self.ok(
                [
                    {
                        "target": "Demo",
                        "buildSettings": {
                            "TARGET_BUILD_DIR": str(derived / "Build/Products/Debug-iphonesimulator"),
                            "WRAPPER_NAME": "Demo.app",
                            "PRODUCT_BUNDLE_IDENTIFIER": "example.Demo",
                            "IPHONEOS_DEPLOYMENT_TARGET": "18.0",
                            "CODE_SIGN_STYLE": "Automatic",
                        },
                    }
                ]
            )
        if command[0] == "xcodebuild" and command[-1] == "build":
            if self.fail_build:
                return CommandResult(65, "", "compile failed")
            derived = Path(command[command.index("-derivedDataPath") + 1])
            (derived / "Build/Products/Debug-iphonesimulator/Demo.app").mkdir(
                parents=True, exist_ok=True
            )
            return CommandResult(0, "BUILD SUCCEEDED", "")
        if command[0:4] == ("xcrun", "xcresulttool", "get", "build-results"):
            return self.ok({"result": "succeeded", "issues": []})
        if command[0:3] == ("xcrun", "simctl", "boot"):
            self.devices[command[3]]["state"] = "Booted"
            return CommandResult(0)
        if command[0:3] == ("xcrun", "simctl", "launch"):
            return CommandResult(0, "example.Demo: 4321\n", "")
        if command[0:4] == ("xcrun", "simctl", "io", command[3]) and command[4] == "screenshot":
            if not self.frame_ready:
                raise AssertionError("screenshot captured before the first app frame")
            Path(command[-1]).write_bytes(b"png")
            return CommandResult(0)
        if command[0:3] == ("xcrun", "simctl", "shutdown"):
            self.devices[command[3]]["state"] = "Shutdown"
            return CommandResult(0)
        if command[0:3] == ("xcrun", "simctl", "delete"):
            self.devices.pop(command[3], None)
            return CommandResult(0)
        if command[0:3] == ("xcrun", "simctl", "terminate"):
            return CommandResult(0)
        if command[0:3] == ("xcrun", "simctl", "install"):
            return CommandResult(0)
        if command[0:3] == ("xcrun", "simctl", "appinfo"):
            return CommandResult(0, "Bundle = example.Demo")
        if command[0:3] in {
            ("xcrun", "simctl", "openurl"),
            ("xcrun", "simctl", "install_app_data"),
        }:
            return CommandResult(0)
        raise AssertionError(f"unexpected command: {command}")

    @staticmethod
    def ok(payload):
        return CommandResult(0, json.dumps(payload), "")

    @staticmethod
    def device(udid, name, state):
        return {
            "udid": udid,
            "name": name,
            "state": state,
            "isAvailable": True,
            "deviceTypeIdentifier": DEVICE_TYPE,
        }


class FakeRecordingRunner:
    def __init__(self) -> None:
        self.calls = []

    def record(self, argv, *, duration_seconds):
        command = tuple(str(item) for item in argv)
        self.calls.append((command, duration_seconds))
        Path(command[-1]).write_bytes(b"mov")
        return CommandResult(0, "", "Recording started")


class IOSAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        scheme_dir = self.repo / "Demo.xcodeproj/xcshareddata/xcschemes"
        scheme_dir.mkdir(parents=True)
        (scheme_dir / "Demo.xcscheme").write_text("<Scheme/>", encoding="utf-8")
        self.state = self.root / "state"
        self.store = FakeOwnership()
        self.runner = FakeRunner()
        self.attempts = iter(("attempt-one", "attempt-two", "attempt-three"))
        self.settle_calls = []

    def request(
        self, *, worktree=None, worktree_id="worktree-one", showroom_id="srm_ios_demo", **overrides
    ):
        values = {
            "project": "Demo.xcodeproj",
            "scheme": "Demo",
            "target": "Demo",
            "device_type_identifier": DEVICE_TYPE,
            "runtime_identifier": RUNTIME,
        }
        values.update(overrides)
        return IOSShowroomRequest(
            showroom_id,
            self.repo,
            worktree or self.repo,
            self.state,
            "project-one",
            worktree_id,
            IOSConfiguration(**values),
        )

    def adapter(self, runner=None):
        selected_runner = runner or self.runner

        def settle(seconds):
            self.settle_calls.append(seconds)
            selected_runner.frame_ready = True

        return IOSSimulatorAdapter(
            selected_runner,
            self.store,
            clock=lambda: datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
            token_factory=lambda: next(self.attempts),
            sleeper=settle,
        )

    def test_full_flow_uses_exact_argv_and_captures_evidence(self) -> None:
        fixture = self.repo / "fixture.xcappdata"
        fixture.mkdir()
        result = self.adapter().start(
            self.request(
                deep_link="demo://screen/42?token=secret",
                launch_arguments=("--fixture", "review"),
                fixture="fixture.xcappdata",
            )
        )
        self.assertEqual(result.verification_status, "passed")
        self.assertEqual(result.launch_pid, 4321)
        self.assertEqual(self.settle_calls, [1.0])
        self.assertTrue(any(path.endswith("screenshot.png") for path in result.evidence_paths))
        self.assertIn(
            ("xcrun", "simctl", "openurl", CLONE_ONE, "demo://screen/42?token=secret"),
            self.runner.calls,
        )
        launch = next(call for call in self.runner.calls if call[0:3] == ("xcrun", "simctl", "launch"))
        self.assertEqual(launch[-4:], (CLONE_ONE, "example.Demo", "--fixture", "review"))
        flattened = " ".join(" ".join(call) for call in self.runner.calls)
        self.assertNotIn("-allowProvisioningUpdates", flattened)
        self.assertNotIn(" booted", flattened)

    def test_discovery_rejects_ambiguous_projects_and_schemes(self) -> None:
        (self.repo / "Other.xcodeproj").mkdir()
        request = self.request(project=None, scheme=None)
        with self.assertRaises(DiscoveryError):
            self.adapter().discover_container(request)
        (self.repo / "Other.xcodeproj").rmdir()
        other_scheme = self.repo / "Demo.xcodeproj/xcshareddata/xcschemes/Other.xcscheme"
        other_scheme.write_text("<Scheme/>", encoding="utf-8")
        class TwoSchemeRunner(FakeRunner):
            def run(inner_self, argv, *, cwd=None):
                if "-list" in argv:
                    inner_self.calls.append(tuple(argv))
                    return inner_self.ok({"project": {"schemes": ["Demo", "Other"]}})
                return super(TwoSchemeRunner, inner_self).run(argv, cwd=cwd)
        with self.assertRaises(DiscoveryError):
            self.adapter(TwoSchemeRunner()).discover_shared_scheme(
                self.request(scheme=None),
                self.adapter().discover_container(self.request()),
            )

    def test_distinct_worktrees_get_distinct_clones_and_build_paths(self) -> None:
        first = self.adapter().start(self.request())
        linked = self.root / "linked"
        linked_scheme = linked / "Demo.xcodeproj/xcshareddata/xcschemes"
        linked_scheme.mkdir(parents=True)
        (linked_scheme / "Demo.xcscheme").write_text("<Scheme/>", encoding="utf-8")
        second = self.adapter().start(
            self.request(worktree=linked, worktree_id="worktree-two")
        )
        self.assertNotEqual(first.simulator_udid, second.simulator_udid)
        self.assertNotEqual(first.derived_data_path, second.derived_data_path)

    def test_repeated_start_reuses_exact_registered_clone(self) -> None:
        self.adapter().start(self.request())
        self.adapter().start(self.request())
        clones = [call for call in self.runner.calls if call[0:3] == ("xcrun", "simctl", "clone")]
        self.assertEqual(len(clones), 1)

    def test_distinct_profiles_in_one_worktree_get_distinct_owned_clones(self) -> None:
        first = self.adapter().start(self.request(showroom_id="srm_ios_profile_one"))
        second = self.adapter().start(self.request(showroom_id="srm_ios_profile_two"))
        self.assertNotEqual(first.simulator_udid, second.simulator_udid)
        ownership = {record.udid: record for record in self.store.list_ios_simulators()}
        self.assertEqual("srm_ios_profile_one", ownership[first.simulator_udid].showroom_id)
        self.assertEqual("srm_ios_profile_two", ownership[second.simulator_udid].showroom_id)

    def test_optional_recording_hook_targets_only_the_exact_clone(self) -> None:
        recorder = FakeRecordingRunner()
        adapter = IOSSimulatorAdapter(
            self.runner,
            self.store,
            clock=lambda: datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
            token_factory=lambda: next(self.attempts),
            recording_runner=recorder,
            sleeper=lambda _: setattr(self.runner, "frame_ready", True),
        )
        result = adapter.start(self.request(recording=True, recording_seconds=1.5))
        self.assertTrue(any(path.endswith("recording.mov") for path in result.evidence_paths))
        self.assertEqual(recorder.calls[0][0][0:5], ("xcrun", "simctl", "io", CLONE_ONE, "recordVideo"))
        self.assertEqual(recorder.calls[0][1], 1.5)

    def test_build_failure_never_installs_or_claims_verification(self) -> None:
        runner = FakeRunner(fail_build=True)
        with self.assertRaises(CommandFailure):
            self.adapter(runner).start(self.request())
        self.assertFalse(any(call[0:3] == ("xcrun", "simctl", "install") for call in runner.calls))
        self.assertFalse(any(call[0:3] == ("xcrun", "simctl", "launch") for call in runner.calls))
        self.assertIn(("xcrun", "simctl", "delete", CLONE_ONE), runner.calls)

    def test_cleanup_dry_run_and_delete_are_exact(self) -> None:
        result = self.adapter().start(self.request())
        before = list(self.runner.calls)
        dry = self.adapter().cleanup(
            self.request(), result.simulator_udid, bundle_identifier=result.bundle_identifier, dry_run=True
        )
        self.assertEqual(dry.status, "would-delete")
        self.assertEqual(before + [("xcrun", "simctl", "list", "devices", "--json")], self.runner.calls)
        deleted = self.adapter().cleanup(
            self.request(), result.simulator_udid, bundle_identifier=result.bundle_identifier
        )
        self.assertEqual(deleted.status, "deleted")
        for command in deleted.commands:
            self.assertIn(CLONE_ONE, command)
            self.assertFalse({"all", "booted", "unavailable", "erase"} & set(command))

    def test_cleanup_recognizes_exact_idempotent_simctl_failures(self) -> None:
        cases = (
            (["xcrun", "simctl", "terminate", CLONE_ONE, "example.Demo"], "app is not running"),
            (["xcrun", "simctl", "shutdown", CLONE_ONE], "Unable to shutdown device in current state: Shutdown"),
            (["xcrun", "simctl", "delete", CLONE_ONE], "Invalid device"),
        )
        for command, stderr in cases:
            with self.subTest(command=command):
                self.assertTrue(
                    IOSSimulatorAdapter._idempotent_cleanup_failure(
                        command, CommandResult(1, "", stderr)
                    )
                )

    def test_cleanup_refuses_ownership_and_observation_drift(self) -> None:
        result = self.adapter().start(self.request())
        with self.assertRaises(OwnershipDrift):
            self.adapter().cleanup(
                self.request(worktree_id="other"), result.simulator_udid
            )
        self.runner.devices[CLONE_ONE]["deviceTypeIdentifier"] = (
            "com.apple.CoreSimulator.SimDeviceType.iPad-Pro"
        )
        with self.assertRaises(OwnershipDrift):
            self.adapter().cleanup(self.request(), result.simulator_udid)
        destructive = [
            call
            for call in self.runner.calls
            if call[0:3] in {
                ("xcrun", "simctl", "delete"),
                ("xcrun", "simctl", "shutdown"),
                ("xcrun", "simctl", "terminate"),
            }
        ]
        self.assertEqual(destructive, [])

    def test_cleanup_survives_deleted_worktree_using_manager_state_cwd(self) -> None:
        result = self.adapter().start(self.request())
        shutil.rmtree(self.repo)
        cleanup = self.adapter().cleanup(
            self.request(),
            result.simulator_udid,
            bundle_identifier=result.bundle_identifier,
        )
        self.assertEqual(cleanup.status, "deleted")
        destructive_indexes = [
            index
            for index, call in enumerate(self.runner.calls)
            if call[0:3]
            in {
                ("xcrun", "simctl", "terminate"),
                ("xcrun", "simctl", "shutdown"),
                ("xcrun", "simctl", "delete"),
            }
        ]
        self.assertTrue(destructive_indexes)
        self.assertTrue(self.state.is_dir())
        self.assertTrue(
            all(self.runner.call_cwds[index] == self.state for index in destructive_indexes)
        )

    def test_recording_runner_drains_large_stdout_and_stderr(self) -> None:
        script = """
import signal
import sys
import time

signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
sys.stderr.write('Recording started\\n')
sys.stderr.flush()
sys.stdout.write('o' * 200000)
sys.stdout.flush()
sys.stderr.write('e' * 200000 + '\\n')
sys.stderr.flush()
while True:
    time.sleep(0.01)
"""
        completed = SubprocessRecordingRunner().record(
            [sys.executable, "-c", script], duration_seconds=0.05
        )
        self.assertEqual(completed.returncode, 0)
        self.assertGreaterEqual(len(completed.stdout), 200000)
        self.assertGreaterEqual(len(completed.stderr), 200000)
        self.assertIn("Recording started", completed.stderr)


if __name__ == "__main__":
    unittest.main()
