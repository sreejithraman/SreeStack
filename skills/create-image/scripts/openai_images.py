#!/usr/bin/env python3
"""Generate or edit images through the OpenAI Images API.

Prints one JSON object on stdout, with file paths rather than image data.

Exit codes:
  0  Images saved, or a dry run passed.
  1  Internal error. See api.may_have_charged before rerunning.
  2  Bad arguments, input file, or output path. Nothing was sent.
  3  The API could not deliver. fallback_allowed is true.
  4  Refused, invalid request, or an image could not be saved. No fallback.
  5  The API could not deliver and --require-model forbids a fallback.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import asdict, dataclass
import http.client
import json
import os
from pathlib import Path
import queue
import re
import socket
import ssl
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
import urllib.request
import uuid

MODEL_ALIASES = {"flare": "gpt-image-2.6-flare", "sunburst": "gpt-image-2.6-sunburst"}
DEFAULT_MODEL = MODEL_ALIASES["flare"]

API_BASE = "https://api.openai.com/v1"
BASE_OVERRIDE_ENV = "OPENAI_IMAGES_BASE_URL"  # For local mock APIs.
KEY_ENV = "OPENAI_API_KEY"
DEFAULT_TIMEOUT_SECONDS = 300
MAX_RETRY_WAIT_SECONDS = 30
MIN_RETRY_BUDGET_SECONDS = 120  # The image guide says complex prompts can take 2 minutes.
MAX_INPUT_BYTES = 50 * 1024 * 1024
MAX_INPUT_IMAGES = 16
MAX_PROMPT_CHARS = 32000
MAX_API_MESSAGE_CHARS = 500
USER_AGENT = "create-image-skill/1"

FORMAT_BY_SUFFIX = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}
REFUSAL_CODES = {"moderation_blocked", "content_policy_violation"}
QUOTA_CODES = {
    "billing_hard_limit_reached",
    "billing_not_active",
    "credit_balance_exhausted",
    "insufficient_quota",
    "organization_spend_limit_exceeded",
    "organization_usage_limit_exceeded",
    "project_spend_limit_exceeded",
}
# These arise while opening the connection. urllib wraps write errors the same way, so other
# errors, such as a route lost during an upload, cannot show that nothing reached the API.
UNSENT_ERRORS = (socket.gaierror, ConnectionRefusedError, ssl.SSLCertVerificationError)

EXIT_OK = 0
EXIT_INTERNAL = 1
EXIT_LOCAL = 2
EXIT_FALLBACK = 3
EXIT_STOP = 4
EXIT_MODEL_REQUIRED = 5

REASON_MESSAGES = {
    "incomplete_error": "The API returned an error, but its explanation did not arrive before the deadline.",
    "access_denied": "The API rejected the key or this organization's access.",
    "api_unavailable": "The API did not accept the request.",
    "invalid_request": "The API rejected the request as invalid.",
    "missing_credentials": f"{KEY_ENV} is missing or malformed, so nothing was sent.",
    "model_unavailable": "This key cannot use the requested model.",
    "network_error": "The API could not be reached, so nothing was sent.",
    "outcome_unknown": "The API returned no usable image, so its outcome is unknown.",
    "overloaded": "The model is temporarily overloaded.",
    "output_write_failed": "The API returned an image that could not be saved.",
    "quota_exhausted": "The API has no credits or spend limit left for this request.",
    "rate_limited": "The API is rate limiting this key.",
    "refused": "The API refused this request under its content policy.",
    "user_error": "The API could not process this prompt or input.",
}
FALLBACK_REASONS = {
    "access_denied",
    "api_unavailable",
    "missing_credentials",
    "model_unavailable",
    "network_error",
    "outcome_unknown",
    "overloaded",
    "quota_exhausted",
    "rate_limited",
}
RETRYABLE_REASONS = {"overloaded", "rate_limited"}
SECRET_PATTERN = re.compile(r"(\bsk-[\w*.-]+|\bBearer\s+\S+)")


@dataclass
class ApiReport:
    outcome: str = "not_sent"  # not_sent | rejected | unknown | succeeded
    may_have_charged: bool = False
    http_status: int | None = None
    error_code: str | None = None
    error_type: str | None = None
    moderation_stage: str | None = None
    request_id: str | None = None
    message: str | None = None


class Failure(Exception):
    def __init__(self, reason: str, detail: str = "", report: ApiReport | None = None, retry_after: float | None = None):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail
        self.report = report
        self.retry_after = retry_after


@dataclass
class InputImage:
    path: Path
    data: bytes
    format: str


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({"status": "error", "reason": "usage", "message": message}, indent=2))
        self.exit(EXIT_LOCAL)


def sniff_format(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def has_alpha(png: bytes) -> bool:
    color_type = png[25] if len(png) > 25 else None
    return color_type in (4, 6) or b"tRNS" in png.split(b"IDAT", 1)[0]


def scrub(text: str, key: str | None) -> str:
    if key:
        text = text.replace(key, "[redacted]")
    return SECRET_PATTERN.sub("[redacted]", text)


def resolve_model(requested: str | None) -> str:
    if requested is None:
        return DEFAULT_MODEL
    model = MODEL_ALIASES.get(requested.strip().lower(), requested.strip())
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", model):
        raise Failure("invalid_input", f"Model {requested!r} is neither an alias nor a model ID.")
    return model


def api_base() -> str:
    base = os.environ.get(BASE_OVERRIDE_ENV, API_BASE).rstrip("/")
    if base == API_BASE or urlsplit(base).hostname in ("127.0.0.1", "localhost", "::1"):
        return base
    raise Failure("invalid_input", f"{BASE_OVERRIDE_ENV} must be a loopback address.")


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt is not None:
        prompt = args.prompt
    else:
        try:
            prompt = sys.stdin.read() if args.prompt_file == "-" else Path(args.prompt_file).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise Failure("invalid_input", f"Could not read the prompt file: {type(error).__name__}.")
    if not prompt.strip():
        raise Failure("invalid_input", "The prompt is empty.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise Failure("invalid_input", f"The prompt exceeds {MAX_PROMPT_CHARS} characters.")
    return prompt


def read_input_image(name: str) -> InputImage:
    path = Path(name).expanduser()
    if not path.is_file():
        raise Failure("invalid_input", f"Input image not found: {path}")
    size = path.stat().st_size
    if size == 0 or size >= MAX_INPUT_BYTES:
        raise Failure("invalid_input", f"Input image must be under 50 MB and not empty: {path}")
    try:
        data = path.read_bytes()
    except OSError as error:
        raise Failure("invalid_input", f"Could not read {path}: {type(error).__name__}.")
    image_format = sniff_format(data)
    if image_format is None:
        raise Failure("invalid_input", f"Input image must be PNG, JPEG, or WebP: {path}")
    return InputImage(path, data, image_format)


def read_mask(name: str) -> InputImage:
    mask = read_input_image(name)
    if mask.format != "png" or not has_alpha(mask.data):
        raise Failure("invalid_input", f"The mask must be a PNG with an alpha channel: {mask.path}")
    return mask


def output_paths(out: Path, count: int) -> list[Path]:
    if count == 1:
        return [out]
    return [out.with_name(f"{out.stem}-{index}{out.suffix}") for index in range(1, count + 1)]


def check_output_paths(paths: list[Path]) -> None:
    for path in paths:
        if os.path.lexists(path):
            raise Failure("output_exists", f"Output already exists, so nothing was sent: {path}")
    directory = paths[0].parent
    while not directory.exists():
        directory = directory.parent
    if not directory.is_dir() or not os.access(directory, os.W_OK):
        raise Failure("invalid_input", f"Output folder is not writable: {directory}")


def usable_key() -> str | None:
    key = os.environ.get(KEY_ENV, "").strip()
    return key if re.fullmatch(r"[\x21-\x7e]+", key) else None


def request_fields(args: argparse.Namespace, model: str, prompt: str, output_format: str) -> dict:
    if args.n < 1 or args.n > 10:
        raise Failure("invalid_input", "--n must be 1 to 10.")
    if not 0 < args.timeout < float("inf"):
        raise Failure("invalid_input", "--timeout must be a finite number above 0.")
    if args.output_compression is not None:
        if output_format == "png":
            raise Failure("invalid_input", "--output-compression needs a .jpg or .webp output.")
        if not 0 <= args.output_compression <= 100:
            raise Failure("invalid_input", "--output-compression must be 0 to 100.")
    if args.background == "transparent" and output_format == "jpeg":
        raise Failure("invalid_input", "A transparent background needs a .png or .webp output.")
    fields = {"model": model, "prompt": prompt, "n": args.n, "output_format": output_format}
    for name in ("size", "quality", "background", "complexity", "output_compression"):
        value = getattr(args, name)
        if value is not None:
            fields[name] = value
    return fields


def multipart_body(fields: dict, images: list[InputImage], mask: InputImage | None) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())

    def add_file(field: str, filename: str, image: InputImage) -> None:
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{filename}.{image.format}"\r\n'
            f"Content-Type: image/{image.format}\r\n\r\n".encode()
        )
        parts.extend((image.data, b"\r\n"))

    for index, image in enumerate(images, start=1):
        add_file("image[]", f"image-{index}", image)
    if mask is not None:
        add_file("mask", "mask", mask)
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def classify_http(status: int, code: str | None, error_type: str | None, moderation_stage: str | None) -> str:
    """Only listed availability failures permit a fallback, so unknown client errors stop."""
    if code in REFUSAL_CODES or moderation_stage:
        return "refused"
    if error_type == "image_generation_user_error":
        return "user_error"
    if code in QUOTA_CODES or error_type == "insufficient_quota":
        return "quota_exhausted"
    if code == "model_not_found":
        return "model_unavailable"
    if status in (401, 403):
        return "access_denied"
    if status == 429:
        return "rate_limited"
    if status == 503 and (code == "server_is_overloaded" or error_type == "service_unavailable_error"):
        return "overloaded"
    if 300 <= status < 400:
        return "api_unavailable"
    if status >= 500:
        return "outcome_unknown"
    return "invalid_request"


def retry_wait(headers) -> float | None:
    try:
        wait = max(0.0, float(headers.get("Retry-After", 1)))
    except ValueError:
        wait = 1.0
    return wait if wait <= MAX_RETRY_WAIT_SECONDS else None


def http_failure(error: HTTPError, key: str) -> Failure:
    try:
        raw = error.read()
    except (OSError, http.client.HTTPException):
        raw = b""
    try:
        body = json.loads(raw)
    except ValueError:
        body = None
    details = body.get("error") if isinstance(body, dict) else None
    details = details if isinstance(details, dict) else {}
    moderation = details.get("moderation_details")
    stage = None
    if moderation is not None:
        stage = (moderation.get("moderation_stage") if isinstance(moderation, dict) else None) or "unknown"
    code = details.get("code") if isinstance(details.get("code"), str) else None
    error_type = details.get("type") if isinstance(details.get("type"), str) else None
    reason = classify_http(error.code, code, error_type, stage)
    message = details.get("message")
    report = ApiReport(
        outcome="unknown" if reason == "outcome_unknown" else "rejected",
        may_have_charged=reason == "outcome_unknown" or (reason in ("refused", "user_error") and stage != "input"),
        http_status=error.code,
        error_code=code,
        error_type=error_type,
        moderation_stage=stage,
        request_id=error.headers.get("x-request-id"),
        message=scrub(message, key)[:MAX_API_MESSAGE_CHARS] if isinstance(message, str) else None,
    )
    retry_after = retry_wait(error.headers) if reason in RETRYABLE_REASONS else None
    return Failure(reason, report=report, retry_after=retry_after)


def interrupted(cause: object) -> Failure:
    detail = f"The connection ended before a response arrived ({type(cause).__name__})."
    return Failure("outcome_unknown", detail=detail, report=ApiReport(outcome="unknown", may_have_charged=True))


def send_failure(cause: object) -> Failure:
    """Classify an error raised while connecting or writing the request."""
    if isinstance(cause, UNSENT_ERRORS) or str(cause).startswith("Tunnel connection failed"):
        return Failure("network_error", detail=type(cause).__name__, report=ApiReport())
    return interrupted(cause)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """A followed redirect would carry the Authorization header to another target."""

    def redirect_request(self, *args, **kwargs):
        return None


def post_once(
    url: str, body: bytes, content_type: str, key: str, timeout: float,
    progress: ApiReport | None = None,
) -> tuple[bytes, str | None]:
    if progress is not None:
        progress.http_status = None
        progress.request_id = None
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": content_type, "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            return response.read(), response.headers.get("x-request-id")
    except HTTPError as error:
        if progress is not None:
            progress.http_status = error.code
            progress.request_id = error.headers.get("x-request-id")
        raise http_failure(error, key)
    except URLError as error:
        raise send_failure(error.reason)
    except (OSError, http.client.HTTPException) as error:
        raise interrupted(error)


def post_with_retry(
    url: str, body: bytes, content_type: str, key: str, timeout: float,
    progress: ApiReport | None = None,
) -> tuple[bytes, str | None]:
    """Retry once when the API explicitly turned the request away for load.

    Other failures never repeat, because a second POST can bill a second image. A retry needs
    time to finish, or it would turn a free rejection into a possible charge.
    """
    started = time.monotonic()
    try:
        return post_once(url, body, content_type, key, timeout, progress)
    except Failure as failure:
        if failure.retry_after is None:
            raise
        remaining = timeout - (time.monotonic() - started) - failure.retry_after
        if remaining < MIN_RETRY_BUDGET_SECONDS:
            raise
        time.sleep(failure.retry_after)
    return post_once(url, body, content_type, key, remaining, progress)


def post_within_deadline(url: str, body: bytes, content_type: str, key: str, timeout: float) -> tuple[bytes, str | None]:
    """Bound the whole exchange, because urllib's timeout limits only each socket wait."""
    results: queue.SimpleQueue = queue.SimpleQueue()
    progress = ApiReport(outcome="unknown", may_have_charged=True)

    def exchange() -> None:
        try:
            results.put(post_with_retry(url, body, content_type, key, timeout, progress))
        except Exception as error:
            results.put(error)

    threading.Thread(target=exchange, daemon=True).start()
    try:
        result = results.get(timeout=timeout)
    except queue.Empty:
        if progress.http_status is not None:
            raise Failure("incomplete_error", report=progress)
        raise interrupted(TimeoutError())
    if isinstance(result, Exception):
        raise result
    return result


