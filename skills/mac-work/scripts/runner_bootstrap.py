#!/usr/bin/env -S /usr/bin/python3 -I -B -S
"""Stable, root-bound launcher for immutable mac-work releases."""

import hashlib
import json
import os
from pathlib import Path
import sys
import stat


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    pointer = root / 'current.json'
    index = 1
    while index < len(sys.argv):
        argument = sys.argv[index]
        if argument == '--config' or argument.startswith('--config='):
            value = sys.argv[index + 1] if argument == '--config' else argument.split('=', 1)[1]
            if Path(value).resolve() != pointer:
                raise ValueError('This launcher is bound to its own current.json')
            index += 2 if argument == '--config' else 1
        else:
            break
    selected = json.loads(pointer.read_text())
    config_path = Path(selected['configuration'])
    if selected['schema'] != 1 or config_path.parent.parent != root / 'versions':
        raise ValueError('Invalid active configuration path/schema')
    if digest(config_path) != selected['sha256']:
        raise ValueError('Configuration hash mismatch')
    config = json.loads(config_path.read_text())
    if Path(config['root']) != root or config['schema'] != 1:
        raise ValueError('Configuration root/schema mismatch')
    if digest(Path(__file__)) != config['launcher_sha256']:
        raise ValueError('Launcher hash mismatch')
    manifest = config_path.parent / 'bundle-manifest.json'
    if digest(manifest) != config['bundle_sha256']:
        raise ValueError('Bundle manifest hash mismatch')
    bundle = config_path.parent / 'bundle'
    expected_files = json.loads(manifest.read_text())
    helper = bundle / 'scripts/runtime_inventory.py'
    info = helper.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('Runtime inventory helper must be a private regular file')
    source = helper.read_bytes()
    if hashlib.sha256(source).hexdigest() != expected_files['scripts/runtime_inventory.py']:
        raise ValueError('Runtime inventory helper hash mismatch')
    namespace = {'__file__': str(helper), '__name__': 'trusted_runtime_inventory'}
    exec(compile(source, str(helper), 'exec'), namespace)
    namespace['verify_bundle'](bundle, expected_files)
    build = config_path.parent / 'build'
    record = namespace['verify'](build, config['build_receipt_sha256'])
    if record['candidate_sha256'] != digest(bundle / 'candidate.json'):
        raise ValueError('Runtime candidate/configuration hash mismatch')
    python = build / 'runtime/bin/python'
    if Path(config['runtime']) != build / 'runtime' or digest(python) != config['python_sha256']:
        raise ValueError('Runtime interpreter path/hash mismatch')
    os.execv(str(python), [str(python), '-I', '-B', str(bundle / 'scripts/mac_work.py'),
                         '--config', str(pointer), *sys.argv[1:]])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError) as error:
        print(f'mac-work refused: {error}', file=sys.stderr)
        sys.exit(2)
