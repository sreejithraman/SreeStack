#!/usr/bin/env python3
"""Link SreeStack skills and shared instructions into each host's home directory.

Each top-level <host>/setup.json names where that host reads skills and its
global instructions, relative to the home directory, and which skills it skips.
Sync also merges the public settings templates listed in host_settings.py.
Supports the macOS system Python (3.9) because Git hooks may run it.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import itertools
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile

import host_settings

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
INSTRUCTIONS = ROOT / "global" / "AGENTS.md"
MANIFEST_KEYS = {"skills", "instructions", "exclude"}
MAIN_BRANCH = "refs/heads/main"
HOOK_EVENT = "reference-transaction"
HANDLER_NAME = "sreestack-host-sync"
HANDLER_MARKER = "# Installed by SreeStack scripts/sync_hosts.py --install-hooks."
VENV_PYTHON = ".venv/bin/python"
# Git runs this hook for ref updates in every worktree, so it must skip
# unrelated updates before reading checkout files or config, and must never
# fail the preparing or prepared phases (that would abort the Git command).
HANDLER_SCRIPT = f"""#!/bin/sh
{HANDLER_MARKER}
# Syncs host setup after a committed update to main or HEAD in the primary
# checkout with main checked out. Git ignores this phase's exit status.
relevant=
while read -r _ _ ref; do
  case $ref in HEAD | {MAIN_BRANCH}) relevant=1 ;; esac
done
[ "$1" = committed ] && [ -n "$relevant" ] || exit 0
[ "$(git rev-parse --absolute-git-dir 2>/dev/null)" = \\
  "$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" ] || exit 0
[ "$(git symbolic-ref -q HEAD)" = {MAIN_BRANCH} ] || exit 0
root="$(git rev-parse --show-toplevel)"
script="$root/scripts/sync_hosts.py"
python="$root/{VENV_PYTHON}"
[ -x "$python" ] || python=python3
if [ ! -f "$script" ]; then
  echo "sreestack: $script is missing" >&2
elif ! command -v "$python" >/dev/null 2>&1; then
  echo "sreestack: python3 is not on Git's PATH" >&2
elif "$python" "$script" --hook; then
  exit 0
fi
echo "sreestack: host sync failed. The Git operation completed and was not rolled" \\
  "back. Fix the problem above, run {VENV_PYTHON} scripts/sync_hosts.py, then confirm" \\
  "with {VENV_PYTHON} scripts/sync_hosts.py --check." >&2
exit 1
"""
CHAIN_SCRIPT = f"""# BEGIN SreeStack host sync
sreestack_handler="$(git rev-parse --path-format=absolute --git-common-dir)/hooks/{HANDLER_NAME}"
if [ -x "$sreestack_handler" ] && \\
   sreestack_refs=$(mktemp "${{TMPDIR:-/tmp}}/sreestack-refs.XXXXXX"); then
  cat > "$sreestack_refs" || {{ rm -f "$sreestack_refs"; exit 1; }}
  "$sreestack_handler" "$@" < "$sreestack_refs" || :
  exec < "$sreestack_refs"
  rm -f "$sreestack_refs"
fi
# END SreeStack host sync"""


class SetupError(Exception):
    pass


@dataclass(frozen=True)
class Host:
    skills: Path
    instructions: Path
    exclude: frozenset


@dataclass(frozen=True)
class Change:
    action: str
    path: Path
    target: Path | None = None


@dataclass
class Plan:
    changes: list
    conflicts: list


def skill_names() -> list:
    return sorted(path.name for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())


def home_path(home: Path, manifest: Path, key: str, value) -> Path:
    if not isinstance(value, str) or not value:
        raise SetupError(f"{manifest}: {key} must be a non-empty path relative to home")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise SetupError(f"{manifest}: {key} must stay inside home: {value!r}")
    return home / relative


