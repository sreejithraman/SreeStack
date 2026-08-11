"""Safe, injectable iOS Simulator showroom adapter.

The registry remains the authority for Simulator ownership.  Device names are
only diagnostics: every mutation uses an exact UDID, and deletion additionally
requires registry and observed-device ownership checks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time
from threading import Event, Thread
from typing import Any, Callable, Mapping, Protocol, Sequence
from uuid import uuid4

import fcntl



EXCLUDED_DISCOVERY_DIRECTORIES = frozenset(
    {".build", "build", "DerivedData", "Carthage", "Pods", "SourcePackages"}
)
FORBIDDEN_SIMCTL_SELECTORS = frozenset({"all", "booted", "unavailable"})


class IOSAdapterError(RuntimeError):
    """Base error for a conservatively stopped adapter operation."""


class DiscoveryError(IOSAdapterError):
    """The Xcode container, scheme, destination, or product was ambiguous."""


class CommandFailure(IOSAdapterError):
    """An external command failed."""

    def __init__(self, argv: Sequence[str], result: "CommandResult") -> None:
        self.argv = tuple(argv)
        self.result = result
        super().__init__(
            f"command failed ({result.returncode}): {argv[0]}; "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )


class OwnershipDrift(IOSAdapterError):
    """Registry ownership no longer agrees with observed Simulator state."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class CommandRunner(Protocol):
    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        timeout_seconds: float | None = None,
    ) -> CommandResult: ...


class SubprocessRunner:
    """Default argv-only runner.  It never invokes a shell."""

    def __init__(self, timeout_seconds: float = 20 * 60) -> None:
        self.timeout_seconds = timeout_seconds

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        timeout_seconds: float | None = None,
    ) -> CommandResult:
        timeout = self.timeout_seconds if timeout_seconds is None else timeout_seconds
        try:
            completed = subprocess.run(
                list(argv),
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                shell=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(124, "", f"command timed out after {timeout:.2f} seconds")
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)


class FileSystem(Protocol):
    def mkdir(self, path: Path) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def nonempty_file(self, path: Path) -> bool: ...


class LocalFileSystem:
    def mkdir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def nonempty_file(self, path: Path) -> bool:
        return path.is_file() and path.stat().st_size > 0


@dataclass(frozen=True)
class SimulatorOwnership:
    udid: str
    name: str
    role: str
    manager_owned: bool
    project_identity: str | None
    worktree_identity: str | None
    device_type_identifier: str
    runtime_identifier: str
    source_template_udid: str | None = None
    showroom_id: str | None = None


class OwnershipStore(Protocol):
    def list_ios_simulators(self) -> Sequence[SimulatorOwnership]: ...

    def get_ios_simulator(self, udid: str) -> SimulatorOwnership | None: ...

    def save_ios_simulator(self, record: SimulatorOwnership) -> None: ...

    def remove_ios_simulator(self, udid: str) -> None: ...


