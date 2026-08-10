from __future__ import annotations

import base64
import fcntl
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .errors import ConfigurationError
from .project import ProjectConfig


APP_STORE_CONNECT_API = "https://api.appstoreconnect.apple.com"
APP_STORE_CONNECT_HOST = "api.appstoreconnect.apple.com"


@dataclass(frozen=True)
class TestFlightBuild:
    bundle_id: str
    version: str
    number: str


def allocate_testflight_build(
    state: Path,
    config: ProjectConfig,
    environment: Mapping[str, str],
) -> TestFlightBuild:
    bundle_id, version, platform = _xcode_app(config)
    remote_numbers = _app_store_build_numbers(bundle_id, version, platform, environment)
    remote_max = max((_integer_build(value) for value in remote_numbers), default=0)
    number = _reserve_build_number(state, bundle_id, version, remote_max)
    return TestFlightBuild(bundle_id, version, str(number))


def _xcode_app(config: ProjectConfig) -> tuple[str, str, str]:
    project = config.ios.get("project")
    scheme = config.ios.get("scheme")
    if not isinstance(project, str) or not isinstance(scheme, str):
        raise ConfigurationError("automatic TestFlight numbering needs an Xcode project and scheme")
    try:
        completed = subprocess.run(
            [
                "xcodebuild",
                "-project",
                str(config.working_directory / project),
                "-scheme",
                scheme,
                "-configuration",
                "Release",
                "-showBuildSettings",
                "-json",
            ],
            cwd=config.working_directory,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConfigurationError(f"could not read Xcode build settings: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise ConfigurationError(f"could not read Xcode build settings: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ConfigurationError("Xcode returned invalid build settings JSON") from exc
    candidates = []
    for item in payload if isinstance(payload, list) else []:
        settings = item.get("buildSettings") if isinstance(item, dict) else None
        if (
            not isinstance(settings, dict)
            or settings.get("PRODUCT_TYPE") != "com.apple.product-type.application"
        ):
            continue
        bundle_id = settings.get("PRODUCT_BUNDLE_IDENTIFIER")
        version = settings.get("MARKETING_VERSION")
        platform = _app_store_platform(settings.get("SUPPORTED_PLATFORMS"))
        if isinstance(bundle_id, str) and bundle_id and isinstance(version, str) and version:
            candidates.append((bundle_id, version, platform))
    unique = sorted(set(candidates))
    if len(unique) != 1:
        raise ConfigurationError(
            "automatic TestFlight numbering needs exactly one app target in the selected scheme"
        )
    return unique[0]


def _app_store_platform(value: Any) -> str:
    platforms = {
        "iphoneos": "IOS",
        "iphonesimulator": "IOS",
        "macosx": "MAC_OS",
        "appletvos": "TV_OS",
        "appletvsimulator": "TV_OS",
        "xros": "VISION_OS",
        "xrsimulator": "VISION_OS",
    }
    if not isinstance(value, str) or not value.split():
        raise ConfigurationError(f"automatic TestFlight numbering does not support platform {value!r}")
    names = value.split()
    if any(name not in platforms for name in names):
        raise ConfigurationError(f"automatic TestFlight numbering does not support platform {value!r}")
    selected = {platforms[name] for name in names}
    if len(selected) != 1:
        raise ConfigurationError(
            "automatic TestFlight numbering needs one App Store platform in the selected scheme"
        )
    return selected.pop()


def _app_store_build_numbers(
    bundle_id: str,
    version: str,
    platform: str,
    environment: Mapping[str, str],
) -> list[str]:
    token = _app_store_token(environment)
    apps = _get_collection(
        "/v1/apps",
        token,
        {"filter[bundleId]": bundle_id, "fields[apps]": "bundleId", "limit": "2"},
    )
    if len(apps) != 1:
        raise ConfigurationError(
            f"App Store Connect returned {len(apps)} apps for bundle ID {bundle_id}"
        )
    releases = _get_collection(
        "/v1/preReleaseVersions",
        token,
        {
            "filter[app]": apps[0]["id"],
            "filter[version]": version,
            "filter[platform]": platform,
            "fields[preReleaseVersions]": "version",
            "limit": "2",
        },
    )
    if not releases:
        return []
    if len(releases) != 1:
        raise ConfigurationError(
            f"App Store Connect returned more than one prerelease version for {version}"
        )
    builds = _get_collection(
        "/v1/builds",
        token,
        {
            "filter[preReleaseVersion]": releases[0]["id"],
            "fields[builds]": "version",
            "limit": "200",
        },
    )
    values = [item.get("attributes", {}).get("version") for item in builds]
    if not all(isinstance(value, str) for value in values):
        raise ConfigurationError("App Store Connect returned a build without a build number")
    return values


def _get_collection(path: str, token: str, query: dict[str, str]) -> list[dict[str, Any]]:
    url = f"{APP_STORE_CONNECT_API}{path}?{urllib.parse.urlencode(query)}"
    result: list[dict[str, Any]] = []
    while url:
        _validate_app_store_url(url)
        payload = _request_json(url, token)
        data = payload.get("data")
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ConfigurationError("App Store Connect returned an invalid collection")
        result.extend(data)
        next_url = payload.get("links", {}).get("next")
        url = next_url if isinstance(next_url, str) and next_url else ""
    return result


def _request_json(url: str, token: str) -> dict[str, Any]:
    _validate_app_store_url(url)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        opener = urllib.request.build_opener(_RejectRedirects())
        with opener.open(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            body = json.load(exc)
            detail = body.get("errors", [{}])[0].get("title")
        except (AttributeError, IndexError, json.JSONDecodeError):
            detail = None
        message = detail or exc.reason or f"HTTP {exc.code}"
        raise ConfigurationError(f"App Store Connect request failed: {message}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"App Store Connect request failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigurationError("App Store Connect returned invalid JSON")
    return payload


def _validate_app_store_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != APP_STORE_CONNECT_HOST:
        raise ConfigurationError("App Store Connect returned an unsafe page URL")


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        raise ConfigurationError("App Store Connect request redirected unexpectedly")


def _app_store_token(environment: Mapping[str, str], now: int | None = None) -> str:
    key_id = environment.get("SHOWROOM_APPLE_KEY_ID")
    issuer_id = environment.get("SHOWROOM_APPLE_ISSUER_ID")
    key_path = environment.get("SHOWROOM_APPLE_KEY_PATH")
    if not key_id or not issuer_id or not key_path:
        raise ConfigurationError("automatic TestFlight numbering needs App Store Connect credentials")
    issued_at = int(time.time() if now is None else now)
    header = _base64url(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}).encode())
    claims = _base64url(
        json.dumps(
            {
                "iss": issuer_id,
                "iat": issued_at,
                "exp": issued_at + 10 * 60,
                "aud": "appstoreconnect-v1",
            }
        ).encode()
    )
    unsigned = f"{header}.{claims}".encode()
    try:
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            input=unsigned,
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConfigurationError(f"could not sign the App Store Connect request: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode(errors="replace").strip() or f"exit {completed.returncode}"
        raise ConfigurationError(f"could not sign the App Store Connect request: {detail}")
    return f"{unsigned.decode()}.{_base64url(_der_signature_to_raw(completed.stdout))}"


def _der_signature_to_raw(value: bytes) -> bytes:
    cursor = 0

    def read_length() -> int:
        nonlocal cursor
        if cursor >= len(value):
            raise ConfigurationError("OpenSSL returned an invalid App Store Connect signature")
        first = value[cursor]
        cursor += 1
        if first < 0x80:
            return first
        count = first & 0x7F
        if count == 0 or cursor + count > len(value):
            raise ConfigurationError("OpenSSL returned an invalid App Store Connect signature")
        length = int.from_bytes(value[cursor : cursor + count], "big")
        cursor += count
        return length

    if not value or value[cursor] != 0x30:
        raise ConfigurationError("OpenSSL returned an invalid App Store Connect signature")
    cursor += 1
    sequence_length = read_length()
    sequence_end = cursor + sequence_length
    integers = []
    for _ in range(2):
        if cursor >= len(value) or value[cursor] != 0x02:
            raise ConfigurationError("OpenSSL returned an invalid App Store Connect signature")
        cursor += 1
        length = read_length()
        integer = value[cursor : cursor + length]
        cursor += length
        integer = integer.lstrip(b"\0")
        if not integer or len(integer) > 32:
            raise ConfigurationError("OpenSSL returned an invalid App Store Connect signature")
        integers.append(integer.rjust(32, b"\0"))
    if cursor != sequence_end or sequence_end != len(value):
        raise ConfigurationError("OpenSSL returned an invalid App Store Connect signature")
    return b"".join(integers)


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _integer_build(value: str) -> int:
    if not value.isdigit() or int(value) <= 0:
        raise ConfigurationError(
            f"automatic TestFlight numbering supports positive integer build numbers; found {value!r}"
        )
    return int(value)


def _reserve_build_number(state: Path, bundle_id: str, version: str, remote_max: int) -> int:
    root = state / "credentials" / "apple"
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    root.chmod(0o700)
    lock_path = root / "build-numbers.lock"
    store_path = root / "build-numbers.json"
    with lock_path.open("a+", encoding="utf-8") as lock:
        lock_path.chmod(0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        document = _read_build_numbers(store_path)
        key = f"{bundle_id}/{version}"
        local_max = document["allocations"].get(key, 0)
        if type(local_max) is not int or local_max < 0:
            raise ConfigurationError("Showroom's TestFlight build-number store is invalid")
        selected = max(local_max, remote_max) + 1
        document["allocations"][key] = selected
        temporary = store_path.with_name(f".{store_path.name}.{os.getpid()}.tmp")
        temporary.write_text(f"{json.dumps(document, indent=2, sort_keys=True)}\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(store_path)
        return selected


def _read_build_numbers(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "allocations": {}}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Showroom's TestFlight build-number store is invalid: {exc}") from exc
    if (
        not isinstance(document, dict)
        or document.get("version") != 1
        or not isinstance(document.get("allocations"), dict)
    ):
        raise ConfigurationError("Showroom's TestFlight build-number store is invalid")
    return document
