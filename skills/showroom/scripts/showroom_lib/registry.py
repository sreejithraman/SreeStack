from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar

from .errors import RegistryError


SCHEMA_VERSION = 1
T = TypeVar("T")


def empty_registry() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "records": {}}


def _validate(data: Any, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RegistryError(f"registry root is not an object: {path}")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError(f"unsupported registry schema version in {path}: {data.get('schema_version')!r}")
    records = data.get("records")
    if not isinstance(records, dict):
        raise RegistryError(f"registry records is not an object: {path}")
    for key, value in records.items():
        if not isinstance(key, str) or not isinstance(value, dict) or value.get("id") != key:
            raise RegistryError(f"registry contains an invalid record: {key!r}")
        _validate_record(value, path)
    return data


def _validate_record(record: dict[str, Any], path: Path) -> None:
    """Enforce the runtime boundary needed by lifecycle code.

    The checked-in JSON Schema remains the portable contract. This standard-
    library validation deliberately covers every field core operations index so
    a corrupt or hand-edited registry fails closed instead of causing partial
    lifecycle mutations.
    """
    required = {
        "record_version", "id", "type", "adapter", "registered", "lifecycle_owner", "cleanup_policy", "profile",
        "status", "repository", "worktree", "surface", "resources", "verification",
        "evidence_paths", "log_paths", "timestamps", "lease_hours", "pinned",
        "availability_limitations", "commands",
    }
    missing = sorted(required - record.keys())
    if missing:
        raise RegistryError(f"registry record {record.get('id')!r} is missing {', '.join(missing)}: {path}")
    if record["record_version"] != 1:
        raise RegistryError(f"unsupported record version for {record['id']!r}: {record['record_version']!r}")
    for field in ("id", "type", "adapter", "lifecycle_owner", "profile", "status"):
        if not isinstance(record[field], str) or not record[field]:
            raise RegistryError(f"registry record {record.get('id')!r} has invalid {field}: {path}")
    if record["status"] not in {"starting", "active", "stopping", "stopped"}:
        raise RegistryError(f"registry record {record['id']!r} has invalid status: {record['status']!r}")
    if record["lifecycle_owner"] not in {"showroom", "provider", "pull-request", "manual"}:
        raise RegistryError(f"registry record {record['id']!r} has invalid lifecycle owner: {record['lifecycle_owner']!r}")
    if record["cleanup_policy"] not in {"lease", "manual", "provider", "pull-request"}:
        raise RegistryError(f"registry record {record['id']!r} has invalid cleanup policy: {record['cleanup_policy']!r}")
    if not isinstance(record["registered"], bool):
        raise RegistryError(f"registry record {record['id']!r} has invalid registered marker: {path}")
    for field in ("repository", "worktree", "surface", "resources", "verification", "timestamps", "commands"):
        if not isinstance(record[field], dict):
            raise RegistryError(f"registry record {record['id']!r} has invalid {field}: {path}")
    repository = record["repository"]
    for field in ("id", "path", "common_directory"):
        if not isinstance(repository.get(field), str) or not repository[field]:
            raise RegistryError(f"registry record {record['id']!r} has invalid repository.{field}: {path}")
    if repository.get("source") is not None and not isinstance(repository.get("source"), str):
        raise RegistryError(f"registry record {record['id']!r} has invalid repository.source: {path}")
    worktree = record["worktree"]
    for field in ("id", "path"):
        if not isinstance(worktree.get(field), str) or not worktree[field]:
            raise RegistryError(f"registry record {record['id']!r} has invalid worktree.{field}: {path}")
    surface = record["surface"]
    if set(surface) != {"url", "device", "artifact", "command"}:
        raise RegistryError(f"registry record {record['id']!r} has invalid surface fields: {path}")
    for field in ("url", "device", "artifact"):
        if surface[field] is not None and not isinstance(surface[field], str):
            raise RegistryError(f"registry record {record['id']!r} has invalid surface.{field}: {path}")
    command = surface["command"]
    if command is not None and (
        not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command)
    ):
        raise RegistryError(f"registry record {record['id']!r} has invalid surface.command: {path}")
    if not {"process", "launchd", "port", "simulator_udid"}.issubset(record["resources"]):
        raise RegistryError(f"registry record {record['id']!r} is missing core resource fields: {path}")
    for field in ("evidence_paths", "log_paths", "availability_limitations"):
        if not isinstance(record[field], list) or not all(isinstance(item, str) for item in record[field]):
            raise RegistryError(f"registry record {record['id']!r} has invalid {field}: {path}")
    if not {"status", "checked_at", "detail"}.issubset(record["verification"]):
        raise RegistryError(f"registry record {record['id']!r} is missing verification fields: {path}")
    verification_status = record["verification"].get("status")
    if verification_status not in {"pending", "passed", "failed", "blocked", "stale"}:
        raise RegistryError(f"registry record {record['id']!r} has invalid verification status: {verification_status!r}")
    checked_at = record["verification"].get("checked_at")
    if checked_at is not None:
        _validate_timestamp(checked_at, record["id"], "verification.checked_at", path)
    detail = record["verification"].get("detail")
    if detail is not None and not isinstance(detail, str):
        raise RegistryError(f"registry record {record['id']!r} has invalid verification.detail: {path}")
    if set(record["timestamps"]) != {"created_at", "renewed_at", "expires_at"}:
        raise RegistryError(f"registry record {record['id']!r} has invalid timestamp fields: {path}")
    for field in ("created_at", "renewed_at"):
        _validate_timestamp(record["timestamps"].get(field), record["id"], f"timestamps.{field}", path)
    expiration = record["timestamps"].get("expires_at")
    if expiration is not None:
        _validate_timestamp(expiration, record["id"], "timestamps.expires_at", path)
    if isinstance(record["lease_hours"], bool) or not isinstance(record["lease_hours"], (int, float)) or record["lease_hours"] <= 0:
        raise RegistryError(f"registry record {record['id']!r} has invalid lease: {path}")
    if not isinstance(record["pinned"], bool):
        raise RegistryError(f"registry record {record['id']!r} has invalid pinned state: {path}")
    expected_commands = {"inspect", "verify", "renew", "pin", "unpin", "stop"}
    if set(record["commands"]) != expected_commands or not all(
        isinstance(value, str) and value for value in record["commands"].values()
    ):
        raise RegistryError(f"registry record {record['id']!r} has invalid lifecycle commands: {path}")
    operation = record.get("operation")
    if record["status"] == "stopping":
        if not isinstance(operation, dict) or set(operation) != {"kind", "started_at", "previous_status"}:
            raise RegistryError(f"stopping registry record {record['id']!r} has invalid operation journal: {path}")
        if operation["kind"] != "stop" or operation["previous_status"] not in {"starting", "active"}:
            raise RegistryError(f"stopping registry record {record['id']!r} has invalid operation values: {path}")
        _validate_timestamp(operation["started_at"], record["id"], "operation.started_at", path)
    elif operation is not None:
        raise RegistryError(f"non-stopping registry record {record['id']!r} contains an operation journal: {path}")


