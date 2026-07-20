from __future__ import annotations

import copy
import hashlib
import json
import os
import plistlib
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence

from ..errors import AdapterError, ConfigurationError
from .base import AdapterContext


LOOPBACK = "127.0.0.1"
DEFAULT_ORIGIN_PORTS = tuple(range(41000, 44000))
DEFAULT_SERVE_PORTS = tuple(range(44000, 49000))
FORBIDDEN_FUNNEL_PORTS = frozenset({443, 8443, 10000})
URL_PATTERN = re.compile(r"https://[^\s/]+(?::\d+)?")


class CommandRunner(Protocol):
    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> Any: ...


class HttpProbe(Protocol):
    def check(self, url: str, timeout: float) -> bool: ...


class FileSystem(Protocol):
    def mkdir(self, path: Path) -> None: ...

    def write_text(self, path: Path, value: str) -> None: ...

    def read_text(self, path: Path) -> str: ...

    def exists(self, path: Path) -> bool: ...

    def unlink(self, path: Path) -> None: ...


class SubprocessRunner:
    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(argv),
            cwd=cwd,
            env=dict(env) if env is not None else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )


class UrllibProbe:
    def check(self, url: str, timeout: float) -> bool:
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            try:
                with urllib.request.urlopen(url, timeout=min(remaining, 2.0)) as response:
                    return 200 <= response.status < 400
            except (OSError, urllib.error.URLError, ValueError):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                time.sleep(min(0.25, remaining))


class LocalFileSystem:
    def mkdir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def write_text(self, path: Path, value: str) -> None:
        self.mkdir(path.parent)
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def exists(self, path: Path) -> bool:
        return path.exists()

    def unlink(self, path: Path) -> None:
        path.unlink(missing_ok=True)


def _socket_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        try:
            candidate.bind((host, port))
        except OSError:
            return False
    return True


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _result_text(result: Any, field: str) -> str:
    value = getattr(result, field, "")
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def _result_ok(result: Any) -> bool:
    return int(getattr(result, "returncode", 1)) == 0


def _listener_ports(value: Any) -> set[int]:
    """Extract listener ports without mistaking backend target ports for routes."""
    ports: set[int] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "TCP" and isinstance(item, dict):
                ports.update(int(candidate) for candidate in item if str(candidate).isdigit())
            elif key in {"Web", "AllowFunnel"} and isinstance(item, dict):
                for candidate in item:
                    match = re.search(r":(\d{1,5})$", str(candidate))
                    ports.add(int(match.group(1)) if match else 443)
            elif key in {"port", "listen_port", "listener_port"} and isinstance(item, int):
                ports.add(item)
            elif key in {"listeners", "endpoints"}:
                ports.update(_listener_ports(item))
    return {port for port in ports if 1 <= port <= 65535}


def _funnel_ports(value: Any) -> set[int]:
    """Extract only listeners explicitly enabled by ServeConfig.AllowFunnel."""
    ports: set[int] = set()
    if not isinstance(value, dict):
        return ports
    allow_funnel = value.get("AllowFunnel")
    if isinstance(allow_funnel, dict):
        for host_port, allowed in allow_funnel.items():
            if not allowed:
                continue
            match = re.search(r":(\d{1,5})$", str(host_port))
            ports.add(int(match.group(1)) if match else 443)
    foreground = value.get("Foreground")
    if isinstance(foreground, dict):
        for config in foreground.values():
            ports.update(_funnel_ports(config))
    return {port for port in ports if 1 <= port <= 65535}


@dataclass(frozen=True)
class Snapshot:
    serve: dict[str, Any]
    funnel: dict[str, Any]

    @property
    def occupied_ports(self) -> set[int]:
        return _listener_ports(self.serve) | _listener_ports(self.funnel)