class JSONOwnershipStore:
    """Small locked sidecar written before a Simulator is subsequently mutated."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock_path = path.with_suffix(path.suffix + ".lock")

    def list_ios_simulators(self) -> Sequence[SimulatorOwnership]:
        with self._locked(write=False) as payload:
            return tuple(
                SimulatorOwnership(**item) for item in payload["simulators"].values()
            )

    def get_ios_simulator(self, udid: str) -> SimulatorOwnership | None:
        with self._locked(write=False) as payload:
            item = payload["simulators"].get(udid)
            return SimulatorOwnership(**item) if item else None

    def save_ios_simulator(self, record: SimulatorOwnership) -> None:
        with self._locked(write=True) as payload:
            existing = payload["simulators"].get(record.udid)
            serialized = asdict(record)
            if existing is not None and existing != serialized:
                raise OwnershipDrift(
                    f"refusing to overwrite conflicting ownership for {record.udid}"
                )
            payload["simulators"][record.udid] = serialized

    def remove_ios_simulator(self, udid: str) -> None:
        with self._locked(write=True) as payload:
            payload["simulators"].pop(udid, None)

    class _Lock:
        def __init__(self, owner: "JSONOwnershipStore", write: bool) -> None:
            self.owner = owner
            self.write = write
            self.handle: Any = None
            self.payload: dict[str, Any] = {}

        def __enter__(self) -> dict[str, Any]:
            self.owner.path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
            self.handle = self.owner.lock_path.open("a+", encoding="utf-8")
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
            if self.owner.path.exists():
                try:
                    self.payload = json.loads(
                        self.owner.path.read_text(encoding="utf-8")
                    )
                except (OSError, json.JSONDecodeError) as error:
                    raise OwnershipDrift("invalid iOS ownership registry") from error
            else:
                self.payload = {"version": 1, "simulators": {}}
            if self.payload.get("version") != 1 or not isinstance(
                self.payload.get("simulators"), dict
            ):
                raise OwnershipDrift("unsupported iOS ownership registry")
            return self.payload

        def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
            try:
                if exc_type is None and self.write:
                    file_descriptor, temporary = tempfile.mkstemp(
                        prefix=f".{self.owner.path.name}.",
                        dir=self.owner.path.parent,
                    )
                    try:
                        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
                            json.dump(self.payload, handle, indent=2, sort_keys=True)
                            handle.write("\n")
                            handle.flush()
                            os.fsync(handle.fileno())
                        os.chmod(temporary, 0o600)
                        os.replace(temporary, self.owner.path)
                    finally:
                        if os.path.exists(temporary):
                            os.unlink(temporary)
            finally:
                if self.handle is not None:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
                    self.handle.close()

    def _locked(self, *, write: bool) -> "JSONOwnershipStore._Lock":
        return self._Lock(self, write)


@dataclass(frozen=True)
class IOSConfiguration:
    workspace: str | None = None
    project: str | None = None
    scheme: str | None = None
    target: str | None = None
    configuration: str = "Debug"
    device: str | None = None
    device_type_identifier: str | None = None
    runtime_identifier: str | None = None
    deep_link: str | None = None
    launch_arguments: tuple[str, ...] = ()
    fixture: str | None = None
    recording: bool = False
    recording_seconds: float = 5.0


@dataclass(frozen=True)
class IOSShowroomRequest:
    showroom_id: str
    repository_root: Path
    worktree_root: Path
    state_directory: Path
    project_identity: str
    worktree_identity: str
    configuration: IOSConfiguration = field(default_factory=IOSConfiguration)


@dataclass(frozen=True)
class XcodeContainer:
    kind: str
    path: Path

    @property
    def argv(self) -> tuple[str, str]:
        return (f"-{self.kind}", str(self.path))


@dataclass(frozen=True)
class SimulatorSpec:
    device_type_identifier: str
    runtime_identifier: str
    device_name: str
    runtime_name: str


@dataclass(frozen=True)
class BuildProduct:
    target: str
    app_path: Path
    bundle_identifier: str
    deployment_target: str | None
    code_sign_style: str | None


@dataclass(frozen=True)
class IOSShowroomResult:
    showroom_id: str
    simulator_udid: str
    simulator_name: str
    container: str
    scheme: str
    target: str
    app_path: str
    bundle_identifier: str
    derived_data_path: str
    result_bundle_path: str
    evidence_paths: tuple[str, ...]
    log_paths: tuple[str, ...]
    verification_status: str
    verification_detail: str
    checks: Mapping[str, str]
    build_summary: Mapping[str, object]
    launch_pid: int | None
    device_type_identifier: str
    runtime_identifier: str
    deployment_target: str | None
    code_sign_style: str | None


@dataclass(frozen=True)
class CleanupResult:
    simulator_udid: str
    status: str
    commands: tuple[tuple[str, ...], ...]
    detail: str


@dataclass(frozen=True)
class _ObservedDevice:
    udid: str
    name: str
    state: str
    runtime_identifier: str
    device_type_identifier: str | None
    available: bool


class RecordingRunner(Protocol):
    def record(self, argv: Sequence[str], *, duration_seconds: float) -> CommandResult: ...


class SubprocessRecordingRunner:
    """Record one exact UDID, stopping only the process this object spawned."""

    def record(self, argv: Sequence[str], *, duration_seconds: float) -> CommandResult:
        process = subprocess.Popen(
            list(argv),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        assert process.stdout is not None
        assert process.stderr is not None
        started = Event()
        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []

        def drain(stream: Any, chunks: list[str], detect_start: bool) -> None:
            for line in iter(stream.readline, ""):
                chunks.append(line)
                if detect_start and "Recording started" in line:
                    started.set()

        readers = (
            Thread(target=drain, args=(process.stdout, stdout_chunks, False), daemon=True),
            Thread(target=drain, args=(process.stderr, stderr_chunks, True), daemon=True),
        )
        for reader in readers:
            reader.start()

        deadline = time.monotonic() + 10.0
        while not started.wait(timeout=0.05):
            if process.poll() is not None or time.monotonic() >= deadline:
                process.terminate()
                self._wait_for_exit(process)
                self._join_readers(readers)
                self._close_pipes(process)
                return CommandResult(
                    process.returncode or 1,
                    "".join(stdout_chunks),
                    "".join(stderr_chunks) + "recording did not start",
                )
        time.sleep(max(0.0, duration_seconds))
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            self._wait_for_exit(process)
            self._join_readers(readers)
            self._close_pipes(process)
            return CommandResult(
                1,
                "".join(stdout_chunks),
                "".join(stderr_chunks) + "recording timed out",
            )
        self._join_readers(readers)
        self._close_pipes(process)
        return CommandResult(
            process.returncode or 0,
            "".join(stdout_chunks),
            "".join(stderr_chunks),
        )

    @staticmethod
    def _wait_for_exit(process: subprocess.Popen[str]) -> None:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)

    @staticmethod
    def _join_readers(readers: Sequence[Thread]) -> None:
        for reader in readers:
            reader.join()

    @staticmethod
    def _close_pipes(process: subprocess.Popen[str]) -> None:
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
