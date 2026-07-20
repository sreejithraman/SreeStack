"""Exact-UDID manager-owned Simulator allocation and ownership gates."""

from __future__ import annotations

import json
import re
from typing import Mapping, Sequence

from .ios_types import (
    CommandFailure,
    CommandResult,
    DiscoveryError,
    FORBIDDEN_SIMCTL_SELECTORS,
    IOSPreviewRequest,
    OwnershipDrift,
    SimulatorOwnership,
    SimulatorSpec,
    _ObservedDevice,
)


class IOSSimulatorLifecycleMixin:
    def _allocate_or_reuse_clone(
        self, request: IOSPreviewRequest, spec: SimulatorSpec
    ) -> SimulatorOwnership:
        records = list(self._ownership.list_ios_simulators())
        matching_clones = [
            record
            for record in records
            if record.role == "clone"
            and record.preview_id == request.preview_id
            and record.project_identity == request.project_identity
            and record.worktree_identity == request.worktree_identity
            and record.device_type_identifier == spec.device_type_identifier
            and record.runtime_identifier == spec.runtime_identifier
        ]
        if len(matching_clones) > 1:
            raise OwnershipDrift("multiple registered clones match this worktree")
        if matching_clones:
            record = matching_clones[0]
            self._assert_observed_ownership(record, self._observed_devices())
            return record

        templates = [
            record
            for record in records
            if record.role == "template"
            and record.manager_owned
            and record.device_type_identifier == spec.device_type_identifier
            and record.runtime_identifier == spec.runtime_identifier
        ]
        if len(templates) > 1:
            raise OwnershipDrift("multiple manager templates match the requested runtime")
        if templates:
            template = templates[0]
            self._assert_observed_ownership(template, self._observed_devices())
        else:
            template_name = self._safe_name(
                f"previewctl template {spec.device_name} {spec.runtime_name}"
            )
            create = self._checked(
                [
                    "xcrun",
                    "simctl",
                    "create",
                    template_name,
                    spec.device_type_identifier,
                    spec.runtime_identifier,
                ],
                cwd=request.worktree_root,
            )
            template_udid = create.stdout.strip()
            self._assert_exact_udid(template_udid)
            template = SimulatorOwnership(
                template_udid,
                template_name,
                "template",
                True,
                None,
                None,
                spec.device_type_identifier,
                spec.runtime_identifier,
            )
            # Ownership is persisted immediately, before any later mutation.
            self._ownership.save_ios_simulator(template)

        clone_name = self._safe_name(
            f"previewctl {request.preview_id} {request.worktree_identity[:8]}"
        )
        clone = self._checked(
            ["xcrun", "simctl", "clone", template.udid, clone_name],
            cwd=request.worktree_root,
        )
        clone_udid = clone.stdout.strip()
        self._assert_exact_udid(clone_udid)
        record = SimulatorOwnership(
            clone_udid,
            clone_name,
            "clone",
            True,
            request.project_identity,
            request.worktree_identity,
            spec.device_type_identifier,
            spec.runtime_identifier,
            template.udid,
            request.preview_id,
        )
        # The exact clone is registered before boot, install, launch, or capture.
        self._ownership.save_ios_simulator(record)
        return record

    def _observed_devices(self) -> dict[str, _ObservedDevice]:
        result = self._checked(["xcrun", "simctl", "list", "devices", "--json"])
        try:
            payload = json.loads(result.stdout)
            devices_by_runtime = payload["devices"]
            observed = {}
            for runtime, devices in devices_by_runtime.items():
                for device in devices:
                    udid = str(device["udid"])
                    observed[udid] = _ObservedDevice(
                        udid=udid,
                        name=str(device.get("name", "")),
                        state=str(device.get("state", "Unknown")),
                        runtime_identifier=str(runtime),
                        device_type_identifier=device.get("deviceTypeIdentifier"),
                        available=bool(device.get("isAvailable", True)),
                    )
            return observed
        except (AttributeError, KeyError, TypeError, json.JSONDecodeError) as error:
            raise DiscoveryError("simctl returned unsupported device JSON") from error

    def _assert_observed_ownership(
        self,
        record: SimulatorOwnership,
        devices: Mapping[str, _ObservedDevice],
    ) -> None:
        self._assert_exact_udid(record.udid)
        if not record.manager_owned:
            raise OwnershipDrift(f"Simulator {record.udid} is not manager-owned")
        observed = devices.get(record.udid)
        if observed is None:
            raise OwnershipDrift(f"registered Simulator {record.udid} is missing")
        if not observed.available:
            raise OwnershipDrift(f"registered Simulator {record.udid} is unavailable")
        if observed.runtime_identifier != record.runtime_identifier:
            raise OwnershipDrift(f"Simulator {record.udid} runtime ownership drift")
        if observed.device_type_identifier != record.device_type_identifier:
            raise OwnershipDrift(f"Simulator {record.udid} device-type ownership drift")

    @staticmethod
    def _assert_cleanup_authority(
        request: IOSPreviewRequest, record: SimulatorOwnership
    ) -> None:
        if not record.manager_owned or record.role != "clone":
            raise OwnershipDrift("cleanup requires an exact manager-owned clone")
        if record.project_identity != request.project_identity:
            raise OwnershipDrift("cleanup project identity does not match ownership")
        if record.worktree_identity != request.worktree_identity:
            raise OwnershipDrift("cleanup worktree identity does not match ownership")
        if record.preview_id != request.preview_id:
            raise OwnershipDrift("cleanup preview identity does not match ownership")

    @staticmethod
    def _assert_exact_udid(udid: str) -> None:
        if udid in FORBIDDEN_SIMCTL_SELECTORS or not re.fullmatch(
            r"[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}", udid
        ):
            raise OwnershipDrift(f"refusing non-exact Simulator UDID: {udid!r}")

    @classmethod
    def _assert_safe_commands(
        cls, commands: Sequence[Sequence[str]], expected_udid: str
    ) -> None:
        cls._assert_exact_udid(expected_udid)
        for command in commands:
            if "erase" in command or any(value in command for value in FORBIDDEN_SIMCTL_SELECTORS):
                raise OwnershipDrift(f"refusing broad Simulator command: {command!r}")
            if expected_udid not in command:
                raise OwnershipDrift("refusing Simulator command without the exact owned UDID")

    @staticmethod
    def _idempotent_cleanup_failure(
        command: Sequence[str], result: CommandResult
    ) -> bool:
        message = f"{result.stdout}\n{result.stderr}".lower()
        if command[1:3] == ["simctl", "terminate"]:
            return "not running" in message or "found nothing to terminate" in message
        if command[1:3] == ["simctl", "shutdown"]:
            return "shutdown" in message and "current state" in message
        if command[1:3] == ["simctl", "delete"]:
            return "invalid device" in message or "unable to find" in message
        return False
