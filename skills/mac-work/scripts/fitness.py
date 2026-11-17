"""Qualify pinned upstream through real CLI and MCP processes in private state.

Exit 0 means every assertion passed, 1 means a safety counterexample, and 2
means setup/observation could not establish a verdict. Never touches live queues.
"""

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import selectors
import re
import signal
import subprocess
import sys
import tempfile
import time

SCRIPTS = Path(__file__).resolve().parent
PIN = {
    'queue_core.py': 'bf23264e5cacca81a16ad48b596c0810d90a3c18e94fd44bca3af0af20e8b8d3',
    'tq.py': '946022175b64d1c7bdbdd735461192c5528dcce52c011561530966ee3bbf3d9d',
    'task_queue.py': 'b2c7a62182ae0c7e34596515778797b9391de444675ad420ed4fb315a4efba5d',
}


def wait_for(check, seconds=8):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if result := check():
            return result
        time.sleep(.025)
    raise TimeoutError('observation deadline expired')


def read_message(process, seconds=15):
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        if not selector.select(seconds):
            raise TimeoutError('MCP peer response deadline expired')
        line = process.stdout.readline()
    if not line:
        raise RuntimeError(f'MCP peer exited {process.poll()}')
    return json.loads(line)


def verify_runtime(runtime):
    code = """import importlib.metadata as m, importlib.util as u, json, re
print(json.dumps({'python': __import__('sys').version.split()[0],
 'queue': m.version('agent-task-queue'),
 'packages': {re.sub(r'[-_.]+','-', d.metadata['Name']).lower(): d.version for d in m.distributions()},
 'files': {n: u.find_spec(n).origin for n in ('queue_core','tq','task_queue')}}))"""
    result = subprocess.run([str(runtime / 'bin/python'), '-I', '-c', code],
                            text=True, capture_output=True, check=True, timeout=10)
    info = json.loads(result.stdout)
    expected = dict(re.findall(r'^([a-z0-9-]+)==(\S+)', (SCRIPTS / 'runtime.lock').read_text(), re.M))
    mismatch = any(info['packages'].get(name) != version for name, version in expected.items())
    if not info['python'].startswith('3.12.') or info['queue'] != '0.4.1' or mismatch:
        raise ValueError('runtime version mismatch; recreate from runtime.lock with Python 3.12')
    for name, digest in PIN.items():
        if hashlib.sha256(Path(info['files'][name[:-3]]).read_bytes()).hexdigest() != digest:
            raise ValueError(f'upstream hash mismatch: {name}; refuse unverified runtime')
    return info


