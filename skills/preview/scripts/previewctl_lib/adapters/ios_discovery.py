"""Xcode container, scheme, destination, and product discovery."""

from __future__ import annotations

from datetime import timezone
import json
import os
from pathlib import Path
import re
from typing import Sequence

from .ios_types import (
    BuildProduct,
    CommandFailure,
    CommandResult,
    DiscoveryError,
    EXCLUDED_DISCOVERY_DIRECTORIES,
    IOSConfiguration,
    IOSPreviewRequest,
    SimulatorSpec,
    XcodeContainer,
)


class IOSDiscoveryMixin:
    def discover_container(self, request: IOSPreviewRequest) -> XcodeContainer:
        config = request.configuration
        if config.workspace and config.project:
            raise DiscoveryError("configure either an Xcode workspace or project, not both")
        if config.workspace:
            path = self._resolve_project_path(request.worktree_root, config.workspace)
            if path.suffix != ".xcworkspace" or not self._filesystem.exists(path):
                raise DiscoveryError(f"configured workspace does not exist: {path}")
            return XcodeContainer("workspace", path)
        if config.project:
            path = self._resolve_project_path(request.worktree_root, config.project)
            if path.suffix != ".xcodeproj" or not self._filesystem.exists(path):
                raise DiscoveryError(f"configured project does not exist: {path}")
            return XcodeContainer("project", path)

        workspaces = self._find_containers(request.worktree_root, ".xcworkspace")
        projects = self._find_containers(request.worktree_root, ".xcodeproj")
        if len(workspaces) == 1:
            return XcodeContainer("workspace", workspaces[0])
        if len(workspaces) > 1:
            raise DiscoveryError("multiple Xcode workspaces found; configure ios.workspace")
        if len(projects) == 1:
            return XcodeContainer("project", projects[0])
        if not projects:
            raise DiscoveryError("no Xcode project or workspace found")
        raise DiscoveryError("multiple Xcode projects found; configure ios.project")

    def discover_shared_scheme(
        self, request: IOSPreviewRequest, container: XcodeContainer
    ) -> str:
        result = self._checked(
            ["xcodebuild", *container.argv, "-list", "-json"],
            cwd=request.worktree_root,
        )
        try:
            payload = json.loads(result.stdout)
            listed = set(
                payload.get("workspace", payload.get("project", {})).get("schemes", [])
            )
        except (AttributeError, json.JSONDecodeError) as error:
            raise DiscoveryError("xcodebuild returned invalid scheme JSON") from error

        shared = {
            path.stem
            for path in self._shared_scheme_paths(request.worktree_root, container)
        }
        candidates = sorted(listed & shared)
        configured = request.configuration.scheme
        if configured:
            if configured not in listed:
                raise DiscoveryError(f"configured scheme is not listed: {configured}")
            if configured not in shared:
                raise DiscoveryError(f"configured scheme is not shared: {configured}")
            return configured
        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            raise DiscoveryError("no checked-in shared scheme found")
        raise DiscoveryError("multiple shared schemes found; configure ios.scheme")

    def discover_simulator_spec(self, config: IOSConfiguration) -> SimulatorSpec:
        result = self._checked(
            ["xcrun", "simctl", "list", "devicetypes", "runtimes", "--json"]
        )
        try:
            payload = json.loads(result.stdout)
            device_types = payload["devicetypes"]
            runtimes = payload["runtimes"]
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise DiscoveryError("simctl returned unsupported device/runtime JSON") from error

        type_matches = [
            item
            for item in device_types
            if (
                config.device_type_identifier
                and item.get("identifier") == config.device_type_identifier
            )
            or (
                not config.device_type_identifier
                and config.device
                and item.get("name") == config.device
            )
        ]
        if not config.device_type_identifier and not config.device:
            phones = [
                item for item in device_types if str(item.get("name", "")).startswith("iPhone")
            ]
            if phones:
                type_matches = [
                    max(
                        phones,
                        key=lambda item: (
                            self._version_key(str(item.get("name", "0"))),
                            "Pro" in str(item.get("name", "")),
                            str(item.get("name", "")),
                        ),
                    )
                ]
        if len(type_matches) != 1:
            raise DiscoveryError("Simulator device type is missing or ambiguous")
        device_type = type_matches[0]

        available_ios = [
            item
            for item in runtimes
            if item.get("isAvailable", True)
            and str(item.get("identifier", "")).startswith(
                "com.apple.CoreSimulator.SimRuntime.iOS-"
            )
        ]
        if config.runtime_identifier:
            available_ios = [
                item
                for item in available_ios
                if item.get("identifier") == config.runtime_identifier
            ]
        if not available_ios:
            raise DiscoveryError("no matching available iOS Simulator runtime found")
        if config.runtime_identifier and len(available_ios) != 1:
            raise DiscoveryError("configured Simulator runtime is ambiguous")
        runtime = max(
            available_ios,
            key=lambda item: self._version_key(
                str(item.get("version") or item.get("name") or "0")
            ),
        )
        return SimulatorSpec(
            str(device_type["identifier"]),
            str(runtime["identifier"]),
            str(device_type["name"]),
            str(runtime.get("name", runtime["identifier"])),
        )

    def _parse_build_product(
        self, output: str, configured_target: str | None
    ) -> BuildProduct:
        try:
            entries = json.loads(output)
        except json.JSONDecodeError as error:
            raise DiscoveryError("xcodebuild returned invalid build-settings JSON") from error
        candidates: list[BuildProduct] = []
        for entry in entries if isinstance(entries, list) else []:
            target = str(entry.get("target", ""))
            settings = entry.get("buildSettings", {})
            wrapper = settings.get("WRAPPER_NAME")
            build_dir = settings.get("TARGET_BUILD_DIR")
            bundle = settings.get("PRODUCT_BUNDLE_IDENTIFIER")
            if configured_target and target != configured_target:
                continue
            if not wrapper or not str(wrapper).endswith(".app") or not build_dir or not bundle:
                continue
            candidates.append(
                BuildProduct(
                    target=target,
                    app_path=Path(str(build_dir)) / str(wrapper),
                    bundle_identifier=str(bundle),
                    deployment_target=settings.get("IPHONEOS_DEPLOYMENT_TARGET"),
                    code_sign_style=settings.get("CODE_SIGN_STYLE"),
                )
            )
        if len(candidates) != 1:
            raise DiscoveryError(
                "build settings did not identify exactly one installable app product; "
                "configure ios.target"
            )
        return candidates[0]

    def _checked(
        self, argv: Sequence[str], *, cwd: Path | None = None
    ) -> CommandResult:
        result = self._runner.run(argv, cwd=cwd)
        if result.returncode != 0:
            raise CommandFailure(argv, result)
        return result

    @staticmethod
    def _xcodebuild_prefix(container: XcodeContainer, scheme: str) -> list[str]:
        return ["xcodebuild", *container.argv, "-scheme", scheme]

    def _attempt_directory(self, request: IOSPreviewRequest) -> Path:
        timestamp = self._clock().astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_preview_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", request.preview_id)
        return (
            request.state_directory
            / "previews"
            / safe_preview_id
            / "ios"
            / f"{timestamp}-{self._token_factory()}"
        )

    @staticmethod
    def _parse_launch_pid(output: str) -> int | None:
        match = re.search(r"(?::|\s)(\d+)\s*$", output.strip())
        return int(match.group(1)) if match else None

    @staticmethod
    def _version_key(value: str) -> tuple[int, ...]:
        numbers = re.findall(r"\d+", value)
        return tuple(int(number) for number in numbers) or (0,)

    @staticmethod
    def _safe_name(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_. -]+", "-", value)[:120]

    @staticmethod
    def _resolve_project_path(root: Path, configured: str) -> Path:
        candidate = (root / configured).resolve()
        resolved_root = root.resolve()
        try:
            candidate.relative_to(resolved_root)
        except ValueError as error:
            raise DiscoveryError(f"configured path escapes the worktree: {configured}") from error
        return candidate

    @staticmethod
    def _find_containers(root: Path, suffix: str) -> list[Path]:
        found: list[Path] = []
        for current, directories, _files in os.walk(root):
            directories[:] = [
                name
                for name in directories
                if name not in EXCLUDED_DISCOVERY_DIRECTORIES
                and not name.endswith((".xcodeproj", ".xcworkspace"))
            ]
            path = Path(current)
            for child in path.iterdir():
                if child.is_dir() and child.name.endswith(suffix):
                    found.append(child.resolve())
        return sorted(set(found))

    @staticmethod
    def _shared_scheme_paths(root: Path, container: XcodeContainer) -> list[Path]:
        direct = container.path / "xcshareddata" / "xcschemes"
        paths = list(direct.glob("*.xcscheme"))
        if container.kind == "workspace":
            paths.extend(root.glob("**/*.xcodeproj/xcshareddata/xcschemes/*.xcscheme"))
        return sorted(set(path.resolve() for path in paths))
