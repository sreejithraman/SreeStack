#!/usr/bin/env python3
"""Run the repository checks with pinned dependencies from any worktree.

The first run for a set of requirements builds a virtual environment in the
clone's shared Git directory. Later runs in every worktree only read it, so they
need no network and work in sandboxes that can write only to the worktree.
Requirements name each environment and a finished build moves into place in one
step, so branches with different pins and concurrent first runs cannot interfere.

With arguments, run them with the environment's Python instead of the checks.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "scripts/requirements-checks.txt"
CHECKS = (
    ("-m", "unittest", "discover", "-s", "scripts", "-p", "test_*.py"),
    ("-m", "unittest", "discover", "-s", "skills/chief-of-staff/scripts", "-p", "test_*.py"),
    ("scripts/check_skills.py",),
    ("scripts/check_whitespace.py",),
)


def environment_path() -> Path:
    git_directory = subprocess.check_output(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT, text=True,
    ).strip()
    digest = hashlib.sha256()
    for requirements in sorted(REQUIREMENTS.parent.glob("requirements-*.txt")):
        digest.update(requirements.read_bytes())
    return Path(git_directory) / "sreestack-check-env" / digest.hexdigest()[:16]


def build(environment: Path) -> None:
    print(f"Building the check environment at {environment}", file=sys.stderr, flush=True)
    environment.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(environment, ignore_errors=True)  # Its interpreter is gone.
    with tempfile.TemporaryDirectory(dir=environment.parent, prefix=".build-") as directory:
        draft = Path(directory) / "environment"
        subprocess.run([sys.executable, "-m", "venv", str(draft)], check=True)
        subprocess.run(
            [str(draft / "bin/python"), "-m", "pip", "install", "--quiet",
             "--disable-pip-version-check", "-r", str(REQUIREMENTS)],
            check=True,
        )
        try:
            draft.rename(environment)
        except OSError:
            if not environment.is_dir():  # A concurrent first run may have finished first.
                raise


def checks_python() -> str:
    environment = environment_path()
    python = environment / "bin/python"
    if not python.exists():
        try:
            build(environment)
        except (OSError, subprocess.CalledProcessError) as error:
            sys.exit(f"Could not build {environment}: {error}\n"
                     "The first run with these requirements needs network access and write "
                     "access to the Git directory. In a sandbox, rerun with those permissions.")
    return str(python)


def main() -> int:
    python = checks_python()
    if len(sys.argv) > 1:
        return subprocess.run([python, *sys.argv[1:]]).returncode
    failed = [check for check in CHECKS if subprocess.run([python, *check], cwd=ROOT).returncode]
    for check in failed:
        print(f"Failed: {' '.join(check)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
