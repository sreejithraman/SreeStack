"""One sealed file-set owner for the private venv and its private CPython base.

This module uses only the trusted host's standard library (Python >=3.9).
It never executes the candidate interpreter or imports its packages.
"""

import hashlib
import json
import os
from pathlib import Path
import stat

ROOTS = ('python', 'runtime')


def digest(path):
    with path.open('rb') as stream:
        value = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def file_set(build):
    build = build.resolve()
    roots = [build / name for name in ROOTS]
    entries = {}
    pending = list(roots)
    for root in roots:
        if root.is_symlink() or not root.is_dir():
            raise ValueError('Runtime inventory root missing or symlinked: ' + root.name)
    while pending:
        path = pending.pop()
        info = path.lstat()
        name = str(path.relative_to(build))
        item = {'mode': stat.S_IMODE(info.st_mode)}
        if stat.S_ISLNK(info.st_mode):
            destination = path.resolve(strict=True)
            if not any(destination.is_relative_to(root) for root in roots):
                raise ValueError('Runtime symlink escapes private code roots: ' + name)
            item.update(kind='symlink', target=os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):
            item['kind'] = 'directory'
            pending.extend(path.iterdir())
        elif stat.S_ISREG(info.st_mode):
            if info.st_nlink != 1:
                raise ValueError('Runtime file shares an inode; use private copies: ' + name)
            item.update(kind='file', size=info.st_size)
        else:
            raise ValueError('Runtime special file refused: ' + name)
        entries[name] = item
    return entries


def file_digest(path):
    before = path.lstat()
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as stream:
        value = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    after = path.lstat()
    identity = lambda item: (item.st_dev, item.st_ino, item.st_mode, item.st_size, item.st_mtime_ns)
    if identity(before) != identity(after):
        raise ValueError('Runtime changed during inventory: ' + str(path))
    return value.hexdigest()


def seal(build):
    """Only call on task-owned copied roots; never chmod uv/cache hardlinks."""
    entries = file_set(build)
    for name, item in entries.items():
        if item['kind'] == 'file':
            os.chmod(build / name, item['mode'] & ~0o222)
    for name, item in sorted(entries.items(), key=lambda entry: len(Path(entry[0]).parts), reverse=True):
        if item['kind'] == 'directory':
            os.chmod(build / name, item['mode'] & ~0o222)
    return create(build)


def create(build):
    entries = file_set(build)
    for name, item in entries.items():
        if item['mode'] & 0o222 and item['kind'] != 'symlink':
            raise ValueError('Runtime code must be sealed read-only: ' + name)
        if item['kind'] == 'file':
            item['sha256'] = file_digest(build / name)
    return {'schema': 1, 'roots': list(ROOTS), 'entries': entries}


def verify(build, expected_receipt_sha256=None):
    """Check the bound receipt and complete code trees before candidate execution."""
    build = build.resolve()
    receipt_path = build / 'build-receipt.json'
    if expected_receipt_sha256 is not None and digest(receipt_path) != expected_receipt_sha256:
        raise ValueError('Runtime build receipt hash mismatch')
    record = json.loads(receipt_path.read_text())
    if record['schema'] != 2 or Path(record['runtime']) != build / 'runtime':
        raise ValueError('Unsupported build receipt schema/runtime inventory protocol; create a fresh private root')
    manifest = build / 'runtime-manifest.json'
    if digest(manifest) != record['runtime_manifest_sha256']:
        raise ValueError('Runtime inventory hash mismatch')
    expected = json.loads(manifest.read_text())
    if expected['schema'] != 1 or expected['roots'] != list(ROOTS):
        raise ValueError('Unsupported runtime inventory schema')
    actual = file_set(build)
    if set(actual) != set(expected['entries']):
        raise ValueError('Runtime inventory file set mismatch')
    for name, item in actual.items():
        stored = expected['entries'][name]
        shape = {key: value for key, value in stored.items() if key != 'sha256'}
        if item != shape:
            raise ValueError('Runtime inventory file type/mode/link mismatch: ' + name)
    for name, item in actual.items():
        if item['kind'] == 'file' and file_digest(build / name) != expected['entries'][name]['sha256']:
            raise ValueError('Runtime inventory content mismatch: ' + name)
    return record


def verify_bundle(bundle, expected):
    """Verify every bundled import file, including any added cache or startup file."""
    actual = set()
    for path in bundle.rglob('*'):
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Bundle file type/link mismatch: ' + str(path.relative_to(bundle)))
        actual.add(str(path.relative_to(bundle)))
    if actual != set(expected):
        raise ValueError('Bundle file set mismatch')
    for name, value in expected.items():
        if file_digest(bundle / name) != value:
            raise ValueError('Bundle hash mismatch: ' + name)


def seal_bundle(bundle):
    """Keep ordinary Python commands from writing unlisted bundle caches."""
    paths = list(bundle.rglob('*')) + [bundle]
    for path in paths:
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise ValueError('Bundle must contain private regular files/directories')
    for path in sorted(paths, key=lambda value: len(value.parts), reverse=True):
        os.chmod(path, stat.S_IMODE(path.stat().st_mode) & ~0o222)
