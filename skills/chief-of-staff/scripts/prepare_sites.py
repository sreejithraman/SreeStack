#!/usr/bin/env python3
"""Prepare a rendered command center and live refresh assets for a static Site."""

import argparse
import hashlib
import json
from pathlib import Path


REFRESH = Path(__file__).resolve().parents[1] / "assets" / "chief-refresh.js"


def prepare(page_file: Path, output: Path) -> str:
    page = page_file.read_text(encoding="utf-8")
    if "</head>" not in page or "</body>" not in page or 'name="chief-version"' in page:
        raise ValueError("--page must be the renderer's HTML, before Sites preparation")
    script = REFRESH.read_bytes()
    version = hashlib.sha256(page.encode("utf-8") + b"\0" + script).hexdigest()
    page = page.replace("</head>", f'<meta name="chief-version" content="{version}">\n</head>', 1)
    page = page.replace("</body>", f'<script defer src="./chief-refresh.js?v={version}"></script>\n</body>', 1)
    output.mkdir(parents=True, exist_ok=True)
    if page_file.resolve() in {output.resolve() / name for name in ("index.html", "chief-refresh.js", "chief-version.json")}:
        raise ValueError("--output must not overwrite the rendered input page")
    (output / "index.html").write_text(page, encoding="utf-8")
    (output / "chief-refresh.js").write_bytes(script)
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
