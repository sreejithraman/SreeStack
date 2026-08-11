from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "showroom" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from showroom_lib.errors import ConfigurationError  # noqa: E402
from showroom_lib.testflight import (  # noqa: E402
    _RejectRedirects,
    _der_signature_to_raw,
    _get_collection,
    _xcode_app,
    allocate_testflight_build,
)


class TestFlightBuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = SimpleNamespace(
            working_directory=self.root,
            ios={"project": "Deal.xcodeproj", "scheme": "Deal"},
        )
        self.environment = {
            "SHOWROOM_APPLE_KEY_ID": "KEY123",
            "SHOWROOM_APPLE_ISSUER_ID": "issuer-123",
            "SHOWROOM_APPLE_KEY_PATH": "/private/key.p8",
        }

    def test_allocates_after_remote_and_local_numbers(self) -> None:
        with (
            patch(
                "showroom_lib.testflight._xcode_app",
                return_value=("world.sree.deal", "1.1", "IOS"),
            ),
            patch("showroom_lib.testflight._app_store_build_numbers", return_value=["1", "2"]),
        ):
            first = allocate_testflight_build(self.root / "state", self.config, self.environment)
            second = allocate_testflight_build(self.root / "state", self.config, self.environment)
        self.assertEqual("3", first.number)
        self.assertEqual("4", second.number)
        store = json.loads(
            (self.root / "state/credentials/apple/build-numbers.json").read_text(encoding="utf-8")
        )
        self.assertEqual(4, store["allocations"]["world.sree.deal/1.1"])

    def test_new_app_version_gets_a_fresh_counter(self) -> None:
        with (
            patch(
                "showroom_lib.testflight._xcode_app",
                return_value=("world.sree.deal", "1.1", "IOS"),
            ),
            patch("showroom_lib.testflight._app_store_build_numbers", return_value=[]),
        ):
            first = allocate_testflight_build(self.root / "state", self.config, self.environment)
        with (
            patch(
                "showroom_lib.testflight._xcode_app",
                return_value=("world.sree.deal", "1.2", "IOS"),
            ),
            patch("showroom_lib.testflight._app_store_build_numbers", return_value=[]),
        ):
            second = allocate_testflight_build(self.root / "state", self.config, self.environment)
        self.assertEqual("1", first.number)
        self.assertEqual("1", second.number)

    def test_existing_timestamp_number_remains_monotonic(self) -> None:
        with (
            patch(
                "showroom_lib.testflight._xcode_app",
                return_value=("world.sree.deal", "1.0", "IOS"),
            ),
            patch(
                "showroom_lib.testflight._app_store_build_numbers",
                return_value=["20260731163520"],
            ),
        ):
            allocation = allocate_testflight_build(
                self.root / "state", self.config, self.environment
            )
        self.assertEqual("20260731163521", allocation.number)

    def test_noninteger_build_requires_a_new_app_version(self) -> None:
        with (
            patch(
                "showroom_lib.testflight._xcode_app",
                return_value=("world.sree.deal", "1.1", "IOS"),
            ),
            patch("showroom_lib.testflight._app_store_build_numbers", return_value=["1.2"]),
            self.assertRaisesRegex(ConfigurationError, "positive integer"),
        ):
            allocate_testflight_build(self.root / "state", self.config, self.environment)

    def test_reads_one_app_target_from_xcode(self) -> None:
        payload = json.dumps(
            [
                {
                    "buildSettings": {
                        "WRAPPER_EXTENSION": "app",
                        "PRODUCT_TYPE": "com.apple.product-type.application",
                        "PRODUCT_BUNDLE_IDENTIFIER": "world.sree.deal",
                        "MARKETING_VERSION": "1.1",
                        "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator",
                    }
                },
                {"buildSettings": {"WRAPPER_EXTENSION": "xctest"}},
            ]
        )
        completed = subprocess.CompletedProcess(("xcodebuild",), 0, payload, "")
        with patch("showroom_lib.testflight.subprocess.run", return_value=completed):
            self.assertEqual(("world.sree.deal", "1.1", "IOS"), _xcode_app(self.config))

    def test_ignores_non_primary_app_products_in_scheme(self) -> None:
        payload = json.dumps(
            [
                {
                    "buildSettings": {
                        "PRODUCT_TYPE": "com.apple.product-type.application",
                        "PRODUCT_BUNDLE_IDENTIFIER": "world.sree.deal",
                        "MARKETING_VERSION": "1.1",
                        "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator",
                    }
                },
                {
                    "buildSettings": {
                        "PRODUCT_TYPE": "com.apple.product-type.application.watchapp2",
                        "PRODUCT_BUNDLE_IDENTIFIER": "world.sree.deal.watchkitapp",
                        "MARKETING_VERSION": "1.1",
                        "PLATFORM_NAME": "watchos",
                    }
                },
            ]
        )
        completed = subprocess.CompletedProcess(("xcodebuild",), 0, payload, "")
        with patch("showroom_lib.testflight.subprocess.run", return_value=completed):
            self.assertEqual(("world.sree.deal", "1.1", "IOS"), _xcode_app(self.config))

    def test_rejects_a_target_with_more_than_one_app_store_platform(self) -> None:
        payload = json.dumps(
            [
                {
                    "buildSettings": {
                        "PRODUCT_TYPE": "com.apple.product-type.application",
                        "PRODUCT_BUNDLE_IDENTIFIER": "world.sree.deal",
                        "MARKETING_VERSION": "1.1",
                        "SUPPORTED_PLATFORMS": "iphoneos macosx",
                    }
                }
            ]
        )
        completed = subprocess.CompletedProcess(("xcodebuild",), 0, payload, "")
        with (
            patch("showroom_lib.testflight.subprocess.run", return_value=completed),
            self.assertRaisesRegex(ConfigurationError, "one App Store platform"),
        ):
            _xcode_app(self.config)

    def test_filters_prerelease_versions_by_platform(self) -> None:
        responses = [
            {"data": [{"id": "app-1"}], "links": {}},
            {"data": [], "links": {}},
        ]
        with (
            patch("showroom_lib.testflight._app_store_token", return_value="secret"),
            patch("showroom_lib.testflight._request_json", side_effect=responses) as request,
        ):
            from showroom_lib.testflight import _app_store_build_numbers

            self.assertEqual(
                [],
                _app_store_build_numbers("world.sree.deal", "1.1", "IOS", {}),
            )
        self.assertIn("filter%5Bplatform%5D=IOS", request.call_args_list[1].args[0])

    def test_rejects_cross_origin_pagination(self) -> None:
        payload = {"data": [], "links": {"next": "https://example.com/steal"}}
        with (
            patch("showroom_lib.testflight._request_json", return_value=payload) as request,
            self.assertRaisesRegex(ConfigurationError, "unsafe page URL"),
        ):
            _get_collection("/v1/apps", "secret", {})
        request.assert_called_once()

    def test_rejects_http_redirects(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "redirected unexpectedly"):
            _RejectRedirects().redirect_request(None, None, 302, "Found", {}, "https://example.com")

    def test_converts_openssl_der_signature_to_jwt_shape(self) -> None:
        r = b"\x01" * 32
        s = b"\x80" + b"\x02" * 31
        der = b"\x30\x45\x02\x20" + r + b"\x02\x21\x00" + s
        self.assertEqual(r + s, _der_signature_to_raw(der))


if __name__ == "__main__":
    unittest.main()
