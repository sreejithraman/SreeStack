"""Failure-sensitive canonical runner proof in an explicitly task-owned install.

Startup cases use the real launcher/MCP. Worker cases inject one boundary fault
in a separate process using the installed bundle; installed bytes are never edited.
"""

import argparse
from contextlib import closing
import asyncio
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
import threading
from unittest.mock import patch


def installed(root):
    pointer = json.loads((root / 'current.json').read_text())
    config = Path(pointer['configuration'])
    sys.path.insert(0, str(config.parent / 'bundle/scripts'))
    import runner_config
    value = runner_config.load(root / 'current.json')
    return value, str(Path(value['runtime']) / 'bin/python')


def invoke(root, *argv, env=None):
    result = subprocess.run([str(root / 'bin/mac-work'), *argv], env=env,
                            capture_output=True, text=True, timeout=35)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def python_environment(root, output):
    shadow = output / 'shadow'
    shadow.mkdir()
    marker = output / 'untrusted-import'
    code = 'from pathlib import Path; Path(' + repr(str(marker)) + ').touch(); raise RuntimeError("untrusted Python override")\n'
    for name in ('queue_core.py', 'queue_lifecycle.py', 'sitecustomize.py'):
        (shadow / name).write_text(code)
    env = {**os.environ, 'PYTHONPATH': str(shadow), 'PYTHONHOME': str(output / 'not-a-python-home')}
    destination = output / 'command-environment'
    operation = 'python-env-' + hashlib.sha256(str(output).encode()).hexdigest()[:16]
    accepted = invoke(root, 'run', '--id', operation, '--owner', 'regression',
        '--worktree', str(Path.cwd()), '--execution-seconds', '10', '--wait-seconds', '20',
        '--json', '--', '/bin/sh', '-c', '/usr/bin/printenv PYTHONPATH > "$1"',
        'fixture', str(destination), env=env)
    assert not marker.exists(), 'trusted launcher/controller/worker imported caller override'
    assert accepted['status'] == 'success' and not accepted['capacity_held'], accepted
    assert destination.read_text().strip() == str(shadow), 'requested command environment changed'
    async def mcp_case():
        from fastmcp import Client
        from fastmcp.client.transports import StdioTransport
        transport = StdioTransport(command=str(root / 'bin/mac-work'), args=['mcp'],
            env={**env, 'FASTMCP_CHECK_FOR_UPDATES': 'off'}, keep_alive=False)
        async with Client(transport) as client:
            mcp_output = output / 'mcp-environment'
            submitted = await client.call_tool('run_command', {
                'operation_id': operation + '-mcp', 'owner': 'regression',
                'worktree': str(Path.cwd()), 'argv': ['/bin/sh', '-c',
                '/usr/bin/printenv PYTHONHOME > "$1"', 'fixture', str(mcp_output)],
                'queue_seconds': 10, 'execution_seconds': 10})
            value = submitted.structured_content
            end = time.monotonic() + 20
            while value['status'] in {'queued', 'running'} and time.monotonic() < end:
                await asyncio.sleep(.1)
                response = await client.call_tool('command_status', {'operation_id': operation + '-mcp'})
                value = response.structured_content
            assert value['status'] == 'success' and not value['capacity_held'], value
            assert mcp_output.read_text().strip() == env['PYTHONHOME']
            assert not marker.exists(), 'MCP imported caller Python override'
            return value

    mcp = asyncio.run(mcp_case())
    (output / 'mcp.json').write_text(json.dumps(mcp, indent=2) + '\n')
    return {'status': accepted['status'], 'sentinel_imported': False,
            'command_environment_preserved': True, 'task_id': accepted['task_id'], 'mcp_task_id': mcp['task_id']}