def decode_response(raw: bytes, output_format: str) -> tuple[list[dict], dict | None]:
    decoded = []
    try:
        payload = json.loads(raw)
        for item in payload["data"]:
            data = base64.b64decode(item["b64_json"], validate=True)
            if sniff_format(data) != output_format:
                raise ValueError
            decoded.append({"data": data, "revised_prompt": item.get("revised_prompt")})
        if decoded:
            usage = payload.get("usage")
            return decoded, usage if isinstance(usage, dict) else None
    except (KeyError, TypeError, ValueError):
        pass
    raise Failure("outcome_unknown")


def save_new_file(path: Path, data: bytes) -> Path:
    """Write without replacing anything, even if a file appeared during the request."""
    candidate = path
    suffix = 2
    while True:
        try:
            with open(candidate, "xb") as file:
                try:
                    file.write(data)
                except OSError:
                    candidate.unlink(missing_ok=True)
                    raise
            return candidate
        except FileExistsError:
            candidate = path.with_name(f"{path.stem}-alt-{suffix}{path.suffix}")
            suffix += 1


def save_images(images: list[dict], paths: list[Path], output_format: str, outputs: list[dict]) -> None:
    """Append as each file lands, so a later failure still reports the earlier images."""
    for image, requested in zip(images, paths):
        path = save_new_file(requested, image["data"])
        entry = {"path": str(path), "format": output_format, "bytes": len(image["data"])}
        if path != requested:
            entry["requested_path"] = str(requested)
        if image["revised_prompt"]:
            entry["revised_prompt"] = image["revised_prompt"]
        outputs.append(entry)


