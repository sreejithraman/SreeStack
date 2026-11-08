import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).parent
LOADER = SCRIPTS / "load-env.sh"
MACHINE_SETUP = SCRIPTS.parent / "references/machine-setup.md"

ACCEPTED = """\
# comment
# a comment's \\ "quotes" and backslashes are ignored
PLAIN=value

export EXPORTED='from export'
SPACED = spaced
APOSTROPHE="it's here"
LITERAL='$HOME `date`'
QUOTED="double quoted"
EMPTY=
CRLF=line\r
INHERITED="from file"
DUPLICATE=first
DUPLICATE=last
CLAUDE_CODE_SKIPPED=file
claude_lower=file
"""

SECRET = "s3cret"
# Each entry rejects the whole file; its first line is the one reported.
REJECTED = {
    "unquoted comment": f"KEY={SECRET} # comment",
    "unquoted space": f"KEY={SECRET} x",
    "unquoted substitution": f"KEY={SECRET}$HOME",
    "double-quoted substitution": f'KEY="{SECRET}$HOME"',
    "invalid key": f"BAD-KEY={SECRET}",
    "leading digit": f"1KEY={SECRET}",
    "no equals sign": f"no equals {SECRET}",
    "unsupported value under a filtered key": f"CLAUDE_KEY={SECRET} x",
    "inline comment after quote": f'KEY="{SECRET}" # comment',
    "escaped quote": f'KEY="{SECRET}\\"x"',
    "escape": f'KEY="{SECRET}\\nx"',
    "inner quote": f"KEY='{SECRET}'x'",
    "unterminated": f'KEY="{SECRET}',
    "multiline": f'KEY="{SECRET}\nSMUGGLED=evil"',
    "escaped quote on continuation": f'KEY="begin\nescaped=\\"\nSMUGGLED=evil\nend{SECRET}"',
    "filtered key": f'CLAUDE_SECRET="begin\nSMUGGLED=evil\nend{SECRET}"',
    "multiline under invalid key": f'BAD-KEY="begin\nSMUGGLED=evil\nend{SECRET}"',
    "backslash before single closing quote": f"KEY='{SECRET}\\'",
}


def run_loader(fixture, preset=None):
    """Evaluate the loader's output in a clean shell; return the variables and stderr."""
    with tempfile.TemporaryDirectory() as directory:
        env_file = Path(directory) / "shared.env"
        env_file.write_bytes(fixture if isinstance(fixture, bytes) else fixture.encode())
        environment = {"PATH": os.environ["PATH"], "AGENTS_SHARED_ENV": str(env_file), **(preset or {})}
        result = subprocess.run(
            ["sh", "-c", 'eval "$(sh "$1")" && env -0', "sh", str(LOADER)],
            env=environment, capture_output=True, check=True,
        )
    variables = dict(entry.split("=", 1) for entry in result.stdout.decode().split("\0") if entry)
    return variables, result.stderr.decode()


def assert_rejected(test, fixture, line, preset=None):
    """Assert that nothing loads and one value-free warning names the line."""
    loaded, warnings = run_loader(fixture, preset)
    test.assertFalse({"BEFORE", "KEY", "SMUGGLED", "AFTER", "OP_SERVICE_ACCOUNT_TOKEN"} & loaded.keys())
    test.assertNotIn(SECRET, warnings)
    test.assertRegex(warnings, rf"^load-env: [^\n]*{line}[^\n]*; nothing exported\n$")


