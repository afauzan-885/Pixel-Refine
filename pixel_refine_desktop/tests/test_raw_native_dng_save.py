"""Focused coverage for source-depth lossless RAW Native DNG output."""

from __future__ import annotations

import numpy as np
import rawpy
import taichi

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline.result import (
    RawPipelineResult,
)
from taichi_vision.taichi_algorithm.compression import RawMosaicFrame


def test_raw_native_dng_is_16_bit_lossless_and_auto_compressed(tmp_path):
    height, width = 64, 128
    rows, columns = np.mgrid[:height, :width]
    samples = ((columns * 3 + rows * 5) % 1024).astype(np.uint16)
    frame = RawMosaicFrame.from_samples(
        samples,
        bits_per_sample=10,
        cfa_pattern=(0, 1, 1, 2),
    )
    normalized = samples.astype(np.float32) / np.float32(1023.0)
    result = RawPipelineResult(
        normalized_mosaic=normalized,
        preview_rgb=np.zeros((height, width, 3), dtype=np.float32),
        reference_frame=frame,
        source_paths=(),
    )

    path = tmp_path / "derived.dng"
    result.save_dng(path)
    decoded = taichi.read_dng(path)
    decoded_samples = np.asarray(decoded["data"])

    assert decoded["bits_per_sample"] == 10
    assert decoded["compression"] == 1
    np.testing.assert_array_equal(
        decoded_samples, result.quantized_mosaic(bits_per_sample=10)
    )
    with rawpy.imread(str(path)) as external:
        np.testing.assert_array_equal(
            external.raw_image.copy(), result.quantized_mosaic(bits_per_sample=10)
        )
