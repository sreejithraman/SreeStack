"""Small image checks used to reject blank iOS review evidence."""

from __future__ import annotations

from pathlib import Path
import struct
from typing import Callable

from .ios_types import CommandFailure, CommandRunner, IOSAdapterError


def screenshots_show_app(
    runner: CommandRunner,
    baseline: Path,
    screenshot: Path,
    *,
    deadline: float,
    monotonic: Callable[[], float],
) -> bool:
    """Return true when the new image differs from launch state and is not blank."""
    baseline_bmp = baseline.with_suffix(".bmp")
    screenshot_bmp = screenshot.with_suffix(".bmp")
    try:
        for source, output in (
            (baseline, baseline_bmp),
            (screenshot, screenshot_bmp),
        ):
            remaining = deadline - monotonic()
            if remaining <= 0:
                return False
            argv = [
                "sips",
                "-s",
                "format",
                "bmp",
                str(source),
                "--out",
                str(output),
            ]
            result = runner.run(argv, timeout_seconds=remaining)
            if result.returncode != 0:
                raise CommandFailure(argv, result)
        before = _sample_bmp(baseline_bmp)
        after = _sample_bmp(screenshot_bmp)
    finally:
        baseline_bmp.unlink(missing_ok=True)
        screenshot_bmp.unlink(missing_ok=True)
    if len(after) != len(before) or len(set(after)) < 8:
        return False
    changed = sum(left != right for left, right in zip(before, after, strict=True))
    return changed / len(after) >= 0.005


def _sample_bmp(path: Path) -> tuple[bytes, ...]:
    payload = path.read_bytes()
    if len(payload) < 54 or payload[:2] != b"BM":
        raise IOSAdapterError(f"sips did not create a valid bitmap: {path}")
    offset = struct.unpack_from("<I", payload, 10)[0]
    width = struct.unpack_from("<i", payload, 18)[0]
    height = abs(struct.unpack_from("<i", payload, 22)[0])
    bits_per_pixel = struct.unpack_from("<H", payload, 28)[0]
    if width <= 0 or height <= 0 or bits_per_pixel not in {24, 32}:
        raise IOSAdapterError(f"unsupported screenshot bitmap format: {path}")
    bytes_per_pixel = bits_per_pixel // 8
    row_size = ((width * bits_per_pixel + 31) // 32) * 4
    if offset + row_size * height > len(payload):
        raise IOSAdapterError(f"truncated screenshot bitmap: {path}")
    x_start = width // 10
    x_end = width - x_start
    y_start = height // 10
    y_end = height - y_start
    x_step = max(1, (x_end - x_start) // 64)
    y_step = max(1, (y_end - y_start) // 64)
    return tuple(
        payload[
            offset + y * row_size + x * bytes_per_pixel :
            offset + y * row_size + x * bytes_per_pixel + 3
        ]
        for y in range(y_start, y_end, y_step)
        for x in range(x_start, x_end, x_step)
    )
