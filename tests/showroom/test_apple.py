from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "showroom" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from showroom_lib.apple import (  # noqa: E402
    API_KEY_SERVICE,
    _run,
    delivery_environment,
    load_profile,
    lock_profile,
    profile_status,
    setup_profile,
    unlock_profile,
)
from showroom_lib.errors import ConfigurationError  # noqa: E402


class FakeSecurity:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[str, ...], str | None]] = []
        self.keychain: Path | None = None
        self.unlocked = False
        self.api_key = ""
        self.search = ["/Users/test/Library/Keychains/login.keychain-db"]

    def __call__(
        self,
        argv,
        *,
        input_text=None,
        check=True,
        capture=True,
    ) -> subprocess.CompletedProcess[str]:
        command = tuple(argv)
        self.calls.append((command, input_text))
        stdout = ""
        returncode = 0
        if command[1] == "create-keychain":
            self.keychain = Path(command[-1])
            self.keychain.touch(mode=0o600)
            self.unlocked = True
        elif command[1] == "delete-keychain":
            Path(command[-1]).unlink(missing_ok=True)
        elif command[1] == "unlock-keychain":
            self.unlocked = True
        elif command[1] == "lock-keychain":
            self.unlocked = False
        elif command[1] == "show-keychain-info":
            returncode = 0 if self.unlocked else 1
        elif command[1] == "add-generic-password":
            self.api_key = input_text or ""
        elif command[1] == "find-generic-password":
            if not self.api_key:
                returncode = 44
            elif "-w" in command:
                stdout = self.api_key
        elif command[1] == "find-identity":
            stdout = (
                '  1) AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA "Apple Distribution: Test"\n'
                '  2) BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB "Apple Development: Test"\n'
                '     2 valid identities found\n'
            )
        elif command[1] == "list-keychains" and "-s" in command:
            self.search = list(command[command.index("-s") + 1 :])
        elif command[1] == "list-keychains":
            stdout = "".join(f'    "{value}"\n' for value in self.search)
        return subprocess.CompletedProcess(command, returncode, stdout, "failure" if returncode else "")

    def put(self, path: Path, account: str, value: bytes) -> None:
        self.api_key = value.decode()

    def get(self, path: Path, account: str) -> bytes:
        if not self.api_key:
            raise ConfigurationError("missing fake key")
        return self.api_key.encode()

    def has(self, path: Path, account: str) -> bool:
        return bool(self.api_key)


class AppleProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        uname = patch(
            "showroom_lib.apple.os.uname",
            return_value=SimpleNamespace(sysname="Darwin"),
        )
        uname.start()
        self.addCleanup(uname.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.state = Path(self.temporary.name) / "state"
        self.source = Path(self.temporary.name) / "source"
        self.source.mkdir()
        self.api_key = self.source / "AuthKey_TEST.p8"
        self.api_key.write_text("PRIVATE API KEY", encoding="utf-8")
        self.certificate = self.source / "distribution.p12"
        self.certificate.write_bytes(b"certificate")
        self.security = FakeSecurity()

    def setup(self) -> dict:
        passwords = iter(("session password", "session password"))
        return setup_profile(
            self.state,
            name="personal",
            team_id="TEAM123456",
            key_id="KEY123",
            issuer_id="issuer-123",
            api_key_path=self.api_key,
            certificates=[self.certificate],
            unlock_seconds=8 * 60 * 60,
            make_default=True,
            password_reader=lambda _: next(passwords),
            runner=self.security,
            secrets=self.security,
        )

    def test_run_reports_uncaptured_command_failure(self) -> None:
        completed = subprocess.CompletedProcess(("security", "import"), 1, None, None)
        with patch("showroom_lib.apple.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(ConfigurationError, "exit 1"):
                _run(("security", "import"), capture=False)

    def test_setup_keeps_secrets_out_of_profile_store(self) -> None:
        result = self.setup()
        self.assertTrue(result["ready"])
        document = json.loads((self.state / "credentials/apple/profiles.json").read_text())
        serialized = json.dumps(document)
        self.assertNotIn("session password", serialized)
        self.assertNotIn("PRIVATE API KEY", serialized)
        self.assertEqual(document["default_profile"], "personal")
        self.assertEqual((self.state / "credentials/apple/profiles.json").stat().st_mode & 0o777, 0o600)
        import_call = next(call for call, _ in self.security.calls if call[1] == "import")
        self.assertIn("-x", import_call)
        self.assertNotIn("-A", import_call)
        self.assertEqual(self.security.api_key, "PRIVATE API KEY")
        self.assertFalse(any(call[1] == "add-generic-password" for call, _ in self.security.calls))

    def test_setup_rejects_an_existing_profile_without_replacing_it(self) -> None:
        self.setup()
        passwords = iter(("another", "another"))
        with self.assertRaisesRegex(ConfigurationError, "already exists"):
            setup_profile(
                self.state,
                name="personal",
                team_id="TEAM123456",
                key_id="KEY123",
                issuer_id="issuer-123",
                api_key_path=self.api_key,
                certificates=[self.certificate],
                unlock_seconds=60,
                make_default=True,
                password_reader=lambda _: next(passwords),
                runner=self.security,
                secrets=self.security,
            )

    def test_unlock_and_lock_do_not_persist_the_password(self) -> None:
        self.setup()
        lock_profile(self.state, runner=self.security, secrets=self.security)
        self.assertFalse(
            profile_status(self.state, runner=self.security, secrets=self.security)["keychain_unlocked"]
        )
        unlock_profile(
            self.state,
            hours=2,
            password_reader=lambda _: "session password",
            runner=self.security,
            secrets=self.security,
        )
        self.assertTrue(
            profile_status(self.state, runner=self.security, secrets=self.security)["keychain_unlocked"]
        )
        unlock_call = next(call for call, _ in self.security.calls if call[1] == "unlock-keychain")
        self.assertIn("session password", unlock_call)
        document = (self.state / "credentials/apple/profiles.json").read_text()
        self.assertNotIn("session password", document)

    def test_delivery_context_lends_a_temporary_key_and_restores_search_list(self) -> None:
        self.setup()
        original_search = list(self.security.search)
        key_path: Path | None = None
        with delivery_environment(
            self.state,
            surface="testflight",
            operation="start",
            required=True,
            base={"SAFE": "1"},
            runner=self.security,
            secrets=self.security,
        ) as environment:
            key_path = Path(environment["SHOWROOM_APPLE_KEY_PATH"])
            self.assertEqual(key_path.read_text(), "PRIVATE API KEY")
            self.assertEqual(environment["SHOWROOM_APPLE_TEAM_ID"], "TEAM123456")
            self.assertEqual(environment["SAFE"], "1")
            self.assertEqual(self.security.search[0], str(load_profile(self.state).keychain_path))
        self.assertIsNotNone(key_path)
        self.assertFalse(key_path.exists())
        self.assertEqual(self.security.search, original_search)

    def test_delivery_context_requires_one_session_unlock(self) -> None:
        self.setup()
        lock_profile(self.state, runner=self.security, secrets=self.security)
        with self.assertRaisesRegex(ConfigurationError, "apple unlock"):
            with delivery_environment(
                self.state,
                surface="testflight",
                operation="verify",
                required=True,
                runner=self.security,
                secrets=self.security,
            ):
                pass

    def test_device_verify_does_not_need_a_profile(self) -> None:
        with delivery_environment(
            self.state,
            surface="device",
            operation="verify",
            required=False,
            base={"SAFE": "1"},
            runner=self.security,
            secrets=self.security,
        ) as environment:
            self.assertEqual(environment, {"SAFE": "1"})


if __name__ == "__main__":
    unittest.main()
