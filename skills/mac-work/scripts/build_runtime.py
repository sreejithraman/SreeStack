"""Build a private, hash-verified experimental lifecycle runtime.

This is a dependency qualification recipe, not host activation or a command
launcher. Source, patch and dependency drift fail before queue execution.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import runpy
import types
import subprocess
import sys
import tarfile
import urllib.request

runtime_inventory = types.SimpleNamespace(**runpy.run_path(
    str(Path(__file__).with_name('runtime_inventory.py'))))

BUNDLE = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(archive=None, patch=None):
    candidate = json.loads((BUNDLE / 'candidate.json').read_text())
    if candidate['schema'] != 1:
        raise ValueError('Unsupported candidate schema')
    for name, expected in candidate['inputs'].items():
        actual = patch if name == 'patches/lifecycle.patch' and patch is not None else BUNDLE / name
        if digest(actual) != expected:
            raise ValueError(f'Input hash mismatch: {name}')
    if archive is not None and digest(archive) != candidate['source']['sha256']:
        raise ValueError('Source archive hash mismatch')
    return candidate


def verify_runtime(runtime, expected_receipt_sha256=None):
    candidate = inputs()
    record = runtime_inventory.verify(runtime.parent, expected_receipt_sha256)
    if record['candidate_sha256'] != digest(BUNDLE / 'candidate.json'):
        raise ValueError('Runtime candidate/configuration hash mismatch')
    observed = dict(record['observed'])
    observed.update(candidate_sha256=record['candidate_sha256'], wheel_sha256=record['wheel_sha256'],
                    verified_modules=candidate['repaired_modules'],
                    runtime_manifest_sha256=record['runtime_manifest_sha256'])
    return observed


def probe_built_runtime(runtime, candidate):
    probe = """import importlib.metadata as m, importlib.util as u, json, sys, re
print(json.dumps({'python':sys.version.split()[0], 'package':m.version('agent-task-queue'),
 'versions':{re.sub(r'[-_.]+','-', d.metadata['Name']).lower(): d.version for d in m.distributions()},
 'files':{n:u.find_spec(n).origin for n in ('queue_core','queue_lifecycle','tq','task_queue')},
 'base_prefix':sys.base_prefix, 'prefix':sys.prefix, 'sys_path':sys.path}))"""
    runtime_inventory.verify(runtime.parent)
    result = subprocess.run([str(runtime / 'bin/python'), '-I', '-B', '-c', probe],
                            text=True, capture_output=True, check=True, timeout=10)
    observed = json.loads(result.stdout)
    if (observed['python'], observed['package']) != (candidate['python'], candidate['package_version']):
        raise ValueError('Runtime version mismatch')
    expected = dict(re.findall(r'^([a-z0-9-]+)==(\S+)', (BUNDLE / 'scripts/runtime.lock').read_text(), re.M))
    expected['agent-task-queue'] = candidate['package_version']
    if observed['versions'] != expected:
        raise ValueError('Runtime dependency file/distribution set mismatch')
    roots = [runtime, runtime.parent / 'python']
    if (Path(observed['prefix']) != runtime or Path(observed['base_prefix']) != roots[1]
            or not all(any(Path(name).is_relative_to(root) for root in roots) for name in observed['sys_path'])):
        raise ValueError('Runtime import path escapes private code roots')
    for name, path in observed['files'].items():
        if digest(Path(path)) != candidate['repaired_modules'][name + '.py']:
            raise ValueError(f'Repaired source hash mismatch: {name}')
    return observed


def run(argv, **kwargs):
    subprocess.run([str(a) for a in argv], check=True, **kwargs)


def build(root, archive=None, patch=None):
    candidate = inputs(archive, patch)
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    download = root / 'upstream.tar.gz'
    if archive is None:
        with urllib.request.urlopen(candidate['source']['url'], timeout=30) as source:
            download.write_bytes(source.read())
    else:
        download.write_bytes(archive.read_bytes())
    if digest(download) != candidate['source']['sha256']:
        raise ValueError('Source archive hash mismatch')
    with tarfile.open(download) as source:
        source.extractall(root / 'source', filter='data')
    source = next((root / 'source').iterdir())
    for name, expected in candidate['source_modules'].items():
        if digest(source / name) != expected:
            raise ValueError(f'Base source hash mismatch: {name}')
    patch = patch or BUNDLE / 'patches/lifecycle.patch'
    # Exact base/output hashes bind the patch; BSD patch uses no prompts or fuzz.
    run(['/usr/bin/patch', '-p1', '-t', '-F', '0', '-i', patch], cwd=source)
    for name, expected in candidate['repaired_modules'].items():
        if digest(source / name) != expected:
            raise ValueError(f'Patched source hash mismatch: {name}')
    (source / 'NOTICE').write_bytes((BUNDLE / 'NOTICE.md').read_bytes())
    backend = root / 'backend'
    runtime = root / 'runtime'
    managed = Path(subprocess.check_output(['uv', 'python', 'find', '--managed-python', candidate['python']], text=True).strip()).resolve().parent.parent
    private_python = root / 'python'
    shutil.copytree(managed, private_python, symlinks=True)
    for environment, lock in ((backend, 'build.lock'), (runtime, 'runtime.lock')):
        run(['uv', 'venv', environment, '--python', private_python / 'bin/python3.12' if environment == runtime else candidate['python']])
        run(['uv', 'pip', 'sync', '--python', environment / 'bin/python',
             BUNDLE / 'scripts' / lock, '--require-hashes', '--link-mode', 'copy'])
    environment = {**os.environ, 'SOURCE_DATE_EPOCH': candidate['source_date_epoch']}
    run(['uv', 'build', '--wheel', '--no-build-isolation', '--python', backend / 'bin/python',
         '--out-dir', root / 'dist', source], env=environment)
    wheel, = (root / 'dist').glob('*.whl')
    run(['uv', 'pip', 'install', '--python', runtime / 'bin/python', '--no-deps', '--link-mode', 'copy', wheel])
    manifest = runtime_inventory.seal(root)
    (root / 'runtime-manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    record = {'schema': 2, 'runtime_manifest_sha256': digest(root / 'runtime-manifest.json'), 'candidate_sha256': digest(BUNDLE / 'candidate.json'),
              'source_sha256': candidate['source']['sha256'],
              'inputs': candidate['inputs'], 'wheel_sha256': digest(wheel),
              'wheel': str(wheel), 'runtime': str(runtime)}
    (root / 'build-receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    record['observed'] = probe_built_runtime(runtime, candidate)
    (root / 'build-receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    verify_runtime(runtime)
    print(json.dumps(record, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['check', 'build', 'verify'])
    parser.add_argument('--root', type=Path, help='new private build directory; parent must exist')
    parser.add_argument('--archive', type=Path, help='optional pinned archive, verified before extraction')
    parser.add_argument('--patch', type=Path, help='optional exact pinned patch, never an override')
    parser.add_argument('--runtime', type=Path, help='runtime created by this recipe')
    parser.add_argument('--receipt-sha256', help='optional trusted build-receipt digest; installed launchers bind it in config')
    args = parser.parse_args()
    try:
        if args.operation == 'check':
            inputs(args.archive, args.patch)
            print('Candidate source/patch/dependency inputs verified')
        elif args.operation == 'verify':
            if args.runtime is None:
                parser.error('verify requires --runtime')
            print(json.dumps(verify_runtime(args.runtime.resolve(), args.receipt_sha256), indent=2))
        else:
            if args.root is None:
                parser.error('build requires --root')
            build(args.root.resolve(), args.archive, args.patch)
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f'Runtime refused: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
