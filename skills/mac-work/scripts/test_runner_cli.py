"""Fast public CLI validation checks; runtime integration is a separate fixture."""

from pathlib import Path
import subprocess
import json
import hashlib
import sqlite3
import fcntl
import shutil
import sys
import tempfile
import unittest

CLI = Path(__file__).with_name('mac_work.py')


class RunnerCLI(unittest.TestCase):
    def test_missing_configuration_refuses_instead_of_running_directly(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'executed'
            result = subprocess.run([sys.executable, str(CLI), '--config', str(Path(directory)/'current.json'),
                                     'run', '--id', 'no-fallback', '--owner', 'test',
                                     '--worktree', str(Path.cwd()), '--', sys.executable, '-c',
                                     f'from pathlib import Path; Path({str(marker)!r}).touch()'],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('mac-work refused:', result.stderr)
            self.assertFalse(marker.exists())


    def test_bound_launcher_does_not_consume_command_config_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();(root/'bin').mkdir();launcher=root/'bin/mac-work'
            shutil.copyfile(CLI.with_name('runner_bootstrap.py'),launcher)
            result=subprocess.run([sys.executable,str(launcher),'run','--id','fixture','--','tool','--config','project.json','--config=other.json'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('current.json',result.stderr)
            self.assertNotIn('bound to its own',result.stderr)
            wrong=subprocess.run([sys.executable,str(launcher),'--config',str(root/'other.json'),'status','--id','fixture'],capture_output=True,text=True)
            self.assertEqual(wrong.returncode,2)
            self.assertIn('bound to its own',wrong.stderr)

    def test_policy_cannot_select_an_unrelated_root_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();version=root/'versions/one';version.mkdir(parents=True)
            config={'schema':1,'root':str(root),'state':str(root/'state'),'runtime':str(version/'build/runtime'),
                    'policy':{'schema':1,'capacities':{'other':9},'ownership_contract':'process-group'}}
            path=version/'config.json';path.write_text(json.dumps(config))
            pointer=root/'current.json';pointer.write_text(json.dumps({'schema':1,'configuration':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
            result=subprocess.run([sys.executable,str(CLI),'--config',str(pointer),'status','--id','unknown','--json'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('Canonical policy/state mismatch',result.stderr)

    def test_config_drift_is_refused_before_importing_a_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();version=root/'versions/one';version.mkdir(parents=True)
            config=version/'config.json';config.write_text('{}')
            pointer=root/'current.json';pointer.write_text(json.dumps({'schema':1,'configuration':str(config),'sha256':'0'*64}))
            result=subprocess.run([sys.executable,str(CLI),'--config',str(pointer),'status','--id','unknown'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('Configuration hash mismatch',result.stderr)

    def test_unlisted_bundle_source_is_refused_before_runtime_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();version=root/'versions/one';bundle=version/'bundle';bundle.mkdir(parents=True)
            (bundle/'unexpected.py').write_text('raise RuntimeError("must never import")')
            manifest=version/'bundle-manifest.json';manifest.write_text('{}')
            config={'schema':1,'root':str(root),'state':str(root/'state'),'runtime':str(version/'build/runtime'),
                    'policy':{'schema':1,'capacities':{'heavy':1},'ownership_contract':'process-group'},
                    'bundle_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}
            path=version/'config.json';path.write_text(json.dumps(config))
            pointer=root/'current.json';pointer.write_text(json.dumps({'schema':1,'configuration':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
            result=subprocess.run([sys.executable,str(CLI),'--config',str(pointer),'status','--id','unknown'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('Bundle file set mismatch',result.stderr)

    def assert_activation_refuses(self, status, contract, expected):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();state=root/'state';state.mkdir()
            with sqlite3.connect(state/'queue.db') as conn:
                conn.execute('CREATE TABLE queue(status TEXT)')
                if status:conn.execute('INSERT INTO queue VALUES (?)',(status,))
                conn.execute('CREATE TABLE admission_policy(singleton INTEGER,policy_json TEXT)')
                conn.execute('INSERT INTO admission_policy VALUES(1,?)',(json.dumps({'schema':1,'capacities':{'heavy':1},'ownership_contract':contract}),))
            original=(state/'queue.db').read_bytes()
            result=subprocess.run([sys.executable,str(CLI),'activate','--root',str(root),'--release','missing'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn(expected,result.stderr)
            self.assertEqual((state/'queue.db').read_bytes(),original)
            self.assertFalse((root/'current.json').exists())

    def test_unresolved_capacity_blocks_rollback_without_changing_state(self):
        self.assert_activation_refuses('running','process-group','unresolved admission remains')

    def test_existing_uncontained_policy_is_never_reinterpreted(self):
        self.assert_activation_refuses(None,'uncontained','no uncontained-state migration')

    def test_active_worker_lock_refuses_activation_without_waiting_for_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            with (Path(directory)/'activation.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_SH)
                result=subprocess.run([sys.executable,str(CLI),'activate','--root',directory,'--release','missing'],capture_output=True,text=True,timeout=1)
            self.assertEqual(result.returncode,2)
            self.assertIn('Activation refused',result.stderr)

    def test_release_cannot_escape_the_version_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result=subprocess.run([sys.executable,str(CLI),'activate','--root',directory,'--release','../other'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('Invalid release name',result.stderr)


if __name__ == '__main__':
    unittest.main()
