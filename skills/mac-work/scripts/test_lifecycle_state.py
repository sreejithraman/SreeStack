"""Existing-state refusal through the maintained dependency's validation seam."""

import json
from pathlib import Path
import sqlite3
import types
import unittest


class ExistingState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch = (Path(__file__).resolve().parent.parent / 'patches/lifecycle.patch').read_text()
        section = patch.split('+++ b/queue_lifecycle.py\n', 1)[1].split('\n--- ', 1)[0]
        source = '\n'.join(line[1:] for line in section.splitlines() if line.startswith('+'))
        cls.lifecycle = types.ModuleType('maintained_lifecycle')
        exec(compile(source, 'maintained queue_lifecycle.py', 'exec'), cls.lifecycle.__dict__)

    def database(self):
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.executescript('''
            CREATE TABLE queue (id INTEGER PRIMARY KEY, queue_name TEXT, status TEXT,
                pid INTEGER, server_id TEXT, child_pid INTEGER, command TEXT,
                working_directory TEXT, worktree_root TEXT, repo_name TEXT,
                git_branch TEXT, agent_name TEXT, created_at TEXT, updated_at TEXT,
                lifecycle_json TEXT);
            CREATE TABLE task_results (task_id INTEGER PRIMARY KEY, result_json TEXT,
                completed_at TEXT);
            CREATE TABLE task_operations (operation_id TEXT PRIMARY KEY, request_json TEXT,
                request_sha256 TEXT, task_id INTEGER UNIQUE, configuration_sha256 TEXT,
                worker_json TEXT);
            CREATE TABLE admission_policy (singleton INTEGER PRIMARY KEY, policy_json TEXT);
        ''')
        conn.execute('INSERT INTO admission_policy VALUES (1, ?)', (json.dumps({
            'schema': 1, 'capacities': {'heavy': 1}, 'ownership_contract': 'process-group'}, sort_keys=True),))
        conn.commit()
        return conn

    def test_compatible_existing_policy_can_be_read_without_changes(self):
        conn = self.database()
        before = conn.total_changes
        self.lifecycle.configure(conn, {'heavy': 1}, 'process-group')
        self.assertEqual(conn.total_changes, before)

    def test_missing_table_is_refused_without_repair(self):
        conn = self.database()
        conn.execute('DROP TABLE task_operations')
        before = list(conn.iterdump())
        with self.assertRaisesRegex(ValueError, 'schema missing/incompatible'):
            self.lifecycle.validate_state(conn)
        self.assertEqual(list(conn.iterdump()), before)

    def test_missing_policy_cannot_be_silently_reconfigured(self):
        conn = self.database()
        conn.execute('DELETE FROM admission_policy')
        conn.commit()
        before = list(conn.iterdump())
        with self.assertRaisesRegex(ValueError, 'policy missing/incompatible'):
            self.lifecycle.configure(conn, {'heavy': 1}, 'process-group')
        self.assertEqual(list(conn.iterdump()), before)

    def test_existing_uncontained_policy_cannot_be_reinterpreted(self):
        conn = self.database()
        with self.assertRaisesRegex(ValueError, 'configuration mismatch'):
            self.lifecycle.configure(conn, {'heavy': 1}, 'uncontained')
        self.lifecycle.configure(conn, {'heavy': 1}, 'process-group')


if __name__ == '__main__':
    unittest.main()