def fault_worker(root, output, name, operation):
    config, _ = installed(root)
    import queue_core as core
    import queue_lifecycle as lifecycle
    import runner
    restore = []
    timers = []
    events = []

    def replace(module, attribute, replacement):
        original = getattr(module, attribute)
        setattr(module, attribute, replacement)
        restore.append((module, attribute, original))
        return original

    if name in {'remaining-budget', 'expired-preflight', 'preflight-failure'}:
        original = runner.validate_config

        def slow_preflight(*args, **kwargs):
            value = original(*args, **kwargs)
            observed = invoke(root, 'status', '--id', operation, '--json')
            events.append({'during_preflight': observed})
            time.sleep(1.2 if name == 'expired-preflight' else .8)
            if name == 'preflight-failure':
                raise ValueError('controlled preflight failure')
            return value

        replace(runner, 'validate_config', slow_preflight)
    elif name == 'finalizer-signals':
        original = lifecycle.close_task

        def signal_during_close(*args, **kwargs):
            if kwargs.get('reason') == 'canonical_worker_finished':
                events.append({'signals_during_final_close': ['SIGTERM', 'SIGINT']})
                os.kill(os.getpid(), signal.SIGTERM)
                os.kill(os.getpid(), signal.SIGINT)
            return original(*args, **kwargs)

        replace(lifecycle, 'close_task', signal_during_close)
    elif name in {'cancel-before-registration', 'cancel-after-registration', 'after-registration-failure'}:
        if name == 'cancel-before-registration':
            original = lifecycle.process_identity
            cancelled = False

            def cancel_at_identity(pid):
                nonlocal cancelled
                if pid != os.getpid() and not cancelled:
                    cancelled = True
                    events.append({'public_cancel': invoke(root, 'cancel', '--id', operation, '--json')})
                return original(pid)

            replace(lifecycle, 'process_identity', cancel_at_identity)
        else:
            original = lifecycle.recorded_child

            def after_registration(*args, **kwargs):
                original(*args, **kwargs)
                if name == 'cancel-after-registration':
                    events.append({'public_cancel': invoke(root, 'cancel', '--id', operation, '--json')})
                else:
                    raise OSError('controlled failure after child registration')

            replace(lifecycle, 'recorded_child', after_registration)
    elif name == 'launch-before-registration':
        def fail_before_registration(*args, **kwargs):
            events.append({'launch_raised_before_child': True})
            raise OSError('controlled launch failure before child registration')

        replace(lifecycle, 'launch', fail_before_registration)
    elif name == 'sqlite-nonbusy':
        def missing_table(conn, *args, **kwargs):
            conn.execute('SELECT * FROM deliberately_missing_table')

        replace(core, 'attempt_task_start', missing_table)
    elif name in {'sqlite-contention', 'sqlite-queue-deadline', 'sqlite-cancel'}:
        original = core.attempt_task_start
        attempted = False

        def contend(conn, *args, **kwargs):
            nonlocal attempted
            if not attempted:
                attempted = True
                ready = threading.Event()

                def hold():
                    with closing(sqlite3.connect(root / 'state/queue.db')) as other:
                        with other:
                            other.execute('BEGIN IMMEDIATE')
                            ready.set()
                            time.sleep(1.4 if name == 'sqlite-queue-deadline' else .4)

                thread = threading.Thread(target=hold)
                timers.append(thread)
                thread.start()
                assert ready.wait(5)
                events.append({'held_write_transaction_seconds': .4})
            try:
                return original(conn, *args, **kwargs)
            except sqlite3.OperationalError:
                if name == 'sqlite-cancel':
                    for thread in timers:
                        thread.join(5)
                    events.append({'public_cancel': invoke(root, 'cancel', '--id', operation, '--json')})
                raise

        replace(core, 'attempt_task_start', contend)
    else:
        raise ValueError(name)
    error = None
    try:
        runner.worker(config, operation)
    except BaseException as failure:
        error = repr(failure)
    finally:
        for module, attribute, original in reversed(restore):
            setattr(module, attribute, original)
        for thread in timers:
            thread.join(5)
    with runner.database(config) as conn:
        task = conn.execute('SELECT task_id FROM task_operations WHERE operation_id=?', (operation,)).fetchone()[0]
        observed = lifecycle.read_task(conn, task)
        receipt, _ = runner.paths(config, operation)
        published = json.loads(receipt.read_text()) if receipt.exists() else None
        # Fixture cleanup by the still-live exact owner is separate from the verdict.
        lifecycle.close_task(conn, task, terminate=True, never_started=True, reason='fixture_cleanup')
        runner.snapshot(conn, config, operation)
    (output / 'worker.json').write_text(json.dumps({'observed': observed, 'published': published,
        'worker_error': error, 'events': events}, indent=2) + '\n')


