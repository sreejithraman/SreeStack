"""Merge the public host settings templates into private host configs.

Templates own their leaf keys; every other local key stays local. Nothing flows
back into the repository. A host can still write a config between the final
check and the rename, so each replacement keeps a backup of what it replaced.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from decimal import Decimal
import errno
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

try:
    import tomlkit
except ImportError:
    tomlkit = None

TEMPLATES = (
    ("claude/settings.json", ".claude/settings.json"),
    ("codex/config.toml", ".codex/config.toml"),
    ("codex/config.toml", ".codex-t3/config.toml"),
)
SETUP = "python3 -m venv --clear .venv && .venv/bin/python -m pip install -r scripts/requirements-sync.txt"


class SettingsError(Exception):
    """A refusal; its message names files and managed keys, never config values."""


class WriteStopped(Exception):
    """A write that could not finish; its message is the complete reason."""


def parse_json(text: str) -> dict:
    def unique_keys(pairs):
        if len({key for key, _ in pairs}) != len(pairs):
            raise SettingsError("an object repeats a key")
        return dict(pairs)

    def exact_float(number: str) -> float:
        value = float(number)
        if Decimal(number) != Decimal(repr(value)):
            raise SettingsError("a number would change if rewritten")
        return value

    try:
        document = json.loads(text, object_pairs_hook=unique_keys, parse_float=exact_float)
    except json.JSONDecodeError as error:
        raise SettingsError(f"invalid JSON at line {error.lineno} column {error.colno}") from None
    if not isinstance(document, dict):
        raise SettingsError("expected a JSON object at the top level")
    dump_json(document)  # json.loads accepts NaN and Infinity; this refuses them.
    return document


def dump_json(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def parse_toml(text: str):
    try:
        return tomlkit.parse(text)
    except tomlkit.exceptions.ParseError as error:
        raise SettingsError(f"invalid TOML at line {error.line} column {error.col}") from None


def syntax(path: Path) -> tuple:
    """Return the (parser, serializer, empty document) for a known config file."""
    if path.suffix == ".json":
        return parse_json, dump_json, "{}"
    return parse_toml, tomlkit.dumps, ""


def plain(value):
    return value.unwrap() if hasattr(value, "unwrap") else value


def canonical(value) -> str:
    """Compare by content and kind, so 1, 1.0, and true stay distinct."""
    return json.dumps(plain(value), sort_keys=True, default=repr)


def leaves(table: Mapping, prefix: tuple = ()) -> list:
    found = []
    for key, value in table.items():
        if isinstance(value, Mapping):
            found.extend(leaves(value, (*prefix, key)))
        else:
            found.append(((*prefix, key), value))
    return found


def merge(document: Mapping, managed: list) -> list:
    """Set each managed leaf in document and return the dotted keys that changed."""
    changed = []
    for path, value in managed:
        name = ".".join(path)
        table = document
        for depth, key in enumerate(path[:-1], start=1):
            if key not in table:
                table[key] = {}
            table = table[key]
            if not isinstance(table, Mapping):
                raise SettingsError(f"{'.'.join(path[:depth])} must be a table to hold {name}")
        key = path[-1]
        if key in table:
            if canonical(table[key]) == canonical(value):
                continue
            if isinstance(table[key], (Mapping, list)):
                raise SettingsError(f"{name} is a table or list locally, but the template sets a value")
        table[key] = value
        changed.append(name)
    return changed


def read_regular(path: Path) -> bytes | None:
    """Return a private config's bytes, or None when absent, without following links."""
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise SettingsError("is a symlink; keep it as a regular private file") from None
        raise
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise SettingsError("is not a regular file")
        if info.st_nlink != 1:
            raise SettingsError("has another hard link; keep it as a single private file")
        with os.fdopen(descriptor, "rb", closefd=False) as file:
            return file.read()
    finally:
        os.close(descriptor)


def observe(path: Path) -> tuple:
    """Return the identity of path's folder, or None, and path's bytes, or None."""
    try:
        folder = os.lstat(path.parent)
    except FileNotFoundError:
        return None, None
    if not stat.S_ISDIR(folder.st_mode):
        raise SettingsError("its folder is a symlink or not a folder; keep it as a real folder")
    return (folder.st_dev, folder.st_ino), read_regular(path)


