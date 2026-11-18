"""Bounded observations over canonical receipts and read-only host signals."""

from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
from pathlib import Path
import re
import selectors
import subprocess
import time

from runner import database, snapshot
import runner_config

MAX_SAMPLE_AGE = 60


def read_probe(argv, seconds=2, max_bytes=1024*1024):
    sampled_at = time.time()
    try:
        with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
            deadline = time.monotonic() + seconds
            content = bytearray()
            reason = None
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        reason = 'timeout'; break
                    if not selector.select(remaining):
                        reason = 'timeout'; break
                    block = os.read(process.stdout.fileno(), 65536)
                    if not block:
                        try:process.wait(timeout=max(.001, deadline-time.monotonic()))
                        except subprocess.TimeoutExpired:reason = 'timeout'
                        break
                    content.extend(block)
                    if len(content) > max_bytes:
                        reason = 'output-limit'; break
            if reason:
                process.kill(); process.wait()
                return {'status':'unavailable','reason':reason,'sampled_at':sampled_at}
            if process.returncode:
                return {'status':'unavailable','reason':f'exit-{process.returncode}','sampled_at':sampled_at}
            return {'status':'available','text':content.decode('utf-8',errors='replace'),'sampled_at':sampled_at}
    except OSError:
        return {'status':'unavailable','reason':'command-unavailable','sampled_at':sampled_at}


def sample_age(sampled_at, now=None):
    now = time.time() if now is None else now
    if type(sampled_at) not in (int,float) or not math.isfinite(sampled_at):
        raise ValueError('Sample timestamp must be a finite epoch second value')
    age = now - sampled_at
    return {'age_seconds':round(age,3), 'freshness':'clock-skew' if age < -1 else 'stale' if age > MAX_SAMPLE_AGE else 'fresh'}


def decode_swap(text):
    values = {}
    for key in ('total','used','free'):
        match = re.search(key+r'\s*=\s*([\d.]+)([BKMG])',text)
        if not match:
            raise ValueError('Unrecognized vm.swapusage units')
        values[key+'_bytes'] = round(float(match[1]) * 1024**'BKMG'.index(match[2]))
    return values


def decode_vm(text):
    match = re.search(r'page size of (\d+) bytes', text)
    if match is None:
        raise ValueError('Unrecognized vm_stat page size')
    page = int(match[1])
    fields = {'Pages free': 'free_bytes', 'Pages occupied by compressor': 'compressor_physical_bytes',
              'Pages stored in compressor': 'compressor_logical_bytes'}
    result = {'page_bytes': page}
    for label, name in fields.items():
        value = re.search(r'^'+re.escape(label)+r':\s+(\d+)\.', text, re.M)
        if value:
            result[name] = int(value[1]) * page
    if len(result) == 1:
        raise ValueError('Unrecognized vm_stat counters')
    return result


def reconcile_and_read_jobs(config, limit, operation_ids):
    if type(limit) is not int or not 1 <= limit <= 100 or len(operation_ids) > 20:
        raise ValueError('Report limit must be 1..100; at most 20 exact IDs')
    with runner_config.activation_lock(Path(config['root'])):
        runner_config.require_active(config)
        import queue_lifecycle as lifecycle
        with database(config) as conn:
            lifecycle.reconcile(conn, 'heavy', 120)
            deadline = time.monotonic() + 5
            conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
            total = conn.execute('SELECT COUNT(*) FROM task_operations').fetchone()[0]
            if operation_ids:
                selected = list(dict.fromkeys(operation_ids))
            else:
                selected = [r[0] for r in conn.execute('''SELECT o.operation_id FROM task_operations o
                    LEFT JOIN queue q ON q.id=o.task_id
                    ORDER BY CASE WHEN q.status='running' THEN 0 WHEN q.status='waiting' THEN 1 ELSE 2 END,
                    o.task_id DESC LIMIT ?''',(limit,))]
            receipts = [snapshot(conn, config, name, reconcile=False) for name in selected]
    now = time.time()
    result = []
    for receipt in receipts:
        start = receipt['started_at']; end = receipt.get('closed_at') or now
        item = {k:receipt.get(k) for k in ('operation_id','task_id','status','exit_code','capacity_held','receipt_path','log_path','queued_at','started_at','closed_at','deadlines','ownership_contract','lifecycle')}
        item.update(owner=receipt['request']['owner'], worktree=receipt['request']['worktree'],
                    revision=receipt['request']['revision'], dirty=receipt['request']['dirty'],
                    handoff=receipt['request'].get('handoff'),
                    queue_wait_seconds=round(max(0,(start or end)-receipt['queued_at']),3),
                    execution_seconds=round(max(0,end-start),3) if start is not None else None,
                    program_duration_seconds=receipt.get('duration_seconds'))
        result.append(item)
    return result, total


def decoded(probe, parse):
    result = {k:v for k,v in probe.items() if k!='text'}
    if probe['status']=='available':
        try:result.update(parse(probe['text']))
        except (ValueError,IndexError,KeyError):result.update(status='unavailable',reason='unrecognized-format')
    return result


