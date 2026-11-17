"""Actual disposable-runtime drift refusals. Mutations never write shared inodes."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile


def private_replace(path, data, mode=None):
    """Replace a task-owned path atomically, including when uv supplied a hardlink."""
    parent_mode = stat.S_IMODE(path.parent.stat().st_mode)
    original_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o444
    os.chmod(path.parent, parent_mode | 0o200)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.fixture-')
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
        os.chmod(temporary, original_mode if mode is None else mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
        os.chmod(path.parent, parent_mode)


def create_directory(path):
    mode = stat.S_IMODE(path.parent.stat().st_mode)
    os.chmod(path.parent, mode | 0o200)
    try:
        path.mkdir()
    finally:
        os.chmod(path.parent, mode)


def remove_owned(path):
    mode = stat.S_IMODE(path.parent.stat().st_mode)
    os.chmod(path.parent, mode | 0o200)
    try:
        if path.is_dir() and not path.is_symlink():
            for child in path.iterdir():
                remove_owned(child)
            path.rmdir()
        else:
            path.unlink()
    finally:
        os.chmod(path.parent, mode)


def observe(root, runtime, verifier, output, case):
    site = next((runtime / 'lib').glob('python*/site-packages'))
    target = site / 'fastmcp/__init__.py'
    before = target.read_bytes()
    before_mode = stat.S_IMODE(target.stat().st_mode)
    links_before = target.stat().st_nlink
    marker = output / (case + '.executed')
    sentinel = ('\nfrom pathlib import Path as _DriftPath\n_DriftPath(' + repr(str(marker)) + ').touch()\n')
    additions = []
    restore_target = False
    try:
        if case == 'dependency-body':
            private_replace(target, before + sentinel.encode() + b'raise RuntimeError("fixture dependency sentinel")\n')
            restore_target = True
        elif case in {'startup-pth', 'bootstrap-python-path'}:
            extra = site / 'mac_work_fixture.pth'
            private_replace(extra, ('import pathlib; pathlib.Path(' + repr(str(marker)) + ').touch()\n').encode())
            additions.append(extra)
        elif case in {'sitecustomize', 'extra-import'}:
            extra = site / ('sitecustomize.py' if case == 'sitecustomize' else 'unexpected_import.py')
            private_replace(extra, sentinel.encode())
            additions.append(extra)
        elif case == 'extra-distribution':
            extra = site / 'unexpected_package-1.0.dist-info'
            create_directory(extra)
            additions.append(extra)
            private_replace(extra / 'METADATA', b'Metadata-Version: 2.1\nName: unexpected-package\nVersion: 1.0\n')
        elif case == 'bytecode-cache':
            code = (sentinel + 'raise RuntimeError("fixture bytecode sentinel")\n').encode()
            assert len(code) < len(before)
            staged = output / 'staged.py'
            staged.write_bytes(code + b'#' * (len(before) - len(code)))
            stamp = target.stat().st_mtime_ns
            os.utime(staged, ns=(stamp, stamp))
            compiled = output / 'staged.pyc'
            subprocess.run([str(runtime / 'bin/python'), '-I', '-B', '-c',
                'import py_compile,sys;py_compile.compile(sys.argv[1],cfile=sys.argv[2],doraise=True)',
                str(staged), str(compiled)], check=True, capture_output=True)
            cache = target.parent / '__pycache__'
            if not cache.exists():
                create_directory(cache)
                additions.append(cache)
            extra = cache / '__init__.cpython-312.pyc'
            if extra.exists():
                raise ValueError('Bytecode fixture requires a clean package cache baseline')
            private_replace(extra, compiled.read_bytes())
            if cache not in additions:
                additions.append(extra)
        elif case in {'symlink', 'fifo', 'file-mode'}:
            if case == 'file-mode':
                private_replace(target, before, mode=0o755)
            else:
                parent_mode = stat.S_IMODE(target.parent.stat().st_mode)
                os.chmod(target.parent, parent_mode | 0o200)
                try:
                    target.unlink()
                    if case == 'symlink':
                        external = output / 'external.py'
                        external.write_bytes(before)
                        target.symlink_to(external)
                    else:
                        os.mkfifo(target)
                finally:
                    os.chmod(target.parent, parent_mode)
            restore_target = True
        else:
            raise ValueError(case)
        verified = subprocess.run([sys.executable, '-I', '-B', str(verifier), 'verify', '--runtime', str(runtime)],
                                  capture_output=True, text=True, timeout=25)
        env = dict(os.environ)
        if case == 'bootstrap-python-path':
            env['PATH'] = str(runtime / 'bin') + os.pathsep + env['PATH']
        mcp = None
        if case != 'fifo':
            mcp = subprocess.run([str(root / 'bin/mac-work'), 'mcp'], stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=25, env=env)
        result = {'case': case, 'verifier_exit': verified.returncode,
                  'verifier_stdout': verified.stdout, 'verifier_stderr': verified.stderr,
                  'mcp_exit': mcp.returncode if mcp else None,
                  'mcp_stderr': mcp.stderr if mcp else None,
                  'sentinel_executed': marker.exists(), 'old_inode_links': links_before,
                  'mutation': 'atomic replacement/new private file; never in-place write',
                  'original_dependency_sha256': hashlib.sha256(before).hexdigest()}
        result['verdict'] = 'passed' if verified.returncode == 2 and (mcp is None or mcp.returncode == 2) and not marker.exists() else 'failed'
        return result
    finally:
        if restore_target:
            if target.is_symlink() or not target.is_file():
                remove_owned(target)
            private_replace(target, before, mode=before_mode)
        for extra in reversed(additions):
            remove_owned(extra)


CASES = ('dependency-body', 'startup-pth', 'sitecustomize', 'extra-import', 'extra-distribution',
         'bytecode-cache', 'symlink', 'fifo', 'file-mode', 'bootstrap-python-path')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='new task-owned disposable install, never shared/retained roots')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES, action='append')
    args = parser.parse_args()
    selected = json.loads((args.root / 'current.json').read_text())
    configuration = Path(selected['configuration'])
    runtime = Path(json.loads(configuration.read_text())['runtime'])
    verifier = configuration.parent / 'bundle/scripts/build_runtime.py'
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    for case in args.case or CASES:
        result = observe(args.root.resolve(), runtime, verifier, args.output, case)
        results.append(result)
        (args.output / (case + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k: result[k] for k in ('case', 'verdict', 'verifier_exit', 'mcp_exit', 'sentinel_executed')}), flush=True)
    (args.output / 'verdicts.json').write_text(json.dumps(results, indent=2) + '\n')
    return int(any(r['verdict'] != 'passed' for r in results))


if __name__ == '__main__':
    sys.exit(main())
