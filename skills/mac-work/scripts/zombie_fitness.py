"""Native zombie-owner recovery with an idle persistent MCP parent and another client."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def status(cli, operation):
    result = subprocess.run([str(cli), 'status', '--id', operation, '--json'],
                            capture_output=True, text=True, check=True, timeout=20)
    return json.loads(result.stdout)


async def until(body, seconds=10):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        value = body()
        if value:
            return value
        await asyncio.sleep(.025)
    raise TimeoutError('Native observation deadline expired')


async def exercise(root, output, pause_parent=False):
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport
    import queue_lifecycle as lifecycle
    cli = root / 'bin/mac-work'
    transport = StdioTransport(command=str(cli), args=['mcp'],
        env={'FASTMCP_CHECK_FOR_UPDATES': 'off'}, keep_alive=False)
    results = []
    async with Client(transport) as client:
        def server():
            for line in subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,args='], text=True).splitlines():
                pid, parent, argv = line.strip().split(None, 2)
                if int(parent) == os.getpid() and str(root) in argv and ' mcp' in argv:
                    return lifecycle.process_identity(int(pid))
        parent = await until(server)
        for mode in ('active-group', 'empty-group'):
            operation = 'zombie-' + mode + '-' + output.name
            marker = output / (mode + '.started')
            spec = {'operation_id': operation, 'owner': 'zombie-fixture', 'worktree': str(Path.cwd()),
                    'queue_seconds': 20, 'execution_seconds': 60,
                    'argv': [sys.executable, '-I', '-B', '-c',
                        'import os,time;from pathlib import Path;Path(' + repr(str(marker)) + ').write_text(str(os.getpid()));time.sleep(40)']}
            worker = child = None
            parent_stopped = False
            observations = {'stage': 'submitting', 'parent': parent}
            try:
                accepted = (await client.call_tool('run_command', spec)).structured_content
                def executing():
                    value = status(cli, operation)
                    return value if value['lifecycle'].get('child') and marker.exists() else None
                running = await until(executing)
                observations.update(stage='executing', before=running)
                worker = running['worker']
                child = running['lifecycle']['child']
                assert lifecycle.process_identity(worker['pid'])['birth'] == worker['birth']
                parent_pid = subprocess.check_output(['/bin/ps', '-o', 'ppid=', '-p', str(worker['pid'])], text=True).strip()
                assert int(parent_pid) == parent['pid'], 'worker is not a child of the persistent MCP server'
                await asyncio.sleep(.5)
                if mode == 'empty-group':
                    os.kill(worker['pid'], signal.SIGSTOP)
                    anchor = lifecycle.process_identity(child['pid'])
                    assert anchor and anchor['birth'] == child['birth'] and anchor['pgid'] == child['pgid']
                    os.killpg(child['pgid'], signal.SIGTERM)
                    await until(lambda: not lifecycle.group_members(child['pgid']))
                if pause_parent:
                    current_parent = lifecycle.process_identity(parent['pid'])
                    assert current_parent and current_parent['birth'] == parent['birth']
                    os.kill(parent['pid'], signal.SIGSTOP)
                    parent_stopped = True
                    await until(lambda: 'T' in subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(parent['pid'])], capture_output=True, text=True).stdout)
                os.kill(worker['pid'], signal.SIGKILL)
                observations.update(stage='owner-killed', worker=worker, child=child)
                samples = []
                def stopped_owner():
                    value = lifecycle.process_identity(worker['pid'])
                    samples.append(value)
                    observations['owner_samples'] = samples
                    return {'identity': value} if value is None or value['zombie'] else None
                observed_owner = (await until(stopped_owner))['identity']
                native_state = subprocess.run(['/bin/ps', '-o', 'pid=,ppid=,stat=', '-p', str(worker['pid'])], capture_output=True, text=True)
                observed = status(cli, operation)
                late = status(cli, operation)
                server_after = lifecycle.process_identity(parent['pid'])
                zombie_after = lifecycle.process_identity(worker['pid'])
                observations = {'case': mode, 'parent': parent, 'server_after': server_after,
                    'worker': worker, 'observed_owner': observed_owner, 'owner_after_other_clients': zombie_after,
                    'before': running, 'after': observed, 'late': late,
                    'group_after': lifecycle.group_members(child['pgid']), 'marker_pid': marker.read_text(),
                    'native_ps_after_kill': {'exit': native_state.returncode, 'stdout': native_state.stdout},
                    'independent_client': True, 'parent_new_submission_before_observation': False,
                    'parent_paused_to_retain_zombie': pause_parent}
                assert server_after and server_after['birth'] == parent['birth'] and not server_after['zombie']
                if observed_owner is not None:
                    assert zombie_after and zombie_after['zombie'], 'parent reaped worker during recovery observation'
                assert observed['status'] == late['status'] == 'interrupted' and not observed['capacity_held']
                assert not observations['group_after']
                verdict = {'case': mode, 'verdict': 'passed', 'native_zombie_observed': bool(observed_owner and observed_owner['zombie']),
                           'native_owner_not_visible_to_libproc': observed_owner is None,
                           'native_ps_after_kill': native_state.stdout.strip(),
                           'parent_stayed_idle_and_alive': True, 'parent_paused_to_retain_zombie': pause_parent, 'capacity_held': False}
            except Exception as error:
                verdict = {'case': mode, 'verdict': 'failed', 'error': repr(error),
                           'native_zombie_observed': bool((observations.get('observed_owner') or {}).get('zombie'))}
            finally:
                if parent_stopped:
                    current_parent = lifecycle.process_identity(parent['pid'])
                    if current_parent and current_parent['birth'] == parent['birth']:
                        os.kill(parent['pid'], signal.SIGCONT)
                # Exact operation cleanup is separate from the recovery verdict.
                if worker is not None:
                    identity = lifecycle.process_identity(worker['pid'])
                    if identity and identity['birth'] == worker['birth'] and not identity['zombie']:
                        os.kill(worker['pid'], signal.SIGKILL)
                        observations['fixture_stopped_live_worker'] = True
                cleanup = subprocess.run([str(cli), 'cancel', '--id', operation, '--json'],
                                         capture_output=True, text=True, timeout=20)
                observations['cleanup'] = {'exit': cleanup.returncode, 'stdout': cleanup.stdout, 'stderr': cleanup.stderr}
                (output / (mode + '.json')).write_text(json.dumps(observations, indent=2) + '\n')
            results.append(verdict)
            print(json.dumps(verdict), flush=True)
    (output / 'verdicts.json').write_text(json.dumps(results, indent=2) + '\n')
    return int(any(value['verdict'] != 'passed' for value in results))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pause-parent', action='store_true', help='bounded SIGSTOP of the owned MCP parent retains a real zombie; resume after observation')
    args = parser.parse_args()
    pointer = json.loads((args.root / 'current.json').read_text())
    runtime = Path(json.loads(Path(pointer['configuration']).read_text())['runtime'])
    if Path(sys.prefix) != runtime:
        os.execv(str(runtime / 'bin/python'), [str(runtime / 'bin/python'), '-I', '-B',
                 str(Path(__file__).resolve()), *sys.argv[1:]])
    args.output.mkdir(parents=True, exist_ok=False)
    return asyncio.run(exercise(args.root.resolve(), args.output.resolve(), args.pause_parent))


if __name__ == '__main__':
    sys.exit(main())
