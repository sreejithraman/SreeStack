from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "showroom" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from showroom_lib.adapters.ios_image import screenshots_show_app  # noqa: E402
from showroom_lib.adapters.ios_types import CommandResult  # noqa: E402


def bmp(colors: list[tuple[int, int, int]], width: int, height: int) -> bytes:
    pixels = b"".join(bytes((blue, green, red, 255)) for red, green, blue in colors)
    offset = 54
    header = bytearray(offset)
    header[:2] = b"BM"
    struct.pack_into("<I", header, 2, offset + len(pixels))
    struct.pack_into("<I", header, 10, offset)
    struct.pack_into("<I", header, 14, 40)
    struct.pack_into("<i", header, 18, width)
    struct.pack_into("<i", header, 22, -height)
    struct.pack_into("<H", header, 26, 1)
    struct.pack_into("<H", header, 28, 32)
    return bytes(header) + pixels


class ConvertingRunner:
    def __init__(self, outputs: dict[str, bytes]) -> None:
        self.outputs = outputs
        self.timeouts: list[float | None] = []

    def run(self, argv, *, cwd=None, timeout_seconds=None):
        self.timeouts.append(timeout_seconds)
        Path(argv[-1]).write_bytes(self.outputs[Path(argv[4]).name])
        return CommandResult(0)


class IOSImageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.baseline = self.root / "baseline.png"
        self.screenshot = self.root / "screenshot.png"
        self.baseline.write_bytes(b"png")
        self.screenshot.write_bytes(b"png")

    def assess(self, before: bytes, after: bytes) -> tuple[bool, ConvertingRunner]:
        runner = ConvertingRunner(
            {self.baseline.name: before, self.screenshot.name: after}
        )
        result = screenshots_show_app(
            runner,
            self.baseline,
            self.screenshot,
            deadline=11.0,
            monotonic=lambda: 1.0,
        )
        return result, runner

    def test_accepts_distinct_nonblank_app_image(self) -> None:
        before = bmp([(255, 255, 255)] * 100, 10, 10)
        colors = [(index, index * 2 % 256, index * 3 % 256) for index in range(100)]
        result, runner = self.assess(before, bmp(colors, 10, 10))
        self.assertTrue(result)
        self.assertEqual([10.0, 10.0], runner.timeouts)

    def test_rejects_blank_or_unchanged_image(self) -> None:
        blank = bmp([(255, 255, 255)] * 100, 10, 10)
        self.assertFalse(self.assess(blank, blank)[0])
        rich = bmp(
            [(index, index * 2 % 256, index * 3 % 256) for index in range(100)],
            10,
            10,
        )
        self.assertFalse(self.assess(rich, rich)[0])

    def test_rejects_system_chrome_around_blank_app_content(self) -> None:
        before = bmp([(0, 0, 0)] * 400, 20, 20)
        colors = []
        for y in range(20):
            for x in range(20):
                if x < 2 or x >= 18 or y < 2 or y >= 18:
                    colors.append((x * 10, y * 10, (x + y) * 5))
                else:
                    colors.append((255, 255, 255))
        self.assertFalse(self.assess(before, bmp(colors, 20, 20))[0])


if __name__ == "__main__":
    unittest.main()
