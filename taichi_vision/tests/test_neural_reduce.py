"""Parity and rejection tests for reductions and average pooling."""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")

CODES = {"mean": 0, "sum": 1, "max": 2, "min": 3}


def _reference(source, axis, kind):
    if kind == "mean":
        return np.mean(source, axis=axis)
    if kind == "sum":
        return np.sum(source, axis=axis)
    if kind == "max":
        return np.max(source, axis=axis)
    if kind == "min":
        return np.min(source, axis=axis)
    raise AssertionError(kind)


@pytest.mark.parametrize("kind", sorted(CODES))
@pytest.mark.parametrize("shape,axis", [
    ((6,), 0),
    ((2, 3), 1),
    ((2, 3), 0),
    ((2, 3, 2), 1),
    ((2, 3, 4), 2),
    ((2, 3, 4), 0),
])
def test_reduce_matches_numpy(kind, shape, axis):
    rng = np.random.default_rng(21)
    source = rng.uniform(-4, 4, size=shape).astype(np.float32)
    expected = _reference(source, axis, kind).astype(np.float32)

    outer = int(np.prod(shape[:axis])) if axis > 0 else 1
    inner = int(np.prod(shape[axis + 1 :])) if axis + 1 < len(shape) else 1
    out = np.zeros(outer * inner, dtype=np.float32)
    native.reduce_axis_f32(
        out.ctypes.data,
        source.ctypes.data,
        outer,
        shape[axis],
        inner,
        CODES[kind],
        False,
    )
    got = out.reshape(expected.shape) if expected.ndim else out.reshape(())
    np.testing.assert_allclose(got, expected, rtol=1e-6, atol=1e-6)


def test_mean_of_one_element_is_itself():
    source = np.asarray([[5.0]], dtype=np.float32)
    out = np.zeros(1, dtype=np.float32)
    native.reduce_axis_f32(out.ctypes.data, source.ctypes.data, 1, 1, 1, CODES["mean"], False)
    assert out[0] == 5.0


def test_max_over_negative_values_does_not_start_at_zero():
    # Starting the accumulator at 0 would return 0 for an all-negative window,
    # which is a plausible-looking wrong answer.
    source = np.asarray([-5.0, -2.0, -9.0], dtype=np.float32)
    out = np.zeros(1, dtype=np.float32)
    native.reduce_axis_f32(out.ctypes.data, source.ctypes.data, 1, 3, 1, CODES["max"], False)
    assert out[0] == -2.0


def _pool(source, kernel, stride, pad, count_include_pad=False):
    n, c, h, w = source.shape
    kh, kw = kernel
    sh, sw = stride
    ph, pw = pad
    oh = (h + 2 * ph - kh) // sh + 1
    ow = (w + 2 * pw - kw) // sw + 1
    out = np.zeros((n, c, oh, ow), dtype=np.float32)
    native.average_pool2d_f32(
        out.ctypes.data,
        source.ctypes.data,
        n=n,
        c=c,
        h=h,
        w=w,
        oh=oh,
        ow=ow,
        kh=kh,
        kw=kw,
        sh=sh,
        sw=sw,
        ph=ph,
        pw=pw,
        count_include_pad=count_include_pad,
    )
    return out


def _numpy_pool(source, kernel, stride, pad, count_include_pad=False):
    kh, kw = kernel
    sh, sw = stride
    ph, pw = pad
    n, c, h, w = source.shape
    padded = np.pad(source, ((0, 0), (0, 0), (ph, ph), (pw, pw)))
    if count_include_pad:
        divisor_kernel = np.ones((kh, kw), dtype=np.float32)
    oh = (h + 2 * ph - kh) // sh + 1
    ow = (w + 2 * pw - kw) // sw + 1
    out = np.zeros((n, c, oh, ow), dtype=np.float32)
    for i in range(oh):
        for j in range(ow):
            window = padded[:, :, i * sh : i * sh + kh, j * sw : j * sw + kw]
            if count_include_pad:
                out[:, :, i, j] = window.sum(axis=(2, 3)) / (kh * kw)
            else:
                # Count only real elements: recompute the mask from the unpadded input.
                h0 = i * sh - ph
                w0 = j * sw - pw
                real_h = max(0, min(kh, h - h0) - max(0, -h0))
                real_w = max(0, min(kw, w - w0) - max(0, -w0))
                count = max(real_h, 0) * max(real_w, 0)
                out[:, :, i, j] = window.sum(axis=(2, 3)) / count
    return out


@pytest.mark.parametrize("kernel,stride,pad", [
    ((2, 2), (2, 2), (0, 0)),
    ((3, 3), (1, 1), (0, 0)),
    ((2, 2), (1, 1), (1, 1)),
    ((3, 3), (2, 2), (1, 1)),
])
def test_average_pool_matches_numpy(kernel, stride, pad):
    rng = np.random.default_rng(31)
    source = rng.uniform(-3, 3, size=(1, 2, 6, 7)).astype(np.float32)
    got = _pool(source, kernel, stride, pad)
    expected = _numpy_pool(source, kernel, stride, pad)
    np.testing.assert_allclose(got, expected, rtol=1e-5, atol=1e-5)


def test_count_include_pad_changes_the_divisor():
    # The two modes give different answers for the same window sum; a build that
    # ignored the flag would silently match only one of them.
    source = np.arange(16, dtype=np.float32).reshape(1, 1, 4, 4)
    with_pad = _pool(source, (2, 2), (2, 2), (1, 1), count_include_pad=True)
    without = _pool(source, (2, 2), (2, 2), (1, 1), count_include_pad=False)
    assert not np.allclose(with_pad, without), "the flag must change the result"
    # The corner window of an include-pad pool divides by 4, the other by 1.
    assert with_pad[0, 0, 0, 0] == pytest.approx(0.0)


def test_a_zero_stride_is_refused():
    source = np.zeros((1, 1, 4, 4), dtype=np.float32)
    out = np.zeros((1, 1, 2, 2), dtype=np.float32)
    with pytest.raises(ValueError, match="stride must be non-zero"):
        native.average_pool2d_f32(
            out.ctypes.data,
            source.ctypes.data,
            n=1,
            c=1,
            h=4,
            w=4,
            oh=2,
            ow=2,
            kh=2,
            kw=2,
            sh=0,
            sw=2,
            ph=0,
            pw=0,
        )


def test_an_empty_kernel_is_refused():
    source = np.zeros((1, 1, 4, 4), dtype=np.float32)
    out = np.zeros((1, 1, 4, 4), dtype=np.float32)
    with pytest.raises(ValueError, match="kernel must be non-empty"):
        native.average_pool2d_f32(
            out.ctypes.data,
            source.ctypes.data,
            n=1,
            c=1,
            h=4,
            w=4,
            oh=4,
            ow=4,
            kh=0,
            kw=2,
            sh=1,
            sw=1,
            ph=0,
            pw=0,
        )


def test_repeated_pooling_is_byte_identical():
    rng = np.random.default_rng(77)
    source = rng.uniform(-1, 1, size=(1, 2, 8, 8)).astype(np.float32)
    first = _pool(source, (3, 3), (2, 2), (1, 1))
    for _ in range(100):
        again = _pool(source, (3, 3), (2, 2), (1, 1))
        np.testing.assert_array_equal(first.view(np.uint32), again.view(np.uint32))
