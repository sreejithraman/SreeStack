#!/usr/bin/env python3
"""Guard the last-resort CoreSimulator restart. See references/break-glass.md.

Any failed read counts as a failed check. Exit codes: 0 go, 1 error, 2 another session
holds the claim, 3 a rule or check refuses, 4 the restart failed.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

STATE = Path(os.environ.get("SIMULATOR_BREAK_GLASS_STATE", "~/.simulator-break-glass")).expanduser()
CLAIM = STATE / "claim"
OWNER = CLAIM / "owner.json"
LOG = STATE / "log.jsonl"
LOCK = STATE / "lock"

HOLD_SECONDS = 30 * 60
RESTART_MARGIN_SECONDS = 5 * 60
STALE_CLAIM_SECONDS = 45 * 60
RESTART_SPACING_SECONDS = 6 * 3600
ABORT_SPACING_SECONDS = 2 * 3600
READ_TIMEOUT_SECONDS = 20
EXIT_WAIT_SECONDS = 15
MAX_CPU_PERCENT = 40
NORMAL_MEMORY_PRESSURE = 1

SERVICE = "com.apple.CoreSimulator.CoreSimulatorService"
SERVICE_PROGRAM = f"/Library/Developer/PrivateFrameworks/CoreSimulator.framework/Versions/A/XPCServices/{SERVICE}.xpc/Contents/MacOS/"
PLANES = {"--local": "worker", "--gateway": "gateway"}
CONSUMERS = re.compile(
    r"launchd_sim|Simulator\.app/Contents/MacOS|xcodebuild|xctest|\bsimctl |simdiskimaged-client|qemu-system|/emulator |maestro|detox|agent-device"
)
# SimLock keeps these running while idle, so they prove nothing about device work.
IDLE_DAEMONS = re.compile(r"agent-device/dist/\S*daemon\.js|\bsimctl (--set \S+ )?list\b")


class Refused(Exception):
    """A rule or check says no."""


def read(*argv: str) -> str:
    return subprocess.run(argv, capture_output=True, text=True, timeout=READ_TIMEOUT_SECONDS, check=True).stdout


@contextlib.contextmanager
def machine_lock():
    """Serialize every read-then-write of the claim and the log across sessions."""
    STATE.mkdir(exist_ok=True)
    with LOCK.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def events() -> list[dict]:
    if not LOG.exists():
        return []
    try:
        return [json.loads(line) for line in LOG.read_text().splitlines() if line]
    except ValueError as error:
        raise Refused(f"{LOG} is unreadable, and only the user can repair it: {error}")


def record(event: str, thread: str, **details) -> None:
    STATE.mkdir(exist_ok=True)
    with LOG.open("a") as log:
        log.write(json.dumps({"at": int(time.time()), "event": event, "thread": thread, **details}) + "\n")
        log.flush()
        os.fsync(log.fileno())


def refusal(now: float) -> str | None:
    """Return why the log rules out a restart. A restart with no result counts as failed."""
    restart_at, failed = None, False
    aborted_at = None
    for entry in events():
        if entry["event"] == "restart-attempt":
            restart_at, failed = entry["at"], True
        elif entry["event"] == "finished":
            failed = entry.get("result") != "acquired"
        elif entry["event"] == "cleared":
            failed = False
        elif entry["event"] == "aborted":
            aborted_at = entry["at"]
    if failed:
        return "an earlier restart failed or has no result, and only the user can clear it"
    if restart_at is not None and now - restart_at < RESTART_SPACING_SECONDS:
        return "a restart ran in the last 6 hours"
    if aborted_at is not None and now - aborted_at < ABORT_SPACING_SECONDS:
        return "an attempt aborted in the last 2 hours"
    return None


def owner() -> dict:
    return json.loads(OWNER.read_text())


def claim_age(now: float) -> float:
    try:
        return now - owner()["claimedAt"]
    except (OSError, ValueError, KeyError):
        return now - CLAIM.stat().st_mtime


def take_claim(thread: str, now: float) -> dict:
    """Claim under the machine lock, and read the log there so a late contender sees the last result."""
    with machine_lock():
        if CLAIM.exists() and claim_age(now) < STALE_CLAIM_SECONDS:
            raise FileExistsError(CLAIM)
        reason = refusal(now)  # First, so an owner still acquiring after its restart keeps its claim.
        if reason:
            raise Refused(reason)
        shutil.rmtree(CLAIM, ignore_errors=True)
        CLAIM.mkdir()
        claim = {"thread": thread, "claimedAt": int(now), "holdUntil": int(now) + HOLD_SECONDS}
        OWNER.write_text(json.dumps(claim))
        return claim


def release_claim(thread: str) -> None:
    require_owner(thread)
    shutil.rmtree(CLAIM)


def require_owner(thread: str) -> dict:
    claim = owner()
    if claim["thread"] != thread:
        raise Refused(f"{claim['thread']} owns the claim")
    return claim


def plane_quiet(plane: str, status: dict) -> bool:
    try:
        capacity = status["capacity"]
        zero = lambda value: type(value) is int and value == 0
        return (
            status["daemon"]["health"] == "running"
            and status["daemon"]["mode"] == PLANES[plane]
            and status["leases"] == []
            and status["waiting"] == []
            and status["installs"] == []
            and zero(status["queueDepth"])
            and zero(status["physicalQueueDepth"])
            and all(zero(capacity[kind][field]) for kind in ("ios", "android", "global") for field in ("running", "reserved", "warm"))
        )
    except (KeyError, TypeError):
        return False


def consumers(rows: list[str], own_pids: set[int]) -> list[str]:
    rows = [row for row in rows if row.strip()]
    if not rows:
        raise ValueError("empty process list")
    return [
        row.strip()[:170]
        for row in rows
        if CONSUMERS.search(row) and not IDLE_DAEMONS.search(row) and int(row.split(None, 1)[0]) not in own_pids
    ]


def service_target() -> str:
    return f"user/{os.getuid()}/{SERVICE}"


def service_pid() -> int:
    match = re.search(r"^\s*pid = (\d+)$", read("/bin/launchctl", "print", service_target()), re.M)
    if not match:
        raise ValueError("service has no pid")
    return int(match.group(1))


def is_service(pid: int) -> bool:
    found = subprocess.run(["/bin/ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True, timeout=READ_TIMEOUT_SECONDS)
    return found.stdout.startswith(SERVICE_PROGRAM)


def cpu_percent() -> float:
    lines = [line for line in read("/usr/bin/top", "-l", "2", "-n", "0", "-s", "3").splitlines() if line.startswith("CPU usage")]
    user, system = re.findall(r"([\d.]+)% (?:user|sys)", lines[-1])
    return float(user) + float(system)


def gate(t3_open_sessions: int) -> dict:
    """Read the machine. Any exception means no."""
    try:
        cpu = cpu_percent()  # Slow, so it runs before the reads that must be freshest.
        planes = {plane: json.loads(read("simlock", plane, "daemon", "status", "--json")) for plane in PLANES}
        pid = service_pid()
        found = consumers(read("/bin/ps", "-axo", "pid=,command=").splitlines(), {os.getpid(), os.getppid()})
        checks = {
            "admin": re.search(r"^Role:\s+admin$", read("simlock", "whoami"), re.M) is not None,
            "noT3DeviceSessions": t3_open_sessions == 0,
            "workerQuiet": plane_quiet("--local", planes["--local"]),
            "gatewayQuiet": plane_quiet("--gateway", planes["--gateway"]),
            "noConsumers": not found,
            "cpu": cpu <= MAX_CPU_PERCENT,
            "memory": int(read("/usr/sbin/sysctl", "-n", "kern.memorystatus_vm_pressure_level")) == NORMAL_MEMORY_PRESSURE,
            "serviceIsCoreSimulator": is_service(pid),
        }
        return {"go": all(checks.values()), "checks": checks, "consumers": found, "cpuPercent": cpu, "pid": pid}
    except Exception as error:  # Fail closed on every read.
        return {"go": False, "readFailure": repr(error)[:300]}


def require_restartable(thread: str) -> dict:
    claim = require_owner(thread)
    if time.time() >= claim["holdUntil"] - RESTART_MARGIN_SECONDS:
        raise Refused("too close to the end of the hold")
    reason = refusal(time.time())
    if reason:
        raise Refused(reason)
    return claim


def restart(thread: str, t3_open_sessions: int) -> dict:
    require_restartable(thread)
    result = gate(t3_open_sessions)
    if not result["go"]:
        raise Refused(json.dumps(result))
    old_pid = result["pid"]
    with machine_lock():
        require_restartable(thread)  # The gate is slow, so ask again right before the kill.
        record("restart-attempt", thread, oldPid=old_pid)
    killed = subprocess.run(["/bin/launchctl", "kill", "SIGTERM", service_target()], capture_output=True, text=True, timeout=READ_TIMEOUT_SECONDS)
    deadline = time.monotonic() + EXIT_WAIT_SECONDS
    while time.monotonic() < deadline and is_service(old_pid):
        time.sleep(0.5)
    return {"launchctlExit": killed.returncode, "oldPid": old_pid, "oldPidExited": not is_service(old_pid)}


def wait() -> None:
    """Return when the claim is gone or its hold has expired."""
    while CLAIM.exists():
        try:
            deadline = owner()["holdUntil"]
        except (OSError, ValueError, KeyError):
            deadline = CLAIM.stat().st_mtime + HOLD_SECONDS
        if time.time() >= deadline:
            return
        time.sleep(5)


def report(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload))
    return code


def run(args: argparse.Namespace) -> int:
    now = time.time()
    if args.command == "status":
        reason = refusal(now)
        return report({"go": reason is None, "reason": reason}, 3 if reason else 0)
    if args.command == "claim":
        try:
            claim = take_claim(args.thread, now)
            return report({"go": True, "holdUntilLocal": time.strftime("%H:%M %Z", time.localtime(claim["holdUntil"])), **claim})
        except FileExistsError:
            return report({"go": False, "reason": "another session holds the claim"}, 2)
    if args.command == "check":
        result = gate(args.t3_open_sessions)
        return report(result, 0 if result["go"] else 3)
    if args.command == "restart":
        outcome = restart(args.thread, args.t3_open_sessions)
        return report(outcome, 0 if outcome["launchctlExit"] == 0 and outcome["oldPidExited"] else 4)
    if args.command == "pid":
        try:
            return report({"pid": service_pid()})
        except (ValueError, subprocess.SubprocessError) as error:
            return report({"pid": None, "reason": str(error)[:200]})
    if args.command == "wait":
        wait()
        return report({"claimHeld": CLAIM.exists()})
    if args.command == "finish":
        require_owner(args.thread)
        record("finished", args.thread, result=args.result, newPid=args.new_pid)
        release_claim(args.thread)
        return report({"finished": args.result})
    if args.command == "abort":
        require_owner(args.thread)
        record("aborted", args.thread, reason=args.reason)
        release_claim(args.thread)
        return report({"aborted": args.reason})
    if args.command == "clear":
        record("cleared", "user", reason=args.reason)
        return report({"cleared": args.reason})
    raise AssertionError(args.command)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="say whether the log allows a restart")
    commands.add_parser("wait", help="return when the claim is gone or its hold expires")
    commands.add_parser("pid", help="print the service's current PID")
    commands.add_parser("claim", help="take the machine-wide claim").add_argument("--thread", required=True)
    commands.add_parser("check", help="read the machine").add_argument("--t3-open-sessions", type=int, required=True)
    restarting = commands.add_parser("restart", help="check again, log, and restart once")
    restarting.add_argument("--thread", required=True)
    restarting.add_argument("--t3-open-sessions", type=int, required=True)
    finishing = commands.add_parser("finish", help="record the acquisition and release the claim")
    finishing.add_argument("--thread", required=True)
    finishing.add_argument("--result", choices=("acquired", "failed"), required=True)
    finishing.add_argument("--new-pid", type=int)
    aborting = commands.add_parser("abort", help="record an abort and release the claim")
    aborting.add_argument("--thread", required=True)
    aborting.add_argument("--reason", required=True)
    commands.add_parser("clear", help="for the user: clear a failed restart").add_argument("--reason", required=True)
    return root


def main() -> int:
    try:
        return run(parser().parse_args())
    except Refused as refused:
        return report({"go": False, "reason": str(refused)}, 3)


if __name__ == "__main__":
    sys.exit(main())
