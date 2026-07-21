"""Orchestration for a verified iOS Simulator review surface."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from .ios_discovery import IOSDiscoveryMixin
from .ios_simulators import IOSSimulatorLifecycleMixin
from .ios_types import (
    BuildProduct,
    CleanupResult,
    CommandFailure,
    CommandRunner,
    FileSystem,
    IOSAdapterError,
    IOSPreviewRequest,
    IOSPreviewResult,
    LocalFileSystem,
    OwnershipDrift,
    OwnershipStore,
    RecordingRunner,
    SimulatorOwnership,
    SimulatorSpec,
    XcodeContainer,
    SubprocessRecordingRunner,
    SubprocessRunner,
)
from uuid import uuid4


@dataclass(frozen=True)
class _BuildPhase:
    product: BuildProduct
    derived_data: Path
    result_bundle: Path
    stdout_log: Path
    stderr_log: Path
    summary: dict[str, Any]


@dataclass(frozen=True)
class _RunPhase:
    evidence: tuple[str, ...]
    launch_pid: int | None
    navigation: str


class IOSSimulatorAdapter(IOSDiscoveryMixin, IOSSimulatorLifecycleMixin):
    def __init__(
        self,
        runner: CommandRunner | None,
        ownership: OwnershipStore,
        *,
        filesystem: FileSystem | None = None,
        clock: Callable[[], datetime] | None = None,
        token_factory: Callable[[], str] | None = None,
        recording_runner: RecordingRunner | None = None,
    ) -> None:
        self._runner = runner or SubprocessRunner()
        self._ownership = ownership
        self._filesystem = filesystem or LocalFileSystem()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_factory = token_factory or (lambda: uuid4().hex[:12])
        self._recording_runner = recording_runner or SubprocessRecordingRunner()

    def start(self, request: IOSPreviewRequest) -> IOSPreviewResult:
        container = self.discover_container(request)
        scheme = self.discover_shared_scheme(request, container)
        spec = self.discover_simulator_spec(request.configuration)
        existing_udids = {
            record.udid for record in self._ownership.list_ios_simulators()
        }
        simulator = self._allocate_or_reuse_clone(request, spec)
        created_by_attempt = simulator.udid not in existing_udids
        try:
            self._assert_observed_ownership(simulator, self._observed_devices())
            build = self._build(request, container, scheme, simulator)
            run = self._install_launch_and_capture(request, simulator, build)
        except Exception:
            if created_by_attempt:
                try:
                    self.cleanup(request, simulator.udid)
                except IOSAdapterError:
                    # Keep the exact ownership record when rollback cannot safely
                    # converge; a retry or janitor can reconcile only this UDID.
                    pass
            raise
        return IOSPreviewResult(
            preview_id=request.preview_id,
            simulator_udid=simulator.udid,
            simulator_name=simulator.name,
            container=str(container.path),
            scheme=scheme,
            target=build.product.target,
            app_path=str(build.product.app_path),
            bundle_identifier=build.product.bundle_identifier,
            derived_data_path=str(build.derived_data),
            result_bundle_path=str(build.result_bundle),
            evidence_paths=run.evidence,
            log_paths=(str(build.stdout_log), str(build.stderr_log)),
            verification_status="passed",
            verification_detail=(
                "build, install, launch, configured navigation, and screenshot capture "
                "succeeded; app state was not asserted by a UI test"
            ),
            checks={
                "discovery": "passed",
                "build": "passed",
                "install": "passed",
                "launch": "passed",
                "navigation": run.navigation,
                "visual_evidence": "passed",
                "ui_assertion": "not-configured",
            },
            build_summary=build.summary,
            launch_pid=run.launch_pid,
            device_type_identifier=spec.device_type_identifier,
            runtime_identifier=spec.runtime_identifier,
            deployment_target=build.product.deployment_target,
            code_sign_style=build.product.code_sign_style,
        )

    def _build(
        self,
        request: IOSPreviewRequest,
        container: XcodeContainer,
        scheme: str,
        simulator: SimulatorOwnership,
    ) -> "_BuildPhase":
        destinations = self._checked(
            self._xcodebuild_prefix(container, scheme) + ["-showdestinations"],
            cwd=request.worktree_root,
        )
        if simulator.udid not in destinations.stdout:
            raise DiscoveryError(
                f"scheme {scheme!r} does not report Simulator {simulator.udid} "
                "as an available destination"
            )

        destination = f"platform=iOS Simulator,id={simulator.udid}"
        attempt = self._attempt_directory(request)
        derived_data = attempt / "DerivedData"
        result_bundle = attempt / "build.xcresult"
        self._filesystem.mkdir(attempt)
        settings = self._checked(
            self._xcodebuild_prefix(container, scheme)
            + [
                "-configuration",
                request.configuration.configuration,
                "-destination",
                destination,
                "-derivedDataPath",
                str(derived_data),
                "-showBuildSettings",
                "-json",
            ],
            cwd=request.worktree_root,
        )
        product = self._parse_build_product(
            settings.stdout, request.configuration.target
        )
        argv = self._xcodebuild_prefix(container, scheme) + [
            "-configuration",
            request.configuration.configuration,
            "-destination",
            destination,
            "-derivedDataPath",
            str(derived_data),
            "-resultBundlePath",
            str(result_bundle),
            "build",
        ]
        completed = self._runner.run(argv, cwd=request.worktree_root)
        if completed.returncode != 0:
            raise CommandFailure(argv, completed)
        summary = self._build_summary(result_bundle, request.worktree_root)
        if not self._filesystem.exists(product.app_path):
            raise IOSAdapterError(
                f"resolved app product does not exist after build: {product.app_path}"
            )
        return _BuildPhase(
            product,
            derived_data,
            result_bundle,
            attempt / "app.stdout.log",
            attempt / "app.stderr.log",
            summary,
        )

    def _build_summary(self, result_bundle: Path, cwd: Path) -> dict[str, Any]:
        completed = self._checked(
            [
                "xcrun",
                "xcresulttool",
                "get",
                "build-results",
                "--path",
                str(result_bundle),
            ],
            cwd=cwd,
        )
        try:
            summary = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise IOSAdapterError(
                "xcresulttool returned invalid build-results JSON"
            ) from error
        if not isinstance(summary, dict):
            raise IOSAdapterError("xcresulttool build-results summary is not an object")
        return summary

    def _install_launch_and_capture(
        self,
        request: IOSPreviewRequest,
        simulator: SimulatorOwnership,
        build: "_BuildPhase",
    ) -> "_RunPhase":
        current = self._observed_devices()[simulator.udid]
        if current.state != "Booted":
            self._checked(
                ["xcrun", "simctl", "boot", simulator.udid],
                cwd=request.worktree_root,
            )
        self._checked(
            ["xcrun", "simctl", "install", simulator.udid, str(build.product.app_path)],
            cwd=request.worktree_root,
        )
        self._checked(
            [
                "xcrun",
                "simctl",
                "appinfo",
                simulator.udid,
                build.product.bundle_identifier,
            ],
            cwd=request.worktree_root,
        )
        self._install_fixture(request, simulator)
        launch = self._checked(
            [
                "xcrun",
                "simctl",
                "launch",
                "--terminate-running-process",
                f"--stdout={build.stdout_log}",
                f"--stderr={build.stderr_log}",
                simulator.udid,
                build.product.bundle_identifier,
                *request.configuration.launch_arguments,
            ],
            cwd=request.worktree_root,
        )
        navigation = self._navigate(request, simulator)
        evidence = self._capture_evidence(request, simulator, build)
        return _RunPhase(tuple(evidence), self._parse_launch_pid(launch.stdout), navigation)

    def _install_fixture(
        self, request: IOSPreviewRequest, simulator: SimulatorOwnership
    ) -> None:
        if not request.configuration.fixture:
            return
        fixture = self._resolve_project_path(
            request.worktree_root, request.configuration.fixture
        )
        self._checked(
            ["xcrun", "simctl", "install_app_data", simulator.udid, str(fixture)],
            cwd=request.worktree_root,
        )

    def _navigate(
        self, request: IOSPreviewRequest, simulator: SimulatorOwnership
    ) -> str:
        if not request.configuration.deep_link:
            return "not-configured"
        self._checked(
            [
                "xcrun",
                "simctl",
                "openurl",
                simulator.udid,
                request.configuration.deep_link,
            ],
            cwd=request.worktree_root,
        )
        return "deep-link-opened (value redacted)"

    def _capture_evidence(
        self,
        request: IOSPreviewRequest,
        simulator: SimulatorOwnership,
        build: "_BuildPhase",
    ) -> list[str]:
        screenshot = build.result_bundle.parent / "screenshot.png"
        self._checked(
            ["xcrun", "simctl", "io", simulator.udid, "screenshot", str(screenshot)],
            cwd=request.worktree_root,
        )
        if not self._filesystem.nonempty_file(screenshot):
            raise IOSAdapterError(f"screenshot was not created or is empty: {screenshot}")
        evidence = [str(build.result_bundle), str(screenshot)]
        if not request.configuration.recording:
            return evidence

        recording = build.result_bundle.parent / "recording.mov"
        argv = [
            "xcrun",
            "simctl",
            "io",
            simulator.udid,
            "recordVideo",
            str(recording),
        ]
        completed = self._recording_runner.record(
            argv, duration_seconds=request.configuration.recording_seconds
        )
        if completed.returncode != 0:
            raise CommandFailure(argv, completed)
        if not self._filesystem.nonempty_file(recording):
            raise IOSAdapterError(
                f"recording was not created or is empty: {recording}"
            )
        evidence.append(str(recording))
        return evidence

    def verify(self, result: IOSPreviewResult) -> IOSPreviewResult:
        record = self._ownership.get_ios_simulator(result.simulator_udid)
        if record is None:
            return replace(
                result,
                verification_status="stale",
                verification_detail="registered Simulator ownership is missing",
            )
        try:
            devices = self._observed_devices()
            self._assert_observed_ownership(record, devices)
        except OwnershipDrift as error:
            return replace(
                result, verification_status="stale", verification_detail=str(error)
            )
        appinfo = self._runner.run(
            [
                "xcrun",
                "simctl",
                "appinfo",
                result.simulator_udid,
                result.bundle_identifier,
            ]
        )
        evidence_ok = any(
            path.endswith((".png", ".mov")) and self._filesystem.nonempty_file(Path(path))
            for path in result.evidence_paths
        )
        if appinfo.returncode != 0 or not evidence_ok:
            return replace(
                result,
                verification_status="failed",
                verification_detail="installed app or captured visual evidence is unavailable",
            )
        return replace(
            result,
            verification_status="passed",
            verification_detail=(
                "exact Simulator, installed app, and visual evidence were reconciled; "
                "app state was not asserted by a UI test"
            ),
        )

    def cleanup(
        self,
        request: IOSPreviewRequest,
        simulator_udid: str,
        *,
        bundle_identifier: str | None = None,
        dry_run: bool = False,
    ) -> CleanupResult:
        self._assert_exact_udid(simulator_udid)
        record = self._ownership.get_ios_simulator(simulator_udid)
        if record is None:
            return CleanupResult(simulator_udid, "absent", (), "not registered")
        self._assert_cleanup_authority(request, record)

        devices = self._observed_devices()
        observed = devices.get(simulator_udid)
        if observed is None:
            if not dry_run:
                self._ownership.remove_ios_simulator(simulator_udid)
            return CleanupResult(
                simulator_udid,
                "would-remove-stale-registration" if dry_run else "absent",
                (),
                "the exact registered device is already absent",
            )
        self._assert_observed_ownership(record, devices)

        commands: list[list[str]] = []
        if observed.state == "Booted" and bundle_identifier:
            commands.append(
                ["xcrun", "simctl", "terminate", simulator_udid, bundle_identifier]
            )
        if observed.state != "Shutdown":
            commands.append(["xcrun", "simctl", "shutdown", simulator_udid])
        commands.append(["xcrun", "simctl", "delete", simulator_udid])
        self._assert_safe_commands(commands, simulator_udid)

        frozen_commands = tuple(tuple(command) for command in commands)
        if dry_run:
            return CleanupResult(
                simulator_udid,
                "would-delete",
                frozen_commands,
                "dry-run; no command or state mutation performed",
            )

        # The source worktree may have been deleted because lease reconciliation
        # is one reason cleanup runs.  Execute only from manager-owned state,
        # which we can safely recreate, rather than depending on that worktree.
        cleanup_cwd = request.state_directory
        self._filesystem.mkdir(cleanup_cwd)
        for command in commands:
            result = self._runner.run(command, cwd=cleanup_cwd)
            if result.returncode != 0 and not self._idempotent_cleanup_failure(
                command, result
            ):
                raise CommandFailure(command, result)
        self._ownership.remove_ios_simulator(simulator_udid)
        return CleanupResult(
            simulator_udid, "deleted", frozen_commands, "exact manager clone deleted"
        )
