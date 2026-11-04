"""Exercise the known host settings merges through the sync command."""

import json
import os
import shutil
import stat
import subprocess
import sys
import textwrap
import unittest

from test_sync_hosts import CLAUDE_TEMPLATE, Fixture

try:
    from tomllib import loads as parse_toml
except ImportError:  # Python 3.9 and 3.10 have no standard TOML parser.
    import tomlkit

    def parse_toml(text):
        return tomlkit.parse(text).unwrap()

SECRET = "PRIVATE-VALUE"
SETUP = "pip install -r scripts/requirements-sync.txt"
CLAUDE = ".claude/settings.json"
CODEX = ".codex/config.toml"
CODEX_T3 = ".codex-t3/config.toml"
LOCAL_TOML = f'''# Private header
model = "old" # keep this note
token = "{SECRET}"

[projects."/private/path"]
trust_level = "trusted"

[agents]
# agent note
max_threads = 3
nickname = "{SECRET}"
'''
MERGED_TOML = LOCAL_TOML.replace('"old"', '"template-model"').replace("max_threads = 3", "max_threads = 12")
LOCAL_JSON = {
    "model": "old",
    "token": SECRET,
    "pluginConfigs": {"demo": {"options": {"mode": "off", "extra": SECRET}}, "mine": {"on": True}},
    "résumé": ["ü"],
}
MERGED_JSON = {
    **LOCAL_JSON,
    "model": "template-model",
    "pluginConfigs": {"demo": {"options": {"mode": "on", "extra": SECRET}}, "mine": {"on": True}},
}


