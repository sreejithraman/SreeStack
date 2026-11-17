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
import subprocess
import sys
import tarfile
import urllib.request

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


def verify_runtime(runtime):
    candidate = inputs()
    record = json.loads((runtime.parent / 'build-receipt.json').read_text())
    if record['schema'] != 1:
        raise ValueError('Unsupported build receipt schema')
    if record['candidate_sha256'] != digest(BUNDLE / 'candidate.json'):
        raise ValueError('Runtime candidate/configuration hash mismatch')
    probe = """import importlib.metadata as m, importlib.util as u, json, sys, re
print(json.dumps({'python':sys.version.split()[0], 'package':m.version('agent-task-queue'),
 'versions':{re.sub(r'[-_.]+','-', d.metadata['Name']).lower(): d.version for d in m.distributions()},
 'files':{n:u.find_spec(n).origin for n in ('queue_core','queue_lifecycle','tq','task_queue')}}))"""
    result = subprocess.run([str(runtime / 'bin/python'), '-I', '-c', probe], text=True,
                            capture_output=True, check=True, timeout=10)
    observed = json.loads(result.stdout)
    if (observed['python'], observed['package']) != (candidate['python'], candidate['package_version']):
        raise ValueError('Runtime version mismatch')
    expected = dict(re.findall(r'^([a-z0-9-]+)==(\S+)', (BUNDLE / 'scripts/runtime.lock').read_text(), re.M))
    if any(observed['versions'].get(name) != version for name, version in expected.items()):
        raise ValueError('Runtime dependency version mismatch')
    for name, path in observed['files'].items():
        if digest(Path(path)) != candidate['repaired_modules'][name + '.py']:
            raise ValueError(f'Repaired source hash mismatch: {name}')
    observed['candidate_sha256'] = record['candidate_sha256']
    observed['wheel_sha256'] = record['wheel_sha256']
    observed['verified_modules'] = candidate['repaired_modules']
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
    for environment, lock in ((backend, 'build.lock'), (runtime, 'runtime.lock')):
        run(['uv', 'venv', environment, '--python', candidate['python']])
        run(['uv', 'pip', 'sync', '--python', environment / 'bin/python',
             BUNDLE / 'scripts' / lock, '--require-hashes'])
    environment = {**os.environ, 'SOURCE_DATE_EPOCH': candidate['source_date_epoch']}
    run(['uv', 'build', '--wheel', '--no-build-isolation', '--python', backend / 'bin/python',
         '--out-dir', root / 'dist', source], env=environment)
    wheel, = (root / 'dist').glob('*.whl')
    run(['uv', 'pip', 'install', '--python', runtime / 'bin/python', '--no-deps', wheel])
    record = {'schema': 1, 'candidate_sha256': digest(BUNDLE / 'candidate.json'),
              'source_sha256': candidate['source']['sha256'],
              'inputs': candidate['inputs'], 'wheel_sha256': digest(wheel),
              'wheel': str(wheel), 'runtime': str(runtime)}
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
    args = parser.parse_args()
    try:
        if args.operation == 'check':
            inputs(args.archive, args.patch)
            print('Candidate source/patch/dependency inputs verified')
        elif args.operation == 'verify':
            if args.runtime is None:
                parser.error('verify requires --runtime')
            print(json.dumps(verify_runtime(args.runtime.resolve()), indent=2))
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
