from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tomllib
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigurationError


MANIFEST_NAME = ".preview.toml"
KINDS = {"web", "ios", "android", "desktop", "api", "cli", "library", "infrastructure", "data", "evidence"}
PRIVACY_VALUES = {"private", "tailnet", "public-requires-approval"}
EVIDENCE_VALUES = {"http", "screenshot", "recording", "transcript", "artifact", "report"}
MANIFEST_KEYS = {
    "version", "kind", "working_directory", "command", "port", "health_check_path",
    "hosted_provider", "privacy", "evidence", "evidence_requirements", "lease_hours",
    "cleanup", "cleanup_policy", "profile", "ios",
}


@dataclass(frozen=True)
class Project:
    repository_root: Path
    repository_common_dir: Path
    worktree_root: Path
    repository_id: str
    worktree_id: str
    source: str | None


@dataclass(frozen=True)
class Manifest:
    path: Path | None
    version: int
    kind: str
    working_directory: Path
    command: tuple[str, ...] | None
    port: str | int
    health_check_path: str
    hosted_provider: str | None
    privacy: str
    evidence: tuple[str, ...]
    lease_hours: float
    cleanup_policy: str
    profile: str
    ios: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "kind": self.kind,
            "working_directory": str(self.working_directory),
            "command": list(self.command) if self.command else None,
            "port": self.port,
            "health_check_path": self.health_check_path,
            "hosted_provider": self.hosted_provider,
            "privacy": self.privacy,
            "evidence": list(self.evidence),
            "lease_hours": self.lease_hours,
            "cleanup_policy": self.cleanup_policy,
            "profile": self.profile,
            "ios": self.ios,
        }


