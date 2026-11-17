"""Focused real dependency regressions; every case uses private disposable state."""

import argparse
import importlib
import json
import os
import shlex
from pathlib import Path
import sqlite3
import sys
import tempfile
import time


def fixture(core, lifecycle, directory):
    path = directory / 'queue.db'
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(core.QUEUE_SCHEMA)
    conn.execute(core.TASK_RESULTS_SCHEMA)
    lifecycle.schema(conn)
    conn.execute('INSERT INTO admission_policy VALUES (1, ?)',
                 (json.dumps({'schema': 1, 'capacities': {'heavy': 1},
                              'ownership_contract': 'process-group'}, sort_keys=True),))
    task = core.insert_waiting_task(conn, 'heavy', os.getpid(), 'regression', 'true', None)
    lifecycle.limits(conn, task, 2, 10)
    return conn, task


def admission_clock(core, lifecycle, directory):
    conn, task = fixture(core, lifecycle, directory)
    before = time.time()
    admitted, _ = core.attempt_task_start(conn, task, 'heavy', {'heavy': 1}, os.getpid())
    after = time.time()
    meta = lifecycle.read_task(conn, task)['lifecycle']
    assert admitted
    assert before <= meta.get('admitted_at', 0) <= after, meta
    assert meta['execution_deadline'] == meta['admitted_at'] + 2, meta
    assert not meta.get('child'), meta
    conn.close()
    return {'admitted_at': meta['admitted_at'], 'execution_deadline': meta['execution_deadline'],
            'observation': [before, after], 'child_registered': False}


def registration_cancel(core, lifecycle, directory):
    conn, task = fixture(core, lifecycle, directory)
    core.attempt_task_start(conn, task, 'heavy', {'heavy': 1}, os.getpid())
    other = sqlite3.connect(directory / 'queue.db')
    other.row_factory = sqlite3.Row
    marker = directory / 'must-not-run'
    original = lifecycle.process_identity
    cancellation = []
    children = []

    def at_child_identity(pid):
        if pid != os.getpid() and not cancellation:
            children.append(pid)
            cancellation.append(lifecycle.close_task(other, task,
                {'status': 'cancelled', 'duration_seconds': 0}, True, 'regression_cancel'))
        return original(pid)

    lifecycle.process_identity = at_child_identity
    process = None
    try:
        try:
            process = lifecycle.launch(conn, task, 'touch ' + shlex.quote(str(marker)))
        except RuntimeError:
            pass
    finally:
        lifecycle.process_identity = original
        if process is not None:
            process.wait(timeout=5)
        for pid in children:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass
    final = lifecycle.close_task(conn, task, {'status': 'error', 'duration_seconds': 0},
                                 True, 'regression_finally')
    assert cancellation, 'launch never reached child identity barrier'
    assert not marker.exists(), 'committed cancellation lost: command executed'
    assert final.get('intended_status', final['status']) == 'cancelled', final
    assert lifecycle.read_task(other, task) == final
    conn.close()
    other.close()
    return {'marker_exists': False, 'durable_status': final.get('intended_status', final['status']),
            'capacity_held': final['capacity_held'], 'clients': 2}


def active_state(core, lifecycle, directory):
    path = directory / 'queue.db'
    path.write_bytes(b'')
    before = path.read_bytes()
    refused = False
    try:
        core.ensure_db(core.QueuePaths.from_data_dir(directory))
        with core.get_db(path) as conn:
            lifecycle.configure(conn, {'heavy': 1}, 'process-group')
    except (ValueError, RuntimeError, sqlite3.DatabaseError):
        refused = True
    assert refused, 'active empty database was silently rebuilt'
    assert path.read_bytes() == before, 'damaged bytes changed during refusal'
    return {'empty_existing_state_refused': True, 'damaged_bytes_preserved': True}


