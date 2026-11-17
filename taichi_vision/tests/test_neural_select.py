"""Parity for `Where`, `Cast`, and `Fill`/`Range`."""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")

CASTS = {
    "f32->f32": 0,
    "f32->i32": 1,
    "f32->i64": 2,
    "i32->f32": 3,
    "i32->i64": 4,
    "i64->f32": 5,
    "i64->i32": 6,
}

DTYPES = {"f32": np.float32, "i32": np.int32, "i64": np.int64}


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


def _where(cond, x, y):
    out_shape = np.broadcast_shapes(cond.shape, x.shape, y.shape)
    out = np.zeros(out_shape, dtype=np.float32)
    native.where_f32(
        out.ctypes.data,
        cond.ctypes.data,
        x.ctypes.data,
        y.ctypes.data,
        list(out_shape),
        list(cond.shape),
        list(x.shape),
        list(y.shape),
        _strides(cond.shape, out_shape),
        _strides(x.shape, out_shape),
        _strides(y.shape, out_shape),
    )
    return out


@pytest.mark.parametrize("shapes", [
    ((4,), (4,), (4,)),
    ((4,), (), ()),
    ((2, 3), (2, 3), (3,)),
    ((2, 1, 3), (2, 4, 3), (1, 4, 3)),
])
def test_where_matches_numpy(shapes):
    cond_shape, x_shape, y_shape = shapes
    rng = np.random.default_rng(5)
    cond = (rng.uniform(0, 1, size=cond_shape) > 0.5).astype(np.int32)
    x = rng.uniform(-1, 1, size=x_shape).astype(np.float32)
    y = rng.uniform(-1, 1, size=y_shape).astype(np.float32)
    expected = np.where(cond.astype(bool), x, y).astype(np.float32)
    np.testing.assert_array_equal(_where(cond, x, y), expected)


def test_where_treats_any_nonzero_as_true():
    # ONNX spells a bool as int32; 2 must mean true, not "not 1".
    cond = np.asarray([2, 0, -1, 0], dtype=np.int32)
    x = np.asarray([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
    y = np.asarray([9.0, 9.0, 9.0, 9.0], dtype=np.float32)
    np.testing.assert_array_equal(_where(cond, x, y), [1.0, 9.0, 1.0, 9.0])


def test_where_refuses_an_overlapping_destination():
    cond = np.ones(4, dtype=np.int32)
    x = np.zeros(4, dtype=np.float32)
    with pytest.raises(ValueError, match="overlaps"):
        native.where_f32(
            x.ctypes.data,
            cond.ctypes.data,
            x.ctypes.data,
            x.ctypes.data,
            [4],
            [4],
            [4],
            [4],
            [1],
            [1],
            [1],
        )


@pytest.mark.parametrize("code", sorted(CASTS.values()))
def test_cast_matches_numpy(code):
    name = next(k for k, v in CASTS.items() if v == code)
    source_kind, target_kind = name.split("->")
    rng = np.random.default_rng(11)
    if source_kind == "f32":
        source = rng.uniform(-100, 100, size=32).astype(np.float32)
    elif source_kind == "i32":
        source = rng.integers(-1000, 1000, size=32).astype(np.int32)
    else:
        source = rng.integers(-10**6, 10**6, size=32).astype(np.int64)
    target = np.zeros(32, dtype=DTYPES[target_kind])
    native.cast_f32(target.ctypes.data, source.ctypes.data, source.size, code)
    expected = source.astype(DTYPES[target_kind])
    np.testing.assert_array_equal(target, expected)


def test_float_to_int_truncates_toward_zero():
    source = np.asarray([2.9, -2.9, 0.0, 0.5, -0.5], dtype=np.float32)
    target = np.zeros(5, dtype=np.int32)
    native.cast_f32(target.ctypes.data, source.ctypes.data, 5, CASTS["f32->i32"])
    np.testing.assert_array_equal(target, [2, -2, 0, 0, 0])


def test_a_float_outside_the_i32_range_is_refused():
    source = np.asarray([1e10], dtype=np.float32)
    target = np.zeros(1, dtype=np.int32)
    with pytest.raises(ValueError, match="outside the i32 range"):
        native.cast_f32(target.ctypes.data, source.ctypes.data, 1, CASTS["f32->i32"])


def test_an_i64_outside_the_i32_range_is_refused():
    source = np.asarray([2**40], dtype=np.int64)
    target = np.zeros(1, dtype=np.int32)
    with pytest.raises(ValueError, match="does not fit in i32"):
        native.cast_f32(target.ctypes.data, source.ctypes.data, 1, CASTS["i64->i32"])


def test_fill_and_range_write_every_element():
    values = np.full(6, 3.0, dtype=np.float32)
    native.fill_f32(values.ctypes.data, 6, -1.5)
    np.testing.assert_array_equal(values, np.full(6, -1.5, dtype=np.float32))

    sequence = np.zeros(5, dtype=np.int64)
    native.range_i64(sequence.ctypes.data, 5, 4, 2)
    np.testing.assert_array_equal(sequence, np.arange(4, 14, 2, dtype=np.int64))


def test_repeated_where_is_byte_identical():
    rng = np.random.default_rng(3)
    cond = (rng.uniform(0, 1, size=(16, 16)) > 0.5).astype(np.int32)
    x = rng.uniform(-1, 1, size=(16, 16)).astype(np.float32)
    y = rng.uniform(-1, 1, size=(16, 16)).astype(np.float32)
    first = _where(cond, x, y)
    for _ in range(100):
        again = _where(cond, x, y)
        np.testing.assert_array_equal(first.view(np.uint32), again.view(np.uint32))
