from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "showroom" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from showroom_lib.delivery import run_delivery, validate_description, validate_result  # noqa: E402
from showroom_lib.errors import AdapterError, ConfigurationError  # noqa: E402
from showroom_lib.project import configured_projects, detect_config, detect_project  # noqa: E402


class ProjectDeliveryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "ios" / "Deal" / "Deal.xcodeproj").mkdir(parents=True)
        self.fake = self.repo / "delivery.py"
        self.fake.write_text(
            """#!/usr/bin/env python3
import json, pathlib, sys
args = sys.argv[1:]
if args == ['describe', '--json']:
    print(json.dumps({'protocol_version': 1, 'surfaces': {
        'device': {'start': ['device', 'install'], 'verify': ['device', 'verify'], 'lifecycle_owner': 'manual', 'required_arguments': []},
        'testflight': {'start': ['testflight', 'upload'], 'verify': ['testflight', 'verify'], 'lifecycle_owner': 'provider', 'provider': 'app-store-connect', 'required_arguments': ['build-number']}
    }}))
    raise SystemExit(0)
result_path = pathlib.Path(args[args.index('--result-json') + 1])
operation = 'verify' if 'verify' in args else 'start'
surface = args[0]
events = pathlib.Path(__file__).with_name('events.log')
with events.open('a') as stream:
    stream.write(surface + ':' + operation + '\\n')
pending = surface == 'testflight' and operation == 'start'
result = {
    'protocol_version': 1, 'surface': surface, 'operation': operation,
    'verification': {'status': 'pending' if pending else 'passed', 'detail': 'ok', 'checks': {'delivery': 'pending' if pending else 'passed'}},
    'location': {'device': 'Test iPhone'} if surface == 'device' else {'url': 'https://appstoreconnect.apple.com/apps'},
    'provider': 'app-store-connect' if surface == 'testflight' else None,
    'provider_resource_id': None if pending or surface == 'device' else 'build_123',
    'evidence_paths': [], 'log_paths': [], 'availability_limitations': ['test fixture']
}
result_path.write_text(json.dumps(result))
""",
            encoding="utf-8",
        )
        self.fake.chmod(0o755)
        subprocess.run(["git", "-C", str(self.repo), "add", "delivery.py"], check=True)
        self.config_path = self.repo / ".showroom.toml"
        self.config_path.write_text(
            f'''version = 1
[deal]
project = "ios/Deal/Deal.xcodeproj"
scheme = "Deal"
delivery = ["{sys.executable}", "delivery.py"]
''',
            encoding="utf-8",
        )


class ConfigurationTests(ProjectDeliveryCase):
    def test_minimal_named_project_config(self) -> None:
        project = detect_project(self.repo)
        self.assertEqual(["deal"], sorted(configured_projects(project)))
        config = detect_config(project, "deal", "device")
        self.assertEqual("ios/Deal/Deal.xcodeproj", config.ios["project"])
        self.assertEqual("Deal", config.ios["scheme"])
        self.assertEqual((sys.executable, "delivery.py"), config.delivery)
        self.assertEqual("deal-device", config.profile)

    def test_unknown_config_key_is_rejected(self) -> None:
        self.config_path.write_text(self.config_path.read_text() + 'device = "mine"\n', encoding="utf-8")
        with self.assertRaisesRegex(ConfigurationError, "unknown key"):
            configured_projects(detect_project(self.repo))

    def test_config_version_requires_an_integer(self) -> None:
        self.config_path.write_text(self.config_path.read_text().replace("version = 1", "version = true"), encoding="utf-8")
        with self.assertRaisesRegex(ConfigurationError, "version = 1"):
            configured_projects(detect_project(self.repo))

    def test_configured_project_path_cannot_escape_worktree(self) -> None:
        self.config_path.write_text(
            'version = 1\n[deal]\nproject = "../Other.xcodeproj"\nscheme = "Deal"\ndelivery = ["node", "delivery.mjs"]\n',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ConfigurationError, "inside the worktree"):
            configured_projects(detect_project(self.repo))

    def test_delivery_command_must_include_a_checked_in_path(self) -> None:
        self.config_path.write_text(
            'version = 1\n[deal]\nproject = "ios/Deal/Deal.xcodeproj"\nscheme = "Deal"\ndelivery = ["node", "../delivery.mjs"]\n',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ConfigurationError, "inside the worktree"):
            configured_projects(detect_project(self.repo))

        untracked = self.repo / "untracked.py"
        untracked.write_text("pass\n", encoding="utf-8")
        self.config_path.write_text(
            'version = 1\n[deal]\nproject = "ios/Deal/Deal.xcodeproj"\nscheme = "Deal"\ndelivery = ["node", "untracked.py"]\n',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ConfigurationError, "checked-in command path"):
            configured_projects(detect_project(self.repo))

    def test_missing_config_keeps_old_discovery(self) -> None:
        self.config_path.unlink()
        (self.repo / "package.json").write_text('{"scripts":{"dev":"vite"}}', encoding="utf-8")
        config = detect_config(detect_project(self.repo))
        self.assertEqual("web", config.kind)
        self.assertEqual(("npm", "run", "dev", "--", "--port", "{port}"), config.command)