def file_ids(paths: list) -> set:
    infos = (os.stat(path) for path in paths if os.path.exists(path))
    return {(info.st_dev, info.st_ino) for info in infos}


def write_private(folder: Path, prefix: str, content: bytes, mode: int = 0o600) -> Path:
    descriptor, name = tempfile.mkstemp(dir=folder, prefix=prefix)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(content)
            file.flush()
            os.fchmod(file.fileno(), mode)
            os.fsync(file.fileno())
    except BaseException:
        os.unlink(name)
        raise
    return Path(name)


def require_unchanged(path: Path, original: bytes | None, expected_folder: tuple | None) -> tuple | None:
    folder, current = observe(path)
    if current != original or expected_folder not in (None, folder):
        raise SettingsError("changed since sync read it; left unchanged, rerun sync")
    return folder


def write_config(path: Path, expected_folder: tuple | None, original: bytes | None,
                 content: bytes, keys: str) -> str:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    folder = require_unchanged(path, original, expected_folder)
    backup, mode = None, 0o600
    if original is not None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = write_private(path.parent, f"{path.name}.backup-{stamp}-", original)
        mode = stat.S_IMODE(os.lstat(path).st_mode)
    temporary = write_private(path.parent, f".{path.name}.sreestack-", content, mode)
    try:
        require_unchanged(path, original, folder)
        if backup:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)  # unlike a rename, never replaces a late file
    except FileExistsError:
        raise SettingsError("appeared since sync read it; left unchanged, rerun sync") from None
    finally:
        if os.path.lexists(temporary):
            temporary.unlink()
    if backup is None:
        return f"created {path} with managed settings: {keys}"
    return f"updated managed settings in {path}: {keys}; backed up the previous file as {backup.name}"


def merge_file(template: Path, path: Path, checkouts: set, check: bool) -> str | None:
    """Merge one config, or describe the merge, and return what changed, if anything."""
    parse, dump, empty = syntax(path)
    try:
        managed = leaves(plain(parse(template.read_text(encoding="utf-8"))))
    except Exception:
        raise SettingsError(f"template {template} is unreadable or invalid") from None
    real = Path(os.path.realpath(path.parent))
    if file_ids([real, *real.parents]) & checkouts:
        raise SettingsError("resolves inside a checkout; keep host configs private")
    folder, original = observe(path)
    text = empty if original is None else original.decode("utf-8")
    document = parse(text)
    changed = merge(document, managed)
    if not changed:
        return None
    expected = plain(parse(text))
    merge(expected, managed)
    content = dump(document)
    if canonical(parse(content)) != canonical(expected):
        raise SettingsError("merging would not keep the expected values")
    keys = ", ".join(changed)
    action = "create settings" if original is None else "update settings"
    if check:
        return f"would {action} in {path}: {keys}"
    try:
        return write_config(path, folder, original, content.encode("utf-8"), keys)
    except SettingsError as error:
        raise WriteStopped(error) from None
    except OSError as error:
        raise WriteStopped(f"could not {action}: {error}") from None


def merge_all(root: Path, home: Path, checkouts: list, check: bool) -> tuple:
    """Merge each known template and return what changed and which configs stopped it."""
    if tomlkit is None:
        return [], [f"tomlkit is not available to {sys.executable}, so host settings were not "
                    f"merged. In {root} run: {SETUP}. Then use .venv/bin/python scripts/sync_hosts.py"]
    changes, conflicts = [], []
    checkout_ids = file_ids(checkouts)
    for template, relative in TEMPLATES:
        path = home / relative
        try:
            change = merge_file(root / template, path, checkout_ids, check)
        except WriteStopped as error:
            conflicts.append(f"{path}: {error}")
        except SettingsError as error:
            conflicts.append(f"{path}: {error}; left unchanged")
        # Parsers can raise many types and may quote private content, so report none of it.
        except Exception:
            conflicts.append(f"{path}: could not merge managed settings into it; left unchanged")
        else:
            if change:
                changes.append(change)
    return changes, conflicts
