"""Check exact artifact refusals through the build recipe's public CLI."""

import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

BUNDLE = Path(__file__).resolve().parent.parent


class RuntimeRecipe(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='lifecycle-recipe-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = self.root / 'mac-work'
        self.bundle.mkdir()
        for name in ('candidate.json', 'scripts/build_runtime.py', 'scripts/runtime.lock',
                     'scripts/build.lock', 'patches/lifecycle.patch', 'NOTICE.md', 'licenses/agent-task-queue.txt'):
            path = self.bundle / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BUNDLE / name, path)
        self.script = self.bundle / 'scripts/build_runtime.py'
        self.destination = self.root / 'never-created'

    def call(self, *arguments):
        return subprocess.run([sys.executable, str(self.script), *arguments],
                              text=True, capture_output=True, timeout=10)

    def test_pinned_inputs_are_accepted_without_installing_packages(self):
        result = self.call('check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('verified', result.stdout)

    def refuse(self, message, *arguments):
        result = self.call('build', '--root', str(self.destination), *arguments)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertFalse(self.destination.exists(), 'unverified input started a runtime build')

    def test_changed_source_archive_is_refused_before_extraction(self):
        archive = self.root / 'upstream.tar.gz'
        archive.write_bytes(b'not the pinned archive')
        self.refuse('Source archive hash mismatch', '--archive', str(archive))

    def test_changed_patch_is_refused_before_build(self):
        patch = self.root / 'patch'
        patch.write_text('unexpected patch')
        self.refuse('Input hash mismatch: patches/lifecycle.patch', '--patch', str(patch))

    def test_changed_runtime_dependencies_are_refused_before_build(self):
        with (self.bundle / 'scripts/runtime.lock').open('a') as lock:
            lock.write('\nunapproved-dependency==1.0\n')
        self.refuse('Input hash mismatch: scripts/runtime.lock')

    def test_changed_build_backend_is_refused_before_build(self):
        (self.bundle / 'scripts/build.lock').write_text('hatchling==0.0\n')
        self.refuse('Input hash mismatch: scripts/build.lock')

    def test_unknown_runtime_receipt_schema_is_refused_before_probing_runtime(self):
        runtime = self.root / 'install/runtime'
        runtime.parent.mkdir()
        value = {'schema': 999, 'candidate_sha256': hashlib.sha256((self.bundle / 'candidate.json').read_bytes()).hexdigest()}
        (runtime.parent / 'build-receipt.json').write_text(json.dumps(value))
        result = self.call('verify', '--runtime', str(runtime))
        self.assertEqual(result.returncode, 2)
        self.assertIn('Unsupported build receipt schema', result.stderr)

    def test_unknown_candidate_schema_is_refused(self):
        path = self.bundle / 'candidate.json'
        value = json.loads(path.read_text())
        value['schema'] = 999
        path.write_text(json.dumps(value))
        self.refuse('Unsupported candidate schema')


if __name__ == '__main__':
    unittest.main()