def failure_result(failure: Failure, result: dict, report: ApiReport, key: str | None) -> tuple[dict, int]:
    fallback_eligible = failure.reason in FALLBACK_REASONS
    if fallback_eligible:
        code = EXIT_MODEL_REQUIRED if result["model_required"] else EXIT_FALLBACK
    elif failure.reason in ("invalid_input", "output_exists"):
        code = EXIT_LOCAL
    else:
        code = EXIT_STOP
    parts = (REASON_MESSAGES.get(failure.reason), failure.detail, report.message)
    message = " ".join(part for part in parts if part)
    if report.may_have_charged:
        message += " The request may be billed."
    result.update(
        status="error",
        reason=failure.reason,
        message=scrub(message, key),
        api=asdict(report),
        fallback_allowed=code == EXIT_FALLBACK,
    )
    return result, code


def run(args: argparse.Namespace) -> tuple[dict, int]:
    report = ApiReport()
    key = None
    result: dict = {
        "status": "error",
        "reason": None,
        "message": "",
        "operation": args.operation,
        "model": None,
        "model_required": args.require_model,
        "endpoint": None,
        "outputs": [],
        "usage": None,
        "api": asdict(report),
        "fallback_allowed": False,
    }
    try:
        model = result["model"] = resolve_model(args.model)
        url = f"{api_base()}/images/{'generations' if args.operation == 'generate' else 'edits'}"
        result["endpoint"] = url
        prompt = read_prompt(args)
        out = Path(os.path.abspath(Path(args.out).expanduser()))
        output_format = FORMAT_BY_SUFFIX.get(out.suffix.lower())
        if output_format is None:
            raise Failure("invalid_input", "--out must end in .png, .jpg, .jpeg, or .webp.")
        fields = request_fields(args, model, prompt, output_format)
        images: list[InputImage] = []
        mask = None
        if args.operation == "edit":
            if len(args.image) > MAX_INPUT_IMAGES:
                raise Failure("invalid_input", f"An edit accepts at most {MAX_INPUT_IMAGES} images.")
            images = [read_input_image(name) for name in args.image]
            mask = read_mask(args.mask) if args.mask else None
        paths = output_paths(out, args.n)
        check_output_paths(paths)

        key = usable_key()
        if args.dry_run:
            summary = {name: value for name, value in fields.items() if name != "prompt"}
            summary["prompt_chars"] = len(prompt)
            result.update(
                status="dry_run",
                message="Nothing was sent or written.",
                credential={"env": KEY_ENV, "usable": key is not None},
                request=summary,
                inputs=[{"path": str(image.path), "format": image.format, "bytes": len(image.data)} for image in images],
                mask=str(mask.path) if mask else None,
                planned_outputs=[str(path) for path in paths],
            )
            return result, EXIT_OK

        if key is None:
            raise Failure("missing_credentials")
        out.parent.mkdir(parents=True, exist_ok=True)
        if args.operation == "edit":
            body, content_type = multipart_body(fields, images, mask)
        else:
            body, content_type = json.dumps(fields).encode(), "application/json"

        report = ApiReport(outcome="unknown", may_have_charged=True)
        raw, request_id = post_within_deadline(url, body, content_type, key, args.timeout)
        report.http_status, report.request_id = 200, request_id
        images_out, usage = decode_response(raw, output_format)
        report.outcome = "succeeded"
        try:
            save_images(images_out, paths, output_format, result["outputs"])
        except OSError as error:
            raise Failure("output_write_failed", type(error).__name__)
    except Failure as failure:
        return failure_result(failure, result, failure.report or report, key)
    except Exception as error:  # A failure here must still produce JSON and hide secrets.
        result.update(
            status="error",
            reason="internal_error",
            message=f"Unexpected {type(error).__name__}.",
            api=asdict(report),
        )
        return result, EXIT_INTERNAL

    result.update(
        status="ok",
        message=f"Saved {len(result['outputs'])} of {args.n} requested image(s).",
        usage=usage,
        api=asdict(report),
    )
    return result, EXIT_OK


