"""Run the repository checks with pinned dependencies from any worktree.

The first run for a set of requirements builds a virtual environment in the
clone's shared Git directory. Later runs in every worktree only read it, so they
need no network and work in sandboxes that can write only to the worktree.
Requirements name each environment, so branches with different pins can coexist.
Builds take turns and a finished one moves into place in one step, so a run sees
a whole environment or none.

With arguments, run them with the environment's Python instead of the checks.
"""

import fcntl
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
    ("-m", "unittest", "discover", "-s", "skills/create-image/scripts", "-p", "test_*.py"),
    ("-m", "unittest", "discover", "-s", "skills/simulator-lifecycle/scripts", "-p", "test_*.py"),
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


def usable(environment: Path) -> bool:
    """Importing pip proves the interpreter runs and still sees its site-packages."""
    python = environment / "bin/python"
    return python.exists() and subprocess.run(
        [str(python), "-I", "-c", "import pip"], capture_output=True,
    ).returncode == 0


def build(environment: Path) -> None:
    print(f"Preparing the check environment at {environment}", file=sys.stderr)
    environment.parent.mkdir(exist_ok=True)
    with open(environment.parent / "build.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if usable(environment):  # Another run finished while this one waited.
            return
        with tempfile.TemporaryDirectory(dir=environment.parent, prefix=".build-") as directory:
            draft = Path(directory) / "environment"
            subprocess.run([sys.executable, "-I", "-m", "venv", str(draft)], check=True)
            subprocess.run(
                [str(draft / "bin/python"), "-I", "-m", "pip", "install", "--quiet",
                 "--disable-pip-version-check", "-r", str(REQUIREMENTS)],
                check=True,
            )
            shutil.rmtree(environment, ignore_errors=True)
            draft.rename(environment)


def checks_python() -> str:
    environment = environment_path()
    if not usable(environment):
        try:
            build(environment)
        except (OSError, subprocess.CalledProcessError) as error:
            sys.exit(f"Could not build {environment}: {error}\n"
                     "If that is a network or permission failure, rerun with network access "
                     "and write access to the Git directory.")
    return str(environment / "bin/python")


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