def worker_case(root, output, name):
    config, python = installed(root)
    import runner
    operation = name + '-' + output.parent.name
    marker = output / 'command-marker'
    argv = ['/usr/bin/touch', str(marker)]
    queue_seconds = 1 if name == 'sqlite-queue-deadline' else 10
    execution_seconds = 5
    if name in {'remaining-budget', 'expired-preflight', 'preflight-failure'}:
        execution_seconds = 1 if name == 'expired-preflight' else 15
        argv = ['/bin/sh', '-c', 'touch "$1"; sleep 14', 'fixture', str(marker)]
    original = subprocess.Popen
    children = []

    def inject(argv, *args, **kwargs):
        if '_worker' in argv:
            argv = [python, '-I', '-B', str(Path(__file__).resolve()), '--root', str(root),
                    '--output', str(output), '--case', name, '--worker', operation]
            process = original(argv, *args, **kwargs)
            children.append(process)
            return process
        return original(argv, *args, **kwargs)

    subprocess.Popen = inject
    try:
        accepted = runner.submit(config, operation, 'failure-regression', argv, str(Path.cwd()),
                                 queue_seconds, execution_seconds)
    finally:
        subprocess.Popen = original
    assert len(children) == 1, 'expected one owned worker'
    assert children[0].wait(timeout=30) == 0
    value = json.loads((output / 'worker.json').read_text())
    (output / 'acceptance.json').write_text(json.dumps(accepted, indent=2) + '\n')
    observed = value['observed']
    assert value['worker_error'] is None, value['worker_error']
    expected = ('queue-timeout' if name == 'sqlite-queue-deadline'
                else 'cancelled' if name == 'sqlite-cancel'
                else 'timeout' if name in {'remaining-budget', 'expired-preflight'}
                else 'cancelled' if name.startswith('cancel-')
                else 'error' if name in {'launch-before-registration', 'preflight-failure', 'after-registration-failure', 'sqlite-nonbusy'} else 'success')
    assert observed['status'] == expected and not observed['capacity_held'], (observed['status'], observed.get('intended_status'), observed.get('error'))
    if name == 'finalizer-signals':
        assert value['published'] and value['published']['status'] == 'success', 'final receipt stale or absent'
    if name == 'sqlite-nonbusy':
        assert 'no such table' in observed.get('error', ''), 'non-lock error was masked'
    should_start = name not in {'launch-before-registration', 'expired-preflight', 'preflight-failure',
                                 'cancel-before-registration', 'cancel-after-registration', 'after-registration-failure',
                                 'sqlite-nonbusy', 'sqlite-queue-deadline', 'sqlite-cancel'}
    assert marker.exists() == should_start, 'unexpected command marker'
    if name in {'remaining-budget', 'expired-preflight', 'preflight-failure'}:
        preflight = value['events'][0]['during_preflight']
        assert preflight['started_at'] == preflight['lifecycle']['admitted_at']
        assert preflight['deadlines']['execution'] == preflight['started_at'] + execution_seconds
        assert value['published']['started_at'] == preflight['started_at']
        assert observed['duration_seconds'] >= .8, 'preflight missing from execution duration'
    return {'status': observed['status'], 'capacity_held': observed['capacity_held'],
            'marker_exists': marker.exists(), 'events': [list(event) for event in value['events']],
            'raw_worker': str(output / 'worker.json')}


