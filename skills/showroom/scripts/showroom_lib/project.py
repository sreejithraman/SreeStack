from __future__ import annotations

import hashlib
import json
import os
import subprocess
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigurationError


@dataclass(frozen=True)
class Project:
    repository_root: Path
    repository_common_dir: Path
    worktree_root: Path
    repository_id: str
    worktree_id: str
    source: str | None


@dataclass(frozen=True)
class ProjectConfig:
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


def detect_config(project: Project) -> ProjectConfig:
    root = project.worktree_root
    kind = _detect_kind(root)
    return ProjectConfig(
        kind=kind,
        working_directory=root,
        command=_detect_command(root, kind),
        port="auto",
        health_check_path="/",
        hosted_provider=None,
        privacy="tailnet",
        evidence=(),
        lease_hours=24.0,
        cleanup_policy="lease",
        profile="default",
        ios={},
    )


def showroom_id(project: Project, adapter: str, profile: str) -> str:
    material = "\0".join((str(project.repository_common_dir), str(project.worktree_root), adapter, profile))
    return f"srm_{_digest(material, 16)}"
