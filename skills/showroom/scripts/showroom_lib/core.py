from __future__ import annotations

import copy
import os
import shlex
import shutil
import sys
from pathlib import Path
from typing import Any

from .adapters.base import AdapterContext
from .adapters.loader import load_adapter
from .errors import AdapterError, ConfigurationError
from .paths import showroom_directory
from .project import ProjectConfig, Project, detect_project, detect_config, showroom_id
from .registry import Registry
from .timeutil import expires_at, format_time, now, parse_time


LOCAL_LEASE_HOURS = 24.0
HOSTED_LEASE_HOURS = 24.0 * 7
STARTING_STALE_SECONDS = 5 * 60
VERIFICATION_STATUSES = {"pending", "passed", "failed", "blocked", "stale"}


def choose_adapter(config: ProjectConfig) -> str:
    if config.kind == "ios":
        return "ios-simulator"
    if config.kind in {"web", "api"}:
        return "web-local"
    return "evidence-only"


def lifecycle_commands(identifier: str, state: Path | None = None) -> dict[str, str]:
    executable = Path(__file__).resolve().parent.parent / "showroom"

    def command(name: str) -> str:
        argv = [sys.executable, str(executable)]
        if state is not None:
            argv.extend(("--state-dir", str(state)))
        argv.extend((name, identifier))
        return shlex.join(argv)

    return {
        "inspect": command("status"),
        "verify": command("verify"),
        "renew": command("renew"),
        "pin": command("pin"),
        "unpin": command("unpin"),
        "stop": command("stop"),
    }


def _record_type(adapter: str, config: ProjectConfig) -> str:
    if adapter == "web-local":
        return "url"
    if adapter == "ios-simulator":
        return "device"
    if adapter == "evidence-only":
        return "artifact"
    return config.kind


def new_record(
    project: Project, config: ProjectConfig, adapter: str, current_time=None, state: Path | None = None
) -> dict[str, Any]:
    current = current_time or now()
    identifier = showroom_id(project, adapter, config.profile)
    lease = config.lease_hours or LOCAL_LEASE_HOURS
    expiration = expires_at(current, lease) if config.cleanup_policy == "lease" else None
    return {
        "record_version": 1,
        "id": identifier,
        "type": _record_type(adapter, config),
        "adapter": adapter,
        "registered": False,
        "provider": None,
        "provider_resource_id": None,
        "lifecycle_owner": "showroom",
        "cleanup_policy": config.cleanup_policy,
        "profile": config.profile,
        "status": "starting",
        "repository": {
            "id": project.repository_id,
            "path": str(project.repository_root),
            "common_directory": str(project.repository_common_dir),
            "source": project.source,
        },
        "worktree": {"id": project.worktree_id, "path": str(project.worktree_root)},
        "surface": {"url": None, "device": None, "artifact": None, "command": None},
        "resources": {"process": None, "launchd": None, "port": None, "simulator_udid": None},
        "verification": {"status": "pending", "checked_at": None, "detail": None},
        "evidence_paths": [],
        "log_paths": [],
        "timestamps": {
            "created_at": format_time(current),
            "renewed_at": format_time(current),
            "expires_at": expiration,
        },
        "lease_hours": lease,
        "pinned": False,
        "availability_limitations": [],
        "commands": lifecycle_commands(identifier, state),
    }


