"""Artifact boundary expectations independent of queue implementation."""

from pathlib import Path
import tempfile
import unittest

from handoff import artifacts


class ArtifactBoundary(unittest.TestCase):
    def test_exact_files_tree_and_internal_links_are_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            app = Path(directory).resolve() / 'app'; app.mkdir()
            (app/'binary').write_bytes(b'abc')
            (app/'current').symlink_to('binary')
            result = artifacts([str(app)])
            self.assertEqual(result[0]['path'], str(app))
            entries = {v['name']: v for v in result[0]['entries']}
            self.assertEqual(entries['binary']['sha256'], 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            self.assertEqual(entries['current']['target'], 'binary')
            (app/'binary').write_bytes(b'changed')
            self.assertNotEqual(artifacts([str(app)]), result)

    def test_external_links_and_special_files_refuse_instead_of_hashing_foreign_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); app = root/'app'; app.mkdir()
            (root/'foreign').write_text('not this artifact')
            (app/'escape').symlink_to('../foreign')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                artifacts([str(app)])
            (app/'escape').unlink()
            import os
            os.mkfifo(app/'pipe')
            with self.assertRaisesRegex(ValueError, 'only files'):
                artifacts([str(app)])

    def test_relative_missing_and_repeated_roots_refuse(self):
        for names in ([], ['relative'], ['/missing-artifact-foo'], ['/tmp','/tmp']):
            with self.subTest(names=names), self.assertRaises(ValueError):
                artifacts(names)


if __name__ == '__main__':
    unittest.main()