class Scenario:
    def __init__(self, runtime, scratch, proof, name):
        self.runtime = runtime
        self.directory = scratch / name
        self.directory.mkdir()
        self.state = self.directory / 'queue'
        self.events_file = self.directory / 'events.jsonl'
        self.proof = proof / name
        self.proof.mkdir()
        self.processes = []
        self.streams = []
        self.transcript = []
        self.env = {'PATH': os.defpath, 'HOME': str(self.directory),
                    'TASK_QUEUE_POLL_WAITING': '.05', 'PYTHONUNBUFFERED': '1'}

    def launch(self, argv, peer=False):
        log = open(self.proof / f'process-{len(self.processes)}.log', 'w')
        self.streams.append(log)
        process = subprocess.Popen(argv, cwd=self.directory, env=self.env,
                                   stdin=subprocess.PIPE if peer else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE if peer else log, stderr=log, text=True)
        self.processes.append(process)
        self.transcript.append({'argv': argv, 'pid': process.pid})
        return process

    def events(self):
        if not self.events_file.exists():
            return []
        return [json.loads(line) for line in self.events_file.read_text().splitlines()]

    def event(self, token, event):
        return next((e for e in self.events() if e['token'] == token and e['event'] == event), None)

    def job(self, token, duration=0.1, mode='normal'):
        return [str(self.runtime / 'bin/python'), str(SCRIPTS / 'probe_job.py'),
                str(self.events_file), token, mode, str(duration)]

    def cli(self, token, duration=.1, mode='normal', timeout=10, queue='heavy/client'):
        return self.launch([str(self.runtime / 'bin/tq'), '--data-dir', str(self.state),
                            '--queue-capacity', 'heavy=1', 'run', '-q', queue,
                            '-t', str(timeout), *self.job(token, duration, mode)])

    def listing(self):
        result = subprocess.run([str(self.runtime / 'bin/tq'), '--data-dir', str(self.state),
                                 'list', '--json'], env=self.env, capture_output=True,
                                text=True, check=True, timeout=10)
        return json.loads(result.stdout)['tasks']

    def peer(self):
        process = self.launch([str(self.runtime / 'bin/python'), str(SCRIPTS / 'mcp_peer.py'),
                               str(self.runtime), str(self.state)], peer=True)
        if read_message(process) != {'ready': True}:
            raise RuntimeError('MCP client did not connect')
        return process

    def call(self, peer, tool, **arguments):
        request = {'tool': tool, 'arguments': arguments}
        self.transcript.append(request)
        peer.stdin.write(json.dumps(request) + '\n')
        peer.stdin.flush()
        response = read_message(peer)
        self.transcript.append(response)
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response['result']

    def submit(self, peer, token, duration=.1, mode='normal', timeout=10):
        import shlex
        return self.call(peer, 'run_task', command=shlex.join(self.job(token, duration, mode)),
                         working_directory=str(self.directory), queue_name='heavy/mcp',
                         timeout_seconds=timeout, wait_seconds=0, agent_name='fitness')

    def status(self, peer, task):
        return self.call(peer, 'task_status', task_id=task, wait_seconds=0)

    def terminal(self, peer, task):
        return wait_for(lambda: (value if (value := self.status(peer, task))['status']
                                in {'success', 'failed', 'cancelled', 'timeout', 'error', 'unknown'}
                                else None))

    def live_descendant(self, token):
        event = self.event(token, 'descendant_start')
        if not event:
            raise RuntimeError('descendant never started')
        result = subprocess.run(['ps', '-p', str(event['pid']), '-o', 'stat=,args='],
                                capture_output=True, text=True, timeout=5)
        self.transcript.append({'observation': 'descendant_identity', 'token': token,
                                'pid': event['pid'], 'time': time.monotonic(),
                                'ps_exit': result.returncode, 'ps_output': result.stdout.strip()})
        return result.returncode == 0 and 'probe_job.py' in result.stdout and not result.stdout.lstrip().startswith('Z')

    def close(self):
        # A group number alone is insufficient if its old processes already exited.
        identities = subprocess.run(['ps', '-axo', 'pgid=,args='], capture_output=True,
                                    text=True, check=True, timeout=5).stdout.splitlines()
        owned_groups = {int(line.split(None, 1)[0]) for line in identities
                        if str(self.events_file) in line and str(SCRIPTS / 'probe_job.py') in line}
        recorded_groups = {event['pgid'] for event in self.events()}
        for group in owned_groups & recorded_groups - {os.getpgrp()}:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(group, signal.SIGKILL)
        for process in self.processes:
            if process.poll() is None and process.stdin:
                with contextlib.suppress(BrokenPipeError):
                    process.stdin.write('{"tool":"close"}\n')
                    process.stdin.flush()
        for process in reversed(self.processes):
            try:
                process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=4)
        for stream in self.streams:
            stream.close()
        (self.proof / 'events.json').write_text(json.dumps(self.events(), indent=2) + '\n')
        (self.proof / 'transcript.json').write_text(json.dumps(self.transcript, indent=2) + '\n')


