"""Contract gates for floating-point DNG decoding (DNG 1.4+)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import taichi
from taichi_vision.taichi_algorithm.compression import RawMosaicFrame

FLOAT_DNG = Path(
    r"E:\Photo_Editor\360\Converts\lapangan\IMG_20250908_062022_EXP0-3.dng"
)


@pytest.mark.skipif(not FLOAT_DNG.is_file(), reason="local floating-point DNG fixture is unavailable")
def test_float24_dng_uses_float_contract() -> None:
    result = taichi.read_dng(FLOAT_DNG)
    samples = np.asarray(result["data"])

    assert samples.dtype == np.float32
    assert samples.shape == (3024, 4032)
    assert result["bits_per_sample"] == 24
    assert result["sample_format"] == 3
    assert result["predictor"] == 34894
    assert result["cfa_pattern_list"] == [1, 0, 2, 1]
    assert float(samples.max()) > 1.0
    assert float(result["white_level"]) >= 1.0


@pytest.mark.skipif(not FLOAT_DNG.is_file(), reason="local floating-point DNG fixture is unavailable")
def test_float24_dng_matches_libraw_scale() -> None:
    rawpy = pytest.importorskip("rawpy")

    result = taichi.read_dng(FLOAT_DNG)
    ours = np.asarray(result["data"], dtype=np.float64)
    with rawpy.imread(str(FLOAT_DNG)) as raw:
        reference = raw.raw_image_visible.astype(np.float64)
    height = min(ours.shape[0], reference.shape[0])
    width = min(ours.shape[1], reference.shape[1])
    ours = ours[:height, :width]
    reference = reference[:height, :width]

    correlation = float(np.corrcoef(ours.ravel(), reference.ravel())[0, 1])
    ratio = float(np.median(reference[np.abs(ours) > 1e-6] / ours[np.abs(ours) > 1e-6]))
    assert correlation > 0.99999
    assert 15.9 < ratio < 16.1


@pytest.mark.skipif(not FLOAT_DNG.is_file(), reason="local floating-point DNG fixture is unavailable")
def test_float24_frame_converts_to_processing_precision() -> None:
    result = taichi.read_dng(FLOAT_DNG)
    frame = RawMosaicFrame.from_raw_image(result)
    assert frame.samples.dtype == np.float32
    assert frame.metadata["source_bits_per_sample"] == 24

    uint16_frame = frame.as_processing_frame("uint16")
    assert uint16_frame.samples.dtype == np.uint16
    assert uint16_frame.bits_per_sample == 16
    assert float(uint16_frame.samples.min()) >= 0.0
    assert float(uint16_frame.samples.max()) <= 65535.0

    float_frame = frame.as_processing_frame("float32")
    assert float_frame.samples.dtype == np.float32
    assert 0.0 <= float(float_frame.samples.min()) <= float(float_frame.samples.max()) <= 1.0


@pytest.mark.skipif(not FLOAT_DNG.is_file(), reason="local floating-point DNG fixture is unavailable")
def test_dng_embedded_preview_is_exposed() -> None:
    result = taichi.imread(FLOAT_DNG, mode="preview")

    assert result["kind"] == "rgb"
    assert result["compression"] == 7
    assert result["width"] == 4032
    assert result["height"] == 3022
    assert bytes(result["preview"][:2]) == b"\xff\xd8"
