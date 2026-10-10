"""Native box-filter ABI regression: scalar HWC and vec3 share physical storage."""

import cv2
import numpy as np
import pytest

from taichi_vision import taichi_aot as aot


@pytest.mark.parametrize("kernel_size", [3, 5])
@pytest.mark.parametrize("is_vector", [False, True])
@pytest.mark.parametrize("destination", ["allocated", "same_layout", "opposite_layout"])
def test_rgb_box_filter_matches_graph_layout(kernel_size, is_vector, destination):
    array = np.random.default_rng(417).random((37, 43, 3), dtype=np.float32)
    engine = aot.get_engine()
    source_owner = engine.upload(array)
    # Upload canonicalizes RGB as vec3; demosaic/analysis can instead expose
    # the same storage as scalar HWC, which triggered the original failure.
    source = source_owner.view_as_vector(is_vector, vector_dim=3)
    dst = None
    output = None
    gray = None
    if destination != "allocated":
        dst = engine.allocate(array.shape, dtype=np.float32,
                              is_vector=is_vector if destination == "same_layout" else not is_vector)
    try:
        output = aot.box_filter(source, kernel_size=kernel_size, dst=dst, return_gpu=True)
        if dst is not None:
            assert output is dst
        else:
            assert output.is_vector  # All RGB inputs use the validated vec3 graph.
        expected = cv2.boxFilter(array, -1, (kernel_size, kernel_size),
                                 normalize=True, borderType=cv2.BORDER_REPLICATE)
        actual = output.to_numpy()
        assert np.isfinite(actual).all()
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-6)
        # The app's reported failure was the *next* graph after a swallowed
        # box-filter error. Verify that the complete filter -> gray chain works.
        gray = aot.rgb2gray(output)
        assert gray.shape == array.shape[:2]
        assert np.isfinite(gray.to_numpy()).all()
    finally:
        for resource in (gray, output, source_owner):
            if resource is not None:
                resource.release()
        if dst is not None and dst is not output:
            dst.release()


@pytest.mark.parametrize("kernel_size", [3, 5])
def test_grayscale_box_filter_remains_scalar(kernel_size):
    array = np.random.default_rng(19).random((37, 43), dtype=np.float32)
    source = aot.get_engine().upload(array, is_vector=False)
    output = None
    try:
        output = aot.box_filter(source, kernel_size=kernel_size, return_gpu=True)
        assert not output.is_vector
        expected = cv2.boxFilter(array, -1, (kernel_size, kernel_size),
                                 normalize=True, borderType=cv2.BORDER_REPLICATE)
        np.testing.assert_allclose(output.to_numpy(), expected, rtol=0, atol=1e-6)
    finally:
        if output is not None:
            output.release()
        source.release()
