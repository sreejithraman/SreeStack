from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "skills" / "showroom" / "scripts" / "showroom"


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.state = self.root / "state"
        self.env = {
            **os.environ,
            "SHOWROOM_STATE_DIR": str(self.state),
            "SHOWROOM_NOW": "2026-01-02T03:04:05Z",
        }

    def run_cli(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([str(CLI), *args], cwd=self.repo, env=self.env, text=True, capture_output=True)
        if ok and result.returncode != 0:
            self.fail(f"showroom failed ({result.returncode}): {result.stderr}\n{result.stdout}")
        return result

    def test_json_command_lifecycle(self) -> None:
        started = json.loads(self.run_cli("start", "--adapter", "evidence-only", "--json").stdout)
        identifier = started["id"]
        status = json.loads(self.run_cli("status", identifier, "--json").stdout)
        self.assertEqual(status["id"], identifier)
        self.assertTrue(json.loads(self.run_cli("pin", identifier, "--json").stdout)["pinned"])
        self.assertFalse(json.loads(self.run_cli("unpin", identifier, "--json").stdout)["pinned"])
        renewed = json.loads(self.run_cli("renew", identifier, "--hours", "12", "--json").stdout)
        self.assertEqual(renewed["timestamps"]["expires_at"], "2026-01-02T15:04:05Z")
        records = json.loads(self.run_cli("list", "--json").stdout)
        self.assertEqual([record["id"] for record in records], [identifier])
        stopped = json.loads(self.run_cli("stop", identifier, "--json").stdout)
        self.assertEqual(stopped["status"], "stopped")

    def test_register_hosted_surface(self) -> None:
        result = self.run_cli(
            "register",
            "--adapter", "vercel",
            "--type", "url",
            "--provider", "vercel",
            "--provider-resource-id", "dep_123",
            "--url", "https://showroom.example.invalid",
            "--verification-status", "passed",
            "--json",
        )
        record = json.loads(result.stdout)
        self.assertEqual(record["surface"]["url"], "https://showroom.example.invalid")
        self.assertIsNone(record["timestamps"]["expires_at"])

    def test_malformed_registry_returns_structured_error(self) -> None:
        self.state.mkdir()
        (self.state / "registry.json").write_text("not-json", encoding="utf-8")
        result = self.run_cli("list", "--json", ok=False)
        self.assertEqual(result.returncode, 2)
        error = json.loads(result.stderr)
        self.assertEqual(error["type"], "RegistryError")

    def test_cleanup_dry_run_does_not_create_state(self) -> None:
        result = self.run_cli("cleanup", "--dry-run", "--json")
        self.assertEqual(json.loads(result.stdout)["actions"], [])
        self.assertFalse(self.state.exists())

    def test_cli_does_not_write_bytecode_into_skill(self) -> None:
        skill = self.root / "showroom"
        shutil.copytree(
            ROOT / "skills" / "showroom",
            skill,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        env = dict(self.env)
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        env.pop("PYTHONPYCACHEPREFIX", None)

        result = subprocess.run(
            [str(skill / "scripts" / "showroom"), "--version"],
            cwd=self.repo,
            env=env,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(skill.rglob("__pycache__")), [])
        self.assertEqual(list(skill.rglob("*.pyc")), [])

    def test_verify_failed_exits_one_with_json_record(self) -> None:
        record = json.loads(self.run_cli("start", "--adapter", "evidence-only", "--json").stdout)
        result = self.run_cli("verify", record["id"], "--json", ok=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["verification"]["status"], "failed")

    def test_project_dotfile_is_not_executed(self) -> None:
        marker = self.root / "marker"
        (self.repo / ".unrelated-tool.toml").write_text(f'kind = "web"\ncommand = "touch {marker}"\n', encoding="utf-8")
        self.run_cli("start", "--adapter", "evidence-only", "--json")
        self.assertFalse(marker.exists())

    def test_apple_status_without_profiles_is_empty(self) -> None:
        result = json.loads(self.run_cli("apple", "status", "--json").stdout)
        self.assertEqual(result, {"default_profile": None, "profiles": []})


if __name__ == "__main__":
    unittest.main()