class SettingsFixture(Fixture):
    def config(self, relative, content):
        path = self.home / relative
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())
        return path

    def local_configs(self):
        return (self.config(CLAUDE, json.dumps(LOCAL_JSON)), self.config(CODEX, LOCAL_TOML),
                self.config(CODEX_T3, LOCAL_TOML))

    def backups(self, path):
        return list(path.parent.glob(f"{path.name}.backup-*"))

    def assert_no_trace(self, path):
        names = {entry.name for entry in path.parent.iterdir()}
        self.assertEqual({name for name in names if "backup" in name or "sreestack" in name}, set())

    def run_injected(self, setup, *args, code):
        """Run the sync command with a test double installed in its process."""
        driver = self.base / "driver.py"
        driver.write_text(textwrap.dedent(f"""\
            import json, os, runpy, sys, tempfile
            scripts = {str(self.repo / "scripts")!r}
            sys.path.insert(0, scripts)
            import host_settings
        """) + textwrap.dedent(setup) + textwrap.dedent(f"""
            sys.argv = ["sync_hosts.py", "--home", {str(self.home)!r}, *{args!r}]
            runpy.run_path(scripts + "/sync_hosts.py", run_name="__main__")
        """))
        result = subprocess.run([sys.executable, str(driver)], cwd=self.repo, env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result


class MergeTests(SettingsFixture):
    def test_new_configs_hold_only_template_keys_in_private_files(self):
        self.run_sync()

        self.assertEqual(json.loads((self.home / CLAUDE).read_text()), CLAUDE_TEMPLATE)
        for relative in (CODEX, CODEX_T3):
            self.assertEqual((self.home / relative).read_text(),
                             'model = "template-model"\n\n[agents]\nmax_threads = 12\n')
        for relative in (CLAUDE, CODEX, CODEX_T3):
            path = self.home / relative
            self.assertFalse(path.is_symlink())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            self.assert_no_trace(path)
        self.assertIn("up to date", self.run_sync("--check").stdout)

    def test_merges_template_leaves_and_keeps_private_keys_and_comments(self):
        claude, codex, codex_t3 = self.local_configs()
        codex.chmod(0o640)

        result = self.run_sync()

        self.assertEqual(json.loads(claude.read_text()), MERGED_JSON)
        self.assertEqual(codex.read_text(), MERGED_TOML)
        self.assertEqual(codex_t3.read_text(), MERGED_TOML)
        self.assertEqual(stat.S_IMODE(codex.stat().st_mode), 0o640)
        self.assertIn("pluginConfigs.demo.options.mode", result.stdout)
        self.assertIn("agents.max_threads", result.stdout)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        self.assertIn("up to date", self.run_sync("--check").stdout)

    def test_replacement_keeps_exact_independent_private_backup(self):
        _, codex, _ = self.local_configs()
        codex.chmod(0o644)
        before = codex.read_bytes()

        self.run_sync()

        [backup] = self.backups(codex)
        self.assertEqual(backup.read_bytes(), before)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)
        self.assertNotEqual(backup.stat().st_ino, codex.stat().st_ino)
        self.assertEqual(sorted(p.name for p in codex.parent.iterdir() if ".sreestack" in p.name), [])

    def test_merges_equivalent_toml_spellings_without_losing_values(self):
        spellings = {
            "dotted": (f'agents.max_threads = 3\nagents.nickname = "{SECRET}"\n', ["nickname"]),
            "inline": (f'agents = {{ max_threads = 3, nickname = "{SECRET}" }}\n', ["nickname"]),
            "split": (f'[agents.sub]\nnickname = "{SECRET}"\n\n[other]\na = 1\n\n[agents]\nb = 2\n',
                      ["sub", "b"]),
            "crlf": (f'[agents]\r\nnickname = "{SECRET}"\r\nmax_threads = 3\r\n', ["nickname"]),
            "root after tables": (f'[other]\nnickname = "{SECRET}"\n', []),
        }
        for label, (text, kept) in spellings.items():
            with self.subTest(label):
                path = self.config(CODEX, text)
                self.run_sync()
                document = parse_toml(path.read_text())
                self.assertEqual(document["model"], "template-model")
                self.assertEqual(document["agents"]["max_threads"], 12)
                self.assertTrue(set(kept) <= set(document["agents"]), document)
                self.assertIn(SECRET, path.read_text())

    def test_same_config_values_leave_bytes_mtime_and_folder_alone(self):
        claude = self.config(CLAUDE, '{"pluginConfigs":{"demo":{"options":{"mode":"on"}}},  "model":"template-model"}')
        codex = self.config(CODEX, '  model   =   "template-model"\n[agents]\nmax_threads=12\n')
        codex_t3 = self.config(CODEX_T3, codex.read_text())
        paths = (claude, codex, codex_t3)
        for path in paths:
            os.utime(path, (1_000_000_000, 1_000_000_000))
        before = [(path.read_bytes(), path.stat().st_mtime_ns) for path in paths]

        self.run_sync()
        self.run_sync("--check")

        self.assertEqual([(path.read_bytes(), path.stat().st_mtime_ns) for path in paths], before)
        for path in paths:
            self.assert_no_trace(path)

    def test_value_kind_counts_as_drift(self):
        claude = self.config(CLAUDE, json.dumps({**CLAUDE_TEMPLATE, "model": 1}))
        codex = self.config(CODEX, 'model = "template-model"\n[agents]\nmax_threads = 12.0\n')

        self.run_sync()

        self.assertEqual(json.loads(claude.read_text()), CLAUDE_TEMPLATE)
        self.assertIn("max_threads = 12\n", codex.read_text())
        self.assertEqual(len(self.backups(codex)), 1)

    def test_check_names_pending_keys_and_writes_nothing(self):
        paths = self.local_configs()
        before = [path.read_bytes() for path in paths]

        result = self.run_sync("--check", code=1)

        self.assertIn(f"would update settings in {paths[1]}: model, agents.max_threads", result.stdout)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        self.assertEqual([path.read_bytes() for path in paths], before)
        for path in paths:
            self.assert_no_trace(path)

    def test_check_fails_on_settings_drift_alone(self):
        self.run_sync()
        codex = self.home / CODEX
        codex.write_text(codex.read_text().replace("max_threads = 12", "max_threads = 3"))

        result = self.run_sync("--check", code=1)

        self.assertEqual(result.stdout.splitlines(), [f"would update settings in {codex}: agents.max_threads"])

    def test_private_values_never_reach_the_checkout(self):
        self.local_configs()

        self.run_sync()

        self.assertEqual(self.git("status", "--porcelain").stdout, "")
        for path in self.repo.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                self.assertNotIn(SECRET.encode(), path.read_bytes(), path)


