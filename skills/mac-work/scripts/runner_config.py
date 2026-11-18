"""One explicit root, immutable versions and verified activation."""

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

import runtime_inventory

BUNDLE = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = Path.home() / 'Library/Application Support/mac-work'
POLICY = {'capacities': {'heavy': 1}, 'ownership_contract': 'process-group', 'schema': 1}
ADAPTIVE_CAPACITY = 2


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def activation_lock(root, exclusive=False):
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (root / 'activation.lock').open('a') as lock:
        try:
            fcntl.flock(lock, (fcntl.LOCK_EX | fcntl.LOCK_NB) if exclusive else fcntl.LOCK_SH)
        except BlockingIOError:
            raise ValueError('Activation refused: a consumer/worker is active; retry when idle') from None
        yield


def validate_config(path, expected_sha=None):
    value = json.loads(path.read_text())
    if expected_sha is not None and digest(path) != expected_sha:
        raise ValueError('Configuration hash mismatch')
    version = path.parent
    root = Path(value['root'])
    if value['schema'] != 1 or version.parent != root / 'versions' or path.name != 'config.json':
        raise ValueError('Invalid configuration schema/path')
    if value['policy'] != POLICY or Path(value['state']) != root / 'state':
        raise ValueError('Canonical policy/state mismatch; heavy=1 and process-group are fixed')
    if type(value.get('adaptive_capacity', False)) is not bool:
        raise ValueError('Adaptive capacity flag must be a boolean')
    if Path(value['runtime']) != version / 'build/runtime':
        raise ValueError('Runtime path mismatch')
    manifest = version / 'bundle-manifest.json'
    if digest(manifest) != value['bundle_sha256']:
        raise ValueError('Bundle manifest hash mismatch')
    expected_files = json.loads(manifest.read_text())
    bundle = version / 'bundle'
    runtime_inventory.verify_bundle(bundle, expected_files)
    from build_runtime import verify_runtime
    verify_runtime(Path(value['runtime']), value['build_receipt_sha256'])
    if digest(Path(value['runtime']) / 'bin/python') != value['python_sha256']:
        raise ValueError('Runtime interpreter hash mismatch')
    value['_path'] = str(path)
    value['_sha256'] = digest(path)
    return value


def load(pointer):
    pointer = pointer.resolve()
    selected = json.loads(pointer.read_text())
    if selected['schema'] != 1:
        raise ValueError('Unsupported active configuration schema')
    config = validate_config(Path(selected['configuration']), selected['sha256'])
    if pointer != Path(config['root']) / 'current.json':
        raise ValueError('Active configuration must be root/current.json')
    return config


def require_active(config):
    pointer = json.loads((Path(config['root']) / 'current.json').read_text())
    if pointer.get('configuration') != config['_path'] or pointer.get('sha256') != config['_sha256']:
        raise ValueError('Active release changed; restart this MCP consumer')
    validate_config(Path(config['_path']), config['_sha256'])


def idle(root):
    database = root / 'state/queue.db'
    if not database.exists():
        if (root / 'current.json').exists():
            raise ValueError('Shared admission database missing; restore state, never reinitialize an active root')
        return
    with sqlite3.connect(database) as conn:
        row = conn.execute('SELECT COUNT(*) FROM queue').fetchone()
        if row[0]:
            raise ValueError('Activation refused: queued, running or unresolved admission remains')
        policy = conn.execute('SELECT policy_json FROM admission_policy WHERE singleton=1').fetchone()
        if policy and json.loads(policy[0]) != POLICY:
            raise ValueError('Existing admission policy differs; no uncontained-state migration is supported')


def setup_files(root):
    providers = root / 'providers'
    providers.mkdir(mode=0o700, exist_ok=True)
    command = str(root / 'bin/mac-work')
    write_json(providers / 'claude.mcp.json', {'mcpServers': {'mac_work': {
        'type': 'stdio', 'command': command, 'args': ['mcp']}}})
    (providers / 'codex.toml').write_text('[mcp_servers.mac_work]\ncommand = ' + json.dumps(command) + '\nargs = ["mcp"]\n')


def release_directory(root, release):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', release):
        raise ValueError('Invalid release name')
    return root / 'versions' / release


def activate(root, release):
    path = release_directory(root, release) / 'config.json'
    with activation_lock(root, True):
        idle(root)
        config = validate_config(path)
        if Path(config['root']) != root:
            raise ValueError('Activation root mismatch')
        launcher = root / 'bin/mac-work'
        launcher.parent.mkdir(mode=0o700, exist_ok=True)
        source = Path(config['_path']).parent / 'bundle/scripts/runner_bootstrap.py'
        if launcher.exists() and digest(launcher) != digest(source):
            raise ValueError('Existing launcher differs; bootstrap protocol migration is not supported')
        if not launcher.exists():
            shutil.copyfile(source, launcher)
            launcher.chmod(0o700)
        state = root / 'state'
        state.mkdir(mode=0o700, exist_ok=True)
        initialize = """from pathlib import Path
from queue_core import QueuePaths,init_db
import sys
paths=QueuePaths.from_data_dir(Path(sys.argv[1]))
init_db(paths,{'heavy':1},'process-group')
"""
        subprocess.run([str(Path(config['runtime']) / 'bin/python'), '-I', '-B', '-c', initialize, str(state)], check=True)
        write_json(root / 'current.json', {'schema': 1, 'configuration': str(path), 'sha256': digest(path)})
        setup_files(root)
    return {'release': release, 'config': str(root / 'current.json'), 'command': str(root / 'bin/mac-work')}


def install(root, release, archive=None, *, adaptive_capacity=False):
    root = root.resolve()
    version = release_directory(root, release)
    with activation_lock(root, True):
        idle(root)
        version.mkdir(mode=0o700, parents=True, exist_ok=False)
    bundle = version / 'bundle'
    shutil.copytree(BUNDLE, bundle, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    runtime_inventory.seal_bundle(bundle)
    hashes = {str(p.relative_to(bundle)): digest(p) for p in bundle.rglob('*') if p.is_file()}
    write_json(version / 'bundle-manifest.json', hashes)
    subprocess.run([sys.executable, '-I', '-B', str(bundle / 'scripts/build_runtime.py'), 'build',
                    '--root', str(version / 'build'), *(['--archive', str(archive.resolve())] if archive else [])],
                   check=True, stdout=sys.stderr)
    config = {'schema': 1, 'root': str(root), 'release': release, 'state': str(root / 'state'),
              'runtime': str(version / 'build/runtime'), 'policy': POLICY,
              'bundle_sha256': digest(version / 'bundle-manifest.json'),
              'launcher_sha256': digest(bundle / 'scripts/runner_bootstrap.py'),
              'python_sha256': digest(version / 'build/runtime/bin/python'),
              'build_receipt_sha256': digest(version / 'build/build-receipt.json')}
    if adaptive_capacity:
        config['adaptive_capacity'] = True
    write_json(version / 'config.json', config)
    return activate(root, release)