def _git(cwd: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or None


def _digest(value: str, length: int = 20) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _safe_source(value: str | None) -> str | None:
    """Remove HTTP userinfo so credentials can never enter machine state."""
    if not value:
        return None
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        return value
    if "@" in parsed.netloc:
        host = parsed.hostname or ""
        if parsed.port:
            host = f"{host}:{parsed.port}"
    else:
        host = parsed.netloc
    return urllib.parse.urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def detect_project(cwd: Path | None = None) -> Project:
    requested = (cwd or Path.cwd()).expanduser().resolve(strict=True)
    top = _git(requested, "rev-parse", "--show-toplevel")
    if top:
        worktree = Path(top).resolve(strict=True)
        common_text = _git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if common_text is None:
            common_text = _git(worktree, "rev-parse", "--git-common-dir")
        if common_text is None:
            raise ConfigurationError("git did not report a common directory")
        common = Path(common_text)
        if not common.is_absolute():
            common = worktree / common
        common = common.resolve(strict=False)
        # A normal repository's common dir is <root>/.git; linked worktrees share it.
        repository_root = common.parent if common.name == ".git" else worktree
        source = _safe_source(_git(worktree, "config", "--get", "remote.origin.url"))
    else:
        worktree = requested
        repository_root = requested
        common = requested
        source = None

    return Project(
        repository_root=repository_root,
        repository_common_dir=common,
        worktree_root=worktree,
        repository_id=_digest(os.path.normcase(str(common))),
        worktree_id=_digest(os.path.normcase(str(worktree))),
        source=source,
    )


def _detect_kind(root: Path) -> str:
    if any(root.glob("*.xcworkspace")) or any(root.glob("*.xcodeproj")):
        return "ios"
    if (root / "package.json").is_file():
        return "web"
    if any((root / name).is_file() for name in ("Dockerfile", "compose.yaml", "docker-compose.yml")):
        return "web"
    if any((root / name).is_file() for name in ("pyproject.toml", "Cargo.toml", "go.mod")):
        return "library"
    return "evidence"


def _detect_command(root: Path, kind: str) -> tuple[str, ...] | None:
    if kind != "web" or not (root / "package.json").is_file():
        return None
    try:
        package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        return None
    for name in ("dev", "start"):
        if isinstance(scripts.get(name), str):
            return ("npm", "run", name, "--", "--port", "{port}")
    return None


def _string_list(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ConfigurationError(f"manifest {field} must be an array of non-empty strings")
    return tuple(value)


def load_manifest(project: Project, explicit_path: Path | None = None) -> Manifest:
    path = explicit_path.expanduser().resolve(strict=False) if explicit_path else project.worktree_root / MANIFEST_NAME
    raw: dict[str, Any] = {}
    actual_path: Path | None = path if path.is_file() else None
    if explicit_path and not path.is_file():
        raise ConfigurationError(f"manifest does not exist: {path}")
    if actual_path:
        try:
            with actual_path.open("rb") as handle:
                raw = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigurationError(f"cannot read manifest {actual_path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ConfigurationError("manifest root must be a table")
        unknown = sorted(set(raw) - MANIFEST_KEYS)
        if unknown:
            raise ConfigurationError(f"unknown manifest field(s): {', '.join(unknown)}")

    version = raw.get("version", 1)
    if version != 1:
        raise ConfigurationError(f"unsupported manifest version: {version!r}")
    kind = raw.get("kind", "auto")
    if kind == "auto":
        kind = _detect_kind(project.worktree_root)
    if kind not in KINDS:
        raise ConfigurationError(f"manifest kind must be one of: {', '.join(sorted(KINDS))}")

    working_value = raw.get("working_directory", ".")
    if not isinstance(working_value, str) or not working_value:
        raise ConfigurationError("manifest working_directory must be a non-empty string")
    working = Path(working_value)
    if working.is_absolute():
        raise ConfigurationError("manifest working_directory must be relative to the worktree")
    working = (project.worktree_root / working).resolve(strict=False)
    try:
        working.relative_to(project.worktree_root)
    except ValueError as exc:
        raise ConfigurationError("manifest working_directory must stay inside the worktree") from exc

    command_value = raw.get("command")
    if command_value is None:
        command = _detect_command(working, kind)
    else:
        command = _string_list(command_value, "command")
        if not command:
            raise ConfigurationError("manifest command must not be empty")

    port = raw.get("port", "auto")
    if port != "auto" and (isinstance(port, bool) or not isinstance(port, int) or not 1024 <= port <= 65535):
        raise ConfigurationError("manifest port must be 'auto' or an integer from 1024 to 65535")
    health_path = raw.get("health_check_path", "/")
    if not isinstance(health_path, str) or not health_path.startswith("/"):
        raise ConfigurationError("manifest health_check_path must start with '/'")
    provider = raw.get("hosted_provider")
    if provider is not None and (not isinstance(provider, str) or not provider):
        raise ConfigurationError("manifest hosted_provider must be a non-empty string")
    privacy = raw.get("privacy", "tailnet")
    if privacy not in PRIVACY_VALUES:
        raise ConfigurationError(f"manifest privacy must be one of: {', '.join(sorted(PRIVACY_VALUES))}")
    evidence = _string_list(raw.get("evidence_requirements", raw.get("evidence")), "evidence_requirements")
    invalid_evidence = sorted(set(evidence) - EVIDENCE_VALUES)
    if invalid_evidence:
        raise ConfigurationError(f"unknown evidence requirement(s): {', '.join(invalid_evidence)}")
    lease = raw.get("lease_hours", 24)
    if isinstance(lease, bool) or not isinstance(lease, (int, float)) or lease <= 0:
        raise ConfigurationError("manifest lease_hours must be a positive number")
    cleanup = raw.get("cleanup_policy", raw.get("cleanup", "lease"))
    if cleanup == "pr":
        cleanup = "pull-request"
    if cleanup not in {"lease", "manual", "provider", "pull-request"}:
        raise ConfigurationError("manifest cleanup_policy must be lease, manual, provider, or pull-request")
    profile = raw.get("profile", "default")
    if not isinstance(profile, str) or not profile:
        raise ConfigurationError("manifest profile must be a non-empty string")
    ios = raw.get("ios", {})
    if not isinstance(ios, dict):
        raise ConfigurationError("manifest ios must be a table")

    return Manifest(
        path=actual_path,
        version=version,
        kind=kind,
        working_directory=working,
        command=command,
        port=port,
        health_check_path=health_path,
        hosted_provider=provider,
        privacy=privacy,
        evidence=evidence,
        lease_hours=float(lease),
        cleanup_policy=cleanup,
        profile=profile,
        ios=ios,
    )


def preview_id(project: Project, adapter: str, profile: str) -> str:
    material = "\0".join((str(project.repository_common_dir), str(project.worktree_root), adapter, profile))
    return f"pvw_{_digest(material, 16)}"
