"""Round-trip gates for the DNG writer at every supported integer depth."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import taichi
from taichi_vision.taichi_algorithm.compression import save_dng_aot


@pytest.mark.parametrize("bits", [8, 10, 12, 14, 16, 24, 32])
@pytest.mark.parametrize("compression", ["none", "packbits", "deflate"])
def test_writer_roundtrip_every_depth(bits: int, compression: str, tmp_path: Path) -> None:
    rng = np.random.default_rng(1000 + bits)
    maximum = (1 << bits) - 1
    dtype = np.uint32 if bits > 16 else np.uint16
    mosaic = rng.integers(0, maximum, size=(24, 32), dtype=dtype)
    path = tmp_path / f"depth_{bits}_{compression}.dng"
    save_dng_aot(
        mosaic,
        path,
        metadata={
            "cfa_pattern": (0, 1, 1, 2),
            "black_level": 0,
            "white_level": maximum,
            "orientation": 1,
        },
        compression=compression,
        bits_per_sample=bits,
    )

    result = taichi.read_dng(path)
    decoded = np.asarray(result["data"])

    assert decoded.dtype == dtype
    assert np.array_equal(decoded, mosaic)
    assert result["bits_per_sample"] == bits
    assert result["dng_version"] == [1, 7, 0, 0]
    assert result["black_source"] == "tag"
    assert result["white_source"] == "tag"


def test_lossless_jpeg_predictors_roundtrip(tmp_path: Path) -> None:
    rng = np.random.default_rng(1024)
    for bits in (8, 12, 16):
        maximum = (1 << bits) - 1
        dtype = np.uint8 if bits == 8 else np.uint16
        mosaic = rng.integers(0, maximum + 1, size=(17, 23), dtype=dtype)
        for predictor in range(1, 8):
            for huffman in ("standard", "optimized"):
                path = tmp_path / f"ljpeg_{bits}_{predictor}_{huffman}.dng"
                save_dng_aot(
                    mosaic,
                    path,
                    metadata={
                        "cfa_pattern": (0, 1, 1, 2),
                        "black_level": 0,
                        "white_level": maximum,
                        "orientation": 1,
                        "jpeg_predictor": predictor,
                        "jpeg_huffman": huffman,
                    },
                    compression="lossless_jpeg",
                    bits_per_sample=bits,
                )
                result = taichi.read_dng(path)
                assert np.array_equal(np.asarray(result["data"]), mosaic)


def test_default_writer_uses_lossless_jpeg(tmp_path: Path) -> None:
    rng = np.random.default_rng(2048)
    mosaic = rng.integers(0, 4096, size=(16, 24), dtype=np.uint16)
    path = tmp_path / "default.dng"
    save_dng_aot(
        mosaic,
        path,
        metadata={
            "cfa_pattern": (0, 1, 1, 2),
            "black_level": 0,
            "white_level": 4095,
            "orientation": 1,
        },
        bits_per_sample=16,
    )
    result = taichi.read_dng(path)
    assert result["compression"] == 7
    assert np.array_equal(np.asarray(result["data"]), mosaic)


def test_horizontal_predictor_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AOT_ALLOW_HOST_FALLBACK", "1")
    rng = np.random.default_rng(77)
    mosaic = rng.integers(0, 4096, size=(16, 24), dtype=np.uint16)
    path = tmp_path / "predictor_horizontal.dng"
    save_dng_aot(
        mosaic,
        path,
        metadata={
            "cfa_pattern": (0, 1, 1, 2),
            "black_level": 0,
            "white_level": 4095,
            "orientation": 1,
        },
        compression="none",
        predictor="horizontal",
        bits_per_sample=16,
    )

    result = taichi.read_dng(path)

    assert result["predictor"] == 2
    assert np.array_equal(np.asarray(result["data"]), mosaic)
