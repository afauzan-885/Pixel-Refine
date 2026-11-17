"""Parity and rejection tests for the movement primitives.

Every reference is computed with NumPy, which is ONNX's own definition of these
operators, so the test does not restate the implementation.
"""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")


def _apply(source, out_shape, offset, strides):
    out = np.zeros(out_shape, dtype=np.float32)
    native.movement_f32(
        out.ctypes.data,
        source.ctypes.data,
        list(out_shape),
        source.size,
        offset,
        list(strides),
    )
    return out


def _contiguous(shape):
    strides = [1] * len(shape)
    running = 1
    for axis in range(len(shape) - 1, -1, -1):
        strides[axis] = running
        running *= shape[axis]
    return strides


@pytest.mark.parametrize(
    "shape,perm",
    [
        ((6,), (0,)),
        ((2, 3), (1, 0)),
        ((2, 3, 4), (2, 0, 1)),
        ((1, 2, 3, 4), (0, 3, 1, 2)),
    ],
)
def test_transpose_matches_numpy(shape, perm):
    rng = np.random.default_rng(11)
    source = rng.uniform(-1, 1, size=shape).astype(np.float32)
    expected = np.transpose(source, perm)
    own = _contiguous(shape)
    strides = [own[axis] for axis in perm]
    got = _apply(source.ravel(), list(expected.shape), 0, strides)
    np.testing.assert_array_equal(got.reshape(expected.shape), expected)


def test_reshape_copies_the_same_bytes():
    source = np.arange(12, dtype=np.float32).reshape(3, 4)
    got = _apply(source.ravel(), [12], 0, [1])
    np.testing.assert_array_equal(got.reshape(3, 4), source)
    got = _apply(source.ravel(), [2, 6], 0, [6, 1])
    np.testing.assert_array_equal(got.reshape(2, 6), source.reshape(2, 6))


def test_slice_matches_numpy():
    source = np.arange(24, dtype=np.float32).reshape(4, 6)
    # Split a slice the way a real model does: a channel/row window.
    expected = source[1:3, 2:5]
    native_out = np.zeros(expected.shape, dtype=np.float32)
    native.slice_f32(
        native_out.ctypes.data,
        source.ctypes.data,
        list(source.shape),
        [1, 2],
        [3, 5],
        [1, 1],
    )
    np.testing.assert_array_equal(native_out, expected)


def test_negative_slice_bounds_match_numpy():
    source = np.arange(20, dtype=np.float32).reshape(4, 5)
    expected = source[-3:-1, -2:]
    native_out = np.zeros(expected.shape, dtype=np.float32)
    native.slice_f32(
        native_out.ctypes.data,
        source.ctypes.data,
        list(source.shape),
        [-3, -2],
        [-1, 5],
        [1, 1],
    )
    np.testing.assert_array_equal(native_out, expected)


def test_slice_beyond_the_extent_is_clamped():
    source = np.arange(6, dtype=np.float32).reshape(2, 3)
    # ONNX clamps an end past the axis, so this must equal the full row.
    expected = source[0:2, 0:3]
    native_out = np.zeros(expected.shape, dtype=np.float32)
    native.slice_f32(
        native_out.ctypes.data,
        source.ctypes.data,
        list(source.shape),
        [0, 0],
        [99, 99],
        [1, 1],
    )
    np.testing.assert_array_equal(native_out, expected)


@pytest.mark.parametrize("axis", [0, 1, 2, 3])
def test_concat_matches_numpy(axis):
    rng = np.random.default_rng(5)
    base = [2, 2, 2, 2]
    left_shape = list(base)
    right_shape = list(base)
    left_shape[axis] = 3
    right_shape[axis] = 5
    left = rng.uniform(-1, 1, size=left_shape).astype(np.float32)
    right = rng.uniform(-1, 1, size=right_shape).astype(np.float32)
    expected = np.concatenate([left, right], axis=axis)
    out = np.zeros(expected.shape, dtype=np.float32)
    native.concat_f32(
        out.ctypes.data,
        [left.ctypes.data, right.ctypes.data],
        [list(left.shape), list(right.shape)],
        axis,
    )
    np.testing.assert_array_equal(out, expected)


def test_concat_axis_zero_and_one():
    left = np.arange(6, dtype=np.float32).reshape(2, 3)
    right = np.arange(3, dtype=np.float32).reshape(1, 3)
    out = np.zeros((3, 3), dtype=np.float32)
    native.concat_f32(
        out.ctypes.data,
        [left.ctypes.data, right.ctypes.data],
        [list(left.shape), list(right.shape)],
        0,
    )
    np.testing.assert_array_equal(out, np.concatenate([left, right], axis=0))