def decode_level(text):
    raw = int(text.strip())
    return {'raw_level':raw,'level':{1:'normal',2:'warning',4:'critical'}.get(raw,'unknown')}


def decode_free(text):
    match = re.search(r'System-wide memory free percentage:\s*(\d+)%',text)
    if not match:raise ValueError('Unknown memory_pressure format')
    return {'free_percentage':int(match[1])}


def group_memory(rows, text):
    import queue_lifecycle as lifecycle
    processes = []
    for line in text.splitlines():
        fields=line.strip().split(None,4)
        if len(fields)!=5:raise ValueError('Unrecognized ps format')
        pid,ppid,pgid,rss=map(int,fields[:4])
        processes.append({'pid':pid,'ppid':ppid,'pgid':pgid,'rss_bytes':rss*1024,'command_name':Path(fields[4]).name})
    groups=[]
    for job in rows:
        if not job['capacity_held']:continue
        child=job['lifecycle'].get('child')
        if child is None:
            groups.append({'operation_id':job['operation_id'],'status':'unavailable','reason':'no-recorded-child'});continue
        anchor='unavailable'
        try:
            actual=lifecycle.process_identity(child['pid'])
            anchor='exited' if actual is None else 'matched' if all(actual[k]==child[k] for k in ('pid','pgid','birth')) else 'mismatch'
            if lifecycle.boot_identity()!=job['lifecycle']['boot']:anchor='boot-changed'
        except RuntimeError:pass
        members=[p for p in processes if p['pgid']==child['pgid']]
        groups.append({'operation_id':job['operation_id'],'pgid':child['pgid'],'anchor_identity':anchor,
                       'status':'observed' if members else 'missing','processes':members[:100],
                       'truncated':len(members)>100,'rss_sum_bytes':sum(p['rss_bytes'] for p in members)})
    return groups


def decode_events(text):
    result=[]
    for line in text.splitlines():
        if not line.strip():continue
        event=json.loads(line);payload=event.get('payload',{});lease=payload.get('leaseId')
        if not isinstance(lease,str):continue
        device=payload.get('deviceId');name=event['event'];stamp=event['timestamp']
        if not isinstance(name,str) or type(stamp) not in (float,int) or not math.isfinite(stamp):
            raise ValueError('Unknown SimLock event envelope')
        result.append({'lease_id':lease,'device_id':device if isinstance(device,str) else None,
                       'event':name,'event_at':stamp/1000})
    return result


def lease_events(executable):
    if executable is None:return {'status':'not-requested','known_leases':[]}
    path=Path(executable)
    if not path.is_absolute():raise ValueError('SimLock probe requires an explicit absolute executable path')
    version=read_probe([str(path),'--version'])
    if version.get('text','').strip()!='0.7.0':
        return {'status':'unavailable','reason':'unqualified-version-or-command','known_leases':[]}
    probe=read_probe([str(path),'events','--since','5m'],seconds=5)
    result={k:v for k,v in probe.items() if k!='text'}
    result.update(source='simlock 0.7 events --since 5m; existing connection/history, no launch',known_leases=[])
    if probe['status']=='available':
        try:
            result['known_leases']=decode_events(probe['text'])
            for event in result['known_leases']:event.update(sample_age(event['event_at']))
            result['truncated']=len(result['known_leases'])>100
            result['known_leases']=result['known_leases'][-100:]
        except (ValueError,KeyError,TypeError):result.update(status='unavailable',reason='unrecognized-format',known_leases=[])
    return result


def pressure(rows, simlock, lease_ids):
    sampled_at=time.time()
    probes={'pressure':(['/usr/sbin/sysctl','-n','kern.memorystatus_vm_pressure_level'],decode_level),
            'free':(['/usr/bin/memory_pressure','-Q'],decode_free),
            'vm':(['/usr/bin/vm_stat'],decode_vm),
            'swap':(['/usr/sbin/sysctl','vm.swapusage'],decode_swap)}
    with ThreadPoolExecutor(max_workers=5) as pool:
        pending={key:(pool.submit(read_probe,argv),parser) for key,(argv,parser) in probes.items()}
        ps=pool.submit(read_probe,['/bin/ps','-axo','pid=,ppid=,pgid=,rss=,comm='])
        signals={key:decoded(future.result(),parser) for key,(future,parser) in pending.items()}
        process_probe=ps.result()
    try:groups=group_memory(rows,process_probe['text']) if process_probe['status']=='available' else []
    except ValueError:groups=[];process_probe.update(status='unavailable',reason='unrecognized-format')
    return {'schema':1,'sampled_at':sampled_at,'signals':signals,'process_groups':groups,
            'process_signal':{k:v for k,v in process_probe.items() if k!='text'},
            'lease_signal':lease_events(simlock),'caller_known_lease_ids':lease_ids,
            'limitations':['RSS uses 1024-byte ps units; group sums double-count shared pages and are not physical footprint.',
                          'Process groups are sampled membership, not arbitrary descendant containment or causal pressure attribution.',
                          'Known lease events/caller IDs are correlation evidence, not a current active-lease inventory.']}


