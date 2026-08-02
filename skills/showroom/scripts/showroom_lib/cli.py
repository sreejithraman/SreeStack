from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from . import __version__
from .core import cleanup, doctor, get_record, list_records, register, renew, resolve_id, set_pinned, start, stop, verify
from .errors import ShowroomError
from .paths import state_root
from .project import detect_project
from .registry import Registry


def _add_common(parser: argparse.ArgumentParser, *, identifier: bool = False) -> None:
    if identifier:
        parser.add_argument("id", nargs="?")
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="emit machine-readable JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="showroom", description="Manage verified review surfaces")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--state-dir", type=Path, help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="command", required=True)

    start_parser = commands.add_parser("start", help="start or return the current worktree showroom")
    start_parser.add_argument("--adapter")
    start_parser.add_argument("--cwd", type=Path, default=Path.cwd())
    start_parser.add_argument("--approve-persistence", action="store_true", help="authorize adapter-owned persistent user service changes")
    start_parser.add_argument("--approve-tailscale-config", action="store_true", help="authorize exact Tailscale Serve configuration changes")
    _add_common(start_parser)
    for name in ("status", "verify", "pin", "unpin", "stop"):
        _add_common(commands.add_parser(name), identifier=True)
    renew_parser = commands.add_parser("renew")
    renew_parser.add_argument("id", nargs="?")
    renew_parser.add_argument("--hours", type=float)
    _add_common(renew_parser)
    _add_common(commands.add_parser("list"))
    cleanup_parser = commands.add_parser("cleanup")
    cleanup_parser.add_argument("--dry-run", action="store_true")
    _add_common(cleanup_parser)
    _add_common(commands.add_parser("doctor"))

    register_parser = commands.add_parser("register", help="register a hosted or evidence review surface")
    register_parser.add_argument("--cwd", type=Path, default=Path.cwd())
    register_parser.add_argument("--adapter", required=True)
    register_parser.add_argument("--profile", default="default")
    register_parser.add_argument("--type", dest="record_type", required=True)
    register_parser.add_argument("--provider")
    register_parser.add_argument("--provider-resource-id")
    register_parser.add_argument("--lifecycle-owner", choices=("showroom", "provider", "pull-request", "pr"), default="provider")
    surface = register_parser.add_mutually_exclusive_group(required=True)
    surface.add_argument("--url")
    surface.add_argument("--device")
    surface.add_argument("--artifact")
    surface.add_argument("--surface-command", nargs="+")
    register_parser.add_argument("--verification-status", choices=("pending", "passed", "failed", "blocked", "stale"), default="pending")
    register_parser.add_argument("--evidence", action="append", default=[])
    register_parser.add_argument("--log", action="append", default=[])
    register_parser.add_argument("--limitation", action="append", default=[])
    register_parser.add_argument("--lease-hours", type=float)
    _add_common(register_parser)
    return parser


def _human_record(record: dict[str, Any]) -> str:
    surface = record.get("surface", {})
    value = surface.get("url") or surface.get("device") or surface.get("artifact") or surface.get("command") or "none"
    verification = record.get("verification", {}).get("status", "unknown")
    expiration = "pinned" if record.get("pinned") else record.get("timestamps", {}).get("expires_at", "none")
    repository = record.get("repository", {})
    worktree = record.get("worktree", {})
    timestamps = record.get("timestamps", {})
    evidence = ", ".join(record.get("evidence_paths", [])) or "none"
    limitations = ", ".join(record.get("availability_limitations", [])) or "none"
    commands = record.get("commands", {})
    command_lines = "\n".join(f"  {name}: {command}" for name, command in commands.items())
    return (
        f"Showroom: {record['id']}\n"
        f"Type: {record['type']} ({record.get('adapter')})\n"
        f"Status: {record.get('status')}\n"
        f"Surface: {value}\n"
        f"Source: {repository.get('source') or repository.get('path')}\n"
        f"Worktree: {worktree.get('path')}\n"
        f"Verification: {verification}\n"
        f"Evidence: {evidence}\n"
        f"Created: {timestamps.get('created_at')}\n"
        f"Expires: {expiration}\n"
        f"Availability: {limitations}\n"
        f"Commands:\n{command_lines}"
    )


def _emit(value: Any, json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, sort_keys=True))
    elif isinstance(value, list):
        if not value:
            print("No showrooms.")
        else:
            print("\n\n".join(_human_record(record) for record in value))
    elif isinstance(value, dict) and "id" in value:
        print(_human_record(value))
    elif isinstance(value, dict):
        print(json.dumps(value, indent=2, sort_keys=True))
    else:
        print(value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.state_dir.resolve(strict=False) if args.state_dir else state_root()
    registry = Registry(root)
    json_output = getattr(args, "json", False)
    try:
        if args.command == "start":
            result = start(
                registry,
                root,
                args.cwd,
                args.adapter,
                {"persistence": args.approve_persistence, "tailscale_config": args.approve_tailscale_config},
            )
        elif args.command == "list":
            result = list_records(registry)
        elif args.command == "doctor":
            result = doctor(registry)
        elif args.command == "cleanup":
            result = cleanup(registry, root, args.dry_run)
        elif args.command == "register":
            if args.lease_hours is not None and args.lease_hours <= 0:
                raise ShowroomError("lease hours must be positive")
            project = detect_project(args.cwd)
            result = register(
                registry,
                project,
                adapter=args.adapter,
                profile=args.profile,
                record_type=args.record_type,
                provider=args.provider,
                provider_resource_id=args.provider_resource_id,
                lifecycle_owner=args.lifecycle_owner,
                surface={"url": args.url, "device": args.device, "artifact": args.artifact, "command": args.surface_command},
                verification_status=args.verification_status,
                evidence_paths=args.evidence,
                log_paths=args.log,
                limitations=args.limitation,
                lease_hours=args.lease_hours,
            )
        else:
            identifier = resolve_id(registry, args.id)
            if args.command == "status":
                result = get_record(registry, identifier)
            elif args.command == "verify":
                result = verify(registry, root, identifier)
            elif args.command == "renew":
                result = renew(registry, identifier, args.hours)
            elif args.command == "pin":
                result = set_pinned(registry, identifier, True)
            elif args.command == "unpin":
                result = set_pinned(registry, identifier, False)
            elif args.command == "stop":
                result = stop(registry, root, identifier)
            else:  # pragma: no cover - argparse enforces this
                parser.error(f"unsupported command: {args.command}")
                return 2
        _emit(result, json_output)
        if args.command == "doctor" and not result["ok"]:
            return 1
        if args.command == "verify" and result.get("verification", {}).get("status") in {"failed", "blocked"}:
            return 1
        if args.command == "cleanup" and result.get("errors"):
            return 1
        return 0
    except ShowroomError as exc:
        if json_output:
            print(json.dumps({"error": str(exc), "type": type(exc).__name__}, sort_keys=True), file=sys.stderr)
        else:
            print(f"showroom: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