def gate_environment(core, lifecycle, directory):
    conn, task = fixture(core, lifecycle, directory)
    core.attempt_task_start(conn, task, 'heavy', {'heavy': 1}, os.getpid())
    shadow = directory / 'shadow'
    shadow.mkdir()
    marker = directory / 'untrusted-import'
    (shadow / 'sitecustomize.py').write_text('from pathlib import Path; Path(' + repr(str(marker)) + ').touch()')
    preserved = directory / 'command-environment'
    env = {**os.environ, 'PYTHONPATH': str(shadow)}
    process = lifecycle.launch(conn, task, '/usr/bin/printenv PYTHONPATH > ' + shlex.quote(str(preserved)), env=env)
    assert process.wait(timeout=5) == 0
    assert not marker.exists(), 'trusted gate imported caller sitecustomize'
    assert preserved.read_text().strip() == str(shadow), 'command lost requested environment'
    final = lifecycle.close_task(conn, task, {'status': 'success', 'duration_seconds': 0}, True)
    assert final['status'] == 'success' and not final['capacity_held'], final
    conn.close()
    return {'trusted_import_sentinel': False, 'requested_environment_preserved': True}


def bootstrap_active_open(core, lifecycle, directory):
    paths = core.QueuePaths.from_data_dir(directory)
    core.init_db(paths, {'heavy': 1}, 'process-group')
    with core.get_db(paths.db_path) as conn:
        assert conn.execute('SELECT COUNT(*) FROM task_operations').fetchone()[0] == 0
        lifecycle.configure(conn, {'heavy': 1}, 'process-group')
    before = paths.db_path.read_bytes()
    core.init_db(paths, {'heavy': 1}, 'process-group')
    assert paths.db_path.read_bytes() == before, 'compatible idle initialization changed state'
    return {'fresh_bootstrap_valid': True, 'compatible_idle_reopen': True}


def damaged_wal_state(core, lifecycle, directory):
    paths = core.QueuePaths.from_data_dir(directory)
    core.init_db(paths, {'heavy': 1}, 'process-group')
    writer = sqlite3.connect(paths.db_path)
    try:
        writer.execute('DROP TABLE task_operations')
        writer.commit()
        files = [paths.db_path, Path(str(paths.db_path) + '-wal')]
        before = {str(path): path.read_bytes() for path in files}
        refused = False
        try:
            core.ensure_db(paths)
        except ValueError:
            refused = True
        assert refused, 'damaged WAL schema accepted'
        assert all(path.read_bytes() == before[str(path)] for path in files), 'refusal checkpointed damaged WAL bytes'
        return {'refused': True, 'database_and_wal_preserved': True}
    finally:
        writer.close()


def registration_phase(core, lifecycle, directory):
    conn, task = fixture(core, lifecycle, directory)
    core.attempt_task_start(conn, task, 'heavy', {'heavy': 1}, os.getpid())
    marker = directory / 'duplicate-command'
    first = lifecycle.launch(conn, task, '/bin/sleep .5')
    second = None
    refused = False
    try:
        try:
            second = lifecycle.launch(conn, task, 'touch ' + shlex.quote(str(marker)))
        except RuntimeError:
            refused = True
        if second is not None:
            second.wait(timeout=5)
        assert refused and not marker.exists(), 'executing phase accepted another gated launch'
    finally:
        first.wait(timeout=5)
        lifecycle.close_task(conn, task, {'status': 'success', 'duration_seconds': 0}, True)
        conn.close()
    return {'second_launch_refused': True, 'duplicate_marker': False}


CASES = {'registration-phase': registration_phase, 'damaged-wal-state': damaged_wal_state, 'bootstrap-active-open': bootstrap_active_open, 'gate-environment': gate_environment, 'active-state' : active_state, 'admission-clock' : admission_clock, 'registration-cancel': registration_cancel}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modules', type=Path, required=True, help='actual repaired source or runtime site-packages')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES, action='append', required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.modules.resolve()))
    core = importlib.import_module('queue_core')
    lifecycle = importlib.import_module('queue_lifecycle')
    args.output.mkdir(parents=True, exist_ok=False)
    verdicts = []
    for name in args.case:
        with tempfile.TemporaryDirectory(prefix='mac-work-regression-') as temporary:
            try:
                details = CASES[name](core, lifecycle, Path(temporary))
                verdict = {'case': name, 'verdict': 'passed', 'details': details}
            except Exception as error:
                verdict = {'case': name, 'verdict': 'failed', 'error': repr(error)}
            verdicts.append(verdict)
            print(json.dumps(verdict), flush=True)
    (args.output / 'verdicts.json').write_text(json.dumps(verdicts, indent=2) + '\n')
    return int(any(v['verdict'] != 'passed' for v in verdicts))


if __name__ == '__main__':
    sys.exit(main())
