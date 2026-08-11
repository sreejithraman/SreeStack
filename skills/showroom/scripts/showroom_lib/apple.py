from __future__ import annotations

import contextlib
import ctypes
import fcntl
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from getpass import getpass
from pathlib import Path
from typing import Any, Iterator, Sequence

from .errors import ConfigurationError


PROFILE_VERSION = 1
API_KEY_SERVICE = "showroom.apple.app-store-connect"
PROFILE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TEAM_ID = re.compile(r"^[A-Z0-9]{10}$")


class KeychainSecrets:
    def __init__(self) -> None:
        self.security = ctypes.CDLL(
            "/System/Library/Frameworks/Security.framework/Security"
        )
        self.core = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        self.security.SecKeychainOpen.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecKeychainOpen.restype = ctypes.c_int32
        self.security.SecKeychainAddGenericPassword.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecKeychainAddGenericPassword.restype = ctypes.c_int32
        self.security.SecKeychainFindGenericPassword.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecKeychainFindGenericPassword.restype = ctypes.c_int32
        self.security.SecKeychainItemFreeContent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.security.SecKeychainItemFreeContent.restype = ctypes.c_int32
        self.core.CFRelease.argtypes = [ctypes.c_void_p]

    def _open(self, path: Path) -> ctypes.c_void_p:
        reference = ctypes.c_void_p()
        status = self.security.SecKeychainOpen(
            os.fsencode(path), ctypes.byref(reference)
        )
        if status != 0:
            raise ConfigurationError(f"macOS could not open the Showroom keychain ({status})")
        return reference

    @staticmethod
    def _bytes(value: str) -> tuple[bytes, ctypes.Array[ctypes.c_char]]:
        raw = value.encode("utf-8")
        return raw, ctypes.create_string_buffer(raw)

    def put(self, path: Path, account: str, value: bytes) -> None:
        keychain = self._open(path)
        item = ctypes.c_void_p()
        service_raw, service = self._bytes(API_KEY_SERVICE)
        account_raw, account_buffer = self._bytes(account)
        secret = ctypes.create_string_buffer(value)
        try:
            status = self.security.SecKeychainAddGenericPassword(
                keychain,
                len(service_raw),
                service,
                len(account_raw),
                account_buffer,
                len(value),
                secret,
                ctypes.byref(item),
            )
            if status != 0:
                raise ConfigurationError(
                    f"macOS could not store the App Store Connect key ({status})"
                )
        finally:
            if item.value:
                self.core.CFRelease(item)
            self.core.CFRelease(keychain)

    def get(self, path: Path, account: str) -> bytes:
        keychain = self._open(path)
        item = ctypes.c_void_p()
        length = ctypes.c_uint32()
        data = ctypes.c_void_p()
        service_raw, service = self._bytes(API_KEY_SERVICE)
        account_raw, account_buffer = self._bytes(account)
        try:
            status = self.security.SecKeychainFindGenericPassword(
                keychain,
                len(service_raw),
                service,
                len(account_raw),
                account_buffer,
                ctypes.byref(length),
                ctypes.byref(data),
                ctypes.byref(item),
            )
            if status != 0:
                raise ConfigurationError(
                    f"macOS could not read the App Store Connect key ({status})"
                )
            return ctypes.string_at(data, length.value)
        finally:
            if data.value:
                self.security.SecKeychainItemFreeContent(None, data)
            if item.value:
                self.core.CFRelease(item)
            self.core.CFRelease(keychain)

    def has(self, path: Path, account: str) -> bool:
        try:
            self.get(path, account)
        except ConfigurationError:
            return False
        return True


@dataclass(frozen=True)
class AppleProfile:
    name: str
    team_id: str
    key_id: str
    issuer_id: str
    keychain_path: Path
    unlock_seconds: int


def apple_root(state: Path) -> Path:
    return state / "credentials" / "apple"


def profiles_path(state: Path) -> Path:
    return apple_root(state) / "profiles.json"


