from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "showroom" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from showroom_lib.core import (  # noqa: E402
    cleanup,
    cleanup_candidates,
    get_record,
    new_record,
    register,
    renew,
    set_pinned,
    start,
    stop,
    verify,
)
from showroom_lib.adapters.base import EvidenceAdapter, RegisteredSurfaceAdapter  # noqa: E402
from showroom_lib.errors import AdapterError, ConfigurationError, RegistryError  # noqa: E402
from showroom_lib.paths import state_root  # noqa: E402
from showroom_lib.project import ProjectConfig, Project, detect_project, detect_config, showroom_id  # noqa: E402
from showroom_lib.registry import Registry  # noqa: E402


NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)


class RepositoryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "showroom@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Showroom Tests"], check=True)
        (self.repo / "README.md").write_text("test\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "initial"], check=True)
        self.state = self.root / "state"
        self.registry = Registry(self.state)


class ProjectTests(RepositoryCase):
    def test_worktrees_share_project_but_have_distinct_identity_and_showroom_ids(self) -> None:
        linked = self.root / "linked"
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "-q", "-b", "linked", str(linked)], check=True)
        first = detect_project(self.repo)
        second = detect_project(linked)
        self.assertEqual(first.repository_id, second.repository_id)
        self.assertNotEqual(first.worktree_id, second.worktree_id)
        self.assertNotEqual(showroom_id(first, "web-local", "default"), showroom_id(second, "web-local", "default"))

    def test_remote_http_credentials_are_not_persisted(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", "https://secret@example.com/team/repo.git"], check=True)
        self.assertEqual(detect_project(self.repo).source, "https://example.com/team/repo.git")

    def test_config_detects_native_project_files_without_a_showroom_file(self) -> None:
        (self.repo / "package.json").write_text('{"scripts":{"dev":"vite"}}', encoding="utf-8")
        config = detect_config(detect_project(self.repo))
        self.assertEqual(config.kind, "web")
        self.assertEqual(config.command, ("npm", "run", "dev", "--", "--port", "{port}"))
        self.assertEqual(config.working_directory, self.repo.resolve())


class RegistryTests(RepositoryCase):
    def test_atomic_registry_preserves_concurrent_updates(self) -> None:
        project = detect_project(self.repo)
        config = detect_config(project)
        barrier = threading.Barrier(8)

        def write(index: int) -> None:
            record = new_record(project, config, f"adapter-{index}", NOW)
            barrier.wait()
            self.registry.put(record)

        threads = [threading.Thread(target=write, args=(index,)) for index in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(self.registry.read()["records"]), 8)

    def test_malformed_registry_is_not_overwritten(self) -> None:
        self.state.mkdir()
        original = b'{"schema_version": 1, "records": '
        self.registry.path.write_bytes(original)
        with self.assertRaises(RegistryError):
            self.registry.put({"id": "anything"})
        self.assertEqual(self.registry.path.read_bytes(), original)

    def test_state_root_precedence(self) -> None:
        self.assertEqual(state_root({"SHOWROOM_STATE_DIR": str(self.root / "custom")}), (self.root / "custom").resolve())
        self.assertEqual(state_root({"HOME": "/Users/example"}, "darwin"), Path("/Users/example/Library/Application Support/showroom"))
        self.assertEqual(state_root({"HOME": "/home/example", "XDG_STATE_HOME": "/state"}, "linux"), Path("/state/showroom"))

    def test_created_state_directory_is_private(self) -> None:
        project = detect_project(self.repo)
        self.registry.put(new_record(project, detect_config(project), "evidence-only", NOW))
        self.assertEqual(stat.S_IMODE(self.state.stat().st_mode), 0o700)

    def test_registry_rejects_missing_nested_fields_and_bad_timestamps(self) -> None:
        project = detect_project(self.repo)
        for mutate in (
            lambda record: record.update(worktree={}),
            lambda record: record["timestamps"].update(created_at="not-a-time"),
        ):
            with self.subTest(mutate=mutate):
                record = new_record(project, detect_config(project), "evidence-only", NOW)
                mutate(record)
                with self.assertRaises(RegistryError):
                    self.registry.put(record)

    def test_registry_requires_a_recoverable_stopping_journal(self) -> None:
        project = detect_project(self.repo)
        record = new_record(project, detect_config(project), "evidence-only", NOW)
        record["status"] = "stopping"
        with self.assertRaisesRegex(RegistryError, "operation journal"):
            self.registry.put(record)


class GenericAdapterTests(unittest.TestCase):
    def test_unexecuted_command_is_not_marked_verified(self) -> None:
        patch = EvidenceAdapter().verify(
            {"surface": {"artifact": None, "command": ["example"]}, "evidence_paths": []},
            None,
        )
        self.assertEqual("blocked", patch["verification"]["status"])

    def test_command_with_nonempty_execution_evidence_is_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "transcript.txt"
            transcript.write_text("example output\n", encoding="utf-8")
            patch = EvidenceAdapter().verify(
                {
                    "surface": {"artifact": None, "command": ["example"]},
                    "evidence_paths": [str(transcript)],
                },
                None,
            )
        self.assertEqual("passed", patch["verification"]["status"])

    def test_missing_primary_artifact_is_failed_even_if_command_is_also_present(self) -> None:
        patch = EvidenceAdapter().verify(
            {
                "surface": {"artifact": "/definitely/missing", "command": ["example"]},
                "evidence_paths": [],
            },
            None,
        )
        self.assertEqual("failed", patch["verification"]["status"])

    def test_registered_url_is_verified_without_provider_deployment_logic(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.status = 204
        with mock.patch("showroom_lib.adapters.base.urllib.request.urlopen", return_value=response):
            patch = RegisteredSurfaceAdapter().verify(
                {"surface": {"url": "https://example.invalid"}}, None
            )
        self.assertEqual("passed", patch["verification"]["status"])


class LifecycleTests(RepositoryCase):
    def _start(self) -> dict:
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
            return start(self.registry, self.state, self.repo, "evidence-only")

    def test_start_is_idempotent(self) -> None:
        first = self._start()
        second = self._start()
        self.assertEqual(first, second)
        self.assertEqual(len(self.registry.read()["records"]), 1)

    def test_failed_start_removes_only_its_reservation(self) -> None:
        class FailingAdapter:
            def start(self, record, context):
                raise RuntimeError("origin failed")

        with mock.patch("showroom_lib.core.load_adapter", return_value=FailingAdapter()):
            with self.assertRaisesRegex(AdapterError, "origin failed"):
                self._start()
        self.assertEqual(self.registry.read()["records"], {})

    def test_stale_starting_reservation_can_recover(self) -> None:
        project = detect_project(self.repo)
        config = detect_config(project)
        stale = new_record(project, config, "evidence-only", datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.registry.put(stale)
        recovered = self._start()
        self.assertEqual(recovered["status"], "active")
        self.assertEqual(recovered["timestamps"]["created_at"], "2026-01-02T03:04:05Z")

    def test_active_start_reconciles_and_restarts_failed_adapter(self) -> None:
        class FakeAdapter:
            starts = 0
            stops = 0

            def start(self, record, context):
                self.starts += 1
                return {"status": "active", "verification": {"status": "passed", "detail": "started"}}

            def verify(self, record, context):
                return {"verification": {"status": "failed", "detail": "unhealthy"}}

            def stop(self, record, context):
                self.stops += 1
                return {"status": "stopped"}

        adapter = FakeAdapter()
        with mock.patch("showroom_lib.core.load_adapter", return_value=adapter):
            with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
                first = start(self.registry, self.state, self.repo, "fake-local")
                second = start(self.registry, self.state, self.repo, "fake-local")
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(adapter.starts, 2)
        self.assertEqual(adapter.stops, 1)
        self.assertEqual(second["verification"]["status"], "passed")

    def test_adapter_allocations_are_serialized_across_projects(self) -> None:
        second_repo = self.root / "repo-two"
        second_repo.mkdir()
        subprocess.run(["git", "init", "-q", str(second_repo)], check=True)

        class AllocatingAdapter:
            def __init__(inner_self):
                inner_self.active = 0
                inner_self.maximum = 0
                inner_self.guard = threading.Lock()

            def start(inner_self, record, context):
                with inner_self.guard:
                    inner_self.active += 1
                    inner_self.maximum = max(inner_self.maximum, inner_self.active)
                time.sleep(0.05)
                with inner_self.guard:
                    inner_self.active -= 1
                return {"status": "active", "verification": {"status": "passed", "detail": "allocated"}}

        adapter = AllocatingAdapter()
        errors: list[Exception] = []

        def begin(repository: Path) -> None:
            try:
                start(self.registry, self.state, repository, "web-local")
            except Exception as exc:  # pragma: no cover - assertion reports the captured error
                errors.append(exc)

        with mock.patch("showroom_lib.core.load_adapter", return_value=adapter):
            threads = [threading.Thread(target=begin, args=(repository,)) for repository in (self.repo, second_repo)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.assertEqual([], errors)
        self.assertEqual(1, adapter.maximum)

    def test_expired_active_start_stops_and_replaces_exact_record(self) -> None:
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-01T00:00:00Z"}):
            expired = start(self.registry, self.state, self.repo, "evidence-only")
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-03T00:00:00Z"}):
            replacement = start(self.registry, self.state, self.repo, "evidence-only")
        self.assertEqual(expired["id"], replacement["id"])
        self.assertEqual(replacement["status"], "active")
        self.assertEqual(replacement["timestamps"]["created_at"], "2026-01-03T00:00:00Z")
        self.assertEqual(len(self.registry.read()["records"]), 1)

    def test_stale_starting_reservation_invokes_exact_adapter_recovery(self) -> None:
        project = detect_project(self.repo)
        config = detect_config(project)
        stale = new_record(project, config, "recoverable", datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.registry.put(stale)

        class RecoverableAdapter:
            recovered = False

            def recover(self, record, context):
                self.recovered = True

            def start(self, record, context):
                return {"status": "active", "verification": {"status": "passed", "detail": "recovered"}}

        adapter = RecoverableAdapter()
        with mock.patch("showroom_lib.core.load_adapter", return_value=adapter), mock.patch.dict(
            os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}
        ):
            recovered = start(self.registry, self.state, self.repo, "recoverable")
        self.assertTrue(adapter.recovered)
        self.assertEqual("active", recovered["status"])

    def test_renew_pin_and_unpin(self) -> None:
        record = self._start()
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-03T00:00:00Z"}):
            renewed = renew(self.registry, record["id"], 48)
        self.assertEqual(renewed["timestamps"]["expires_at"], "2026-01-05T00:00:00Z")
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
            pinned = set_pinned(self.registry, record["id"], True)
            self.assertTrue(pinned["pinned"])
            self.assertIsNone(pinned["timestamps"]["expires_at"])
            renewed_pinned = renew(self.registry, record["id"], 72)
            self.assertIsNone(renewed_pinned["timestamps"]["expires_at"])
            unpinned = set_pinned(self.registry, record["id"], False)
        self.assertFalse(unpinned["pinned"])
        self.assertEqual(unpinned["timestamps"]["expires_at"], "2026-01-05T03:04:05Z")

    def test_verify_preserves_a_concurrent_pin(self) -> None:
        record = self._start()

        class PinningAdapter:
            def verify(inner_self, current, context):
                set_pinned(self.registry, current["id"], True)
                return {"verification": {"status": "passed", "detail": "checked"}}

        with mock.patch("showroom_lib.core._load_record_adapter", return_value=PinningAdapter()):
            checked = verify(self.registry, self.state, record["id"])
        self.assertTrue(checked["pinned"])
        self.assertIsNone(checked["timestamps"]["expires_at"])
        self.assertEqual("passed", checked["verification"]["status"])

    def test_verify_refuses_to_overwrite_a_concurrent_stop_claim(self) -> None:
        record = self._start()

        class RacingAdapter:
            def verify(inner_self, current, context):
                def claim(data):
                    claimed = data["records"][current["id"]]
                    claimed["status"] = "stopping"
                    claimed["operation"] = {
                        "kind": "stop",
                        "started_at": "2026-01-02T03:04:05Z",
                        "previous_status": "active",
                    }
                self.registry.update(claim)
                return {"verification": {"status": "passed", "detail": "late"}}

        with mock.patch("showroom_lib.core._load_record_adapter", return_value=RacingAdapter()):
            with self.assertRaisesRegex(AdapterError, "lifecycle changed"):
                verify(self.registry, self.state, record["id"])
        self.assertEqual("stopping", self.registry.get(record["id"])["status"])

    def test_stale_stop_claim_is_recoverable(self) -> None:
        record = self._start()

        def interrupted(data):
            current = data["records"][record["id"]]
            current["status"] = "stopping"
            current["operation"] = {
                "kind": "stop",
                "started_at": "2026-01-01T00:00:00Z",
                "previous_status": "active",
            }

        self.registry.update(interrupted)
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
            stopped = stop(self.registry, self.state, record["id"])
        self.assertEqual("stopped", stopped["status"])
        self.assertNotIn("operation", stopped)

    def test_start_never_overwrites_an_in_progress_stop(self) -> None:
        record = self._start()

        def stopping(data):
            current = data["records"][record["id"]]
            current["status"] = "stopping"
            current["operation"] = {
                "kind": "stop",
                "started_at": "2026-01-02T03:04:04Z",
                "previous_status": "active",
            }

        self.registry.update(stopping)
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
            with self.assertRaisesRegex(AdapterError, "stop already in progress"):
                start(self.registry, self.state, self.repo, "evidence-only")
        self.assertEqual("stopping", self.registry.get(record["id"])["status"])

    def test_lease_expiry_and_pinning_are_deterministic(self) -> None:
        record = self._start()
        later = datetime(2026, 1, 4, tzinfo=timezone.utc)
        self.assertEqual(cleanup_candidates([record], later)[0]["reasons"], ["expired lease"])
        record["pinned"] = True
        self.assertEqual(cleanup_candidates([record], later), [])

    def test_cleanup_dry_run_is_byte_for_byte_immutable(self) -> None:
        record = self._start()
        before_registry = self.registry.path.read_bytes()
        before_files = sorted(path.relative_to(self.state) for path in self.state.rglob("*"))
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-04T00:00:00Z"}):
            result = cleanup(self.registry, self.state, dry_run=True)
        self.assertEqual(result["actions"][0]["id"], record["id"])
        self.assertEqual(self.registry.path.read_bytes(), before_registry)
        self.assertEqual(sorted(path.relative_to(self.state) for path in self.state.rglob("*")), before_files)

    def test_missing_worktree_is_cleanup_candidate(self) -> None:
        record = self._start()
        record["worktree"]["path"] = str(self.root / "gone")
        candidates = cleanup_candidates([record], NOW)
        self.assertIn("missing worktree", candidates[0]["reasons"])

    def test_cleanup_removes_expired_owned_record(self) -> None:
        record = self._start()
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-04T00:00:00Z"}):
            result = cleanup(self.registry, self.state, dry_run=False)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["actions"][0]["id"], record["id"])
        with self.assertRaises(ConfigurationError):
            get_record(self.registry, record["id"])

    def test_register_is_idempotent_and_preserves_pin(self) -> None:
        project = detect_project(self.repo)
        kwargs = dict(
            adapter="vercel",
            profile="pr",
            record_type="url",
            provider="vercel",
            provider_resource_id="dep_123",
            lifecycle_owner="provider",
            surface={"url": "https://example.invalid"},
            verification_status="passed",
            evidence_paths=[],
            log_paths=[],
            limitations=["provider lifecycle"],
            lease_hours=168,
        )
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
            first = register(self.registry, project, **kwargs)
        set_pinned(self.registry, first["id"], True)
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-03T03:04:05Z"}):
            second = register(self.registry, project, **kwargs)
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(first["timestamps"]["created_at"], second["timestamps"]["created_at"])
        self.assertTrue(second["pinned"])

    def test_stop_provider_record_stops_only_its_local_registration(self) -> None:
        project = detect_project(self.repo)
        record = register(
            self.registry,
            project,
            adapter="vercel-deploy",
            profile="pr",
            record_type="url",
            provider="vercel",
            provider_resource_id="dep_123",
            lifecycle_owner="provider",
            surface={"url": "https://example.invalid"},
            verification_status="passed",
            evidence_paths=[],
            log_paths=[],
            limitations=["provider resource remains externally owned"],
            lease_hours=None,
        )
        stopped = stop(self.registry, self.state, record["id"])
        self.assertEqual("stopped", stopped["status"])
        self.assertIn("external lifecycle is unchanged", stopped["verification"]["detail"])

    def test_provider_owned_registration_never_gets_a_guessed_expiration(self) -> None:
        project = detect_project(self.repo)
        record = register(
            self.registry,
            project,
            adapter="vercel-deploy",
            profile="provider-lease",
            record_type="url",
            provider="vercel",
            provider_resource_id="dep_lease",
            lifecycle_owner="provider",
            surface={"url": "https://example.invalid"},
            verification_status="passed",
            evidence_paths=[],
            log_paths=[],
            limitations=[],
            lease_hours=None,
        )
        self.assertIsNone(record["timestamps"]["expires_at"])
        pinned = set_pinned(self.registry, record["id"], True)
        self.assertIsNone(pinned["timestamps"]["expires_at"])
        unpinned = set_pinned(self.registry, record["id"], False)
        self.assertIsNone(unpinned["timestamps"]["expires_at"])
        renewed = renew(self.registry, record["id"], 168)
        self.assertIsNone(renewed["timestamps"]["expires_at"])

    def test_register_refuses_to_replace_manager_owned_local_record(self) -> None:
        local = self._start()
        project = detect_project(self.repo)
        with self.assertRaisesRegex(AdapterError, "manager-owned local resources"):
            register(
                self.registry,
                project,
                adapter="evidence-only",
                profile="default",
                record_type="artifact",
                provider=None,
                provider_resource_id=None,
                lifecycle_owner="showroom",
                surface={"artifact": "README.md"},
                verification_status="passed",
                evidence_paths=[],
                log_paths=[],
                limitations=[],
                lease_hours=None,
            )
        self.assertEqual(local, self.registry.get(local["id"]))

    def test_register_refuses_a_conflicting_provider_resource(self) -> None:
        project = detect_project(self.repo)
        common = dict(
            adapter="vercel-deploy",
            profile="pr",
            record_type="url",
            provider="vercel",
            lifecycle_owner="provider",
            surface={"url": "https://example.invalid"},
            verification_status="passed",
            evidence_paths=[],
            log_paths=[],
            limitations=[],
            lease_hours=None,
        )
        register(self.registry, project, provider_resource_id="dep_123", **common)
        with self.assertRaisesRegex(AdapterError, "identity conflicts"):
            register(self.registry, project, provider_resource_id="dep_456", **common)

    def test_register_normalizes_relative_artifact_and_evidence_paths(self) -> None:
        project = detect_project(self.repo)
        record = register(
            self.registry,
            project,
            adapter="evidence-only",
            profile="artifact",
            record_type="artifact",
            provider=None,
            provider_resource_id=None,
            lifecycle_owner="showroom",
            surface={"artifact": "README.md"},
            verification_status="pending",
            evidence_paths=["README.md"],
            log_paths=["showroom.log"],
            limitations=[],
            lease_hours=24,
        )
        self.assertEqual(record["surface"]["artifact"], str((self.repo / "README.md").resolve()))
        self.assertEqual(record["evidence_paths"], [str((self.repo / "README.md").resolve())])
        self.assertEqual(record["log_paths"], [str((self.repo / "showroom.log").resolve())])

    def test_local_evidence_registration_defaults_to_a_24_hour_lease(self) -> None:
        project = detect_project(self.repo)
        with mock.patch.dict(os.environ, {"SHOWROOM_NOW": "2026-01-02T03:04:05Z"}):
            record = register(
                self.registry,
                project,
                adapter="evidence-only",
                profile="local",
                record_type="artifact",
                provider=None,
                provider_resource_id=None,
                lifecycle_owner="showroom",
                surface={"artifact": "README.md"},
                verification_status="pending",
                evidence_paths=[],
                log_paths=[],
                limitations=[],
                lease_hours=None,
            )
        self.assertEqual(24, record["lease_hours"])
        self.assertEqual("2026-01-03T03:04:05Z", record["timestamps"]["expires_at"])


if __name__ == "__main__":
    unittest.main()