def _validate_timestamp(value: Any, record_id: str, field: str, path: Path) -> None:
    if not isinstance(value, str):
        raise RegistryError(f"registry record {record_id!r} has invalid {field}: {path}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryError(f"registry record {record_id!r} has unparseable {field}: {path}") from exc
    if parsed.tzinfo is None:
        raise RegistryError(f"registry record {record_id!r} has timezone-free {field}: {path}")


class Registry:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / "registry.json"
        self.lock_path = root / "registry.lock"

    def read(self) -> dict[str, Any]:
        """Read an atomic snapshot without creating state (safe for dry-runs)."""
        if not self.path.exists():
            return empty_registry()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RegistryError(f"cannot read registry {self.path}: {exc}") from exc
        return _validate(data, self.path)

    @contextmanager
    def _locked(self) -> Iterator[None]:
        root_existed = self.root.exists()
        self.root.mkdir(parents=True, mode=0o700, exist_ok=True)
        if not root_existed:
            self.root.chmod(0o700)
        descriptor = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        with os.fdopen(descriptor, "a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    @contextmanager
    def resource_lock(self, scope: str = "global") -> Iterator[None]:
        """Serialize one adapter resource namespace across CLI processes."""
        root_existed = self.root.exists()
        self.root.mkdir(parents=True, mode=0o700, exist_ok=True)
        if not root_existed:
            self.root.chmod(0o700)
        digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:16]
        lock_path = self.root / f"resources.{digest}.lock"
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        with os.fdopen(descriptor, "a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _write_locked(self, data: dict[str, Any]) -> None:
        _validate(data, self.path)
        descriptor, temporary_name = tempfile.mkstemp(prefix=".registry.", suffix=".tmp", dir=self.root)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            directory_fd = os.open(self.root, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if temporary.exists():
                temporary.unlink()

    def update(self, operation: Callable[[dict[str, Any]], T]) -> T:
        with self._locked():
            data = self.read()
            result = operation(data)
            self._write_locked(data)
            return result

    def get(self, showroom_id: str) -> dict[str, Any] | None:
        record = self.read()["records"].get(showroom_id)
        return copy.deepcopy(record) if record else None

    def put(self, record: dict[str, Any]) -> dict[str, Any]:
        def operation(data: dict[str, Any]) -> dict[str, Any]:
            data["records"][record["id"]] = copy.deepcopy(record)
            return copy.deepcopy(record)

        return self.update(operation)

    def delete_if(self, showroom_id: str, predicate: Callable[[dict[str, Any]], bool]) -> bool:
        def operation(data: dict[str, Any]) -> bool:
            current = data["records"].get(showroom_id)
            if current is None or not predicate(current):
                return False
            del data["records"][showroom_id]
            return True

        return self.update(operation)
