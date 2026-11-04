"""Exercise host sync and its Git hook against fixture repositories and homes."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).parent
HOSTS = {
    "codex": {"skills": ".agents/skills", "instructions": ".codex/AGENTS.md", "exclude": []},
    "claude": {"skills": ".claude/skills", "instructions": ".claude/CLAUDE.md", "exclude": []},
}
SKILL_DIRS = (".agents/skills", ".claude/skills")
INSTRUCTIONS = "# Shared\n\n- Keep it simple.\n"
CLAUDE_TEMPLATE = {"model": "template-model", "pluginConfigs": {"demo": {"options": {"mode": "on"}}}}
CODEX_TEMPLATE = '# Public note.\nmodel = "template-model"\n\n[agents]\nmax_threads = 12\n'
HOOK = "reference-transaction"


class Fixture(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(os.path.realpath(directory.name))
        self.repo = self.base / "SreeStack"
        self.home = self.base / "home"
        self.home.mkdir()
        empty_config = self.base / "gitconfig"
        empty_config.write_text("")
        # Hooks find git and python3 on PATH; pin both so a test can remove python3.
        self.bin = self.base / "bin"
        self.bin.mkdir()
        os.symlink(shutil.which("git"), self.bin / "git")
        self.python_shim(self.bin / "python3")
        self.env = {
            **os.environ,
            "PATH": f"{self.bin}{os.pathsep}/usr/bin{os.pathsep}/bin",
            "GIT_CONFIG_GLOBAL": str(empty_config),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        (self.repo / "scripts").mkdir(parents=True)
        for script in ("sync_hosts.py", "host_settings.py"):
            shutil.copyfile(SCRIPTS / script, self.repo / "scripts" / script)
        self.write("global/AGENTS.md", INSTRUCTIONS)
        self.write("claude/settings.json", json.dumps(CLAUDE_TEMPLATE))
        self.write("codex/config.toml", CODEX_TEMPLATE)
        for host, manifest in HOSTS.items():
            self.write(f"{host}/setup.json", json.dumps(manifest))
        self.add_skill("alpha")
        self.add_skill("beta")
        self.git("init", "--quiet", "--initial-branch=main")
        self.commit("initial")

    def python_shim(self, path, *flags):
        """Wrap the test interpreter; a symlink would lose its virtual environment."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'#!/bin/sh\nexec "{sys.executable}" {" ".join(flags)} "$@"\n')
        path.chmod(0o755)

    def write(self, name, content, root=None):
        path = (root or self.repo) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def add_skill(self, name, root=None):
        self.write(f"skills/{name}/SKILL.md", f"---\nname: {name}\n---\n", root)

    def git(self, *args, cwd=None, check=True, env=None):
        return subprocess.run(
            ["git", *args], cwd=cwd or self.repo, env=env or self.env,
            text=True, capture_output=True, check=check,
        )

    def commit(self, message, cwd=None, env=None):
        self.git("add", "-A", cwd=cwd)
        return self.git("commit", "--quiet", "-m", message, cwd=cwd, env=env)

    def run_sync(self, *args, root=None, code=0):
        result = subprocess.run(
            [sys.executable, str((root or self.repo) / "scripts/sync_hosts.py"),
             "--home", str(self.home), *args],
            env=self.env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def links(self, relative):
        directory = self.home / relative
        return {entry.name: os.readlink(entry) for entry in directory.iterdir() if entry.is_symlink()}

    def expected_links(self, *names):
        return {name: str(self.repo / "skills" / name) for name in names}

    def assert_linked(self, *names, message=None):
        for skills in SKILL_DIRS:
            self.assertEqual(self.links(skills), self.expected_links(*names), message)

    def tree(self):
        return sorted(
            (str(path.relative_to(self.home)), os.readlink(path) if path.is_symlink() else None)
            for path in self.home.rglob("*")
        )


class SyncTests(Fixture):
    def test_links_each_skill_and_shared_instructions_for_every_host(self):
        self.run_sync()

        for skills in SKILL_DIRS:
            self.assertFalse((self.home / skills).is_symlink())
        self.assert_linked("alpha", "beta")
        for instructions in (".codex/AGENTS.md", ".claude/CLAUDE.md"):
            self.assertEqual(os.readlink(self.home / instructions), str(self.repo / "global/AGENTS.md"))
        self.assertIn("up to date", self.run_sync("--check").stdout)
        before = self.tree()
        self.assertIn("up to date", self.run_sync().stdout)
        self.assertEqual(self.tree(), before)

    def test_check_reports_changes_without_writing(self):
        result = self.run_sync("--check", code=1)

        self.assertIn(".claude/skills/alpha", result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_converges_after_skills_are_added_renamed_and_removed(self):
        self.run_sync()
        self.add_skill("gamma")
        (self.repo / "skills/alpha").rename(self.repo / "skills/alpha-two")
        shutil.rmtree(self.repo / "skills/beta")

        self.run_sync()

        self.assert_linked("alpha-two", "gamma")

    def test_preserves_foreign_entries_and_reports_name_conflicts(self):
        claude = self.home / ".claude/skills"
        (claude / "synced/account-skill").mkdir(parents=True)
        (claude / "synced/account-skill/SKILL.md").write_text("account")
        (claude / ".DS_Store").write_text("finder")
        os.symlink("/elsewhere/tool", claude / "tool")
        os.symlink("/elsewhere/beta", claude / "beta")

        result = self.run_sync(code=1)

        self.assertIn(f"{claude / 'beta'}: already exists", result.stderr)
        self.assertEqual(os.readlink(claude / "beta"), "/elsewhere/beta")
        self.assertEqual(os.readlink(claude / "tool"), "/elsewhere/tool")
        self.assertEqual((claude / "synced/account-skill/SKILL.md").read_text(), "account")
        self.assertEqual((claude / ".DS_Store").read_text(), "finder")
        self.assertEqual(os.readlink(claude / "alpha"), str(self.repo / "skills/alpha"))
        self.assertEqual(self.links(".agents/skills"), self.expected_links("alpha", "beta"))
        self.assertNotIn("synced", os.listdir(self.home / ".agents/skills"))

    def test_host_exclusions_remove_only_that_hosts_link(self):
        self.run_sync()
        self.write("claude/setup.json", json.dumps({**HOSTS["claude"], "exclude": ["beta"]}))

        self.run_sync()

        self.assertEqual(self.links(".claude/skills"), self.expected_links("alpha"))
        self.assertEqual(self.links(".agents/skills"), self.expected_links("alpha", "beta"))

    def test_rejects_manifest_typos_before_writing(self):
        cases = {
            "unknown key": ({**HOSTS["claude"], "exlude": []}, "unknown keys: exlude"),
            "unknown skill": ({**HOSTS["claude"], "exclude": ["betta"]}, "unknown skills in exclude: betta"),
            "escaping path": ({**HOSTS["claude"], "skills": "../skills"}, "must stay inside home"),
            "shared path": ({**HOSTS["claude"], "skills": ".agents/skills"}, "hosts share a skills path"),
        }
        for label, (manifest, message) in cases.items():
            with self.subTest(label):
                self.write("claude/setup.json", json.dumps(manifest))
                self.assertIn(message, self.run_sync(code=1).stderr)
                self.assertEqual(list(self.home.iterdir()), [])

    def test_converts_owned_whole_directory_link_and_rewrites_chained_links(self):
        (self.home / ".agents").mkdir()
        os.symlink(self.repo / "skills", self.home / ".agents/skills")
        claude = self.home / ".claude/skills"
        claude.mkdir(parents=True)
        os.symlink("../../.agents/skills/alpha", claude / "alpha")

        self.run_sync()

        self.assertFalse((self.home / ".agents/skills").is_symlink())
        self.assert_linked("alpha", "beta")
        self.assertEqual(sorted(os.listdir(self.repo / "skills")), ["alpha", "beta"])

    def test_relink_preserves_foreign_entries_at_any_temporary_name(self):
        claude = self.home / ".claude/skills"
        claude.mkdir(parents=True)
        os.symlink("../../../SreeStack/skills/alpha", claude / "alpha")
        os.symlink("../../../SreeStack/skills/beta", claude / "beta")
        (claude / ".alpha.sreestack-tmp").write_text("user data")
        os.symlink("/elsewhere/keep", claude / ".beta.sreestack-tmp")

        self.run_sync()

        for name in ("alpha", "beta"):
            self.assertEqual(os.readlink(claude / name), str(self.repo / "skills" / name))
        self.assertEqual((claude / ".alpha.sreestack-tmp").read_text(), "user data")
        self.assertEqual(os.readlink(claude / ".beta.sreestack-tmp"), "/elsewhere/keep")
        self.assertEqual(
            sorted(os.listdir(claude)), [".alpha.sreestack-tmp", ".beta.sreestack-tmp", "alpha", "beta"],
        )

    def test_does_not_adopt_unrecognized_whole_directory_link(self):
        other = self.home / "other-skills"
        other.mkdir()
        (self.home / ".agents").mkdir()
        os.symlink(other, self.home / ".agents/skills")

        result = self.run_sync(code=1)

        self.assertIn("is not this checkout's skills/", result.stderr)
        self.assertEqual(os.readlink(self.home / ".agents/skills"), str(other))
        self.assertEqual(list(other.iterdir()), [])
        self.assertEqual(self.links(".claude/skills"), self.expected_links("alpha", "beta"))

    def test_removes_stale_links_only_when_they_point_into_this_checkout(self):
        self.run_sync()
        claude = self.home / ".claude/skills"
        os.symlink(self.repo / "skills/retired", claude / "retired")
        os.symlink(self.repo.parent / "worktree/skills/retired", claude / "elsewhere")

        self.run_sync()

        self.assertFalse(os.path.lexists(claude / "retired"))
        self.assertTrue(os.path.lexists(claude / "elsewhere"))


class StableCloneTests(Fixture):
    def test_health_checks_reject_off_main_from_primary_and_worktree(self):
        self.run_sync()
        self.run_sync("--install-hooks")
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))
        self.git("switch", "--quiet", "-c", "feature")
        for root in (self.repo, worktree):
            for mode in ("--check", "--check-hooks"):
                self.assertIn("does not have main checked out",
                              self.run_sync(mode, root=root, code=1).stderr)

    def test_hook_installation_rejects_feature_and_detached_without_writes(self):
        self.run_sync("--install-hooks")
        hooks = self.repo / ".git/hooks"
        before = {path.name: path.read_bytes() for path in hooks.iterdir() if path.is_file()}
        config = (self.repo / ".git/config").read_bytes()
        for switch in (("-c", "feature"), ("--detach",)):
            self.git("switch", "--quiet", *switch)
            result = self.run_sync("--install-hooks", code=1)
            self.assertIn("does not have main checked out", result.stderr)
            self.assertEqual((self.repo / ".git/config").read_bytes(), config)
            self.assertEqual({path.name: path.read_bytes() for path in hooks.iterdir()
                              if path.is_file()}, before)

    def test_worktree_checks_use_stable_clone_even_when_task_source_differs(self):
        self.run_sync()
        self.run_sync("--install-hooks")
        before = self.tree()
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))
        self.add_skill("task-only", root=worktree)
        self.write("global/AGENTS.md", "task instructions", root=worktree)
        for mode in ("--check", "--check-hooks"):
            result = self.run_sync(mode, root=worktree)
            self.assertIn(f"Checking stable clone {self.repo}", result.stdout)
            self.assertNotIn("conflict", result.stderr)
        self.assertEqual(self.tree(), before)

    def test_writes_only_from_primary_checkout_on_main(self):
        self.git("switch", "--quiet", "-c", "feature")
        self.assertIn("does not have main checked out", self.run_sync(code=1).stderr)
        self.git("switch", "--quiet", "--detach")
        self.assertIn("does not have main checked out", self.run_sync(code=1).stderr)
        self.assertIn("does not have main checked out", self.run_sync("--check", code=1).stderr)

        worktree = self.repo.parent / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))
        self.assertIn("linked worktree", self.run_sync(root=worktree, code=1).stderr)
        self.assertIn("linked worktree", self.run_sync("--install-hooks", root=worktree, code=1).stderr)
        self.run_sync("--check", root=worktree, code=1)
        self.assertEqual(list(self.home.iterdir()), [])

        self.git("switch", "--quiet", "main")
        self.run_sync()
        self.assert_linked("alpha", "beta")

    def test_linked_worktree_work_never_reaches_host_visible_content(self):
        self.run_sync("--install-hooks")
        self.run_sync()
        before = self.tree()
        skill = self.home / ".claude/skills/alpha/SKILL.md"
        instructions = self.home / ".claude/CLAUDE.md"
        skill_text, instruction_text = skill.read_text(), instructions.read_text()
        worktree = self.repo.parent / "worktree"

        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree), "main")
        self.write("skills/alpha/SKILL.md", "task edit\n", root=worktree)
        self.write("global/AGENTS.md", "task instructions\n", root=worktree)
        self.add_skill("epsilon", root=worktree)
        shutil.rmtree(worktree / "skills/beta")
        self.commit("task work", cwd=worktree)
        self.git("commit", "--quiet", "--amend", "--no-edit", cwd=worktree)
        self.git("reset", "--quiet", "--hard", "HEAD", cwd=worktree)
        self.git("switch", "--quiet", "--detach", cwd=worktree)
        self.run_sync(root=worktree, code=1)

        self.assertEqual(self.tree(), before)
        self.assertEqual(skill.read_text(), skill_text)
        self.assertEqual(instructions.read_text(), instruction_text)


