"""Canonical build/artifact/foreground-runner proof; no real devices or leases."""

import argparse
import hashlib
import json
import os
import shlex
import shutil
from pathlib import Path
import subprocess
import sys

from fitness import wait_for
from runner_fitness import Pilot, SCRIPTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    pilot = Pilot(args.root, args.output, Path.cwd())
    outputs = args.output/'fixtures'
    outputs.mkdir()
    foreign = outputs/'foreign.fixture-lease'
    foreign.write_text('foreign owner: leave untouched')
    verdicts = []
    def record(case, body):
        try:
            details = body()
            verdict = 'passed'
        except Exception as error:
            details = {'error':repr(error), 'traceback':__import__('traceback').format_exc()}
            verdict='failed'
        value = {'case':case,'verdict':verdict,'details':details}
        verdicts.append(value)
        print(json.dumps(value),flush=True)
    def job(label, phase, root, failure=None, seconds=.05):
        spec = pilot.operation(label)
        spec['argv'] = [pilot.python,str(SCRIPTS/'handoff_fixture.py'),phase,str(root),'--run-id',spec['operation_id'],'--seconds',str(seconds)]
        if failure:
            spec['argv'] += ['--failure',failure]
        return spec
    def seal(spec, root):
        return pilot.invoke([pilot.cli,'handoff','--id',spec['operation_id'],'--artifact',str(root/'artifact.bin'),'--json'])
    def run_after(spec, build):
        argv=pilot.argv(spec)
        at=argv.index('--')
        argv[at:at]=['--handoff',build['operation_id']]
        return pilot.invoke(argv)
    def events(root):
        path=root/'events.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    def success():
        root=outputs/'success'
        build=job('build','build',root)
        pilot.run(build)
        assert pilot.terminal(build['operation_id'])['status']=='success'
        manifest=seal(build,root)
        assert seal(build,root)==manifest
        peer=pilot.peer()
        assert pilot.call(peer,'build_handoff',operation_id=build['operation_id'],artifacts=[str(root/'artifact.bin')])==manifest
        check=job('checks','checks',root)
        run_after(check,build)
        done=pilot.terminal(check['operation_id'])
        assert done['status']=='success' and not done['capacity_held']
        finished=next(e['result'] for e in events(root) if e['event']=='finished')
        assert finished['artifact_sha256']==hashlib.sha256((root/'artifact.bin').read_bytes()).hexdigest()
        (root/'artifact.bin').unlink()
        late=run_after(check,build)
        assert late['task_id']==done['task_id']
        assert sum(e['event']=='acquired' for e in events(root))==1
        return {'task_id':done['task_id'],'manifest':manifest['manifest_path'],'late_no_replay':True,'exact_artifact':True}
    def failed_build():
        root=outputs/'failed'
        build=job('failed-build','build',root,'command')
        pilot.run(build)
        assert pilot.terminal(build['operation_id'])['status']=='failed'
        error=pilot.invoke([pilot.cli,'handoff','--id',build['operation_id'],'--artifact',str(root/'artifact.bin'),'--json'],expected=2)
        assert 'successful, closed build' in error and not any(e['event']=='acquired' for e in events(root))
        return {'handoff_refused':True,'acquisitions':0}
    def cancellation_and_drift():
        root=outputs/'cancel'
        build=job('cancel-build','build',root)
        pilot.run(build)
        pilot.terminal(build['operation_id'])
        seal(build,root)
        holder=pilot.operation('holder',60)
        holder['execution_seconds']=90
        check_queue_seconds=120
        pilot.run(holder)
        wait_for(lambda:pilot.event(holder['operation_id'],'start'))
        check=job('queued-check','checks',root)
        check['queue_seconds']=check_queue_seconds
        run_after(check,build)
        pilot.cancel(check['operation_id'])
        assert pilot.terminal(check['operation_id'])['status']=='cancelled'
        drift=job('drift-check','checks',root)
        drift['queue_seconds']=check_queue_seconds
        run_after(drift,build)
        (root/'artifact.bin').write_text('drifted after queueing')
        pilot.cancel(holder['operation_id'])
        pilot.terminal(holder['operation_id'])
        done=pilot.terminal(drift['operation_id'])
        assert done['status']=='error' and 'artifact drift' in done['error']
        assert not any(e['event']=='acquired' for e in events(root))
        return {'queued_cancel':'cancelled','artifact_drift':'error','acquisitions':0}
    def preflight_timeout():
        root = outputs / 'preflight-timeout'
        build = job('preflight-build', 'build', root)
        pilot.run(build)
        assert pilot.terminal(build['operation_id'])['status'] == 'success'
        seal(build, root)
        check = job('expired-preflight-check', 'checks', root)
        check['execution_seconds'] = 1
        observed = root / 'preflight.json'
        shim = root / 'git-shim'
        shim.mkdir()
        real_git = shutil.which('git')
        probe = shim / 'git_probe.py'
        probe.write_text("""import json, os, sqlite3, sys, time
from pathlib import Path
with sqlite3.connect(sys.argv[1]) as conn:
    row = conn.execute('SELECT q.status,q.lifecycle_json FROM queue q JOIN task_operations o ON o.task_id=q.id WHERE o.operation_id=?', (sys.argv[2],)).fetchone()
if row and row[0] == 'running':
    Path(sys.argv[3]).write_text(json.dumps({'observed_at':time.time(),'lifecycle':json.loads(row[1])}))
    time.sleep(1.2)
os.execv(sys.argv[4], [sys.argv[4], *sys.argv[5:]])
""")
        wrapper = shim / 'git'
        wrapper.write_text('#!/bin/sh\nexec ' + shlex.join([pilot.python, '-I', '-B', str(probe),
            str(pilot.root / 'state/queue.db'), check['operation_id'], str(observed), real_git]) + ' "$@"\n')
        wrapper.chmod(0o700)
        argv = pilot.argv(check)
        at = argv.index('--')
        argv[at:at] = ['--handoff', build['operation_id']]
        submitted = subprocess.run(argv, env={**os.environ, 'PATH': str(shim) + os.pathsep + os.environ['PATH']},
                                   text=True, capture_output=True, timeout=30)
        pilot.transcript.append({'argv': argv, 'exit': submitted.returncode,
                                 'stdout': submitted.stdout, 'stderr': submitted.stderr})
        assert submitted.returncode == 0, submitted.stderr
        preflight = wait_for(lambda: json.loads(observed.read_text()) if observed.exists() else None)
        done = wait_for(lambda: (value if (value := pilot.status(check['operation_id']))['status'] == 'timeout'
                                  and not value['capacity_held'] else None), 10)
        assert done['started_at'] == preflight['lifecycle']['admitted_at']
        assert done['deadlines']['execution'] == done['started_at'] + 1
        assert not any(event['event'] == 'acquired' for event in events(root))
        assert foreign.read_text() == 'foreign owner: leave untouched'
        return {'status': done['status'], 'capacity_held': done['capacity_held'],
                'acquisitions': 0, 'started_at': done['started_at'],
                'preflight_observed_at': preflight['observed_at'], 'task_id': done['task_id']}

    def cleanup_failures():
        results=[]
        for failure in ('release','cleanup','command'):
            root=outputs/failure
            build=job(failure+'-build','build',root)
            pilot.run(build)
            pilot.terminal(build['operation_id'])
            seal(build,root)
            check=job(failure+'-checks','checks',root,failure)
            run_after(check,build)
            done=pilot.terminal(check['operation_id'])
            result=next(e['result'] for e in events(root) if e['event']=='finished')
            assert done['status']=='failed' and done['exit_code']==70 and not done['capacity_held']
            assert result[failure if failure!='command' else 'command']=='failed'
            assert result['command']==('failed' if failure=='command' else 'success')
            results.append(result)
        assert foreign.read_text()=='foreign owner: leave untouched'
        return {'results':results,'foreign_lease_unchanged':True,'device_cleanup_claim':False}
    def running_cancel():
        root=outputs/'running-cancel'
        build=job('running-build','build',root)
        pilot.run(build)
        pilot.terminal(build['operation_id'])
        seal(build,root)
        check=job('running-check','checks',root,seconds=10)
        run_after(check,build)
        wait_for(lambda:any(e['event']=='acquired' for e in events(root)))
        pilot.cancel(check['operation_id'])
        done=pilot.terminal(check['operation_id'])
        result=wait_for(lambda:next((e['result'] for e in events(root) if e['event']=='finished'),None))
        assert done['status']=='cancelled' and not done['capacity_held'] and result['release']=='released'
        assert not (root/(check['operation_id']+'.fixture-lease')).exists()
        return {'status':done['status'],'release':result['release']}
    try:
        for case,body in (('exact-handoff-late-no-replay',success),('failure-before-acquisition',failed_build),('queued-cancel-and-artifact-drift',cancellation_and_drift),('command-and-teardown-failures',cleanup_failures),('running-cancellation',running_cancel),('admitted-preflight-timeout',preflight_timeout)):
            record(case,body)
    finally:
        pilot.close()
    (args.output/'verdicts.json').write_text(json.dumps(verdicts,indent=2)+'\n')
    return int(any(v['verdict']!='passed' for v in verdicts))


if __name__=='__main__':
    sys.exit(main())