def assertions(s, name):
    if name in {'atomic-cold-start', 'atomic-admission'}:
        if name == 'atomic-admission':
            primer = s.cli('primer')
            if primer.wait(timeout=8) != 0:
                raise RuntimeError('private database initialization failed')
        processes = [s.cli(str(i), .25, queue=f'heavy/client-{i}') for i in range(4)]
        codes = [p.wait(timeout=12) for p in processes]
        events = [e for e in s.events() if e['token'] != 'primer']
        active = 0
        peak = 0
        for event in sorted(events, key=lambda e: e['time']):
            active += 1 if event['event'] == 'start' else -1
            peak = max(peak, active)
        return {'codes': codes, 'peak': peak}, codes == [0] * 4 and peak == 1 and len(events) == 8
    if name == 'wait-vs-execution':
        first = s.cli('first', 2)
        wait_for(lambda: s.event('first', 'start'))
        second = s.cli('second', .1, timeout=1)
        codes = [first.wait(timeout=8), second.wait(timeout=8)]
        gap = s.event('second', 'start')['time'] - s.event('first', 'start')['time']
        return {'codes': codes, 'queued_seconds_at_least': gap}, codes == [0, 0] and gap >= 1.8
    if name == 'execution-timeout':
        first = s.cli('first', 5, timeout=1)
        wait_for(lambda: s.event('first', 'start'))
        second = s.cli('second')
        codes = [first.wait(timeout=8), second.wait(timeout=8)]
        return {'codes': codes, 'first_end': s.event('first', 'end')}, codes == [124, 0] and not s.event('first', 'end')
    if name == 'cancel-queued':
        first = s.cli('first', 2)
        wait_for(lambda: s.event('first', 'start'))
        second = s.cli('second')
        wait_for(lambda: any(t['pid'] == second.pid and t['status'] == 'waiting' for t in s.listing()))
        second.terminate()
        codes = [first.wait(timeout=8), second.wait(timeout=8)]
        return {'codes': codes, 'second_started': bool(s.event('second', 'start'))}, codes == [0, 130] and not s.event('second', 'start')
    if name in {'cli-cancel-running', 'cli-crash', 'cli-success-lingering'}:
        mode = 'exit-linger' if name == 'cli-success-lingering' else 'linger'
        first = s.cli('first', 15, mode, timeout=20)
        wait_for(lambda: s.event('first', 'descendant_ready'))
        if name == 'cli-cancel-running':
            first.terminate()
        elif name == 'cli-crash':
            first.kill()
        first.wait(timeout=8)
        second = s.cli('second')
        wait_for(lambda: s.event('second', 'start'))
        alive = s.live_descendant('first')
        second.wait(timeout=5)
        return {'first_exit': first.returncode, 'second_started_while_descendant_alive': alive}, not alive
    if name == 'mixed-client-wait':
        peer = s.peer()
        first = s.cli('first', 2)
        wait_for(lambda: s.event('first', 'start'))
        second = s.submit(peer, 'second', .1, timeout=1)['task_id']
        wait_for(lambda: s.status(peer, second)['status'] == 'queued')
        done = s.terminal(peer, second)
        gap = s.event('second', 'start')['time'] - s.event('first', 'start')['time']
        later_peer = s.peer()
        reread = s.status(later_peer, second)
        starts = sum(e['event'] == 'start' and e['token'] == 'second' for e in s.events())
        return {'cli_exit': first.wait(timeout=5), 'mcp_status': done['status'],
                'queue_wait_at_least': gap, 'fresh_server_read': reread['status'],
                'mcp_start_count': starts}, first.returncode == 0 and done['status'] == reread['status'] == 'success' and gap > 1.8 and starts == 1
    if name == 'mcp-execution-timeout':
        peer = s.peer()
        first = s.submit(peer, 'first', 5, timeout=1)['task_id']
        done = s.terminal(peer, first)
        second = s.cli('second')
        code = second.wait(timeout=5)
        return {'mcp_status': done['status'], 'cli_exit': code}, done['status'] == 'timeout' and code == 0 and not s.event('first', 'end')
    if name == 'mcp-cancel-and-read':
        a, b = s.peer(), s.peer()
        first = s.submit(a, 'first', 15, 'linger', 20)['task_id']
        wait_for(lambda: s.event('first', 'descendant_ready'))
        second = s.submit(b, 'second')['task_id']
        wait_for(lambda: s.status(b, second)['status'] == 'queued')
        cancelled = s.call(b, 'cancel_task', task_id=second)
        running_cancel = s.call(a, 'cancel_task', task_id=first)
        survivor = s.live_descendant('first')
        third = s.submit(b, 'third')['task_id']
        done = s.terminal(b, third)
        reread = s.status(b, third)
        starts = sum(e['event'] == 'start' and e['token'] == 'third' for e in s.events())
        details = {'queued_cancel': cancelled['status'], 'running_cancel': running_cancel['status'],
                   'descendant_survived': survivor, 'third_status': done['status'],
                   'late_read_status': reread['status'], 'third_start_count': starts,
                   'cancelled_started': bool(s.event('second', 'start'))}
        return details, cancelled['status'] == running_cancel['status'] == 'cancelled' and not survivor and done['status'] == reread['status'] == 'success' and starts == 1 and not s.event('second', 'start')
    if name in {'mcp-crash-restart', 'mcp-cancel-detached', 'mcp-success-lingering'}:
        a = s.peer()
        mode = {'mcp-crash-restart': 'linger', 'mcp-cancel-detached': 'detach',
                'mcp-success-lingering': 'exit-linger'}[name]
        first = s.submit(a, 'first', 15, mode, 20)['task_id']
        wait_for(lambda: s.event('first', 'descendant_ready'))
        if name == 'mcp-crash-restart':
            row = next(t for t in s.listing() if t['id'] == first)
            os.kill(row['pid'], signal.SIGKILL)
            wait_for(lambda: not subprocess.run(['ps', '-p', str(row['pid']), '-o', 'pid='], capture_output=True).stdout.strip())
        elif name == 'mcp-cancel-detached':
            s.call(a, 'cancel_task', task_id=first)
        else:
            s.terminal(a, first)
        b = s.peer()
        second = s.submit(b, 'second')['task_id']
        wait_for(lambda: s.event('second', 'start'))
        alive = s.live_descendant('first')
        done = s.terminal(b, second)
        prior = s.status(b, first)
        return {'second_started_while_descendant_alive': alive, 'second_status': done['status'],
                'old_task_after_restart': prior['status']}, not alive and done['status'] == 'success'
    raise ValueError(name)