def load_hosts(home: Path) -> list:
    known = set(skill_names())
    hosts = []
    for manifest in sorted(ROOT.glob("*/setup.json")):
        label = manifest.relative_to(ROOT)
        try:
            data = json.loads(manifest.read_text())
        except json.JSONDecodeError as error:
            raise SetupError(f"{label}: invalid JSON: {error}") from error
        if not isinstance(data, dict):
            raise SetupError(f"{label}: expected a JSON object")
        unknown_keys = set(data) - MANIFEST_KEYS
        if unknown_keys:
            raise SetupError(f"{label}: unknown keys: {', '.join(sorted(unknown_keys))}")
        exclude = data.get("exclude", [])
        if not isinstance(exclude, list) or not all(isinstance(name, str) for name in exclude):
            raise SetupError(f"{label}: exclude must be a list of skill names")
        unknown_skills = set(exclude) - known
        if unknown_skills:
            raise SetupError(f"{label}: unknown skills in exclude: {', '.join(sorted(unknown_skills))}")
        hosts.append(Host(
            skills=home_path(home, label, "skills", data.get("skills")),
            instructions=home_path(home, label, "instructions", data.get("instructions")),
            exclude=frozenset(exclude),
        ))
    for key in ("skills", "instructions"):
        paths = [getattr(host, key) for host in hosts]
        if len(paths) != len(set(paths)):
            raise SetupError(f"hosts share a {key} path; give each host its own destination")
    if not hosts:
        raise SetupError("no */setup.json host manifests found")
    return hosts


def resolves_to(path: Path, target: Path) -> bool:
    return os.path.realpath(path) == os.path.realpath(target)


def owned_skill_link(entry: Path) -> bool:
    """A link is ours only when it resolves to a direct child of this checkout's skills/."""
    return entry.is_symlink() and Path(os.path.realpath(entry)).parent == Path(os.path.realpath(SKILLS))


def plan_skills(host: Host, names: list, plan: Plan) -> None:
    wanted = {name: SKILLS / name for name in names if name not in host.exclude}
    directory = host.skills
    existing = {}
    if directory.is_symlink():
        if not resolves_to(directory, SKILLS):
            plan.conflicts.append(
                f"{directory}: symlink to {os.readlink(directory)} is not this checkout's skills/; "
                "move it aside to let SreeStack manage it"
            )
            return
        plan.changes.append(Change("replace-root-link", directory, SKILLS))
    elif directory.exists() and not directory.is_dir():
        plan.conflicts.append(f"{directory}: expected a directory")
        return
    elif not directory.exists():
        plan.changes.append(Change("create-dir", directory))
    else:
        existing = {entry.name: Path(entry.path) for entry in os.scandir(directory)}

    for name, entry in sorted(existing.items()):
        target = wanted.pop(name, None)
        if not owned_skill_link(entry):
            if target:
                plan.conflicts.append(
                    f"{entry}: already exists and is not a SreeStack skill link; move it aside to link {name}"
                )
        elif not target:
            plan.changes.append(Change("remove", entry))
        elif os.readlink(entry) != str(target):
            plan.changes.append(Change("relink", entry, target))
    for name, target in sorted(wanted.items()):
        plan.changes.append(Change("link", directory / name, target))


def plan_instructions(host: Host, plan: Plan) -> None:
    path = host.instructions
    if not os.path.lexists(path):
        plan.changes.append(Change("link", path, INSTRUCTIONS))
    elif resolves_to(path, INSTRUCTIONS):
        return
    elif path.is_file() and path.read_bytes() == INSTRUCTIONS.read_bytes():
        plan.changes.append(Change("backup-and-link", path, INSTRUCTIONS))
    else:
        plan.conflicts.append(
            f"{path}: differs from global/AGENTS.md; merge its guidance there or move it aside"
        )


def make_plan(home: Path) -> Plan:
    hosts = load_hosts(home)
    names = skill_names()
    plan = Plan([], [])
    for host in hosts:
        plan_skills(host, names, plan)
        plan_instructions(host, plan)
    return plan


def replace_with_link(path: Path, target: Path) -> None:
    """Atomically point path at target through a temporary name this call creates."""
    while True:
        temporary = path.with_name(f".{path.name}.sreestack-{secrets.token_hex(6)}")
        try:
            os.symlink(target, temporary)
            break
        except FileExistsError:
            continue
    try:
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink()
        raise