def _run(
    argv: Sequence[str],
    *,
    input_text: str | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            list(argv),
            check=False,
            capture_output=capture,
            text=True,
            input=input_text,
        )
    except OSError as exc:
        raise ConfigurationError(f"Apple signing command failed: {exc}") from exc
    if check and completed.returncode != 0:
        detail = (completed.stderr or "").strip() or (completed.stdout or "").strip()
        detail = detail or f"exit {completed.returncode}"
        raise ConfigurationError(f"Apple signing command failed: {detail}")
    return completed


def _private_directory(path: Path) -> None:
    path.mkdir(parents=True, mode=0o700, exist_ok=True)
    path.chmod(0o700)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    _private_directory(path.parent)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(f"{json.dumps(value, indent=2, sort_keys=True)}\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def _load_document(state: Path, *, required: bool = True) -> dict[str, Any]:
    path = profiles_path(state)
    if not path.is_file():
        if required:
            raise ConfigurationError("No Showroom Apple profile. Run `showroom apple setup` once on this Mac.")
        return {"version": PROFILE_VERSION, "default_profile": None, "profiles": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Invalid Showroom Apple profile store: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("version") != PROFILE_VERSION
        or not isinstance(value.get("profiles"), dict)
    ):
        raise ConfigurationError("Unsupported Showroom Apple profile store")
    return value


def _profile_from_value(name: str, value: Any) -> AppleProfile:
    if not isinstance(value, dict):
        raise ConfigurationError(f"Invalid Showroom Apple profile: {name}")
    try:
        profile = AppleProfile(
            name=name,
            team_id=str(value["team_id"]),
            key_id=str(value["key_id"]),
            issuer_id=str(value["issuer_id"]),
            keychain_path=Path(str(value["keychain_path"])).expanduser().resolve(strict=False),
            unlock_seconds=int(value["unlock_seconds"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"Invalid Showroom Apple profile: {name}") from exc
    if profile.unlock_seconds <= 0:
        raise ConfigurationError(f"Invalid unlock period for Showroom Apple profile: {name}")
    return profile


def load_profile(state: Path, name: str | None = None) -> AppleProfile:
    document = _load_document(state)
    selected = name or os.environ.get("SHOWROOM_APPLE_PROFILE") or document.get("default_profile")
    if not isinstance(selected, str) or not selected:
        raise ConfigurationError("No default Showroom Apple profile")
    value = document["profiles"].get(selected)
    if value is None:
        raise ConfigurationError(f"Unknown Showroom Apple profile: {selected}")
    return _profile_from_value(selected, value)


def _profile_value(profile: AppleProfile) -> dict[str, Any]:
    value = asdict(profile)
    value["keychain_path"] = str(profile.keychain_path)
    value.pop("name")
    return value


def setup_profile(
    state: Path,
    *,
    name: str,
    team_id: str,
    key_id: str,
    issuer_id: str,
    api_key_path: Path,
    certificates: Sequence[Path],
    unlock_seconds: int,
    make_default: bool,
    password_reader=getpass,
    runner=_run,
    secrets: KeychainSecrets | None = None,
) -> dict[str, Any]:
    if os.uname().sysname != "Darwin":
        raise ConfigurationError("Showroom Apple profiles require macOS")
    if not PROFILE_NAME.fullmatch(name):
        raise ConfigurationError("Apple profile names may use letters, numbers, dot, dash, and underscore")
    if not TEAM_ID.fullmatch(team_id):
        raise ConfigurationError("The Apple team ID must contain 10 uppercase letters or numbers")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", key_id) or not issuer_id:
        raise ConfigurationError("The App Store Connect key ID and issuer ID are required")
    if unlock_seconds <= 0:
        raise ConfigurationError("Unlock time must be positive")
    api_key = api_key_path.expanduser().resolve(strict=True)
    certificate_paths = [path.expanduser().resolve(strict=True) for path in certificates]
    if not certificate_paths:
        raise ConfigurationError("Add at least one Apple signing certificate exported as .p12")
    document = _load_document(state, required=False)
    if name in document["profiles"]:
        raise ConfigurationError(f"Showroom Apple profile already exists: {name}")

    root = apple_root(state)
    _private_directory(root)
    keychain = root / f"{name}.keychain-db"
    if keychain.exists():
        raise ConfigurationError(f"Showroom Apple keychain already exists: {keychain}")
    password = password_reader("Choose a Showroom signing password: ")
    confirmation = password_reader("Repeat the Showroom signing password: ")
    if not password or password != confirmation:
        raise ConfigurationError("Showroom signing passwords did not match")

    created = False
    secret_store = secrets or KeychainSecrets()
    try:
        runner(("security", "create-keychain", "-p", password, str(keychain)))
        created = True
        runner(("security", "set-keychain-settings", "-lu", "-t", str(unlock_seconds), str(keychain)))
        for certificate in certificate_paths:
            runner(
                (
                    "security", "import", str(certificate), "-k", str(keychain), "-f", "pkcs12", "-x",
                    "-T", "/usr/bin/codesign", "-T", "/usr/bin/xcodebuild", "-T", "/usr/bin/security",
                ),
                capture=False,
            )
        runner(
            (
                "security", "set-key-partition-list", "-S", "apple-tool:,apple:,codesign:",
                "-s", "-k", password, str(keychain),
            )
        )
        secret_store.put(keychain, name, api_key.read_bytes())
        profile = AppleProfile(name, team_id, key_id, issuer_id, keychain, unlock_seconds)
        document["profiles"][name] = _profile_value(profile)
        if make_default or not document.get("default_profile"):
            document["default_profile"] = name
        _write_json(profiles_path(state), document)
    except Exception:
        if created:
            runner(("security", "delete-keychain", str(keychain)), check=False)
        raise
    finally:
        password = ""
        confirmation = ""

    return profile_status(state, name, runner=runner, secrets=secret_store)


def unlock_profile(
    state: Path,
    name: str | None = None,
    *,
    hours: float | None = None,
    password_reader=getpass,
    runner=_run,
    secrets: KeychainSecrets | None = None,
) -> dict[str, Any]:
    profile = load_profile(state, name)
    seconds = profile.unlock_seconds if hours is None else int(hours * 60 * 60)
    if seconds <= 0:
        raise ConfigurationError("Unlock time must be positive")
    password = password_reader(f"Unlock Showroom Apple profile {profile.name}: ")
    try:
        runner(("security", "unlock-keychain", "-p", password, str(profile.keychain_path)))
        runner(("security", "set-keychain-settings", "-lu", "-t", str(seconds), str(profile.keychain_path)))
    finally:
        password = ""
    return profile_status(state, profile.name, runner=runner, secrets=secrets)


def lock_profile(
    state: Path,
    name: str | None = None,
    *,
    runner=_run,
    secrets: KeychainSecrets | None = None,
) -> dict[str, Any]:
    profile = load_profile(state, name)
    runner(("security", "lock-keychain", str(profile.keychain_path)))
    return profile_status(state, profile.name, runner=runner, secrets=secrets)


def _identity_lines(profile: AppleProfile, *, runner=_run) -> list[str]:
    completed = runner(
        ("security", "find-identity", "-v", "-p", "codesigning", str(profile.keychain_path)),
        check=False,
    )
    return [line.strip() for line in completed.stdout.splitlines() if '"Apple ' in line]


def _signing_identity(profile: AppleProfile, surface: str, *, runner=_run) -> str:
    kind = "Apple Distribution" if surface == "testflight" else "Apple Development"
    for line in _identity_lines(profile, runner=runner):
        match = re.search(r'\)\s+([0-9A-Fa-f]{40})\s+"([^"]+)"', line)
        if match and match.group(2).startswith(kind):
            return match.group(1)
    raise ConfigurationError(f"Showroom Apple profile {profile.name!r} has no {kind} identity")


def _keychain_unlocked(profile: AppleProfile, *, runner=_run) -> bool:
    completed = runner(("security", "show-keychain-info", str(profile.keychain_path)), check=False)
    return completed.returncode == 0


def profile_status(
    state: Path,
    name: str | None = None,
    *,
    runner=_run,
    secrets: KeychainSecrets | None = None,
) -> dict[str, Any]:
    profile = load_profile(state, name)
    unlocked = profile.keychain_path.is_file() and _keychain_unlocked(profile, runner=runner)
    identities = _identity_lines(profile, runner=runner) if profile.keychain_path.is_file() else []
    api_key_configured = True
    if unlocked:
        api_key_configured = (secrets or KeychainSecrets()).has(
            profile.keychain_path, profile.name
        )
    return {
        "profile": profile.name,
        "default": _load_document(state).get("default_profile") == profile.name,
        "team_configured": bool(profile.team_id),
        "api_key_configured": api_key_configured,
        "keychain_exists": profile.keychain_path.is_file(),
        "keychain_unlocked": unlocked,
        "signing_identities": len(identities),
        "unlock_seconds": profile.unlock_seconds,
        "ready": unlocked and bool(identities) and api_key_configured,
    }


def list_profiles(
    state: Path,
    *,
    runner=_run,
    secrets: KeychainSecrets | None = None,
) -> dict[str, Any]:
    document = _load_document(state, required=False)
    return {
        "default_profile": document.get("default_profile"),
        "profiles": [
            profile_status(state, name, runner=runner, secrets=secrets)
            for name in sorted(document["profiles"])
        ],
    }


def _search_list(*, runner=_run) -> list[str]:
    completed = runner(("security", "list-keychains", "-d", "user"))
    return [line.strip().strip('"') for line in completed.stdout.splitlines() if line.strip()]


@contextlib.contextmanager
def delivery_environment(
    state: Path,
    *,
    surface: str,
    operation: str,
    required: bool,
    base: dict[str, str] | None = None,
    runner=_run,
    secrets: KeychainSecrets | None = None,
) -> Iterator[dict[str, str]]:
    needs_signing = surface == "testflight" or (surface == "device" and operation == "start")
    if not needs_signing or not required:
        yield dict(os.environ if base is None else base)
        return
    profile = load_profile(state)
    if not _keychain_unlocked(profile, runner=runner):
        raise ConfigurationError(
            f"Showroom Apple profile {profile.name!r} is locked. Run `showroom apple unlock` once for this session."
        )

    root = apple_root(state)
    _private_directory(root)
    lock_path = root / "delivery.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        lock_path.chmod(0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        previous = _search_list(runner=runner)
        selected = str(profile.keychain_path)
        search = [selected, *(value for value in previous if value != selected)]
        runner(("security", "list-keychains", "-d", "user", "-s", *search))
        temporary_root = root / "tmp"
        _private_directory(temporary_root)
        try:
            with tempfile.TemporaryDirectory(prefix="auth-", dir=temporary_root) as directory:
                path = Path(directory)
                path.chmod(0o700)
                probe = path / "signing-probe"
                shutil.copyfile("/usr/bin/true", probe)
                runner(
                    (
                        "codesign", "--force", "--sign",
                        _signing_identity(profile, surface, runner=runner),
                        "--keychain", str(profile.keychain_path), str(probe),
                    )
                )
                key_path = path / f"AuthKey_{profile.key_id}.p8"
                key = (secrets or KeychainSecrets()).get(
                    profile.keychain_path, profile.name
                )
                key_path.write_bytes(key)
                key_path.chmod(0o600)
                environment = dict(os.environ if base is None else base)
                environment.update(
                    {
                        "SHOWROOM_APPLE_PROFILE": profile.name,
                        "SHOWROOM_APPLE_TEAM_ID": profile.team_id,
                        "SHOWROOM_APPLE_KEY_ID": profile.key_id,
                        "SHOWROOM_APPLE_ISSUER_ID": profile.issuer_id,
                        "SHOWROOM_APPLE_KEY_PATH": str(key_path),
                        "SHOWROOM_APPLE_KEYCHAIN_PATH": str(profile.keychain_path),
                    }
                )
                yield environment
        finally:
            runner(("security", "list-keychains", "-d", "user", "-s", *previous), check=False)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