class ProtocolTests(ProjectDeliveryCase):
    def test_description_rejects_unknown_fields_and_shell_strings(self) -> None:
        with self.assertRaises(ConfigurationError):
            validate_description({"protocol_version": 1, "surfaces": {"device": {
                "start": "device install", "verify": ["device", "verify"], "lifecycle_owner": "manual",
                "required_arguments": [], "extra": True,
            }}})

    def test_description_rejects_wrong_lifecycle_and_argument_shapes(self) -> None:
        for value in (
            {"protocol_version": True, "surfaces": {"device": {
                "start": ["device", "install"], "verify": ["device", "verify"],
                "lifecycle_owner": "manual", "required_arguments": [],
            }}},
            {"protocol_version": 1, "surfaces": {"device": {
                "start": ["device", "install"], "verify": ["device", "verify"],
                "lifecycle_owner": "provider", "provider": "vendor", "required_arguments": [],
            }}},
            {"protocol_version": 1, "surfaces": {"device": {
                "start": ["device", "install"], "verify": ["device", "verify"],
                "lifecycle_owner": "manual", "provider": None, "required_arguments": [],
            }}},
            {"protocol_version": 1, "surfaces": {"testflight": {
                "start": ["testflight", "upload"], "verify": ["testflight", "verify"],
                "lifecycle_owner": "provider", "provider": "app-store-connect",
                "required_arguments": ["-build-number"],
            }}},
        ):
            with self.assertRaises(ConfigurationError):
                validate_description(value)

    def test_result_accepts_pending_provider_without_resource_id(self) -> None:
        value = {
            "protocol_version": 1,
            "surface": "testflight",
            "operation": "start",
            "verification": {"status": "pending", "detail": "processing", "checks": {"upload": "passed", "processing": "pending"}},
            "location": {"url": "https://appstoreconnect.apple.com/"},
            "provider": "app-store-connect",
            "provider_resource_id": None,
            "evidence_paths": [],
            "log_paths": [],
            "availability_limitations": ["Apple processing is pending"],
        }
        result = validate_result(value, surface="testflight", operation="start", worktree=self.repo, showroom_dir=self.root / "state")
        self.assertEqual("pending", result["verification"]["status"])

    def test_result_paths_must_stay_in_owned_roots(self) -> None:
        value = {
            "protocol_version": 1,
            "surface": "device",
            "operation": "start",
            "verification": {"status": "passed", "detail": "ok", "checks": {}},
            "location": {"device": "iPhone"},
            "evidence_paths": ["/etc/hosts"],
            "log_paths": [],
            "availability_limitations": [],
        }
        with self.assertRaisesRegex(AdapterError, "inside the worktree or Showroom state"):
            validate_result(value, surface="device", operation="start", worktree=self.repo, showroom_dir=self.root / "state")

    def test_result_rejects_bad_status_types_and_missing_artifacts(self) -> None:
        value = {
            "protocol_version": True,
            "surface": "device",
            "operation": "verify",
            "verification": {"status": [], "detail": "bad", "checks": {}},
            "location": {"artifact": "missing.app"},
            "evidence_paths": [],
            "log_paths": [],
            "availability_limitations": [],
        }
        with self.assertRaises(AdapterError):
            validate_result(
                value,
                surface="device",
                operation="verify",
                worktree=self.repo,
                showroom_dir=self.root / "state",
            )
        value["protocol_version"] = 1
        value["verification"]["status"] = "passed"
        with self.assertRaisesRegex(AdapterError, "does not exist"):
            validate_result(
                value,
                surface="device",
                operation="verify",
                worktree=self.repo,
                showroom_dir=self.root / "state",
            )

    def test_malformed_result_is_an_adapter_error(self) -> None:
        with self.assertRaisesRegex(AdapterError, "missing field"):
            validate_result(
                {"protocol_version": 1},
                surface="device",
                operation="verify",
                worktree=self.repo,
                showroom_dir=self.root / "state",
            )
        value = {
            "protocol_version": 1,
            "surface": "device",
            "operation": "verify",
            "verification": {"status": "passed", "detail": "bad", "checks": {"probe": []}},
            "location": {"device": "iPhone"},
            "evidence_paths": [],
            "log_paths": [],
            "availability_limitations": [],
        }
        with self.assertRaisesRegex(AdapterError, "checks must map"):
            validate_result(
                value,
                surface="device",
                operation="verify",
                worktree=self.repo,
                showroom_dir=self.root / "state",
            )

    def test_result_requires_the_surface_location(self) -> None:
        value = {
            "protocol_version": 1,
            "surface": "device",
            "operation": "verify",
            "verification": {"status": "passed", "detail": "ok", "checks": {}},
            "location": {"url": "https://example.invalid"},
            "evidence_paths": [],
            "log_paths": [],
            "availability_limitations": [],
        }
        with self.assertRaisesRegex(AdapterError, "needs location device"):
            validate_result(
                value,
                surface="device",
                operation="verify",
                worktree=self.repo,
                showroom_dir=self.root / "state",
            )

    def test_delivery_cannot_reuse_a_stale_result_file(self) -> None:
        showroom_dir = self.root / "state"
        showroom_dir.mkdir()
        (showroom_dir / "delivery-device-verify.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(AdapterError, "did not write result JSON"):
            run_delivery(
                command=(sys.executable, "-c", "pass"),
                operation_argv=("device", "verify"),
                surface="device",
                operation="verify",
                arguments={},
                required_arguments=(),
                worktree=self.repo,
                showroom_dir=showroom_dir,
            )


class CliIntegrationTests(ProjectDeliveryCase):
    def setUp(self) -> None:
        super().setUp()
        self.state = self.root / "state"
        self.cli = ROOT / "skills" / "showroom" / "scripts" / "showroom"
        self.env = {**os.environ, "SHOWROOM_STATE_DIR": str(self.state), "SHOWROOM_NOW": "2026-01-02T03:04:05Z"}

    def run_cli(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([str(self.cli), *args], cwd=self.repo, env=self.env, text=True, capture_output=True)
        if ok and result.returncode != 0:
            self.fail(f"showroom failed ({result.returncode}): {result.stderr}\n{result.stdout}")
        return result

    def test_doctor_checks_config_and_description_without_delivery(self) -> None:
        result = json.loads(self.run_cli("doctor", "deal", "--json").stdout)
        self.assertTrue(result["ok"])
        self.assertFalse((self.repo / "events.log").exists())

    def test_device_start_verify_and_stop_never_remove_device(self) -> None:
        started = json.loads(self.run_cli("start", "deal", "device", "--json").stdout)
        self.assertEqual("manual", started["lifecycle_owner"])
        self.assertEqual("2026-01-03T03:04:05Z", started["timestamps"]["expires_at"])
        checked = json.loads(self.run_cli("verify", started["id"], "--json").stdout)
        self.assertEqual("passed", checked["verification"]["status"])
        stopped = json.loads(self.run_cli("stop", started["id"], "--json").stdout)
        self.assertEqual("stopped", stopped["status"])
        self.assertEqual(["device:start", "device:verify"], (self.repo / "events.log").read_text().splitlines())

    def test_device_verification_cannot_claim_a_provider(self) -> None:
        started = json.loads(self.run_cli("start", "deal", "device", "--json").stdout)
        self.fake.write_text(
            self.fake.read_text().replace(
                "'provider': 'app-store-connect' if surface == 'testflight' else None,",
                "'provider': 'app-store-connect',",
            ),
            encoding="utf-8",
        )
        result = self.run_cli("verify", started["id"], "--json", ok=False)
        self.assertIn("manual delivery verification", result.stderr)

    def test_testflight_start_is_provider_owned_without_guessed_expiry(self) -> None:
        started = json.loads(self.run_cli("start", "deal", "testflight", "--build-number", "12", "--json").stdout)
        self.assertEqual("provider", started["lifecycle_owner"])
        self.assertIsNone(started["timestamps"]["expires_at"])
        self.assertEqual("pending", started["verification"]["status"])
        checked = json.loads(self.run_cli("verify", started["id"], "--json").stdout)
        self.assertEqual("build_123", checked["provider_resource_id"])
        stopped = json.loads(self.run_cli("stop", started["id"], "--json").stdout)
        self.assertEqual("stopped", stopped["status"])
        self.assertEqual(["testflight:start", "testflight:verify"], (self.repo / "events.log").read_text().splitlines())

    def test_testflight_build_numbers_get_distinct_records(self) -> None:
        first = json.loads(self.run_cli("start", "deal", "testflight", "--build-number", "12", "--json").stdout)
        second = json.loads(self.run_cli("start", "deal", "testflight", "--build-number", "13", "--json").stdout)
        self.assertNotEqual(first["id"], second["id"])

    def test_testflight_verification_rejects_provider_resource_drift(self) -> None:
        started = json.loads(self.run_cli("start", "deal", "testflight", "--build-number", "12", "--json").stdout)
        self.run_cli("verify", started["id"], "--json")
        self.fake.write_text(self.fake.read_text().replace("build_123", "build_456"), encoding="utf-8")
        result = self.run_cli("verify", started["id"], "--json", ok=False)
        self.assertIn("provider resource changed", result.stderr)

    def test_testflight_requires_declared_argument(self) -> None:
        result = self.run_cli("start", "deal", "testflight", "--json", ok=False)
        self.assertEqual(2, result.returncode)
        self.assertIn("--build-number", result.stderr)


if __name__ == "__main__":
    unittest.main()
