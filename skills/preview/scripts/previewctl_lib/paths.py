from __future__ import annotations

import os
import sys
from pathlib import Path


def state_root(env: dict[str, str] | None = None, platform: str | None = None) -> Path:
    values = os.environ if env is None else env
    override = values.get("PREVIEWCTL_STATE_DIR")
    if override:
        return Path(override).expanduser().resolve(strict=False)

    home = Path(values.get("HOME", str(Path.home()))).expanduser()
    current_platform = sys.platform if platform is None else platform
    if current_platform == "darwin":
        return home / "Library" / "Application Support" / "previewctl"

    xdg = values.get("XDG_STATE_HOME")
    return (Path(xdg).expanduser() if xdg else home / ".local" / "state") / "previewctl"


def preview_directory(root: Path, preview_id: str) -> Path:
    return root / "previews" / preview_id
