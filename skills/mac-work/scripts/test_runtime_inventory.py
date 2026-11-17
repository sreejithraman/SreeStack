"""Complete code-tree verification without executing a candidate interpreter."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import runtime_inventory as inventory
from runtime_drift_fitness import private_replace


class RuntimeInventory(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='runtime-inventory-')).resolve()
        self.addCleanup(self.cleanup)
        for name in inventory.ROOTS:
            (self.root / name).mkdir()
        self.code = self.root / 'runtime/dependency.py'
        self.code.write_bytes(b'approved dependency body\n')
        (self.root / 'python/python').write_bytes(b'private interpreter fixture\n')
        (self.root / 'runtime/python').symlink_to('../python/python')
        value = inventory.seal(self.root)
        path = self.root / 'runtime-manifest.json'
        path.write_text(json.dumps(value))
        self.receipt = self.root / 'build-receipt.json'
        self.receipt.write_text(json.dumps({'schema': 2, 'runtime': str(self.root / 'runtime'),
                                           'runtime_manifest_sha256': inventory.digest(path)}))
        self.expected = inventory.digest(self.receipt)

    def cleanup(self):
        for directory, names, files in os.walk(self.root, followlinks=False):
            os.chmod(directory, 0o700)
        shutil.rmtree(self.root)

    def test_complete_sealed_inventory_is_stable(self):
        first = inventory.verify(self.root, self.expected)
        self.assertEqual(inventory.verify(self.root, self.expected), first)

    def test_same_version_dependency_body_change_refuses(self):
        private_replace(self.code, b'changed dependency body\n')
        with self.assertRaisesRegex(ValueError, 'content mismatch|type/mode/link mismatch'):
            inventory.verify(self.root, self.expected)

    def test_extra_startup_bytecode_or_distribution_refuses(self):
        for name in ('startup.pth', 'sitecustomize.py', 'unchecked.pyc', 'extra.dist-info'):
            with self.subTest(name=name):
                path = self.root / 'runtime' / name
                private_replace(path, b'unapproved startup or installed code')
                try:
                    with self.assertRaisesRegex(ValueError, 'file set mismatch'):
                        inventory.verify(self.root, self.expected)
                finally:
                    os.chmod(path.parent, 0o755)
                    path.unlink()
                    os.chmod(path.parent, 0o555)

    def test_symlink_cannot_replace_a_regular_body_even_with_identical_bytes(self):
        parent = self.code.parent
        os.chmod(parent, 0o755)
        self.code.unlink()
        self.code.symlink_to('../python/python')
        os.chmod(parent, 0o555)
        with self.assertRaisesRegex(ValueError, 'type/mode/link mismatch'):
            inventory.verify(self.root, self.expected)

    def test_symlink_escape_and_special_file_refuse_without_reading(self):
        os.chmod(self.code.parent, 0o755)
        self.code.unlink()
        self.code.symlink_to(self.root / 'runtime-manifest.json')
        with self.assertRaisesRegex(ValueError, 'symlink escapes'):
            inventory.verify(self.root, self.expected)
        self.code.unlink()
        os.mkfifo(self.code)
        with self.assertRaisesRegex(ValueError, 'special file'):
            inventory.verify(self.root, self.expected)

    def test_external_hardlink_alias_is_refused(self):
        os.link(self.code, self.root / 'external-alias')
        with self.assertRaisesRegex(ValueError, 'shares an inode'):
            inventory.verify(self.root, self.expected)

    def test_receipt_is_bound_before_inventory_is_trusted(self):
        self.receipt.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'build receipt hash mismatch'):
            inventory.verify(self.root, self.expected)


if __name__ == '__main__':
    unittest.main()
