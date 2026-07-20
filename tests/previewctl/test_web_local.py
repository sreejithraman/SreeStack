from __future__ import annotations

import json
import plistlib
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "skills" / "preview" / "scripts"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from previewctl_lib.adapters.base import AdapterContext
from previewctl_lib.adapters.web_local import Adapter, UrllibProbe
from previewctl_lib.errors import AdapterError
from previewctl_lib.project import Manifest, Project


class FakeRunner:
    def __init__(
        self,
        *,
        serve_conflicts: dict[int, str] | None = None,
        funnel_conflicts: dict[int, str] | None = None,
        fail: str | None = None,
    ) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.route: tuple[int, str] | None = None
        self.launchd_loaded = False
        self.serve_conflicts = serve_conflicts or {}
        self.funnel_conflicts = funnel_conflicts or {}
        self.fail = fail

    def run(self, argv, **kwargs):
        command = tuple(str(value) for value in argv)
        self.calls.append(command)
        if command[1:3] == ("version", "--json"):
            return SimpleNamespace(returncode=0, stdout='{"version":"1.96.2"}', stderr="")
        if command[1:4] in {("serve", "status", "--json"), ("funnel", "status", "--json")}:
            # Current Tailscale returns the same ServeConfig from both status
            # commands. Public listeners are the exact true AllowFunnel keys.
            routes = {**self.serve_conflicts, **self.funnel_conflicts}
            if self.route is not None:
                routes[self.route[0]] = self.route[1]
            payload = {"TCP": {}, "Web": {}, "AllowFunnel": {}}
            for port, target in routes.items():
                payload["TCP"][str(port)] = {"HTTPS": True}
                payload["Web"][f"developer.example.ts.net:{port}"] = {
                    "Handlers": {"/": {"Proxy": target}}
                }
            for port in self.funnel_conflicts:
                payload["AllowFunnel"][f"developer.example.ts.net:{port}"] = True
            return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")
        if command[0] == "/bin/launchctl" and command[1] == "bootstrap":
            if self.fail == "bootstrap":
                return SimpleNamespace(returncode=5, stdout="", stderr="bootstrap failed")
            self.launchd_loaded = True
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if command[0] == "/bin/launchctl" and command[1] == "kickstart":
            if self.fail == "kickstart":
                return SimpleNamespace(returncode=5, stdout="", stderr="kickstart failed")
            return SimpleNamespace(returncode=0, stdout="8123\n", stderr="")
        if command[0] == "/bin/launchctl" and command[1] == "print":
            return SimpleNamespace(returncode=0 if self.launchd_loaded else 3, stdout="", stderr="")
        if command[0] == "/bin/launchctl" and command[1] == "bootout":
            if self.fail == "bootout":
                return SimpleNamespace(returncode=5, stdout="", stderr="bootout failed")
            self.launchd_loaded = False
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if command[1] == "serve" and "--bg" in command:
            if self.fail == "serve":
                return SimpleNamespace(returncode=1, stdout="", stderr="serve failed")
            port = int(next(item.split("=", 1)[1] for item in command if item.startswith("--https=")))
            self.route = (port, command[-1])
            return SimpleNamespace(
                returncode=0,
                stdout=f"Available within your tailnet:\nhttps://developer.example.ts.net:{port}\n",
                stderr="",
            )
        if command[1] == "serve" and command[-1] == "off":
            self.route = None
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(f"unexpected command: {command}")


class FakeProbe:
    def __init__(self, outcomes: dict[str, bool] | None = None) -> None:
        self.outcomes = outcomes or {}
        self.urls: list[str] = []

    def check(self, url: str, timeout: float) -> bool:
        self.urls.append(url)
        return self.outcomes.get(url, True)


def make_context(root: Path, approvals: dict[str, bool] | None = None) -> AdapterContext:
    worktree = root / "repo"
    worktree.mkdir()
    project = Project(worktree, worktree / ".git", worktree, "repo-id", "worktree-id", None)
    manifest = Manifest(
        path=None,
        version=1,
        kind="web",
        working_directory=worktree,
        command=("python3", "-m", "http.server", "{port}", "--bind", "{host}"),
        port="auto",
        health_check_path="/health",
        hosted_provider=None,
        privacy="tailnet",
        evidence=(),
        lease_hours=24,
        cleanup_policy="lease",
        profile="default",
        ios={},
    )
    return AdapterContext(
        project=project,
        manifest=manifest,
        state_root=root / "state",
        preview_dir=root / "state" / "previews" / "pvw_test",
        approvals=approvals or {"persistence": True, "tailscale_config": True},
    )


