"""previewctl integration for the safe iOS Simulator adapter."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from ..errors import AdapterError as CoreAdapterError
from .base import AdapterContext
from .ios_engine import IOSSimulatorAdapter
from .ios_types import (
    CommandFailure,
    CommandResult,
    CommandRunner,
    DiscoveryError,
    FileSystem,
    IOSAdapterError,
    IOSConfiguration,
    IOSPreviewRequest,
    IOSPreviewResult,
    JSONOwnershipStore,
    OwnershipDrift,
    OwnershipStore,
    RecordingRunner,
    SimulatorOwnership,
    SubprocessRecordingRunner,
)


class Adapter:
    """previewctl loader integration around the independently testable adapter."""

    name = "ios-simulator"

    def __init__(
        self,
        *,
        runner: CommandRunner | None = None,
        filesystem: FileSystem | None = None,
        clock: Callable[[], datetime] | None = None,
        token_factory: Callable[[], str] | None = None,
        recording_runner: RecordingRunner | None = None,
        ownership_factory: Callable[[Path], OwnershipStore] = JSONOwnershipStore,
    ) -> None:
        self._runner = runner
        self._filesystem = filesystem
        self._clock = clock
        self._token_factory = token_factory
        self._recording_runner = recording_runner
        self._ownership_factory = ownership_factory

    def start(
        self, record: dict[str, Any], context: AdapterContext
    ) -> dict[str, Any]:
        store_path = context.state_root / "ios-simulators.json"
        request = self._request(record, context, store_path)
        manager = self._manager(store_path)
        try:
            result = manager.start(request)
        except IOSAdapterError as error:
            raise CoreAdapterError(str(error)) from error
        return {
            "status": "active",
            "surface": {
                "device": f"{result.simulator_name} ({result.simulator_udid})",
                "artifact": next(
                    (
                        path
                        for path in result.evidence_paths
                        if path.endswith((".png", ".mov"))
                    ),
                    None,
                ),
            },
            "resources": {
                "simulator_udid": result.simulator_udid,
                "ios_ownership_store": str(store_path),
                "ios": {
                    "device_type_identifier": result.device_type_identifier,
                    "runtime_identifier": result.runtime_identifier,
                    "bundle_identifier": result.bundle_identifier,
                    "app_path": result.app_path,
                    "derived_data_path": result.derived_data_path,
                    "result_bundle_path": result.result_bundle_path,
                },
            },
            "verification": {
                "status": result.verification_status,
                "detail": result.verification_detail,
                "checks": dict(result.checks),
            },
            "evidence_paths": list(result.evidence_paths),
            "log_paths": list(result.log_paths),
            "availability_limitations": [
                "Available only on this Mac while its Simulator and Xcode runtime remain installed.",
                "Simulator does not reproduce every physical-device capability or performance characteristic.",
            ],
            "adapter_state": {"ios_result": asdict(result)},
        }

    def verify(
        self, record: dict[str, Any], context: AdapterContext | None
    ) -> dict[str, Any]:
        try:
            result = self._stored_result(record)
            store_path = self._store_path(record, context)
            verified = self._manager(store_path).verify(result)
        except IOSAdapterError as error:
            return {"verification": {"status": "stale", "detail": str(error)}}
        return {
            "verification": {
                "status": verified.verification_status,
                "detail": verified.verification_detail,
                "checks": dict(verified.checks),
            },
            "adapter_state": {"ios_result": asdict(verified)},
        }

    def stop(
        self, record: dict[str, Any], context: AdapterContext | None
    ) -> dict[str, Any]:
        resources = record.get("resources", {})
        udid = resources.get("simulator_udid")
        if not udid:
            return {"status": "stopped"}
        store_path = self._store_path(record, context)
        request = self._request(record, context, store_path)
        bundle = resources.get("ios", {}).get("bundle_identifier")
        try:
            result = self._manager(store_path).cleanup(
                request, str(udid), bundle_identifier=bundle
            )
        except IOSAdapterError as error:
            raise CoreAdapterError(str(error)) from error
        return {
            "status": "stopped",
            "verification": {
                "status": "stale",
                "detail": result.detail,
            },
        }

    def recover(
        self, record: dict[str, Any], context: AdapterContext
    ) -> dict[str, Any] | None:
        """Remove an interrupted start's exact worktree-owned clone."""
        store_path = context.state_root / "ios-simulators.json"
        request = self._request(record, context, store_path)
        manager = self._manager(store_path)
        matches = [
            item
            for item in self._ownership_factory(store_path).list_ios_simulators()
            if item.role == "clone"
            and item.manager_owned
            and item.preview_id == request.preview_id
            and item.project_identity == request.project_identity
            and item.worktree_identity == request.worktree_identity
        ]
        if len(matches) > 1:
            raise CoreAdapterError("multiple manager-owned Simulator clones match interrupted preview start")
        if not matches:
            return None
        try:
            result = manager.cleanup(request, matches[0].udid)
        except IOSAdapterError as error:
            raise CoreAdapterError(str(error)) from error
        return {"status": "stopped", "verification": {"status": "stale", "detail": result.detail}}

    def cleanup_plan(
        self, record: dict[str, Any], context: AdapterContext | None
    ) -> dict[str, Any]:
        resources = record.get("resources", {})
        udid = resources.get("simulator_udid")
        if not udid:
            return {"dry_run": True, "commands": [], "detail": "no registered Simulator"}
        store_path = self._store_path(record, context)
        request = self._request(record, context, store_path)
        bundle = resources.get("ios", {}).get("bundle_identifier")
        try:
            result = self._manager(store_path).cleanup(
                request, str(udid), bundle_identifier=bundle, dry_run=True
            )
        except IOSAdapterError as error:
            raise CoreAdapterError(str(error)) from error
        return {
            "dry_run": True,
            "commands": [list(command) for command in result.commands],
            "detail": result.detail,
        }

    def _manager(self, store_path: Path) -> IOSSimulatorAdapter:
        return IOSSimulatorAdapter(
            self._runner,
            self._ownership_factory(store_path),
            filesystem=self._filesystem,
            clock=self._clock,
            token_factory=self._token_factory,
            recording_runner=self._recording_runner,
        )

    @staticmethod
    def _configuration(context: AdapterContext | None) -> IOSConfiguration:
        raw = dict(context.manifest.ios) if context is not None else {}
        launch_arguments = raw.get("launch_arguments", ())
        if not isinstance(launch_arguments, (list, tuple)) or not all(
            isinstance(value, str) for value in launch_arguments
        ):
            raise CoreAdapterError("manifest ios.launch_arguments must be a string array")
        return IOSConfiguration(
            workspace=raw.get("workspace"),
            project=raw.get("project"),
            scheme=raw.get("scheme"),
            target=raw.get("target"),
            configuration=raw.get("configuration", "Debug"),
            device=raw.get("device"),
            device_type_identifier=raw.get("device_type_identifier"),
            runtime_identifier=raw.get("runtime_identifier"),
            deep_link=raw.get("deep_link"),
            launch_arguments=tuple(launch_arguments),
            fixture=raw.get("fixture"),
            recording=bool(raw.get("recording", False)),
            recording_seconds=float(raw.get("recording_seconds", 5.0)),
        )

    @classmethod
    def _request(
        cls,
        record: dict[str, Any],
        context: AdapterContext | None,
        store_path: Path,
    ) -> IOSPreviewRequest:
        if context is not None:
            project = context.project
            repository_root = project.repository_root
            worktree_root = project.worktree_root
            project_identity = project.repository_id
            worktree_identity = project.worktree_id
        else:
            repository = record.get("repository", {})
            worktree = record.get("worktree", {})
            repository_root = Path(repository.get("path", "."))
            worktree_root = Path(worktree.get("path", "."))
            project_identity = str(repository.get("id", ""))
            worktree_identity = str(worktree.get("id", ""))
        return IOSPreviewRequest(
            preview_id=str(record["id"]),
            repository_root=repository_root,
            worktree_root=worktree_root,
            state_directory=store_path.parent,
            project_identity=project_identity,
            worktree_identity=worktree_identity,
            configuration=cls._configuration(context),
        )

    @staticmethod
    def _store_path(
        record: dict[str, Any], context: AdapterContext | None
    ) -> Path:
        stored = record.get("resources", {}).get("ios_ownership_store")
        if stored:
            return Path(stored)
        if context is not None:
            return context.state_root / "ios-simulators.json"
        raise IOSAdapterError("iOS ownership registry path is missing")

    @staticmethod
    def _stored_result(record: dict[str, Any]) -> IOSPreviewResult:
        raw = record.get("adapter_state", {}).get("ios_result")
        if not isinstance(raw, dict):
            raise IOSAdapterError("iOS verification metadata is missing")
        raw = dict(raw)
        raw["evidence_paths"] = tuple(raw.get("evidence_paths", ()))
        raw["log_paths"] = tuple(raw.get("log_paths", ()))
        return IOSPreviewResult(**raw)


def get_adapter() -> Adapter:
    return Adapter()
