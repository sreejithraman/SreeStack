"""Real canonical CLI/MCP proof in an explicitly installed task-owned root."""

import argparse
import contextlib
import hashlib
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time

from fitness import read_message, wait_for

SCRIPTS = Path(__file__).resolve().parent


class Pilot:
    def __init__(self, root, proof, worktree):
        self.root, self.proof, self.worktree = root.resolve(), proof, worktree.resolve()
        self.cli = str(self.root / 'bin/mac-work')
        pointer = json.loads((self.root / 'current.json').read_text())
        config = json.loads(Path(pointer['configuration']).read_text())
        self.python = str(Path(config['runtime']) / 'bin/python')
        self.events_path = proof / 'events.jsonl'
        self.peers = []
        self.logs = []
        self.transcript = []
        self.counter = 0
        self.operations = set()
        self.prefix = hashlib.sha256(str(proof).encode()).hexdigest()[:8]

    def operation(self, label, duration=.1, mode='normal'):
        self.counter += 1
        name = f'{self.prefix}-{label}-{self.counter}'
        self.operations.add(name)
        return {'operation_id': name, 'owner': 'runner-proof', 'worktree': str(self.worktree),
                'argv': [self.python, str(SCRIPTS / 'probe_job.py'), str(self.events_path), name, mode, str(duration)],
                'queue_seconds': 20, 'execution_seconds': 20}

    def argv(self, spec, wait=0):
        return [self.cli, 'run', '--id', spec['operation_id'], '--owner', spec['owner'],
                '--worktree', spec['worktree'], '--queue-seconds', str(spec['queue_seconds']),
                '--execution-seconds', str(spec['execution_seconds']), '--wait-seconds', str(wait),
                '--json', '--', *spec['argv']]

    def invoke(self, argv, expected=0):
        result = subprocess.run(argv, text=True, capture_output=True, timeout=35)
        self.transcript.append({'argv': argv, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode != expected:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(result.stdout) if expected == 0 else result.stderr

    def run(self, spec, wait=0):
        return self.invoke(self.argv(spec, wait))

    def status(self, name):
        return self.invoke([self.cli, 'status', '--id', name, '--json'])

    def cancel(self, name):
        return self.invoke([self.cli, 'cancel', '--id', name, '--json'])

    def terminal(self, name):
        return wait_for(lambda: (v if (v := self.status(name))['status'] not in {'queued', 'running'} else None), 30)

    def events(self):
        return [json.loads(line) for line in self.events_path.read_text().splitlines()] if self.events_path.exists() else []

    def event(self, name, kind):
        return next((e for e in self.events() if e['token'] == name and e['event'] == kind), None)

    def peer(self):
        log = open(self.proof / f'peer-{len(self.peers)}.log', 'w')
        self.logs.append(log)
        process = subprocess.Popen([self.python, str(SCRIPTS / 'runner_peer.py'), str(self.root)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True,
            env={**os.environ, 'FASTMCP_CHECK_FOR_UPDATES': 'off'})
        self.peers.append(process)
        message = read_message(process, 30)
        if not message.get('ready'):
            raise RuntimeError(message)
        process.server_pid = message['server_pid']
        return process

    def call(self, peer, tool, **arguments):
        request = {'tool': tool, 'arguments': arguments}
        self.transcript.append(request)
        peer.stdin.write(json.dumps(request) + '\n'); peer.stdin.flush()
        response = read_message(peer, 30)
        self.transcript.append(response)
        if 'error' in response:
            raise ValueError(response['error'])
        return response['result']

    def root_unlocked(self):
        with (self.root/'activation.lock').open('a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return False
        return True

    def close(self):
        for operation in self.operations:
            with contextlib.suppress(Exception):self.cancel(operation)
        # This proof owns only marker-identifiable fixture groups, never shared daemons.
        output = subprocess.check_output(['/bin/ps', '-axo', 'pgid=,args='], text=True)
        for line in output.splitlines():
            if str(self.events_path) in line and 'probe_job.py' in line:
                group = int(line.strip().split(None, 1)[0])
                if group != os.getpgrp():
                    with contextlib.suppress(ProcessLookupError):os.killpg(group, signal.SIGKILL)
        for operation in self.operations:
            with contextlib.suppress(Exception):self.status(operation)
        for peer in self.peers:
            if peer.poll() is None:
                with contextlib.suppress(BrokenPipeError):
                    peer.stdin.write('{"tool":"close"}\n'); peer.stdin.flush()
                try:peer.wait(timeout=4)
                except subprocess.TimeoutExpired:peer.kill();peer.wait()
        for log in self.logs:log.close()
        (self.proof / 'transcript.json').write_text(json.dumps(self.transcript, indent=2)+'\n')


def check(p, case):
    if case == 'mixed-cap':
        peer = p.peer()
        specs = [p.operation('mixed', .3) for _ in range(4)]
        processes = [subprocess.Popen(p.argv(s), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for s in specs[:2]]
        for spec in specs[2:]:p.call(peer, 'run_command', **spec)
        for child in processes:
            out, err = child.communicate(timeout=30)
            assert child.returncode == 0, out + err
        results = [p.terminal(s['operation_id']) for s in specs]
        events = [e for e in p.events() if e['token'] in {s['operation_id'] for s in specs}]
        active = peak = 0
        for event in sorted(events, key=lambda e:e['time']):
            active += 1 if event['event'] == 'start' else -1
            peak=max(peak,active)
        assert peak == 1 and len(events)==8 and all(r['status']=='success' for r in results)
        return {'peak':peak,'statuses':[r['status'] for r in results]}
    if case == 'idempotent-race':
        spec=p.operation('race', .5)
        peer=p.peer()
        children=[subprocess.Popen(p.argv(spec),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(5)]
        values=[p.call(peer,'run_command',**spec)]
        for child in children:
            out,err=child.communicate(timeout=30);assert child.returncode==0,out+err;values.append(json.loads(out))
        done=p.terminal(spec['operation_id'])
        late=p.call(peer,'run_command',**spec)
        conflict={**spec,'owner':'different-owner'}
        error=p.invoke(p.argv(conflict),expected=2)
        assert 'conflict' in error and len({v['task_id'] for v in values})==1 and done['task_id']==late['task_id']
        starts=sum(e['token']==spec['operation_id'] and e['event']=='start' for e in p.events())
        assert starts==1
        return {'task_id':done['task_id'],'submissions':7,'starts':starts,'conflict_refused':True}
    if case == 'conflicting-race':
        spec=p.operation('conflict-race',.2)
        other={**spec,'owner':'competing-owner'}
        children=[subprocess.Popen(p.argv(v),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for v in (spec,other)]
        outcomes=[]
        for child in children:
            out,err=child.communicate(timeout=30);outcomes.append((child.returncode,out,err))
        assert sorted(v[0] for v in outcomes)==[0,2],outcomes
        result=p.terminal(spec['operation_id'])
        starts=sum(e['token']==spec['operation_id'] and e['event']=='start' for e in p.events())
        assert result['status']=='success' and starts==1
        return {'exits':sorted(v[0] for v in outcomes),'starts':starts}
    if case == 'submission-handoff-crash':
        spec=p.operation('handoff-crash',.5)
        child=subprocess.Popen(p.argv(spec,30),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        def association():
            with sqlite3.connect(p.root/'state/queue.db') as conn:
                return conn.execute('SELECT task_id,worker_json FROM task_operations WHERE operation_id=?',(spec['operation_id'],)).fetchone()
        original=wait_for(association)
        before_claim=original[1] is None
        child.kill();child.communicate(timeout=5)
        again=p.run(spec);result=p.terminal(spec['operation_id'])
        starts=sum(e['token']==spec['operation_id'] and e['event']=='start' for e in p.events())
        assert again['task_id']==result['task_id']==original[0] and starts<=1
        assert result['status'] in {'success','cancelled'}
        return {'interrupted_before_claim':before_claim,'stable_task_id':original[0],'starts':starts,'status':result['status']}
    if case == 'client-death':
        spec=p.operation('client-death',2)
        child=subprocess.Popen(p.argv(spec,30),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        wait_for(lambda:p.event(spec['operation_id'],'start'))
        child.kill();child.communicate(timeout=5)
        result=p.terminal(spec['operation_id']);again=p.run(spec)
        assert result['status']==again['status']=='success' and result['task_id']==again['task_id']
        return {'status':result['status'],'stable_task_id':again['task_id']}
    if case == 'queued-worker-death':
        holder=p.operation('queued-death-holder',3);p.run(holder);wait_for(lambda:p.event(holder['operation_id'],'start'))
        spec=p.operation('queued-worker-death');initial=p.run(spec)
        assert initial['status']=='queued'
        os.kill(initial['worker']['pid'],signal.SIGKILL)
        result=p.terminal(spec['operation_id']);again=p.run(spec)
        p.terminal(holder['operation_id'])
        assert result['status']==again['status']=='cancelled' and not p.event(spec['operation_id'],'start')
        return {'status':result['status'],'started':False,'stable_task_id':again['task_id']}
    if case == 'argv-and-environment':
        spec=p.operation('literal-argv');target=p.proof/'argv-value.txt';literal='spaces ; $HOME $(echo not-executed)'
        spec['argv']=[p.python,'-c','import pathlib,sys,json;pathlib.Path(sys.argv[1]).write_text(json.dumps(sys.argv[2:]))',str(target),literal,'--config','project.json','--config=other.json']
        previous=os.environ.get('MAC_WORK_TEST_SECRET');secret='private-fixture-value-never-dumped'
        old_queue=os.environ.get('TASK_QUEUE_DATA_DIR');ignored=p.proof/'ignored-environment-queue'
        os.environ['TASK_QUEUE_DATA_DIR']=str(ignored)
        os.environ['MAC_WORK_TEST_SECRET']=secret
        try:
            p.run(spec);result=p.terminal(spec['operation_id'])
        finally:
            if previous is None:os.environ.pop('MAC_WORK_TEST_SECRET',None)
            else:os.environ['MAC_WORK_TEST_SECRET']=previous
            if old_queue is None:os.environ.pop('TASK_QUEUE_DATA_DIR',None)
            else:os.environ['TASK_QUEUE_DATA_DIR']=old_queue
        assert not ignored.exists()
        assert result['status']=='success' and result['request']['argv']==spec['argv'] and json.loads(target.read_text())==[literal,'--config','project.json','--config=other.json']
        assert secret not in Path(result['receipt_path']).read_text() and secret not in Path(result['log_path']).read_text()
        return {'literal_argv_preserved':True,'secret_environment_not_dumped':True,'queue_environment_override_ignored':True}
    if case == 'deadlines':
        first=p.operation('holder',3);p.run(first);wait_for(lambda:p.event(first['operation_id'],'start'))
        waiting=p.operation('wait-success',.1);waiting['execution_seconds']=1
        expired=p.operation('wait-expired');expired['queue_seconds']=1
        p.run(waiting);p.run(expired)
        a=p.terminal(expired['operation_id']);b=p.terminal(waiting['operation_id'])
        timeout=p.operation('execution-timeout',5);timeout['execution_seconds']=1;p.run(timeout);c=p.terminal(timeout['operation_id'])
        assert a['status']=='queue-timeout' and not p.event(expired['operation_id'],'start') and b['status']=='success' and c['status']=='timeout'
        return {'queued_timeout':a['status'],'wait_then_execute':b['status'],'execution_timeout':c['status']}
    if case == 'cancel':
        first=p.operation('cancel-running',10,'linger');p.run(first);wait_for(lambda:p.event(first['operation_id'],'descendant_ready'))
        second=p.operation('cancel-queued');p.run(second)
        queued=p.cancel(second['operation_id']);running=p.cancel(first['operation_id'])
        a=p.terminal(first['operation_id']);b=p.terminal(second['operation_id'])
        assert a['status']==b['status']=='cancelled' and not a['capacity_held'] and not p.event(second['operation_id'],'start')
        return {'queued':b['status'],'running':a['status'],'capacity_held':a['capacity_held']}
    if case == 'worker-death':
        spec=p.operation('worker-death',10,'linger');p.run(spec);wait_for(lambda:p.event(spec['operation_id'],'descendant_ready'))
        state=p.status(spec['operation_id']);os.kill(state['worker']['pid'],signal.SIGKILL)
        after=p.terminal(spec['operation_id']);again=p.run(spec)
        next_job=p.operation('after-crash');p.run(next_job);next_result=p.terminal(next_job['operation_id'])
        assert after['status']==again['status']=='interrupted' and next_result['status']=='success'
        assert sum(e['token']==spec['operation_id'] and e['event']=='start' for e in p.events())==1
        return {'interrupted':after['status'],'repeat_task_id':again['task_id'],'successor':next_result['status']}
    if case == 'server-death':
        peer=p.peer();spec=p.operation('server-death',2);initial=p.call(peer,'run_command',**spec)
        wait_for(lambda:p.event(spec['operation_id'],'start'));os.kill(peer.server_pid,signal.SIGKILL)
        result=p.terminal(spec['operation_id']);fresh=p.peer();late=p.call(fresh,'command_status',operation_id=spec['operation_id'])
        assert result['status']==late['status']=='success' and initial['task_id']==late['task_id']
        return {'status':result['status'],'late_task_id':late['task_id']}
    if case == 'drift-refusal':
        selected=json.loads((p.root/'current.json').read_text());configuration=Path(selected['configuration'])
        config=json.loads(configuration.read_text());version=configuration.parent
        import importlib.util
        module_probe=subprocess.check_output([str(Path(config['runtime'])/'bin/python'),'-I','-c',"import importlib.util;print(importlib.util.find_spec('queue_core').origin)"],text=True).strip()
        checks=[('config',configuration,lambda b:b+b' '),
                ('patch',version/'bundle/patches/lifecycle.patch',lambda b:b+b'\n'),
                ('source-pin',version/'bundle/candidate.json',lambda b:b+b' '),
                ('runtime',Path(module_probe),lambda b:b+b'\n# isolated drift fixture\n')]
        refused=[]
        for label,path,alter in checks:
            original=path.read_bytes();spec=p.operation('drift-'+label)
            try:
                path.write_bytes(alter(original))
                error=p.invoke(p.argv(spec),expected=2)
                assert 'mismatch' in error.lower(),error
                assert not p.event(spec['operation_id'],'start')
                refused.append(label)
            finally:path.write_bytes(original)
        unexpected=version/'bundle/scripts/unlisted_source.py'
        spec=p.operation('drift-unlisted')
        try:
            unexpected.write_text('# unexpected code in a sealed version\n')
            error=p.invoke(p.argv(spec),expected=2)
            assert 'Bundle file set mismatch' in error
            refused.append('unlisted-source')
        finally:unexpected.unlink()
        wait_for(p.root_unlocked)
        database=p.root/'state/queue.db';saved=database.with_name('queue.proof-backup')
        assert not database.with_name('queue.db-wal').exists()
        spec=p.operation('drift-missing-state')
        database.rename(saved)
        try:
            error=p.invoke(p.argv(spec),expected=2)
            assert 'Shared admission database missing' in error and not database.exists()
            refused.append('missing-state')
        finally:saved.rename(database)
        valid=p.operation('after-drift');p.run(valid);assert p.terminal(valid['operation_id'])['status']=='success'
        return {'refused':refused,'restored_operation':'success'}
    if case == 'maintenance':
        if p.archive is None:raise ValueError('maintenance proof requires --archive')
        old=json.loads((p.root/'current.json').read_text());old_release=Path(old['configuration']).parent.name
        stable=p.operation('maintenance-stable');p.run(stable);before=p.terminal(stable['operation_id'])
        holder=p.operation('maintenance-holder',10);p.run(holder);wait_for(lambda:p.event(holder['operation_id'],'start'))
        error=p.invoke([p.cli,'activate','--root',str(p.root),'--release',old_release,'--json'],expected=2)
        assert 'Activation refused' in error
        blocked='blocked-'+p.prefix
        error=p.invoke([p.cli,'install','--root',str(p.root),'--release',blocked,'--archive',str(p.archive),'--json'],expected=2)
        assert 'Activation refused' in error and not (p.root/'versions'/blocked).exists()
        p.cancel(holder['operation_id']);p.terminal(holder['operation_id']);wait_for(p.root_unlocked)
        stale=p.peer();new_release='upgrade-'+p.prefix
        upgraded=p.invoke([p.cli,'install','--root',str(p.root),'--release',new_release,'--archive',str(p.archive),'--json'])
        spec=p.operation('stale-consumer')
        try:p.call(stale,'run_command',**spec)
        except ValueError as error:assert 'Active release changed' in str(error)
        else:raise AssertionError('Old MCP server accepted submission after activation')
        same=p.run(stable);assert same['task_id']==before['task_id']
        wait_for(p.root_unlocked)
        rolled=p.invoke([p.cli,'activate','--root',str(p.root),'--release',old_release,'--json'])
        same_again=p.run(stable)
        assert same_again['task_id']==before['task_id'] and same_again['status']=='success'
        assert sum(e['token']==stable['operation_id'] and e['event']=='start' for e in p.events())==1
        return {'active_upgrade_refused':True,'active_rollback_refused':True,'upgraded':upgraded['release'],
                'rolled_back':rolled['release'],'stable_task_id':before['task_id'],'stale_mcp_refused':True}
    if case == 'group-recovery':
        first=p.operation('lingering-success',.1,'exit-linger');p.run(first)
        wait_for(lambda:p.event(first['operation_id'],'descendant_ready'))
        held=p.terminal(first['operation_id'])
        wait_for(p.root_unlocked)
        release=Path(json.loads((p.root/'current.json').read_text())['configuration']).parent.name
        refusal=p.invoke([p.cli,'activate','--root',str(p.root),'--release',release,'--json'],expected=2)
        assert 'unresolved admission remains' in refusal
        second=p.operation('behind-group');p.run(second)
        assert held['status']=='recovery-pending' and held['capacity_held'] and p.status(second['operation_id'])['status']=='queued'
        leaf=p.event(first['operation_id'],'descendant_start');os.kill(leaf['pid'],signal.SIGKILL)
        recovered=wait_for(lambda:(v if (v:=p.status(first['operation_id']))['status']=='success' else None),10)
        successor=p.terminal(second['operation_id'])
        assert not recovered['capacity_held'] and successor['status']=='success'
        return {'while_group_alive':held['status'],'after_verified_closure':recovered['status'],'successor':successor['status']}
    raise ValueError(case)


CASES=('mixed-cap','idempotent-race','conflicting-race','submission-handoff-crash','client-death','queued-worker-death','argv-and-environment','deadlines','cancel','worker-death','server-death','group-recovery','drift-refusal','maintenance')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worktree',type=Path,default=Path.cwd())
    parser.add_argument('--case',choices=CASES,action='append')
    parser.add_argument('--archive',type=Path,help='pinned archive for disposable upgrade proof')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    pilot=Pilot(args.root,args.output,args.worktree);pilot.archive=args.archive.resolve() if args.archive else None;results=[]
    try:
        for case in args.case or CASES:
            try:details=check(pilot,case);verdict='passed'
            except Exception as error:details={'error':repr(error),'traceback':__import__('traceback').format_exc()};verdict='failed'
            value={'case':case,'verdict':verdict,'details':details};results.append(value);print(json.dumps(value),flush=True)
    finally:pilot.close()
    (args.output/'verdicts.json').write_text(json.dumps(results,indent=2)+'\n')
    return int(any(r['verdict']!='passed' for r in results))


if __name__=='__main__':sys.exit(main())
