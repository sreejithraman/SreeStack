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
    project_name: str | None = None
    surface_name: str | None = None
    delivery: tuple[str, ...] | None = None

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
            "project_name": self.project_name,
            "surface_name": self.surface_name,
            "delivery": list(self.delivery) if self.delivery else None,
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


def _inside(root: Path, value: Path) -> bool:
    try:
        value.relative_to(root)
    except ValueError:
        return False
    return True


def _delivery_command(root: Path, value: Any, project_name: str) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(argument, str) and argument for argument in value)
    ):
        raise ConfigurationError(
            f".showroom.toml project {project_name!r} delivery must be a nonempty command array"
        )
    checked_in_path = False
    for index, argument in enumerate(value):
        candidate = Path(argument)
        if candidate.is_absolute():
            if index == 0:
                continue
            raise ConfigurationError(
                f".showroom.toml project {project_name!r} delivery paths must be relative"
            )
        resolved = (root / candidate).resolve(strict=False)
        if not _inside(root, resolved):
            raise ConfigurationError(
                f".showroom.toml project {project_name!r} delivery must stay inside the worktree"
            )
        checked_in_path = checked_in_path or resolved.is_file()
    if not checked_in_path:
        raise ConfigurationError(
            f".showroom.toml project {project_name!r} delivery must include a checked-in command path"
        )
    return tuple(value)


def configured_projects(project: Project) -> dict[str, dict[str, Any]]:
    path = project.worktree_root / ".showroom.toml"
    if not path.exists():
        return {}
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"invalid .showroom.toml: {exc}") from exc
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ConfigurationError(".showroom.toml must set version = 1")
    projects: dict[str, dict[str, Any]] = {}
    for name, raw in document.items():
        if name == "version":
            continue
        if not isinstance(raw, dict):
            raise ConfigurationError(f".showroom.toml project {name!r} must be a table")
        unknown = set(raw) - {"project", "scheme", "delivery"}
        if unknown:
            raise ConfigurationError(
                f".showroom.toml project {name!r} has unknown key(s): {', '.join(sorted(unknown))}"
            )
        xcode_project = raw.get("project")
        scheme = raw.get("scheme")
        delivery = raw.get("delivery")
        if not isinstance(xcode_project, str) or not xcode_project:
            raise ConfigurationError(f".showroom.toml project {name!r} needs a nonempty project path")
        resolved = (project.worktree_root / xcode_project).resolve(strict=False)
        if Path(xcode_project).is_absolute() or not _inside(project.worktree_root, resolved):
            raise ConfigurationError(f".showroom.toml project {name!r} path must stay inside the worktree")
        if resolved.suffix != ".xcodeproj" or not resolved.is_dir():
            raise ConfigurationError(f"configured Xcode project does not exist: {resolved}")
        if not isinstance(scheme, str) or not scheme:
            raise ConfigurationError(f".showroom.toml project {name!r} needs a nonempty scheme")
        projects[name] = {
            "project": str(resolved.relative_to(project.worktree_root)),
            "scheme": scheme,
            "delivery": _delivery_command(project.worktree_root, delivery, name),
        }
    if not projects:
        raise ConfigurationError(".showroom.toml must define at least one named project")
    return projects


def detect_config(project: Project, project_name: str | None = None, surface_name: str | None = None) -> ProjectConfig:
    root = project.worktree_root
    projects = configured_projects(project)
    selected_project: dict[str, Any] | None = None
    if project_name is not None:
        if not projects:
            raise ConfigurationError(f"project {project_name!r} needs a .showroom.toml entry")
        selected_project = projects.get(project_name)
        if selected_project is None:
            available = ", ".join(sorted(projects))
            raise ConfigurationError(f"unknown showroom project {project_name!r}; available: {available}")
    kind = "ios" if selected_project else _detect_kind(root)
    profile = project_name or "default"
    if surface_name and project_name:
        profile = f"{project_name}-{surface_name}"
    ios = {}
    delivery = None
    if selected_project:
        ios = {"project": selected_project["project"], "scheme": selected_project["scheme"]}
        delivery = selected_project["delivery"]
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
        profile=profile,
        ios=ios,
        project_name=project_name,
        surface_name=surface_name,
        delivery=delivery,
    )


def showroom_id(project: Project, adapter: str, profile: str) -> str:
    material = "\0".join((str(project.repository_common_dir), str(project.worktree_root), adapter, profile))
    return f"srm_{_digest(material, 16)}"
