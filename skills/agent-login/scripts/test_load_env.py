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
SKIPPED_ENTRIES = {
    "UNQUOTED_COMMENT": f"UNQUOTED_COMMENT={SECRET} # comment",
    "SUBSTITUTION": f'SUBSTITUTION="{SECRET}$HOME"',
    "UNQUOTED_SUBSTITUTION": f"UNQUOTED_SUBSTITUTION={SECRET}$HOME",
    "UNQUOTED_SPACE": f"UNQUOTED_SPACE={SECRET} x",
}
# Each form can move entry boundaries; its first line is the one reported.
UNCLEAR_BOUNDARIES = {
    "inline comment after quote": f'KEY="{SECRET}" # comment',
    "escaped quote": f'KEY="{SECRET}\\"x"',
    "escape": f'KEY="{SECRET}\\nx"',
    "inner quote": f"KEY='{SECRET}'x'",
    "unterminated": f'KEY="{SECRET}',
    "multiline": f'KEY="{SECRET}\nSMUGGLED=evil"',
    "escaped quote on continuation": f'KEY="begin\nescaped=\\"\nSMUGGLED=evil\nend{SECRET}"',
    "filtered key": f'CLAUDE_SECRET="begin\nSMUGGLED=evil\nend{SECRET}"',
    "invalid key": f'BAD-KEY="begin\nSMUGGLED=evil\nend{SECRET}"',
    "backslash before single closing quote": f"KEY='{SECRET}\\'",
}


def run_loader(fixture, preset=None):
    """Evaluate the loader's output in a clean shell; return the variables and stderr."""
    with tempfile.TemporaryDirectory() as directory:
        env_file = Path(directory) / "shared.env"
        env_file.write_text(fixture, encoding="utf-8")
        environment = {"PATH": os.environ["PATH"], "AGENTS_SHARED_ENV": str(env_file), **(preset or {})}
        result = subprocess.run(
            ["sh", "-c", 'eval "$(sh "$1")" && env -0', "sh", str(LOADER)],
            env=environment, capture_output=True, check=True,
        )
    variables = dict(entry.split("=", 1) for entry in result.stdout.decode().split("\0") if entry)
    return variables, result.stderr.decode()


class FileEndTest(unittest.TestCase):
    def test_trailing_whitespace_needs_a_final_newline(self):
        cases = {
            "KEY=value ": "value", "KEY= ": "", 'KEY="quoted" ': "quoted", "KEY='quoted'\t": "quoted",
        }
        for entry, value in cases.items():
            with self.subTest(entry):
                loaded, warnings = run_loader(f"{entry}\n")
                self.assertEqual((loaded["KEY"], warnings), (value, ""))
                loaded, warnings = run_loader(f"AFTER=ok\n{entry}")
                self.assertNotIn("KEY", loaded)
                self.assertEqual(loaded["AFTER"], "ok")
                self.assertRegex(warnings, r"^load-env: .*:2: whitespace at end of file[^\n]*\n$")

    def test_duplicate_without_final_newline_keeps_earlier_value(self):
        loaded, warnings = run_loader("KEY=old\nKEY=new ")
        self.assertEqual(loaded["KEY"], "old")
        self.assertRegex(warnings, ":2: ")

    def test_value_without_final_newline_loads(self):
        loaded, warnings = run_loader("KEY=value")
        self.assertEqual((loaded["KEY"], warnings), ("value", ""))


class NonAsciiTest(unittest.TestCase):
    LOCALES = ("C", "en_US.UTF-8")

    def test_unquoted_unicode_whitespace_is_skipped(self):
        for locale in self.LOCALES:
            for space in ("\u00a0", "\u2003"):
                for entry in (f"KEY={space}{SECRET}", f"KEY={SECRET}{space}"):
                    with self.subTest(locale=locale, entry=ascii(entry)):
                        loaded, warnings = run_loader(f"{entry}\nAFTER=ok\n", {"LC_ALL": locale})
                        self.assertNotIn("KEY", loaded)
                        self.assertEqual(loaded["AFTER"], "ok")
                        self.assertNotIn(SECRET, warnings)
                        self.assertRegex(warnings, r"^load-env: .*:1: KEY: [^\n]*non-ASCII")

    def test_quoted_unicode_stays_literal(self):
        for locale in self.LOCALES:
            with self.subTest(locale):
                loaded, warnings = run_loader('KEY="\u00a0value\u2003"\n', {"LC_ALL": locale})
                self.assertEqual((loaded["KEY"], warnings), ("\u00a0value\u2003", ""))


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


class RejectedEntriesTest(unittest.TestCase):
    def test_unsupported_entries_are_skipped(self):
        for key, entry in SKIPPED_ENTRIES.items():
            with self.subTest(key):
                loaded, warnings = run_loader(f"{entry}\nAFTER=ok\n")
                self.assertNotIn(key, loaded)
                self.assertEqual(loaded["AFTER"], "ok")
                self.assertNotIn(SECRET, warnings)
                self.assertRegex(warnings, rf"^load-env: .*:1: {key}: ")

    def test_unclear_boundaries_export_nothing_from_the_file(self):
        for name, entry in UNCLEAR_BOUNDARIES.items():
            with self.subTest(name):
                loaded, warnings = run_loader(f"BEFORE=ok\n{entry}\nOP_SERVICE_ACCOUNT_TOKEN=marker\n")
                self.assertFalse({"BEFORE", "KEY", "SMUGGLED", "OP_SERVICE_ACCOUNT_TOKEN"} & loaded.keys())
                self.assertNotIn(SECRET, warnings)
                self.assertRegex(warnings, r"^load-env: .*:2: [^\n]*nothing exported[^\n]*\n$")

    def test_invalid_keys_warn_without_exporting(self):
        loaded, warnings = run_loader("1BAD=x\nBAD-KEY=x\nno equals sign\n")
        self.assertFalse({"1BAD", "BAD-KEY"} & loaded.keys())
        self.assertEqual(len(warnings.splitlines()), 3)


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
