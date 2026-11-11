#!/usr/bin/env python3
"""Prepare a rendered command center and live refresh assets for a static Site."""

import argparse
import hashlib
import json
from pathlib import Path
import re


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


def prepare(page_file: Path, output: Path) -> str:
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
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", required=True, type=Path, help="Already rendered HTML selected for publication")
    parser.add_argument("--output", required=True, type=Path, help="Static output directory in the durable Site source, normally dist")
    args = parser.parse_args()
    try:
        print(prepare(args.page, args.output))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
