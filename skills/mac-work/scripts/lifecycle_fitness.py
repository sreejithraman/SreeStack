"""Exercise repaired upstream ownership through actual CLI/MCP client processes.

Automatic process-group availability and conservative uncontained quarantine are
separate assertions. A policy pass never establishes arbitrary-descendant cleanup.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time

from fitness import CASES, SCRIPTS, Scenario, assertions, wait_for


class LifecycleScenario(Scenario):
    def __init__(self, runtime, scratch, proof, name, contract, repaired):
        super().__init__(runtime, scratch, proof, name)
        self.contract = contract
        self.repaired = repaired

    def launch(self, argv, peer=False):
        if self.repaired:
            if Path(argv[0]).name == 'tq':
                argv = [argv[0], '--ownership-contract', self.contract, *argv[1:]]
            elif peer:
                argv = [*argv, self.contract]
        return super().launch(argv, peer)

    def task(self, operation, task):
        result = subprocess.run([str(self.runtime / 'bin/tq'), '--data-dir', str(self.state),
                                 operation, str(task), '--json'], env=self.env,
                                capture_output=True, text=True, check=True, timeout=10)
        value = json.loads(result.stdout)
        self.transcript.append({'cli': operation, 'task_id': task, 'result': value})
        return value


def policy(s, name):
    if name == 'cli-durable-read':
        import re
        first = s.cli('first')
        code = first.wait(timeout=8)
        text = (s.proof / 'process-0.log').read_text()
        task = int(re.search(r'Task #(\d+) queued', text).group(1))
        completed = s.task('status', task)
        later = s.task('status', task)
        second = s.cli('second', 15, 'linger', 20)
        wait_for(lambda: s.event('second', 'descendant_ready'))
        active = next(t for t in s.listing() if t['pid'] == second.pid)
        cancelled = s.task('cancel', active['id'])
        second.wait(timeout=8)
        reread = s.task('status', active['id'])
        count = sum(e['token'] == 'first' and e['event'] == 'start' for e in s.events())
        return {'exit': code, 'completed': completed['status'], 'fresh_read': later['status'],
                'cancel': cancelled['status'], 'late_cancel_read': reread['status'], 'start_count': count}, code == 0 and completed['status'] == later['status'] == 'success' and cancelled['status'] == reread['status'] == 'cancelled' and count == 1 and not s.live_descendant('second')
    if name == 'no-force-clear':
        first = s.cli('first', 15)
        wait_for(lambda: s.event('first', 'start'))
        result = subprocess.run([str(s.runtime / 'bin/tq'), '--data-dir', str(s.state), 'clear', '--json'], env=s.env, capture_output=True, text=True, timeout=8)
        retained = s.listing()
        ok = result.returncode != 0 and 'Bulk clearing is disabled' in result.stderr and len(retained) == 1
        s.task('cancel', retained[0]['id'])
        first.wait(timeout=8)
        return {'exit': result.returncode, 'row_retained': len(retained) == 1, 'error': result.stderr.strip()}, ok
    if name == 'corrupt-init':
        import hashlib
        s.state.mkdir()
        database = s.state / 'queue.db'
        database.write_bytes(b'not a SQLite database; preserve these bytes')
        before = hashlib.sha256(database.read_bytes()).hexdigest()
        process = s.cli('never')
        code = process.wait(timeout=8)
        after = hashlib.sha256(database.read_bytes()).hexdigest()
        return {'exit': code, 'bytes_preserved': before == after}, code != 0 and before == after and not s.event('never', 'start')
    if name == 'identity-mismatch':
        a = s.peer()
        first = s.submit(a, 'first', 15, 'linger', 20)['task_id']
        wait_for(lambda: s.event('first', 'descendant_ready'))
        with sqlite3.connect(s.state / 'queue.db') as conn:
            metadata = json.loads(conn.execute('SELECT lifecycle_json FROM queue WHERE id=?', (first,)).fetchone()[0])
            metadata['child']['birth'] = [0, 0]
            conn.execute('UPDATE queue SET lifecycle_json=? WHERE id=?', (json.dumps(metadata), first))
        result = s.call(a, 'cancel_task', task_id=first)
        live = s.live_descendant('first')
        return {'status': result['status'], 'capacity_held': result.get('capacity_held'), 'unverified_group_left_alive': live}, result['status'] == 'recovery-pending' and result['capacity_held'] and live
    if name in {'quarantine-cancel', 'quarantine-crash', 'quarantine-success', 'quarantine-no-release', 'group-recovery'}:
        a = s.peer()
        mode = 'exit-linger' if name in {'quarantine-success', 'group-recovery'} else 'detach'
        first = s.submit(a, 'first', 15, mode, 20)['task_id']
        wait_for(lambda: s.event('first', 'descendant_ready'))
        if name == 'quarantine-crash':
            row = next(t for t in s.listing() if t['id'] == first)
            os.kill(row['pid'], signal.SIGKILL)
        elif mode != 'exit-linger':
            s.call(a, 'cancel_task', task_id=first)
        b = s.peer()
        second = s.submit(b, 'second')['task_id']
        pending = wait_for(lambda: (x if (x := s.status(b, first))['status'] not in {'queued', 'running'} else None))
        time.sleep(.25)
        queued = s.status(b, second)
        live = s.live_descendant('first')
        starts = sum(e['token'] == 'first' and e['event'] == 'start' for e in s.events())
        ok = pending.get('capacity_held', False) and pending['status'] == 'recovery-pending' and queued['status'] == 'queued' and live and starts == 1 and not s.event('second', 'start')
        details = {'first_status': pending['status'], 'capacity_held': pending.get('capacity_held'),
                   'successor_status': queued['status'], 'descendant_alive': live, 'first_start_count': starts}
        if name in {'quarantine-no-release', 'group-recovery'}:
            leaf = s.event('first', 'descendant_start')
            os.kill(leaf['pid'], signal.SIGKILL)
            wait_for(lambda: not s.live_descendant('first'))
            if name == 'group-recovery':
                wait_for(lambda: s.event('second', 'start'))
                final = s.terminal(b, second)
                recovered = s.status(b, first)
                ok = ok and recovered['status'] == 'success' and not recovered['capacity_held'] and final['status'] == 'success'
                details.update(after_verified_group_closure=recovered['status'], successor_after_closure=final['status'])
            else:
                later = s.peer()
                retained = s.status(later, first)
                ok = ok and retained['status'] == 'recovery-pending' and s.status(later, second)['status'] == 'queued'
                details['after_group_empty'] = retained['status']
        s.call(b, 'cancel_task', task_id=second)
        return details, ok
    if name == 'foreground-quarantine':
        a = s.peer()
        first = s.submit(a, 'first')['task_id']
        wait_for(lambda: s.event('first', 'end'))
        status = wait_for(lambda: (x if (x := s.status(a, first))['status'] not in {'queued', 'running'} else None))
        return {'status': status['status'], 'capacity_held': status.get('capacity_held')}, status['status'] == 'recovery-pending' and status.get('capacity_held')
    if name == 'config-mismatch':
        prime = s.cli('first')
        if prime.wait(timeout=8) != 0:
            raise RuntimeError('group policy primer failed')
        result = subprocess.run([str(s.runtime / 'bin/tq'), '--data-dir', str(s.state),
                                 '--queue-capacity', 'heavy=2', '--ownership-contract', s.contract,
                                 'run', '-q', 'heavy/client', *s.job('wrong')],
                                env=s.env, capture_output=True, text=True, timeout=8)
        return {'exit': result.returncode, 'error': result.stderr.strip()}, result.returncode != 0 and 'configuration mismatch' in result.stderr and not s.event('wrong', 'start')
    if name == 'queue-deadline':
        a = s.peer()
        first = s.submit(a, 'first', 3)['task_id']
        wait_for(lambda: s.event('first', 'start'))
        second = s.call(a, 'run_task', command=__import__('shlex').join(s.job('second')),
                        working_directory=str(s.directory), queue_name='heavy/mcp',
                        timeout_seconds=1, queue_timeout_seconds=1, wait_seconds=0)['task_id']
        done = s.terminal(a, second)
        s.terminal(a, first)
        return {'status': done['status'], 'error': done.get('error'), 'second_started': bool(s.event('second', 'start'))}, done['status'] == 'error' and 'Queue wait deadline' in done['error'] and not s.event('second', 'start')
    if name == 'boot-recovery-fixture':
        a = s.peer()
        first = s.submit(a, 'first')['task_id']
        wait_for(lambda: s.event('first', 'end'))
        wait_for(lambda: s.status(a, first)['status'] == 'recovery-pending')
        # Fixture models an offline database from a prior boot; no reboot or live state changes.
        with sqlite3.connect(s.state / 'queue.db') as conn:
            metadata = json.loads(conn.execute('SELECT lifecycle_json FROM queue WHERE id=?', (first,)).fetchone()[0])
            metadata['boot'] = '00000000-0000-0000-0000-000000000000'
            conn.execute('UPDATE queue SET lifecycle_json=? WHERE id=?', (json.dumps(metadata), first))
        fresh = s.peer()
        recovered = s.status(fresh, first)
        second = s.submit(fresh, 'second')['task_id']
        wait_for(lambda: s.event('second', 'end'))
        return {'old_boot_fixture': True, 'prior_task_status': recovered['status'], 'prior_capacity_held': recovered['capacity_held'], 'new_command_started': bool(s.event('second', 'start'))}, recovered['status'] == 'success' and not recovered['capacity_held'] and bool(s.event('second', 'start'))
    raise ValueError(name)


POLICIES = ('cli-durable-read', 'no-force-clear', 'corrupt-init', 'identity-mismatch', 'quarantine-cancel', 'quarantine-crash', 'quarantine-success', 'quarantine-no-release',
            'foreground-quarantine', 'group-recovery', 'config-mismatch', 'queue-deadline', 'boot-recovery-fixture')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--original', action='store_true', help='baseline counterexample: no local repair flags')
    parser.add_argument('--contract', choices=['uncontained', 'process-group'], default='uncontained')
    parser.add_argument('--case', choices=CASES + POLICIES, action='append', required=True)
    args = parser.parse_args()
    if args.original:
        from fitness import verify_runtime
    else:
        from build_runtime import verify_runtime
    identity = verify_runtime(args.runtime.resolve())
    identity['harness'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in SCRIPTS.glob('*.py') if not p.name.startswith('test_')}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'runtime.json').write_text(json.dumps(identity, indent=2) + '\n')
    results = []
    with tempfile.TemporaryDirectory(prefix='mac-work-policy-') as scratch:
        for name in args.case:
            s = LifecycleScenario(args.runtime.resolve(), Path(scratch), args.output, name, args.contract, not args.original)
            try:
                details, passed = policy(s, name) if name in POLICIES else assertions(s, name)
                verdict = 'passed' if passed else 'failed'
            except Exception as error:
                details, verdict = {'error': str(error)}, 'blocked'
            finally:
                s.close()
            value = {'case': name, 'expectation': ('quarantine-policy' if name.startswith(('quarantine', 'foreground')) or name == 'identity-mismatch'
                                     else 'refusal' if name in {'corrupt-init', 'config-mismatch', 'no-force-clear'}
                                     else 'changed-boot-fixture' if name == 'boot-recovery-fixture'
                                     else 'bounded-availability'),
                     'contract': args.contract, 'verdict': verdict, 'details': details}
            results.append(value)
            print(json.dumps(value), flush=True)
    (args.output / 'verdicts.json').write_text(json.dumps(results, indent=2) + '\n')
    return 2 if any(r['verdict'] == 'blocked' for r in results) else int(any(r['verdict'] == 'failed' for r in results))


if __name__ == '__main__':
    sys.exit(main())
