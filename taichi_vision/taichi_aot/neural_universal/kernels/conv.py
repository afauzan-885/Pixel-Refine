"""Convolution universal kernels (forward and transposed)."""

import taichi as ti

from .common import nu_activate


@ti.kernel
def nu_conv2d(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    kh: ti.i32,
    kw: ti.i32,
    sh: ti.i32,
    sw: ti.i32,
    ph: ti.i32,
    pw: ti.i32,
    dh: ti.i32,
    dw: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    ci_per_group = ci // group
    co_per_group = co // group
    kk = kh * kw
    plane = h * w_in
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        acc = 0.0
        group_id = oc // co_per_group
        iy0 = yy * sh - ph
        ix0 = xx * sw - pw
        ky_lo = 0
        if iy0 < 0:
            ky_lo = (dh - 1 - iy0) // dh
        ky_hi = ti.min(kh, (h - iy0 + dh - 1) // dh)
        kx_lo = 0
        if ix0 < 0:
            kx_lo = (dw - 1 - ix0) // dw
        kx_hi = ti.min(kw, (w_in - ix0 + dw - 1) // dw)
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * kk
        for ic in range(ci_per_group):
            for ky in range(ky_lo, ky_hi):
                xrow = x_base + ic * plane + (iy0 + ky * dh) * w_in + ix0
                wrow = w_base + ic * kk + ky * kw
                for kx in range(kx_lo, kx_hi):
                    acc += x[xrow + kx * dw] * w[wrow + kx]
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_4x4_s2(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Static 4x4/stride-2 specialization; all other Conv shapes use nu_conv2d."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        iy0 = yy * 2
        ix0 = xx * 2
        acc = 0.0
        compensation = 0.0
        for channel_block in range((ci_per_group + 3) // 4):
            for lane in ti.static(range(4)):
                ic = channel_block * 4 + lane
                if ic < ci_per_group:
                    input_channel = x_base + ic * plane
                    weight_channel = w_base + ic * 16
                    for ky in range(4):
                        input_row = input_channel + (iy0 + ky) * w_in + ix0
                        weight_row = weight_channel + ky * 4
                        for kx in range(4):
                            product = x[input_row + kx] * w[weight_row + kx]
                            corrected = product - compensation
                            updated = acc + corrected
                            compensation = (updated - acc) - corrected
                            acc = updated
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_4x4_s2_spatial_2x2(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Profile-only 2x2 output tile with independent, ordered Kahan sums."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    tile_rows = (oh + 1) // 2
    tile_cols = (ow + 1) // 2
    for idx in range(n_batch * co * tile_rows * tile_cols):
        tile_x = idx % tile_cols
        t = idx // tile_cols
        tile_y = t % tile_rows
        t2 = t // tile_rows
        oc = t2 % co
        n = t2 // co
        out_y = tile_y * 2
        out_x = tile_x * 2
        has_out_y1 = out_y + 1 < oh
        has_out_x1 = out_x + 1 < ow
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        input_y0 = out_y * 2
        input_x0 = out_x * 2

        acc00 = 0.0
        comp00 = 0.0
        acc01 = 0.0
        comp01 = 0.0
        acc10 = 0.0
        comp10 = 0.0
        acc11 = 0.0
        comp11 = 0.0

        for ic in range(ci_per_group):
            input_channel = x_base + ic * plane
            patch = ti.Matrix.zero(ti.f32, 6, 6)
            for py in range(6):
                if py < 4 or has_out_y1:
                    for px in range(6):
                        if px < 4 or has_out_x1:
                            patch[py, px] = x[
                                input_channel + (input_y0 + py) * w_in + input_x0 + px
                            ]
            weight_channel = w_base + ic * 16
            for ky in range(4):
                for kx in range(4):
                    weight = w[weight_channel + ky * 4 + kx]

                    product00 = patch[ky, kx] * weight
                    corrected00 = product00 - comp00
                    updated00 = acc00 + corrected00
                    comp00 = (updated00 - acc00) - corrected00
                    acc00 = updated00

                    if has_out_x1:
                        product01 = patch[ky, kx + 2] * weight
                        corrected01 = product01 - comp01
                        updated01 = acc01 + corrected01
                        comp01 = (updated01 - acc01) - corrected01
                        acc01 = updated01

                    if has_out_y1:
                        product10 = patch[ky + 2, kx] * weight
                        corrected10 = product10 - comp10
                        updated10 = acc10 + corrected10
                        comp10 = (updated10 - acc10) - corrected10
                        acc10 = updated10

                    if has_out_y1 and has_out_x1:
                        product11 = patch[ky + 2, kx + 2] * weight
                        corrected11 = product11 - comp11
                        updated11 = acc11 + corrected11
                        comp11 = (updated11 - acc11) - corrected11
                        acc11 = updated11

        if has_bias != 0:
            acc00 += b[oc]
            if has_out_x1:
                acc01 += b[oc]
            if has_out_y1:
                acc10 += b[oc]
            if has_out_y1 and has_out_x1:
                acc11 += b[oc]

        out_base = (n * co + oc) * oh * ow + out_y * ow + out_x
        y[out_base] = nu_activate(acc00, act)
        if has_out_x1:
            y[out_base + 1] = nu_activate(acc01, act)
        if has_out_y1:
            y[out_base + ow] = nu_activate(acc10, act)
        if has_out_y1 and has_out_x1:
            y[out_base + ow + 1] = nu_activate(acc11, act)


@ti.kernel
def nu_conv2d_4x4_s2_kahan_p8(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Profile-only CPU scheduling directive; arithmetic matches baseline."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    ti.loop_config(parallelize=8)
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        iy0 = yy * 2
        ix0 = xx * 2
        acc = 0.0
        compensation = 0.0
        for channel_block in range((ci_per_group + 3) // 4):
            for lane in ti.static(range(4)):
                ic = channel_block * 4 + lane
                if ic < ci_per_group:
                    input_channel = x_base + ic * plane
                    weight_channel = w_base + ic * 16
                    for ky in range(4):
                        input_row = input_channel + (iy0 + ky) * w_in + ix0
                        weight_row = weight_channel + ky * 4
                        for kx in range(4):
                            product = x[input_row + kx] * w[weight_row + kx]
                            corrected = product - compensation
                            updated = acc + corrected
                            compensation = (updated - acc) - corrected
                            acc = updated
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_4x4_s2_kahan_ndrange(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Profile-only coordinate iteration; preserve baseline Kahan arithmetic."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    for n, oc, yy, xx in ti.ndrange(n_batch, co, oh, ow):
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        iy0 = yy * 2
        ix0 = xx * 2
        acc = 0.0
        compensation = 0.0
        for channel_block in range((ci_per_group + 3) // 4):
            for lane in ti.static(range(4)):
                ic = channel_block * 4 + lane
                if ic < ci_per_group:
                    input_channel = x_base + ic * plane
                    weight_channel = w_base + ic * 16
                    for ky in range(4):
                        input_row = input_channel + (iy0 + ky) * w_in + ix0
                        weight_row = weight_channel + ky * 4
                        for kx in range(4):
                            product = x[input_row + kx] * w[weight_row + kx]
                            corrected = product - compensation
                            updated = acc + corrected
                            compensation = (updated - acc) - corrected
                            acc = updated
        if has_bias != 0:
            acc += b[oc]
        y[((n * co + oc) * oh + yy) * ow + xx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_4x4_s2_kahan_linear_ci(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Opt-in CPU512 variant: linear CI traversal preserves Kahan product order."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        iy0 = yy * 2
        ix0 = xx * 2
        acc = 0.0
        compensation = 0.0
        for ic in range(ci_per_group):
            input_channel = x_base + ic * plane
            weight_channel = w_base + ic * 16
            for ky in range(4):
                input_row = input_channel + (iy0 + ky) * w_in + ix0
                weight_row = weight_channel + ky * 4
                for kx in range(4):
                    product = x[input_row + kx] * w[weight_row + kx]
                    corrected = product - compensation
                    updated = acc + corrected
                    compensation = (updated - acc) - corrected
                    acc = updated
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_4x4_s2_kahan_unrolled(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Static-profile-only unrolled taps; preserves Kahan accumulation order."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        iy0 = yy * 2
        ix0 = xx * 2
        acc = 0.0
        compensation = 0.0
        for channel_block in range((ci_per_group + 3) // 4):
            for lane in ti.static(range(4)):
                ic = channel_block * 4 + lane
                if ic < ci_per_group:
                    input_channel = x_base + ic * plane
                    weight_channel = w_base + ic * 16
                    for ky in ti.static(range(4)):
                        input_row = input_channel + (iy0 + ky) * w_in + ix0
                        weight_row = weight_channel + ky * 4
                        for kx in ti.static(range(4)):
                            product = x[input_row + kx] * w[weight_row + kx]
                            corrected = product - compensation
                            updated = acc + corrected
                            compensation = (updated - acc) - corrected
                            acc = updated
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_4x4_s2_plain(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Profile-only plain FP32 accumulation; generic Kahan path remains default."""
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        group_id = oc // co_per_group
        x_base = (n * ci + group_id * ci_per_group) * plane
        w_base = oc * ci_per_group * 16
        iy0 = yy * 2
        ix0 = xx * 2
        acc = 0.0
        for channel_block in range((ci_per_group + 3) // 4):
            for lane in ti.static(range(4)):
                ic = channel_block * 4 + lane
                if ic < ci_per_group:
                    input_channel = x_base + ic * plane
                    weight_channel = w_base + ic * 16
                    for ky in range(4):
                        input_row = input_channel + (iy0 + ky) * w_in + ix0
                        weight_row = weight_channel + ky * 4
                        for kx in range(4):
                            acc += x[input_row + kx] * w[weight_row + kx]
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_3x3_s1p1(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Group-1, kernel 3x3, stride 1, pad 1, dilation 1 with hoisted taps."""
    plane = h * w_in
    hw = plane
    for idx in range(n_batch * co * hw):
        p = idx % hw
        oc = (idx // hw) % co
        n = idx // (hw * co)
        yy = p // w_in
        xx = p % w_in
        nh = h - 2
        nw = w_in - 2
        acc = 0.0
        w_base = oc * ci * 9
        x_base = n * ci * plane
        for ic in range(ci):
            xb = x_base + ic * plane
            wb = w_base + ic * 9
            c0 = 0.0
            c1 = 0.0
            c2 = 0.0
            if yy >= 1 and yy <= nh:
                r = xb + (yy - 1) * w_in
                if xx >= 1 and xx <= nw:
                    c0 = x[r + xx - 1] * w[wb] + x[r + xx] * w[wb + 1] + x[r + xx + 1] * w[wb + 2]
                    c1 = x[r + w_in + xx - 1] * w[wb + 3] + x[r + w_in + xx] * w[wb + 4] + x[r + w_in + xx + 1] * w[wb + 5]
                    c2 = x[r + 2 * w_in + xx - 1] * w[wb + 6] + x[r + 2 * w_in + xx] * w[wb + 7] + x[r + 2 * w_in + xx + 1] * w[wb + 8]
                else:
                    for ky in ti.static(range(3)):
                        for kx in ti.static(range(3)):
                            iy = yy + ky - 1
                            ix = xx + kx - 1
                            if 0 <= iy < h and 0 <= ix < w_in:
                                c1 += x[xb + iy * w_in + ix] * w[wb + ky * 3 + kx]
            else:
                for ky in ti.static(range(3)):
                    for kx in ti.static(range(3)):
                        iy = yy + ky - 1
                        ix = xx + kx - 1
                        if 0 <= iy < h and 0 <= ix < w_in:
                            c1 += x[xb + iy * w_in + ix] * w[wb + ky * 3 + kx]
            acc += c0 + c1 + c2
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_1x1(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    hw: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    for idx in range(n_batch * co * hw):
        p = idx % hw
        oc = (idx // hw) % co
        n = idx // (hw * co)
        acc = 0.0
        w_base = oc * ci
        x_base = n * ci * hw + p
        for ic in range(ci):
            acc += x[x_base + ic * hw] * w[w_base + ic]
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv2d_1x1_spatial4(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    hw: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    """Profile-only 1x1 Conv over four same-row spatial outputs.

    This override is compiled only into the exact square CPU512 static profile.
    Every output keeps the baseline ``ic`` accumulation order; the spatial
    tile shares each weight load across four independent scalar accumulators.
    """
    width = ti.cast(ti.sqrt(ti.cast(hw, ti.f32)) + 0.5, ti.i32)
    tiles_per_row = (width + 3) // 4
    positions_per_n = width * tiles_per_row
    for idx in range(n_batch * co * positions_per_n):
        tile = idx % positions_per_n
        oc = (idx // positions_per_n) % co
        n = idx // (positions_per_n * co)
        row = tile // tiles_per_row
        tile_x = (tile % tiles_per_row) * 4
        spatial = row * width + tile_x
        remaining = width - tile_x
        acc0 = 0.0
        acc1 = 0.0
        acc2 = 0.0
        acc3 = 0.0
        weight_base = oc * ci
        input_base = n * ci * hw + spatial
        for ic in range(ci):
            weight = w[weight_base + ic]
            channel_base = input_base + ic * hw
            value0 = x[channel_base]
            acc0 += value0 * weight
            if remaining > 1:
                value1 = x[channel_base + 1]
                acc1 += value1 * weight
            if remaining > 2:
                value2 = x[channel_base + 2]
                acc2 += value2 * weight
            if remaining > 3:
                value3 = x[channel_base + 3]
                acc3 += value3 * weight
        if has_bias != 0:
            bias = b[oc]
            acc0 += bias
            if remaining > 1:
                acc1 += bias
            if remaining > 2:
                acc2 += bias
            if remaining > 3:
                acc3 += bias
        output_base = (n * co + oc) * hw + spatial
        y[output_base] = nu_activate(acc0, act)
        if remaining > 1:
            y[output_base + 1] = nu_activate(acc1, act)
        if remaining > 2:
            y[output_base + 2] = nu_activate(acc2, act)
        if remaining > 3:
            y[output_base + 3] = nu_activate(acc3, act)


@ti.kernel
def nu_conv2d_depthwise_3x3_s1p1(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    plane = h * w_in
    for idx in range(n_batch * channels * plane):
        p = idx % plane
        c = (idx // plane) % channels
        n = idx // (plane * channels)
        yy = p // w_in
        xx = p % w_in
        acc = 0.0
        base = (n * channels + c) * plane
        wb = c * 9
        for ky in ti.static(range(3)):
            for kx in ti.static(range(3)):
                iy = yy + ky - 1
                ix = xx + kx - 1
                if 0 <= iy < h and 0 <= ix < w_in:
                    acc += x[base + iy * w_in + ix] * w[wb + ky * 3 + kx]
        if has_bias != 0:
            acc += b[c]
        y[idx] = nu_activate(acc, act)


@ti.kernel
def nu_conv_transpose2d(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    ci: ti.i32,
    co: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    kh: ti.i32,
    kw: ti.i32,
    sh: ti.i32,
    sw: ti.i32,
    ph: ti.i32,
    pw: ti.i32,
    dh: ti.i32,
    dw: ti.i32,
    group: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    ci_per_group = ci // group
    co_per_group = co // group
    plane = h * w_in
    for idx in range(n_batch * co * oh * ow):
        xx = idx % ow
        t = idx // ow
        yy = t % oh
        t2 = t // oh
        oc = t2 % co
        n = t2 // co
        group_id = oc // co_per_group
        acc = 0.0
        # ONNX ConvTranspose weight shape is [ci, co_per_group, kh, kw].
        w_base = group_id * ci_per_group * co_per_group * kh * kw + (oc % co_per_group) * kh * kw
        x_base = (n * ci + group_id * ci_per_group) * plane
        for ic in range(ci_per_group):
            for ky in range(kh):
                ty = yy + ph - ky * dh
                if ty >= 0 and ty % sh == 0:
                    iy = ty // sh
                    if iy < h:
                        for kx in range(kw):
                            tx = xx + pw - kx * dw
                            if tx >= 0 and tx % sw == 0:
                                ix = tx // sw
                                if ix < w_in:
                                    acc += (
                                        x[x_base + ic * plane + iy * w_in + ix]
                                        * w[w_base + ic * co_per_group * kh * kw + ky * kw + kx]
                                    )
        if has_bias != 0:
            acc += b[oc]
        y[idx] = nu_activate(acc, act)


ALL_CONV_KERNELS = [
    nu_conv2d,
    nu_conv2d_4x4_s2,
    nu_conv2d_4x4_s2_kahan_unrolled,
    nu_conv2d_4x4_s2_plain,
    nu_conv2d_3x3_s1p1,
    nu_conv2d_1x1,
    nu_conv2d_depthwise_3x3_s1p1,
    nu_conv_transpose2d,
]
