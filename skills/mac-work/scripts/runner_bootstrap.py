#!/usr/bin/env -S python3 -I -B
"""Stable, root-bound launcher for immutable mac-work releases."""

import hashlib
import json
import os
from pathlib import Path
import sys


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
    actual_files = {str(p.relative_to(bundle)) for p in bundle.rglob('*')
                    if p.is_file() and '__pycache__' not in p.parts}
    if actual_files != set(expected_files):
        raise ValueError('Bundle file set mismatch')
    for name, expected in expected_files.items():
        if digest(bundle / name) != expected:
            raise ValueError(f'Bundle hash mismatch: {name}')
    python = config_path.parent / 'build/runtime/bin/python'
    if digest(python.resolve()) != config['python_sha256']:
        raise ValueError('Runtime interpreter hash mismatch')
    os.execv(str(python), [str(python), '-I', '-B', str(bundle / 'scripts/mac_work.py'),
                         '--config', str(pointer), *sys.argv[1:]])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError) as error:
        print(f'mac-work refused: {error}', file=sys.stderr)
        sys.exit(2)
