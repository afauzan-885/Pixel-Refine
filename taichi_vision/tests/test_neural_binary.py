"""Parity and rejection tests for the binary primitives.

Accuracy is the gate. The reference is NumPy broadcasting, which is what ONNX
specifies, computed independently of the Rust code under test.
"""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")

CODES = {
    "Add": 0,
    "Sub": 1,
    "Mul": 2,
    "Div": 3,
    "Pow": 4,
    "Min": 5,
    "Max": 6,
    "Mod": 7,
}


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


def _reference(op, a, b):
    if op == "Add":
        return a + b
    if op == "Sub":
        return a - b
    if op == "Mul":
        return a * b
    if op == "Div":
        return a / b
    if op == "Pow":
        return a ** b
    if op == "Min":
        return np.minimum(a, b)
    if op == "Max":
        return np.maximum(a, b)
    if op == "Mod":
        return np.mod(a, b)
    raise AssertionError(op)


def run(op, a, b):
    a = np.ascontiguousarray(a, dtype=np.float32)
    b = np.ascontiguousarray(b, dtype=np.float32)
    out_shape = np.broadcast_shapes(a.shape, b.shape)
    out = np.zeros(out_shape, dtype=np.float32)
    native.binary_f32(
        out.ctypes.data,
        a.ctypes.data,
        b.ctypes.data,
        list(out_shape),
        list(a.shape),
        list(b.shape),
        _strides(a.shape, out_shape),
        _strides(b.shape, out_shape),
        CODES[op],
    )
    return out


SHAPES = [
    ((4,), (4,)),
    ((4,), ()),
    ((), (4,)),
    ((2, 3), (3,)),
    ((2, 1, 3), (1, 4, 1)),
    ((2, 2, 2, 2), (1, 2, 1, 1)),
    ((1, 3, 1, 1), (2, 3, 4, 5)),
]


@pytest.mark.parametrize("op", sorted(CODES))
@pytest.mark.parametrize("a_shape,b_shape", SHAPES)
def test_parity_with_numpy(op, a_shape, b_shape):
    rng = np.random.default_rng(1234)
    a = rng.uniform(0.5, 4.0, size=a_shape).astype(np.float32)
    b = rng.uniform(0.5, 4.0, size=b_shape).astype(np.float32)
    expected = _reference(op, a, b).astype(np.float32)
    got = run(op, a, b)
    assert got.shape == expected.shape
    # 1e-6 relative is the project's gate for f32.
    np.testing.assert_allclose(got, expected, rtol=1e-6, atol=1e-6)


def test_scalar_times_tensor_is_exact():
    a = np.arange(16, dtype=np.float32).reshape(2, 2, 2, 2)
    got = run("Mul", a, np.asarray(2.5, dtype=np.float32))
    np.testing.assert_array_equal(got, a * np.float32(2.5))


def test_negative_axis_broadcast_matches_numpy():
    a = np.linspace(-2, 2, 12, dtype=np.float32).reshape(3, 4)
    b = np.asarray([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    got = run("Max", a, b)
    np.testing.assert_array_equal(got, np.maximum(a, b))


def test_mod_follows_the_divisor_sign():
    a = np.asarray([-3.0, -3.0, 3.0, 3.0], dtype=np.float32)
    b = np.asarray([2.0, -2.0, 2.0, -2.0], dtype=np.float32)
    got = run("Mod", a, b)
    # ONNX `Mod` with fmod=0 is Python-style: the result has the divisor's sign.
    np.testing.assert_allclose(got, np.mod(a, b))


def test_incompatible_shapes_are_refused():
    a = np.zeros((2, 3), dtype=np.float32)
    b = np.zeros((4,), dtype=np.float32)
    out = np.zeros((2, 3), dtype=np.float32)
    with pytest.raises(ValueError, match="not broadcastable|neither 1"):
        native.binary_f32(
            out.ctypes.data,
            a.ctypes.data,
            b.ctypes.data,
            [2, 3],
            [2, 3],
            [4],
            [3, 1],
            [1],
            CODES["Add"],
        )


def test_overlapping_destination_is_refused():
    # In-place would make the result depend on iteration order.
    a = np.arange(8, dtype=np.float32)
    with pytest.raises(ValueError, match="overlaps"):
        native.binary_f32(
            a.ctypes.data,
            a.ctypes.data,
            a.ctypes.data,
            [8],
            [8],
            [8],
            [1],
            [1],
            CODES["Add"],
        )


def test_an_unknown_code_is_refused():
    a = np.ones(4, dtype=np.float32)
    out = np.zeros(4, dtype=np.float32)
    with pytest.raises(ValueError, match="unknown operator code"):
        native.binary_f32(
            out.ctypes.data,
            a.ctypes.data,
            a.ctypes.data,
            [4],
            [4],
            [4],
            [1],
            [1],
            99,
        )


def test_a_stride_that_would_read_outside_is_refused():
    a = np.ones(2, dtype=np.float32)
    out = np.zeros((2,), dtype=np.float32)
    with pytest.raises(ValueError, match="read outside|neither 1"):
        native.binary_f32(
            out.ctypes.data,
            a.ctypes.data,
            a.ctypes.data,
            [2],
            [2],
            [2],
            [4],
            [1],
            CODES["Add"],
        )


def test_repeated_runs_are_byte_identical():
    rng = np.random.default_rng(7)
    a = rng.uniform(-1, 1, size=(64,)).astype(np.float32)
    b = rng.uniform(0.5, 1.5, size=(64,)).astype(np.float32)
    first = run("Div", a, b)
    for _ in range(100):
        again = run("Div", a, b)
        np.testing.assert_array_equal(
            first.view(np.uint32), again.view(np.uint32), "output changed between runs"
        )


def test_integer_binary_matches_numpy():
    a = np.asarray([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
    b = np.asarray([10, 20, 30], dtype=np.int32)
    out = np.zeros((2, 3), dtype=np.int32)
    native.binary_i32(
        out.ctypes.data,
        a.ctypes.data,
        b.ctypes.data,
        [2, 3],
        [2, 3],
        [3],
        [3, 1],
        [1],
        CODES["Add"],
    )
    np.testing.assert_array_equal(out, a + b)


def test_i64_binary_is_bit_exact():
    a = np.asarray([2**40, 2**41, 2**42], dtype=np.int64)
    b = np.asarray([3, 5, 7], dtype=np.int64)
    out = np.zeros(3, dtype=np.int64)
    native.binary_i64(
        out.ctypes.data,
        a.ctypes.data,
        b.ctypes.data,
        [3],
        [3],
        [3],
        [1],
        [1],
        CODES["Mul"],
    )
    np.testing.assert_array_equal(out, a * b)


def test_integer_division_by_zero_is_an_error():
    a = np.asarray([1, 2], dtype=np.int32)
    zero = np.asarray([1, 0], dtype=np.int32)
    out = np.zeros(2, dtype=np.int32)
    with pytest.raises(ValueError, match="zero"):
        native.binary_i32(
            out.ctypes.data,
            a.ctypes.data,
            zero.ctypes.data,
            [2],
            [2],
            [2],
            [1],
            [1],
            CODES["Div"],
        )
