"""Block Flow must filter the reference, not silently skip it due to import order."""

import cv2
import numpy as np
import pytest

from taichi_vision import taichi_aot as aot
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.flownet_inference import (
    AOTOpticalFlowAligner,
)


@pytest.mark.parametrize(("noise_score", "kernel_size"), [(0.1, 0), (0.45, 3), (0.8, 5)])
def test_reference_prefilter_uses_shared_score(monkeypatch, noise_score, kernel_size):
    array = np.random.default_rng(74).random((64, 80, 3), dtype=np.float32)
    source_owner = aot.upload(array)
    source = source_owner.view_as_vector(False)
    calls = []
    original_filter = aot.box_filter

    def record_filter(src, **kwargs):
        calls.append(kwargs["kernel_size"])
        return original_filter(src, **kwargs)

    monkeypatch.setattr(aot, "box_filter", record_filter)
    aligner = None
    expected_owner = None
    expected_gray = None
    try:
        aligner = AOTOpticalFlowAligner(source, work_scale=1., full_shape=array.shape[:2],
                                      noise_score=noise_score)
        assert aligner.prefilter_kernel_size == kernel_size
        assert calls == ([kernel_size] if kernel_size else [])
        expected = array if not kernel_size else cv2.boxFilter(
            array, -1, (kernel_size, kernel_size), normalize=True, borderType=cv2.BORDER_REPLICATE)
        expected_owner = aot.upload(expected)
        expected_gray = aot.rgb2gray(expected_owner)
        actual = aligner.ref_l0.to_numpy()
        assert np.isfinite(actual).all()
        np.testing.assert_allclose(actual, expected_gray.to_numpy(), rtol=0, atol=1e-6)
    finally:
        if aligner is not None:
            aligner.close()
        for resource in (expected_gray, expected_owner, source_owner):
            if resource is not None:
                resource.release()
