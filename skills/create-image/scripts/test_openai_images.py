"""Run the real CLI against a scripted local Images API."""

import base64
import email.parser
import errno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import ssl
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
from urllib.error import URLError
import zlib


CLI = Path(__file__).with_name("openai_images.py")
KEY = "sk-test-SECRETVALUE1234567890"


def png_bytes(color_type=6):
    def chunk(kind, data):
        checksum = zlib.crc32(kind + data)
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)

    header = struct.pack(">IIBBBBB", 1, 1, 8, color_type, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"\0\0\0\0\0")) + chunk(b"IEND", b"")


PNG = png_bytes()
JPEG = b"\xff\xd8\xff\xe0" + b"jpeg-bytes" + b"\xff\xd9"


def image_response(*images):
    return json_response(200, {
        "created": 1,
        "data": [{"b64_json": base64.b64encode(image).decode(), "revised_prompt": "revised"} for image in images],
        "usage": {"input_tokens": 3, "output_tokens": 5, "total_tokens": 8},
    })


def json_response(status, body, headers=None):
    return {"status": status, "body": json.dumps(body).encode(), "headers": headers or {}}


def api_error(status, code=None, error_type=None, message="nope", headers=None, **extra):
    return json_response(status, {"error": {"code": code, "type": error_type, "message": message, **extra}}, headers)


