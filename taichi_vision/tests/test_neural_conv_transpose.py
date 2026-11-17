"""Parity for `ConvTranspose`.

The reference is built by scattering in NumPy, written independently of the Rust
code, so a weight-layout mistake (ci/co swapped) cannot agree with itself.
"""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")


def _scatter_reference(x, w, b, stride, pads, output_shape):
    """ConvTranspose by explicit scatter, in f64."""
    n, ci, h, wid = x.shape
    _, co, kh, kw = w.shape
    sh, sw = stride
    ph, pw = pads
    oh, ow = output_shape
    out = np.zeros((n, co, oh, ow), dtype=np.float64)
    if b is not None:
        out += b.astype(np.float64)[None, :, None, None]
    xd = x.astype(np.float64)
    wd = w.astype(np.float64)
    for ni in range(n):
        for ic in range(ci):
            for iy in range(h):
                for ix in range(wid):
                    value = xd[ni, ic, iy, ix]
                    if value == 0.0:
                        continue
                    for oc in range(co):
                        for ky in range(kh):
                            oy = iy * sh + ky - ph
                            if oy < 0 or oy >= oh:
                                continue
                            for kx in range(kw):
                                ox = ix * sw + kx - pw
                                if ox < 0 or ox >= ow:
                                    continue
                                out[ni, oc, oy, ox] += value * wd[ic, oc, ky, kx]
    return out.astype(np.float32)


def _run(x, w, b, stride, pads, output_shape):
    n, ci, h, wid = x.shape
    _, co, kh, kw = w.shape
    sh, sw = stride
    ph, pw = pads
    oh, ow = output_shape
    out = np.zeros((n, co, oh, ow), dtype=np.float32)
    native.conv_transpose2d_f32(
        x.ctypes.data,
        w.ctypes.data,
        b.ctypes.data if b is not None else 0,
        out.ctypes.data,
        n=n,
        ci=ci,
        co=co,
        h=h,
        w_in=wid,
        oh=oh,
        ow=ow,
        kh=kh,
        kw=kw,
        sh=sh,
        sw=sw,
        ph=ph,
        pw=pw,
        has_bias=1 if b is not None else 0,
        act=0,
    )
    return out


@pytest.mark.parametrize("kernel,stride,pad", [
    ((2, 2), (2, 2), (0, 0)),
    ((3, 3), (1, 1), (0, 0)),
    ((3, 3), (2, 2), (1, 1)),
    ((2, 2), (1, 1), (0, 0)),
])
def test_conv_transpose_matches_the_scatter_reference(kernel, stride, pad):
    rng = np.random.default_rng(83)
    n, ci, h, wid = 1, 2, 3, 3
    co = 3
    kh, kw = kernel
    sh, sw = stride
    ph, pw = pad
    oh = (h - 1) * sh + kh - 2 * ph
    ow = (wid - 1) * sw + kw - 2 * pw
    x = rng.uniform(-1, 1, size=(n, ci, h, wid)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(ci, co, kh, kw)).astype(np.float32)
    b = rng.uniform(-1, 1, size=(co,)).astype(np.float32)
    expected = _scatter_reference(x, w, b, stride, pad, (oh, ow))
    got = _run(x, w, b, stride, pad, (oh, ow))
    np.testing.assert_allclose(got, expected, rtol=1e-5, atol=1e-5)


def test_the_weight_layout_is_input_major():
    # A (ci, co, k, k) weight is ONNX's spelling for ConvTranspose. If the code
    # read it as (co, ci, k, k) the result would have the right shape and the wrong
    # numbers, so this locks the layout with a distinguishable case.
    x = np.arange(1, 5, dtype=np.float32).reshape(1, 1, 2, 2)
    w = np.asarray([[[[1.0]]]], dtype=np.float32)  # ci=1, co=1, 1x1
    expected = _scatter_reference(x, w, None, (1, 1), (0, 0), (2, 2))
    got = _run(x, w, None, (1, 1), (0, 0), (2, 2))
    np.testing.assert_array_equal(got, expected)


def test_bias_is_the_starting_value():
    # Every element begins at the bias and the scatter adds to it, so a region the
    # kernel does not reach must equal the bias, not zero.
    x = np.zeros((1, 1, 2, 2), dtype=np.float32)
    w = np.ones((1, 1, 1, 1), dtype=np.float32)
    b = np.asarray([2.5], dtype=np.float32)
    got = _run(x, w, b, (1, 1), (0, 0), (2, 2))
    np.testing.assert_array_equal(got, np.full((1, 1, 2, 2), 2.5, dtype=np.float32))


def test_repeated_runs_are_byte_identical():
    rng = np.random.default_rng(89)
    x = rng.uniform(-1, 1, size=(1, 2, 3, 3)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(2, 2, 3, 3)).astype(np.float32)
    first = _run(x, w, None, (2, 2), (1, 1), (5, 5))
    for _ in range(50):
        again = _run(x, w, None, (2, 2), (1, 1), (5, 5))
        np.testing.assert_array_equal(first.view(np.uint32), again.view(np.uint32))