class RefusalTests(SettingsFixture):
    def assert_refused(self, relative, message, mode="sync"):
        path = self.home / relative
        args = ("--check",) if mode == "check" else ()
        result = self.run_sync(*args, code=1)
        self.assertIn(f"{path}: ", result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        return result

    def test_refuses_unusable_configs_and_continues_with_the_others(self):
        cases = {
            "broken JSON": (CLAUDE, b'{"token": "' + SECRET.encode(), "invalid JSON"),
            "repeated JSON key": (CLAUDE, f'{{"token": "{SECRET}", "token": 1}}'.encode(), "repeats"),
            "JSON NaN": (CLAUDE, b'{"a": NaN}', "could not merge"),
            "JSON NaN without drift": (CLAUDE, json.dumps({**CLAUDE_TEMPLATE, "a": float("nan")}).encode(),
                                       "could not merge"),
            "JSON overflow": (CLAUDE, b'{"a": 1e999}', "would change"),
            "JSON precision": (CLAUDE, b'{"a": 1.0000000000000000001}', "would change"),
            "JSON array": (CLAUDE, b'["' + SECRET.encode() + b'"]', "JSON object"),
            "empty JSON": (CLAUDE, b"", "invalid JSON"),
            "JSON table for value": (CLAUDE, b'{"model": {"a": 1}}', "model"),
            "JSON list for value": (CLAUDE, b'{"model": [{"a": 1}]}', "model"),
            "JSON value for table": (CLAUDE, b'{"pluginConfigs": 3}', "pluginConfigs"),
            "not UTF-8": (CLAUDE, b'{"token": "\xff"}', "could not merge"),
            "broken TOML": (CODEX, f'token = "{SECRET}'.encode(), "invalid TOML"),
            "repeated TOML key": (CODEX, f'a = "{SECRET}"\na = 2\n'.encode(), "invalid TOML"),
            "table for value": (CODEX, b"[model]\na = 1\n", "model"),
            "table array for value": (CODEX, b"[[model]]\na = 1\n", "model"),
            "table array for table": (CODEX_T3, b"[[agents]]\na = 1\n", "agents"),
            "value for table": (CODEX_T3, b"agents = 3\n", "agents"),
        }
        for label, (relative, content, message) in cases.items():
            with self.subTest(label):
                shutil.rmtree(self.home)
                self.home.mkdir()
                path = self.config(relative, content)
                os.utime(path, (1_000_000_000, 1_000_000_000))
                mtime = path.stat().st_mtime_ns

                self.assert_refused(relative, message, "check")
                self.assert_refused(relative, message)

                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (content, mtime))
                self.assert_no_trace(path)
                for other in {CLAUDE, CODEX, CODEX_T3} - {relative}:
                    self.assertTrue((self.home / other).is_file())

    def test_refuses_links_and_special_files_without_following_them(self):
        elsewhere = self.base / "elsewhere.toml"
        elsewhere.write_text(LOCAL_TOML)

        def link():
            os.symlink(elsewhere, self.home / CODEX)

        def dangling():
            os.symlink(self.base / "missing.toml", self.home / CODEX)

        def hard_link():
            os.link(elsewhere, self.home / CODEX)

        def directory():
            (self.home / CODEX).mkdir()

        def pipe():
            os.mkfifo(self.home / CODEX)

        cases = {"symlink": (link, "symlink"), "dangling": (dangling, "symlink"),
                 "hard link": (hard_link, "hard link"), "folder": (directory, "regular file"),
                 "pipe": (pipe, "regular file")}
        for label, (create, message) in cases.items():
            with self.subTest(label):
                shutil.rmtree(self.home)
                (self.home / ".codex").mkdir(parents=True)
                create()

                self.assert_refused(CODEX, message)

                self.assertEqual(elsewhere.read_text(), LOCAL_TOML)
                self.assertFalse((self.base / "missing.toml").exists())
                self.assert_no_trace(self.home / CODEX)

    def test_refuses_folder_aliases_without_writing_through_them(self):
        codex = self.config(CODEX, LOCAL_TOML)
        os.symlink(".codex", self.home / ".codex-t3")

        result = self.run_sync(code=1)

        self.assertIn(f"{self.home / CODEX_T3}: its folder", result.stderr)
        self.assertEqual(os.readlink(self.home / ".codex-t3"), ".codex")
        self.assertEqual(codex.read_text(), MERGED_TOML)
        self.assertEqual(len(self.backups(codex)), 1)

    def test_refuses_a_file_where_the_folder_belongs(self):
        (self.home / ".codex-t3").write_text(SECRET)

        result = self.run_sync(code=1)

        self.assertIn(f"{self.home / CODEX_T3}: its folder", result.stderr)
        self.assertEqual((self.home / ".codex-t3").read_text(), SECRET)

    def test_refuses_destinations_inside_any_checkout(self):
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))
        link = self.base / "home-link"
        link.symlink_to(worktree / "nested")
        (worktree / "nested").mkdir()
        for home in (self.repo / "nested", link):
            with self.subTest(home=home):
                self.home = home
                result = self.run_sync(code=1)
                self.assertIn("inside a checkout", result.stderr)
                for relative in (CLAUDE, CODEX, CODEX_T3):
                    self.assertFalse((home / relative).exists())

    def test_reports_invalid_template_without_touching_configs(self):
        claude, codex, _ = self.local_configs()
        before = claude.read_bytes(), codex.read_bytes()
        self.write("codex/config.toml", "broken = \n")

        result = self.run_sync(code=1)

        self.assertIn(f"template {self.repo / 'codex/config.toml'}", result.stderr)
        self.assertEqual(codex.read_bytes(), before[1])
        self.assertEqual(json.loads(claude.read_text()), MERGED_JSON)

    def test_unexpected_parser_failure_is_refused_without_its_text(self):
        claude = self.config(CLAUDE, f'{{"token": "{SECRET}"}}')
        before = claude.read_bytes()

        result = self.run_injected(f"""
            real = json.loads
            def loads(text, **options):
                if {SECRET!r} in text:
                    raise RecursionError({SECRET!r})
                return real(text, **options)
            json.loads = loads
        """, code=1)

        self.assertIn("could not merge", result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(claude.read_bytes(), before)

    def test_write_failure_reports_its_os_reason_and_continues(self):
        claude, codex, _ = self.local_configs()
        codex.parent.chmod(0o500)
        self.addCleanup(codex.parent.chmod, 0o700)

        result = self.run_sync(code=1)

        self.assertIn(f"{codex}: could not update settings: ", result.stderr)
        self.assertIn("Permission denied", result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        self.assertEqual(codex.read_text(), LOCAL_TOML)
        self.assertEqual(json.loads(claude.read_text()), MERGED_JSON)

    def test_output_that_would_lose_or_garble_values_is_refused(self):
        codex = self.config(CODEX, LOCAL_TOML)
        for output in ('model = "template-model"\n', "[unterminated\n"):
            with self.subTest(output):
                result = self.run_injected(f"""
                    host_settings.tomlkit.dumps = lambda document: {output!r}
                """, code=1)
                self.assertIn(f"{codex}: ", result.stderr)
                self.assertEqual(codex.read_text(), LOCAL_TOML)
                self.assert_no_trace(codex)


class RaceTests(SettingsFixture):
    REPLACING_NOW = """
        real = tempfile.mkstemp
        def mkstemp(*args, **options):
            path = {path!r}
            if (options["prefix"].startswith(".config.toml.sreestack-")
                    and str(options["dir"]) == os.path.dirname(path)):
                {action}
            return real(*args, **options)
        tempfile.mkstemp = mkstemp
    """

    def injected(self, path, action):
        return self.REPLACING_NOW.format(path=str(path), action=action)

    def test_host_edit_during_sync_is_kept_with_the_backup(self):
        claude, codex, codex_t3 = self.local_configs()
        original = codex.read_bytes()

        result = self.run_injected(self.injected(
            codex_t3, "open(path, 'w').write('edited by host')",
        ), code=1)

        self.assertIn(f"{codex_t3}: changed since sync read it", result.stderr)
        self.assertEqual(codex_t3.read_text(), "edited by host")
        self.assertEqual([path.read_bytes() for path in self.backups(codex_t3)], [original])
        self.assertEqual(sorted(p.name for p in codex_t3.parent.iterdir() if ".sreestack" in p.name), [])

    def test_path_swapped_for_a_link_during_sync_is_left_alone(self):
        _, _, codex_t3 = self.local_configs()
        elsewhere = self.base / "elsewhere.toml"
        elsewhere.write_text(LOCAL_TOML)

        result = self.run_injected(self.injected(
            codex_t3, f"os.unlink(path); os.symlink({str(elsewhere)!r}, path)",
        ), code=1)

        self.assertIn(f"{codex_t3}: ", result.stderr)
        self.assertEqual(os.readlink(codex_t3), str(elsewhere))
        self.assertEqual(elsewhere.read_text(), LOCAL_TOML)

    def test_folder_swapped_during_sync_is_left_alone(self):
        for label in ("after planning", "before replacing"):
            with self.subTest(label):
                _, _, codex_t3 = self.local_configs()
                swap = (f"path = {str(codex_t3)!r}; content = open(path, 'rb').read(); "
                        f"os.rename(os.path.dirname(path), {str(self.base / label)!r}); "
                        "os.mkdir(os.path.dirname(path)); open(path, 'wb').write(content)")
                setup = self.injected(codex_t3, swap) if label == "before replacing" else f"""
                    real = host_settings.write_config
                    def write(config, *details):
                        if str(config) == {str(codex_t3)!r}:
                            {swap}
                        return real(config, *details)
                    host_settings.write_config = write
                """

                result = self.run_injected(setup, code=1)

                self.assertIn(f"{codex_t3}: changed since sync read it", result.stderr)
                self.assertEqual(codex_t3.read_text(), LOCAL_TOML)

    def test_new_file_appearing_during_sync_is_never_replaced(self):
        codex_t3 = self.home / CODEX_T3

        late = self.run_injected(f"""
            real = os.link
            def link(source, target, **options):
                if str(target) == {str(codex_t3)!r}:
                    open(target, "w").write("created by host")
                return real(source, target, **options)
            os.link = link
        """, code=1)

        self.assertIn(f"{codex_t3}: ", late.stderr)
        self.assertEqual(codex_t3.read_text(), "created by host")
        self.assertEqual(sorted(p.name for p in codex_t3.parent.iterdir()), ["config.toml"])


class DependencyTests(SettingsFixture):
    def without_tomlkit(self, *args, root=None, code=0):
        """Run sync with no site-packages, like an interpreter missing the dependency."""
        script = (root or self.repo) / "scripts/sync_hosts.py"
        result = subprocess.run([sys.executable, "-S", str(script), "--home", str(self.home), *args],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def fake_venv(self):
        """Stand in for the installed .venv: the test interpreter keeps its packages."""
        log = self.base / "venv-used.log"
        python = self.repo / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.write_text(f'#!/bin/sh\necho "$*" >> "{log}"\nexec "{sys.executable}" "$@"\n')
        python.chmod(0o755)
        with open(self.repo / ".git/info/exclude", "a") as exclude:
            exclude.write("/.venv/\n")
        return log

    def test_missing_dependency_keeps_links_and_names_the_setup(self):
        result = self.without_tomlkit(code=1)

        self.assertIn("tomlkit", result.stderr)
        self.assertIn("python3 -m venv --clear .venv", result.stderr)
        self.assertIn(SETUP, result.stderr)
        self.assert_linked("alpha", "beta")
        self.assertFalse((self.home / CLAUDE).exists())
        self.assertIn(SETUP, self.without_tomlkit("--check", code=1).stderr)

    def test_hook_setup_and_health_checks_need_no_dependency(self):
        self.without_tomlkit("--install-hooks")
        self.assertIn("up to date", self.without_tomlkit("--check-hooks").stdout)

    def test_main_update_merges_with_clone_venv_and_never_with_bare_python(self):
        self.run_sync("--install-hooks")
        self.run_sync()
        codex = self.home / CODEX
        self.python_shim(self.bin / "python3", "-S")

        self.add_skill("gamma")
        self.write("codex/config.toml", 'model = "new-model"\n')
        result = self.commit("change template without setup")

        self.assertEqual(result.returncode, 0)
        self.assertIn(SETUP, result.stderr)
        self.assertIn("was not rolled back", result.stderr)
        self.assertIn(".venv/bin/python scripts/sync_hosts.py", result.stderr)
        self.assert_linked("alpha", "beta", "gamma")
        self.assertIn('"template-model"', codex.read_text())

        log = self.fake_venv()
        self.write("codex/config.toml", 'model = "newer-model"\n')
        result = self.commit("change template after setup")

        self.assertNotIn("sreestack:", result.stderr)
        self.assertIn("--hook", log.read_text())
        self.assertIn('model = "newer-model"', codex.read_text())
        self.assertIn("max_threads = 12", codex.read_text())
        self.assertEqual(len(self.backups(codex)), 1)

    def test_worktree_check_uses_stable_clone_venv(self):
        self.run_sync()
        log = self.fake_venv()
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))

        result = self.without_tomlkit("--check", root=worktree)

        self.assertIn(f"Checking stable clone {self.repo}", result.stdout)
        self.assertIn("--check", log.read_text())
        self.assertEqual(self.git("-C", str(worktree), "status", "--porcelain").stdout, "")


if __name__ == "__main__":
    unittest.main()
