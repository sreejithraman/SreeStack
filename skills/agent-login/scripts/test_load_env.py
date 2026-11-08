import os
from pathlib import Path
import subprocess
import tempfile
import unittest

LOADER = Path(__file__).with_name("load-env.sh")

FIXTURE = """\
# comment
PLAIN=value

export EXPORTED=from export
SINGLE_QUOTE=it's "here"
QUOTED="double quoted"
SQUOTED='single quoted'
DOLLAR=$HOME and `date`
CRLF=line\r
PRESET=from file
EMPTY_PRESET=from file
1BAD=skipped
BAD-KEY=skipped
no equals sign
"""


def load(fixture, preset):
    """Evaluate the loader's output in a clean shell and return the resulting variables."""
    with tempfile.TemporaryDirectory() as directory:
        env_file = Path(directory) / "shared.env"
        env_file.write_text(fixture)
        environment = {"PATH": os.environ["PATH"], "AGENTS_SHARED_ENV": str(env_file), **preset}
        output = subprocess.run(
            ["sh", "-c", 'eval "$(sh "$1")" && env -0', "sh", str(LOADER)],
            env=environment, capture_output=True, check=True,
        ).stdout.decode()
    return dict(entry.split("=", 1) for entry in output.split("\0") if entry)


class LoadEnvTest(unittest.TestCase):
    def setUp(self):
        self.loaded = load(FIXTURE, {"PRESET": "from parent", "EMPTY_PRESET": ""})

    def test_values_are_literal(self):
        self.assertEqual(self.loaded["PLAIN"], "value")
        self.assertEqual(self.loaded["SINGLE_QUOTE"], "it's \"here\"")
        self.assertEqual(self.loaded["DOLLAR"], "$HOME and `date`")
        self.assertEqual(self.loaded["CRLF"], "line")

    def test_surrounding_quotes_and_export_prefix(self):
        self.assertEqual(self.loaded["QUOTED"], "double quoted")
        self.assertEqual(self.loaded["SQUOTED"], "single quoted")
        self.assertEqual(self.loaded["EXPORTED"], "from export")

    def test_existing_variables_win(self):
        self.assertEqual(self.loaded["PRESET"], "from parent")
        self.assertEqual(self.loaded["EMPTY_PRESET"], "")

    def test_skips_invalid_lines(self):
        self.assertNotIn("1BAD", self.loaded)
        self.assertNotIn("BAD-KEY", self.loaded)
        self.assertFalse(any(key.startswith(("#", "no ")) for key in self.loaded))

    def test_missing_file_prints_nothing(self):
        result = subprocess.run(
            ["sh", str(LOADER)], env={"AGENTS_SHARED_ENV": "/nonexistent/shared.env"},
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
