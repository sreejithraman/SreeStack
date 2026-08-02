from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .errors import AdapterError, ConfigurationError


PROTOCOL_VERSION = 1
SURFACES = {"device", "testflight"}
OWNERS = {"manual", "provider"}
STATUSES = {"pending", "passed", "failed", "blocked", "stale"}
ARGUMENT_NAME = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")


def _object(
    value: Any,
    label: str,
    allowed: set[str],
    required: set[str],
    error_type: type[ConfigurationError | AdapterError] = ConfigurationError,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise error_type(f"{label} must be an object")
    unknown = set(value) - allowed
    missing = required - set(value)
    if unknown:
        raise error_type(f"{label} has unknown field(s): {', '.join(sorted(unknown))}")
    if missing:
        raise error_type(f"{label} is missing field(s): {', '.join(sorted(missing))}")
    return value


def _argv(
    value: Any,
    label: str,
    error_type: type[ConfigurationError | AdapterError] = ConfigurationError,
) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise error_type(f"{label} must be a nonempty command array")
    return tuple(value)


def validate_description(value: Any) -> dict[str, Any]:
    document = _object(
        value,
        "delivery description",
        {"protocol_version", "surfaces"},
        {"protocol_version", "surfaces"},
    )
    if type(document["protocol_version"]) is not int or document["protocol_version"] != PROTOCOL_VERSION:
        raise ConfigurationError(f"unsupported delivery protocol version: {document['protocol_version']!r}")
    raw_surfaces = document["surfaces"]
    if not isinstance(raw_surfaces, dict) or not raw_surfaces:
        raise ConfigurationError("delivery description surfaces must be a nonempty object")
    if set(raw_surfaces) - SURFACES:
        raise ConfigurationError("delivery description supports only device and testflight surfaces")
    surfaces: dict[str, Any] = {}
    for name, raw in raw_surfaces.items():
        item = _object(
            raw,
            f"delivery surface {name!r}",
            {"start", "verify", "lifecycle_owner", "provider", "required_arguments"},
            {"start", "verify", "lifecycle_owner", "required_arguments"},
        )
        owner = item["lifecycle_owner"]
        if not isinstance(owner, str) or owner not in OWNERS:
            raise ConfigurationError(f"delivery surface {name!r} has invalid lifecycle_owner")
        provider = item.get("provider")
        if provider is not None and (not isinstance(provider, str) or not provider):
            raise ConfigurationError(f"delivery surface {name!r} provider must be a nonempty string")
        if owner == "provider" and not provider:
            raise ConfigurationError(f"delivery surface {name!r} needs a provider")
        required_arguments = item["required_arguments"]
        if (
            not isinstance(required_arguments, list)
            or not all(
                isinstance(argument, str)
                and argument
                and ARGUMENT_NAME.fullmatch(argument)
                for argument in required_arguments
            )
            or len(set(required_arguments)) != len(required_arguments)
        ):
            raise ConfigurationError(f"delivery surface {name!r} required_arguments must be unique names")
        if name == "device" and (owner != "manual" or provider is not None or required_arguments):
            raise ConfigurationError(
                "device delivery must use manual ownership, no provider, and no required arguments"
            )
        if name == "testflight" and (
            owner != "provider" or not provider or required_arguments != ["build-number"]
        ):
            raise ConfigurationError(
                "testflight delivery must use provider ownership and require only build-number"
            )
        surfaces[name] = {
            "start": _argv(item["start"], f"delivery surface {name!r} start"),
            "verify": _argv(item["verify"], f"delivery surface {name!r} verify"),
            "lifecycle_owner": owner,
            "provider": provider,
            "required_arguments": tuple(required_arguments),
        }
    return {"protocol_version": PROTOCOL_VERSION, "surfaces": surfaces}


def describe(command: tuple[str, ...], cwd: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [*command, "describe", "--json"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConfigurationError(f"delivery describe failed: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise ConfigurationError(f"delivery describe failed: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ConfigurationError("delivery describe returned invalid JSON") from exc
    return validate_description(payload)


def _normalize_path(
    value: Any,
    label: str,
    roots: tuple[Path, ...],
    *,
    must_exist: bool = False,
) -> str:
    if not isinstance(value, str) or not value:
        raise AdapterError(f"delivery result {label} must be a nonempty path")
    raw = Path(value).expanduser()
    resolved = (roots[0] / raw).resolve(strict=False) if not raw.is_absolute() else raw.resolve(strict=False)
    if not any(_within(root, resolved) for root in roots):
        raise AdapterError(f"delivery result {label} must stay inside the worktree or Showroom state")
    if must_exist and not resolved.exists():
        raise AdapterError(f"delivery result {label} does not exist: {resolved}")
    return str(resolved)


def _within(root: Path, value: Path) -> bool:
    try:
        value.relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def validate_result(
    value: Any,
    *,
    surface: str,
    operation: str,
    worktree: Path,
    showroom_dir: Path,
) -> dict[str, Any]:
    allowed = {
        "protocol_version", "surface", "operation", "verification", "location", "provider",
        "provider_resource_id", "evidence_paths", "log_paths", "availability_limitations",
    }
    document = _object(
        value,
        "delivery result",
        allowed,
        {
            "protocol_version", "surface", "operation", "verification", "location",
            "evidence_paths", "log_paths", "availability_limitations",
        },
        AdapterError,
    )
    if type(document["protocol_version"]) is not int or document["protocol_version"] != PROTOCOL_VERSION:
        raise AdapterError(f"unsupported delivery result protocol version: {document['protocol_version']!r}")
    if document["surface"] != surface or document["operation"] != operation:
        raise AdapterError("delivery result surface or operation does not match the request")
    verification = _object(
        document["verification"],
        "delivery result verification",
        {"status", "detail", "checks"},
        {"status", "detail", "checks"},
        AdapterError,
    )
    if (
        not isinstance(verification["status"], str)
        or verification["status"] not in STATUSES
        or not isinstance(verification["detail"], str)
    ):
        raise AdapterError("delivery result has invalid verification status or detail")
    checks = verification["checks"]
    if not isinstance(checks, dict) or not all(
        isinstance(key, str)
        and key
        and isinstance(value, str)
        and value in STATUSES
        for key, value in checks.items()
    ):
        raise AdapterError("delivery result verification checks must map names to status values")
    location = _object(
        document["location"],
        "delivery result location",
        {"url", "device", "artifact", "command"},
        set(),
        AdapterError,
    )
    normalized_location = {"url": None, "device": None, "artifact": None, "command": None}
    normalized_location.update(location)
    if normalized_location["command"] is not None:
        normalized_location["command"] = list(
            _argv(
                normalized_location["command"],
                "delivery result location command",
                AdapterError,
            )
        )
    for key in ("url", "device"):
        if normalized_location[key] is not None and (
            not isinstance(normalized_location[key], str) or not normalized_location[key]
        ):
            raise AdapterError(f"delivery result location {key} must be a nonempty string")
    roots = (worktree.resolve(strict=False), showroom_dir.resolve(strict=False))
    if normalized_location["artifact"] is not None:
        normalized_location["artifact"] = _normalize_path(
            normalized_location["artifact"], "location artifact", roots, must_exist=True
        )
    if not any(value is not None for value in normalized_location.values()):
        raise AdapterError("delivery result needs a location")
    expected_location = "device" if surface == "device" else "url"
    if normalized_location[expected_location] is None:
        raise AdapterError(f"{surface} delivery result needs location {expected_location}")
    provider = document.get("provider")
    resource_id = document.get("provider_resource_id")
    for label, value in (("provider", provider), ("provider_resource_id", resource_id)):
        if value is not None and (not isinstance(value, str) or not value):
            raise AdapterError(f"delivery result {label} must be a nonempty string")
    limitations = document["availability_limitations"]
    if not isinstance(limitations, list) or not all(isinstance(item, str) and item for item in limitations):
        raise AdapterError("delivery result availability_limitations must be a string array")
    evidence = document["evidence_paths"]
    logs = document["log_paths"]
    if not isinstance(evidence, list) or not isinstance(logs, list):
        raise AdapterError("delivery result evidence_paths and log_paths must be arrays")
    return {
        "verification": {"status": verification["status"], "detail": verification["detail"], "checks": checks},
        "location": normalized_location,
        "provider": provider,
        "provider_resource_id": resource_id,
        "evidence_paths": [
            _normalize_path(item, "evidence path", roots, must_exist=True) for item in evidence
        ],
        "log_paths": [
            _normalize_path(item, "log path", roots, must_exist=True) for item in logs
        ],
        "availability_limitations": list(limitations),
    }


def run_delivery(
    *,
    command: tuple[str, ...],
    operation_argv: tuple[str, ...],
    surface: str,
    operation: str,
    arguments: dict[str, str],
    required_arguments: tuple[str, ...],
    worktree: Path,
    showroom_dir: Path,
) -> dict[str, Any]:
    missing = [name for name in required_arguments if not arguments.get(name)]
    if missing:
        raise ConfigurationError(f"{surface} requires: {', '.join('--' + name for name in missing)}")
    showroom_dir.mkdir(parents=True, exist_ok=True)
    result_path = showroom_dir / f"delivery-{surface}-{operation}.json"
    log_path = showroom_dir / f"delivery-{surface}-{operation}.log"
    result_path.unlink(missing_ok=True)
    argv = [*command, *operation_argv]
    for name in required_arguments:
        argv.extend((f"--{name}", arguments[name]))
    argv.extend(("--result-json", str(result_path)))
    try:
        completed = subprocess.run(
            argv, cwd=worktree, check=False, capture_output=True, text=True, shell=False, timeout=20 * 60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdapterError(f"delivery {operation} failed: {exc}") from exc
    log_path.write_text(
        f"command: {json.dumps(argv)}\nexit: {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        encoding="utf-8",
    )
    os.chmod(log_path, 0o600)
    if not result_path.is_file():
        raise AdapterError(f"delivery {operation} did not write result JSON; see {log_path}")
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError(f"delivery {operation} wrote invalid result JSON; see {log_path}") from exc
    result = validate_result(
        payload, surface=surface, operation=operation, worktree=worktree, showroom_dir=showroom_dir,
    )
    if completed.returncode != 0 and result["verification"]["status"] == "passed":
        raise AdapterError(f"delivery {operation} exited {completed.returncode} but reported passed; see {log_path}")
    result["log_paths"] = [*result["log_paths"], str(log_path)]
    return result
