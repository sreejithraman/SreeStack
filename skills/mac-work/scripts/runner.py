"""Canonical operation handling over the upstream SQLite task/receipt seam."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import sqlite3
import subprocess
import sys
import time

from runner_config import POLICY, activation_lock, validate_config, write_json, require_active


def request(operation_id, owner, argv, worktree, queue_seconds, execution_seconds):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}', operation_id):
        raise ValueError('Operation ID must be 1..128 letters, numbers or _.:-')
    if not owner.strip() or not argv or any(not isinstance(a, str) or '\0' in a for a in argv):
        raise ValueError('Owner and nonempty command argv are required')
    if type(queue_seconds) is not int or type(execution_seconds) is not int or min(queue_seconds, execution_seconds) < 1:
        raise ValueError('Queue and execution deadlines must be positive integer seconds')
    directory = Path(worktree).expanduser()
    if not directory.is_absolute():
        raise ValueError('Worktree must be absolute')
    directory = directory.resolve()
    top = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', '--show-toplevel'], text=True).strip()
    if Path(top).resolve() != directory:
        raise ValueError('Worktree must be its Git root')
    revision = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-C', str(directory), 'status', '--porcelain'], text=True).strip())
    return {'schema': 1, 'operation_id': operation_id, 'owner': owner, 'argv': argv,
            'worktree': str(directory), 'revision': revision, 'dirty': dirty,
            'queue_seconds': queue_seconds, 'execution_seconds': execution_seconds,
            'ownership_contract': 'process-group'}


def paths(config, operation_id):
    token = hashlib.sha256(operation_id.encode()).hexdigest()
    directory = Path(config['state']) / 'operations' / token
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    return directory / 'receipt.json', directory / 'output.log'


@contextmanager
def database(config):
    from queue_core import QueuePaths, get_db
    import queue_lifecycle as lifecycle
    queue = QueuePaths.from_data_dir(Path(config['state']))
    if not queue.db_path.is_file():
        raise ValueError('Shared admission database missing; restore state, never resubmit into an empty queue')
    with get_db(queue.db_path) as conn:
        lifecycle.configure(conn, POLICY['capacities'], POLICY['ownership_contract'])
        yield conn


def snapshot(conn, config, operation_id):
    import queue_lifecycle as lifecycle
    lifecycle.reconcile(conn, 'heavy', 120)
    conn.execute('BEGIN IMMEDIATE')
    operation = conn.execute('SELECT * FROM task_operations WHERE operation_id=?', (operation_id,)).fetchone()
    if operation is None:
        raise ValueError('Unknown operation ID; status never submits')
    value = lifecycle.read_task(conn, operation['task_id'])
    spec = json.loads(operation['request_json'])
    receipt, output = paths(config, operation_id)
    metadata = value['lifecycle']
    queued_at = metadata['queue_deadline'] - spec['queue_seconds']
    started_at = metadata.get('admitted_at')
    if started_at is None and metadata.get('execution_deadline') is not None:
        started_at = metadata['execution_deadline'] - spec['execution_seconds']
    value.update(schema=1, queued_at=queued_at, started_at=started_at,
                 deadlines={'queue': metadata['queue_deadline'], 'execution': metadata.get('execution_deadline')},
                 operation_id=operation_id, request=spec,
                 configuration_sha256=operation['configuration_sha256'],
                 worker=json.loads(operation['worker_json']) if operation['worker_json'] else None,
                 receipt_path=str(receipt), log_path=str(output), ownership_contract='process-group')
    write_json(receipt, value)
    conn.commit()
    return value


def status(config, operation_id):
    with activation_lock(Path(config['root'])):
        require_active(config)
        with database(config) as conn:
            return snapshot(conn, config, operation_id)


def submit(config, spec):
    import queue_lifecycle as lifecycle
    with activation_lock(Path(config['root'])):
        require_active(config)
        import queue_lifecycle as lifecycle
        with database(config) as conn:
            task, created = lifecycle.reserve_operation(conn, spec['operation_id'], spec, config['_sha256'])
        if created:
            receipt, output = paths(config, spec['operation_id'])
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                child = subprocess.Popen([str(Path(config['root']) / 'bin/mac-work'),
                    '--config', str(Path(config['root']) / 'current.json'), '_worker',
                    '--configuration', config['_path'], '--sha256', config['_sha256'],
                    '--id', spec['operation_id']], stdin=subprocess.DEVNULL,
                    stdout=descriptor, stderr=descriptor, start_new_session=True, close_fds=True)
            except OSError as error:
                with database(config) as conn:
                    lifecycle.close_task(conn, task, {'status': 'error', 'error': str(error), 'duration_seconds': 0}, reason='worker_start_failed')
                raise
            finally:
                os.close(descriptor)
            # Acceptance includes durable worker ownership, not merely a spawned PID.
            deadline = time.monotonic() + 15
            while True:
                with database(config) as conn:
                    row = conn.execute('SELECT worker_json FROM task_operations WHERE operation_id=?',
                                       (spec['operation_id'],)).fetchone()
                    if row['worker_json'] is not None:
                        break
                    state = lifecycle.read_task(conn, task)
                    if state['status'] not in {'queued', 'running'}:
                        break
                    if child.poll() is not None or time.monotonic() >= deadline:
                        lifecycle.close_task(conn, task,
                            {'status': 'error', 'error': 'Worker did not establish ownership; inspect log', 'duration_seconds': 0},
                            reason='worker_start_failed')
                        break
                time.sleep(.025)
        with database(config) as conn:
            return snapshot(conn, config, spec['operation_id'])


def cancel(config, operation_id):
    with activation_lock(Path(config['root'])):
        require_active(config)
        import queue_lifecycle as lifecycle
        with database(config) as conn:
            operation = conn.execute('SELECT * FROM task_operations WHERE operation_id=?', (operation_id,)).fetchone()
            if operation is None:
                raise ValueError('Unknown operation ID')
            lifecycle.close_task(conn, operation['task_id'], {'status': 'cancelled', 'duration_seconds': 0},
                                 terminate=True, reason='canonical_cancel')
            return snapshot(conn, config, operation_id)


def wait(config, operation_id, seconds):
    end = time.monotonic() + seconds
    while True:
        value = status(config, operation_id)
        if value['status'] not in {'queued', 'running'} or time.monotonic() >= end:
            return value
        time.sleep(.1)


def worker(config, operation_id):
    with activation_lock(Path(config['root'])):
        require_active(config)
        from queue_core import attempt_task_start
        import queue_lifecycle as lifecycle
        with database(config) as conn:
            operation = lifecycle.claim_operation(conn, operation_id, config['_sha256'])
        if operation is None:
            return
        spec = json.loads(operation['request_json'])
        task = operation['task_id']
        launched = False
        result = None
        started = None
        execution_deadline = None
        process = None

        def interrupted(signum, frame):
            raise InterruptedError('Worker interrupted')

        signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        try:
            while True:
                with database(config) as conn:
                    lifecycle.reconcile(conn, 'heavy', 120)
                    row = conn.execute('SELECT * FROM queue WHERE id=?', (task,)).fetchone()
                    if row is None:
                        return
                    if lifecycle.read_task(conn, task)['status'] == 'recovery-pending':
                        result = {'status': 'cancelled', 'duration_seconds': 0}
                        break
                    metadata = json.loads(row['lifecycle_json'])
                    if time.time() >= metadata['queue_deadline']:
                        result = {'status': 'queue-timeout', 'duration_seconds': 0}
                        break
                    try:
                        admitted, _ = attempt_task_start(conn, task, 'heavy', {'heavy': 1}, os.getpid())
                    except sqlite3.OperationalError as error:
                        code = getattr(error, 'sqlite_errorcode', 0) & 255
                        if code not in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}:
                            raise
                        admitted = False
                    if admitted:
                        metadata = lifecycle.read_task(conn, task)['lifecycle']
                        started = metadata['admitted_at']
                        execution_deadline = metadata['execution_deadline']
                if admitted:
                    break
                time.sleep(.1)
            if result is None:
                validate_config(Path(config['_path']), config['_sha256'])
                current_revision = subprocess.check_output(['git', '-C', spec['worktree'], 'rev-parse', 'HEAD'], text=True).strip()
                if current_revision != spec['revision']:
                    raise ValueError('Worktree revision changed while queued')
                with database(config) as conn:
                    if lifecycle.read_task(conn, task)['status'] == 'recovery-pending':
                        result = {'status': 'cancelled', 'duration_seconds': 0}
                    else:
                        process = lifecycle.launch(conn, task, shlex.join(spec['argv']), cwd=spec['worktree'])
                        launched = True
                if process is not None:
                    try:
                        code = process.wait(timeout=max(0, execution_deadline - time.time()))
                        result = {'status': 'success' if code == 0 else 'failed', 'exit_code': code,
                                  'duration_seconds': time.time() - started}
                    except subprocess.TimeoutExpired:
                        result = {'status': 'timeout', 'duration_seconds': time.time() - started,
                                  'timeout_seconds': spec['execution_seconds']}
        except BaseException as error:
            if isinstance(error, TimeoutError):
                status = 'timeout' if started is not None else 'queue-timeout'
            elif isinstance(error, InterruptedError):
                status = 'interrupted'
            else:
                status = 'error'
            result = {'status': status, 'error': str(error),
                      'duration_seconds': time.time() - started if started is not None else 0}
            if status == 'timeout':
                result['timeout_seconds'] = spec['execution_seconds']
        finally:
            blocked = {signal.SIGTERM, signal.SIGINT}
            previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, blocked)
            for signum in blocked:
                signal.signal(signum, signal.SIG_IGN)
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
            with database(config) as conn:
                lifecycle.close_task(conn, task, result, terminate=True,
                    reason='canonical_worker_finished', never_started=not launched)
                snapshot(conn, config, operation_id)
