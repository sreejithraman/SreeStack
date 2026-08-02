from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
import urllib.error
import urllib.request

from ..project import ProjectConfig, Project


@dataclass(frozen=True)
class AdapterContext:
    project: Project
    config: ProjectConfig
    state_root: Path
    showroom_dir: Path
    approvals: dict[str, bool]


class Adapter(Protocol):
    """Adapters return normalized record patches and touch only exact owned resources."""

    def start(self, record: dict[str, Any], context: AdapterContext) -> dict[str, Any]: ...

    def verify(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]: ...

    def stop(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]: ...


class EvidenceAdapter:
    name = "evidence-only"

    def start(self, record: dict[str, Any], context: AdapterContext) -> dict[str, Any]:
        command = list(context.config.command) if context.config.command else None
        return {
            "status": "active",
            "surface": {"url": None, "device": None, "artifact": None, "command": command},
            "verification": {
                "status": "pending" if command else "blocked",
                "checked_at": None,
                "detail": "Evidence-only record; attach evidence or a runnable command for review.",
            },
        }

    def verify(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        surface = record.get("surface", {})
        artifact = surface.get("artifact")
        command = surface.get("command")
        if artifact:
            ok = Path(artifact).exists()
            detail = "artifact exists" if ok else "artifact is missing"
            status = "passed" if ok else "failed"
        elif command:
            evidence = [Path(value) for value in record.get("evidence_paths", [])]
            ok = any(path.is_file() and path.stat().st_size > 0 for path in evidence)
            detail = (
                "recorded command has nonempty execution evidence"
                if ok
                else "runnable command is recorded but has not been executed; attach a nonempty transcript or artifact"
            )
            status = "passed" if ok else "blocked"
        else:
            evidence = [Path(value) for value in record.get("evidence_paths", [])]
            ok = any(path.is_file() and path.stat().st_size > 0 for path in evidence)
            detail = "nonempty evidence exists" if ok else "no usable review evidence is recorded"
            status = "passed" if ok else "failed"
        return {"verification": {"status": status, "detail": detail}}

    def stop(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        return {"status": "stopped"}


class RegisteredSurfaceAdapter:
    """Verify already-created surfaces without duplicating provider workflows."""

    name = "registered"

    def start(self, record: dict[str, Any], context: AdapterContext) -> dict[str, Any]:
        raise RuntimeError("registered surfaces must be created before showroom registration")

    def verify(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        surface = record.get("surface", {})
        url = surface.get("url")
        artifact = surface.get("artifact")
        command = surface.get("command")
        device = surface.get("device")
        if url:
            try:
                request = urllib.request.Request(str(url), method="GET")
                with urllib.request.urlopen(request, timeout=10.0) as response:
                    ok = 200 <= response.status < 400
            except (OSError, urllib.error.URLError, ValueError):
                ok = False
            detail = "registered URL responded successfully" if ok else "registered URL health check failed"
            status = "passed" if ok else "failed"
        elif artifact:
            ok = Path(str(artifact)).is_file()
            detail = "registered artifact exists" if ok else "registered artifact is missing"
            status = "passed" if ok else "failed"
        elif device:
            evidence = [Path(value) for value in record.get("evidence_paths", [])]
            ok = any(path.is_file() for path in evidence)
            detail = "device evidence exists" if ok else "registered device was not exercised by showroom"
            status = "passed" if ok else "blocked"
        elif command:
            evidence = [Path(value) for value in record.get("evidence_paths", [])]
            ok = any(path.is_file() and path.stat().st_size > 0 for path in evidence)
            status = "passed" if ok else "blocked"
            detail = (
                "registered command has nonempty execution evidence"
                if ok
                else "registered command was not executed; attach a nonempty transcript or artifact"
            )
        else:
            status = "blocked"
            detail = "registered surface is missing"
        return {"verification": {"status": status, "detail": detail}}

    def stop(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        return {
            "status": "stopped",
            "verification": {"status": "stale", "detail": "local registration stopped; external lifecycle is unchanged"},
        }
