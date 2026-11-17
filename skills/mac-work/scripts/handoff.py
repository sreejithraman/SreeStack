"""Receipt-gated artifact evidence; allocation stays with the project/host."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time

from runner import paths, status

MAX_ENTRIES = 10000
MAX_BYTES = 2 * 1024**3
MAX_SECONDS = 30


def artifacts(names):
    if not names or len(set(names)) != len(names):
        raise ValueError('Distinct absolute artifact paths are required')
    deadline = time.monotonic() + MAX_SECONDS
    total = count = 0
    result = []
    for name in sorted(names):
        root = Path(name)
        if not root.is_absolute() or root.is_symlink() or not root.exists():
            raise ValueError('Artifact must exist at an absolute, nonsymlink root')
        root = root.resolve()
        nodes = [root]
        entries = []
        while nodes:
            path = nodes.pop()
            before = path.lstat()
            count += 1
            if count > MAX_ENTRIES or time.monotonic() > deadline:
                raise ValueError('Artifact inspection budget exceeded (10000 entries / 30 seconds)')
            entry = {'name': str(path.relative_to(root)), 'mode': stat.S_IMODE(before.st_mode)}
            if stat.S_ISLNK(before.st_mode):
                if not path.resolve().is_relative_to(root):
                    raise ValueError('Artifact symlink escapes its root')
                entry.update(kind='symlink', target=os.readlink(path))
            elif stat.S_ISDIR(before.st_mode):
                entry.update(kind='directory')
                nodes.extend(sorted(path.iterdir(), reverse=True))
            elif stat.S_ISREG(before.st_mode):
                total += before.st_size
                if total > MAX_BYTES:
                    raise ValueError('Artifact inspection budget exceeded (2 GiB)')
                digest = hashlib.sha256()
                with path.open('rb') as stream:
                    while chunk := stream.read(1024 * 1024):
                        digest.update(chunk)
                        if time.monotonic() > deadline:
                            raise ValueError('Artifact inspection budget exceeded (30 seconds)')
                entry.update(kind='file', size=before.st_size, sha256=digest.hexdigest())
            else:
                raise ValueError('Artifacts must contain only files, directories and internal symlinks')
            after = path.lstat()
            if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_mode) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode):
                raise ValueError('Artifact changed during inspection')
            entries.append(entry)
        result.append({'path': str(root), 'entries': sorted(entries, key=lambda e: e['name'])})
    return result


def producer(receipt):
    if receipt['status'] != 'success' or receipt.get('exit_code') != 0 or receipt['capacity_held']:
        raise ValueError('Handoff requires a successful, closed build; inspect status/log before acquiring')
    if receipt['lifecycle']['state'] != 'closed':
        raise ValueError('Build closure is unresolved')
    return {k: receipt[k] for k in ('operation_id', 'task_id', 'request', 'configuration_sha256', 'receipt_path', 'log_path')}


def path_for(config, operation_id):
    return paths(config, operation_id)[0].with_name('handoff.json')


def seal(config, operation_id, names):
    receipt = status(config, operation_id)
    source = producer(receipt)
    current = subprocess.check_output(['git', '-C', source['request']['worktree'], 'rev-parse', 'HEAD'], text=True).strip()
    if current != source['request']['revision']:
        raise ValueError('Build worktree revision changed; do not acquire a device for stale artifacts')
    value = {'schema': 1, 'producer': source, 'artifacts': artifacts(names)}
    path = path_for(config, operation_id)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.handoff-')
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(value, stream, sort_keys=True, indent=2); stream.write('\n')
            stream.flush(); os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if json.loads(path.read_text()) != value:
                raise ValueError('Handoff conflict: existing artifact evidence is immutable') from None
    finally:
        os.unlink(temporary)
    return {**value, 'manifest_path': str(path), 'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def bind(config, spec, receipt):
    source = producer(receipt)
    operation_id = source['operation_id']
    path = path_for(config, operation_id)
    value = json.loads(path.read_text())
    if value['schema'] != 1 or value['producer'] != source:
        raise ValueError('Handoff producer mismatch')
    if any(spec[key] != source['request'][key] for key in ('worktree', 'revision')):
        raise ValueError('Handoff requires the same worktree/revision as its build')
    return {**spec, 'handoff': {'operation_id': operation_id, 'manifest_path': str(path),
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}}


def verify(config, spec):
    evidence = spec['handoff']
    path = path_for(config, evidence['operation_id'])
    if str(path) != evidence['manifest_path'] or hashlib.sha256(path.read_bytes()).hexdigest() != evidence['sha256']:
        raise ValueError('Handoff manifest hash mismatch')
    value = json.loads(path.read_text())
    if artifacts([a['path'] for a in value['artifacts']]) != value['artifacts']:
        raise ValueError('Handoff artifact drift; device-dependent command did not launch')