def back_up(path: Path) -> Path:
    """Keep a copy of path under a new backup name without replacing anything."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for suffix in itertools.count():
        backup = path.with_name(f"{path.name}.backup-{stamp}" + (f"-{suffix}" if suffix else ""))
        try:
            if path.is_symlink():
                os.symlink(os.readlink(path), backup)
            else:
                os.link(path, backup)
            return backup
        except FileExistsError:
            continue


def apply(change: Change) -> str:
    path, target = change.path, change.target
    if change.action == "create-dir":
        path.mkdir(parents=True)
        return f"created {path}"
    if change.action == "replace-root-link":
        path.unlink()
        path.mkdir()
        return f"replaced {path} -> {target} with a directory of skill links"
    if change.action == "remove":
        path.unlink()
        return f"removed stale {path}"
    if change.action == "relink":
        replace_with_link(path, target)
        return f"relinked {path} -> {target}"
    if change.action == "backup-and-link":
        backup = back_up(path)
        replace_with_link(path, target)
        return f"backed up {path} as {backup.name} and linked it -> {target}"
    if change.action == "link":
        path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, path)
        return f"linked {path} -> {target}"
    raise ValueError(f"unknown change action: {change.action}")


def describe(change: Change) -> str:
    if change.target is None:
        return f"would {change.action} {change.path}"
    return f"would {change.action} {change.path} -> {change.target}"


def git(*args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def git_dirs() -> tuple | None:
    """Return (git dir, common dir) of this checkout, or None outside Git."""
    output = git("rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir")
    return tuple(output.splitlines()) if output else None


def checkouts() -> list:
    """Return every checkout of this repository, starting with the primary one."""
    listing = git("worktree", "list", "--porcelain", "-z")
    if listing is None:
        raise SetupError(f"could not list the checkouts of {ROOT}")
    return [Path(field[len("worktree "):]) for field in listing.split("\0")
            if field.startswith("worktree ")]


def require_primary() -> Path:
    dirs = git_dirs()
    if dirs is None:
        raise SetupError(f"{ROOT} is not a Git checkout; sync from your stable clone")
    git_dir, common_dir = dirs
    if git_dir != common_dir:
        raise SetupError(
            f"{ROOT} is a linked worktree; sync from your stable clone so links "
            "never point at temporary checkouts"
        )
    return Path(common_dir)


def require_stable_main() -> Path:
    common = require_primary()
    if git("symbolic-ref", "-q", "HEAD") != MAIN_BRANCH:
        raise SetupError(f"{ROOT} does not have main checked out; switch it back to main to sync")
    return common


def locked():
    """Serialize syncs from this repository, including concurrent Git hooks."""
    dirs = git_dirs()
    directory = Path(dirs[1]) if dirs else Path(tempfile.gettempdir())
    handle = open(directory / "sreestack-sync.lock", "w")
    fcntl.flock(handle, fcntl.LOCK_EX)
    return handle


def sync(home: Path, check: bool, quiet: bool = False) -> int:
    with locked():
        common = require_stable_main()
        if not check:
            hooks = common / "hooks"
            if (hooks / HANDLER_NAME).exists():
                install_handler(hooks)
        plan = make_plan(home)
        # Settings go first so sync creates a missing host folder with private modes.
        settings, refused = host_settings.merge_all(ROOT, home, checkouts(), check)
        plan.conflicts = refused + plan.conflicts
        for change in settings:
            print(change)
        if check:
            for change in plan.changes:
                print(describe(change))
        else:
            for change in plan.changes:
                try:
                    print(apply(change))
                except OSError as error:
                    plan.conflicts.append(f"{change.path}: could not {change.action}: {error}")
    for conflict in plan.conflicts:
        print(f"conflict: {conflict}", file=sys.stderr)
    pending = settings or plan.changes
    if plan.conflicts or (check and pending):
        return 1
    if not pending and not quiet:
        print(f"Host setup in {home} is up to date.")
    return 0


def run_hook() -> int:
    home = git("config", "--get", "sreestack.home")
    if not home:
        raise SetupError("sreestack.home is unset; rerun scripts/sync_hosts.py --install-hooks")
    return sync(Path(home), check=False, quiet=True)


def install_handler(hooks: Path) -> Path:
    handler = hooks / HANDLER_NAME
    if os.path.lexists(handler) and (
        handler.is_symlink() or not handler.read_text().startswith(f"#!/bin/sh\n{HANDLER_MARKER}")
    ):
        raise SetupError(f"{handler} already exists and was not installed by SreeStack; move it aside")
    if handler.is_file() and handler.read_text() == HANDLER_SCRIPT and os.access(handler, os.X_OK):
        return handler
    hooks.mkdir(exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=hooks, prefix=f".{HANDLER_NAME}.")
    try:
        with os.fdopen(descriptor, "w") as file:
            file.write(HANDLER_SCRIPT)
        os.chmod(temporary, 0o755)
        os.replace(temporary, handler)
    except BaseException:
        os.unlink(temporary)
        raise
    return handler


def hook_runs_handler(hook: Path, handler: Path) -> bool:
    if hook.is_symlink() and resolves_to(hook, handler):
        return hook.is_file() and os.access(hook, os.X_OK)
    if not hook.is_file() or not os.access(hook, os.X_OK):
        return False
    before, marker, _ = hook.read_text(errors="replace").partition(CHAIN_SCRIPT)
    return bool(marker) and all(not line.strip() or line.lstrip().startswith("#")
                                for line in before.splitlines())


def check_hooks(home: Path) -> int:
    hooks = require_stable_main() / "hooks"
    handler = hooks / HANDLER_NAME
    hooks_path = git("config", "--get", "core.hooksPath")
    hook = (ROOT / Path(hooks_path).expanduser() if hooks_path else hooks) / HOOK_EVENT
    problems = []
    if (handler.is_symlink() or not handler.is_file()
            or handler.read_text(errors="replace") != HANDLER_SCRIPT
            or not os.access(handler, os.X_OK)):
        problems.append("host-sync handler is missing, stale, or not executable")
    if not hook_runs_handler(hook, handler):
        problems.append(f"{hook} does not start with the SreeStack integration")
    if git("config", "--get", "sreestack.home") != str(home):
        problems.append("sreestack.home does not match the requested home")
    for problem in problems:
        print(f"sreestack: {problem}; rerun --install-hooks from {ROOT}", file=sys.stderr)
    if not problems:
        print(f"Host sync hook in {ROOT} is up to date.")
    return int(bool(problems))


def install_hooks(home: Path) -> int:
    hooks = require_stable_main() / "hooks"
    handler = install_handler(hooks)
    subprocess.run(["git", "config", "--local", "sreestack.home", str(home)], cwd=ROOT, check=True)
    hooks_path = git("config", "--get", "core.hooksPath")
    hook = (ROOT / Path(hooks_path).expanduser() if hooks_path else hooks) / HOOK_EVENT
    if not hooks_path and not os.path.lexists(hook):
        os.symlink(HANDLER_NAME, hook)
    if hook_runs_handler(hook, handler):
        print(f"{hook} runs {handler}; it syncs {home} when {ROOT} updates main.")
        return 0
    reason = f"core.hooksPath is {hooks_path}" if hooks_path else f"{hook} already exists"
    print(
        f"sreestack: installed {handler} and set sreestack.home, but {reason}. "
        f"SreeStack will not change your hooks. Add this block to {hook} immediately "
        "after its shebang, before any commands (create it with #!/bin/sh and make it "
        "executable if needed), then rerun --install-hooks to confirm:\n\n"
        f"{CHAIN_SCRIPT}\n",
        file=sys.stderr,
    )
    return 1


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check-hooks", action="store_true",
        help="check the installed handler, reference hook, and home configuration",
    )
    mode.add_argument(
        "--check", action="store_true",
        help="report needed changes without changing host files; exit 0 only when up to date",
    )
    mode.add_argument(
        "--install-hooks", action="store_true",
        help="install the Git hook that syncs after this checkout updates main",
    )
    mode.add_argument("--hook", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--home", type=Path, default=Path.home(),
        help="home directory to configure (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    home = args.home.expanduser().absolute()
    try:
        if args.check or args.check_hooks:
            dirs = git_dirs()
            if dirs is not None and dirs[0] != dirs[1]:
                primary = checkouts()[0]
                script = primary / "scripts" / "sync_hosts.py"
                if not script.is_file():
                    raise SetupError(f"host sync is not available in stable clone {primary}")
                venv = primary / VENV_PYTHON
                python = str(venv) if os.access(venv, os.X_OK) else sys.executable
                print(f"Checking stable clone {primary}", flush=True)
                return subprocess.run(
                    [python, str(script), "--home", str(home),
                     "--check-hooks" if args.check_hooks else "--check"], cwd=primary,
                ).returncode
        if args.check_hooks:
            return check_hooks(home)
        if args.hook:
            return run_hook()
        if args.install_hooks:
            return install_hooks(home)
        return sync(home, args.check)
    except SetupError as error:
        print(f"sreestack: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