class RejectedFileTest(unittest.TestCase):
    def test_any_unsupported_entry_rejects_the_file(self):
        for name, entry in REJECTED.items():
            with self.subTest(name):
                assert_rejected(self, f"BEFORE=ok\n{entry}\nOP_SERVICE_ACCOUNT_TOKEN=marker\n", ":2: ")

    def test_unsupported_later_duplicate_rejects_the_file(self):
        for name, later in {"Unicode space before key": "\u2003\tKEY=new",
                            "inline comment": f"KEY={SECRET} # comment"}.items():
            with self.subTest(name):
                assert_rejected(self, f"BEFORE=ok\nKEY=old\n{later}\nAFTER=ok\n", ":3: ")

    def test_trailing_whitespace_needs_a_final_newline(self):
        cases = {
            "KEY=value ": "value", "KEY= ": "", 'KEY="quoted" ': "quoted", "KEY='quoted'\t": "quoted",
        }
        for entry, value in cases.items():
            with self.subTest(entry):
                loaded, warnings = run_loader(f"{entry}\n")
                self.assertEqual((loaded["KEY"], warnings), (value, ""))
                assert_rejected(self, f"BEFORE=ok\n{entry}", ":2: whitespace at end of file")
        assert_rejected(self, "KEY=old\nKEY=new ", ":2: ")

    def test_value_without_final_newline_loads(self):
        loaded, warnings = run_loader("KEY=value")
        self.assertEqual((loaded["KEY"], warnings), ("value", ""))

    def test_unquoted_unicode_whitespace_rejects_the_file(self):
        for locale in ("C", "en_US.UTF-8"):
            for space in ("\u00a0", "\u2003"):
                for entry in (f"KEY={space}{SECRET}", f"KEY={SECRET}{space}"):
                    with self.subTest(locale=locale, entry=ascii(entry)):
                        assert_rejected(self, f"BEFORE=ok\n{entry}\nAFTER=ok\n", ":2: [^\\n]*non-ASCII",
                                        {"LC_ALL": locale})

    def test_quoted_unicode_stays_literal(self):
        for locale in ("C", "en_US.UTF-8"):
            with self.subTest(locale):
                loaded, warnings = run_loader('KEY="\u00a0value\u2003"\n', {"LC_ALL": locale})
                self.assertEqual((loaded["KEY"], warnings), ("\u00a0value\u2003", ""))

    def test_files_that_are_not_utf8_text_export_nothing(self):
        secret = SECRET.encode()
        cases = {
            "invalid byte in double quotes": b'KEY="' + secret + b'\xff"',
            "invalid byte in single quotes": b"KEY='" + secret + b"\xff'",
            "truncated sequence": b'KEY="' + secret + b'\xc3("',
            "above U+10FFFF": b'KEY="' + secret + b'\xf4\x90\x80\x80"',
            "NUL byte": b"KEY=" + secret + b"\x00value",
        }
        for name, entry in cases.items():
            with self.subTest(name):
                assert_rejected(self, b"BEFORE=ok\n" + entry + b"\nAFTER=ok\n", ": not UTF-8 text without NUL bytes")

    def test_quoted_utf8_loads(self):
        loaded, warnings = run_loader('BEFORE=ok\nKEY="caf\u00e9"\n'.encode())
        self.assertEqual((loaded["BEFORE"], loaded["KEY"], warnings), ("ok", "caf\u00e9", ""))


class AcceptedEntriesTest(unittest.TestCase):
    def setUp(self):
        self.loaded, self.warnings = run_loader(
            ACCEPTED, {"INHERITED": "from parent", "CLAUDE_CODE_SKIPPED": "from parent"})

    def test_accepts_without_warnings(self):
        self.assertEqual(self.warnings, "")

    def test_values_are_literal(self):
        self.assertEqual(self.loaded["PLAIN"], "value")
        self.assertEqual(self.loaded["APOSTROPHE"], "it's here")
        self.assertEqual(self.loaded["LITERAL"], "$HOME `date`")
        self.assertEqual(self.loaded["QUOTED"], "double quoted")
        self.assertEqual(self.loaded["EMPTY"], "")
        self.assertEqual(self.loaded["CRLF"], "line")

    def test_export_prefix_and_whitespace_around_equals(self):
        self.assertEqual(self.loaded["EXPORTED"], "from export")
        self.assertEqual(self.loaded["SPACED"], "spaced")

    def test_file_wins_and_last_duplicate_wins(self):
        self.assertEqual(self.loaded["INHERITED"], "from file")
        self.assertEqual(self.loaded["DUPLICATE"], "last")

    def test_claude_keys_are_skipped(self):
        self.assertEqual(self.loaded["CLAUDE_CODE_SKIPPED"], "from parent")
        self.assertNotIn("claude_lower", self.loaded)

    def test_missing_file_prints_nothing(self):
        result = subprocess.run(
            ["sh", str(LOADER)], env={"AGENTS_SHARED_ENV": "/nonexistent/shared.env"},
            capture_output=True, text=True, check=True,
        )
        self.assertEqual((result.stdout, result.stderr), ("", ""))


class SessionStartHookTest(unittest.TestCase):
    def test_documented_hook_loads_shared_file_from_custom_config_dir(self):
        hook = re.search(r"```sh\n(line=.*CLAUDE_ENV_FILE.*)\n```", MACHINE_SETUP.read_text()).group(1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home, config = root / "home", root / "custom-claude"
            shared = home / ".config/agents/shared.env"
            shared.parent.mkdir(parents=True)
            shared.write_text("DEMO=private-marker\n")
            installed = config / "skills/agent-login/scripts/load-env.sh"
            installed.parent.mkdir(parents=True)
            shutil.copy(LOADER, installed)
            environment = {"PATH": os.environ["PATH"], "HOME": str(home), "CLAUDE_CONFIG_DIR": str(config)}
            env_file = root / "claude-env"
            for _ in range(2):
                subprocess.run(["sh", "-c", hook], env={**environment, "CLAUDE_ENV_FILE": str(env_file)},
                               check=True)
            self.assertEqual(len(env_file.read_text().splitlines()), 1)
            result = subprocess.run(
                ["sh", "-c", '. "$1" && printf %s "$DEMO"', "sh", str(env_file)],
                env=environment, capture_output=True, text=True, check=True,
            )
        self.assertEqual((result.stdout, result.stderr), ("private-marker", ""))


if __name__ == "__main__":
    unittest.main()