class WebLocalAdapterTests(unittest.TestCase):
    def test_http_probe_polls_until_a_development_server_is_ready(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.status = 200
        with mock.patch(
            "previewctl_lib.adapters.web_local.urllib.request.urlopen",
            side_effect=[urllib.error.URLError("not ready"), response],
        ) as urlopen, mock.patch(
            "previewctl_lib.adapters.web_local.time.monotonic",
            side_effect=[0.0, 0.1, 0.2, 0.3],
        ), mock.patch("previewctl_lib.adapters.web_local.time.sleep"):
            self.assertTrue(UrllibProbe().check("http://127.0.0.1:43100/health", 1.0))
        self.assertEqual(2, urlopen.call_count)

    def test_start_creates_exact_private_route_and_verified_patch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            probe = FakeProbe()
            adapter = Adapter(
                runner=runner,
                http_probe=probe,
                clock=lambda: datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )

            patch = adapter.start({"id": "pvw_test", "resources": {}}, make_context(Path(directory)))

            self.assertEqual("active", patch["status"])
            self.assertEqual("https://developer.example.ts.net:44100", patch["surface"]["url"])
            self.assertEqual(43100, patch["resources"]["port"])
            self.assertEqual(44100, patch["resources"]["serve"]["port"])
            self.assertEqual("passed", patch["verification"]["status"])
            self.assertIn((
                "/usr/local/bin/tailscale",
                "serve",
                "--bg",
                "--https=44100",
                "http://127.0.0.1:43100",
            ), runner.calls)
            self.assertIn((
                "/bin/launchctl",
                "bootstrap",
                "gui/501",
                str(Path(directory) / "state" / "previews" / "pvw_test" / "origin.plist"),
            ), runner.calls)
            self.assertEqual(
                [
                    "http://127.0.0.1:43100/health",
                    "https://developer.example.ts.net:44100/health",
                ],
                probe.urls,
            )
            plist_path = Path(patch["resources"]["launchd"]["plist_path"])
            plist = plistlib.loads(plist_path.read_bytes())
            self.assertTrue(Path(plist["ProgramArguments"][0]).is_absolute())
            self.assertIn("PATH", plist["EnvironmentVariables"])
            self.assertTrue(Path(patch["resources"]["ownership_path"]).is_file())

    def test_stop_uses_only_exact_registered_route_and_launchd_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            patch = adapter.start(record, context)
            record.update(patch)
            runner.calls.clear()

            result = adapter.stop(record, context)

            target = record["resources"]["launchd"]["target"]
            self.assertEqual("stopped", result["status"])
            self.assertIn(
                ("/usr/local/bin/tailscale", "serve", "--https=44100", "off"),
                runner.calls,
            )
            self.assertIn(("/bin/launchctl", "bootout", target), runner.calls)
            self.assertFalse(Path(record["resources"]["launchd"]["plist_path"]).exists())
            for command in runner.calls:
                self.assertNotIn("reset", command)
                self.assertNotIn(command[0], {"pkill", "killall", "kill"})
                if len(command) > 1 and command[1] == "funnel":
                    self.assertEqual(("funnel", "status", "--json"), command[1:])

            runner.calls.clear()
            record.update(result)
            self.assertEqual({"status": "stopped"}, adapter.stop(record, None))
            self.assertEqual([], runner.calls)

    def test_reconcile_is_idempotent_and_read_only_when_preview_is_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            probe = FakeProbe()
            adapter = Adapter(
                runner=runner,
                http_probe=probe,
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            record.update(adapter.start(record, context))
            runner.calls.clear()
            probe.urls.clear()

            first = adapter.reconcile(record, None)
            second = adapter.reconcile(record, None)

            self.assertEqual("passed", first["verification"]["status"])
            self.assertEqual(first["verification"]["detail"], second["verification"]["detail"])
            self.assertEqual(
                [
                    "http://127.0.0.1:43100/health",
                    "https://developer.example.ts.net:44100/health",
                ] * 2,
                probe.urls,
            )
            for command in runner.calls:
                if command[0] == "/bin/launchctl":
                    self.assertEqual("print", command[1])
                else:
                    self.assertIn(command[1:4], {
                        ("serve", "status", "--json"),
                        ("funnel", "status", "--json"),
                    })

    def test_missing_approvals_fail_before_any_mutation(self) -> None:
        for approvals in (
            {"persistence": False, "tailscale_config": True},
            {"persistence": True, "tailscale_config": False},
        ):
            with self.subTest(approvals=approvals), tempfile.TemporaryDirectory() as directory:
                runner = FakeRunner()
                adapter = Adapter(
                    runner=runner,
                    http_probe=FakeProbe(),
                    tailscale_bin="/usr/local/bin/tailscale",
                    origin_ports=(43100,),
                    serve_ports=(44100,),
                    port_available=lambda host, port: True,
                    uid=501,
                )
                context = make_context(Path(directory), approvals)
                with self.assertRaises(AdapterError):
                    adapter.start({"id": "pvw_test", "resources": {}}, context)
                self.assertEqual([], runner.calls)
                self.assertFalse(context.preview_dir.exists())

    def test_allocator_skips_os_serve_and_funnel_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner(
                serve_conflicts={44100: "http://127.0.0.1:9000"},
                funnel_conflicts={44101: "http://127.0.0.1:9001"},
            )
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100, 43101),
                serve_ports=(44100, 44101, 44102),
                port_available=lambda host, port: port != 43100,
                uid=501,
            )
            patch = adapter.start({"id": "pvw_test", "resources": {}}, make_context(Path(directory)))
            self.assertEqual(43101, patch["resources"]["port"])
            self.assertEqual(44102, patch["resources"]["serve"]["port"])

    def test_bootstrap_failure_leaves_no_owned_process_route_or_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner(fail="bootstrap")
            context = make_context(Path(directory))
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            with self.assertRaisesRegex(AdapterError, "bootstrap"):
                adapter.start({"id": "pvw_test", "resources": {}}, context)
            self.assertFalse(runner.launchd_loaded)
            self.assertIsNone(runner.route)
            self.assertFalse((context.preview_dir / "origin.plist").exists())
            self.assertFalse((context.preview_dir / "ownership.json").exists())

    def test_recover_removes_exact_resources_from_an_interrupted_start(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            context = make_context(Path(directory))
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            record = {"id": "pvw_test", "status": "starting", "resources": {}}
            adapter.start(record, context)
            self.assertTrue(runner.launchd_loaded)
            self.assertIsNotNone(runner.route)

            recovered = adapter.recover(record, context)

            self.assertEqual("stopped", recovered["status"])
            self.assertFalse(runner.launchd_loaded)
            self.assertIsNone(runner.route)
            self.assertFalse((context.preview_dir / "ownership.json").exists())

    def test_origin_health_failure_boots_out_exact_launchagent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            probe = FakeProbe({"http://127.0.0.1:43100/health": False})
            context = make_context(Path(directory))
            adapter = Adapter(
                runner=runner,
                http_probe=probe,
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            with self.assertRaisesRegex(AdapterError, "origin health"):
                adapter.start({"id": "pvw_test", "resources": {}}, context)
            bootouts = [call for call in runner.calls if call[1] == "bootout"]
            self.assertEqual(1, len(bootouts))
            self.assertTrue(bootouts[0][-1].startswith("gui/501/com.sreestack.preview."))
            self.assertFalse(any(call[1:2] == ("serve",) and "--bg" in call for call in runner.calls))

    def test_serve_failure_rolls_back_origin_without_broad_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner(fail="serve")
            context = make_context(Path(directory))
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            with self.assertRaisesRegex(AdapterError, "Serve start"):
                adapter.start({"id": "pvw_test", "resources": {}}, context)
            self.assertFalse(runner.launchd_loaded)
            self.assertIsNone(runner.route)
            self.assertFalse(any("reset" in call for call in runner.calls))
            self.assertFalse(any(call[1] == "funnel" and call[2] != "status" for call in runner.calls))

    def test_tailnet_health_failure_removes_exact_route_then_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            probe = FakeProbe({"https://developer.example.ts.net:44100/health": False})
            context = make_context(Path(directory))
            adapter = Adapter(
                runner=runner,
                http_probe=probe,
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            with self.assertRaisesRegex(AdapterError, "tailnet health"):
                adapter.start({"id": "pvw_test", "resources": {}}, context)
            off_index = runner.calls.index(
                ("/usr/local/bin/tailscale", "serve", "--https=44100", "off")
            )
            bootout_index = next(index for index, call in enumerate(runner.calls) if call[1] == "bootout")
            self.assertLess(off_index, bootout_index)
            self.assertFalse(runner.launchd_loaded)
            self.assertIsNone(runner.route)

    def test_rollback_never_removes_a_route_that_changed_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()

            class ChangingProbe(FakeProbe):
                def check(self, url: str, timeout: float) -> bool:
                    self.urls.append(url)
                    if url.startswith("https://"):
                        runner.route = (44100, "http://127.0.0.1:49999")
                        return False
                    return True

            adapter = Adapter(
                runner=runner,
                http_probe=ChangingProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            with self.assertRaisesRegex(AdapterError, "tailnet health"):
                adapter.start({"id": "pvw_test", "resources": {}}, make_context(Path(directory)))
            self.assertEqual((44100, "http://127.0.0.1:49999"), runner.route)
            self.assertFalse(any(call[-1] == "off" for call in runner.calls))

    def test_failed_rollback_preserves_exact_recovery_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner(fail="bootout")
            context = make_context(Path(directory))
            probe = FakeProbe({"https://developer.example.ts.net:44100/health": False})
            adapter = Adapter(
                runner=runner,
                http_probe=probe,
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            with self.assertRaisesRegex(AdapterError, "tailnet health"):
                adapter.start({"id": "pvw_test", "resources": {}}, context)
            self.assertTrue(runner.launchd_loaded)
            self.assertIsNone(runner.route)
            self.assertTrue((context.preview_dir / "origin.plist").is_file())
            self.assertTrue((context.preview_dir / "ownership.json").is_file())

    def test_dry_run_stop_reports_exact_plan_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            record.update(adapter.start(record, context))
            runner.calls.clear()

            plan = adapter.stop(record, context, dry_run=True)

            self.assertTrue(plan["dry_run"])
            self.assertEqual(
                ["/usr/local/bin/tailscale", "serve", "--https=44100", "off"],
                plan["commands"][0],
            )
            self.assertTrue(runner.launchd_loaded)
            self.assertIsNotNone(runner.route)
            self.assertTrue(Path(record["resources"]["launchd"]["plist_path"]).exists())
            self.assertFalse(any(call[-1] == "off" or call[1] == "bootout" for call in runner.calls))

    def test_ownership_drift_fails_closed_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            record.update(adapter.start(record, context))
            plist_path = Path(record["resources"]["launchd"]["plist_path"])
            plist_path.write_text("unexpected replacement", encoding="utf-8")
            runner.calls.clear()

            with self.assertRaisesRegex(AdapterError, "ownership drift"):
                adapter.stop(record, None)
            self.assertEqual([], runner.calls)
            self.assertTrue(runner.launchd_loaded)
            self.assertIsNotNone(runner.route)

    def test_stop_recovers_after_crash_between_owned_file_unlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            record.update(adapter.start(record, context))
            Path(record["resources"]["launchd"]["plist_path"]).unlink()

            result = adapter.stop(record, context)

            self.assertEqual("stopped", result["status"])
            self.assertFalse(runner.launchd_loaded)
            self.assertIsNone(runner.route)
            self.assertFalse(Path(record["resources"]["ownership_path"]).exists())

    def test_route_ownership_drift_fails_closed_after_read_only_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            adapter = Adapter(
                runner=runner,
                http_probe=FakeProbe(),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            record.update(adapter.start(record, context))
            runner.route = (44100, "http://127.0.0.1:49999")
            runner.calls.clear()

            with self.assertRaisesRegex(AdapterError, "ownership drift"):
                adapter.stop(record, None)
            self.assertTrue(runner.launchd_loaded)
            self.assertIsNotNone(runner.route)
            self.assertFalse(any(call[-1] == "off" or call[1] == "bootout" for call in runner.calls))

    def test_verify_reports_health_failure_without_mutating_resources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = FakeRunner()
            probe = FakeProbe()
            adapter = Adapter(
                runner=runner,
                http_probe=probe,
                clock=lambda: datetime(2026, 7, 20, 13, 0, tzinfo=timezone.utc),
                tailscale_bin="/usr/local/bin/tailscale",
                origin_ports=(43100,),
                serve_ports=(44100,),
                port_available=lambda host, port: True,
                uid=501,
            )
            context = make_context(Path(directory))
            record = {"id": "pvw_test", "resources": {}}
            record.update(adapter.start(record, context))
            probe.outcomes["http://127.0.0.1:43100/health"] = False
            runner.calls.clear()

            patch = adapter.verify(record, None)

            self.assertEqual("failed", patch["verification"]["status"])
            self.assertEqual("2026-07-20T13:00:00Z", patch["verification"]["checked_at"])
            self.assertFalse(any(call[-1] == "off" or call[1] == "bootout" for call in runner.calls))

    def test_doctor_is_read_only_and_reports_provider_safety_context(self) -> None:
        runner = FakeRunner(funnel_conflicts={8443: "http://127.0.0.1:9000"})
        adapter = Adapter(
            runner=runner,
            http_probe=FakeProbe(),
            tailscale_bin="/usr/local/bin/tailscale",
            uid=501,
        )

        result = adapter.doctor()

        self.assertTrue(result["available"])
        self.assertEqual([8443], result["funnel_ports"])
        self.assertTrue(any("Certificate Transparency" in item for item in result["warnings"]))
        self.assertEqual(
            {
                ("/usr/local/bin/tailscale", "version", "--json"),
                ("/usr/local/bin/tailscale", "serve", "status", "--json"),
                ("/usr/local/bin/tailscale", "funnel", "status", "--json"),
            },
            set(runner.calls),
        )


if __name__ == "__main__":
    unittest.main()
