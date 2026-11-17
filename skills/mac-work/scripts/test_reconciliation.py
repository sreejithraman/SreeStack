"""Recorded-deadline and ownership behavior through real receipt closure."""

from datetime import datetime
import json
from pathlib import Path
import sqlite3
import time
import types
import unittest
from unittest.mock import patch


def maintained_lifecycle():
    source = (Path(__file__).resolve().parent.parent / 'patches/lifecycle.patch').read_text()
    section = source.split('+++ b/queue_lifecycle.py\n', 1)[1].split('\n--- ', 1)[0]
    module = types.ModuleType('maintained_lifecycle')
    exec(compile('\n'.join(line[1:] for line in section.splitlines() if line.startswith('+')),
                 'maintained_queue_lifecycle.py', 'exec'), module.__dict__)
    return module


class Reconciliation(unittest.TestCase):
    def observe(self, *, age, remaining, allowance=10800, dead=False, cancelled=False, child=True, zombie=False):
        lifecycle = maintained_lifecycle()
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.row_factory = sqlite3.Row
        conn.executescript('''CREATE TABLE queue(id INTEGER PRIMARY KEY,queue_name TEXT,status TEXT,
            pid INTEGER,server_id TEXT,child_pid INTEGER,command TEXT,working_directory TEXT,
            worktree_root TEXT,agent_name TEXT,created_at TEXT,updated_at TEXT,lifecycle_json TEXT);
            CREATE TABLE task_results(task_id INTEGER PRIMARY KEY,result_json TEXT,completed_at TEXT);''')
        now = time.time()
        owner = {'pid': 101, 'pgid': 101, 'birth': [1, 1], 'zombie': False}
        group = {'pid': 102, 'pgid': 102, 'birth': [2, 2], 'zombie': False}
        meta = {'owner': owner, 'boot': 'fixture-boot', 'state': 'executing',
                'ownership_contract': 'process-group', 'execution_seconds': allowance,
                'admitted_at': now - age}
        if remaining is not None:
            meta['execution_deadline'] = now + remaining
        if child:
            meta['child'] = group
        if cancelled:
            meta.update(state='closing', result={'status': 'cancelled', 'duration_seconds': 0})
        stamp = datetime.fromtimestamp(now - age).isoformat()
        conn.execute('INSERT INTO queue VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?)',
            ('heavy', 'running', 101, 'fixture', 102 if child else None, 'fixture command',
             None, None, 'fixture', stamp, stamp, json.dumps(meta)))
        conn.commit()
        signals = []

        def identity(pid):
            if pid == 101:
                return None if dead else {**owner, 'zombie': zombie}
            return group if pid == 102 else None

        observations = types.SimpleNamespace(getpid=lambda: 999,
            killpg=lambda pgid, signum: signals.append((pgid, int(signum))))
        with patch.object(lifecycle, 'process_identity', side_effect=identity), patch.object(
                lifecycle, 'boot_identity', return_value='fixture-boot'), patch.object(
                lifecycle, 'group_members', side_effect=lambda pgid: [] if signals else [group]), patch.object(
                lifecycle, 'os', observations):
            lifecycle.reconcile(conn, 'heavy', 120)
        return lifecycle.read_task(conn, 1), signals

    def test_long_unexpired_recorded_allowance_survives_legacy_age(self):
        value, signals = self.observe(age=7201, remaining=3599)
        self.assertEqual(value['status'], 'running')
        self.assertTrue(value['capacity_held'])
        self.assertEqual(signals, [])

    def test_expired_short_deadline_records_its_allowance_and_closes_group(self):
        value, signals = self.observe(age=5, remaining=-4, allowance=1)
        self.assertEqual(value['status'], 'timeout')
        self.assertEqual(value['timeout_seconds'], 1)
        self.assertEqual(value['duration_seconds'], 1)
        self.assertFalse(value['capacity_held'])
        self.assertEqual(signals, [(102, 15)])

    def test_only_legacy_no_deadline_uses_age_fallback(self):
        fresh, signals = self.observe(age=1, remaining=None)
        self.assertEqual(fresh['status'], 'running')
        self.assertEqual(signals, [])
        expired, signals = self.observe(age=7201, remaining=None)
        self.assertEqual(expired['status'], 'interrupted')
        self.assertFalse(expired['capacity_held'])
        self.assertEqual(signals, [(102, 15)])

    def test_expired_deadline_does_not_replace_cancellation(self):
        value, signals = self.observe(age=5, remaining=-4, allowance=1, cancelled=True)
        self.assertEqual(value['status'], 'cancelled')
        self.assertFalse(value['capacity_held'])
        self.assertEqual(signals, [(102, 15)])

    def test_dead_owner_reconciles_before_unexpired_deadline(self):
        value, signals = self.observe(age=1, remaining=3599, dead=True)
        self.assertEqual(value['status'], 'interrupted')
        self.assertFalse(value['capacity_held'])
        self.assertEqual(signals, [(102, 15)])

    def test_unknown_owner_without_child_retains_spawn_window(self):
        value, signals = self.observe(age=1, remaining=3599, dead=True, child=False)
        self.assertEqual(value['status'], 'recovery-pending')
        self.assertTrue(value['capacity_held'])
        self.assertEqual(signals, [])

    def test_matching_zombie_owner_is_dead_and_closes_exact_group(self):
        value, signals = self.observe(age=1, remaining=3599, zombie=True)
        self.assertEqual(value['status'], 'interrupted')
        self.assertFalse(value['capacity_held'])
        self.assertEqual(signals, [(102, 15)])

    def test_zombie_owner_without_recorded_child_keeps_spawn_window(self):
        value, signals = self.observe(age=1, remaining=3599, zombie=True, child=False)
        self.assertEqual(value['status'], 'recovery-pending')
        self.assertTrue(value['capacity_held'])
        self.assertEqual(signals, [])


if __name__ == '__main__':
    unittest.main()