def add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    prompt = parser.add_mutually_exclusive_group(required=True)
    prompt.add_argument("--prompt", help="Image prompt.")
    prompt.add_argument("--prompt-file", help="Read the prompt from this UTF-8 file, or stdin with -.")
    parser.add_argument("--out", required=True, help="New .png, .jpg, .jpeg, or .webp path. Sets the output format.")
    parser.add_argument(
        "--model",
        help=f"{' or '.join(MODEL_ALIASES)}, or an exact model ID. Default: {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--require-model", action="store_true",
        help="Forbid a fallback to any other model. Failures exit 5 instead of 3.",
    )
    parser.add_argument("--n", type=int, default=1, help="Images to make, 1-10. Outputs get -1, -2 suffixes.")
    parser.add_argument("--size", help="Such as 1024x1024, 1536x1024, or auto.")
    parser.add_argument("--quality", help="Such as low, medium, high, or auto.")
    parser.add_argument("--complexity", help="low, medium, or high.")
    parser.add_argument("--background", choices=("auto", "opaque", "transparent"))
    parser.add_argument("--output-compression", type=int, help="0-100, for .jpg and .webp outputs.")
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Seconds the whole API exchange may take. Default: {DEFAULT_TIMEOUT_SECONDS}.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and print the plan. Needs no key.")


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="operation", required=True)
    generate = commands.add_parser("generate", help="Create images from a prompt.")
    add_shared_arguments(generate)
    edit = commands.add_parser("edit", help="Change local images, or use them as references.")
    edit.add_argument("--image", action="append", required=True, help="Local image. Repeat for references, up to 16.")
    edit.add_argument("--mask", help="PNG with alpha. Transparent areas mark what to change in the first image.")
    add_shared_arguments(edit)
    return parser


def main() -> int:
    result, code = run(build_parser().parse_args())
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