class Adapter:
    name = "web-local"

    def __init__(
        self,
        *,
        runner: CommandRunner | None = None,
        http_probe: HttpProbe | None = None,
        clock: Callable[[], datetime] = _now,
        filesystem: FileSystem | None = None,
        tailscale_bin: str | None = None,
        launchctl_bin: str = "/bin/launchctl",
        origin_ports: Iterable[int] = DEFAULT_ORIGIN_PORTS,
        serve_ports: Iterable[int] = DEFAULT_SERVE_PORTS,
        port_available: Callable[[str, int], bool] = _socket_available,
        executable_resolver: Callable[[str], str | None] = shutil.which,
        uid: int | None = None,
        command_timeout: float = 15.0,
        health_timeout: float = 10.0,
    ) -> None:
        self.runner = runner or SubprocessRunner()
        self.http_probe = http_probe or UrllibProbe()
        self.clock = clock
        self.fs = filesystem or LocalFileSystem()
        self.tailscale_bin = tailscale_bin or shutil.which("tailscale")
        self.launchctl_bin = launchctl_bin
        self.origin_ports = tuple(origin_ports)
        self.serve_ports = tuple(serve_ports)
        self.port_available = port_available
        self.executable_resolver = executable_resolver
        self.uid = os.getuid() if uid is None else uid
        self.command_timeout = command_timeout
        self.health_timeout = health_timeout

    def start(self, record: dict[str, Any], context: AdapterContext) -> dict[str, Any]:
        self._require_approval(context)
        if not self.tailscale_bin:
            raise AdapterError("Tailscale CLI is not installed or discoverable")
        if not os.path.isabs(self.tailscale_bin) or not os.path.isabs(self.launchctl_bin):
            raise AdapterError("Tailscale and launchctl executables must use absolute paths")
        if not context.manifest.command:
            raise ConfigurationError("web-local preview requires a development command")

        self.recover(record, context)

        snapshot = self._snapshot()
        origin_port, serve_port = self._allocate_ports(record["id"], context, snapshot)
        target = f"http://{LOOPBACK}:{origin_port}"
        label = self._label(record["id"])
        domain = f"gui/{self.uid}"
        service_target = f"{domain}/{label}"
        if _result_ok(self._run((self.launchctl_bin, "print", service_target))):
            raise AdapterError("ownership conflict: exact LaunchAgent label is already loaded")
        plist_path = context.preview_dir / "origin.plist"
        stdout_path = context.preview_dir / "origin.stdout.log"
        stderr_path = context.preview_dir / "origin.stderr.log"
        command = tuple(
            item.replace("{port}", str(origin_port)).replace("{host}", LOOPBACK)
            for item in context.manifest.command
        )
        executable = self._resolve_executable(command[0])
        command = (executable, *command[1:])
        safe_path = self._safe_path(executable)
        plist_text = self._plist(
            label,
            command,
            context,
            stdout_path,
            stderr_path,
            origin_port,
            safe_path,
        )
        plist_digest = hashlib.sha256(plist_text.encode("utf-8")).hexdigest()
        ownership_path = context.preview_dir / "ownership.json"
        off_argv = [self.tailscale_bin, "serve", f"--https={serve_port}", "off"]
        ownership = {
            "version": 1,
            "preview_id": record["id"],
            "created_at": _format_time(self.clock()),
            "launchd": {
                "domain": domain,
                "label": label,
                "target": service_target,
                "plist_path": str(plist_path),
                "plist_sha256": plist_digest,
            },
            "serve": {
                "port": serve_port,
                "target": target,
                "off_argv": off_argv,
            },
        }
        ownership_text = json.dumps(ownership, indent=2, sort_keys=True) + "\n"
        ownership_digest = hashlib.sha256(ownership_text.encode("utf-8")).hexdigest()
        self.fs.mkdir(context.preview_dir)
        self.fs.write_text(plist_path, plist_text)
        # This manager-owned recovery record is durable before the first
        # external mutation, so an interrupted bootstrap can be reconciled by
        # exact identities rather than process or port guessing.
        self.fs.write_text(ownership_path, ownership_text)

        launchd_loaded = False
        launchd_attempted = False
        serve_attempted = False
        try:
            launchd_attempted = True
            self._checked(
                (self.launchctl_bin, "bootstrap", domain, str(plist_path)),
                "bootstrap origin LaunchAgent",
            )
            launchd_loaded = True
            self._checked(
                (self.launchctl_bin, "kickstart", "-p", service_target),
                "start origin LaunchAgent",
            )
            local_url = self._with_health(target, context.manifest.health_check_path)
            if not self.http_probe.check(local_url, self.health_timeout):
                raise AdapterError(f"origin health check failed: {local_url}")

            # Allocation and mutation are serialized against previewctl, but a
            # human or another Tailscale client can still change Serve. Re-read
            # immediately before the mutating command and never replace a route.
            pre_serve = self._snapshot()
            if serve_port in pre_serve.occupied_ports:
                raise AdapterError(f"Tailscale listener was claimed during startup: {serve_port}")

            start_argv = (
                self.tailscale_bin,
                "serve",
                "--bg",
                f"--https={serve_port}",
                target,
            )
            serve_attempted = True
            result = self._run(start_argv, tailscale=True)
            if not _result_ok(result):
                detail = (_result_text(result, "stderr") or _result_text(result, "stdout")).strip()
                raise AdapterError(f"Tailscale Serve start failed: {detail or 'unknown error'}")
            public_url = self._url_from_output(_result_text(result, "stdout"), serve_port)
            post_start = self._snapshot()
            if serve_port in _funnel_ports(post_start.funnel):
                raise AdapterError(f"unsafe Funnel conflict appeared on port {serve_port}")
            if not self._route_matches(post_start.serve, serve_port, target):
                raise AdapterError("Tailscale Serve did not report the exact configured route")
            remote_health = self._with_health(public_url, context.manifest.health_check_path)
            if not self.http_probe.check(remote_health, self.health_timeout):
                raise AdapterError(f"tailnet health check failed: {remote_health}")
        except Exception:
            serve_cleanup_safe = not serve_attempted
            if serve_attempted:
                try:
                    failed_snapshot = self._snapshot()
                    should_remove = (
                        serve_port not in _funnel_ports(failed_snapshot.funnel)
                        and self._route_matches(failed_snapshot.serve, serve_port, target)
                    )
                    # A changed route is not ours to remove; our exact route is
                    # already absent. A Funnel route is public ownership drift,
                    # so retain metadata for explicit diagnosis.
                    serve_cleanup_safe = not should_remove and serve_port not in _funnel_ports(failed_snapshot.funnel)
                except AdapterError:
                    should_remove = False
                    serve_cleanup_safe = False
                if should_remove:
                    try:
                        serve_cleanup_safe = _result_ok(
                            self._run(tuple(off_argv), tailscale=True)
                        )
                    except AdapterError:
                        serve_cleanup_safe = False
            launchd_cleanup_safe = not (launchd_loaded or launchd_attempted)
            if launchd_loaded or launchd_attempted:
                try:
                    loaded = _result_ok(self._run((self.launchctl_bin, "print", service_target)))
                    if loaded:
                        launchd_cleanup_safe = _result_ok(
                            self._run((self.launchctl_bin, "bootout", service_target))
                        )
                    else:
                        launchd_cleanup_safe = True
                except AdapterError:
                    launchd_cleanup_safe = False
            if serve_cleanup_safe and launchd_cleanup_safe:
                self.fs.unlink(plist_path)
                self.fs.unlink(ownership_path)
            raise

        checked_at = _format_time(self.clock())
        return {
            "status": "active",
            "surface": {"url": public_url, "command": list(command)},
            "resources": {
                "process": {"kind": "launchd", "label": label},
                "launchd": {
                    "domain": domain,
                    "label": label,
                    "target": service_target,
                    "plist_path": str(plist_path),
                    "plist_sha256": plist_digest,
                },
                "port": origin_port,
                "ownership_path": str(ownership_path),
                "ownership_sha256": ownership_digest,
                "serve": {
                    "port": serve_port,
                    "target": target,
                    "health_path": context.manifest.health_check_path,
                    "start_argv": list(start_argv),
                    "off_argv": off_argv,
                },
            },
            "verification": {
                "status": "passed",
                "checked_at": checked_at,
                "detail": "origin and tailnet HTTPS health checks passed",
            },
            "log_paths": [str(stdout_path), str(stderr_path)],
            "availability_limitations": [
                "Available only to peers permitted by the tailnet access policy.",
                "Unavailable while this Mac sleeps, is off, is logged out, loses connectivity, or the origin is unhealthy.",
            ],
        }

    def verify(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        checked_at = _format_time(self.clock())
        try:
            launchd, serve = self._owned_resources(record)
            plist_path = Path(launchd["plist_path"])
            if not self.fs.exists(plist_path):
                raise AdapterError("registered LaunchAgent plist is missing")
            digest = hashlib.sha256(self.fs.read_text(plist_path).encode("utf-8")).hexdigest()
            if digest != launchd["plist_sha256"]:
                raise AdapterError("registered LaunchAgent plist was modified")
            snapshot = self._snapshot()
            port = int(serve["port"])
            target = str(serve["target"])
            if port in _funnel_ports(snapshot.funnel):
                raise AdapterError("registered port is now exposed through Funnel")
            if not self._route_matches(snapshot.serve, port, target):
                raise AdapterError("registered Serve route is missing or points elsewhere")
            if not _result_ok(self._run((self.launchctl_bin, "print", launchd["target"]))):
                raise AdapterError("registered LaunchAgent is not loaded")
        except AdapterError as exc:
            return {
                "verification": {
                    "status": "stale",
                    "checked_at": checked_at,
                    "detail": str(exc),
                }
            }

        health_path = str(serve.get("health_path") or (context.manifest.health_check_path if context else "/"))
        local_url = self._with_health(target, health_path)
        public_url = record.get("surface", {}).get("url")
        if not isinstance(public_url, str) or not public_url.startswith("https://"):
            return {
                "verification": {
                    "status": "stale",
                    "checked_at": checked_at,
                    "detail": "registered tailnet URL is missing",
                }
            }
        remote_url = self._with_health(public_url, health_path)
        local_ok = self.http_probe.check(local_url, self.health_timeout)
        remote_ok = self.http_probe.check(remote_url, self.health_timeout)
        if not local_ok or not remote_ok:
            failed = "origin" if not local_ok else "tailnet route"
            return {
                "verification": {
                    "status": "failed",
                    "checked_at": checked_at,
                    "detail": f"{failed} health check failed",
                }
            }
        return {
            "verification": {
                "status": "passed",
                "checked_at": checked_at,
                "detail": "origin and tailnet HTTPS health checks passed",
            }
        }

    def reconcile(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        """Reconcile by verifying exact registered resources without mutating them."""
        return self.verify(record, context)

    def recover(self, record: dict[str, Any], context: AdapterContext) -> dict[str, Any] | None:
        """Remove an interrupted start using only its durable exact claims."""
        ownership_path = context.preview_dir / "ownership.json"
        if not self.fs.exists(ownership_path):
            return None
        try:
            raw_text = self.fs.read_text(ownership_path)
            ownership = json.loads(raw_text)
            launchd = ownership["launchd"]
            serve = ownership["serve"]
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise AdapterError("cannot recover malformed web-local ownership metadata") from exc
        if ownership.get("version") != 1 or ownership.get("preview_id") != record.get("id"):
            raise AdapterError("cannot recover web-local ownership metadata for another preview")
        expected_label = self._label(str(record["id"]))
        expected_domain = f"gui/{self.uid}"
        expected_plist = context.preview_dir / "origin.plist"
        if (
            launchd.get("label") != expected_label
            or launchd.get("domain") != expected_domain
            or launchd.get("target") != f"{expected_domain}/{expected_label}"
            or launchd.get("plist_path") != str(expected_plist)
            or not isinstance(launchd.get("plist_sha256"), str)
        ):
            raise AdapterError("cannot recover web-local ownership metadata with unexpected launchd identity")
        target = serve.get("target")
        match = re.fullmatch(rf"http://{re.escape(LOOPBACK)}:(\d{{4,5}})", str(target))
        if not match:
            raise AdapterError("cannot recover web-local ownership metadata with unexpected origin target")
        try:
            serve_port = int(serve["port"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AdapterError("cannot recover web-local ownership metadata with invalid Serve port") from exc
        if serve.get("off_argv") != [self.tailscale_bin, "serve", f"--https={serve_port}", "off"]:
            raise AdapterError("cannot recover web-local ownership metadata with unexpected cleanup command")
        synthetic = copy.deepcopy(record)
        synthetic["resources"] = {
            "process": {"kind": "launchd", "label": expected_label},
            "launchd": launchd,
            "port": int(match.group(1)),
            "ownership_path": str(ownership_path),
            "ownership_sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
            "serve": serve,
        }
        return self.stop(synthetic, context)

    def cleanup_plan(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        return self.stop(record, context, dry_run=True)

    def stop(
        self,
        record: dict[str, Any],
        context: AdapterContext | None,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if record.get("status") == "stopped":
            return {"status": "stopped"}
        ownership_path = Path(str(record.get("resources", {}).get("ownership_path", "")))
        ownership_missing = not self.fs.exists(ownership_path)
        launchd, serve = self._owned_resources(record, allow_missing_ownership=ownership_missing)
        plist_path = Path(launchd["plist_path"])
        if not self.fs.exists(plist_path):
            if ownership_missing:
                snapshot = self._snapshot()
                port = int(serve["port"])
                target = str(serve["target"])
                route_present = self._route_matches(snapshot.serve, port, target)
                launchd_present = _result_ok(self._run((self.launchctl_bin, "print", launchd["target"])))
                if not route_present and not launchd_present:
                    return {
                        "status": "stopped",
                        "resources": {"process": None},
                        "verification": {
                            "status": "stale",
                            "detail": "exact web-local resources were already absent after an interrupted stop",
                        },
                    }
                raise AdapterError("ownership drift: both ownership metadata and LaunchAgent plist are missing while resources remain")
            # The intact, hash-checked ownership sidecar still proves the exact
            # label and route after a crash between the two final file unlinks.
        else:
            actual_digest = hashlib.sha256(self.fs.read_text(plist_path).encode("utf-8")).hexdigest()
            if actual_digest != launchd["plist_sha256"]:
                raise AdapterError("ownership drift: registered LaunchAgent plist was modified")

        snapshot = self._snapshot()
        port = int(serve["port"])
        target = str(serve["target"])
        if port in _funnel_ports(snapshot.funnel):
            raise AdapterError("ownership drift: registered Serve port is now Funnel-owned")
        route_present = port in _listener_ports(snapshot.serve)
        if route_present and not self._route_matches(snapshot.serve, port, target):
            raise AdapterError("ownership drift: registered Serve port points to another target")

        launchd_present = _result_ok(self._run((self.launchctl_bin, "print", launchd["target"])))
        commands: list[list[str]] = []
        if route_present:
            commands.append(list(serve["off_argv"]))
        if launchd_present:
            commands.append([self.launchctl_bin, "bootout", launchd["target"]])
        if dry_run:
            return {
                "dry_run": True,
                "commands": commands,
                "paths": [launchd["plist_path"], record["resources"]["ownership_path"]],
            }

        if route_present:
            result = self._run(tuple(serve["off_argv"]), tailscale=True)
            if not _result_ok(result):
                detail = (_result_text(result, "stderr") or _result_text(result, "stdout")).strip()
                raise AdapterError(f"cannot remove exact Tailscale Serve route: {detail or 'unknown error'}")
        if launchd_present:
            result = self._run((self.launchctl_bin, "bootout", launchd["target"]))
            if not _result_ok(result):
                detail = (_result_text(result, "stderr") or _result_text(result, "stdout")).strip()
                raise AdapterError(f"cannot remove exact origin LaunchAgent: {detail or 'unknown error'}")
        self.fs.unlink(plist_path)
        self.fs.unlink(Path(record["resources"]["ownership_path"]))
        return {
            "status": "stopped",
            "resources": {
                "process": None,
                "launchd": {**launchd, "status": "stopped"},
                "serve": {**serve, "status": "stopped"},
            },
            "verification": {
                "status": "stale",
                "detail": "preview stopped; prior verification no longer proves availability",
            },
        }

    def doctor(self) -> dict[str, Any]:
        """Return a read-only dependency and exposure assessment."""
        warnings = [
            "First-time tailnet HTTPS setup publishes the machine and tailnet DNS names in Certificate Transparency.",
            "Serve is unavailable while the Mac sleeps, is off or logged out, or loses network/Tailscale connectivity.",
            "Serve access follows tailnet policy and may include accepted device shares.",
        ]
        if not self.tailscale_bin:
            return {
                "available": False,
                "tailscale_cli": None,
                "launchctl": self.launchctl_bin,
                "serve_ports": [],
                "funnel_ports": [],
                "warnings": warnings,
                "detail": "Tailscale CLI is not installed or discoverable",
            }
        version_result = self._run((self.tailscale_bin, "version", "--json"), tailscale=True)
        if not _result_ok(version_result):
            return {
                "available": False,
                "tailscale_cli": self.tailscale_bin,
                "launchctl": self.launchctl_bin,
                "serve_ports": [],
                "funnel_ports": [],
                "warnings": warnings,
                "detail": "Tailscale CLI version check failed",
            }
        try:
            version_data = json.loads(_result_text(version_result, "stdout") or "{}")
        except json.JSONDecodeError:
            version_data = {"raw": _result_text(version_result, "stdout").strip()}
        try:
            snapshot = self._snapshot()
        except AdapterError as exc:
            return {
                "available": False,
                "tailscale_cli": self.tailscale_bin,
                "tailscale_version": version_data,
                "launchctl": self.launchctl_bin,
                "serve_ports": [],
                "funnel_ports": [],
                "warnings": warnings,
                "detail": str(exc),
            }
        launchctl_available = self.fs.exists(Path(self.launchctl_bin))
        return {
            "available": launchctl_available,
            "tailscale_cli": self.tailscale_bin,
            "tailscale_version": version_data,
            "launchctl": self.launchctl_bin,
            "launchctl_available": launchctl_available,
            "serve_ports": sorted(_listener_ports(snapshot.serve)),
            "funnel_ports": sorted(_funnel_ports(snapshot.funnel)),
            "https_readiness": "unknown-read-only; start may require explicit interactive consent",
            "warnings": warnings,
            "detail": "dependencies are available" if launchctl_available else "launchctl is unavailable",
        }

    def _require_approval(self, context: AdapterContext) -> None:
        if not context.approvals.get("persistence", False):
            raise AdapterError("launchd persistence requires explicit approval")
        if not context.approvals.get("tailscale_config", False):
            raise AdapterError("Tailscale Serve and HTTPS configuration require explicit approval")

    def _owned_resources(
        self, record: dict[str, Any], *, allow_missing_ownership: bool = False
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        resources = record.get("resources")
        if not isinstance(resources, dict):
            raise AdapterError("ownership drift: web-local resources are missing")
        launchd = resources.get("launchd")
        serve = resources.get("serve")
        if not isinstance(launchd, dict) or not isinstance(serve, dict):
            raise AdapterError("ownership drift: exact launchd or Serve identity is missing")
        label = self._label(str(record.get("id", "")))
        domain = f"gui/{self.uid}"
        if (
            launchd.get("label") != label
            or launchd.get("domain") != domain
            or launchd.get("target") != f"{domain}/{label}"
            or not isinstance(launchd.get("plist_path"), str)
            or not isinstance(launchd.get("plist_sha256"), str)
        ):
            raise AdapterError("ownership drift: launchd identity does not match the preview ID")
        try:
            port = int(serve["port"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AdapterError("ownership drift: Serve port is invalid") from exc
        expected_target = f"http://{LOOPBACK}:{resources.get('port')}"
        expected_off = [self.tailscale_bin, "serve", f"--https={port}", "off"]
        if (
            serve.get("target") != expected_target
            or serve.get("off_argv") != expected_off
            or port in FORBIDDEN_FUNNEL_PORTS
        ):
            raise AdapterError("ownership drift: Serve cleanup identity is not exact")
        ownership_path = resources.get("ownership_path")
        ownership_sha256 = resources.get("ownership_sha256")
        if not isinstance(ownership_path, str) or not isinstance(ownership_sha256, str):
            raise AdapterError("ownership drift: recovery metadata identity is missing")
        path = Path(ownership_path)
        if not self.fs.exists(path):
            if allow_missing_ownership:
                return dict(launchd), dict(serve)
            raise AdapterError("ownership drift: recovery metadata is missing")
        digest = hashlib.sha256(self.fs.read_text(path).encode("utf-8")).hexdigest()
        if digest != ownership_sha256:
            raise AdapterError("ownership drift: recovery metadata was modified")
        return dict(launchd), dict(serve)

    def _resolve_executable(self, executable: str) -> str:
        if os.path.isabs(executable):
            return executable
        resolved = self.executable_resolver(executable)
        if not resolved or not os.path.isabs(resolved):
            raise ConfigurationError(f"development executable is not resolvable to an absolute path: {executable}")
        return resolved

    @staticmethod
    def _safe_path(executable: str) -> str:
        paths = [
            str(Path(executable).parent),
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin",
            "/usr/sbin",
            "/sbin",
        ]
        return ":".join(dict.fromkeys(paths))

    def _run(self, argv: Sequence[str], *, tailscale: bool = False) -> Any:
        environment = None
        if tailscale:
            environment = dict(os.environ)
            environment["TAILSCALE_BE_CLI"] = "1"
        try:
            return self.runner.run(tuple(argv), env=environment, timeout=self.command_timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AdapterError(f"command failed: {' '.join(argv)}: {exc}") from exc

    def _checked(self, argv: Sequence[str], operation: str) -> Any:
        result = self._run(argv)
        if not _result_ok(result):
            detail = (_result_text(result, "stderr") or _result_text(result, "stdout")).strip()
            raise AdapterError(f"cannot {operation}: {detail or 'unknown error'}")
        return result

    def _snapshot(self) -> Snapshot:
        assert self.tailscale_bin is not None
        values: list[dict[str, Any]] = []
        for mode in ("serve", "funnel"):
            result = self._run((self.tailscale_bin, mode, "status", "--json"), tailscale=True)
            if not _result_ok(result):
                detail = (_result_text(result, "stderr") or _result_text(result, "stdout")).strip()
                raise AdapterError(f"cannot inspect Tailscale {mode} status: {detail or 'unknown error'}")
            try:
                parsed = json.loads(_result_text(result, "stdout") or "{}")
            except json.JSONDecodeError as exc:
                raise AdapterError(f"unrecognized Tailscale {mode} status JSON") from exc
            if not isinstance(parsed, dict):
                raise AdapterError(f"unrecognized Tailscale {mode} status JSON")
            if parsed and not ({"TCP", "Web", "AllowFunnel"} & set(parsed)):
                raise AdapterError(f"unrecognized Tailscale {mode} status JSON")
            values.append(parsed)
        return Snapshot(values[0], values[1])

    def _allocate_ports(
        self,
        preview_id: str,
        context: AdapterContext,
        snapshot: Snapshot,
    ) -> tuple[int, int]:
        occupied = snapshot.occupied_ports | FORBIDDEN_FUNNEL_PORTS
        requested = context.manifest.port
        if isinstance(requested, int):
            origin_port = requested
            if origin_port in occupied or not self.port_available(LOOPBACK, origin_port):
                raise AdapterError(f"configured origin port is unavailable: {origin_port}")
        else:
            origin_port = self._choose(self.origin_ports, occupied, preview_id, "origin")
        occupied.add(origin_port)
        serve_port = self._choose(self.serve_ports, occupied, preview_id, "Serve")
        return origin_port, serve_port

    def _choose(self, candidates: Sequence[int], occupied: set[int], preview_id: str, kind: str) -> int:
        if not candidates:
            raise AdapterError(f"no {kind} port candidates are configured")
        offset = int(hashlib.sha256(preview_id.encode("utf-8")).hexdigest()[:8], 16) % len(candidates)
        ordered = candidates[offset:] + candidates[:offset]
        for port in ordered:
            if port not in occupied and self.port_available(LOOPBACK, port):
                return port
        raise AdapterError(f"no collision-free {kind} port is available")

    @staticmethod
    def _label(preview_id: str) -> str:
        digest = hashlib.sha256(preview_id.encode("utf-8")).hexdigest()[:20]
        return f"com.sreestack.preview.{digest}"

    @staticmethod
    def _plist(
        label: str,
        command: Sequence[str],
        context: AdapterContext,
        stdout_path: Path,
        stderr_path: Path,
        port: int,
        safe_path: str,
    ) -> str:
        payload = {
            "Label": label,
            "ProgramArguments": list(command),
            "WorkingDirectory": str(context.manifest.working_directory),
            "EnvironmentVariables": {"HOST": LOOPBACK, "PORT": str(port), "PATH": safe_path},
            "KeepAlive": True,
            "ExitTimeOut": 10,
            "StandardOutPath": str(stdout_path),
            "StandardErrorPath": str(stderr_path),
        }
        return plistlib.dumps(payload, fmt=plistlib.FMT_XML, sort_keys=True).decode("utf-8")

    @staticmethod
    def _url_from_output(output: str, port: int) -> str:
        match = URL_PATTERN.search(output)
        if not match:
            raise AdapterError("Tailscale Serve did not report a review URL")
        url = match.group(0).rstrip("/")
        if port != 443 and not url.endswith(f":{port}"):
            raise AdapterError("Tailscale Serve reported a URL for an unexpected port")
        return url

    @staticmethod
    def _with_health(base: str, path: str) -> str:
        return f"{base.rstrip('/')}{path}"

    @staticmethod
    def _route_matches(payload: dict[str, Any], port: int, target: str) -> bool:
        if port not in _listener_ports(payload):
            return False

        def contains(value: Any) -> bool:
            if isinstance(value, dict):
                return any(contains(item) for item in value.values())
            if isinstance(value, list):
                return any(contains(item) for item in value)
            return isinstance(value, str) and value.rstrip("/") == target

        web = payload.get("Web")
        if not isinstance(web, dict):
            return False
        for listener, configuration in web.items():
            match = re.search(r":(\d{1,5})$", str(listener))
            listener_port = int(match.group(1)) if match else 443
            if listener_port == port and contains(configuration):
                return True
        return False


def get_adapter() -> Adapter:
    return Adapter()