class FakeApi(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.server.requests.append({"path": self.path, "headers": self.headers, "body": body})
        script = self.server.script
        step = script.pop(0) if len(script) > 1 else script[0]
        if callable(step):
            step = step()
        if step == "drop":
            self.connection.shutdown(socket.SHUT_RDWR)
            return
        if step == "hang":
            time.sleep(1.0)
            return
        if step == "drip":
            self.drip()
            return
        if step == "slow-error":
            self.drip(api_error(400, "moderation_blocked", "image_generation_user_error"))
            return
        self.send_response(step["status"])
        for name, value in step["headers"].items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(step["body"])))
        self.send_header("x-request-id", "req_test")
        self.end_headers()
        self.wfile.write(step["body"])

    do_GET = do_POST

    def drip(self, response=None):
        """Keep every socket wait short while the whole response runs long."""
        response = response or image_response(PNG)
        body = response["body"]
        self.send_response(response["status"])
        self.send_header("x-request-id", "req_test")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            for start in range(0, len(body), len(body) // 12):
                self.wfile.write(body[start:start + len(body) // 12])
                self.wfile.flush()
                time.sleep(0.1)
        except OSError:
            pass

    def do_CONNECT(self):
        self.server.requests.append({"path": self.path, "headers": self.headers, "body": b""})
        self.send_error(403)


class CliTestCase(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(os.path.realpath(directory.name))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApi)
        self.server.requests = []
        self.server.script = [image_response(PNG)]
        thread = threading.Thread(target=self.server.serve_forever, args=(0.01,), daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.base = f"http://127.0.0.1:{self.server.server_port}/v1"

    def cli(self, *args, code=0, key=KEY, base=None, stdin=None, proxy=None):
        env = {name: value for name, value in os.environ.items() if name != "OPENAI_API_KEY"}
        env["OPENAI_IMAGES_BASE_URL"] = base or self.base
        env["NO_PROXY"] = env["no_proxy"] = "" if proxy else "127.0.0.1"
        if proxy:
            env["https_proxy"] = proxy
        if key is not None:
            env["OPENAI_API_KEY"] = key
        result = subprocess.run(
            [sys.executable, str(CLI), *args], env=env, input=stdin, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertNotIn(KEY, result.stdout)
        return json.loads(result.stdout)

    def generate(self, *args, out="out.png", code=0, **kwargs):
        return self.cli("generate", "--prompt", "a red kite", "--out", str(self.root / out), *args, code=code, **kwargs)

    def script(self, *steps):
        self.server.script = list(steps)

    def load_cli(self):
        sys.path.insert(0, str(CLI.parent))
        self.addCleanup(sys.path.remove, str(CLI.parent))
        import openai_images
        return openai_images

    def write(self, name, data=PNG):
        path = self.root / name
        path.write_bytes(data)
        return str(path)


class Help(CliTestCase):
    def test_help_lists_operations_and_flags(self):
        top = subprocess.run([sys.executable, str(CLI), "--help"], text=True, capture_output=True, check=True).stdout
        self.assertIn("generate", top)
        self.assertIn("edit", top)
        self.assertIn("Exit codes", top)
        edit = subprocess.run([sys.executable, str(CLI), "edit", "--help"], text=True, capture_output=True, check=True).stdout
        for flag in ("--image", "--mask", "--require-model", "--dry-run", "sunburst"):
            self.assertIn(flag, edit)

    def test_usage_error_is_json(self):
        result = subprocess.run([sys.executable, str(CLI), "generate", "--prompt", "x"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason"], "usage")


class DryRun(CliTestCase):
    def test_needs_no_key_and_touches_nothing(self):
        result = self.generate("--dry-run", out="new/folder/out.png", key=None)
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["credential"], {"env": "OPENAI_API_KEY", "usable": False})
        self.assertEqual(result["model"], "gpt-image-2.6-flare")
        self.assertEqual(result["planned_outputs"], [str(self.root / "new/folder/out.png")])
        self.assertEqual(result["request"]["prompt_chars"], len("a red kite"))
        self.assertEqual(result["api"]["outcome"], "not_sent")
        self.assertNotIn("prompt", result["request"])
        self.assertEqual(self.server.requests, [])
        self.assertFalse((self.root / "new").exists())

    def test_reports_a_usable_key_without_its_value(self):
        self.assertTrue(self.generate("--dry-run")["credential"]["usable"])

    def test_edit_validates_inputs(self):
        image = self.write("in.png")
        result = self.cli("edit", "--image", image, "--prompt", "x", "--out", str(self.root / "o.png"), "--dry-run", key=None)
        self.assertEqual(result["inputs"], [{"path": image, "format": "png", "bytes": len(PNG)}])
        self.cli("edit", "--image", image + ".missing", "--prompt", "x", "--out", str(self.root / "o.png"), "--dry-run", code=2)


class Generate(CliTestCase):
    def test_default_request_and_saved_file(self):
        result = self.generate("--size", "1536x1024", "--quality", "low", "--complexity", "medium")
        request = self.server.requests[0]
        self.assertEqual(request["path"], "/v1/images/generations")
        self.assertEqual(request["headers"]["Authorization"], f"Bearer {KEY}")
        self.assertEqual(request["headers"]["Content-Type"], "application/json")
        self.assertEqual(request["headers"]["User-Agent"], "create-image-skill/1")
        self.assertEqual(json.loads(request["body"]), {
            "model": "gpt-image-2.6-flare", "prompt": "a red kite", "n": 1, "output_format": "png",
            "size": "1536x1024", "quality": "low", "complexity": "medium",
        })
        path = self.root / "out.png"
        self.assertEqual(path.read_bytes(), PNG)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["outputs"], [{
            "path": str(path), "format": "png", "bytes": len(PNG), "revised_prompt": "revised",
        }])
        self.assertEqual(result["usage"]["total_tokens"], 8)
        self.assertEqual(result["api"]["outcome"], "succeeded")
        self.assertEqual(result["api"]["request_id"], "req_test")
        self.assertFalse(result["fallback_allowed"])
        self.assertNotIn(base64.b64encode(PNG).decode(), json.dumps(result))

    def test_model_selection(self):
        for index, (flag, expected) in enumerate((
            ([], "gpt-image-2.6-flare"),
            (["--model", "sunburst"], "gpt-image-2.6-sunburst"),
            (["--model", "Sunburst"], "gpt-image-2.6-sunburst"),
            (["--model", "flare"], "gpt-image-2.6-flare"),
            (["--model", "gpt-image-2.5-flare"], "gpt-image-2.5-flare"),
        )):
            with self.subTest(flag):
                self.server.requests.clear()
                self.assertEqual(self.generate(*flag, "--dry-run")["model"], expected)
                self.generate(*flag, out=f"model-{index}.png")
                self.assertEqual(json.loads(self.server.requests[0]["body"])["model"], expected)

    def test_keeps_the_usage_field_a_mapping(self):
        self.script(json_response(200, {"data": [{"b64_json": base64.b64encode(PNG).decode()}], "usage": "odd"}))
        self.assertIsNone(self.generate()["usage"])

    def test_rejects_a_malformed_model(self):
        result = self.generate("--model", "gpt image", code=2)
        self.assertEqual(result["reason"], "invalid_input")
        self.assertEqual(result["outputs"], [])
        self.assertFalse(result["fallback_allowed"])
        self.assertEqual(result["api"]["outcome"], "not_sent")

    def test_format_follows_the_output_extension(self):
        self.script(image_response(JPEG))
        result = self.generate("--output-compression", "80", out="out.jpg")
        body = json.loads(self.server.requests[0]["body"])
        self.assertEqual((body["output_format"], body["output_compression"]), ("jpeg", 80))
        self.assertEqual(result["outputs"][0]["format"], "jpeg")

    def test_rejects_options_the_output_format_cannot_hold(self):
        cases = (
            (["--output-compression", "50"], "out.png"),
            (["--background", "transparent"], "out.jpg"),
            ([], "out.gif"),
            (["--n", "0"], "out.png"),
            (["--n", "11"], "out.png"),
            (["--timeout", "0"], "out.png"),
            (["--timeout", "nan"], "out.png"),
            (["--timeout", "inf"], "out.png"),
        )
        for flags, out in cases:
            with self.subTest(flags=flags, out=out):
                self.assertEqual(self.generate(*flags, out=out, code=2)["reason"], "invalid_input")
        self.assertEqual(self.server.requests, [])

    def test_several_images_get_numbered_paths(self):
        self.script(image_response(PNG, PNG))
        result = self.generate("--n", "2")
        self.assertEqual([output["path"] for output in result["outputs"]],
                         [str(self.root / "out-1.png"), str(self.root / "out-2.png")])

    def test_fewer_images_than_requested_is_reported(self):
        result = self.generate("--n", "2")
        self.assertEqual(len(result["outputs"]), 1)
        self.assertIn("1 of 2", result["message"])

    def test_prompt_from_stdin_and_file(self):
        self.cli("generate", "--prompt-file", "-", "--out", str(self.root / "a.png"), stdin="from stdin")
        self.assertEqual(json.loads(self.server.requests[0]["body"])["prompt"], "from stdin")
        prompt = self.root / "prompt.txt"
        prompt.write_text("from file")
        self.cli("generate", "--prompt-file", str(prompt), "--out", str(self.root / "b.png"))
        self.assertEqual(json.loads(self.server.requests[1]["body"])["prompt"], "from file")

    def test_rejects_empty_and_oversized_prompts(self):
        for prompt in ("  ", "x" * 32001):
            self.cli("generate", "--prompt", prompt, "--out", str(self.root / "a.png"), code=2)
        self.assertEqual(self.server.requests, [])

    def test_creates_missing_output_folders(self):
        self.generate(out="new/folder/out.png")
        self.assertEqual((self.root / "new/folder/out.png").read_bytes(), PNG)


class Edit(CliTestCase):
    def test_multipart_request(self):
        first, second = self.write("private-name.png"), self.write("two.jpg", JPEG)
        mask = self.write("mask.png", png_bytes(color_type=6))
        self.cli("edit", "--image", first, "--image", second, "--mask", mask, "--prompt", "add a hat",
                 "--model", "sunburst", "--out", str(self.root / "out.png"))
        request = self.server.requests[0]
        self.assertEqual(request["path"], "/v1/images/edits")
        message = email.parser.BytesParser().parsebytes(
            b"Content-Type: " + request["headers"]["Content-Type"].encode() + b"\r\n\r\n" + request["body"]
        )
        parts = [(part.get_param("name", header="content-disposition"), part) for part in message.get_payload()]
        fields = {name: part.get_payload(decode=True) for name, part in parts}
        self.assertEqual(fields["prompt"], b"add a hat")
        self.assertEqual(fields["model"], b"gpt-image-2.6-sunburst")
        self.assertEqual(fields["output_format"], b"png")
        self.assertEqual(fields["n"], b"1")
        images = [part for name, part in parts if name == "image[]"]
        self.assertEqual([part.get_payload(decode=True) for part in images], [PNG, JPEG])
        self.assertEqual([part.get_content_type() for part in images], ["image/png", "image/jpeg"])
        self.assertEqual(fields["mask"], png_bytes(color_type=6))
        self.assertNotIn(b"private-name", request["body"])

    def test_rejects_unusable_inputs_before_sending(self):
        text = self.write("note.png", b"not an image")
        empty = self.write("empty.png", b"")
        big = self.root / "big.png"
        with big.open("wb") as file:
            file.write(PNG)
            file.truncate(50 * 1024 * 1024)
        cases = ([str(self.root / "gone.png")], [text], [empty], [str(big)], [self.write("ok.png")] * 17)
        for images in cases:
            with self.subTest(images=images[0]):
                flags = [flag for image in images for flag in ("--image", image)]
                result = self.cli("edit", *flags, "--prompt", "x", "--out", str(self.root / "o.png"), code=2)
                self.assertEqual(result["reason"], "invalid_input")
        self.assertEqual(self.server.requests, [])

    def test_rejects_a_mask_without_alpha(self):
        image = self.write("in.png")
        for mask in (self.write("rgb.png", png_bytes(color_type=2)), self.write("mask.jpg", JPEG)):
            result = self.cli("edit", "--image", image, "--mask", mask, "--prompt", "x",
                              "--out", str(self.root / "o.png"), code=2)
            self.assertIn("alpha", result["message"])
        self.assertEqual(self.server.requests, [])


class OutputSafety(CliTestCase):
    def test_refuses_an_existing_output_before_paying(self):
        path = self.write("out.png", b"original")
        result = self.generate(code=2)
        self.assertEqual(result["reason"], "output_exists")
        self.assertEqual(self.server.requests, [])
        self.assertEqual(Path(path).read_bytes(), b"original")

    def test_refuses_to_replace_the_edit_source(self):
        source = self.write("in.png")
        result = self.cli("edit", "--image", source, "--prompt", "x", "--out", source, code=2)
        self.assertEqual(result["reason"], "output_exists")

    def test_refuses_a_numbered_output_collision(self):
        self.write("out-2.png", b"original")
        self.assertEqual(self.generate("--n", "2", code=2)["reason"], "output_exists")

    def test_refuses_a_dangling_symlink(self):
        (self.root / "out.png").symlink_to(self.root / "elsewhere.png")
        self.assertEqual(self.generate(code=2)["reason"], "output_exists")
        self.assertFalse((self.root / "elsewhere.png").exists())

    def test_keeps_a_file_that_appears_during_the_request(self):
        path = self.root / "out.png"

        def respond():
            path.write_bytes(b"arrived first")
            return image_response(PNG)

        self.script(respond)
        result = self.generate()
        self.assertEqual(path.read_bytes(), b"arrived first")
        saved = result["outputs"][0]
        self.assertEqual(saved["requested_path"], str(path))
        self.assertEqual(Path(saved["path"]).read_bytes(), PNG)

    def test_refuses_an_unwritable_folder_before_paying(self):
        locked = self.root / "locked"
        locked.mkdir()
        locked.chmod(stat.S_IRUSR | stat.S_IXUSR)
        self.addCleanup(locked.chmod, stat.S_IRWXU)
        if os.access(locked, os.W_OK):
            self.skipTest("This user can write through read-only folders.")
        self.assertEqual(self.generate(out="locked/out.png", code=2)["reason"], "invalid_input")
        self.assertEqual(self.server.requests, [])

    def test_a_failed_save_stops_without_fallback(self):
        locked = self.root / "locked"
        locked.mkdir()
        self.addCleanup(locked.chmod, stat.S_IRWXU)

        def respond():
            locked.chmod(stat.S_IRUSR | stat.S_IXUSR)
            return image_response(PNG)

        if os.getuid() == 0:
            self.skipTest("Root can write through read-only folders.")
        self.script(respond)
        result = self.generate(out="locked/out.png", code=4)
        self.assertEqual(result["reason"], "output_write_failed")
        self.assertEqual(result["api"]["outcome"], "succeeded")
        self.assertTrue(result["api"]["may_have_charged"])
        self.assertFalse(result["fallback_allowed"])
        self.assertIn("may be billed", result["message"])
        self.assertNotIn("unknown", result["message"])

    def test_a_failed_save_still_reports_the_images_already_saved(self):
        stem = "x" * 249  # "-9.png" reaches the 255-byte name limit, so "-10.png" cannot be created.
        self.script(image_response(*[PNG] * 10))
        result = self.generate("--n", "10", out=f"{stem}.png", code=4)
        self.assertEqual(result["reason"], "output_write_failed")
        self.assertEqual(len(result["outputs"]), 9)
        for output in result["outputs"]:
            self.assertEqual(Path(output["path"]).read_bytes(), PNG)


class Credentials(CliTestCase):
    def test_missing_key_falls_back_without_sending(self):
        for key in (None, "", "  "):
            with self.subTest(key=key):
                result = self.generate(code=3, key=key)
                self.assertEqual(result["reason"], "missing_credentials")
                self.assertTrue(result["fallback_allowed"])
                self.assertEqual(result["api"]["outcome"], "not_sent")
                self.assertFalse(result["api"]["may_have_charged"])
        self.assertEqual(self.server.requests, [])

    def test_malformed_key_is_never_sent_or_echoed(self):
        result = self.generate(code=3, key="sk-line\nbreak")
        self.assertEqual(result["reason"], "missing_credentials")
        self.assertNotIn("break", json.dumps(result))
        self.assertEqual(self.server.requests, [])

    def test_required_model_blocks_the_fallback(self):
        result = self.generate("--model", "sunburst", "--require-model", code=5, key=None)
        self.assertEqual(result["reason"], "missing_credentials")
        self.assertFalse(result["fallback_allowed"])

    def test_local_problems_outrank_missing_credentials(self):
        self.assertEqual(self.generate(out="out.gif", code=2, key=None)["reason"], "invalid_input")

    def test_key_shaped_text_in_local_errors_is_scrubbed(self):
        self.assertNotIn("SECRETVALUE", json.dumps(self.generate("--model", f"{KEY} x", code=2)))

    def test_key_shaped_text_in_api_errors_is_scrubbed(self):
        self.script(api_error(401, "invalid_api_key", message=f"Bad key {KEY} and sk-abc***xyz, Bearer token123"))
        result = self.generate(code=3)
        self.assertNotIn("SECRETVALUE", json.dumps(result))
        self.assertNotIn("sk-abc", json.dumps(result))
        self.assertNotIn("token123", json.dumps(result))

    def test_unrelated_words_survive_scrubbing(self):
        self.script(api_error(400, message="This task-based risk-free request failed"))
        self.assertIn("task-based risk-free", self.generate(code=4)["api"]["message"])

    def test_refuses_to_send_the_key_to_a_remote_override(self):
        for base in ("http://example.com/v1", "https://example.com/v1"):
            self.assertEqual(self.generate(code=2, base=base)["reason"], "invalid_input")


class Outcomes(CliTestCase):
    def test_availability_failures_permit_fallback(self):
        cases = (
            ("credits gone", api_error(429, "credit_balance_exhausted", "insufficient_quota"), "quota_exhausted"),
            ("quota type only", api_error(429, None, "insufficient_quota"), "quota_exhausted"),
            ("project spend", api_error(429, "project_spend_limit_exceeded"), "quota_exhausted"),
            ("org spend", api_error(429, "organization_spend_limit_exceeded"), "quota_exhausted"),
            ("org usage", api_error(429, "organization_usage_limit_exceeded"), "quota_exhausted"),
            ("bad key", api_error(401, "invalid_api_key"), "access_denied"),
            ("region", api_error(403), "access_denied"),
            ("no model access", api_error(403, "model_not_found"), "model_unavailable"),
            ("unknown model", api_error(404, "model_not_found"), "model_unavailable"),
            ("rate", api_error(429, "rate_limit_exceeded", headers={"Retry-After": "0"}), "rate_limited"),
            ("overloaded", api_error(503, "server_is_overloaded", headers={"Retry-After": "0"}), "overloaded"),
            ("overloaded type", api_error(503, None, "service_unavailable_error", headers={"Retry-After": "0"}), "overloaded"),
        )
        for name, step, reason in cases:
            with self.subTest(name):
                self.script(step)
                result = self.generate(code=3)
                self.assertEqual(result["reason"], reason)
                self.assertTrue(result["fallback_allowed"])
                self.assertEqual(result["api"]["outcome"], "rejected")
                self.assertFalse(result["api"]["may_have_charged"])

                self.assertFalse(self.generate("--require-model", code=5)["fallback_allowed"])
        self.assertFalse((self.root / "out.png").exists())

    def test_refusals_and_invalid_requests_never_fall_back(self):
        moderation = {"moderation_stage": "input", "categories": ["harassment"]}
        cases = (
            ("blocked", api_error(400, "moderation_blocked", "image_generation_user_error",
                                  moderation_details=moderation), "refused"),
            ("blocked, no details", api_error(400, "moderation_blocked"), "refused"),
            ("legacy policy", api_error(400, "content_policy_violation"), "refused"),
            ("details alone", api_error(400, moderation_details={}), "refused"),
            ("details alone on a rate limit", api_error(429, moderation_details={}, headers={"Retry-After": "0"}), "refused"),
            ("details alone on overload", api_error(503, moderation_details={}, headers={"Retry-After": "0"}), "refused"),
            ("null stage on a rate limit", api_error(429, moderation_details={"moderation_stage": None},
                                                     headers={"Retry-After": "0"}), "refused"),
            ("odd details on a server error", api_error(500, moderation_details="blocked"), "refused"),
            ("blocked with odd status", api_error(403, "moderation_blocked"), "refused"),
            ("user error", api_error(400, "bad_image", "image_generation_user_error"), "user_error"),
            ("user error with odd status", api_error(429, "bad_image", "image_generation_user_error"), "user_error"),
            ("bad parameter", api_error(400, "invalid_value", "invalid_request_error"), "invalid_request"),
            ("too large", api_error(413), "invalid_request"),
            ("unknown client error", api_error(418), "invalid_request"),
            ("html client error", {"status": 400, "body": b"<html>", "headers": {}}, "invalid_request"),
            ("cut-off error body", {"status": 400, "body": b"{", "headers": {"Content-Length": "10"}}, "invalid_request"),
        )
        for name, step, reason in cases:
            with self.subTest(name):
                self.server.requests.clear()
                self.script(step)
                result = self.generate(code=4)
                self.assertEqual(result["reason"], reason)
                self.assertFalse(result["fallback_allowed"])
                self.assertEqual(len(self.server.requests), 1)

    def test_required_model_keeps_refusals_on_their_own_exit(self):
        self.script(api_error(400, "moderation_blocked"))
        self.assertEqual(self.generate("--require-model", code=4)["reason"], "refused")

    def test_output_stage_refusal_may_be_billed(self):
        for stage, charged in (("input", False), ("output", True), ("unknown", True)):
            with self.subTest(stage):
                self.script(api_error(400, "moderation_blocked", moderation_details={"moderation_stage": stage}))
                result = self.generate(code=4)
                self.assertEqual(result["api"]["moderation_stage"], stage)
                self.assertEqual(result["api"]["may_have_charged"], charged)

    def test_refusal_or_user_error_without_a_stage_may_be_billed(self):
        for step in (api_error(400, "moderation_blocked"), api_error(400, "bad_image", "image_generation_user_error")):
            self.script(step)
            self.assertTrue(self.generate(code=4)["api"]["may_have_charged"])

    def test_the_api_explanation_reaches_the_message(self):
        self.script(api_error(400, "invalid_value", message="Size must be a multiple of 16."))
        self.assertIn("multiple of 16", self.generate(code=4)["message"])

    def test_a_long_api_message_keeps_the_billing_notice(self):
        self.script(api_error(500, message="x" * 2000))
        result = self.generate(code=3)
        self.assertLessEqual(len(result["api"]["message"]), 500)
        self.assertTrue(result["message"].endswith("may be billed."))

    def test_explicit_load_rejection_retries_once(self):
        for step in (api_error(429, "rate_limit_exceeded", headers={"Retry-After": "0"}),
                     api_error(503, "server_is_overloaded", headers={"Retry-After": "0"})):
            with self.subTest(step["status"]):
                self.server.requests.clear()
                self.script(step, image_response(PNG))
                out = f"retry-{step['status']}.png"
                self.assertEqual(self.generate(out=out)["status"], "ok")
                self.assertEqual(len(self.server.requests), 2)

    def test_a_503_retries_only_for_a_documented_overload(self):
        retry_at_once = {"Retry-After": "0"}
        cases = (
            ("refusal", api_error(503, "moderation_blocked", headers=retry_at_once), 4),
            ("user error", api_error(503, "bad_image", "image_generation_user_error", headers=retry_at_once), 4),
            ("quota", api_error(503, "credit_balance_exhausted", headers=retry_at_once), 3),
            ("bare", {"status": 503, "body": b"<html>", "headers": retry_at_once}, 3),
        )
        for name, step, code in cases:
            with self.subTest(name):
                self.server.requests.clear()
                self.script(step, image_response(PNG))
                self.generate(code=code)
                self.assertEqual(len(self.server.requests), 1)
                self.assertFalse((self.root / "out.png").exists())

    def test_a_bare_503_may_be_billed(self):
        self.script({"status": 503, "body": b"<html>", "headers": {}})
        result = self.generate(code=3)
        self.assertEqual(result["reason"], "outcome_unknown")
        self.assertTrue(result["api"]["may_have_charged"])

    def test_retry_stops_after_one_extra_attempt(self):
        self.script(api_error(429, "rate_limit_exceeded", headers={"Retry-After": "0"}))
        self.generate(code=3)
        self.assertEqual(len(self.server.requests), 2)

    def test_too_little_time_left_keeps_a_rejection_free(self):
        self.script(api_error(429, "rate_limit_exceeded", headers={"Retry-After": "0"}), image_response(PNG))
        result = self.generate("--timeout", "119", code=3)
        self.assertEqual(result["reason"], "rate_limited")
        self.assertFalse(result["api"]["may_have_charged"])
        self.assertEqual(len(self.server.requests), 1)

    def test_the_retry_gets_only_the_time_left(self):
        openai_images = self.load_cli()
        timeouts = []

        def post_once(url, body, content_type, key, timeout, progress=None):
            timeouts.append(timeout)
            if len(timeouts) == 1:
                raise openai_images.Failure("rate_limited", retry_after=0.02)
            return b"", None

        with mock.patch.object(openai_images, "post_once", post_once):
            openai_images.post_with_retry("url", b"", "type", KEY, 130)
        self.assertEqual(timeouts[0], 130)
        self.assertLessEqual(timeouts[1], 129.98)

    def test_the_timeout_bounds_the_whole_exchange(self):
        self.script("drip")
        result = self.generate("--timeout", "0.4", code=3)
        self.assertEqual(result["reason"], "outcome_unknown")
        self.assertTrue(result["api"]["may_have_charged"])
        self.assertFalse((self.root / "out.png").exists())

    def test_a_slow_error_body_stops_without_fallback(self):
        self.script("slow-error")
        started = time.monotonic()
        result = self.generate("--timeout", "0.3", code=4)
        self.assertLess(time.monotonic() - started, 1.0)
        self.assertEqual(result["reason"], "incomplete_error")
        self.assertEqual(result["api"]["http_status"], 400)
        self.assertEqual(result["api"]["request_id"], "req_test")
        self.assertFalse(result["fallback_allowed"])
        self.assertEqual(len(self.server.requests), 1)

    def test_long_retry_after_goes_straight_to_fallback(self):
        self.script(api_error(429, "rate_limit_exceeded", headers={"Retry-After": "120"}))
        self.assertEqual(self.generate(code=3)["reason"], "rate_limited")
        self.assertEqual(len(self.server.requests), 1)

    def test_billing_errors_never_retry(self):
        self.script(api_error(429, "credit_balance_exhausted", headers={"Retry-After": "0"}))
        self.generate(code=3)
        self.assertEqual(len(self.server.requests), 1)

    def test_ambiguous_failures_disclose_and_never_retry(self):
        cases = (
            ("server error", api_error(500)),
            ("gateway error", {"status": 502, "body": b"<html>bad gateway", "headers": {}}),
            ("dropped", "drop"),
            ("cut off mid-body", {"status": 200, "body": b"{", "headers": {"Content-Length": "10"}}),
            ("timed out", "hang"),
        )
        for name, step in cases:
            with self.subTest(name):
                self.server.requests.clear()
                self.script(step)
                result = self.generate("--timeout", "0.3", code=3)
                self.assertEqual(result["reason"], "outcome_unknown")
                self.assertEqual(result["api"]["outcome"], "unknown")
                self.assertTrue(result["api"]["may_have_charged"])
                self.assertTrue(result["fallback_allowed"])
                self.assertIn("may be billed", result["message"])
                self.assertEqual(len(self.server.requests), 1)

    def test_required_model_stops_on_ambiguity(self):
        self.script(api_error(500))
        result = self.generate("--require-model", code=5)
        self.assertTrue(result["api"]["may_have_charged"])

    def test_unusable_success_body_is_ambiguous(self):
        cases = (
            ("not json", {"status": 200, "body": b"<html>", "headers": {}}),
            ("not an object", json_response(200, [])),
            ("no data", json_response(200, {"created": 1})),
            ("empty data", json_response(200, {"data": []})),
            ("url only", json_response(200, {"data": [{"url": "https://example.com/a.png"}]})),
            ("bad base64", json_response(200, {"data": [{"b64_json": "!!!"}]})),
            ("wrong format", image_response(JPEG)),
            ("not an image", image_response(b"hello")),
        )
        for name, step in cases:
            with self.subTest(name):
                self.script(step)
                result = self.generate(code=3)
                self.assertEqual(result["reason"], "outcome_unknown")
                self.assertEqual(result["api"]["outcome"], "unknown")
                self.assertEqual(result["api"]["http_status"], 200)
                self.assertEqual(result["api"]["request_id"], "req_test")
                self.assertTrue(result["api"]["may_have_charged"])
                self.assertFalse((self.root / "out.png").exists())

    def test_unreachable_api_is_not_a_charge(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        result = self.generate(code=3, base=f"http://127.0.0.1:{port}/v1")
        self.assertEqual(result["reason"], "network_error")
        self.assertEqual(result["api"]["outcome"], "not_sent")
        self.assertFalse(result["api"]["may_have_charged"])

    def test_a_refused_proxy_tunnel_is_not_a_charge(self):
        result = self.generate(code=3, base="https://127.0.0.1:9/v1", proxy=f"http://127.0.0.1:{self.server.server_port}")
        self.assertEqual(self.server.requests[0]["path"], "127.0.0.1:9")
        self.assertEqual(result["reason"], "network_error")
        self.assertEqual(result["api"]["outcome"], "not_sent")
        self.assertFalse(result["api"]["may_have_charged"])

    def test_a_connection_lost_while_sending_or_waiting_may_be_billed(self):
        openai_images = self.load_cli()
        for name, error in (
            ("route lost while waiting", OSError(errno.EHOSTUNREACH, "No route to host")),
            ("blocked while waiting", PermissionError()),
            ("blocked while sending", URLError(PermissionError())),
            ("route lost while sending", URLError(OSError(errno.EHOSTUNREACH, "No route to host"))),
            ("network lost while sending", URLError(OSError(errno.ENETUNREACH, "Network is unreachable"))),
            ("reset while sending", URLError(ConnectionResetError())),
        ):
            with self.subTest(name):
                class BrokenOpener:
                    def open(self, request, timeout):
                        raise error

                with mock.patch.object(openai_images.urllib.request, "build_opener", lambda *_: BrokenOpener()):
                    with self.assertRaises(openai_images.Failure) as caught:
                        openai_images.post_once("http://127.0.0.1/v1", b"{}", "application/json", KEY, 1)
                self.assertEqual(caught.exception.reason, "outcome_unknown")
                self.assertTrue(caught.exception.report.may_have_charged)

    def test_errors_that_only_arise_while_connecting_are_not_a_charge(self):
        openai_images = self.load_cli()
        for error in (socket.gaierror(), ConnectionRefusedError(), ssl.SSLCertVerificationError()):
            with self.subTest(type(error).__name__):
                failure = openai_images.send_failure(error)
                self.assertEqual(failure.reason, "network_error")
                self.assertFalse(failure.report.may_have_charged)

    def test_redirects_are_not_followed(self):
        self.script(json_response(302, {}, {"Location": f"{self.base}/elsewhere"}))
        result = self.generate(code=3)
        self.assertEqual(result["reason"], "api_unavailable")
        self.assertEqual(len(self.server.requests), 1)


if __name__ == "__main__":
    unittest.main()
