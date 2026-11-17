"""Controlled foreground project-runner fixture, never a device/SimLock adapter."""

import argparse
import hashlib
import json
from pathlib import Path
import signal
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('build', 'checks'))
    parser.add_argument('root', type=Path)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--failure', choices=('command', 'release', 'cleanup'))
    parser.add_argument('--seconds', type=float, default=.05)
    args = parser.parse_args()
    root = args.root; root.mkdir(parents=True, exist_ok=True)
    artifact = root/'artifact.bin'
    def event(name, **fields):
        with (root/'events.jsonl').open('a') as stream:
            stream.write(json.dumps({'event': name, 'run_id': args.run_id, 'time': time.time(), **fields})+'\n')
    if args.phase == 'build':
        artifact.write_text('exact-build-'+args.run_id)
        event('built', artifact=str(artifact))
        return 1 if args.failure else 0
    lease = root/(args.run_id+'.fixture-lease')
    identity = {'run_id': args.run_id, 'lease_id': 'fixture-'+args.run_id}
    with lease.open('x') as stream:
        json.dump(identity, stream)
    event('acquired', **{'lease_id': identity['lease_id']})
    result = {'run_id': args.run_id, 'lease_id': identity['lease_id'], 'command': 'interrupted',
              'release': 'not-attempted', 'cleanup': 'not-attempted'}
    def interrupted(signum, frame):
        raise InterruptedError('fixture interrupted')
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        result['artifact_sha256'] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        time.sleep(args.seconds)
        result['command'] = 'failed' if args.failure == 'command' else 'success'
    except InterruptedError:
        pass
    finally:
        if args.failure == 'release':
            result['release'] = 'failed'
        elif json.loads(lease.read_text()) != identity:
            result['release'] = 'ownership-conflict'
        else:
            lease.unlink(); result['release'] = 'released'
        result['cleanup'] = 'failed' if args.failure == 'cleanup' else 'complete'
        event('finished', result=result)
        print(json.dumps(result), flush=True)
    return 0 if (result['command'], result['release'], result['cleanup']) == ('success','released','complete') else 70


if __name__ == '__main__':
    raise SystemExit(main())
