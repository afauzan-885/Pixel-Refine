# -*- coding: utf-8 -*-
"""Unit tests for strict input validation, color preprocessing separation, and device residency."""

import numpy as np
import onnx
from onnx import helper as h, numpy_helper as nh, TensorProto as T
import pytest
import taichi as ti

from taichi_vision.taichi_aot import neural_engine, neural_adapters
from taichi_vision.taichi_aot.neural_adapters import adapt_image_to_nchw


@pytest.fixture(scope="module", autouse=True)
def runtime():
    ti.init(arch=ti.cpu, fast_math=False, enable_fallback=False)
    yield
    ti.sync()


def _make_dummy_model(channels=1, height=4, width=4):
    shape = (1, channels, height, width)
    g = h.make_graph(
        [h.make_node("Relu", ["x"], ["y"])],
        "test_val",
        [h.make_tensor_value_info("x", T.FLOAT, shape)],
        [h.make_tensor_value_info("y", T.FLOAT, shape)],
    )
    proto = h.make_model(g, opset_imports=[h.make_opsetid("", 17)])
    return neural_engine.onnx(proto.SerializeToString(), backend="cpu", channels=channels)


def test_rejects_non_4d_dimension_with_descriptive_error():
    model = _make_dummy_model(channels=1)

    # 2D input (H, W)
    x_2d = np.ones((4, 4), dtype=np.float32)
    with pytest.raises(ValueError, match="dimension mismatch.*model expects 4D tensor"):
        model(x_2d)

    # 3D input (H, W, C)
    x_3d = np.ones((4, 4, 1), dtype=np.float32)
    with pytest.raises(ValueError, match="dimension mismatch.*model expects 4D tensor"):
        model(x_3d)


def test_rejects_channel_mismatch_with_descriptive_error():
    # Model expects 1 channel (Grayscale)
    model_gray = _make_dummy_model(channels=1)
    x_rgb = np.ones((1, 3, 4, 4), dtype=np.float32)

    with pytest.raises(ValueError, match="channel/color mismatch: model requires 1 channel.*Grayscale"):
        model_gray(x_rgb)

    # Model expects 3 channels
    model_rgb = _make_dummy_model(channels=3)
    x_gray = np.ones((1, 1, 4, 4), dtype=np.float32)

    with pytest.raises(ValueError, match="channel/color mismatch: model requires 3 channel"):
        model_rgb(x_gray)


def test_rejects_unnormalized_dtype():
    model = _make_dummy_model(channels=1)
    x_uint8 = np.full((1, 1, 4, 4), 255, dtype=np.uint8)

    with pytest.raises(ValueError, match="dtype mismatch: model expects float32 normalized tensor"):
        model(x_uint8)


def test_external_adapter_successfully_feeds_into_neural_engine():
    model = _make_dummy_model(channels=1, height=8, width=8)

    # Raw BGR uint8 image (H=8, W=8, C=3) as typically loaded by cv2.imread
    raw_bgr_img = np.full((8, 8, 3), 128, dtype=np.uint8)

    # Preprocessing outside neural engine
    preprocessed = adapt_image_to_nchw(raw_bgr_img, expected_channels=1, is_bgr=True, normalize=True)
    assert preprocessed.shape == (1, 1, 8, 8)
    assert preprocessed.dtype == np.float32

    # Neural engine executes validated preprocessed tensor
    out = model(preprocessed)
    assert out.shape == (1, 1, 8, 8)
    assert out.dtype == np.float32


def test_end_to_end_device_residency_without_cpu_readback():
    model = _make_dummy_model(channels=1, height=4, width=4)
    x_np = np.ones((1, 1, 4, 4), dtype=np.float32)

    # 1. Device input
    x_dev = ti.ndarray(dtype=ti.f32, shape=(1, 1, 4, 4))
    x_dev.from_numpy(x_np)

    # 2. Execute with return_gpu=True -> Result stays 100% in Taichi device memory
    out_dev = model(x_dev, return_gpu=True)
    assert isinstance(out_dev, ti.Ndarray)
    assert out_dev.shape == (1, 1, 4, 4)
    assert out_dev.dtype == ti.f32

    # 3. Only caller explicitly chooses when to download to CPU
    out_cpu = out_dev.to_numpy()
    np.testing.assert_allclose(out_cpu, x_np)