def _merge(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(target)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _context(project: Project, config: ProjectConfig, state: Path, identifier: str, approvals: dict[str, bool] | None = None) -> AdapterContext:
    return AdapterContext(project, config, state, showroom_directory(state, identifier), approvals or {})


def _load_record_adapter(record: dict[str, Any]):
    return load_adapter("registered" if record.get("registered") else record["adapter"])


def _resource_scope(adapter: str, identifier: str) -> str:
    # Web showrooms share one Serve/listener namespace; iOS showrooms share one
    # Simulator-template namespace. Non-mutating/generic records need only
    # serialize operations on their own stable identity.
    return adapter if adapter in {"web-local", "ios-simulator"} else f"showroom:{identifier}"


def resolve_id(registry: Registry, value: str | None, cwd: Path | None = None, adapter: str | None = None) -> str:
    if value:
        return value
    project = detect_project(cwd)
    config = detect_config(project)
    selected = adapter or choose_adapter(config)
    identifier = showroom_id(project, selected, config.profile)
    if registry.get(identifier) is None:
        raise ConfigurationError("no showroom found for the current worktree; pass an ID or run showroom start")
    return identifier


def start(registry: Registry, state: Path, cwd: Path | None = None, adapter_name: str | None = None,
          approvals: dict[str, bool] | None = None) -> dict[str, Any]:
    project = detect_project(cwd)
    config = detect_config(project)
    selected = adapter_name or choose_adapter(config)
    if config.cleanup_policy in {"provider", "pull-request"}:
        raise ConfigurationError(
            f"cleanup_policy={config.cleanup_policy!r} is only valid for a surface created and registered by its provider workflow"
        )
    identifier = showroom_id(project, selected, config.profile)
    existing = registry.get(identifier)
    current = now()
    adapter = load_adapter(selected)
    if existing and existing.get("status") == "active":
        expiration = existing.get("timestamps", {}).get("expires_at")
        if existing.get("pinned") or expiration is None or parse_time(expiration) > current:
            if selected == "evidence-only":
                return existing
            try:
                verification_patch = adapter.verify(
                    copy.deepcopy(existing),
                    _context(project, config, state, identifier, approvals),
                )
            except Exception as exc:
                if isinstance(exc, AdapterError):
                    raise
                raise AdapterError(f"{selected} reconciliation failed: {exc}") from exc
            verification_patch.setdefault("verification", {})["checked_at"] = format_time(current)
            reconciled = _merge(existing, verification_patch)
            verification_status = reconciled.get("verification", {}).get("status")
            if verification_status not in VERIFICATION_STATUSES:
                raise AdapterError(f"{selected} returned invalid verification status: {verification_status!r}")

            def save_reconciliation(data: dict[str, Any]) -> bool:
                if data["records"].get(identifier) != existing:
                    return False
                data["records"][identifier] = copy.deepcopy(reconciled)
                return True

            if not registry.update(save_reconciliation):
                raise AdapterError(f"showroom changed while reconciliation was in progress; retry: {identifier}")
            if reconciled.get("verification", {}).get("status") == "passed":
                return reconciled
            if reconciled.get("lifecycle_owner") != "showroom":
                raise AdapterError(f"showroom verification did not pass and lifecycle is externally owned: {identifier}")
            stop(registry, state, identifier, expected_renewed_at=reconciled.get("timestamps", {}).get("renewed_at"))
        # Reconcile the exact expired resources before allocating replacements.
        else:
            stop(registry, state, identifier, expected_renewed_at=existing.get("timestamps", {}).get("renewed_at"))

    if existing and existing.get("status") == "starting":
        created_at = existing.get("timestamps", {}).get("created_at")
        stale = bool(created_at and (current - parse_time(created_at)).total_seconds() >= STARTING_STALE_SECONDS)
        if not stale:
            raise AdapterError(f"showroom start already in progress: {identifier}")
        # Another process can still be completing a long start. The resource
        # lock makes stale takeover wait for it; then the registry snapshot is
        # checked again before exact sidecar/ownership recovery.
        changed = False
        with registry.resource_lock(_resource_scope(selected, identifier)):
            latest = registry.get(identifier)
            if latest != existing:
                changed = True
            else:
                recover = getattr(adapter, "recover", None)
                if recover is not None:
                    recover(copy.deepcopy(existing), _context(project, config, state, identifier, approvals))
                if not registry.delete_if(identifier, lambda value: value == existing):
                    raise AdapterError(f"showroom changed during interrupted-start recovery: {identifier}")
        if changed:
            return start(registry, state, cwd, adapter_name, approvals)
        existing = None

    if existing and existing.get("status") == "stopping":
        # Wait behind a live stop. If its process crashed, the persisted
        # operation timestamp lets the normal idempotent stop path take over.
        with registry.resource_lock(_resource_scope(selected, identifier)):
            latest = registry.get(identifier)
        if latest is None or latest.get("status") != "stopping":
            return start(registry, state, cwd, adapter_name, approvals)
        operation_started = latest.get("operation", {}).get("started_at")
        stale = bool(
            operation_started
            and (current - parse_time(operation_started)).total_seconds() >= STARTING_STALE_SECONDS
        )
        if not stale:
            raise AdapterError(f"showroom stop already in progress: {identifier}")
        stop(registry, state, identifier)
        return start(registry, state, cwd, adapter_name, approvals)

    record = new_record(project, config, selected, current, state)
    # Reserving the stable identity before adapter work prevents two starts from
    # allocating resources independently. Registry writes remain atomic/locked.
    def reserve(data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        current_record = data["records"].get(identifier)
        if current_record and current_record.get("status") == "starting":
            created_at = current_record.get("timestamps", {}).get("created_at")
            stale = bool(created_at and (current - parse_time(created_at)).total_seconds() >= STARTING_STALE_SECONDS)
            if not stale:
                return False, copy.deepcopy(current_record)
        if current_record and current_record.get("status") == "stopping":
            return False, copy.deepcopy(current_record)
        if current_record and current_record.get("status") == "active":
            expiration = current_record.get("timestamps", {}).get("expires_at")
            healthy_lease = current_record.get("pinned") or expiration is None or parse_time(expiration) > current
            if healthy_lease:
                return False, copy.deepcopy(current_record)
        data["records"][identifier] = copy.deepcopy(record)
        return True, copy.deepcopy(record)

    owned, reserved = registry.update(reserve)
    if not owned:
        if reserved.get("status") in {"starting", "stopping"}:
            raise AdapterError(f"showroom lifecycle operation already in progress: {identifier}")
        return reserved
    context = _context(project, config, state, identifier, approvals)
    showroom_dir_existed = context.showroom_dir.exists()
    context.showroom_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
    if not showroom_dir_existed:
        context.showroom_dir.chmod(0o700)
    try:
        with registry.resource_lock(_resource_scope(selected, identifier)):
            patch = adapter.start(copy.deepcopy(record), context)
            completed = _merge(record, patch)
            if completed.get("status") == "starting":
                completed["status"] = "active"

            def commit(data: dict[str, Any]) -> bool:
                if data["records"].get(identifier) != record:
                    return False
                data["records"][identifier] = copy.deepcopy(completed)
                return True

            if not registry.update(commit):
                # A stale attempt must not overwrite a newer reservation. Roll
                # back before releasing the machine resource boundary.
                try:
                    adapter.stop(copy.deepcopy(completed), context)
                except Exception:
                    pass
                raise AdapterError(f"showroom start was superseded by another attempt: {identifier}")
        return completed
    except Exception as exc:
        # The adapter owns rollback of resources it created. Remove only this
        # attempt's unchanged reservation, never a concurrently repaired record.
        registry.delete_if(identifier, lambda value: value == record)
        if not showroom_dir_existed:
            try:
                context.showroom_dir.rmdir()
            except OSError:
                pass
        if isinstance(exc, AdapterError):
            raise
        raise AdapterError(f"{selected} start failed: {exc}") from exc


def get_record(registry: Registry, identifier: str) -> dict[str, Any]:
    record = registry.get(identifier)
    if record is None:
        raise ConfigurationError(f"showroom not found: {identifier}")
    return record


def list_records(registry: Registry) -> list[dict[str, Any]]:
    records = registry.read()["records"].values()
    return sorted((copy.deepcopy(item) for item in records), key=lambda item: item["timestamps"]["created_at"])


def _record_context(record: dict[str, Any], state: Path) -> AdapterContext | None:
    worktree = Path(record["worktree"]["path"])
    if not worktree.is_dir():
        return None
    try:
        project = detect_project(worktree)
        config = detect_config(project)
    except (ConfigurationError, OSError):
        return None
    return _context(project, config, state, record["id"])


def verify(registry: Registry, state: Path, identifier: str) -> dict[str, Any]:
    record = get_record(registry, identifier)
    if record.get("status") in {"stopping", "stopped"}:
        raise AdapterError(f"showroom is not active: {identifier}")
    adapter = _load_record_adapter(record)
    patch = adapter.verify(copy.deepcopy(record), _record_context(record, state))
    checked = format_time(now())
    patch.setdefault("verification", {})["checked_at"] = checked

    def commit(data: dict[str, Any]) -> dict[str, Any]:
        current = data["records"].get(identifier)
        if current is None:
            raise ConfigurationError(f"showroom not found: {identifier}")
        lifecycle_fields = ("status", "adapter", "provider_resource_id", "resources", "worktree")
        if any(current.get(field) != record.get(field) for field in lifecycle_fields):
            raise AdapterError(f"showroom lifecycle changed during verification; retry: {identifier}")
        # Pin/renew metadata may change while a slow external check runs. Merge
        # the result into the latest record so those changes survive.
        updated = _merge(current, patch)
        data["records"][identifier] = copy.deepcopy(updated)
        return copy.deepcopy(updated)

    return registry.update(commit)


def renew(registry: Registry, identifier: str, lease_hours: float | None = None) -> dict[str, Any]:
    current = now()

    def operation(data: dict[str, Any]) -> dict[str, Any]:
        record = data["records"].get(identifier)
        if record is None:
            raise ConfigurationError(f"showroom not found: {identifier}")
        if record.get("status") in {"starting", "stopping"}:
            raise AdapterError(f"showroom lifecycle operation is in progress: {identifier}")
        hours = lease_hours if lease_hours is not None else record.get("lease_hours", LOCAL_LEASE_HOURS)
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or hours <= 0:
            raise ConfigurationError("lease hours must be a positive number")
        record["lease_hours"] = float(hours)
        record["timestamps"]["renewed_at"] = format_time(current)
        record["timestamps"]["expires_at"] = (
            None
            if record.get("pinned")
            or record.get("cleanup_policy") in {"manual", "provider", "pull-request"}
            else expires_at(current, float(hours))
        )
        return copy.deepcopy(record)

    return registry.update(operation)


def set_pinned(registry: Registry, identifier: str, pinned: bool) -> dict[str, Any]:
    current = now()

    def operation(data: dict[str, Any]) -> dict[str, Any]:
        record = data["records"].get(identifier)
        if record is None:
            raise ConfigurationError(f"showroom not found: {identifier}")
        if record.get("status") in {"starting", "stopping"}:
            raise AdapterError(f"showroom lifecycle operation is in progress: {identifier}")
        record["pinned"] = pinned
        if pinned:
            record["timestamps"]["expires_at"] = None
        elif record.get("cleanup_policy") in {"manual", "provider", "pull-request"}:
            record["timestamps"]["renewed_at"] = format_time(current)
            record["timestamps"]["expires_at"] = None
        else:
            hours = float(record.get("lease_hours", LOCAL_LEASE_HOURS))
            record["timestamps"]["renewed_at"] = format_time(current)
            record["timestamps"]["expires_at"] = expires_at(current, hours)
        return copy.deepcopy(record)

    return registry.update(operation)


def stop(registry: Registry, state: Path, identifier: str, remove: bool = False, expected_renewed_at: str | None = None) -> dict[str, Any]:
    # Starts and stops share external namespaces (Serve listeners, launchd, and
    # CoreSimulator). Holding this cross-process lock through the exact mutation
    # closes check-then-act allocation races and makes crash takeover safe.
    snapshot = get_record(registry, identifier)
    with registry.resource_lock(_resource_scope(snapshot["adapter"], identifier)):
        return _stop_locked(registry, state, identifier, remove, expected_renewed_at)


def _stop_locked(registry: Registry, state: Path, identifier: str, remove: bool = False,
                 expected_renewed_at: str | None = None) -> dict[str, Any]:
    record = get_record(registry, identifier)
    if record.get("status") == "stopped":
        fingerprint = record.get("timestamps", {}).get("renewed_at")
        expected_matches = expected_renewed_at is None or expected_renewed_at == fingerprint
        if remove and expected_matches and not record.get("pinned"):
            registry.delete_if(
                identifier,
                lambda current: current.get("status") == "stopped"
                and current.get("timestamps", {}).get("renewed_at") == fingerprint
                and not current.get("pinned"),
            )
        return record
    if not record.get("registered") and record.get("lifecycle_owner") != "showroom":
        raise AdapterError(f"showroom lifecycle is owned by {record.get('lifecycle_owner')!r}")
    if expected_renewed_at is not None:
        renewed = record.get("timestamps", {}).get("renewed_at")
        if renewed != expected_renewed_at or record.get("pinned"):
            return record

    operation_time = now()

    def claim(data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        current = data["records"].get(identifier)
        if current is None:
            raise ConfigurationError(f"showroom not found: {identifier}")
        if current.get("status") == "stopped":
            return False, copy.deepcopy(current)
        if current.get("status") == "stopping":
            operation = current.get("operation", {})
            started_at = operation.get("started_at")
            stale = bool(
                started_at
                and (operation_time - parse_time(started_at)).total_seconds() >= STARTING_STALE_SECONDS
            )
            if not stale:
                raise AdapterError(f"showroom stop already in progress: {identifier}")
        if expected_renewed_at is not None:
            renewed = current.get("timestamps", {}).get("renewed_at")
            if renewed != expected_renewed_at or current.get("pinned"):
                return False, copy.deepcopy(current)
        claimed = copy.deepcopy(current)
        if current.get("status") == "stopping":
            claimed["status"] = current.get("operation", {}).get("previous_status", "active")
            claimed.pop("operation", None)
        previous_status = claimed.get("status", "active")
        current["status"] = "stopping"
        current["operation"] = {
            "kind": "stop",
            "started_at": format_time(operation_time),
            "previous_status": previous_status,
        }
        return True, claimed

    owned, record = registry.update(claim)
    if not owned:
        return record
    adapter = _load_record_adapter(record)
    try:
        patch = adapter.stop(copy.deepcopy(record), _record_context(record, state))
    except Exception as exc:
        def restore(data: dict[str, Any]) -> None:
            current = data["records"].get(identifier)
            if current and current.get("status") == "stopping":
                data["records"][identifier] = copy.deepcopy(record)

        registry.update(restore)
        if isinstance(exc, AdapterError):
            raise
        raise AdapterError(f"{record['adapter']} stop failed: {exc}") from exc
    updated = _merge(record, patch)
    updated["status"] = "stopped"
    updated.pop("operation", None)
    def commit(data: dict[str, Any]) -> bool:
        current = data["records"].get(identifier)
        if current is None or current.get("status") != "stopping":
            return False
        data["records"][identifier] = copy.deepcopy(updated)
        return True

    if not registry.update(commit):
        raise AdapterError(f"showroom record changed while stop was in progress: {identifier}")
    if remove:
        fingerprint = updated.get("timestamps", {}).get("renewed_at")
        registry.delete_if(identifier, lambda current: current.get("status") == "stopped" and current.get("timestamps", {}).get("renewed_at") == fingerprint)
    return updated


def cleanup_candidates(records: list[dict[str, Any]], current=None) -> list[dict[str, Any]]:
    at = current or now()
    candidates: list[dict[str, Any]] = []
    for record in records:
        if record.get("pinned"):
            continue
        if record.get("cleanup_policy") == "manual" and record.get("status") != "stopped":
            continue
        reasons: list[str] = []
        expiration = record.get("timestamps", {}).get("expires_at")
        if expiration and parse_time(expiration) <= at:
            reasons.append("expired lease")
        repository_path = record.get("repository", {}).get("path")
        worktree_path = record.get("worktree", {}).get("path")
        if repository_path and not Path(repository_path).exists():
            reasons.append("missing repository")
        if worktree_path and not Path(worktree_path).exists():
            reasons.append("missing worktree")
        if record.get("status") == "stopped":
            reasons.append("stopped")
        if reasons:
            candidates.append({"record": record, "reasons": reasons})
    return candidates


def cleanup(registry: Registry, state: Path, dry_run: bool) -> dict[str, Any]:
    records = list_records(registry)
    candidates = cleanup_candidates(records)
    candidate_ids = {item["record"]["id"] for item in candidates}
    # Reconciliation is read-only here. It detects an active local process,
    # route, or manager-owned Simulator that no longer matches its exact record.
    for record in records:
        if (
            record["id"] in candidate_ids
            or record.get("pinned")
            or record.get("cleanup_policy") == "manual"
            or record.get("status") != "active"
            or record.get("registered")
        ):
            continue
        try:
            adapter = _load_record_adapter(record)
            reconcile = getattr(adapter, "reconcile", adapter.verify)
            patch = reconcile(copy.deepcopy(record), _record_context(record, state))
            verification_status = patch.get("verification", {}).get("status")
            if verification_status in {"failed", "stale"}:
                detail = patch.get("verification", {}).get("detail") or "registered resources are unhealthy"
                candidates.append({"record": record, "reasons": [f"stale resources: {detail}"]})
                candidate_ids.add(record["id"])
        except (AdapterError, OSError) as exc:
            candidates.append({"record": record, "reasons": [f"reconciliation failed: {exc}"]})
            candidate_ids.add(record["id"])

    actions: list[dict[str, Any]] = []
    planning_errors: list[dict[str, str]] = []
    for item in candidates:
        record = item["record"]
        action_name = "remove-registration" if record.get("lifecycle_owner") in {"provider", "pull-request"} else "stop-and-remove"
        action: dict[str, Any] = {
            "id": record["id"],
            "reasons": item["reasons"],
            "action": f"would-{action_name}" if dry_run else action_name,
        }
        if dry_run and action_name == "stop-and-remove" and record.get("status") != "stopped":
            try:
                adapter = _load_record_adapter(record)
                planner = getattr(adapter, "cleanup_plan", None)
                if planner is not None:
                    action["exact_plan"] = planner(copy.deepcopy(record), _record_context(record, state))
            except (AdapterError, OSError) as exc:
                planning_errors.append({"id": record["id"], "error": str(exc)})
        actions.append(action)
    if dry_run:
        return {"dry_run": True, "actions": actions, "errors": planning_errors}

    errors: list[dict[str, str]] = []
    completed: list[dict[str, Any]] = []
    for item, action in zip(candidates, actions):
        record = item["record"]
        try:
            before = record.get("timestamps", {}).get("renewed_at")
            stopped = stop(registry, state, record["id"], remove=True, expected_renewed_at=before)
            if stopped.get("status") == "stopped":
                completed.append(action)
        except (AdapterError, ConfigurationError) as exc:
            # Provider-owned registrations can be forgotten after their own
            # lifecycle expires, but showroom never claims to delete them.
            if record.get("lifecycle_owner") == "provider":
                fingerprint = record.get("timestamps", {}).get("renewed_at")
                removed = registry.delete_if(record["id"], lambda current: not current.get("pinned") and current.get("timestamps", {}).get("renewed_at") == fingerprint)
                if removed:
                    action["action"] = "remove-registration"
                    completed.append(action)
                    continue
            errors.append({"id": record["id"], "error": str(exc)})
    return {"dry_run": False, "actions": completed, "errors": errors}


def register(registry: Registry, project: Project, *, adapter: str, profile: str, record_type: str, provider: str | None,
             provider_resource_id: str | None, lifecycle_owner: str, surface: dict[str, Any], verification_status: str,
             evidence_paths: list[str], log_paths: list[str], limitations: list[str], lease_hours: float | None) -> dict[str, Any]:
    surface = copy.deepcopy(surface)
    current = now()
    identifier = showroom_id(project, adapter, profile)
    if lease_hours is None:
        lease_hours = LOCAL_LEASE_HOURS if adapter == "evidence-only" and provider is None else HOSTED_LEASE_HOURS
    if lifecycle_owner == "pr":
        lifecycle_owner = "pull-request"
    def normalize_path(value: str) -> str:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = project.worktree_root / path
        return str(path.resolve(strict=False))

    if surface.get("artifact"):
        surface["artifact"] = normalize_path(surface["artifact"])
    evidence_paths = [normalize_path(value) for value in evidence_paths]
    log_paths = [normalize_path(value) for value in log_paths]

    normalized_surface = {
        "url": surface.get("url"),
        "device": surface.get("device"),
        "artifact": surface.get("artifact"),
        "command": surface.get("command"),
    }

    def operation(data: dict[str, Any]) -> dict[str, Any]:
        existing = data["records"].get(identifier)
        if existing:
            if not existing.get("registered"):
                raise AdapterError(
                    f"registration would replace manager-owned local resources; use a distinct profile or stop them first: {identifier}"
                )
            if existing.get("status") in {"starting", "stopping"}:
                raise AdapterError(f"registered showroom lifecycle operation is in progress: {identifier}")
            prior_identity = (
                existing.get("adapter"),
                existing.get("provider"),
                existing.get("provider_resource_id"),
                existing.get("lifecycle_owner"),
            )
            requested_identity = (adapter, provider, provider_resource_id, lifecycle_owner)
            if prior_identity != requested_identity:
                raise AdapterError(
                    f"registration identity conflicts with an existing surface; use a distinct profile: {identifier}"
                )
            if provider_resource_id is None and existing.get("surface") != normalized_surface:
                raise AdapterError(
                    f"registration without a provider resource ID cannot replace a different surface: {identifier}"
                )
        created = existing.get("timestamps", {}).get("created_at") if existing else format_time(current)
        pinned = bool(existing and existing.get("pinned"))
        expiration = None if pinned or lifecycle_owner in {"provider", "pull-request"} else expires_at(current, lease_hours)
        record = {
            "record_version": 1,
            "id": identifier,
            "type": record_type,
            "adapter": adapter,
            "registered": True,
            "provider": provider,
            "provider_resource_id": provider_resource_id,
            "lifecycle_owner": lifecycle_owner,
            "cleanup_policy": lifecycle_owner if lifecycle_owner in {"provider", "pull-request"} else "lease",
            "profile": profile,
            "status": "active",
            "repository": {"id": project.repository_id, "path": str(project.repository_root), "common_directory": str(project.repository_common_dir), "source": project.source},
            "worktree": {"id": project.worktree_id, "path": str(project.worktree_root)},
            "surface": normalized_surface,
            "resources": {"process": None, "launchd": None, "port": None, "simulator_udid": None},
            "verification": {"status": verification_status, "checked_at": format_time(current) if verification_status != "pending" else None, "detail": None},
            "evidence_paths": evidence_paths,
            "log_paths": log_paths,
            "timestamps": {"created_at": created, "renewed_at": format_time(current), "expires_at": expiration},
            "lease_hours": lease_hours,
            "pinned": pinned,
            "availability_limitations": limitations,
            "commands": lifecycle_commands(identifier, registry.root),
        }
        data["records"][identifier] = copy.deepcopy(record)
        return copy.deepcopy(record)

    return registry.update(operation)


def doctor(registry: Registry) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    adapters: dict[str, Any] = {}
    try:
        records = registry.read()["records"]
        checks.append({"name": "registry", "ok": True, "detail": f"valid runtime registry structure; {len(records)} record(s)"})
    except Exception as exc:
        checks.append({"name": "registry", "ok": False, "detail": str(exc)})
    parent = registry.root if registry.root.exists() else registry.root.parent
    checks.append({"name": "state-directory", "ok": parent.exists() and os.access(parent, os.W_OK), "detail": str(registry.root)})
    checks.append({"name": "python", "ok": True, "detail": "Python 3.11+ standard library runtime"})
    try:
        web_adapter = load_adapter("web-local")
        adapters["web-local"] = web_adapter.doctor()
    except (AdapterError, OSError) as exc:
        adapters["web-local"] = {"available": False, "detail": str(exc)}
    adapters["ios-simulator"] = {
        "available": sys.platform == "darwin" and bool(shutil.which("xcodebuild")) and bool(shutil.which("xcrun")),
        "xcodebuild": shutil.which("xcodebuild"),
        "xcrun": shutil.which("xcrun"),
        "detail": "Requires a logged-in macOS session, an installed Simulator runtime, and project-specific discovery.",
    }
    return {"ok": all(check["ok"] for check in checks), "checks": checks, "adapters": adapters}