def adaptive_admission(root, output, case):
    config, _ = installed(root)
    import queue_core as core
    import queue_lifecycle as lifecycle
    import runner
    assert config.get('adaptive_capacity'), 'fixture requires a disposable adaptive install'
    operations = {}
    observations = []
    original_attempt = core.attempt_task_start
    original_probe = subprocess.check_output
    original_admitted = lifecycle.admitted
    signals = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}

    def reserve(label):
        operation = f'{case}-{output.parent.name}-{label}'
        spec = runner.request(operation, 'admission-regression', ['/usr/bin/true'], str(Path.cwd()), 30, 30)
        with runner.database(config) as conn:
            task, created = lifecycle.reserve_operation(conn, operation, spec, config['_sha256'])
        assert created
        operations[task] = operation
        return task

    def attempt(task, sample, expire=False):
        elapsed = 10.0
        tentative = None

        def probe(argv, **kwargs):
            if argv == ['/usr/sbin/sysctl', '-n',
                        'kern.memorystatus_vm_pressure_level', 'kern.memorystatus_level']:
                return sample
            return original_probe(argv, **kwargs)

        def admitted(conn, task_id):
            nonlocal elapsed, tentative
            original_admitted(conn, task_id)
            if expire:
                tentative = lifecycle.read_task(conn, task_id)
                elapsed += .25

        def observe(conn, task_id, *args, **kwargs):
            assert task_id == task
            before = dict(conn.execute('SELECT * FROM queue WHERE id=?', (task,)).fetchone())
            result = original_attempt(conn, task_id, *args, **kwargs)
            with runner.database(config) as reader:
                after = dict(reader.execute('SELECT * FROM queue WHERE id=?', (task,)).fetchone())
                persisted = runner.snapshot(reader, config, operations[task], reconcile=False)
            observations.append({'operation': operations[task], 'sample': sample.decode(), 'admitted': result[0],
                                 'before': before, 'after': after, 'tentative': tentative, 'persisted': persisted})
            # Stop this fixture worker before launch so the test measures one admission attempt.
            raise InterruptedError('fixture observed admission')

        with patch.object(runner, 'time', wraps=time) as clock, \
             patch.object(subprocess, 'check_output', probe), \
             patch.object(lifecycle, 'admitted', admitted), \
             patch.object(core, 'attempt_task_start', observe):
            clock.monotonic.side_effect = lambda: elapsed
            clock.clock_gettime.side_effect = lambda clock_id: elapsed
            runner.worker(config, operations[task])
        assert observations and observations[-1]['operation'] == operations[task], 'worker never reached admission'
        return observations[-1]

    def assert_waiting(value):
        persisted = value['persisted']
        assert not value['admitted'] and persisted['status'] == 'queued', (
            f"{persisted['operation_id']} committed an unexpected admission")
        assert persisted['started_at'] is None and persisted['deadlines']['execution'] is None, persisted
        assert value['after'] == value['before'], 'aborted admission changed the persisted queue row'

    try:
        older, newer = reserve('older'), reserve('newer')
        normal, warning = b'1\n80\n', b'2\n80\n'
        if case == 'adaptive-fifo':
            newer_first = attempt(newer, normal)
            older_warning = attempt(older, warning)
            assert_waiting(newer_first)
            assert older_warning['admitted'], older_warning
            raw_older, raw_newer = reserve('raw-older'), reserve('raw-newer')
            with runner.database(config) as conn:
                assert original_attempt(conn, raw_newer, 'heavy', {'heavy': 2}, os.getpid())[0]
                assert lifecycle.read_task(conn, raw_older)['status'] == 'queued'
        else:
            with runner.database(config) as conn:
                assert original_attempt(conn, older, 'heavy', {'heavy': 1}, os.getpid())[0]
            expired_second = attempt(newer, normal, expire=True)
            assert expired_second['tentative']['lifecycle']['admitted_at']
            assert_waiting(expired_second)
            with runner.database(config) as conn:
                lifecycle.close_task(conn, older, never_started=True)
            expired_first = attempt(reserve('first'), normal, expire=True)
            assert expired_first['admitted'] and expired_first['persisted']['started_at'], expired_first
    finally:
        (output / 'attempts.json').write_text(json.dumps(observations, indent=2) + '\n')
        for sig, handler in signals.items():
            signal.signal(sig, handler)
        with runner.database(config) as conn:
            for task in operations:
                lifecycle.close_task(conn, task, never_started=True)
    if case == 'adaptive-fifo':
        return {'newer_with_normal_waited': True, 'older_with_warning_admitted': True, 'raw_order_unchanged': True}
    return {'expired_second_rolled_back': True, 'expired_first_admitted': True}


