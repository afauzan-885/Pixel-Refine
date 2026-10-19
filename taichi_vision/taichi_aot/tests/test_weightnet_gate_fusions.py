"""Focused CPU-JIT tests for the standalone WeightNet gate fusion."""

import numpy as np
import pytest
import taichi as ti

from taichi_vision.taichi_aot.weightnet_gate_fusions import (
    _weightnet_gate_flat_kernel,
    fused_weightnet_adaptive_gate,
)


@pytest.fixture(scope="module", autouse=True)
def taichi_cpu_runtime():
    ti.init(arch=ti.cpu, fast_math=False, enable_fallback=False)
    yield
    ti.sync()


def _sequential_fp32_reference(conv, safety_softplus):
    # Keep each ONNX intermediate rounded to FP32, like its materialized tensor.
    channel0_softplus = np.logaddexp(np.float32(0.0), conv[:, 0:1]).astype(np.float32)
    channel1_softplus = np.logaddexp(np.float32(0.0), conv[:, 1:2]).astype(np.float32)
    channel1_minus_safety = np.subtract(
        channel1_softplus, safety_softplus, dtype=np.float32
    )
    channel0_plus_half = np.add(
        channel0_softplus, np.float32(0.5), dtype=np.float32
    )
    product = np.multiply(channel0_plus_half, channel1_minus_safety, dtype=np.float32)
    with np.errstate(over="ignore", invalid="ignore"):
        exp_term = np.exp(np.negative(product, dtype=np.float32)).astype(np.float32)
    denominator = np.add(np.float32(1.0), exp_term, dtype=np.float32)
    return np.divide(np.float32(1.0), denominator, dtype=np.float32)


@pytest.mark.parametrize("shape", [(1, 2, 5, 7), (2, 2, 3, 11)])
def test_fused_adaptive_gate_matches_sequential_fp32(shape):
    rng = np.random.default_rng(9137)
    conv = rng.normal(0.0, 9.0, size=shape).astype(np.float32)
    safety = rng.normal(0.0, 4.0, size=(shape[0], 1, shape[2], shape[3])).astype(
        np.float32
    )
    conv.reshape(-1)[:12] = np.array(
        [-100.0, -80.0, -20.0, -1.0, -1e-5, 0.0, 1e-5, 1.0, 20.0, 80.0, 100.0, 3.0],
        dtype=np.float32,
    )
    safety.reshape(-1)[:6] = np.array(
        [-90.0, -10.0, -1e-5, 0.0, 10.0, 90.0], dtype=np.float32
    )

    expected = _sequential_fp32_reference(conv, safety)
    actual = fused_weightnet_adaptive_gate(conv, safety)

    assert actual.shape == (shape[0], 1, shape[2], shape[3])
    assert actual.dtype == np.float32
    assert np.isfinite(actual).all()
    np.testing.assert_allclose(actual, expected, atol=2e-7, rtol=2e-6)


def test_fused_adaptive_gate_reuses_non_aliasing_output():
    conv = np.zeros((1, 2, 2, 3), dtype=np.float32)
    safety = np.zeros((1, 1, 2, 3), dtype=np.float32)
    out = np.empty_like(safety)

    result = fused_weightnet_adaptive_gate(conv, safety, out)

    assert result is out
    expected = _sequential_fp32_reference(conv, safety)
    np.testing.assert_allclose(result, expected, atol=2e-7, rtol=2e-6)


def test_flat_gate_kernel_maps_nchw_channel_and_batch_offsets():
    conv = np.arange(2 * 2 * 2 * 3, dtype=np.float32).reshape(2, 2, 2, 3) / 3.0
    safety = np.linspace(-1.0, 1.0, 2 * 2 * 3, dtype=np.float32).reshape(2, 1, 2, 3)
    out = np.empty((2, 1, 2, 3), dtype=np.float32)

    _weightnet_gate_flat_kernel(
        conv.reshape(-1), safety.reshape(-1), out.reshape(-1), 2, 2, 3
    )

    np.testing.assert_allclose(
        out,
        _sequential_fp32_reference(conv, safety),
        atol=2e-7,
        rtol=2e-6,
    )


@pytest.mark.parametrize(
    "conv,safety,error,match",
    [
        (np.zeros((1, 1, 2, 2), np.float32), np.zeros((1, 1, 2, 2), np.float32), ValueError, "shape"),
        (np.zeros((1, 2, 2, 2), np.float32), np.zeros((1, 1, 2, 3), np.float32), ValueError, "safety_softplus"),
        (np.zeros((1, 2, 2, 2), np.float64), np.zeros((1, 1, 2, 2), np.float32), TypeError, "float32"),
        (np.zeros((1, 2, 2, 4), np.float32)[:, :, :, ::2], np.zeros((1, 1, 2, 2), np.float32), ValueError, "C-contiguous"),
    ],
)
def test_fused_adaptive_gate_rejects_invalid_inputs(conv, safety, error, match):
    with pytest.raises(error, match=match):
        fused_weightnet_adaptive_gate(conv, safety)


def test_fused_adaptive_gate_rejects_output_alias():
    conv = np.zeros((1, 2, 2, 2), dtype=np.float32)
    safety = np.zeros((1, 1, 2, 2), dtype=np.float32)
    with pytest.raises(ValueError, match="overlap"):
        fused_weightnet_adaptive_gate(conv, safety, conv[:, :1])

