"""Check the qualification CLI's refusal boundary without installing a queue."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent


class FitnessCLI(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='mac-work-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.runtime = self.root / 'runtime'
        (self.runtime / 'bin').mkdir(parents=True)
        self.output = self.root / 'proof'
        self.marker = self.root / 'queue-was-invoked'
        tq = self.runtime / 'bin/tq'
        tq.write_text(f'#!{sys.executable}\nfrom pathlib import Path\nPath({str(self.marker)!r}).touch()\n')
        tq.chmod(0o700)

    def metadata(self, **changes):
        info = {'python': '3.12.12', 'queue': '0.4.1', 'files': {}}
        for name in ('queue_core', 'tq', 'task_queue'):
            module = self.root / (name + '.py')
            module.write_text('print("unverified source")\n')
            info['files'][name] = str(module)
        info['packages'] = {}
        for line in (SCRIPTS / 'runtime.lock').read_text().splitlines():
            if line and line[0].isalnum() and '==' in line:
                name, version = line.split('==', 1)
                info['packages'][name] = version.split()[0]
        if 'fakeredis' in changes:
            info['packages']['fakeredis'] = changes.pop('fakeredis')
        info.update(changes)
        python = self.runtime / 'bin/python'
        # This is only the runtime metadata probe, never a stand-in queue engine.
        python.write_text(f'#!{sys.executable}\nprint({json.dumps(info)!r})\n')
        python.chmod(0o700)

    def refuse(self, message):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'fitness.py'),
                                 '--runtime', str(self.runtime), '--output', str(self.output)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertFalse(self.marker.exists(), 'unverified queue was invoked')
        self.assertFalse(self.output.exists(), 'refusal created a proof run')

    def test_missing_runtime_never_falls_back_to_path_queue(self):
        self.refuse('Fitness setup refused:')

    def test_incompatible_transitive_pin_is_refused_before_queue_invocation(self):
        self.metadata(fakeredis='2.40.0')
        self.refuse('runtime version mismatch')

    def test_changed_upstream_source_is_refused_before_queue_invocation(self):
        self.metadata()
        self.refuse('upstream hash mismatch')

    def test_wrong_package_version_is_refused_before_queue_invocation(self):
        self.metadata(queue='0.4.0')
        self.refuse('runtime version mismatch')


if __name__ == '__main__':
    unittest.main()
