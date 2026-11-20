#!/usr/bin/env python3
"""Prepare a rendered command center, the result images beside it, and live refresh assets for a static Site."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from render_dashboard import page_files


REFRESH = Path(__file__).resolve().parents[1] / "assets" / "chief-refresh.js"
VIEW_SCOPE = """<script>
(() => {
  const intervals = [];
  const setInterval = (...args) => {
    const timer = window.setInterval(...args);
    intervals.push(timer);
    return timer;
  };
  document.addEventListener('chief:replace', () => {
    saveView();
    intervals.forEach(clearInterval);
  }, {once: true});
%s
})();
</script>"""


def default_output(page_file: Path) -> Path:
    resolved = page_file.expanduser().resolve()
    if resolved.parent.name == "record":
        return resolved.parent.parent / "site" / "dist"
    raise ValueError("--output is required unless --page is inside a program's record/ folder")


def git_root(path: Path) -> Path | None:
    probe = path.expanduser().resolve()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    if not probe.exists():
        return None
    if probe.is_file():
        probe = probe.parent
    result = subprocess.run(
        ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 and result.stdout.strip() else None


def is_record_repo(repo_root: Path) -> bool:
    if (repo_root / "program.json").exists():
        return True
    head = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "-e", "HEAD:program.json"],
        capture_output=True,
    )
    return head.returncode == 0


def prepare(page_file: Path, output: Path | None = None) -> str:
    page_file = page_file.expanduser()
    output = default_output(page_file) if output is None else output.expanduser()
    output_resolved = output.resolve()
    page_repo = git_root(page_file)
    if page_repo is not None and output_resolved.is_relative_to(page_repo):
        raise ValueError(
            f"--output ({output}) must be outside the program record git repo ({page_repo}) "
            "so Codex Sites does not nest .git inside it; use a sibling site/dist directory"
        )
    out_repo = git_root(output)
    if out_repo is not None and is_record_repo(out_repo):
        raise ValueError(
            f"--output ({output}) must be outside the program record git repo ({out_repo}) "
            "so Codex Sites does not nest .git inside it; use a sibling site/dist directory"
        )
    page = page_file.read_text(encoding="utf-8")
    if "</head>" not in page or "</body>" not in page or 'name="chief-version"' in page:
        raise ValueError("--page must be the renderer's HTML, before Sites preparation")
    # document.open() retains window bindings and timers across full replacements.
    page, scripts = re.subn(r"<script>(.*?)</script>", lambda match: VIEW_SCOPE % match[1], page, flags=re.DOTALL)
    if scripts != 1:
        raise ValueError("--page must contain the renderer's single inline view script")
    script = REFRESH.read_text(encoding="utf-8")
    page = page.replace("</body>", f"<script>\n{script}</script>\n</body>", 1)
    version = hashlib.sha256(page.encode("utf-8")).hexdigest()
    page = page.replace("</head>", f'<meta name="chief-version" content="{version}">\n</head>', 1)
    output.mkdir(parents=True, exist_ok=True)
    if page_file.resolve() in {output.resolve() / name for name in ("index.html", "chief-refresh.js", "chief-version.json")}:
        raise ValueError("--output must not overwrite the rendered input page")
    (output / "index.html").write_text(page, encoding="utf-8")
    (output / "chief-refresh.js").unlink(missing_ok=True)
    (output / "chief-version.json").write_text(json.dumps({"version": version}) + "\n", encoding="utf-8")
    for name in page_files(page):
        (output / name).parent.mkdir(exist_ok=True)
        shutil.copyfile(page_file.parent / name, output / name)
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", required=True, type=Path, help="Already rendered HTML selected for publication")
    parser.add_argument("--output", type=Path,
                        help="Static output directory in the sibling Site checkout (defaults to ../site/dist when --page is in record/)")
    args = parser.parse_args()
    try:
        print(prepare(args.page, args.output))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