def historical(path):
    path=Path(path)
    if path.stat().st_size>1024*1024:raise ValueError('Saved report exceeds 1 MiB')
    value=json.loads(path.read_text())['pressure']
    if value['schema']!=1:raise ValueError('Unknown saved pressure schema')
    fields={'raw_level','free_percentage','page_bytes','free_bytes','compressor_physical_bytes',
            'compressor_logical_bytes','total_bytes','used_bytes'}
    signals={}
    for key in ('pressure','free','vm','swap'):
        signal=value['signals'][key];item={'status':signal['status'],'sampled_at':signal['sampled_at']}
        if item['status'] not in ('available','unavailable'):raise ValueError('Unknown saved signal status')
        sample_age(item['sampled_at'])
        if item['status']=='available':
            for field in fields & signal.keys():
                number=signal[field]
                if type(number) not in (int,float) or not math.isfinite(number):raise ValueError('Invalid saved metric')
                item[field]=number
            if key=='pressure':item['level']={1:'normal',2:'warning',4:'critical'}.get(item.get('raw_level'),'unknown')
        else:item['reason']='recorded-unavailable'
        signals[key]=item
    return {'schema':1,'sampled_at':value['sampled_at'],'signals':signals,'process_groups':[],
            'lease_signal':{'status':'not-resampled','known_leases':[]},'caller_known_lease_ids':[],
            'source_path':str(path.resolve()),'limitations':['Historical host signals only; original file retains process/lease evidence.']}


def report(config, limit=20, operation_ids=None, sample=False, simlock=None, lease_ids=None, sample_file=None):
    operation_ids=operation_ids or [];lease_ids=lease_ids or []
    if sample and sample_file or simlock and not sample or len(lease_ids)>20:
        raise ValueError('Choose live sample or saved sample; SimLock requires live sampling; at most 20 known lease IDs')
    rows,total=reconcile_and_read_jobs(config,limit,operation_ids)
    adaptive = config.get('adaptive_capacity', False)
    admission = {'mode': 'adaptive' if adaptive else 'fixed',
                 'max_heavy': runner_config.ADAPTIVE_CAPACITY if adaptive else config['policy']['capacities']['heavy']}
    value={'schema':1,'reported_at':time.time(),'root':config['root'],'configuration_sha256':config['_sha256'],
           'policy':config['policy'],'admission':admission,'total_operations':total,'truncated':not operation_ids and total>len(rows),
           'jobs':rows,'pressure':{'status':'not-requested'},'observation_only':True}
    if sample or sample_file:
        observed=pressure(rows,simlock,lease_ids) if sample else historical(sample_file)
        observed.update(sample_age(observed['sampled_at']))
        for signal in observed['signals'].values():signal.update(sample_age(signal['sampled_at']))
        value['pressure']=observed
    return value


def readable(value):
    admission = value['admission']
    lines=[f"Mac Work: {len(value['jobs'])}/{value['total_operations']} operations; heavy={admission['mode']} "
           f"(max {admission['max_heavy']}); jobs reconciled; at={value['reported_at']}"]
    for job in value['jobs']:
        execution='not started' if job['execution_seconds'] is None else str(job['execution_seconds'])+'s'
        lines += [f"{job['operation_id']}: {job['status']} owner={job['owner']} task={job['task_id']}",
                  f"  queue={job['queue_wait_seconds']}s execution={execution} exit={job['exit_code']} held={job['capacity_held']}",
                  f"  closure: {job['lifecycle']['state']} ({job['lifecycle'].get('reason','no closure reason')})",
                  f"  {job['worktree']} @ {job['revision']}",f"  receipt: {job['receipt_path']}",f"  log: {job['log_path']}"]
    sample=value['pressure']
    if 'signals' in sample:
        lines.append(f"Pressure: {sample['freshness']} age={sample['age_seconds']}s sampled_at={sample['sampled_at']}")
        for name,signal in sample['signals'].items():lines.append(f"  {name}: {json.dumps(signal,sort_keys=True)}")
        for group in sample['process_groups']:lines.append(f"  group: {json.dumps(group,sort_keys=True)}")
        lines.append(f"  process signal: {json.dumps(sample.get('process_signal',{'status':'not-resampled'}),sort_keys=True)}")
        lines.append(f"  lease signal: {sample['lease_signal']['status']}; known events={len(sample['lease_signal']['known_leases'])}; caller IDs={sample['caller_known_lease_ids']}")
        for event in sample['lease_signal']['known_leases'][-10:]:
            lines.append(f"  lease correlation: {event['lease_id']} {event['event']} age={event['age_seconds']}s ({event['freshness']})")
    else:lines.append('Pressure: not requested')
    if value['truncated']:lines.append('More operations exist; select exact --id or increase --limit (max 100).')
    return '\n'.join(lines)
