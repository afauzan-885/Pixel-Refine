"""Parity for grouped convolution, including the depthwise case.

The reference is an explicit NumPy convolution written here, not a call into the
Rust code, so a group-indexing mistake cannot agree with itself.
"""

from __future__ import annotations

import numpy as np
import pytest

native = pytest.importorskip("taichi.taichi_python")


def _reference_conv(x, w, b, stride, pads, group):
    """Explicit grouped convolution in NCHW, in f64 then cast to f32."""
    n, ci, h, wid = x.shape
    co, ci_per_group, kh, kw = w.shape
    sh, sw = stride
    ph, pw = pads
    co_per_group = co // group
    xp = np.pad(x.astype(np.float64), ((0, 0), (0, 0), (ph, ph), (pw, pw)))
    oh = (h + 2 * ph - kh) // sh + 1
    ow = (wid + 2 * pw - kw) // sw + 1
    out = np.zeros((n, co, oh, ow), dtype=np.float64)
    for g in range(group):
        for oc in range(co_per_group):
            global_oc = g * co_per_group + oc
            for i in range(oh):
                for j in range(ow):
                    window = xp[
                        :,
                        g * ci_per_group : (g + 1) * ci_per_group,
                        i * sh : i * sh + kh,
                        j * sw : j * sw + kw,
                    ]
                    out[:, global_oc, i, j] = np.sum(
                        window * w[global_oc][None, :, :, :], axis=(1, 2, 3)
                    )
    if b is not None:
        out += b.astype(np.float64)[None, :, None, None]
    return out.astype(np.float32)


def _run_conv(x, w, b, stride, pads, group, oh, ow):
    n, ci, h, wid = x.shape
    co, _, kh, kw = w.shape
    sh, sw = stride
    ph, pw = pads
    ci_per_group = ci // group
    workspace = np.zeros(
        (ci_per_group * kh * kw * oh * ow,), dtype=np.float32
    )
    out = np.zeros((n, co, oh, ow), dtype=np.float32)
    native.conv2d_group_f32(
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
        group=group,
        has_bias=1 if b is not None else 0,
        act=0,
        workspace_ptr=workspace.ctypes.data,
        workspace_bytes=workspace.nbytes,
    )
    return out


