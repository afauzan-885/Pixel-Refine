"""Isolated numeric candidates for AveragePool parity experiments."""

import taichi as ti


@ti.kernel
def nu_average_pool2d_2x2_pair_candidate(
    x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32, channels: ti.i32, h: ti.i32, w: ti.i32,
    oh: ti.i32, ow: ti.i32, sh: ti.i32, sw: ti.i32,
    ph: ti.i32, pw: ti.i32, count_include_pad: ti.i32,
):
    """2x2 AveragePool with pairwise row summation for CPU ORT parity."""
    for idx in range(n_batch * channels * oh * ow):
        ox = idx % ow
        t = idx // ow
        oy = t % oh
        c = (t // oh) % channels
        n = t // (oh * channels)
        base = (n * channels + c) * h * w
        iy0 = oy * sh - ph
        ix0 = ox * sw - pw
        v00 = 0.0
        v01 = 0.0
        v10 = 0.0
        v11 = 0.0
        valid = 0
        if 0 <= iy0 < h and 0 <= ix0 < w:
            v00 = x[base + iy0 * w + ix0]
            valid += 1
        if 0 <= iy0 < h and 0 <= ix0 + 1 < w:
            v01 = x[base + iy0 * w + ix0 + 1]
            valid += 1
        if 0 <= iy0 + 1 < h and 0 <= ix0 < w:
            v10 = x[base + (iy0 + 1) * w + ix0]
            valid += 1
        if 0 <= iy0 + 1 < h and 0 <= ix0 + 1 < w:
            v11 = x[base + (iy0 + 1) * w + ix0 + 1]
            valid += 1
        pair_sum = (v00 + v01) + (v10 + v11)
        denominator = 4 if count_include_pad != 0 else ti.max(valid, 1)
        y[idx] = pair_sum / ti.cast(denominator, ti.f32)


ALL_POOL_CANDIDATE_KERNELS = [nu_average_pool2d_2x2_pair_candidate]


@ti.kernel
def nu_average_pool2d_2x2_vertical_candidate(
    x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32, channels: ti.i32, h: ti.i32, w: ti.i32,
    oh: ti.i32, ow: ti.i32,
):
    """MLAS opset-17 2x2 pooling order: vertical pairs, horizontal sum, /4."""
    for idx in range(n_batch * channels * oh * ow):
        ox = idx % ow
        t = idx // ow
        oy = t % oh
        c = (t // oh) % channels
        n = t // (oh * channels)
        base = (n * channels + c) * h * w
        input_top = (oy * 2) * w + ox * 2
        top_left = x[base + input_top]
        top_right = x[base + input_top + 1]
        bottom_left = x[base + input_top + w]
        bottom_right = x[base + input_top + w + 1]
        vertical_left = top_left + bottom_left
        vertical_right = top_right + bottom_right
        total = vertical_left + vertical_right
        y[idx] = total / 4.0


ALL_POOL_CANDIDATE_KERNELS.append(nu_average_pool2d_2x2_vertical_candidate)