CASES = ('atomic-cold-start', 'atomic-admission', 'wait-vs-execution', 'execution-timeout', 'cancel-queued',
         'cli-cancel-running', 'cli-crash', 'cli-success-lingering', 'mixed-client-wait',
         'mcp-execution-timeout', 'mcp-cancel-and-read',
         'mcp-crash-restart', 'mcp-cancel-detached', 'mcp-success-lingering')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True, help='private Python 3.12 venv from runtime.lock')
    parser.add_argument('--output', type=Path, required=True, help='new retained proof directory')
    parser.add_argument('--case', choices=CASES, action='append', help='default: all gates')
    args = parser.parse_args()
    try:
        runtime = args.runtime.resolve()
        identity = verify_runtime(runtime)
        identity['harness'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in SCRIPTS.glob('*.py') if not p.name.startswith('test_')}
        identity['lock_sha256'] = hashlib.sha256((SCRIPTS / 'runtime.lock').read_bytes()).hexdigest()
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'runtime.json').write_text(json.dumps(identity, indent=2) + '\n')
        results = []
        with tempfile.TemporaryDirectory(prefix='mac-work-gate-') as directory:
            for name in args.case or CASES:
                scenario = Scenario(runtime, Path(directory), args.output, name)
                try:
                    details, passed = assertions(scenario, name)
                    verdict = 'passed' if passed else 'failed'
                except Exception as error:
                    details, verdict = {'error': str(error)}, 'blocked'
                finally:
                    scenario.close()
                result = {'case': name, 'verdict': verdict, 'details': details}
                results.append(result)
                print(json.dumps(result), flush=True)
        (args.output / 'verdicts.json').write_text(json.dumps(results, indent=2) + '\n')
        return 2 if any(r['verdict'] == 'blocked' for r in results) else int(any(r['verdict'] == 'failed' for r in results))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f'Fitness setup refused: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