@pytest.mark.parametrize("group", [1, 2, 4])
def test_grouped_conv_matches_the_explicit_reference(group):
    rng = np.random.default_rng(41)
    n, ci, h, wid = 1, 4, 6, 6
    co = 4
    x = rng.uniform(-1, 1, size=(n, ci, h, wid)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(co, ci // group, 3, 3)).astype(np.float32)
    b = rng.uniform(-1, 1, size=(co,)).astype(np.float32)
    expected = _reference_conv(x, w, b, (1, 1), (1, 1), group)
    got = _run_conv(x, w, b, (1, 1), (1, 1), group, expected.shape[2], expected.shape[3])
    np.testing.assert_allclose(got, expected, rtol=1e-5, atol=1e-5)


def test_depthwise_conv_matches_the_reference():
    # group == ci == co is the depthwise case SDU uses.
    rng = np.random.default_rng(43)
    channels = 8
    x = rng.uniform(-1, 1, size=(1, channels, 5, 5)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(channels, 1, 3, 3)).astype(np.float32)
    expected = _reference_conv(x, w, None, (1, 1), (1, 1), channels)
    got = _run_conv(x, w, None, (1, 1), (1, 1), channels, expected.shape[2], expected.shape[3])
    np.testing.assert_allclose(got, expected, rtol=1e-5, atol=1e-5)


def test_group_one_delegates_to_the_proven_path():
    # The group=1 branch must equal the original conv bit for bit, since it calls it.
    rng = np.random.default_rng(47)
    x = rng.uniform(-1, 1, size=(1, 3, 5, 5)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(4, 3, 3, 3)).astype(np.float32)
    oh = (5 + 2 - 3) // 1 + 1
    workspace = np.zeros((3 * 3 * 3 * oh * oh,), dtype=np.float32)
    via_group = np.zeros((1, 4, oh, oh), dtype=np.float32)
    native.conv2d_group_f32(
        x.ctypes.data,
        w.ctypes.data,
        0,
        via_group.ctypes.data,
        n=1,
        ci=3,
        co=4,
        h=5,
        w_in=5,
        oh=oh,
        ow=oh,
        kh=3,
        kw=3,
        sh=1,
        sw=1,
        ph=1,
        pw=1,
        group=1,
        has_bias=0,
        act=0,
        workspace_ptr=workspace.ctypes.data,
        workspace_bytes=workspace.nbytes,
    )
    direct = np.zeros((1, 4, oh, oh), dtype=np.float32)
    workspace2 = np.zeros((3 * 3 * 3 * oh * oh,), dtype=np.float32)
    native.conv2d_f32(
        x.ctypes.data,
        w.ctypes.data,
        0,
        direct.ctypes.data,
        1,
        3,
        4,
        5,
        5,
        oh,
        oh,
        3,
        3,
        1,
        1,
        1,
        1,
        0,
        0,
        workspace2.ctypes.data,
        workspace2.nbytes,
    )
    np.testing.assert_array_equal(
        via_group.view(np.uint32), direct.view(np.uint32), "group=1 must delegate exactly"
    )


def test_a_group_that_does_not_divide_the_channels_is_refused():
    x = np.zeros((1, 3, 4, 4), dtype=np.float32)
    w = np.zeros((4, 1, 2, 2), dtype=np.float32)
    workspace = np.zeros((2 * 2 * 2 * 3 * 3,), dtype=np.float32)
    out = np.zeros((1, 4, 3, 3), dtype=np.float32)
    with pytest.raises(ValueError, match="does not divide"):
        native.conv2d_group_f32(
            x.ctypes.data,
            w.ctypes.data,
            0,
            out.ctypes.data,
            n=1,
            ci=3,
            co=4,
            h=4,
            w_in=4,
            oh=3,
            ow=3,
            kh=2,
            kw=2,
            sh=1,
            sw=1,
            ph=0,
            pw=0,
            group=2,
            has_bias=0,
            act=0,
            workspace_ptr=workspace.ctypes.data,
            workspace_bytes=workspace.nbytes,
        )


def test_a_workspace_that_is_too_small_is_refused():
    x = np.zeros((1, 4, 4, 4), dtype=np.float32)
    w = np.zeros((4, 2, 2, 2), dtype=np.float32)
    out = np.zeros((1, 4, 3, 3), dtype=np.float32)
    too_small = np.zeros((4,), dtype=np.float32)
    with pytest.raises(ValueError, match="workspace"):
        native.conv2d_group_f32(
            x.ctypes.data,
            w.ctypes.data,
            0,
            out.ctypes.data,
            n=1,
            ci=4,
            co=4,
            h=4,
            w_in=4,
            oh=3,
            ow=3,
            kh=2,
            kw=2,
            sh=1,
            sw=1,
            ph=0,
            pw=0,
            group=2,
            has_bias=0,
            act=0,
            workspace_ptr=too_small.ctypes.data,
            workspace_bytes=too_small.nbytes,
        )


def test_repeated_grouped_conv_is_byte_identical():
    rng = np.random.default_rng(53)
    x = rng.uniform(-1, 1, size=(1, 4, 5, 5)).astype(np.float32)
    w = rng.uniform(-1, 1, size=(4, 2, 3, 3)).astype(np.float32)
    first = _run_conv(x, w, None, (1, 1), (1, 1), 2, 5, 5)
    for _ in range(50):
        again = _run_conv(x, w, None, (1, 1), (1, 1), 2, 5, 5)
        np.testing.assert_array_equal(first.view(np.uint32), again.view(np.uint32))