def active_state_replay(root, output):
    config, python = installed(root)
    cli = Path(config['_path']).parent / 'bundle/scripts/mac_work.py'
    archive = Path(config['_path']).parent / 'build/upstream.tar.gz'
    results = []
    for damage in ('empty', 'missing-table', 'missing-policy'):
        private = output / damage
        with (output / (damage + '-install.log')).open('w') as log:
            subprocess.run([python, '-I', '-B', str(cli), 'install', '--root', str(private),
                '--release', 'damaged-state', '--archive', str(archive), '--json'],
                stdout=log, stderr=log, check=True, timeout=60)
        marker = output / (damage + '-marker')
        args = ['run', '--id', 'must-not-replay', '--owner', 'regression',
                '--worktree', str(Path.cwd()), '--wait-seconds', '20', '--json', '--',
                '/bin/sh', '-c', 'printf x >> "$1"', 'fixture', str(marker)]
        first = invoke(private, *args)
        assert first['status'] == 'success' and not first['capacity_held'], first
        end = time.monotonic() + 10
        while True:
            with (private / 'activation.lock').open('a') as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    assert time.monotonic() < end, 'worker did not finish'
            time.sleep(.025)
        db = private / 'state/queue.db'
        (output / (damage + '-original.sqlite')).write_bytes(db.read_bytes())
        if damage == 'empty':
            db.write_bytes(b'')
        else:
            with closing(sqlite3.connect(db)) as conn:
                with conn:
                    conn.execute('DROP TABLE task_operations' if damage == 'missing-table' else 'DELETE FROM admission_policy')
        damaged = db.read_bytes()
        (output / (damage + '-damaged.sqlite')).write_bytes(damaged)
        refusal = subprocess.run([str(private / 'bin/mac-work'), *args], text=True,
                                 capture_output=True, timeout=15)
        assert refusal.returncode == 2 and 'missing/incompatible' in refusal.stderr, refusal.stderr
        assert db.read_bytes() == damaged, 'refusal mutated damaged state'
        assert marker.read_text() == 'x', 'same operation replayed'
        result = {'damage': damage, 'refused': True, 'marker_count': 1,
                  'bytes_preserved': True, 'stderr': refusal.stderr}
        results.append(result)
    return {'variants': results, 'damaged_roots_retained': True}


CASES = {'python-environment': python_environment, 'active-state-replay': active_state_replay,
         'adaptive-fifo': lambda root, output: adaptive_admission(root, output, 'adaptive-fifo'),
         'adaptive-expiry': lambda root, output: adaptive_admission(root, output, 'adaptive-expiry'),
         'sqlite-contention': lambda root, output: worker_case(root, output, 'sqlite-contention'),
         'launch-before-registration': lambda root, output: worker_case(root, output, 'launch-before-registration'),
         'finalizer-signals': lambda root, output: worker_case(root, output, 'finalizer-signals'),
         **{name: (lambda root, output, name=name: worker_case(root, output, name))
            for name in ('sqlite-nonbusy', 'sqlite-queue-deadline', 'sqlite-cancel',
                         'remaining-budget', 'expired-preflight', 'preflight-failure',
                         'cancel-before-registration', 'cancel-after-registration', 'after-registration-failure')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES, action='append', required=True)
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    args = parser.parse_args()
    selected = json.loads((args.root / 'current.json').read_text())
    runtime = Path(json.loads(Path(selected['configuration']).read_text())['runtime'])
    if Path(sys.prefix) != runtime:
        os.execv(str(runtime / 'bin/python'), [str(runtime / 'bin/python'), '-I', '-B',
                 str(Path(__file__).resolve()), *sys.argv[1:]])
    if args.worker:
        fault_worker(args.root.resolve(), args.output, args.case[0], args.worker)
        return 0
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    for name in args.case:
        directory = args.output / name
        directory.mkdir()
        try:
            value = {'case': name, 'verdict': 'passed', 'details': CASES[name](args.root.resolve(), directory)}
        except Exception as error:
            value = {'case': name, 'verdict': 'failed', 'error': repr(error)}
        results.append(value)
        print(json.dumps(value), flush=True)
    (args.output / 'verdicts.json').write_text(json.dumps(results, indent=2) + '\n')
    return int(any(v['verdict'] != 'passed' for v in results))


if __name__ == '__main__':
    sys.exit(main())
