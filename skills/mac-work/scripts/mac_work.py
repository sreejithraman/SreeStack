"""Run foreground build/test commands through one shared heavy=1 queue.

Install creates a private versioned root; it does not edit provider profiles.
Commands must wait for their heavy work. Daemons and escaping groups/sessions
are outside this pilot contract. Output logs are verbatim, not secret redaction.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import sys

# Only this verified bundle directory supplements isolated Python's import path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner_config as configuration


def emit(value, as_json):
    if as_json:
        print(json.dumps(value, sort_keys=True))
    elif 'operation_id' in value:
        print(f"{value['operation_id']}: {value['status']} (capacity held: {value.get('capacity_held', False)})")
        print(f"receipt: {value['receipt_path']}\nlog: {value['log_path']}")
    else:
        for key, item in value.items():
            print(f'{key}: {item}')


def serve(config):
    import asyncio
    from fastmcp import FastMCP
    import runner
    server = FastMCP('Mac Work')

    @server.tool()
    async def run_command(operation_id: str, owner: str, argv: list[str], worktree: str,
                          queue_seconds: int = 1200, execution_seconds: int = 1200):
        """Submit once by stable ID. Commands must keep all heavy work foreground.

        Same ID/input returns its original task/result; changed input conflicts.
        Read status rather than resubmitting. No queue/capacity overrides exist.
        """
        return await asyncio.to_thread(runner.submit, config, operation_id, owner, argv,
                                       worktree, queue_seconds, execution_seconds)

    @server.tool()
    async def command_status(operation_id: str):
        """Read/reconcile an existing operation; never submits work."""
        return await asyncio.to_thread(runner.status, config, operation_id)

    @server.tool()
    async def cancel_command(operation_id: str):
        """Cancel an exact operation; unresolved ownership keeps capacity held."""
        return await asyncio.to_thread(runner.cancel, config, operation_id)

    server.run(show_banner=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=configuration.DEFAULT_ROOT / 'current.json',
                        help='explicit shared root/current.json; never a per-process queue option')
    commands = parser.add_subparsers(dest='command', required=True)
    install = commands.add_parser('install', help='build and activate an immutable private release if idle')
    install.add_argument('--root', type=Path, default=configuration.DEFAULT_ROOT)
    install.add_argument('--release', required=True)
    install.add_argument('--archive', type=Path)
    install.add_argument('--json', action='store_true')
    activate = commands.add_parser('activate', help='upgrade/rollback to an existing verified release if idle')
    activate.add_argument('--root', type=Path, default=configuration.DEFAULT_ROOT)
    activate.add_argument('--release', required=True)
    activate.add_argument('--json', action='store_true')
    run = commands.add_parser('run', help='submit one immutable operation and return its handle')
    run.add_argument('--id', required=True)
    run.add_argument('--owner', required=True)
    run.add_argument('--worktree', required=True)
    run.add_argument('--queue-seconds', type=int, default=1200)
    run.add_argument('--execution-seconds', type=int, default=1200)
    run.add_argument('--wait-seconds', type=int, default=0, help='bounded observation only; expiration does not cancel')
    run.add_argument('--json', action='store_true')
    run.add_argument('argv', nargs=argparse.REMAINDER)
    for operation in ('status', 'cancel'):
        command = commands.add_parser(operation)
        command.add_argument('--id', required=True)
        command.add_argument('--json', action='store_true')
        if operation == 'status':
            command.add_argument('--wait-seconds', type=int, default=0)
    commands.add_parser('mcp', help='stdio facade over the same configuration and upstream state')
    worker = commands.add_parser('_worker', help=argparse.SUPPRESS)
    worker.add_argument('--configuration', type=Path, required=True)
    worker.add_argument('--sha256', required=True)
    worker.add_argument('--id', required=True)
    args = parser.parse_args()
    if args.command == 'install':
        emit(configuration.install(args.root, args.release, args.archive), args.json)
        return 0
    if args.command == 'activate':
        emit(configuration.activate(args.root.resolve(), args.release), args.json)
        return 0
    config = configuration.load(args.config)
    if args.command == '_worker' and (args.configuration != Path(config['_path']) or args.sha256 != config['_sha256']):
        raise ValueError('Worker configuration differs from active release')
    installed = Path(config['_path']).parent / 'bundle/scripts/mac_work.py'
    if Path(sys.prefix) != Path(config['runtime']) or Path(__file__).resolve() != installed:
        os.execv(str(Path(config['root']) / 'bin/mac-work'), [str(Path(config['root']) / 'bin/mac-work'), *sys.argv[1:]])
    if args.command == 'mcp':
        serve(config)
        return 0
    import runner
    if args.command == '_worker':
        runner.worker(config, args.id)
        return 0
    wait_seconds = getattr(args, 'wait_seconds', 0)
    if not 0 <= wait_seconds <= 30:
        raise ValueError('Observation wait must be 0..30 seconds; it is separate from task deadlines')
    if args.command == 'run':
        argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
        value = runner.submit(config, args.id, args.owner, argv, args.worktree,
                              args.queue_seconds, args.execution_seconds)
    elif args.command == 'cancel':
        value = runner.cancel(config, args.id)
    else:
        value = runner.status(config, args.id)
    if wait_seconds and args.command != 'cancel':
        value = runner.wait(config, args.id, wait_seconds)
    emit(value, args.json)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, sqlite3.Error, subprocess.SubprocessError) as error:
        print(f'mac-work refused: {error}', file=sys.stderr)
        sys.exit(2)
