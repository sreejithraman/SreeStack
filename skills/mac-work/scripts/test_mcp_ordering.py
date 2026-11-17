"""Refused calls on a registered MCP server stop before operational work."""

import asyncio
import builtins
from contextlib import nullcontext
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mac_work
import runner
import runner_config


class PersistentServer:
    def tool(self):
        def register(function):
            setattr(self, function.__name__, function)
            return function
        return register

    def run(self, **kwargs):
        pass


class MCPOrdering(unittest.TestCase):
    def setUp(self):
        self.config = {'root': '/unused-mac-work-ordering-fixture'}
        self.server = PersistentServer()
        fastmcp = SimpleNamespace(FastMCP=lambda name: self.server)
        with patch.dict(sys.modules, {'fastmcp': fastmcp}):
            mac_work.serve(self.config)

    def assert_refused_before_work(self, tool, **arguments):
        events = []
        original_import = builtins.__import__

        def observe_import(name, *args, **kwargs):
            if name in {'queue_core', 'queue_lifecycle', 'handoff', 'diagnostics'}:
                events.append(f'import {name}')
                if name.startswith('queue_'):
                    return SimpleNamespace()
            return original_import(name, *args, **kwargs)

        def refuse(config):
            self.assertIs(config, self.config)
            events.append('validate')
            raise ValueError('fixture integrity refusal')

        with (patch('builtins.__import__', side_effect=observe_import),
              patch.object(runner, 'activation_lock', return_value=nullcontext()),
              patch.object(runner_config, 'activation_lock', return_value=nullcontext()),
              patch.object(runner, 'require_active', side_effect=refuse),
              patch.object(runner_config, 'require_active', side_effect=refuse),
              patch.object(runner, 'request', side_effect=lambda *a: events.append('read worktree')),
              patch.object(runner, 'database', side_effect=AssertionError('Opened admission state')),
              patch.object(runner, 'paths', side_effect=AssertionError('Accessed receipt or log')),
              patch.object(runner.subprocess, 'Popen', side_effect=AssertionError('Spawned work'))):
            with self.assertRaisesRegex(ValueError, '^fixture integrity refusal$'):
                asyncio.run(getattr(self.server, tool)(**arguments))
        self.assertEqual(events, ['validate'])

    def test_run_refuses_before_request_or_queue_import(self):
        self.assert_refused_before_work('run_command', operation_id='test', owner='fixture',
                                        worktree='/unused-worktree', argv=['/usr/bin/true'])

    def test_status_refuses_before_state_access(self):
        self.assert_refused_before_work('command_status', operation_id='test')

    def test_cancel_refuses_before_queue_import(self):
        self.assert_refused_before_work('cancel_command', operation_id='test')