def test_concat_refuses_a_mismatched_other_axis():
    # Concatenating along axis 1 requires axis 0 to agree. 2 vs 3 does not, so the
    # output shape (2, 7) would be a shape no real concatenation produces.
    left = np.zeros((2, 3), dtype=np.float32)
    right = np.zeros((3, 4), dtype=np.float32)
    out = np.zeros((2, 7), dtype=np.float32)
    with pytest.raises(ValueError, match="only the concatenation axis may differ"):
        native.concat_f32(
            out.ctypes.data,
            [left.ctypes.data, right.ctypes.data],
            [list(left.shape), list(right.shape)],
            1,
        )


def test_pad_matches_numpy():
    source = np.arange(6, dtype=np.float32).reshape(2, 3)
    expected = np.pad(source, ((1, 2), (0, 1)), mode="constant", constant_values=-1.0)
    out = np.zeros(expected.shape, dtype=np.float32)
    native.pad_f32(
        out.ctypes.data,
        source.ctypes.data,
        list(source.shape),
        [1, 0],
        [2, 1],
        -1.0,
    )
    np.testing.assert_array_equal(out, expected)


def test_pad_with_zero_keeps_interior_intact():
    source = np.arange(4, dtype=np.float32).reshape(2, 2)
    out = np.zeros((4, 4), dtype=np.float32)
    native.pad_f32(out.ctypes.data, source.ctypes.data, [2, 2], [1, 1], [1, 1], 7.0)
    np.testing.assert_array_equal(out[1:3, 1:3], source)
    assert out[0, 0] == 7.0


def test_overlapping_destination_is_refused():
    source = np.arange(8, dtype=np.float32)
    with pytest.raises(ValueError, match="overlaps"):
        native.movement_f32(source.ctypes.data, source.ctypes.data, [8], 8, 0, [1])


def test_slice_step_walks_the_axis():
    # A pixel-unshuffle slice takes every other element, which is step 2.
    source = np.arange(8, dtype=np.float32)
    expected = source[::2]
    out = np.zeros(expected.shape, dtype=np.float32)
    native.slice_f32(out.ctypes.data, source.ctypes.data, [8], [0], [8], [2])
    np.testing.assert_array_equal(out, expected)


def test_a_non_positive_slice_step_is_refused():
    source = np.arange(8, dtype=np.float32)
    out = np.zeros(4, dtype=np.float32)
    for step in (0, -1):
        with pytest.raises(ValueError, match="positive stride"):
            native.slice_f32(
                out.ctypes.data, source.ctypes.data, [8], [0], [8], [step]
            )


def test_space_to_depth_matches_numpy():
    # ONNX layout: output channel c*b² + dh*b + dw holds the cell's (dh, dw) pixel of
    # input channel c. Written as an explicit reference so a plain reshape cannot
    # accidentally agree.
    rng = np.random.default_rng(101)
    n, c, h, w, block = 1, 2, 4, 4, 2
    source = rng.uniform(-1, 1, size=(n, c, h, w)).astype(np.float32)
    oh, ow = h // block, w // block
    expected = np.zeros((n, c * block * block, oh, ow), dtype=np.float32)
    for channel in range(c):
        for dh in range(block):
            for dw in range(block):
                target = channel * block * block + dh * block + dw
                expected[:, target, :, :] = source[
                    :, channel, dh::block, dw::block
                ]
    out = np.zeros(expected.shape, dtype=np.float32)
    native.space_to_depth_f32(
        out.ctypes.data,
        source.ctypes.data,
        n=n,
        c=c,
        h=h,
        w=w,
        block=block,
    )
    np.testing.assert_array_equal(out, expected)


def test_space_to_depth_refuses_an_indivisible_shape():
    source = np.zeros((1, 1, 5, 4), dtype=np.float32)
    out = np.zeros((1, 4, 2, 2), dtype=np.float32)
    with pytest.raises(ValueError, match="not divisible"):
        native.space_to_depth_f32(
            out.ctypes.data, source.ctypes.data, n=1, c=1, h=5, w=4, block=2
        )


def test_repeated_movement_is_byte_identical():
    rng = np.random.default_rng(9)
    source = rng.uniform(-2, 2, size=(3, 5)).astype(np.float32)
    first = _apply(source.ravel(), [5, 3], 0, [1, 5])
    for _ in range(100):
        again = _apply(source.ravel(), [5, 3], 0, [1, 5])
        np.testing.assert_array_equal(first.view(np.uint32), again.view(np.uint32))
