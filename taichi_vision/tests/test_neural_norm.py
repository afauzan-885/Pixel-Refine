"""Parity for softmax, log-softmax, normalisation, ReduceL2, and comparisons.

References are NumPy expressions written here, not calls into the Rust code.
"""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")

CMP = {"greater": 0, "less": 1, "equal": 2, "and": 3, "or": 4}


def _softmax(source, axis):
    out = np.zeros_like(source)
    outer = int(np.prod(source.shape[:axis])) if axis > 0 else 1
    inner = int(np.prod(source.shape[axis + 1 :])) if axis + 1 < len(source.shape) else 1
    native.softmax_f32(
        out.ctypes.data, source.ctypes.data, outer, source.shape[axis], inner
    )
    return out


def _log_softmax(source, axis):
    out = np.zeros_like(source)
    outer = int(np.prod(source.shape[:axis])) if axis > 0 else 1
    inner = int(np.prod(source.shape[axis + 1 :])) if axis + 1 < len(source.shape) else 1
    native.log_softmax_f32(
        out.ctypes.data, source.ctypes.data, outer, source.shape[axis], inner
    )
    return out


def _numpy_softmax(source, axis):
    shifted = source - source.max(axis=axis, keepdims=True)
    exponentiated = np.exp(shifted)
    return exponentiated / exponentiated.sum(axis=axis, keepdims=True)


@pytest.mark.parametrize("shape,axis", [
    ((5,), 0),
    ((2, 5), 1),
    ((2, 5), 0),
    ((2, 3, 4), 1),
    ((2, 3, 4), 2),
])
def test_softmax_matches_numpy(shape, axis):
    rng = np.random.default_rng(17)
    source = rng.uniform(-5, 5, size=shape).astype(np.float32)
    np.testing.assert_allclose(
        _softmax(source, axis), _numpy_softmax(source, axis), rtol=1e-6, atol=1e-6
    )


def test_softmax_is_stable_for_large_values():
    source = np.asarray([[1000.0, 1001.0, 999.0]], dtype=np.float32)
    got = _softmax(source, 1)
    assert np.isfinite(got).all()
    np.testing.assert_allclose(got.sum(), 1.0, rtol=1e-6)
    np.testing.assert_allclose(got, _numpy_softmax(source, 1), rtol=1e-6)


def test_log_softmax_matches_numpy():
    rng = np.random.default_rng(19)
    source = rng.uniform(-4, 4, size=(3, 6)).astype(np.float32)
    expected = np.log(_numpy_softmax(source, 1))
    np.testing.assert_allclose(_log_softmax(source, 1), expected, rtol=1e-5, atol=1e-5)


def test_normalize_matches_numpy_layer_norm():
    rng = np.random.default_rng(23)
    source = rng.uniform(-3, 3, size=(2, 8)).astype(np.float32)
    epsilon = 1e-5
    out = np.zeros_like(source)
    native.normalize_f32(
        out.ctypes.data, source.ctypes.data, 2, 8, 1, epsilon, False, 0, 0
    )
    mean = source.mean(axis=1, keepdims=True)
    variance = source.var(axis=1, keepdims=True)
    expected = (source - mean) / np.sqrt(variance + epsilon)
    np.testing.assert_allclose(out, expected, rtol=1e-5, atol=1e-5)


def test_normalize_with_scale_and_bias_matches_numpy():
    rng = np.random.default_rng(29)
    source = rng.uniform(-2, 2, size=(3, 4)).astype(np.float32)
    scale = rng.uniform(0.5, 1.5, size=(4,)).astype(np.float32)
    bias = rng.uniform(-1, 1, size=(4,)).astype(np.float32)
    epsilon = 1e-5
    out = np.zeros_like(source)
    native.normalize_f32(
        out.ctypes.data,
        source.ctypes.data,
        3,
        4,
        1,
        epsilon,
        True,
        scale.ctypes.data,
        bias.ctypes.data,
    )
    mean = source.mean(axis=1, keepdims=True)
    variance = source.var(axis=1, keepdims=True)
    expected = (source - mean) / np.sqrt(variance + epsilon) * scale + bias
    np.testing.assert_allclose(out, expected, rtol=1e-5, atol=1e-5)


def test_reduce_l2_matches_numpy():
    rng = np.random.default_rng(31)
    source = rng.uniform(-2, 2, size=(3, 5)).astype(np.float32)
    out = np.zeros((3,), dtype=np.float32)
    native.reduce_l2_f32(out.ctypes.data, source.ctypes.data, 3, 5, 1)
    np.testing.assert_allclose(
        out, np.sqrt((source**2).sum(axis=1)), rtol=1e-6, atol=1e-6
    )


def _strides(shape, out_shape):
    if not shape:
        return []
    offset = len(out_shape) - len(shape)
    own = [1] * len(shape)
    running = 1
    for axis in range(len(shape) - 1, -1, -1):
        own[axis] = running
        running *= shape[axis]
    return [0 if shape[a] == 1 and out_shape[a + offset] != 1 else own[a] for a in range(len(shape))]


@pytest.mark.parametrize("name", sorted(CMP))
def test_compare_matches_numpy(name):
    rng = np.random.default_rng(37)
    a = rng.uniform(-1, 1, size=(2, 4)).astype(np.float32)
    b = rng.uniform(-1, 1, size=(4,)).astype(np.float32)
    out_shape = np.broadcast_shapes(a.shape, b.shape)
    out = np.zeros(out_shape, dtype=np.int32)
    native.compare_f32(
        out.ctypes.data,
        a.ctypes.data,
        b.ctypes.data,
        list(out_shape),
        list(a.shape),
        list(b.shape),
        _strides(a.shape, out_shape),
        _strides(b.shape, out_shape),
        CMP[name],
    )
    expected = {
        "greater": a > b,
        "less": a < b,
        "equal": a == b,
        "and": (a != 0) & (b != 0),
        "or": (a != 0) | (b != 0),
    }[name].astype(np.int32)
    np.testing.assert_array_equal(out, expected)


def test_repeated_softmax_is_byte_identical():
    rng = np.random.default_rng(41)
    source = rng.uniform(-3, 3, size=(8, 16)).astype(np.float32)
    first = _softmax(source, 1)
    for _ in range(100):
        again = _softmax(source, 1)
        np.testing.assert_array_equal(first.view(np.uint32), again.view(np.uint32))
