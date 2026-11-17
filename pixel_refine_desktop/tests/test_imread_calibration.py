"""Bit-exact and calibration gates for the native DNG/TIFF reader."""
from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import pytest

import taichi


def _write_tiff(
    path: Path,
    samples: np.ndarray,
    *,
    active_area: tuple[int, int, int, int] | None = None,
) -> None:
    height, width = samples.shape
    payload = np.ascontiguousarray(samples, dtype="<u2").tobytes()
    entries: list[tuple[int, int, int, bytes]] = [
        (256, 4, 1, struct.pack("<I", width)),
        (257, 4, 1, struct.pack("<I", height)),
        (258, 3, 1, struct.pack("<H", 16) + b"\x00\x00"),
        (259, 3, 1, struct.pack("<H", 1) + b"\x00\x00"),
        (278, 4, 1, struct.pack("<I", height)),
        (279, 4, 1, struct.pack("<I", len(payload))),
        (33421, 3, 2, struct.pack("<HH", 2, 2)),
        (33422, 1, 4, bytes([0, 1, 1, 2])),
    ]
    if active_area is not None:
        entries.append((50829, 4, 4, b"\x00" * 4))
    entries.append((273, 4, 1, b"\x00" * 4))
    entries.sort(key=lambda item: item[0])

    ifd_offset = 8
    entry_count = len(entries)
    data_offset = ifd_offset + 2 + entry_count * 12 + 4
    extra_offset = data_offset + len(payload)
    extra = b""
    if active_area is not None:
        extra = struct.pack("<IIII", *active_area)

    header = b"II" + struct.pack("<H", 42) + struct.pack("<I", ifd_offset)
    ifd = struct.pack("<H", entry_count)
    for tag, type_id, count, value in entries:
        if tag == 273:
            value = struct.pack("<I", data_offset)
        elif tag == 50829:
            value = struct.pack("<I", extra_offset)
        ifd += struct.pack("<HHI", tag, type_id, count) + value.ljust(4, b"\x00")
    ifd += struct.pack("<I", 0)
    path.write_bytes(header + ifd + payload + extra)


def test_raw_samples_are_bit_exact_and_missing_white_is_dynamic(tmp_path: Path) -> None:
    samples = np.full((16, 16), 100, dtype=np.uint16)
    samples[4:8, 4:8] = 4000
    path = tmp_path / "no_levels.tif"
    _write_tiff(path, samples)

    result = taichi.read_dng(path)
    decoded = np.asarray(result["data"])

    assert np.array_equal(decoded, samples)
    assert result["white_source"] == "percentile"
    assert result["calibration_source"] == "dynamic"
    assert np.allclose(result["white_levels"], 4000.0)


def test_masked_border_supplies_black_level(tmp_path: Path) -> None:
    samples = np.full((16, 16), 200, dtype=np.uint16)
    samples[0, :] = 50
    samples[:, 0] = 50
    samples[-1, :] = 50
    samples[:, -1] = 50
    path = tmp_path / "active_area.tif"
    _write_tiff(path, samples, active_area=(1, 1, 15, 15))

    result = taichi.read_dng(path)

    assert np.array_equal(np.asarray(result["data"]), samples)
    assert result["black_source"] == "masked-border"
    assert np.allclose(result["black_levels"], 50.0)
    assert result["calibration_source"] == "hybrid"


def test_capabilities_report_native_raw_and_standard_formats() -> None:
    caps = taichi.image_capabilities()

    assert caps["dng"]["supported"] is True
    assert caps["dng"]["cfa"] == "bayer"
    for name in ("jpeg", "png", "tiff"):
        assert caps[name]["supported"] is True
    for name in ("cr2", "cr3", "nef", "arw", "rw2", "orf", "pef", "srw", "3fr", "raw"):
        assert caps[name]["supported"] is True
    assert caps["mos"]["supported"] is False
    assert caps["raf"]["supported"] is False
    assert caps["x3f"]["supported"] is False
    assert "Leaf" in caps["mos"]["reason"]
    assert "6x6" in caps["raf"]["reason"]
    assert "Foveon" in caps["x3f"]["reason"]