class InstructionTests(Fixture):
    def test_backs_up_matching_files_and_links_shared_instructions(self):
        codex = self.home / ".codex/AGENTS.md"
        codex.parent.mkdir()
        codex.write_text(INSTRUCTIONS)
        claude = self.home / ".claude/CLAUDE.md"
        claude.parent.mkdir()
        os.symlink("../.codex/AGENTS.md", claude)

        self.run_sync()

        canonical = str(self.repo / "global/AGENTS.md")
        self.assertEqual(os.readlink(codex), canonical)
        self.assertEqual(os.readlink(claude), canonical)
        [codex_backup] = codex.parent.glob("AGENTS.md.backup-*")
        self.assertEqual(codex_backup.read_text(), INSTRUCTIONS)
        [claude_backup] = claude.parent.glob("CLAUDE.md.backup-*")
        self.assertEqual(os.readlink(claude_backup), "../.codex/AGENTS.md")
        self.assertEqual(sorted(os.listdir(codex.parent)),
                         ["AGENTS.md", codex_backup.name, "config.toml"])

    def test_keeps_aliases_that_already_resolve_to_shared_instructions(self):
        codex = self.home / ".codex/AGENTS.md"
        codex.parent.mkdir()
        os.symlink(self.repo / "global/AGENTS.md", codex)
        claude = self.home / ".claude/CLAUDE.md"
        claude.parent.mkdir()
        os.symlink("../.codex/AGENTS.md", claude)

        self.run_sync()

        self.assertEqual(os.readlink(claude), "../.codex/AGENTS.md")
        self.assertEqual(list(claude.parent.glob("*.backup-*")), [])

    def test_reports_differing_instructions_without_overwriting(self):
        codex = self.home / ".codex/AGENTS.md"
        codex.parent.mkdir()
        codex.write_text(INSTRUCTIONS + "- Local preference.\n")

        result = self.run_sync(code=1)

        self.assertIn(f"{codex}: differs from global/AGENTS.md", result.stderr)
        self.assertFalse(codex.is_symlink())
        self.assertEqual(codex.read_text(), INSTRUCTIONS + "- Local preference.\n")
        self.assertEqual(list(codex.parent.glob("*.backup-*")), [])
        self.assertTrue((self.home / ".claude/CLAUDE.md").is_symlink())

    def test_concurrent_syncs_back_up_once(self):
        codex = self.home / ".codex/AGENTS.md"
        codex.parent.mkdir()
        codex.write_text(INSTRUCTIONS)
        command = [sys.executable, str(self.repo / "scripts/sync_hosts.py"), "--home", str(self.home)]

        processes = [subprocess.Popen(command, env=self.env, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for _ in range(6)]
        results = [(process.wait(), process.communicate()) for process in processes]

        self.assertEqual([code for code, _ in results], [0] * 6, results)
        self.assertEqual(len(list(codex.parent.glob("AGENTS.md.backup-*"))), 1)
        self.assertEqual(self.links(".claude/skills"), self.expected_links("alpha", "beta"))


class HookTests(Fixture):
    def test_health_and_install_reject_dangling_or_foreign_custom_alias(self):
        self.install()
        custom = self.base / "custom-hooks"
        custom.mkdir()
        self.git("config", "core.hooksPath", str(custom))
        alias = custom / HOOK
        alias.symlink_to("sreestack-host-sync")
        for foreign in (False, True):
            if foreign:
                target = custom / "sreestack-host-sync"
                target.write_text("#!/bin/sh\nexit 0\n")
                target.chmod(0o755)
            with self.subTest(foreign=foreign):
                self.run_sync("--check-hooks", code=1)
                self.install(code=1)
                self.assertEqual(os.readlink(alias), "sreestack-host-sync")
                if foreign:
                    self.assertEqual(target.read_text(), "#!/bin/sh\nexit 0\n")
        alias.unlink()
        alias.symlink_to(self.repo / ".git/hooks/sreestack-host-sync")
        self.run_sync("--check-hooks")

    def test_chain_leaves_input_and_git_operations_intact_when_temp_creation_fails(self):
        hook = self.repo / ".git/hooks" / HOOK
        log = self.base / "original-refs.bin"
        hook.write_text("#!/bin/sh\nexit 0\n")
        hook.chmod(0o755)
        block = self.chain_block(self.install(code=1))
        hook.write_text(f'#!/bin/sh\n{block}\ncat > "{log}"\n')
        env = {**self.env, "TMPDIR": str(self.base / "missing")}
        payload = b"one\n\n"
        subprocess.run([str(hook), "preparing"], cwd=self.repo, env=env,
                       input=payload, check=True, capture_output=True)
        self.assertEqual(log.read_bytes(), payload)
        self.git("commit", "--quiet", "--allow-empty", "-m", "primary", env=env)
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "task", str(worktree))
        self.git("commit", "--quiet", "--allow-empty", "-m", "task", cwd=worktree, env=env)

    def install(self, code=0):
        return self.run_sync("--install-hooks", code=code)

    def chain_block(self, result):
        start = result.stderr.index("# BEGIN SreeStack host sync")
        end = result.stderr.index("# END SreeStack host sync", start)
        return result.stderr[start:end] + "# END SreeStack host sync"

    def assert_failed_visibly(self, result, message):
        self.assertEqual(result.returncode, 0, "Git ignores this hook's exit status")
        self.assertIn(message, result.stderr)
        self.assertIn("was not rolled back", result.stderr)
        self.run_sync("--check", code=1)

    def test_install_preserves_unrelated_hooks_and_records_home(self):
        pre_commit = self.repo / ".git/hooks/pre-commit"
        pre_commit.write_text("#!/bin/sh\nexit 0\n")
        self.git("config", "sreestack.primary", "/stale/clone")

        self.install()
        self.install()

        self.assertEqual(pre_commit.read_text(), "#!/bin/sh\nexit 0\n")
        self.assertEqual(os.readlink(self.repo / ".git/hooks" / HOOK), "sreestack-host-sync")
        self.assertEqual(self.git("config", "--get", "sreestack.home").stdout.strip(), str(self.home))
        self.assertEqual([path.name for path in (self.repo / ".git/hooks").glob(".sreestack*")], [])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_hook_syncs_every_main_update_path(self):
        self.install()
        self.run_sync()

        self.add_skill("gamma")
        self.commit("normal commit adds gamma")
        self.assert_linked("alpha", "beta", "gamma", message="commit")

        self.git("switch", "--quiet", "-c", "feature")
        self.git("mv", "skills/alpha", "skills/alpha-two")
        self.commit("rename alpha")
        self.assert_linked("alpha", "beta", "gamma", message="feature commit must not sync")
        self.git("switch", "--quiet", "main")
        self.git("merge", "--quiet", "--ff-only", "feature")
        self.assert_linked("alpha-two", "beta", "gamma", message="fast-forward merge")

        self.git("rm", "--quiet", "-r", "skills/gamma")
        self.git("commit", "--quiet", "--amend", "--no-edit")
        self.assert_linked("alpha-two", "beta", message="amend")

        self.git("reset", "--quiet", "--hard", "HEAD~1")
        self.assert_linked("alpha", "beta", "gamma", message="reset --hard")

        self.git("switch", "--quiet", "-c", "upstream")
        self.add_skill("delta")
        self.commit("upstream adds delta")
        self.git("switch", "--quiet", "main")
        self.git("rebase", "--quiet", "upstream")
        self.assert_linked("alpha", "beta", "delta", "gamma", message="fast-forward rebase")

        self.write("claude/setup.json", json.dumps({**HOSTS["claude"], "exclude": ["delta"]}))
        self.commit("exclude delta from claude")
        self.assertEqual(self.links(".claude/skills"), self.expected_links("alpha", "beta", "gamma"))
        self.git("switch", "--quiet", "upstream")
        self.add_skill("zeta")
        self.commit("upstream adds zeta")
        self.git("switch", "--quiet", "main")
        self.assertEqual(self.links(".claude/skills"), self.expected_links("alpha", "beta", "gamma"))
        self.git("rebase", "--quiet", "upstream")
        self.assertEqual(self.links(".claude/skills"), self.expected_links("alpha", "beta", "gamma", "zeta"))
        self.assertEqual(self.links(".agents/skills"),
                         self.expected_links("alpha", "beta", "delta", "gamma", "zeta"), "rebase")

    def test_hook_syncs_pulls_from_a_remote(self):
        self.install()
        self.run_sync()
        origin = self.base / "origin.git"
        other = self.base / "other"
        self.git("clone", "--quiet", "--bare", str(self.repo), str(origin))
        self.git("remote", "add", "origin", str(origin))
        self.git("clone", "--quiet", str(origin), str(other))

        self.add_skill("gamma", root=other)
        self.commit("add gamma", cwd=other)
        self.git("push", "--quiet", "origin", "main", cwd=other)
        self.git("pull", "--quiet", "--ff-only", "origin", "main")
        self.assert_linked("alpha", "beta", "gamma", message="pull --ff-only")

        shutil.rmtree(other / "skills/beta")
        self.commit("remove beta", cwd=other)
        self.git("push", "--quiet", "origin", "main", cwd=other)
        self.git("pull", "--quiet", "--rebase", "origin", "main")
        self.assert_linked("alpha", "gamma", message="pull --rebase")

    def test_hook_skips_feature_detached_and_worktree_updates(self):
        self.install()
        self.run_sync()
        before = self.tree()

        worktree = self.repo.parent / "worktree"
        results = []
        self.git("switch", "--quiet", "-c", "feature")
        self.add_skill("gamma")
        results.append(self.commit("feature adds gamma"))
        results.append(self.git("switch", "--quiet", "--detach"))
        self.add_skill("delta")
        results.append(self.commit("detached adds delta"))
        results.append(self.git("reset", "--quiet", "--hard", "main"))
        self.assertEqual(self.tree(), before)

        self.git("switch", "--quiet", "-c", "parking")
        results.append(self.git("worktree", "add", "--quiet", str(worktree), "main"))
        self.add_skill("epsilon", root=worktree)
        results.append(self.commit("worktree main adds epsilon", cwd=worktree))
        results.append(self.git("merge", "--quiet", "--no-edit", "feature", cwd=worktree))
        results.append(self.git("commit", "--quiet", "--amend", "--no-edit", cwd=worktree))
        results.append(self.git("reset", "--quiet", "--hard", "HEAD~1", cwd=worktree))

        self.assertEqual(self.tree(), before)
        for result in results:
            self.assertNotIn("sreestack", result.stderr, result.args)

    def test_unrelated_operations_skip_before_reading_checkout_or_config(self):
        self.install()
        self.run_sync()
        before = self.tree()
        self.git("switch", "--quiet", "-c", "old")
        self.git("rm", "--quiet", "-r", "scripts")
        self.commit("branch without sync script")
        self.git("config", "sreestack.primary", "/stale/clone")
        self.git("config", "sreestack.home", "/stale/home")
        no_python = self.base / "bin-without-python"
        no_python.mkdir()
        os.symlink(shutil.which("git"), no_python / "git")
        worktree = self.repo.parent / "worktree"

        for label, env in (("python3 present", self.env), ("python3 missing", {**self.env, "PATH": str(no_python)})):
            with self.subTest(label):
                shutil.rmtree(worktree, ignore_errors=True)
                self.git("worktree", "prune")
                steps = [
                    self.git("worktree", "add", "--quiet", "-B", "task", str(worktree), "main", env=env),
                    self.git("switch", "--quiet", "-C", "task-two", cwd=worktree, env=env),
                    self.git("commit", "--quiet", "--allow-empty", "-m", "worktree", cwd=worktree, env=env),
                    self.git("commit", "--quiet", "--allow-empty", "-m", "primary", env=env),
                ]
                for result in steps:
                    self.assertEqual(result.stderr, "", result.args)
        self.assertEqual(self.tree(), before)

    def test_missing_runtime_or_script_on_main_fails_visibly(self):
        self.install()
        self.run_sync()
        no_python = self.base / "bin-without-python"
        no_python.mkdir()
        os.symlink(shutil.which("git"), no_python / "git")

        self.add_skill("gamma")
        result = self.commit("add gamma", env={**self.env, "PATH": str(no_python)})
        self.assert_failed_visibly(result, "python3 is not on Git's PATH")

        self.git("rm", "--quiet", "scripts/sync_hosts.py")
        result = self.git("commit", "--quiet", "-m", "remove script")
        self.assertEqual(result.returncode, 0)
        self.assertIn("scripts/sync_hosts.py is missing", result.stderr)
        self.assertIn("was not rolled back", result.stderr)

    def test_failures_print_warnings_for_every_update_path(self):
        self.install()
        self.run_sync()
        self.git("switch", "--quiet", "-c", "feature")
        self.add_skill("gamma")
        self.commit("add gamma")
        self.git("switch", "--quiet", "main")
        (self.home / ".claude/skills/gamma").mkdir()
        conflict = ".claude/skills/gamma: already exists"

        self.assert_failed_visibly(self.git("merge", "--quiet", "--ff-only", "feature"), conflict)
        self.assert_failed_visibly(self.git("commit", "--quiet", "--amend", "-m", "amended"), conflict)
        self.assert_failed_visibly(self.git("commit", "--quiet", "--allow-empty", "-m", "empty"), conflict)
        self.assert_failed_visibly(self.git("reset", "--quiet", "--hard", "HEAD~1"), conflict)
        self.git("switch", "--quiet", "feature")
        self.add_skill("delta")
        self.commit("add delta")
        self.assert_failed_visibly(self.git("switch", "--quiet", "main"), conflict)
        self.assert_failed_visibly(self.git("rebase", "--quiet", "feature"), conflict)
        self.assertTrue((self.home / ".claude/skills/gamma").is_dir())
        self.assertEqual(self.links(".agents/skills"), self.expected_links("alpha", "beta", "delta", "gamma"))

    def test_hook_reports_invalid_manifest_as_failed_sync(self):
        self.install()
        self.write("claude/setup.json", json.dumps({**HOSTS["claude"], "exclude": ["missing"]}))

        result = self.commit("break manifest")

        self.assert_failed_visibly(result, "unknown skills in exclude: missing")
        self.assertEqual(list(self.home.iterdir()), [])

    def test_existing_hook_chains_handler_without_losing_its_body(self):
        log = self.base / "mine.log"
        hook = self.repo / ".git/hooks" / HOOK
        body = f'#!/bin/sh\n# sreestack-host-sync integration pending\necho "$1" >> "{log}"\n'
        hook.write_text(body)
        hook.chmod(0o755)

        result = self.install(code=1)

        self.assertEqual(hook.read_text(), body)
        self.assertTrue((self.repo / ".git/hooks/sreestack-host-sync").is_file())
        self.assertEqual(self.git("config", "--get", "sreestack.home").stdout.strip(), str(self.home))
        hook.write_text("#!/bin/sh\n" + self.chain_block(result) + "\n" + body.split("\n", 1)[1])
        self.install()

        self.add_skill("gamma")
        self.commit("add gamma")
        self.assert_linked("alpha", "beta", "gamma")
        self.assertIn("committed", log.read_text())

    def test_custom_hooks_path_chains_handler_without_changing_config(self):
        custom = self.base / "custom-hooks"
        self.git("config", "core.hooksPath", str(custom))

        result = self.install(code=1)

        self.assertFalse(custom.exists())
        self.assertEqual(self.git("config", "--get", "core.hooksPath").stdout.strip(), str(custom))
        custom.mkdir()
        (custom / HOOK).write_text("#!/bin/sh\n" + self.chain_block(result) + "\n")
        (custom / HOOK).chmod(0o755)
        self.install()
        self.git("switch", "--quiet", "-c", "feature")
        self.add_skill("gamma")
        self.commit("add gamma")
        self.assertEqual(list(self.home.iterdir()), [])

        self.git("switch", "--quiet", "main")
        self.assert_linked("alpha", "beta")
        self.git("merge", "--quiet", "--ff-only", "feature")
        self.assert_linked("alpha", "beta", "gamma")

    def test_chained_handler_preserves_reference_input_for_existing_hook(self):
        log = self.base / "references.log"
        hook = self.repo / ".git/hooks" / HOOK
        hook.write_text(f'#!/bin/sh\ncat >> "{log}"\n')
        hook.chmod(0o755)
        result = self.install(code=1)
        hook.write_text(f'#!/bin/sh\n{self.chain_block(result)}\ncat >> "{log}"\n')

        self.add_skill("gamma")
        self.commit("add gamma")

        self.assert_linked("alpha", "beta", "gamma")
        self.assertIn("refs/heads/main", log.read_text())

    def test_chain_replays_exact_input_and_strict_hook_allows_noop_fetch_and_pull(self):
        hook = self.repo / ".git/hooks" / HOOK
        log = self.base / "references.bin"
        hook.write_text("#!/bin/sh\nexit 0\n")
        hook.chmod(0o755)
        result = self.install(code=1)
        block = self.chain_block(result)
        hook.write_text(f'#!/bin/sh\n{block}\ncat > "{log}"\n')
        for payload in (b"", b"one\n", b"one\n\n", b"one without newline"):
            subprocess.run([str(hook), "preparing"], cwd=self.repo, env=self.env,
                           input=payload, check=True, capture_output=True)
            self.assertEqual(log.read_bytes(), payload)
        hook.write_text('#!/bin/sh\n' + block + '\n'
                        'while read -r old new ref; do\n'
                        '  [ -n "$old" ] && [ -n "$new" ] && [ -n "$ref" ] || exit 1\n'
                        'done\n')
        origin = self.base / "origin.git"
        self.git("clone", "--quiet", "--bare", str(self.repo), str(origin))
        self.git("remote", "add", "origin", str(origin))
        self.git("fetch", "--quiet", "origin")
        self.git("fetch", "--quiet", "origin")
        self.git("pull", "--quiet", "--ff-only", "origin", "main")

    def test_install_does_not_confirm_chain_after_an_existing_reader(self):
        hook = self.repo / ".git/hooks" / HOOK
        hook.write_text("#!/bin/sh\ncat >/dev/null\n")
        hook.chmod(0o755)
        result = self.install(code=1)
        hook.write_text(hook.read_text() + self.chain_block(result) + "\n")
        self.assertIn("before any commands", self.install(code=1).stderr)

    def test_hook_health_detects_drift_and_main_updates_refresh_owned_handler(self):
        self.run_sync("--check-hooks", code=1)
        self.install()
        self.run_sync("--check-hooks")
        handler = self.repo / ".git/hooks/sreestack-host-sync"
        handler.write_text(handler.read_text() + "# stale\n")
        self.assertIn("stale", self.run_sync("--check-hooks", code=1).stderr)
        self.run_sync()
        self.run_sync("--check-hooks")
        script = self.repo / "scripts/sync_hosts.py"
        script.write_text(script.read_text().replace("relevant=\n", "# new handler revision\nrelevant=\n", 1))
        self.commit("update hook implementation")
        self.assertIn("# new handler revision", handler.read_text())
        self.run_sync("--check-hooks")
        (self.repo / ".git/hooks" / HOOK).unlink()
        self.run_sync("--check-hooks", code=1)
        self.install()
        self.run_sync("--check-hooks")

    def test_install_refuses_foreign_handler(self):
        handler = self.repo / ".git/hooks/sreestack-host-sync"
        handler.write_text("#!/bin/sh\necho mine\n")

        self.assertIn("not installed by SreeStack", self.install(code=1).stderr)
        self.assertEqual(handler.read_text(), "#!/bin/sh\necho mine\n")
        self.assertFalse(os.path.lexists(self.repo / ".git/hooks" / HOOK))


if __name__ == "__main__":
    unittest.main()
