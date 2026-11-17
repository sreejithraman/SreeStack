"""Real report CLI/MCP proof with task-owned lightweight queue fixtures."""

import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time

from fitness import wait_for
from runner_fitness import Pilot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--simlock',help='optional qualified installed read-only event source')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    p=Pilot(args.root,args.output,Path.cwd())
    results=[]
    def record(case,body):
        try:
            details=body()
            verdict='passed'
        except Exception as error:
            details={'error':repr(error),'traceback':__import__('traceback').format_exc()}
            verdict='failed'
        value={'case':case,'verdict':verdict,'details':details}
        results.append(value)
        print(json.dumps(value),flush=True)
    def report(*flags):
        return p.invoke([p.cli,'report',*flags,'--json'])
    def live():
        holder=p.operation('report-running',10)
        p.run(holder)
        wait_for(lambda:p.event(holder['operation_id'],'start'))
        queued=p.operation('report-queued',.1)
        p.run(queued)
        time.sleep(.2)
        cancelled=p.operation('report-already-cancelled')
        p.run(cancelled)
        p.cancel(cancelled['operation_id'])
        ordered=report('--limit','2')
        assert [j['operation_id'] for j in ordered['jobs']]==[holder['operation_id'],queued['operation_id']]
        flags=['--sample','--lease-id','fixture-correlation-only','--output',str(args.output/'live-report.json')]
        if args.simlock:
            flags += ['--simlock',args.simlock]
        value=report(*flags)
        by_id={j['operation_id']:j for j in value['jobs']}
        active=by_id[holder['operation_id']]
        waiting=by_id[queued['operation_id']]
        assert active['status']=='running' and active['execution_seconds']>0 and active['capacity_held']
        assert waiting['status']=='queued' and waiting['execution_seconds'] is None and waiting['queue_wait_seconds']>0
        sample=value['pressure']
        assert sample['freshness']=='fresh' and value['policy']['capacities']=={'heavy':1}
        assert all(s['status']=='available' for s in sample['signals'].values()),sample
        group=next(g for g in sample['process_groups'] if g['operation_id']==holder['operation_id'])
        assert group['status']=='observed' and group['rss_sum_bytes']>0 and group['anchor_identity']=='matched'
        one=report('--limit','1')
        assert one['truncated'] and one['jobs'][0]['operation_id']==holder['operation_id']
        peer=p.peer()
        remote=p.call(peer,'work_report',operation_ids=[holder['operation_id'],queued['operation_id']],sample=True)
        assert {j['task_id'] for j in remote['jobs']}=={active['task_id'],waiting['task_id']}
        (args.output/'mcp-report.json').write_text(json.dumps(remote,indent=2)+'\n')
        p.cancel(queued['operation_id'])
        p.cancel(holder['operation_id'])
        p.terminal(holder['operation_id'])
        done=report('--id',holder['operation_id'],'--id',queued['operation_id'])
        assert all(j['status']=='cancelled' and not j['capacity_held'] for j in done['jobs'])
        return {'running_and_queue_separate':True,'rss_bytes':group['rss_sum_bytes'],'lease_signal':sample['lease_signal']['status'],'mcp_same_tasks':True}
    def stale_missing():
        old=json.loads((args.output/'live-report.json').read_text())
        old['pressure']['sampled_at']-=120
        for signal_value in old['pressure']['signals'].values():
            signal_value['sampled_at']-=120
        old['private_env']={'SECRET':'must-not-copy'}
        path=args.output/'old-report.json'
        path.write_text(json.dumps(old))
        value=report('--sample-file',str(path))
        assert value['pressure']['freshness']=='stale'
        assert 'must-not-copy' not in json.dumps(value) and value['pressure']['process_groups']==[]
        (args.output/'stale-report.json').write_text(json.dumps(value,indent=2)+'\n')
        missing=report('--sample','--simlock','/missing-simlock-fixture')
        assert missing['pressure']['lease_signal']['status']=='unavailable'
        bad=p.invoke([p.cli,'report','--limit','101','--json'],expected=2)
        assert '1..100' in bad
        count=report('--limit','1')['total_operations']
        bad=p.invoke([p.cli,'report','--id','unknown-report-only','--json'],expected=2)
        assert 'Unknown operation' in bad
        assert report('--limit','1')['total_operations']==count
        original=(args.output/'live-report.json').read_bytes()
        p.invoke([p.cli,'report','--output',str(args.output/'live-report.json'),'--json'],expected=2)
        assert (args.output/'live-report.json').read_bytes()==original
        return {'stale_explicit':True,'missing_explicit':True,'private_fields_not_copied':True,'proof_not_overwritten':True}
    def recovery():
        spec=p.operation('report-lingering',.1,'exit-linger')
        p.run(spec)
        wait_for(lambda:p.event(spec['operation_id'],'descendant_ready'))
        wait_for(lambda:p.status(spec['operation_id'])['status']=='recovery-pending')
        held=report('--id',spec['operation_id'],'--sample')
        job=held['jobs'][0]
        assert job['status']=='recovery-pending' and job['capacity_held'] and job['lifecycle']['state']=='recovery-pending'
        (args.output/'held-report.json').write_text(json.dumps(held,indent=2)+'\n')
        leaf=p.event(spec['operation_id'],'descendant_start')
        os.kill(leaf['pid'],signal.SIGKILL)
        done=wait_for(lambda:(v if (v:=report('--id',spec['operation_id']))['jobs'][0]['status']=='success' else None),10)
        assert not done['jobs'][0]['capacity_held']
        (args.output/'closed-report.json').write_text(json.dumps(done,indent=2)+'\n')
        return {'before':'recovery-pending','after_verified_closure':'success','no_force_clear':True}
    try:
        for case,body in (('live-cli-mcp-attribution',live),('stale-missing-and-read-only',stale_missing),('recovery-hold-and-closure',recovery)):
            record(case,body)
    finally:
        p.close()
    (args.output/'verdicts.json').write_text(json.dumps(results,indent=2)+'\n')
    return int(any(r['verdict']!='passed' for r in results))


if __name__=='__main__':
    sys.exit(main())
