import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest import mock

import hosts

CODEX_EVENTS = [{"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
                {"type": "turn.completed", "usage": {"input_tokens": 5, "output_tokens": 1}}]


class HostsTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.root)
        self.enterContext(mock.patch("hosts.GRACE_SECONDS", 0.5))

    def test_a_timeout_ends_the_whole_process_group(self):
        marker = self.root / "survivor"
        script = f"(sleep 1; touch {marker}) & sleep 30"
        with open(self.root / "out.log", "w") as log:
            code = hosts.run_group(["sh", "-c", script], cwd=self.root, env=dict(os.environ),
                                   stdout=log, stderr=log, timeout=0.2)
        self.assertIsNone(code)
        time.sleep(1.5)
        self.assertFalse(marker.exists())

    def test_descendants_end_when_the_host_exits(self):
        marker = self.root / "survivor"
        with open(self.root / "out.log", "w") as log:
            code = hosts.run_group(["sh", "-c", f"(sleep 1; touch {marker}) & exit 0"], cwd=self.root,
                                   env=dict(os.environ), stdout=log, stderr=log, timeout=5)
        self.assertEqual(code, 0)
        time.sleep(1.5)
        self.assertFalse(marker.exists())

    def codex(self, session: str):
        """Run the Codex adapter against a fake CLI and a fake real login."""
        real_home = self.root / "real-codex"
        real_home.mkdir()
        (real_home / "auth.json").write_text('{"token": "old"}')
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        events = "\n".join(json.dumps(e) for e in CODEX_EVENTS)
        (bin_dir / "codex").write_text(f"#!/bin/sh\n{session}\ncat <<'EOF'\n{events}\nEOF\n")
        (bin_dir / "codex").chmod(0o755)
        work, out, scratch = self.root / "work", self.root / "out", self.root / "scratch"
        for path in (work, out, scratch):
            path.mkdir()
        environment = {"CODEX_HOME": str(real_home), "PATH": f"{bin_dir}:{os.environ['PATH']}"}
        with mock.patch.dict(os.environ, environment):
            result = hosts.Codex().run(skills=None, prompt="p", work=work, out=out,
                                       settings={"model": "fake"}, scratch=scratch, variant="v")
        return result, real_home / "auth.json"

    def test_codex_may_refresh_the_real_login_through_its_link(self):
        result, login = self.codex("""printf '{"token": "refreshed"}' > "$CODEX_HOME/auth.json\"""")
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual(login.read_text(), '{"token": "refreshed"}')
        self.assertFalse(login.is_symlink())

    def test_a_real_login_that_stops_being_a_regular_file_fails_the_session(self):
        result, login = self.codex("""real=$(readlink "$CODEX_HOME/auth.json"); rm "$real"; ln -s /dev/null "$real\"""")
        self.assertEqual(result.status, "error")
        self.assertIn("no longer a regular file", result.error)

    def test_a_session_that_replaces_the_link_fails(self):
        result, login = self.codex("""rm "$CODEX_HOME/auth.json"; echo '{}' > "$CODEX_HOME/auth.json\"""")
        self.assertEqual(result.status, "error")
        self.assertIn("replaced the login link", result.error)
        self.assertEqual(login.read_text(), '{"token": "old"}')


if __name__ == "__main__":
    unittest.main()
