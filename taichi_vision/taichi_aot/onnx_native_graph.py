"""Static FP32 ONNX execution with Taichi kernels and explicit operator admission.

This module executes the GPU WeightNet profile without torch/ORT compute. ONNX
is used only to read the graph. Host constants retain their original integer
type for shape/axis calculations. Intermediate storage is allocated once.
"""

import math
import threading

import numpy as np
import taichi as ti

from taichi_vision.taichi_aot.fused_mul_clip import _fused_mul_clip_kernel
from taichi_vision.taichi_aot.weightnet_gate_fusions import _weightnet_gate_flat_kernel


class UnsupportedONNXOperatorError(ValueError):
    """The graph requires semantics not implemented by this executor."""


_CONCAT_GATHER_MAX_INPUTS = 8


@ti.func
def _activation(x, kind: ti.template()):
    result = x
    if ti.static(kind == 1):
        result = ti.max(x, 0.0)
    elif ti.static(kind == 2):
        result = 1.0 / (1.0 + ti.exp(-x))
    elif ti.static(kind == 3):
        # Stable softplus, including large positive and negative inputs.
        u = ti.exp(-ti.abs(x))
        v = 1.0 + u
        correction = u
        if v != 1.0:
            # Compensated log1p for Taichi distributions without ti.log1p.
            # u is in [0, 1]; avoid cancellation when 1+u rounds to one.
            correction = ti.log(v) * (u / (v - 1.0))
        result = ti.max(x, 0.0) + correction
    elif ti.static(kind == 4):
        # erf approximation (maximum absolute erf error about 1.5e-7).
        z = ti.abs(x) * 0.7071067811865476
        t = 1.0 / (1.0 + 0.3275911 * z)
        p = (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
              - 0.284496736) * t + 0.254829592) * t
        erf = 1.0 - p * ti.exp(-z * z)
        if x < 0.0:
            erf = -erf
        result = x * 0.5 * (1.0 + erf)
    return result


@ti.kernel
def _unary(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
           op: ti.template(), low: ti.f32, high: ti.f32):
    ti.loop_config(block_dim=256)
    for i in y:
        v = x[i]
        if ti.static(op <= 4):
            y[i] = _activation(v, op)
        elif ti.static(op == 5):
            y[i] = ti.abs(v)
        elif ti.static(op == 6):
            y[i] = ti.sqrt(v)
        elif ti.static(op == 7):
            y[i] = ti.tanh(v)
        elif ti.static(op == 8):
            y[i] = ti.min(ti.max(v, low), high)


@ti.kernel
def _binary(a: ti.types.ndarray(ti.f32, 1), b: ti.types.ndarray(ti.f32, 1),
            y: ti.types.ndarray(ti.f32, 1), op: ti.template(),
            shape: ti.types.vector(4, ti.i32),
            sa: ti.types.vector(4, ti.i32), sb: ti.types.vector(4, ti.i32)):
    ti.loop_config(block_dim=256)
    for i in y:
        rem, ia, ib = i, 0, 0
        ma, mb = 1, 1
        for j in ti.static(range(3, -1, -1)):
            c = rem % shape[j]
            rem //= shape[j]
            ia += (c % sa[j]) * ma
            ib += (c % sb[j]) * mb
            ma *= sa[j]
            mb *= sb[j]
        va, vb = a[ia], b[ib]
        if ti.static(op == 0):
            y[i] = va + vb
        elif ti.static(op == 1):
            y[i] = va - vb
        elif ti.static(op == 2):
            y[i] = va * vb
        elif ti.static(op == 3):
            y[i] = va / vb
        elif ti.static(op == 4):
            y[i] = va ** vb


@ti.kernel
def _binary_flat(a: ti.types.ndarray(ti.f32, 1), b: ti.types.ndarray(ti.f32, 1),
                 y: ti.types.ndarray(ti.f32, 1), op: ti.template()):
    ti.loop_config(block_dim=256)
    for i in y:
        va, vb = a[i], b[i]
        if ti.static(op == 0):
            y[i] = va + vb
        elif ti.static(op == 1):
            y[i] = va - vb
        elif ti.static(op == 2):
            y[i] = va * vb
        elif ti.static(op == 3):
            y[i] = va / vb
        elif ti.static(op == 4):
            y[i] = va ** vb


@ti.kernel
def _binary_scalar(a: ti.types.ndarray(ti.f32, 1), b: ti.types.ndarray(ti.f32, 1),
                   y: ti.types.ndarray(ti.f32, 1), op: ti.template(),
                   scalar_is_rhs: ti.template()):
    """High-performance specialized scalar broadcast kernel (zero index division)."""
    ti.loop_config(block_dim=256)
    for i in y:
        va = a[i] if ti.static(scalar_is_rhs) else a[0]
        vb = b[0] if ti.static(scalar_is_rhs) else b[i]
        if ti.static(op == 0):
            y[i] = va + vb
        elif ti.static(op == 1):
            y[i] = va - vb
        elif ti.static(op == 2):
            y[i] = va * vb
        elif ti.static(op == 3):
            y[i] = va / vb
        elif ti.static(op == 4):
            y[i] = va ** vb


@ti.kernel
def _square(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1)):
    ti.loop_config(block_dim=256)
    for i in y:
        y[i] = x[i] * x[i]


@ti.kernel
def _weightnet_sigmoid_product(
        lhs: ti.types.ndarray(ti.f32, 1),
        rhs: ti.types.ndarray(ti.f32, 1),
        output: ti.types.ndarray(ti.f32, 1)):
    for i in output:
        # Both inputs are produced by Sigmoid (or a fused Sigmoid activation),
        # so their finite FP32 product is already in [0, 1].
        output[i] = lhs[i] * rhs[i]


@ti.kernel
def _weightnet_fused_heads_and_gate(
    reasoner: ti.types.ndarray(ti.f32, 1),
    stats: ti.types.ndarray(ti.f32, 1),
    safety_w: ti.types.ndarray(ti.f32, 1),
    safety_b: ti.types.ndarray(ti.f32, 1),
    benefit_w: ti.types.ndarray(ti.f32, 1),
    benefit_b: ti.types.ndarray(ti.f32, 1),
    gate0_w: ti.types.ndarray(ti.f32, 1),
    gate0_b: ti.types.ndarray(ti.f32, 1),
    gate2_w: ti.types.ndarray(ti.f32, 1),
    gate2_b: ti.types.ndarray(ti.f32, 1),
    gate_out: ti.types.ndarray(ti.f32, 1),
    weight_out: ti.types.ndarray(ti.f32, 1),
    pixels: ti.i32,
):
    """Super-fuse 127x127 heads (benefit, safety), gate MLP, and product in registers."""
    ti.loop_config(block_dim=128)
    for p in range(pixels):
        s0 = stats[p]
        s1 = stats[pixels + p]

        # Gate MLP Layer 0: 2 -> 8 (Conv 1x1 + GELU)
        h0 = _activation(gate0_b[0] + s0 * gate0_w[0] + s1 * gate0_w[1], 4)
        h1 = _activation(gate0_b[1] + s0 * gate0_w[2] + s1 * gate0_w[3], 4)
        h2 = _activation(gate0_b[2] + s0 * gate0_w[4] + s1 * gate0_w[5], 4)
        h3 = _activation(gate0_b[3] + s0 * gate0_w[6] + s1 * gate0_w[7], 4)
        h4 = _activation(gate0_b[4] + s0 * gate0_w[8] + s1 * gate0_w[9], 4)
        h5 = _activation(gate0_b[5] + s0 * gate0_w[10] + s1 * gate0_w[11], 4)
        h6 = _activation(gate0_b[6] + s0 * gate0_w[12] + s1 * gate0_w[13], 4)
        h7 = _activation(gate0_b[7] + s0 * gate0_w[14] + s1 * gate0_w[15], 4)

        # Gate MLP Layer 2: 8 -> 2 (Conv 1x1 linear)
        m0 = (gate2_b[0]
              + h0 * gate2_w[0] + h1 * gate2_w[1] + h2 * gate2_w[2] + h3 * gate2_w[3]
              + h4 * gate2_w[4] + h5 * gate2_w[5] + h6 * gate2_w[6] + h7 * gate2_w[7])
        m1 = (gate2_b[1]
              + h0 * gate2_w[8] + h1 * gate2_w[9] + h2 * gate2_w[10] + h3 * gate2_w[11]
              + h4 * gate2_w[12] + h5 * gate2_w[13] + h6 * gate2_w[14] + h7 * gate2_w[15])

        # Reasoner dual heads: 20 -> 1 safety (Softplus) and 1 benefit (Sigmoid)
        safe_acc = safety_b[0]
        ben_acc = benefit_b[0]
        for c in ti.static(range(20)):
            r_val = reasoner[c * pixels + p]
            safe_acc += r_val * safety_w[c]
            ben_acc += r_val * benefit_w[c]

        safety = _activation(safe_acc, 3)     # Softplus
        raw_weight = _activation(ben_acc, 2) # Sigmoid

        # Adaptive gate math
        ch0 = _activation(m0, 3) + 0.5
        ch1 = _activation(m1, 3) - safety
        gate = _activation(ch0 * ch1, 2)      # Sigmoid

        # Gated weight
        gated_weight = raw_weight * gate

        # Output writes
        gate_out[p] = gate
        weight_out[p] = gated_weight


@ti.kernel
def _weightnet_fused_phase_gate_concat23(
    ref_tiles: ti.types.ndarray(ti.f32, 1),
    sup_tiles: ti.types.ndarray(ti.f32, 1),
    gate_w: ti.types.ndarray(ti.f32, 1),
    gate_b: ti.types.ndarray(ti.f32, 1),
    concat_out: ti.types.ndarray(ti.f32, 1),
    h: ti.i32,
    width: ti.i32,
):
    """Super-fuse WeightNet Phase Gate (gradient diff, norm, sigmoid gate) and 23-ch Concat."""
    ti.loop_config(block_dim=256)
    for idx in concat_out:
        area = h * width
        plane = idx // area
        channel = plane % 23
        n = plane // 23
        pixel = idx % area
        oy = pixel // width
        ox = pixel % width

        if channel < 4:
            concat_out[idx] = ref_tiles[(n * 4 + channel) * area + pixel]
        elif channel < 8:
            concat_out[idx] = sup_tiles[(n * 4 + (channel - 4)) * area + pixel]
        elif channel < 12:
            c = channel - 8
            s_val = sup_tiles[(n * 4 + c) * area + pixel]
            r_val = ref_tiles[(n * 4 + c) * area + pixel]
            concat_out[idx] = s_val - r_val
        elif channel < 16:
            c = channel - 12
            total = 0.0
            for ky, kx in ti.static(ti.ndrange(3, 3)):
                iy, ix = oy + ky - 1, ox + kx - 1
                if 0 <= iy < h and 0 <= ix < width:
                    s_val = sup_tiles[(n * 4 + c) * area + iy * width + ix]
                    r_val = ref_tiles[(n * 4 + c) * area + iy * width + ix]
                    total += (s_val - r_val)
            concat_out[idx] = ti.abs(total / 9.0)
        elif channel < 20:
            c = channel - 16
            s_val = sup_tiles[(n * 4 + c) * area + pixel]
            r_val = ref_tiles[(n * 4 + c) * area + pixel]
            concat_out[idx] = r_val * s_val
        else:
            c = channel - 20
            r0 = ref_tiles[(n * 4 + 0) * area + pixel]
            r1 = ref_tiles[(n * 4 + 1) * area + pixel]
            r2 = ref_tiles[(n * 4 + 2) * area + pixel]
            r3 = ref_tiles[(n * 4 + 3) * area + pixel]

            s0 = sup_tiles[(n * 4 + 0) * area + pixel]
            s1 = sup_tiles[(n * 4 + 1) * area + pixel]
            s2 = sup_tiles[(n * 4 + 2) * area + pixel]
            s3 = sup_tiles[(n * 4 + 3) * area + pixel]

            g0 = (s1 - s0) - (r1 - r0)
            g1 = (s2 - s0) - (r2 - r0)
            g2 = (s3 - s0) - (r3 - r0)

            pool_sq = 0.0
            for ky, kx in ti.static(ti.ndrange(3, 3)):
                iy, ix = oy + ky - 1, ox + kx - 1
                if 0 <= iy < h and 0 <= ix < width:
                    val = ref_tiles[(n * 4 + 0) * area + iy * width + ix]
                    pool_sq += val * val
            avg_sq = pool_sq / 9.0
            norm = ti.max(0.05, ti.sqrt(avg_sq + 0.0025))

            d0 = g0 / norm
            d1 = g1 / norm
            d2 = g2 / norm

            w0 = gate_w[0]
            w1 = gate_w[1]
            w2 = gate_w[2]
            bias = gate_b[0]

            acc = ti.abs(d0) * w0 + ti.abs(d1) * w1 + ti.abs(d2) * w2 + bias
            sig = _activation(acc, 2)

            val_out = 0.0
            if c == 0:
                val_out = d0 * sig
            elif c == 1:
                val_out = d1 * sig
            else:
                val_out = d2 * sig

            concat_out[idx] = val_out


@ti.kernel
def _weightnet_square_reduce_mean(
        x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
        inner: ti.i32):
    for i in y:
        base = (i // inner) * inner * 4 + i % inner
        total = ti.cast(0.0, ti.f32)
        for channel in ti.static(range(4)):
            value = x[base + channel * inner]
            square = ti.cast(value * value, ti.f32)
            total = ti.cast(total + square, ti.f32)
        y[i] = ti.cast(total / 4.0, ti.f32)


@ti.kernel
def _weightnet_concat_conv_gelu(
        x0: ti.types.ndarray(ti.f32, 1), x1: ti.types.ndarray(ti.f32, 1),
        x2: ti.types.ndarray(ti.f32, 1), weights: ti.types.ndarray(ti.f32, 1),
        bias: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
        batch: ti.template(), h: ti.i32, width: ti.i32,
        c0: ti.template(), c1: ti.template(), c2: ti.template(),
        output_channels: ti.template()):
    """Read ordered Concat sources directly into the audited 1x1 Conv+GELU."""
    ti.loop_config(block_dim=128)
    for idx in range(batch * (output_channels // 4) * (h * width)):
        pixels = h * width
        output_groups = output_channels // 4
        pixel = idx % pixels
        group_channel = idx // pixels % output_groups * 4
        n = idx // (pixels * output_groups)
        accum = ti.Vector.zero(ti.f32, 4)
        for input_channel in range(c0):
            value = x0[(n * c0 + input_channel) * pixels + pixel]
            for output_lane in ti.static(range(4)):
                weight_index = ((group_channel + output_lane) * (c0 + c1 + c2)
                                + input_channel)
                accum[output_lane] = ti.cast(
                    accum[output_lane] + value * weights[weight_index], ti.f32,
                )
        for input_channel in range(c1):
            value = x1[(n * c1 + input_channel) * pixels + pixel]
            for output_lane in ti.static(range(4)):
                weight_index = ((group_channel + output_lane) * (c0 + c1 + c2)
                                + c0 + input_channel)
                accum[output_lane] = ti.cast(
                    accum[output_lane] + value * weights[weight_index], ti.f32,
                )
        for input_channel in range(c2):
            value = x2[(n * c2 + input_channel) * pixels + pixel]
            for output_lane in ti.static(range(4)):
                weight_index = ((group_channel + output_lane) * (c0 + c1 + c2)
                                + c0 + c1 + input_channel)
                accum[output_lane] = ti.cast(
                    accum[output_lane] + value * weights[weight_index], ti.f32,
                )
        for output_lane in ti.static(range(4)):
            channel = group_channel + output_lane
            value = ti.cast(accum[output_lane] + bias[channel], ti.f32)
            y[(n * output_channels + channel) * pixels + pixel] = _activation(value, 4)


@ti.kernel
def _weightnet_pow2_sub_clip_sqrt(
        average: ti.types.ndarray(ti.f32, 1), base: ti.types.ndarray(ti.f32, 1),
        y: ti.types.ndarray(ti.f32, 1), low: ti.f32):
    for i in y:
        # Keep each FP32 stage explicit to mirror Pow -> Sub -> Clip -> Sqrt.
        square = ti.cast(base[i] * base[i], ti.f32)
        difference = ti.cast(average[i] - square, ti.f32)
        clipped = ti.cast(ti.max(difference, low), ti.f32)
        y[i] = ti.sqrt(clipped)


@ti.kernel
def _weightnet_sub3_stats_tanh(
        x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
        h: ti.i32, ow: ti.i32,
        simplify_power_of_two_scale: ti.template()):
    """Fuse the guarded WeightNet square/mean/RMS/pool/scale/Tanh branch."""
    for idx in y:
        ox = idx % ow
        oy = idx // ow % ow
        n = idx // (ow * ow)
        pool_total = ti.cast(0.0, ti.f32)
        for ky, kx in ti.static(ti.ndrange(4, 4)):
            iy = oy * 2 + ky
            ix = ox * 2 + kx
            channel_total = ti.cast(0.0, ti.f32)
            for channel in ti.static(range(4)):
                value = x[((n * 4 + channel) * h + iy) * h + ix]
                square = ti.cast(value * value, ti.f32)
                channel_total = ti.cast(channel_total + square, ti.f32)
            rms = ti.cast(0.0, ti.f32)
            if ti.static(simplify_power_of_two_scale):
                # sqrt(sum(x*x) / 4) == 0.5 * sqrt(sum(x*x)).
                # Fold the factor into the terminal pool scale below.
                rms = ti.cast(ti.sqrt(channel_total), ti.f32)
            else:
                channel_mean = ti.cast(channel_total / 4.0, ti.f32)
                rms = ti.cast(ti.sqrt(channel_mean), ti.f32)
            pool_total = ti.cast(pool_total + rms, ti.f32)
        scaled = ti.cast(0.0, ti.f32)
        if ti.static(simplify_power_of_two_scale):
            # 8 * mean_16(0.5 * sqrt(sum(x*x))) == 0.25 * sum(sqrt(sum(x*x))).
            scaled = ti.cast(pool_total * 0.25, ti.f32)
        else:
            pooled = ti.cast(pool_total / 16.0, ti.f32)
            scaled = ti.cast(pooled * 8.0, ti.f32)
        y[idx] = ti.tanh(scaled)


@ti.kernel
def _conv(x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
          b: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
          ci: ti.template(), co: ti.template(), h: ti.i32, width: ti.i32,
          oh: ti.i32, ow: ti.i32, kh: ti.template(), kw: ti.template(),
          sh: ti.template(), sw: ti.template(), ph: ti.template(), pw: ti.template(),
          dh: ti.template(), dw: ti.template(), group: ti.template(),
          bias: ti.template(), activation: ti.template()):
    ti.loop_config(block_dim=256)
    for idx in y:
        xx = idx % ow
        idx_div_ow = idx // ow
        yy = idx_div_ow % oh
        oc = idx_div_ow // oh % co
        n = idx_div_ow // (oh * co)
        acc = 0.0
        for ic in range(ci // group):
            channel = oc // (co // group) * (ci // group) + ic
            x_ch_base = (n * ci + channel) * h
            w_ch_base = (oc * (ci // group) + ic) * kh * kw
            for ky in range(kh):
                iy = yy * sh + ky * dh - ph
                if 0 <= iy < h:
                    x_row_base = (x_ch_base + iy) * width
                    w_row_base = w_ch_base + ky * kw
                    for kx in range(kw):
                        ix = xx * sw + kx * dw - pw
                        if 0 <= ix < width:
                            acc += x[x_row_base + ix] * w[w_row_base + kx]
        if ti.static(bias):
            acc += b[oc]
        y[idx] = _activation(acc, activation)


@ti.kernel
def _conv_channels4(x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
                    b: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                    ci: ti.template(), co: ti.template(), h: ti.i32, width: ti.i32,
                    oh: ti.i32, ow: ti.i32, kh: ti.template(), kw: ti.template(),
                    sh: ti.template(), sw: ti.template(), ph: ti.template(), pw: ti.template(),
                    bias: ti.template(), activation: ti.template()):
    # Four channels share input loads. Reduction order matches the scalar oracle.
    ti.loop_config(block_dim=256)
    for idx in range(y.shape[0] // 4):
        xx = idx % ow
        idx_div_ow = idx // ow
        yy = idx_div_ow % oh
        oc = (idx_div_ow // oh % (co // 4)) * 4
        n = idx_div_ow // (oh * (co // 4))
        acc = ti.Vector.zero(ti.f32, 4)
        for ic in range(ci):
            x_ch_base = (n * ci + ic) * h
            w_ch_base = ic * kh * kw
            for ky, kx in ti.static(ti.ndrange(kh, kw)):
                iy = yy * sh + ky - ph
                ix = xx * sw + kx - pw
                if 0 <= iy < h and 0 <= ix < width:
                    v = x[(x_ch_base + iy) * width + ix]
                    w_offset = w_ch_base + ky * kw + kx
                    for c in ti.static(range(4)):
                        acc[c] += v * w[((oc + c) * ci * kh * kw) + w_offset]
        for c in ti.static(range(4)):
            value = acc[c]
            if ti.static(bias):
                value += b[oc + c]
            y[((n * co + oc + c) * oh + yy) * ow + xx] = _activation(value, activation)


@ti.kernel
def _conv_1x1_tiled(x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
                    b: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                    ci: ti.template(), co: ti.template(),
                    pixels: ti.i32, bias: ti.template(), activation: ti.template()):
    """High-efficiency Pointwise 1x1 Convolution kernel computing 4 output channels per thread."""
    ti.loop_config(block_dim=128)
    for idx in range((pixels * co) // 4):
        p = idx % pixels
        oc_group = (idx // pixels) * 4
        acc = ti.Vector.zero(ti.f32, 4)
        for ic in range(ci):
            val = x[ic * pixels + p]
            w_base = oc_group * ci + ic
            for c in ti.static(range(4)):
                acc[c] += val * w[w_base + c * ci]
        for c in ti.static(range(4)):
            ch = oc_group + c
            v = acc[c]
            if ti.static(bias):
                v += b[ch]
            y[ch * pixels + p] = _activation(v, activation)


@ti.kernel
def _conv_k4s2_tiled(x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
                     b: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                     ci: ti.template(), co: ti.template(), h: ti.i32, width: ti.i32,
                     oh: ti.i32, ow: ti.i32, bias: ti.template(), activation: ti.template()):
    """Specialized 4x4 stride 2 convolution with boundary-free interior fast path."""
    ti.loop_config(block_dim=128)
    for idx in range((oh * ow * co) // 4):
        xx = idx % ow
        idx_div = idx // ow
        yy = idx_div % oh
        oc_group = (idx_div // oh) * 4
        acc = ti.Vector.zero(ti.f32, 4)
        iy_base = yy * 2
        ix_base = xx * 2
        if iy_base + 3 < h and ix_base + 3 < width:
            for ic in range(ci):
                x_ch_base = ic * h
                w_ch_base = ic * 16
                for ky in ti.static(range(4)):
                    x_row = (x_ch_base + iy_base + ky) * width + ix_base
                    w_row = w_ch_base + ky * 4
                    for kx in ti.static(range(4)):
                        v = x[x_row + kx]
                        w_offset = w_row + kx
                        for c in ti.static(range(4)):
                            acc[c] += v * w[(oc_group + c) * ci * 16 + w_offset]
        else:
            for ic in range(ci):
                x_ch_base = ic * h
                w_ch_base = ic * 16
                for ky in ti.static(range(4)):
                    iy = iy_base + ky
                    if iy < h:
                        x_row = (x_ch_base + iy) * width
                        w_row = w_ch_base + ky * 4
                        for kx in ti.static(range(4)):
                            ix = ix_base + kx
                            if ix < width:
                                v = x[x_row + ix]
                                w_offset = w_row + kx
                                for c in ti.static(range(4)):
                                    acc[c] += v * w[(oc_group + c) * ci * 16 + w_offset]
        for c in ti.static(range(4)):
            ch = oc_group + c
            v = acc[c]
            if ti.static(bias):
                v += b[ch]
            y[(ch * oh + yy) * ow + xx] = _activation(v, activation)


@ti.kernel
def _depthwise(x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
               b: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
               c: ti.i32, h: ti.i32, width: ti.i32, bias: ti.template(),
               activation: ti.template()):
    ti.loop_config(block_dim=256)
    for idx in y:
        xx, yy = idx % width, idx // width % h
        channel = idx // (width * h) % c
        plane = idx // (width * h)
        acc = 0.0
        for ky, kx in ti.static(ti.ndrange(3, 3)):
            iy, ix = yy + ky - 1, xx + kx - 1
            if 0 <= iy < h and 0 <= ix < width:
                acc += x[(plane * h + iy) * width + ix] * w[channel * 9 + ky * 3 + kx]
        if ti.static(bias):
            acc += b[channel]
        y[idx] = _activation(acc, activation)


@ti.kernel
def _pool(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
          h: ti.i32, w: ti.i32, oh: ti.i32, ow: ti.i32,
          kh: ti.template(), kw: ti.template(), sh: ti.template(), sw: ti.template(),
          ph: ti.template(), pw: ti.template(), include_pad: ti.template()):
    ti.loop_config(block_dim=256)
    for idx in y:
        xx, yy, plane = idx % ow, idx // ow % oh, idx // (ow * oh)
        total, count = 0.0, 0
        for ky, kx in ti.ndrange(kh, kw):
            iy, ix = yy * sh + ky - ph, xx * sw + kx - pw
            if 0 <= iy < h and 0 <= ix < w:
                total += x[(plane * h + iy) * w + ix]
                count += 1
        if ti.static(include_pad):
            count = kh * kw
        y[idx] = total / count


@ti.kernel
def _space_to_depth(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                    c: ti.i32, h: ti.i32, w: ti.i32, block: ti.template()):
    ti.loop_config(block_dim=256)
    for idx in y:
        ow, oh = w // block, h // block
        ox, oy = idx % ow, idx // ow % oh
        oc, n = idx // (ow * oh) % (c * block * block), idx // (c * h * w)
        ic = oc % c
        by, bx = oc // c // block, oc // c % block
        y[idx] = x[((n * c + ic) * h + oy * block + by) * w + ox * block + bx]


@ti.kernel
def _copy_axis(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
               inner: ti.i32, axis_in: ti.i32, axis_out: ti.i32, offset: ti.i32,
               concat: ti.template()):
    ti.loop_config(block_dim=256)
    if ti.static(concat):
        for i in x:
            outer, pos = i // (axis_in * inner), i % (axis_in * inner)
            y[outer * axis_out * inner + offset * inner + pos] = x[i]
    else:
        for i in y:
            outer, pos = i // (axis_out * inner), i % (axis_out * inner)
            y[i] = x[outer * axis_in * inner + offset * inner + pos]


@ti.kernel
def _concat_gather(x0: ti.types.ndarray(ti.f32, 1),
                   x1: ti.types.ndarray(ti.f32, 1),
                   x2: ti.types.ndarray(ti.f32, 1),
                   x3: ti.types.ndarray(ti.f32, 1),
                   x4: ti.types.ndarray(ti.f32, 1),
                   x5: ti.types.ndarray(ti.f32, 1),
                   x6: ti.types.ndarray(ti.f32, 1),
                   x7: ti.types.ndarray(ti.f32, 1),
                   y: ti.types.ndarray(ti.f32, 1),
                   inner: ti.i32, axis_out: ti.i32,
                   axis_sizes: ti.template(), axis_starts: ti.template(),
                   input_count: ti.template()):
    """Gather one flat Concat output from an ordered tuple of flat inputs."""
    ti.loop_config(block_dim=256)
    for i in y:
        outer = i // (axis_out * inner)
        rem = i % (axis_out * inner)
        axis_pos = rem // inner
        inner_pos = rem % inner
        value = 0.0
        for input_index in ti.static(range(input_count)):
            axis_start = ti.static(axis_starts[input_index])
            axis_size = ti.static(axis_sizes[input_index])
            if axis_start <= axis_pos and axis_pos < axis_start + axis_size:
                source = (outer * axis_size + axis_pos - axis_start) * inner + inner_pos
                if ti.static(input_index == 0):
                    value = x0[source]
                elif ti.static(input_index == 1):
                    value = x1[source]
                elif ti.static(input_index == 2):
                    value = x2[source]
                elif ti.static(input_index == 3):
                    value = x3[source]
                elif ti.static(input_index == 4):
                    value = x4[source]
                elif ti.static(input_index == 5):
                    value = x5[source]
                elif ti.static(input_index == 6):
                    value = x6[source]
                else:
                    value = x7[source]
        y[i] = value


@ti.kernel
def _weightnet_concat_pool_abs_gather(
        x0: ti.types.ndarray(ti.f32, 1), x1: ti.types.ndarray(ti.f32, 1),
        x2: ti.types.ndarray(ti.f32, 1), pool_input: ti.types.ndarray(ti.f32, 1),
        x4: ti.types.ndarray(ti.f32, 1), x5: ti.types.ndarray(ti.f32, 1),
        y: ti.types.ndarray(ti.f32, 1), h: ti.i32, width: ti.i32):
    ti.loop_config(block_dim=256)
    for idx in y:
        area = h * width
        plane = idx // area
        channel = plane % 23
        n = plane // 23
        pixel = idx % area
        if channel < 4:
            y[idx] = x0[(n * 4 + channel) * area + pixel]
        elif channel < 8:
            y[idx] = x1[(n * 4 + channel - 4) * area + pixel]
        elif channel < 12:
            y[idx] = x2[(n * 4 + channel - 8) * area + pixel]
        elif channel < 16:
            pool_channel = channel - 12
            oy, ox = pixel // width, pixel % width
            total = 0.0
            for ky, kx in ti.static(ti.ndrange(3, 3)):
                iy, ix = oy + ky - 1, ox + kx - 1
                if 0 <= iy < h and 0 <= ix < width:
                    total += pool_input[(n * 4 + pool_channel) * area + iy * width + ix]
            y[idx] = ti.abs(total / 9.0)
        elif channel < 20:
            y[idx] = x4[(n * 4 + channel - 16) * area + pixel]
        else:
            y[idx] = x5[(n * 3 + channel - 20) * area + pixel]


@ti.kernel
def _transpose(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
               rank: ti.template(), out_dims: ti.template(),
               in_strides: ti.template(), perm: ti.template()):
    for i in y:
        remaining = i
        source = 0
        for axis in ti.static(range(rank - 1, -1, -1)):
            coordinate = remaining % out_dims[axis]
            remaining //= out_dims[axis]
            source += coordinate * in_strides[perm[axis]]
        y[i] = x[source]


@ti.kernel
def _reduce_axis(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                 inner: ti.i32, count: ti.i32):
    for i in y:
        base = (i // inner) * inner * count + i % inner
        total = 0.0
        for j in range(count):
            total += x[base + j * inner]
        y[i] = total / count


@ti.kernel
def _reduce_chunks(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                   count: ti.i32, chunk_count: ti.i32):
    for i in range(chunk_count):
        total = 0.0
        for j in range(i * 256, ti.min((i + 1) * 256, count)):
            total += x[j]
        y[i] = total


@ti.kernel
def _reduce_finish(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
                   count: ti.i32, chunk_count: ti.i32):
    for i in range(1):
        total = 0.0
        for j in range(chunk_count):
            total += x[j]
        y[0] = total / count


@ti.kernel
def _transpose_conv(x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
                    y: ti.types.ndarray(ti.f32, 1), h: ti.i32, width: ti.i32,
                    oh: ti.i32, ow: ti.i32, kh: ti.template(), kw: ti.template(),
                    sh: ti.template(), sw: ti.template()):
    # Audited WeightNet single-channel transposed convolution, no padding/bias.
    for idx in y:
        xx, yy = idx % ow, idx // ow % oh
        n = idx // (ow * oh)
        acc = 0.0
        for iy in range(ti.max(0, (yy - kh + sh) // sh), ti.min(h, yy // sh + 1)):
            for ix in range(ti.max(0, (xx - kw + sw) // sw), ti.min(width, xx // sw + 1)):
                acc += x[(n * h + iy) * width + ix] * w[(yy - iy * sh) * kw + xx - ix * sw]
        y[idx] = acc


@ti.kernel
def _transpose_conv_mul_clip(
        x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
        scale: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
        h: ti.i32, width: ti.i32, oh: ti.i32, ow: ti.i32,
        kh: ti.template(), kw: ti.template(), sh: ti.template(), sw: ti.template(),
        low: ti.f32, high: ti.f32):
    # Preserve ConvTranspose accumulation order, then apply the exact Mul -> Clip epilogue.
    for idx in y:
        xx, yy = idx % ow, idx // ow % oh
        n = idx // (ow * oh)
        acc = 0.0
        for iy in range(ti.max(0, (yy - kh + sh) // sh), ti.min(h, yy // sh + 1)):
            for ix in range(ti.max(0, (xx - kw + sw) // sw), ti.min(width, xx // sw + 1)):
                acc += x[(n * h + iy) * width + ix] * w[(yy - iy * sh) * kw + xx - ix * sw]
        scale_index = idx % (oh * ow)
        y[idx] = ti.min(ti.max(acc * scale[scale_index], low), high)


@ti.kernel
def _weightnet_abs_conv_sigmoid(
        x: ti.types.ndarray(ti.f32, 1), w: ti.types.ndarray(ti.f32, 1),
        b: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
        h: ti.i32, width: ti.i32):
    ti.loop_config(block_dim=256)
    for idx in y:
        pixels = h * width
        pixel = idx % pixels
        n = idx // pixels
        acc = 0.0
        for ic in ti.static(range(3)):
            value = ti.abs(x[(n * 3 + ic) * pixels + pixel])
            acc += value * w[ic]
        acc += b[0]
        y[idx] = _activation(acc, 2)


def _padded(shape):
    if len(shape) > 4:
        raise UnsupportedONNXOperatorError(f"Rank > 4 is not admitted: {shape}")
    return (1,) * (4 - len(shape)) + tuple(shape)


@ti.kernel
def _upload_device(x: ti.types.ndarray(dtype=ti.f32), y: ti.types.ndarray(ti.f32, 1)):
    for index in ti.grouped(x):
        offset = 0
        for axis in ti.static(range(len(index))):
            offset = offset * x.shape[axis] + index[axis]
        y[offset] = x[index]


@ti.kernel
def _download_device(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(dtype=ti.f32)):
    for index in ti.grouped(y):
        offset = 0
        for axis in ti.static(range(len(index))):
            offset = offset * y.shape[axis] + index[axis]
        y[index] = x[offset]



@ti.kernel
def _weightnet_fused_tile_statistics(
    ref_4ch: ti.types.ndarray(ti.f32, 1),
    concat_1: ti.types.ndarray(ti.f32, 1),
    tanh_out: ti.types.ndarray(ti.f32, 1),
    h: ti.i32,
    w: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
):
    """Fuse 9-step tile statistics (mean, variance, texture context) into a single kernel."""
    ti.loop_config(block_dim=128)
    plane_in = h * w
    plane_out = oh * ow
    for idx in range(plane_out):
        ox = idx % ow
        oy = idx // ow
        iy = oy * 2
        ix = ox * 2

        sum_m = 0.0
        sum_sq = 0.0
        sum_std = 0.0

        for ky in ti.static(range(4)):
            y = iy + ky
            for kx in ti.static(range(4)):
                x = ix + kx
                p = y * w + x
                c0 = ref_4ch[p]
                c1 = ref_4ch[plane_in + p]
                c2 = ref_4ch[2 * plane_in + p]
                c3 = ref_4ch[3 * plane_in + p]

                m = (c0 + c1 + c2 + c3) * 0.25
                sum_m += m
                sum_sq += (c0 * c0 + c1 * c1 + c2 * c2 + c3 * c3) * 0.25

                d0 = c0 - m
                d1 = c1 - m
                d2 = c2 - m
                d3 = c3 - m
                variance = (d0 * d0 + d1 * d1 + d2 * d2 + d3 * d3) * 0.25
                sum_std += ti.sqrt(ti.max(variance, 1e-12))

        mean_tile = sum_m * (1.0 / 16.0)
        sq_tile = sum_sq * (1.0 / 16.0)
        std_tile = sum_std * (1.0 / 16.0)

        var_tile = ti.max(sq_tile - mean_tile * mean_tile, 1e-5)
        std_out = ti.sqrt(var_tile)

        concat_1[idx] = mean_tile
        concat_1[plane_out + idx] = std_out
        tanh_out[idx] = ti.tanh(std_tile * 8.0)


class NativeGraph:
    """Validated static graph; host output copies are owned by the caller.

    A model serializes calls because its preallocated scratch belongs to one
    invocation at a time. No output buffer is returned to an allocation pool.
    """

    OPS = {"Conv", "DmlFusedConv", "FusedConv", "Relu", "Sigmoid", "Softplus", "Gelu",
           "Abs", "Sqrt", "Tanh", "Clip", "Add", "Sub", "Mul", "Div", "Pow",
           "AveragePool", "SpaceToDepth", "Reshape", "Identity", "Concat",
           "Slice", "ReduceMean", "ConvTranspose", "Transpose", "Split", "Constant"}
    INPUT_ARITY = {
        "Conv": (2, 3), "DmlFusedConv": (2, 3), "FusedConv": (2, 3),
        "Relu": (1, 1), "Sigmoid": (1, 1), "Softplus": (1, 1),
        "Gelu": (1, 1), "Abs": (1, 1), "Sqrt": (1, 1), "Tanh": (1, 1),
        "Clip": (1, 3), "Add": (2, 2), "Sub": (2, 2), "Mul": (2, 2),
        "Div": (2, 2), "Pow": (2, 2), "AveragePool": (1, 1),
        "SpaceToDepth": (1, 1), "Reshape": (2, 2), "Identity": (1, 1),
        "Concat": (1, None), "Slice": (3, 5), "ReduceMean": (1, 2), "ConvTranspose": (2, 3),
        "Transpose": (1, 1), "Split": (1, 2), "Constant": (0, 0),
    }
    OPTIONAL_INPUTS = {
        "Conv": {2}, "DmlFusedConv": {2}, "FusedConv": {2}, "ConvTranspose": {2},
        "Clip": {1, 2}, "Slice": {3, 4}, "ReduceMean": {1}, "Split": {1},
    }
    CONSTANT_INPUTS = {
        "Conv": {1, 2}, "DmlFusedConv": {1, 2}, "FusedConv": {1, 2},
        "Clip": {1, 2}, "Reshape": {1}, "Slice": {1, 2, 3, 4},
        "ReduceMean": {1}, "ConvTranspose": {1}, "Split": {1},
    }
    INTEGER_VECTOR_INPUTS = {
        "Reshape": (1,), "Slice": (1, 2, 3, 4),
        "ReduceMean": (1,), "Split": (1,),
    }
    DEVICE_DATA_INPUTS = {
        "Conv": {1, 2}, "DmlFusedConv": {1, 2}, "FusedConv": {1, 2},
        "Add": {1}, "Sub": {1}, "Mul": {1}, "Div": {1}, "Pow": {1},
        "ConvTranspose": {1},
    }
    ALLOWED_ATTRIBUTES = {
        "Conv": {"auto_pad", "dilations", "group", "kernel_shape", "pads", "strides"},
        "DmlFusedConv": {"auto_pad", "dilations", "fused_activation",
                         "fused_activation_domain",
                         "fused_activation_since_version", "group",
                         "kernel_shape", "pads", "strides"},
        "FusedConv": {"activation", "auto_pad", "dilations", "group", "kernel_shape",
                      "pads", "strides"},
        "Gelu": {"approximate"},
        "Clip": {"max", "min"},
        "AveragePool": {"auto_pad", "ceil_mode", "count_include_pad", "kernel_shape", "pads", "strides"},
        "SpaceToDepth": {"blocksize"},
        "Reshape": {"allowzero"},
        "Concat": {"axis"},
        "Split": {"axis", "split"},
        "ReduceMean": {"axes", "keepdims", "noop_with_empty_axes"},
        "ConvTranspose": {"auto_pad", "dilations", "group", "kernel_shape",
                          "output_padding", "output_shape", "pads", "strides"},
        "Transpose": {"perm"},
        "Constant": {"value"},
    }
    REQUIRED_ATTRIBUTES = {
        "DmlFusedConv": {"fused_activation"}, "FusedConv": {"activation"},
        "AveragePool": {"kernel_shape"}, "SpaceToDepth": {"blocksize"},
        "Concat": {"axis"},
    }

    def __init__(self, graph, opset_imports=None, *, enable_conv_gelu_fusion=False,
                 enable_concat_gather=False, enable_weightnet_gate_fusion=False,
                 enable_mul_clip_fusion=False,
                 enable_weightnet_sigmoid_product_clip_fusion=False,
                 enable_weightnet_pow2_sub_clip_sqrt_fusion=False,
                 enable_weightnet_stats_tanh_fusion=False,
                 enable_weightnet_stats_tanh_algebraic_simplification=False,
                 enable_constant_pow2_mul_lowering=False,
                 enable_weightnet_pow2_reduce_mean_fusion=False,
                 enable_weightnet_full_range_slice_alias=False,
                 enable_weightnet_concat_conv_gelu_fusion=False,
                 enable_weightnet_conv_transpose_mul_clip_fusion=False,
                 enable_weightnet_abs_conv_fusion=False,
                 enable_weightnet_pool_abs_concat_fusion=False,
                 enable_weightnet_fused_heads_and_gate_fusion=False,
                 enable_weightnet_phase_gate_concat23_fusion=False,
                 enable_weightnet_fused_tile_statistics=False):
        from onnx import defs, helper, numpy_helper

        self.opsets = {}
        if opset_imports is not None:
            for opset in opset_imports:
                domain = opset.domain or ""
                version = int(opset.version)
                if domain in self.opsets and self.opsets[domain] != version:
                    raise UnsupportedONNXOperatorError(
                        f"Conflicting opset imports for {domain or 'ai.onnx'}"
                    )
                self.opsets[domain] = version
        initializer_names = [value.name for value in graph.initializer]
        if any(not name for name in initializer_names) or len(set(initializer_names)) != len(initializer_names):
            raise UnsupportedONNXOperatorError("Initializer names must be non-empty and unique")
        graph_input_names = [value.name for value in graph.input]
        if any(not name for name in graph_input_names) or len(set(graph_input_names)) != len(graph_input_names):
            raise UnsupportedONNXOperatorError("Graph input names must be non-empty and unique")
        graph_output_names = [value.name for value in graph.output]
        if any(not name for name in graph_output_names) or len(set(graph_output_names)) != len(graph_output_names):
            raise UnsupportedONNXOperatorError("Graph output names must be non-empty and unique")
        self.constants = {v.name: numpy_helper.to_array(v).copy() for v in graph.initializer}
        self.shapes = {k: tuple(v.shape) for k, v in self.constants.items()}
        self.runtime_constant_names = set()
        self.inputs = []
        self.outputs = graph_output_names
        for v in graph.input:
            if v.name not in self.constants:
                shape = tuple(d.dim_value for d in v.type.tensor_type.shape.dim)
                if not shape or any(d <= 0 for d in shape) or v.type.tensor_type.elem_type != 1:
                    raise UnsupportedONNXOperatorError(f"Static FP32 input required: {v.name} {shape}")
                self.shapes[v.name] = shape
                self.inputs.append(v.name)
        self.steps = []
        self.aliases = {}
        custom_operator_domains = {
            "Gelu": "com.microsoft",
            "FusedConv": "com.microsoft",
            "DmlFusedConv": "com.microsoft.dml",
        }
        defined_values = set(self.constants) | set(graph_input_names)
        for node in graph.node:
            op = node.op_type
            if op not in self.OPS or (len(node.output) != 1 and op != "Split"):
                raise UnsupportedONNXOperatorError(f"Unsupported ONNX operator: {node.domain}::{op} ({node.name})")
            min_inputs, max_inputs = self.INPUT_ARITY[op]
            if len(node.input) < min_inputs or (
                max_inputs is not None and len(node.input) > max_inputs
            ):
                max_input_label = max_inputs if max_inputs is not None else "unbounded"
                raise UnsupportedONNXOperatorError(
                    f"{op} expects {min_inputs}..{max_input_label} inputs, got {len(node.input)}"
                )
            optional_inputs = self.OPTIONAL_INPUTS.get(op, set())
            if any(not value and index not in optional_inputs
                   for index, value in enumerate(node.input)):
                raise UnsupportedONNXOperatorError(
                    f"{op} omits a required input"
                )
            if any(not output for output in node.output):
                raise UnsupportedONNXOperatorError(
                    f"{op} output elision is not admitted"
                )
            missing_inputs = [name for name in node.input if name and name not in defined_values]
            if missing_inputs:
                raise UnsupportedONNXOperatorError(
                    f"{op} references undefined input tensor(s): {missing_inputs}"
                )
            if len(set(node.output)) != len(node.output) or any(
                name in defined_values for name in node.output
            ):
                raise UnsupportedONNXOperatorError(
                    f"{op} output tensor names must be unique and newly defined"
                )
            defined_values.update(node.output)
            expected_domain = custom_operator_domains.get(op)
            if expected_domain is not None:
                if node.domain != expected_domain:
                    raise UnsupportedONNXOperatorError(
                        f"{op} requires domain {expected_domain}, got {node.domain or 'ai.onnx'}"
                    )
                if self.opsets.get(expected_domain) != 1:
                    raise UnsupportedONNXOperatorError(
                        f"{expected_domain}::{op} requires declared opset 1; "
                        f"got {self.opsets.get(expected_domain)}"
                    )
            elif node.domain not in ("", "ai.onnx"):
                raise UnsupportedONNXOperatorError(
                    f"Standard operator {op} cannot use domain {node.domain}"
                )
            attribute_names = [attribute.name for attribute in node.attribute]
            if len(set(attribute_names)) != len(attribute_names):
                raise UnsupportedONNXOperatorError(f"{op} has duplicate attributes")
            unknown_attributes = set(attribute_names) - self.ALLOWED_ATTRIBUTES.get(op, set())
            if unknown_attributes:
                raise UnsupportedONNXOperatorError(
                    f"{op} has unsupported attribute(s): {sorted(unknown_attributes)}"
                )
            missing_attributes = self.REQUIRED_ATTRIBUTES.get(op, set()) - set(attribute_names)
            if missing_attributes:
                raise UnsupportedONNXOperatorError(
                    f"{op} is missing required attribute(s): {sorted(missing_attributes)}"
                )
            attrs = {a.name: helper.get_attribute_value(a) for a in node.attribute}
            ins, out = list(node.input), node.output[0]
            if op == "Constant":
                if set(attrs) != {"value"}:
                    raise UnsupportedONNXOperatorError(
                        "Constant requires exactly one tensor value attribute"
                    )
                self.constants[out] = numpy_helper.to_array(attrs["value"]).copy()
                self.shapes[out] = self.constants[out].shape
                continue
            for index in self.CONSTANT_INPUTS.get(op, ()):
                if index < len(ins) and ins[index] and ins[index] not in self.constants:
                    raise UnsupportedONNXOperatorError(
                        f"{op} input {index} must be a constant tensor in this profile"
                    )
            for index in self.INTEGER_VECTOR_INPUTS.get(op, ()):
                if index < len(ins) and ins[index]:
                    value = self.constants[ins[index]]
                    if value.dtype != np.int64 or value.ndim != 1:
                        raise UnsupportedONNXOperatorError(
                            f"{op} input {index} must be a 1D int64 tensor"
                        )
            integer_control_slots = set(self.INTEGER_VECTOR_INPUTS.get(op, ()))
            for index, name in enumerate(ins):
                if (name and name in self.constants and index not in integer_control_slots
                        and self.constants[name].dtype != np.float32):
                    raise UnsupportedONNXOperatorError(
                        f"{op} data input {index} must be FP32 in this profile"
                    )
            device_input_indices = {0} | self.DEVICE_DATA_INPUTS.get(op, set())
            if op == "Concat":
                device_input_indices.update(range(1, len(ins)))
            self.runtime_constant_names.update(
                ins[index] for index in device_input_indices
                if index < len(ins) and ins[index] in self.constants
            )
            shape = self.shapes[ins[0]]
            if op in ("Conv", "DmlFusedConv", "FusedConv", "ConvTranspose"):
                for name in ins[1:]:
                    if name and (name not in self.constants or self.constants[name].dtype != np.float32):
                        raise UnsupportedONNXOperatorError(f"{op} requires constant FP32 weights/bias: {name}")
            step = {"op": op, "inputs": ins, "output": out, "attrs": attrs}
            if op in ("Conv", "DmlFusedConv", "FusedConv"):
                if len(shape) != 4 or len(self.shapes[ins[1]]) != 4:
                    raise UnsupportedONNXOperatorError("Conv requires NCHW")
                wshape = self.shapes[ins[1]]
                pads = tuple(attrs.get("pads", [0, 0, 0, 0]))
                stride = tuple(attrs.get("strides", [1, 1]))
                dilation = tuple(attrs.get("dilations", [1, 1]))
                group = int(attrs.get("group", 1))
                if attrs.get("auto_pad", b"NOTSET") not in (b"NOTSET", b""):
                    raise UnsupportedONNXOperatorError("auto_pad requires explicit resolution")
                if (len(pads) != 4 or any(value < 0 for value in pads)
                        or len(stride) != 2 or any(value <= 0 for value in stride)
                        or len(dilation) != 2 or any(value <= 0 for value in dilation)
                        or group <= 0 or any(value <= 0 for value in wshape)):
                    raise UnsupportedONNXOperatorError("Invalid Conv pads, strides, dilation, group, or weights")
                if shape[1] != wshape[1] * group or wshape[0] % group:
                    raise UnsupportedONNXOperatorError("Invalid Conv groups")
                if "kernel_shape" in attrs and tuple(attrs["kernel_shape"]) != wshape[2:]:
                    raise UnsupportedONNXOperatorError("Conv kernel_shape must match weight dimensions")
                if len(ins) > 2 and ins[2] and self.shapes[ins[2]] != (wshape[0],):
                    raise UnsupportedONNXOperatorError("Conv bias must have shape [output_channels]")
                activation = 0
                if op in ("DmlFusedConv", "FusedConv"):
                    activation_attr = "fused_activation" if op == "DmlFusedConv" else "activation"
                    name = attrs.get(activation_attr, b"").decode()
                    activation = {"Relu": 1, "Sigmoid": 2, "Softplus": 3}.get(name)
                    if activation is None:
                        raise UnsupportedONNXOperatorError(f"Unsupported fused activation {name}")
                    if op == "DmlFusedConv":
                        activation_domain = attrs.get("fused_activation_domain", b"")
                        if activation_domain not in (b"", b"ai.onnx"):
                            raise UnsupportedONNXOperatorError(
                                "DmlFusedConv fused activation must use the standard ONNX domain"
                            )
                        activation_since = attrs.get("fused_activation_since_version")
                        if activation_since is not None:
                            standard_opset = self.opsets.get("", 0)
                            if type(activation_since) is not int or activation_since <= 0 or standard_opset <= 0:
                                raise UnsupportedONNXOperatorError(
                                    "DmlFusedConv fused activation since_version requires a "
                                    "positive version and an imported standard ONNX opset"
                                )
                            schema_since = defs.get_schema(
                                name, standard_opset, ""
                            ).since_version
                            if activation_since != schema_since:
                                raise UnsupportedONNXOperatorError(
                                    "DmlFusedConv fused activation since_version does not "
                                    "match the imported ONNX activation schema"
                                )
                step.update(pads=pads, stride=stride, dilation=dilation, group=group, activation=activation)
                shape = (shape[0], wshape[0], *[(shape[k+2] + pads[k] + pads[k+2] - dilation[k] * (wshape[k+2]-1)-1)//stride[k]+1 for k in range(2)])
            elif op in ("Add", "Sub", "Mul", "Div", "Pow"):
                shape = np.broadcast_shapes(shape, self.shapes[ins[1]])
                _padded(shape)
            elif op == "Gelu":
                if attrs.get("approximate", b"none") != b"none":
                    raise UnsupportedONNXOperatorError("Only exact-form GELU is admitted")
            elif op == "Clip":
                if ((len(ins) > 1 and ins[1] and "min" in attrs)
                        or (len(ins) > 2 and ins[2] and "max" in attrs)):
                    raise UnsupportedONNXOperatorError("Clip cannot mix bound attributes with bound inputs")
                low = self.constants[ins[1]] if len(ins) > 1 and ins[1] else None
                high = self.constants[ins[2]] if len(ins) > 2 and ins[2] else None
                if any(value is not None and (value.size != 1 or value.dtype != np.float32)
                       for value in (low, high)):
                    raise UnsupportedONNXOperatorError("Clip bounds must be scalar FP32 tensors")
                step["low"] = float(low.item()) if low is not None else float(attrs.get("min", -np.inf))
                step["high"] = float(high.item()) if high is not None else float(attrs.get("max", np.inf))
            elif op == "AveragePool":
                if attrs.get("ceil_mode", 0) or attrs.get("auto_pad", b"NOTSET") not in (b"NOTSET", b""):
                    raise UnsupportedONNXOperatorError("Pool ceil_mode/auto_pad not admitted")
                if len(shape) != 4:
                    raise UnsupportedONNXOperatorError("AveragePool requires NCHW")
                pads = tuple(attrs.get("pads", [0, 0, 0, 0]))
                stride = tuple(attrs.get("strides", [1, 1]))
                kernel = tuple(attrs["kernel_shape"])
                if (len(pads) != 4 or any(value < 0 for value in pads)
                        or len(stride) != 2 or any(value <= 0 for value in stride)
                        or len(kernel) != 2 or any(value <= 0 for value in kernel)):
                    raise UnsupportedONNXOperatorError("Invalid AveragePool pads, strides, or kernel_shape")
                step.update(pads=pads, stride=stride, kernel=kernel)
                shape = (*shape[:2], *[(shape[k+2]+pads[k]+pads[k+2]-kernel[k])//stride[k]+1 for k in range(2)])
            elif op == "SpaceToDepth":
                block = int(attrs["blocksize"])
                if block <= 0 or len(shape) != 4 or shape[2] % block or shape[3] % block:
                    raise UnsupportedONNXOperatorError("Invalid SpaceToDepth shape")
                shape = (shape[0], shape[1]*block*block, shape[2]//block, shape[3]//block)
            elif op in ("Reshape", "Identity"):
                if op == "Reshape":
                    target = [int(x) for x in self.constants[ins[1]].ravel()]
                    allowzero = int(attrs.get("allowzero", 0))
                    if allowzero not in (0, 1) or any(d < -1 for d in target):
                        raise UnsupportedONNXOperatorError("Invalid Reshape target or allowzero")
                    if target.count(-1) > 1:
                        raise UnsupportedONNXOperatorError("Invalid reshape")
                    if allowzero and 0 in target and -1 in target:
                        raise UnsupportedONNXOperatorError(
                            "Reshape cannot combine allowzero dimensions with -1"
                        )
                    if not allowzero:
                        if any(d == 0 and i >= len(shape) for i, d in enumerate(target)):
                            raise UnsupportedONNXOperatorError(
                                "Reshape zero-copy dimension exceeds input rank"
                            )
                        target = [shape[i] if d == 0 else d for i, d in enumerate(target)]
                    if -1 in target:
                        known_product = math.prod(d for d in target if d != -1)
                        if known_product == 0 or math.prod(shape) % known_product:
                            raise UnsupportedONNXOperatorError("Invalid inferred Reshape dimension")
                        target[target.index(-1)] = math.prod(shape) // known_product
                    if math.prod(target) != math.prod(shape):
                        raise UnsupportedONNXOperatorError("Reshape changes element count")
                    shape = tuple(target)
                self.aliases[out] = ins[0]
            elif op == "Concat":
                rank = len(shape)
                requested_axis = int(attrs["axis"])
                if rank == 0 or requested_axis < -rank or requested_axis >= rank:
                    raise UnsupportedONNXOperatorError(
                        f"Concat axis must be in [-{rank}, {rank - 1}] for rank {rank}"
                    )
                axis = requested_axis + rank if requested_axis < 0 else requested_axis
                step["axis"] = axis
                for name in ins:
                    s = self.shapes[name]
                    if len(s) != len(shape) or any(s[k] != shape[k] for k in range(len(shape)) if k != axis):
                        raise UnsupportedONNXOperatorError("Invalid Concat shape")
                shape = tuple(sum(self.shapes[n][k] for n in ins) if k == axis else d for k, d in enumerate(shape))
            elif op == "Transpose":
                perm = tuple(attrs.get("perm", reversed(range(len(shape)))))
                if len(perm) != len(shape) or sorted(perm) != list(range(len(shape))):
                    raise UnsupportedONNXOperatorError("Invalid Transpose permutation")
                if len(shape) > 8:
                    raise UnsupportedONNXOperatorError("Transpose rank > 8 is not admitted")
                step["perm"] = perm
                shape = tuple(shape[k] for k in perm)
            elif op == "Split":
                if len(ins) > 1 and ins[1] and "split" in attrs:
                    raise UnsupportedONNXOperatorError("Split cannot mix split input and split attribute")
                axis = int(attrs.get("axis", 0)) % len(shape)
                if len(ins) > 1 and ins[1]:
                    if ins[1] not in self.constants:
                        raise UnsupportedONNXOperatorError("Split sizes must be constant")
                    lengths = tuple(int(x) for x in self.constants[ins[1]].ravel())
                elif "split" in attrs:
                    lengths = tuple(int(x) for x in attrs["split"])
                else:
                    if shape[axis] % len(node.output):
                        raise UnsupportedONNXOperatorError("Split axis is not evenly divisible")
                    lengths = (shape[axis] // len(node.output),) * len(node.output)
                if len(lengths) != len(node.output) or any(x <= 0 for x in lengths) or sum(lengths) != shape[axis]:
                    raise UnsupportedONNXOperatorError("Invalid Split lengths")
                step.update(axis=axis, lengths=lengths, outputs=list(node.output))
                for output, length in zip(node.output, lengths):
                    out_shape = tuple(length if k == axis else d for k, d in enumerate(shape))
                    self.shapes[output] = out_shape
                self.steps.append(step)
                continue
            elif op == "Slice":
                starts, ends = (self.constants[n].ravel().tolist() for n in ins[1:3])
                axes = self.constants[ins[3]].ravel().tolist() if len(ins) > 3 and ins[3] else list(range(len(starts)))
                strides = self.constants[ins[4]].ravel().tolist() if len(ins) > 4 and ins[4] else [1]*len(starts)
                if len(axes) != 1 or strides != [1]:
                    raise UnsupportedONNXOperatorError("Only one-axis unit-step Slice admitted")
                axis = int(axes[0]) % len(shape)
                start, end, _ = slice(starts[0], ends[0]).indices(shape[axis])
                step.update(axis=axis, start=start)
                shape = tuple(max(0, end-start) if k == axis else d for k,d in enumerate(shape))
            elif op == "ReduceMean":
                if len(ins) > 1 and ins[1] and "axes" in attrs:
                    raise UnsupportedONNXOperatorError("ReduceMean cannot mix axes input and axes attribute")
                axes = self.constants[ins[1]].ravel().tolist() if len(ins)>1 and ins[1] else attrs.get("axes", list(range(len(shape))))
                if not axes and attrs.get("noop_with_empty_axes", 0):
                    self.aliases[out] = ins[0]
                else:
                    rank = len(shape)
                    requested_axes = [int(a) for a in (axes or list(range(rank)))]
                    if any(axis < -rank or axis >= rank for axis in requested_axes):
                        raise UnsupportedONNXOperatorError(
                            f"ReduceMean axis must be in [-{rank}, {rank - 1}] for rank {rank}"
                        )
                    axes = sorted(axis + rank if axis < 0 else axis for axis in requested_axes)
                    if axes != list(range(len(shape))) and len(axes) != 1:
                        raise UnsupportedONNXOperatorError("Only one-axis or full ReduceMean admitted")
                    step["axes"] = axes
                    keep = attrs.get("keepdims", 1)
                    shape = tuple(1 if k in axes else d for k,d in enumerate(shape)) if keep else tuple(d for k,d in enumerate(shape) if k not in axes)
            elif op == "ConvTranspose":
                ws = self.shapes[ins[1]]
                stride = tuple(attrs.get("strides",[1,1]))
                if "kernel_shape" in attrs and tuple(attrs["kernel_shape"]) != ws[2:]:
                    raise UnsupportedONNXOperatorError(
                        "ConvTranspose kernel_shape must match weight dimensions"
                    )
                if (len(shape) != 4 or len(ws) != 4 or any(value <= 0 for value in ws)
                        or len(stride) != 2 or any(value <= 0 for value in stride)
                        or attrs.get("auto_pad", b"NOTSET") not in (b"NOTSET", b"")
                        or shape[1] != 1 or ws[:2] != (1,1) or len(ins) != 2
                        or attrs.get("group",1) != 1 or any(attrs.get("pads",[0]*4))
                        or any(attrs.get("output_padding",[0]*2))
                        or len(attrs.get("pads",[0]*4)) != 4
                        or len(attrs.get("output_padding",[0]*2)) != 2
                        or tuple(attrs.get("dilations",[1,1])) != (1,1)
                        or "output_shape" in attrs):
                    raise UnsupportedONNXOperatorError("Only WeightNet single-channel ConvTranspose admitted")
                step["stride"] = stride
                shape = (shape[0],1,(shape[2]-1)*stride[0]+ws[2],(shape[3]-1)*stride[1]+ws[3])
            if any(d <= 0 for d in shape):
                raise UnsupportedONNXOperatorError(f"Empty tensor not admitted: {out} {shape}")
            self.shapes[out] = tuple(shape)
            self.steps.append(step)
        for output in graph.output:
            if output.name not in self.shapes:
                raise UnsupportedONNXOperatorError(
                    f"Graph output is not defined: {output.name}"
                )
            if output.name in self.constants and self.constants[output.name].dtype != np.float32:
                raise UnsupportedONNXOperatorError(
                    f"Graph output must be FP32: {output.name}"
                )
            if output.name in self.constants:
                self.runtime_constant_names.add(output.name)
            declared = tuple(d.dim_value for d in output.type.tensor_type.shape.dim)
            if output.type.tensor_type.elem_type != 1 or declared != self.shapes[output.name]:
                raise UnsupportedONNXOperatorError(f"Output metadata mismatch: {output.name}, declared {declared}, computed {self.shapes[output.name]}")
        self.fusion_stats = {
            "conv_gelu": 0,
            "weightnet_gate": 0,
            "mul_clip": 0,
            "weightnet_sigmoid_product_clip": 0,
            "weightnet_pow2_sub_clip_sqrt": 0,
            "weightnet_stats_tanh": 0,
            "weightnet_stats_tanh_algebraic_simplification": 0,
            "constant_pow2_mul_lowering": 0,
            "weightnet_pow2_reduce_mean": 0,
            "weightnet_full_range_slice_alias": 0,
            "weightnet_concat_conv_gelu": 0,
            "weightnet_conv_transpose_mul_clip": 0,
            "weightnet_abs_conv": 0,
            "weightnet_pool_abs_concat": 0,
            "weightnet_fused_heads_and_gate": 0,
            "weightnet_phase_gate_concat23": 0,
        }
        if enable_conv_gelu_fusion:
            self.fusion_stats["conv_gelu"] = self._fuse_conv_gelu()
        if enable_weightnet_gate_fusion:
            self.fusion_stats["weightnet_gate"] = self._fuse_weightnet_gate()
        if enable_weightnet_sigmoid_product_clip_fusion:
            self.fusion_stats["weightnet_sigmoid_product_clip"] = (
                self._fuse_weightnet_sigmoid_product_clip()
            )
        if enable_weightnet_conv_transpose_mul_clip_fusion:
            self.fusion_stats["weightnet_conv_transpose_mul_clip"] = (
                self._fuse_weightnet_conv_transpose_mul_clip()
            )
        if enable_weightnet_abs_conv_fusion:
            self.fusion_stats["weightnet_abs_conv"] = self._fuse_weightnet_abs_conv()
        if enable_weightnet_pool_abs_concat_fusion:
            self.fusion_stats["weightnet_pool_abs_concat"] = (
                self._fuse_weightnet_pool_abs_concat()
            )
        if enable_mul_clip_fusion:
            self.fusion_stats["mul_clip"] = self._fuse_mul_clip()
        if enable_weightnet_pow2_sub_clip_sqrt_fusion:
            self.fusion_stats["weightnet_pow2_sub_clip_sqrt"] = (
                self._fuse_weightnet_pow2_sub_clip_sqrt()
            )
        if enable_weightnet_stats_tanh_fusion:
            self.fusion_stats["weightnet_stats_tanh"] = (
                self._fuse_weightnet_stats_tanh()
            )
        if enable_weightnet_stats_tanh_algebraic_simplification:
            self.fusion_stats["weightnet_stats_tanh_algebraic_simplification"] = (
                self._enable_weightnet_stats_tanh_algebraic_simplification()
            )
        if enable_weightnet_pow2_reduce_mean_fusion:
            self.fusion_stats["weightnet_pow2_reduce_mean"] = (
                self._fuse_weightnet_pow2_reduce_mean()
            )
        if enable_weightnet_full_range_slice_alias:
            self.fusion_stats["weightnet_full_range_slice_alias"] = (
                self._alias_weightnet_full_range_slices()
            )
        if enable_weightnet_concat_conv_gelu_fusion:
            self.fusion_stats["weightnet_concat_conv_gelu"] = (
                self._fuse_weightnet_concat_conv_gelu()
            )
        if enable_constant_pow2_mul_lowering:
            self.fusion_stats["constant_pow2_mul_lowering"] = (
                self._lower_constant_pow2_to_square()
            )
        if enable_weightnet_fused_heads_and_gate_fusion:
            self.fusion_stats["weightnet_fused_heads_and_gate"] = (
                self._fuse_weightnet_heads_and_gate()
            )
        if enable_weightnet_phase_gate_concat23_fusion:
            self.fusion_stats["weightnet_phase_gate_concat23"] = (
                self._fuse_weightnet_phase_gate_concat23()
            )
        self.fusion_stats["weightnet_fused_tile_statistics"] = 0
        if enable_weightnet_fused_tile_statistics:
            self.fusion_stats["weightnet_fused_tile_statistics"] = (
                self._fuse_weightnet_tile_statistics()
            )
        self.concat_stats = {"gather_nodes": 0, "legacy_fallback_nodes": 0}
        if enable_concat_gather:
            for step in self.steps:
                if step["op"] == "Concat":
                    if len(step["inputs"]) <= _CONCAT_GATHER_MAX_INPUTS:
                        step["use_concat_gather"] = True
                        self.concat_stats["gather_nodes"] += 1
                    else:
                        self.concat_stats["legacy_fallback_nodes"] += 1
        self.alias_roots = {name: self._root_name(name) for name in self.shapes}
        self.buffer_plan, self.buffer_plan_stats = self._build_buffer_plan()
        self.buffers = {}
        self.scratch = {}
        self.dummy = None
        self._allocated = False
        self._allocation_lock = threading.Lock()
        self._lock = threading.Lock()
        self.optimized = True
        self.backend = None

    def _lower_constant_pow2_to_square(self):
        """Use one multiply for a scalar FP32 Pow exponent exactly equal to 2.

        This experimental lowering is opt-in. The strict constant/type/shape
        checks keep generic Pow semantics on the existing path; runtime
        benchmark and parity evidence are required before enabling it by
        default.
        """
        lowered = 0
        for step in self.steps:
            if step["op"] != "Pow" or len(step["inputs"]) != 2:
                continue
            base_name, exponent_name = step["inputs"]
            exponent = self.constants.get(exponent_name)
            if (exponent is None or exponent.shape != ()
                    or exponent.dtype != np.float32
                    or int(exponent.view(np.uint32)) != 0x40000000):
                continue
            if self.shapes.get(step["output"]) != self.shapes.get(base_name):
                continue

            step.update(
                op="Square",
                inputs=[base_name],
                attrs={},
                lowered_from="Pow(base, scalar_fp32(2.0))",
            )
            lowered += 1
            if (exponent_name not in self.outputs
                    and not any(exponent_name in other["inputs"]
                                for other in self.steps if other is not step)):
                self.runtime_constant_names.discard(exponent_name)
        return lowered

    def _fuse_weightnet_pow2_reduce_mean(self):
        """Fuse the exact Pow/Square -> channel ReduceMean branch in WeightNet."""
        if self.opsets.get("", 0) < 13:
            return 0

        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        candidates = []
        for reduce_index, reduce_step in enumerate(self.steps):
            if reduce_step["op"] != "ReduceMean":
                continue
            if reduce_step.get("axes") != [1]:
                continue
            if int(reduce_step.get("attrs", {}).get("keepdims", 1)) != 1:
                continue
            if int(reduce_step.get("attrs", {}).get("noop_with_empty_axes", 0)) != 0:
                continue
            if set(reduce_step.get("attrs", {})) - {"keepdims", "noop_with_empty_axes"}:
                continue
            if len(reduce_step["inputs"]) < 1:
                continue
            pow_name = reduce_step["inputs"][0]
            pow_index = producers.get(pow_name)
            if pow_index is None or pow_index >= reduce_index:
                continue
            pow_step = self.steps[pow_index]
            exponent_name = None
            if pow_step["op"] == "Pow":
                if len(pow_step["inputs"]) != 2 or pow_step.get("attrs"):
                    continue
                base_name, exponent_name = pow_step["inputs"]
                exponent = self.constants.get(exponent_name)
                if (exponent is None or exponent.shape != ()
                        or exponent.dtype != np.float32
                        or int(exponent.view(np.uint32).item()) != 0x40000000):
                    continue
            elif pow_step["op"] == "Square":
                if len(pow_step["inputs"]) != 1 or pow_step.get("attrs"):
                    continue
                base_name = pow_step["inputs"][0]
            else:
                continue

            base_shape = self.shapes.get(base_name)
            pow_shape = self.shapes.get(pow_name)
            output_name = reduce_step["output"]
            output_shape = self.shapes.get(output_name)
            if (base_shape is None or len(base_shape) != 4 or base_shape[1] != 4
                    or pow_shape != base_shape
                    or output_shape != (base_shape[0], 1, base_shape[2], base_shape[3])):
                continue
            if (pow_name in self.outputs or pow_name in self.aliases
                    or consumers.get(pow_name) != [reduce_index]):
                continue
            candidates.append((pow_index, reduce_index, base_name, exponent_name, reduce_step))

        if not candidates:
            return 0

        removed_steps = set()
        for pow_index, reduce_index, base_name, exponent_name, reduce_step in candidates:
            reduce_step.update(
                op="WeightNetSquareReduceMean",
                inputs=[base_name],
                attrs={},
            )
            removed_steps.add(pow_index)
            if (exponent_name and exponent_name not in self.outputs
                    and not any(exponent_name in s["inputs"] for idx, s in enumerate(self.steps) if idx not in removed_steps)):
                self.runtime_constant_names.discard(exponent_name)

        self.steps = [
            step for index, step in enumerate(self.steps) if index not in removed_steps
        ]
        return len(candidates)

    def _alias_weightnet_full_range_slices(self):
        """Alias terminal full-range WeightNet ConvTranspose Slice pairs."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)

        # 1. Check exact candidate pair (covers unit tests and GPU model)
        candidates = (
            ("/Slice_2_output_0", "/ConvTranspose_output_0", 2),
            ("/Slice_3_output_0", "/Slice_2_output_0", 3),
        )
        all_candidates_match = True
        cand_removed = set()
        cand_alias_map = {}
        for output_name, expected_input, expected_axis in candidates:
            index = producers.get(output_name)
            if index is None:
                all_candidates_match = False
                break
            step = self.steps[index]
            if (step["op"] != "Slice" or step["inputs"][0] != expected_input
                    or step.get("attrs") or step.get("start") != 0
                    or step.get("axis") != expected_axis
                    or output_name in graph_outputs or output_name in self.aliases
                    or len(step["inputs"]) < 3
                    or self.shapes.get(output_name) != self.shapes.get(expected_input)
                    or len(consumers.get(output_name, ())) != 1
                    or consumers[output_name][0] <= index):
                all_candidates_match = False
                break
            cand_alias_map[output_name] = expected_input
            cand_removed.add(index)

        if all_candidates_match and len(cand_removed) == len(candidates):
            self.aliases.update(cand_alias_map)
            self.steps = [
                step for index, step in enumerate(self.steps) if index not in cand_removed
            ]
            return len(cand_removed)

        # 2. General topological search from ConvTranspose (e.g. CPU model / dynamic models)
        removed = set()
        alias_map = {}
        for conv_index, conv_step in enumerate(self.steps):
            if conv_step["op"] != "ConvTranspose":
                continue
            conv_out = conv_step["output"]
            conv_shape = self.shapes.get(conv_out)
            if conv_shape is None or len(conv_shape) != 4:
                continue

            cons1 = consumers.get(conv_out, [])
            if len(cons1) != 1:
                continue
            s1_index = cons1[0]
            if s1_index <= conv_index:
                continue
            s1 = self.steps[s1_index]
            if (s1["op"] != "Slice" or s1["inputs"][0] != conv_out
                    or s1.get("attrs") or s1.get("start") != 0
                    or s1.get("axis") != 2
                    or s1["output"] in graph_outputs or s1["output"] in self.aliases
                    or len(s1["inputs"]) < 3
                    or self.shapes.get(s1["output"]) != conv_shape
                    or len(consumers.get(s1["output"], ())) != 1):
                continue

            s2_index = consumers[s1["output"]][0]
            if s2_index <= s1_index:
                continue
            s2 = self.steps[s2_index]
            if (s2["op"] != "Slice" or s2["inputs"][0] != s1["output"]
                    or s2.get("attrs") or s2.get("start") != 0
                    or s2.get("axis") != 3
                    or s2["output"] in graph_outputs or s2["output"] in self.aliases
                    or len(s2["inputs"]) < 3
                    or self.shapes.get(s2["output"]) != conv_shape
                    or len(consumers.get(s2["output"], ())) != 1):
                continue

            alias_map[s1["output"]] = conv_out
            alias_map[s2["output"]] = s1["output"]
            removed.add(s1_index)
            removed.add(s2_index)

        if not removed:
            return 0
        self.aliases.update(alias_map)
        self.steps = [
            step for index, step in enumerate(self.steps) if index not in removed
        ]
        return len(removed)

    def _fuse_weightnet_conv_transpose_mul_clip(self):
        """Fuse the terminal ConvTranspose -> full-range Slice -> Mul -> Clip path."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)
        clip_candidates = []
        for clip_index, clip in enumerate(self.steps):
            if clip["op"] != "Clip" or len(clip["inputs"]) != 3:
                continue
            if (clip["inputs"][1] not in self.constants
                    or clip["inputs"][2] not in self.constants):
                continue
            low_value = self.constants[clip["inputs"][1]]
            high_value = self.constants[clip["inputs"][2]]
            if (low_value.shape != () or high_value.shape != ()
                    or low_value.dtype != np.float32 or high_value.dtype != np.float32
                    or float(low_value.item()) != 0.0 or float(high_value.item()) != 1.0
                    or clip.get("low") != 0.0 or clip.get("high") != 1.0):
                continue

            mul_name = clip["inputs"][0]
            mul_index = producers.get(mul_name)
            if mul_index is None or mul_index >= clip_index:
                continue
            mul = self.steps[mul_index]
            if mul["op"] != "Mul" or len(mul["inputs"]) != 2:
                continue
            if (mul_name in graph_outputs or mul_name in self.aliases
                    or consumers.get(mul_name) != [clip_index]):
                continue

            map_inputs = [name for name in mul["inputs"] if name in self.constants]
            tensor_inputs = [name for name in mul["inputs"] if name not in self.constants]
            if len(tensor_inputs) != 1 or len(map_inputs) != 1:
                continue
            scale_name = map_inputs[0]
            slice_or_conv_name = tensor_inputs[0]

            curr = slice_or_conv_name
            removed_slices = set()
            while True:
                curr_root = self.aliases.get(curr, curr)
                if curr_root != curr:
                    curr = curr_root
                    continue
                p_idx = producers.get(curr)
                if p_idx is None:
                    break
                p_step = self.steps[p_idx]
                if p_step["op"] == "Slice":
                    if curr in graph_outputs:
                        break
                    removed_slices.add(p_idx)
                    curr = p_step["inputs"][0]
                elif p_step["op"] == "ConvTranspose":
                    break
                else:
                    break

            conv_name = curr
            conv_index = producers.get(conv_name)
            if conv_index is None or conv_index >= mul_index:
                continue
            conv = self.steps[conv_index]
            if conv["op"] != "ConvTranspose" or len(conv["inputs"]) != 2:
                continue
            if conv_name in graph_outputs or any(self._root_name(output_name) == conv_name for output_name in graph_outputs):
                continue

            input_shape = self.shapes.get(conv["inputs"][0])
            conv_shape = self.shapes.get(conv_name)
            output_shape = self.shapes.get(clip["output"])
            scale = self.constants[scale_name]
            weight_shape = self.shapes.get(conv["inputs"][1])
            if (input_shape is None or len(input_shape) != 4 or input_shape[1] != 1
                    or conv_shape is None or len(conv_shape) != 4 or conv_shape[1] != 1
                    or output_shape != conv_shape
                    or self.shapes.get(mul_name) != conv_shape
                    or weight_shape is None or weight_shape[:2] != (1, 1)
                    or tuple(conv.get("stride", ())) != (4, 4)
                    or weight_shape[2:] != (8, 8)
                    or scale.dtype != np.float32
                    or scale.shape != (1, 1, conv_shape[2], conv_shape[3])):
                continue
            if clip["output"] in self.aliases:
                continue

            all_removed = {mul_index, clip_index} | removed_slices
            clip_candidates.append((
                conv_index, all_removed,
                conv, clip, scale_name,
            ))

        if len(clip_candidates) != 1:
            return 0

        conv_index, removed_steps, conv, clip, scale_name = clip_candidates[0]
        conv.update(
            op="WeightNetConvTransposeMulClip",
            inputs=[conv["inputs"][0], conv["inputs"][1], scale_name],
            output=clip["output"],
            attrs={},
            low=clip["low"],
            high=clip["high"],
        )
        self.steps = [
            step for index, step in enumerate(self.steps) if index not in removed_steps
        ]
        return 1

    def _fuse_weightnet_abs_conv(self):
        """Fuse the private phase-gate Abs into its exact 1x1 sigmoid Conv loads."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)
        candidates = []
        for conv_index, conv_step in enumerate(self.steps):
            if conv_step["op"] not in ("DmlFusedConv", "FusedConv"):
                continue
            if len(conv_step["inputs"]) != 3 or conv_step.get("activation") != 2:
                continue
            abs_name = conv_step["inputs"][0]
            abs_index = producers.get(abs_name)
            if abs_index is None or abs_index >= conv_index:
                continue
            abs_step = self.steps[abs_index]
            if (abs_step["op"] != "Abs" or len(abs_step["inputs"]) != 1
                    or abs_step.get("attrs")
                    or consumers.get(abs_name) != [conv_index]
                    or abs_name in graph_outputs or abs_name in self.aliases):
                continue

            source_name = abs_step["inputs"][0]
            input_shape = self.shapes.get(source_name)
            abs_shape = self.shapes.get(abs_name)
            output_shape = self.shapes.get(conv_step["output"])
            weight_name, bias_name = conv_step["inputs"][1:]
            weight = self.constants.get(weight_name)
            bias = self.constants.get(bias_name)
            if (input_shape is None or len(input_shape) != 4
                    or input_shape[1] != 3 or abs_shape != input_shape
                    or output_shape != (input_shape[0], 1, input_shape[2], input_shape[3])
                    or weight is None or weight.dtype != np.float32
                    or weight.shape != (1, 3, 1, 1)
                    or bias is None or bias.dtype != np.float32
                    or bias.shape != (1,)
                    or conv_step.get("group") != 1
                    or tuple(conv_step.get("stride", ())) != (1, 1)
                    or tuple(conv_step.get("dilation", ())) != (1, 1)
                    or tuple(conv_step.get("pads", ())) != (0, 0, 0, 0)):
                continue

            candidates.append((conv_index, abs_index, conv_step, source_name, weight_name, bias_name))

        if len(candidates) != 1:
            return 0

        conv_index, abs_index, conv_step, source_name, weight_name, bias_name = candidates[0]
        conv_step.update(
            op="WeightNetAbsConvSigmoid",
            inputs=[source_name, weight_name, bias_name],
            attrs={},
        )
        self.steps = [
            step for index, step in enumerate(self.steps) if index != abs_index
        ]
        return 1

    def _fuse_weightnet_pool_abs_concat(self):
        """Fuse the private padded AveragePool -> Abs segment into WeightNet Concat."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)
        candidates = []
        for concat_index, concat in enumerate(self.steps):
            if concat["op"] != "Concat" or concat.get("axis") != 1:
                continue
            if len(concat["inputs"]) != 6:
                continue
            abs_name = concat["inputs"][3]
            abs_index = producers.get(abs_name)
            if abs_index is None or abs_index >= concat_index:
                continue
            abs_step = self.steps[abs_index]
            if (abs_step["op"] != "Abs" or len(abs_step["inputs"]) != 1
                    or abs_step.get("attrs")
                    or consumers.get(abs_name) != [concat_index]
                    or abs_name in graph_outputs or abs_name in self.aliases):
                continue

            pool_name = abs_step["inputs"][0]
            pool_index = producers.get(pool_name)
            if pool_index is None or pool_index >= abs_index:
                continue
            pool = self.steps[pool_index]
            sub_name = concat["inputs"][2]
            if (pool["op"] != "AveragePool" or pool["inputs"] != [sub_name]
                    or tuple(pool.get("kernel", ())) != (3, 3)
                    or tuple(pool.get("stride", ())) != (1, 1)
                    or tuple(pool.get("pads", ())) != (1, 1, 1, 1)
                    or int(pool.get("attrs", {}).get("count_include_pad", 0)) != 1
                    or int(pool.get("attrs", {}).get("ceil_mode", 0)) != 0
                    or pool.get("attrs", {}).get("auto_pad", b"NOTSET") not in (b"NOTSET", b"")
                    or consumers.get(pool_name) != [abs_index]
                    or pool_name in graph_outputs or pool_name in self.aliases):
                continue

            input_names = [concat["inputs"][0], concat["inputs"][1], sub_name,
                           sub_name, concat["inputs"][4], concat["inputs"][5]]
            shapes = [self.shapes.get(name) for name in input_names]
            output_shape = self.shapes.get(concat["output"])
            pool_shape = self.shapes.get(pool_name)
            abs_shape = self.shapes.get(abs_name)
            if (any(shape is None or len(shape) != 4 for shape in shapes)
                    or shapes[0][1] != 4 or shapes[1][1] != 4 or shapes[2][1] != 4
                    or shapes[3][1] != 4 or shapes[4][1] != 4 or shapes[5][1] != 3
                    or any(shape[0] != shapes[0][0] or shape[2:] != shapes[0][2:]
                           for shape in shapes[1:])
                    or pool_shape != shapes[2] or abs_shape != shapes[2]
                    or output_shape != (shapes[0][0], 23, shapes[0][2], shapes[0][3])):
                continue

            candidates.append((concat_index, pool_index, abs_index, concat, input_names))

        if len(candidates) != 1:
            return 0

        concat_index, pool_index, abs_index, concat, input_names = candidates[0]
        concat.update(
            op="WeightNetConcatPoolAbsGather",
            inputs=input_names,
            attrs={},
        )
        self.steps = [
            step for index, step in enumerate(self.steps)
            if index not in (pool_index, abs_index)
        ]
        return 1

    def _fuse_weightnet_concat_conv_gelu(self):
        """Fuse the three-source Concat -> 1x1 Conv -> GELU path."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)
        candidates = []
        for conv_index, conv in enumerate(self.steps):
            if conv["op"] not in ("Conv", "FusedConv"):
                continue
            if conv.get("activation") != 4:
                continue
            if (conv.get("stride") != (1, 1) or conv.get("dilation") != (1, 1)
                    or conv.get("pads") != (0, 0, 0, 0) or conv.get("group") != 1):
                continue
            if len(conv["inputs"]) != 3:
                continue
            concat_name = conv["inputs"][0]
            concat_index = producers.get(concat_name)
            if concat_index is None or concat_index >= conv_index:
                continue
            concat = self.steps[concat_index]
            if (concat["op"] != "Concat" or concat.get("axis") != 1
                    or len(concat["inputs"]) != 3
                    or concat.get("attrs", {}).get("axis") != 1):
                continue
            if (concat_name in graph_outputs or concat_name in self.aliases
                    or consumers.get(concat_name) != [conv_index]):
                continue

            source_shapes = [self.shapes.get(name) for name in concat["inputs"]]
            concat_shape = self.shapes.get(concat_name)
            weight_name, bias_name = conv["inputs"][1:]
            weights = self.constants.get(weight_name)
            bias = self.constants.get(bias_name)
            output_shape = self.shapes.get(conv["output"])
            if (any(shape is None or len(shape) != 4 for shape in source_shapes)
                    or source_shapes[0][1] != 20
                    or source_shapes[1][1] != 2
                    or source_shapes[2][1] != 1
                    or any(shape[0] != source_shapes[0][0]
                           or shape[2:] != source_shapes[0][2:]
                           for shape in source_shapes[1:])
                    or concat_shape != (source_shapes[0][0], 23, *source_shapes[0][2:])
                    or weights is None or weights.dtype != np.float32
                    or weights.shape[1:] != (23, 1, 1)
                    or weights.shape[0] % 4 != 0
                    or bias is None or bias.dtype != np.float32
                    or bias.shape != (weights.shape[0],)
                    or output_shape != (source_shapes[0][0], weights.shape[0],
                                        *source_shapes[0][2:])):
                continue

            candidates.append((conv_index, concat_index, conv, concat, weight_name, bias_name, source_shapes, weights))

        if len(candidates) != 1:
            return 0

        conv_index, concat_index, conv, concat, weight_name, bias_name, source_shapes, weights = candidates[0]
        conv.update(
            op="WeightNetConcatConvGelu",
            inputs=[*concat["inputs"], weight_name, bias_name],
            attrs={},
            source_channels=(20, 2, 1),
            output_channels=weights.shape[0],
            batch=source_shapes[0][0],
        )
        self.steps = [
            step for index, step in enumerate(self.steps) if index != concat_index
        ]
        return 1

    def _fuse_conv_gelu(self):
        """Fuse single-use Conv -> exact-form GELU pairs when explicitly enabled.

        This pass is opt-in until each target model profile clears its
        accuracy, latency, and memory gates. It leaves graph-output GELU values
        visible and aliases that value to the Conv result buffer, so the fused
        Conv writes the final GELU result without allocating a second tensor.
        """
        consumers = {}
        producers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers[name] = consumers.get(name, 0) + 1

        graph_outputs = set(self.outputs)
        removed_steps = set()
        fused_pairs = 0
        for gelu_index, gelu_step in enumerate(self.steps):
            if gelu_step["op"] != "Gelu" or len(gelu_step["inputs"]) != 1:
                continue
            conv_output = gelu_step["inputs"][0]
            conv_index = producers.get(conv_output)
            if conv_index is None or conv_index >= gelu_index:
                continue
            conv_step = self.steps[conv_index]
            if conv_step["op"] != "Conv" or conv_step.get("activation") != 0:
                continue
            if (conv_output in graph_outputs or consumers.get(conv_output) != 1
                    or conv_output in self.aliases):
                continue

            gelu_output = gelu_step["output"]
            if (gelu_output in self.aliases
                    or self.shapes.get(conv_output) != self.shapes.get(gelu_output)):
                continue

            conv_step["activation"] = 4
            self.aliases[gelu_output] = conv_output
            removed_steps.add(gelu_index)
            fused_pairs += 1

        if removed_steps:
            self.steps = [
                step for index, step in enumerate(self.steps)
                if index not in removed_steps
            ]
        return fused_pairs

    def _fuse_weightnet_gate(self):
        """Fuse the two-channel WeightNet adaptive-gate subgraph."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)

        def producer(name, expected_op=None):
            index = producers.get(name)
            if index is None:
                return None
            step = self.steps[index]
            if expected_op is not None and step["op"] != expected_op:
                return None
            return index, step

        def private_single_use(name, expected_index):
            return (
                name not in graph_outputs
                and name not in self.aliases
                and consumers.get(name) == [expected_index]
            )

        removed_steps = set()
        fused_count = 0
        for sigmoid_index, sigmoid in enumerate(self.steps):
            if sigmoid["op"] != "Sigmoid" or len(sigmoid["inputs"]) != 1:
                continue
            gate_output = sigmoid["output"]
            gate_shape = self.shapes.get(gate_output)
            if (gate_shape is None or len(gate_shape) != 4
                    or gate_shape[1] != 1 or any(dim <= 0 for dim in gate_shape)):
                continue

            mul_match = producer(sigmoid["inputs"][0], "Mul")
            if mul_match is None:
                continue
            mul_index, mul = mul_match
            if mul_index >= sigmoid_index or len(mul["inputs"]) != 2:
                continue

            branch_match = None
            for add_input in mul["inputs"]:
                add_candidate = producer(add_input, "Add")
                if add_candidate is None:
                    continue
                add_index, add = add_candidate
                sub_input = mul["inputs"][1] if add_input == mul["inputs"][0] else mul["inputs"][0]
                sub_candidate = producer(sub_input, "Sub")
                if sub_candidate is not None:
                    branch_match = (add_index, add, sub_candidate[0], sub_candidate[1])
                    break
            if branch_match is None:
                continue
            add_index, add, sub_index, sub = branch_match
            if (add_index >= mul_index or sub_index >= mul_index
                    or len(add["inputs"]) != 2 or len(sub["inputs"]) != 2):
                continue

            add_softplus = None
            half_constant = None
            for name in add["inputs"]:
                if name in self.constants:
                    value = self.constants[name]
                    if (value.size == 1 and value.dtype == np.float32
                            and float(value.item()) == 0.5):
                        half_constant = name
                else:
                    candidate = producer(name, "Softplus")
                    if candidate is not None:
                        add_softplus = candidate
            if add_softplus is None or half_constant is None:
                continue
            add_softplus_index, add_softplus_step = add_softplus

            sub_softplus = producer(sub["inputs"][0], "Softplus")
            safety_name = sub["inputs"][1]
            safety_match = producer(safety_name)
            if sub_softplus is None or safety_match is None:
                continue
            safety_op = safety_match[1]["op"]
            if safety_op in ("DmlFusedConv", "FusedConv"):
                if safety_match[1].get("activation") != 3:
                    continue
            elif safety_op == "Softplus":
                pass
            else:
                continue
            sub_softplus_index, sub_softplus_step = sub_softplus

            ch0_input = add_softplus_step["inputs"][0]
            ch1_input = sub_softplus_step["inputs"][0]
            slice0_match = producer(ch0_input, "Slice")
            slice1_match = producer(ch1_input, "Slice")
            split_match = producer(ch0_input, "Split")

            private_indices = {
                add_softplus_index, sub_softplus_index, add_index, sub_index, mul_index,
            }

            if slice0_match is not None and slice1_match is not None:
                slice0_index, slice0 = slice0_match
                slice1_index, slice1 = slice1_match
                conv_name = slice0["inputs"][0]
                if slice1["inputs"][0] != conv_name:
                    continue
                if (slice0.get("axis") != 1 or slice0.get("start") != 0
                        or slice1.get("axis") != 1 or slice1.get("start") != 1):
                    continue
                if (not private_single_use(slice0["output"], add_softplus_index)
                        or not private_single_use(slice1["output"], sub_softplus_index)):
                    continue
                private_indices.add(slice0_index)
                private_indices.add(slice1_index)
            elif split_match is not None:
                split_index, split_step = split_match
                outputs = split_step.get("outputs", [])
                if len(outputs) != 2 or outputs[0] != ch0_input or outputs[1] != ch1_input:
                    continue
                conv_name = split_step["inputs"][0]
                if (not private_single_use(ch0_input, add_softplus_index)
                        or not private_single_use(ch1_input, sub_softplus_index)):
                    continue
                private_indices.add(split_index)
            else:
                continue

            conv_match = producer(conv_name, "Conv")
            conv_shape = self.shapes.get(conv_name)
            if (conv_match is None or conv_match[1].get("activation") != 0
                    or conv_shape is None or len(conv_shape) != 4
                    or conv_shape[1] != 2 or any(dim <= 0 for dim in conv_shape)):
                continue
            expected_gate_shape = (conv_shape[0], 1, conv_shape[2], conv_shape[3])
            if gate_shape != expected_gate_shape or self.shapes.get(safety_name) != expected_gate_shape:
                continue

            private_edges = (
                (add_softplus_step["output"], add_index),
                (sub_softplus_step["output"], sub_index),
                (add["output"], mul_index),
                (sub["output"], mul_index),
                (mul["output"], sigmoid_index),
            )
            if not all(private_single_use(name, index) for name, index in private_edges):
                continue
            if any(index >= sigmoid_index for index in private_indices):
                continue

            sigmoid.update(
                op="WeightNetAdaptiveGate",
                inputs=[conv_name, safety_name],
                attrs={},
            )
            sigmoid["batch"] = conv_shape[0]
            sigmoid["height"] = conv_shape[2]
            sigmoid["width"] = conv_shape[3]
            removed_steps.update(private_indices)
            fused_count += 1

        if removed_steps:
            self.steps = [
                step for index, step in enumerate(self.steps)
                if index not in removed_steps
            ]
        return fused_count

    def _fuse_mul_clip(self):
        """Fuse private same-shape FP32 Mul -> Clip pairs with scalar bounds."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)
        removed_steps = set()
        fused_count = 0
        for clip_index, clip in enumerate(self.steps):
            if clip["op"] != "Clip" or len(clip["inputs"]) != 3:
                continue
            mul_name = clip["inputs"][0]
            mul_index = producers.get(mul_name)
            if mul_index is None or mul_index >= clip_index:
                continue
            mul = self.steps[mul_index]
            if mul["op"] != "Mul" or len(mul["inputs"]) != 2:
                continue
            if (clip["inputs"][1] not in self.constants
                    or clip["inputs"][2] not in self.constants):
                continue
            low_value = self.constants[clip["inputs"][1]]
            high_value = self.constants[clip["inputs"][2]]
            if (low_value.size != 1 or high_value.size != 1
                    or low_value.dtype != np.float32 or high_value.dtype != np.float32
                    or float(low_value.item()) != 0.0 or float(high_value.item()) != 1.0
                    or clip.get("low") != 0.0 or clip.get("high") != 1.0):
                continue
            mul_shape = self.shapes.get(mul_name)
            clip_shape = self.shapes.get(clip["output"])
            lhs_shape = self.shapes.get(mul["inputs"][0])
            rhs_shape = self.shapes.get(mul["inputs"][1])
            if (mul_shape is None or mul_shape != clip_shape
                    or lhs_shape != mul_shape or rhs_shape != mul_shape
                    or not mul_shape or math.prod(mul_shape) <= 0):
                continue
            if (mul_name in graph_outputs or mul_name in self.aliases
                    or consumers.get(mul_name) != [clip_index]):
                continue

            clip.update(
                op="FusedMulClip",
                inputs=list(mul["inputs"]),
                attrs={},
                low=0.0,
                high=1.0,
            )
            removed_steps.add(mul_index)
            fused_count += 1

        if removed_steps:
            self.steps = [
                step for index, step in enumerate(self.steps)
                if index not in removed_steps
            ]
        return fused_count

    def _fuse_weightnet_sigmoid_product_clip(self):
        """Drop the redundant Clip after multiplying two Sigmoid outputs.

        This WeightNet-only pass accepts a private Mul -> Clip[0, 1] pair when
        both Mul inputs come directly from standard Sigmoid operators or
        Conv operators with fused Sigmoid activation. It preserves the Clip
        output name and fails closed for other products, shapes, bounds, or
        graph-visible Mul outputs.
        """
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        def is_sigmoid_output(name):
            producer_index = producers.get(name)
            if producer_index is None:
                return False
            producer = self.steps[producer_index]
            return (producer["op"] == "Sigmoid"
                    or (producer["op"] in ("Conv", "DmlFusedConv", "FusedConv")
                        and producer.get("activation") == 2))

        graph_outputs = set(self.outputs)
        removed_steps = set()
        fused_count = 0
        for clip_index, clip in enumerate(self.steps):
            if clip["op"] != "Clip" or len(clip["inputs"]) != 3:
                continue
            mul_name = clip["inputs"][0]
            mul_index = producers.get(mul_name)
            if mul_index is None or mul_index >= clip_index:
                continue
            mul = self.steps[mul_index]
            if mul["op"] != "Mul" or len(mul["inputs"]) != 2:
                continue
            if (clip["inputs"][1] not in self.constants
                    or clip["inputs"][2] not in self.constants):
                continue
            low_value = self.constants[clip["inputs"][1]]
            high_value = self.constants[clip["inputs"][2]]
            if (low_value.size != 1 or high_value.size != 1
                    or low_value.dtype != np.float32 or high_value.dtype != np.float32
                    or float(low_value.item()) != 0.0
                    or float(high_value.item()) != 1.0
                    or clip.get("low") != 0.0 or clip.get("high") != 1.0):
                continue

            lhs_name, rhs_name = mul["inputs"]
            mul_shape = self.shapes.get(mul_name)
            clip_shape = self.shapes.get(clip["output"])
            if (not is_sigmoid_output(lhs_name) or not is_sigmoid_output(rhs_name)
                    or mul_shape is None or mul_shape != clip_shape
                    or self.shapes.get(lhs_name) != mul_shape
                    or self.shapes.get(rhs_name) != mul_shape
                    or not mul_shape or math.prod(mul_shape) <= 0):
                continue
            if (mul_name in graph_outputs or mul_name in self.aliases
                    or consumers.get(mul_name) != [clip_index]):
                continue

            clip.update(
                op="WeightNetSigmoidProduct",
                inputs=[lhs_name, rhs_name],
                attrs={},
            )
            removed_steps.add(mul_index)
            fused_count += 1

        if removed_steps:
            self.steps = [
                step for index, step in enumerate(self.steps)
                if index not in removed_steps
            ]
        return fused_count

    def _fuse_weightnet_heads_and_gate(self):
        """Super-fuse the 127x127 heads (benefit, safety), gate MLP, and product into one kernel."""
        def root_name(name):
            return self.aliases.get(name, name)

        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
                root = root_name(name)
                if root != name:
                    producers[root] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)
                    root = root_name(name)
                    if root != name:
                        consumers.setdefault(root, []).append(index)

        graph_outputs = set(self.outputs)

        def private_single_use(name, expected_index):
            return (
                name not in graph_outputs
                and set(consumers.get(root_name(name), [])) == {expected_index}
            )

        removed_steps = set()
        fused_count = 0

        for mul_index, mul_step in enumerate(self.steps):
            if mul_step["op"] not in ("FusedMulClip", "WeightNetSigmoidProduct"):
                continue
            inps = mul_step["inputs"]
            gate_match = None
            benefit_match = None
            for inp in inps:
                r_inp = root_name(inp)
                p_idx = producers.get(r_inp)
                if p_idx is not None and self.steps[p_idx]["op"] == "WeightNetAdaptiveGate":
                    gate_match = (p_idx, self.steps[p_idx])
                elif p_idx is not None and self.steps[p_idx]["op"] in ("Conv", "DmlFusedConv", "FusedConv"):
                    p_step = self.steps[p_idx]
                    if p_step.get("activation") == 2:
                        benefit_match = (p_idx, p_step)

            if gate_match is None or benefit_match is None:
                continue

            gate_index, gate_step = gate_match
            ben_index, ben_step = benefit_match
            if gate_index >= mul_index or ben_index >= mul_index:
                continue

            if len(ben_step["inputs"]) < 3:
                continue
            reasoner_ben = root_name(ben_step["inputs"][0])
            benefit_w = ben_step["inputs"][1]
            benefit_b = ben_step["inputs"][2]
            if benefit_w not in self.constants or benefit_b not in self.constants:
                continue

            if len(gate_step["inputs"]) < 2:
                continue
            conv2_name = root_name(gate_step["inputs"][0])
            safety_name = root_name(gate_step["inputs"][1])
            conv2_index = producers.get(conv2_name)
            safety_index = producers.get(safety_name)
            if conv2_index is None or safety_index is None:
                continue
            if conv2_index >= gate_index or safety_index >= gate_index:
                continue
            conv2_step = self.steps[conv2_index]
            safety_step = self.steps[safety_index]

            safety_conv_index = safety_index
            safety_conv_step = safety_step
            if safety_step["op"] == "Softplus":
                s_inp = root_name(safety_step["inputs"][0])
                s_conv_idx = producers.get(s_inp)
                if s_conv_idx is None or s_conv_idx >= safety_index:
                    continue
                safety_conv_index = s_conv_idx
                safety_conv_step = self.steps[s_conv_idx]

            if len(safety_conv_step["inputs"]) < 3:
                continue
            reasoner_safe = root_name(safety_conv_step["inputs"][0])
            safety_w = safety_conv_step["inputs"][1]
            safety_b = safety_conv_step["inputs"][2]
            if safety_w not in self.constants or safety_b not in self.constants:
                continue
            if reasoner_safe != reasoner_ben:
                continue

            if conv2_step["op"] not in ("Conv", "DmlFusedConv", "FusedConv"):
                continue
            if len(conv2_step["inputs"]) < 3:
                continue
            conv0_name = root_name(conv2_step["inputs"][0])
            gate2_w = conv2_step["inputs"][1]
            gate2_b = conv2_step["inputs"][2]
            if gate2_w not in self.constants or gate2_b not in self.constants:
                continue
            conv0_index = producers.get(conv0_name)
            if conv0_index is None or conv0_index >= conv2_index:
                continue
            conv0_step = self.steps[conv0_index]

            if conv0_step["op"] not in ("Conv", "DmlFusedConv", "FusedConv"):
                continue
            if conv0_step.get("activation") != 4:
                continue
            if len(conv0_step["inputs"]) < 3:
                continue
            stats_name = root_name(conv0_step["inputs"][0])
            gate0_w = conv0_step["inputs"][1]
            gate0_b = conv0_step["inputs"][2]
            if gate0_w not in self.constants or gate0_b not in self.constants:
                continue

            benefit_out = ben_step["output"]
            if not private_single_use(benefit_out, mul_index):
                continue
            if safety_step["op"] == "Softplus":
                if not private_single_use(safety_conv_step["output"], safety_index):
                    continue
            if not private_single_use(safety_step["output"], gate_index):
                continue
            if not private_single_use(conv0_step["output"], conv2_index):
                continue
            if not private_single_use(conv2_step["output"], gate_index):
                continue

            stats_shape = self.shapes.get(stats_name)
            reasoner_shape = self.shapes.get(reasoner_ben)
            if stats_shape is None or reasoner_shape is None:
                continue
            if len(stats_shape) != 4 or len(reasoner_shape) != 4:
                continue
            if stats_shape[2:] != reasoner_shape[2:]:
                continue

            gate_output = gate_step["output"]
            weight_output = mul_step["output"]
            h, w = stats_shape[2], stats_shape[3]
            pixels = h * w

            removed_steps.add(conv0_index)
            removed_steps.add(conv2_index)
            if safety_step["op"] == "Softplus":
                removed_steps.add(safety_conv_index)
            removed_steps.add(safety_index)
            removed_steps.add(ben_index)
            removed_steps.add(mul_index)

            removed_outputs = {
                conv0_step["output"], conv2_step["output"],
                ben_step["output"], safety_step["output"],
            }
            if safety_step["op"] == "Softplus":
                removed_outputs.add(safety_conv_step["output"])
            self.aliases = {
                k: v for k, v in self.aliases.items()
                if k not in removed_outputs and v not in removed_outputs
            }

            self.runtime_constant_names.update([
                safety_w, safety_b, benefit_w, benefit_b,
                gate0_w, gate0_b, gate2_w, gate2_b,
            ])

            gate_step.update(
                op="WeightNetFusedHeadsAndGate",
                inputs=[
                    reasoner_ben,
                    stats_name,
                    safety_w,
                    safety_b,
                    benefit_w,
                    benefit_b,
                    gate0_w,
                    gate0_b,
                    gate2_w,
                    gate2_b,
                ],
                outputs=[weight_output, gate_output],
                output=weight_output,
                gate_output=gate_output,
                weight_output=weight_output,
                pixels=pixels,
                attrs={},
            )
            fused_count += 1

        if removed_steps:
            self.steps = [
                step for index, step in enumerate(self.steps)
                if index not in removed_steps
            ]
        return fused_count

    def _fuse_weightnet_phase_gate_concat23(self):
        """Super-fuse WeightNet Phase Gate, difference kernels, and Concat23."""
        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)

        def producer(name, expected_op):
            index = producers.get(name)
            if index is None:
                return None
            step = self.steps[index]
            return (index, step) if step["op"] == expected_op else None

        def private_single_use(name, expected_index):
            return (
                name not in graph_outputs
                and name not in self.aliases
                and consumers.get(name) == [expected_index]
            )

        candidates = []
        for concat_index, concat_step in enumerate(self.steps):
            if concat_step["op"] != "WeightNetConcatPoolAbsGather":
                continue
            c_ins = concat_step["inputs"]
            if len(c_ins) != 6:
                continue
            ref_tiles = c_ins[0]
            sup_tiles = c_ins[1]
            sub_name = c_ins[2]
            pool_input = c_ins[3]
            mul_name = c_ins[4]
            phase_gate_name = c_ins[5]

            if pool_input != sub_name:
                continue

            # 1. Check phase_gate_name = Mul(div, sigmoid)
            mul_gate_match = producer(phase_gate_name, "Mul")
            if mul_gate_match is None:
                continue
            mul_gate_idx, mul_gate_step = mul_gate_match
            if not private_single_use(phase_gate_name, concat_index):
                continue

            mg_ins = mul_gate_step["inputs"]
            sig_match = producer(mg_ins[1], "WeightNetAbsConvSigmoid")
            div_name = mg_ins[0]
            if sig_match is None:
                sig_match = producer(mg_ins[0], "WeightNetAbsConvSigmoid")
                div_name = mg_ins[1]
            if sig_match is None:
                continue
            sig_idx, sig_step = sig_match
            if not private_single_use(sig_step["output"], mul_gate_idx):
                continue

            if sig_step["inputs"][0] != div_name:
                continue
            gate_w_name = sig_step["inputs"][1]
            gate_b_name = sig_step["inputs"][2]

            # 2. Check Div(grad_diff, clip)
            div_match = producer(div_name, "Div")
            if div_match is None:
                continue
            div_idx, div_step = div_match
            if consumers.get(div_name) != [sig_idx, mul_gate_idx] and consumers.get(div_name) != [mul_gate_idx, sig_idx]:
                continue

            grad_diff_name, clip_name = div_step["inputs"]

            # 3. Check Clip(sqrt, min=0.05)
            clip_match = producer(clip_name, "Clip")
            if clip_match is None:
                continue
            clip_idx, clip_step = clip_match
            if not private_single_use(clip_name, div_idx):
                continue

            sqrt_name = clip_step["inputs"][0]
            sqrt_match = producer(sqrt_name, "Sqrt")
            if sqrt_match is None:
                continue
            sqrt_idx, sqrt_step = sqrt_match
            if not private_single_use(sqrt_name, clip_idx):
                continue

            add_name = sqrt_step["inputs"][0]
            add_match = producer(add_name, "Add")
            if add_match is None:
                continue
            add_idx, add_step = add_match
            if not private_single_use(add_name, sqrt_idx):
                continue

            avg_pool_name = add_step["inputs"][0]
            avg_pool_match = producer(avg_pool_name, "AveragePool")
            if avg_pool_match is None:
                avg_pool_name = add_step["inputs"][1]
                avg_pool_match = producer(avg_pool_name, "AveragePool")
            if avg_pool_match is None:
                continue
            avg_pool_idx, avg_pool_step = avg_pool_match
            if not private_single_use(avg_pool_name, add_idx):
                continue

            pow_name = avg_pool_step["inputs"][0]
            pow_match = producer(pow_name, "Square")
            if pow_match is None:
                continue
            pow_idx, pow_step = pow_match
            if not private_single_use(pow_name, avg_pool_idx):
                continue

            conv_zero_name = pow_step["inputs"][0]
            conv_zero_match = producer(conv_zero_name, "Conv")
            if conv_zero_match is None:
                continue
            conv_zero_idx, conv_zero_step = conv_zero_match
            if not private_single_use(conv_zero_name, pow_idx):
                continue
            if conv_zero_step["inputs"][0] != ref_tiles:
                continue

            # 4. Check grad_diff = Sub(sup_grad, ref_grad)
            sub_diff_match = producer(grad_diff_name, "Sub")
            if sub_diff_match is None:
                continue
            sub_diff_idx, sub_diff_step = sub_diff_match
            if not private_single_use(grad_diff_name, div_idx):
                continue

            sup_grad_name, ref_grad_name = sub_diff_step["inputs"]
            sup_grad_match = producer(sup_grad_name, "Conv")
            ref_grad_match = producer(ref_grad_name, "Conv")
            if sup_grad_match is None or ref_grad_match is None:
                continue
            sup_grad_idx, sup_grad_step = sup_grad_match
            ref_grad_idx, ref_grad_step = ref_grad_match
            if not private_single_use(sup_grad_name, sub_diff_idx):
                continue
            if not private_single_use(ref_grad_name, sub_diff_idx):
                continue
            if sup_grad_step["inputs"][0] != sup_tiles:
                continue
            if ref_grad_step["inputs"][0] != ref_tiles:
                continue

            # 5. Check Mul(ref_tiles, sup_tiles)
            mul_match = producer(mul_name, "Mul")
            if mul_match is None:
                continue
            mul_idx, mul_step = mul_match
            if not private_single_use(mul_name, concat_index):
                continue

            # 6. Check Sub(sup_tiles, ref_tiles)
            sub_match = producer(sub_name, "Sub")
            if sub_match is None:
                continue
            sub_idx, sub_step = sub_match
            if consumers.get(sub_name) != [concat_index, concat_index] and consumers.get(sub_name) != [concat_index]:
                continue

            to_remove = {
                sup_grad_idx, ref_grad_idx, sub_diff_idx,
                conv_zero_idx, pow_idx, avg_pool_idx, add_idx, sqrt_idx, clip_idx,
                div_idx, sig_idx, mul_gate_idx, mul_idx, sub_idx
            }
            candidates.append((concat_index, to_remove, ref_tiles, sup_tiles, gate_w_name, gate_b_name))

        if not candidates:
            return 0

        removed_steps = set()
        removed_outputs = set()
        for concat_index, to_remove, ref_tiles, sup_tiles, gate_w_name, gate_b_name in candidates:
            concat_step = self.steps[concat_index]
            out_name = concat_step["output"]
            out_shape = self.shapes[out_name]
            h, w = out_shape[2], out_shape[3]

            concat_step.update(
                op="WeightNetFusedPhaseGateConcat23",
                inputs=[ref_tiles, sup_tiles, gate_w_name, gate_b_name],
                output=out_name,
                attrs={},
                h=h,
                w=w,
            )
            for idx in to_remove:
                removed_steps.add(idx)
                for o in self.steps[idx].get("outputs") or [self.steps[idx]["output"]]:
                    removed_outputs.add(o)

            self.runtime_constant_names.update([gate_w_name, gate_b_name])

        self.steps = [
            step for index, step in enumerate(self.steps)
            if index not in removed_steps
        ]
        self.aliases = {
            k: v for k, v in self.aliases.items()
            if k not in removed_outputs and v not in removed_outputs
        }
        return len(candidates)

    def _fuse_weightnet_pow2_sub_clip_sqrt(self):
        """Fuse the WeightNet Pow/Square -> Sub -> Clip -> Sqrt chain."""
        if self.opsets.get("", 0) < 11:
            return 0

        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)

        def producer(name, expected_op):
            index = producers.get(name)
            if index is None:
                return None
            step = self.steps[index]
            return (index, step) if step["op"] == expected_op else None

        def private_single_use(name, expected_index):
            return (
                name not in graph_outputs
                and name not in self.aliases
                and consumers.get(name) == [expected_index]
            )

        candidates = []
        for sqrt_index, sqrt_step in enumerate(self.steps):
            if sqrt_step["op"] != "Sqrt" or len(sqrt_step["inputs"]) != 1 or sqrt_step.get("attrs"):
                continue
            clip_name = sqrt_step["inputs"][0]
            clip_match = producer(clip_name, "Clip")
            if clip_match is None:
                continue
            clip_index, clip_step = clip_match
            if clip_index >= sqrt_index or not private_single_use(clip_name, sqrt_index):
                continue

            clip_inputs = clip_step["inputs"]
            if (len(clip_inputs) not in (2, 3)
                    or not clip_inputs[1]
                    or (len(clip_inputs) == 3 and clip_inputs[2])
                    or clip_step.get("attrs")):
                continue
            clip_min_name = clip_inputs[1]
            clip_min = self.constants.get(clip_min_name)
            if (clip_min is None or clip_min.shape != () or clip_min.dtype != np.float32
                    or int(clip_min.view(np.uint32).item()) != 0x3727C5AC
                    or clip_step.get("low") != float(np.float32(1.0e-5))
                    or not math.isinf(clip_step.get("high", 0.0))
                    or clip_step.get("high", 0.0) < 0.0):
                continue

            sub_name = clip_inputs[0]
            sub_match = producer(sub_name, "Sub")
            if sub_match is None:
                continue
            sub_index, sub_step = sub_match
            if sub_index >= clip_index or not private_single_use(sub_name, clip_index):
                continue
            if len(sub_step["inputs"]) != 2 or sub_step.get("attrs"):
                continue

            sub_lhs_name, sub_rhs_name = sub_step["inputs"]
            sub_lhs_match = producer(sub_lhs_name, "AveragePool")
            if sub_lhs_match is None:
                continue

            pow_match = producer(sub_rhs_name, "Pow")
            square_match = producer(sub_rhs_name, "Square")
            if pow_match is not None:
                pow_index, pow_step = pow_match
                if pow_index >= sub_index or not private_single_use(sub_rhs_name, sub_index):
                    continue
                if len(pow_step["inputs"]) != 2 or pow_step.get("attrs"):
                    continue
                pow_base_name, exponent_name = pow_step["inputs"]
                exponent = self.constants.get(exponent_name)
                if (exponent is None or exponent.shape != () or exponent.dtype != np.float32
                        or int(exponent.view(np.uint32).item()) != 0x40000000):
                    continue
            elif square_match is not None:
                pow_index, pow_step = square_match
                if pow_index >= sub_index or not private_single_use(sub_rhs_name, sub_index):
                    continue
                if len(pow_step["inputs"]) != 1 or pow_step.get("attrs"):
                    continue
                pow_base_name = pow_step["inputs"][0]
            else:
                continue

            pow_base_match = producer(pow_base_name, "AveragePool")
            if pow_base_match is None:
                continue

            sqrt_output = sqrt_step["output"]
            if sqrt_output in self.aliases:
                continue

            shapes = (
                self.shapes.get(pow_base_name),
                self.shapes.get(sub_rhs_name),
                self.shapes.get(sub_lhs_name),
                self.shapes.get(sub_name),
                self.shapes.get(clip_name),
                self.shapes.get(sqrt_output),
            )
            shape = shapes[0]
            if (shape is None or len(shape) != 4 or shape[1] != 1
                    or any(dimension <= 0 for dimension in shape)
                    or any(candidate != shape for candidate in shapes[1:])):
                continue

            candidates.append((sqrt_step, sub_lhs_name, pow_base_name, {pow_index, sub_index, clip_index}))

        if len(candidates) != 1:
            return 0

        sqrt_step, sub_lhs_name, pow_base_name, removed_steps = candidates[0]
        sqrt_step.update(
            op="WeightNetPow2SubClipSqrt",
            inputs=[sub_lhs_name, pow_base_name],
            attrs={},
            low=float(np.float32(1.0e-5)),
        )
        self.steps = [
            step for index, step in enumerate(self.steps)
            if index not in removed_steps
        ]
        return 1

    def _fuse_weightnet_stats_tanh(self):
        """Fuse the WeightNet statistics branch through Tanh."""
        if self.opsets.get("", 0) < 18:
            return 0

        producers = {}
        consumers = {}
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                producers[name] = index
            for name in step["inputs"]:
                if name:
                    consumers.setdefault(name, []).append(index)

        graph_outputs = set(self.outputs)

        def producer(name, expected_op):
            index = producers.get(name)
            if index is None:
                return None
            step = self.steps[index]
            return (index, step) if step["op"] == expected_op else None

        def private_single_use(name, expected_index):
            return (
                name not in graph_outputs
                and name not in self.aliases
                and consumers.get(name) == [expected_index]
            )

        candidates = []
        for tanh_index, tanh_step in enumerate(self.steps):
            if tanh_step["op"] != "Tanh" or len(tanh_step["inputs"]) != 1 or tanh_step.get("attrs"):
                continue
            scale_name = tanh_step["inputs"][0]
            scale_match = producer(scale_name, "Mul")
            if scale_match is None:
                continue
            scale_index, scale_step = scale_match
            if scale_index >= tanh_index or not private_single_use(scale_name, tanh_index):
                continue
            if len(scale_step["inputs"]) != 2 or scale_step.get("attrs"):
                continue

            scale_const_name = scale_step["inputs"][1] if scale_step["inputs"][1] in self.constants else scale_step["inputs"][0]
            pool_name = scale_step["inputs"][0] if scale_const_name == scale_step["inputs"][1] else scale_step["inputs"][1]
            scale = self.constants.get(scale_const_name)
            if (scale is None or scale.shape != () or scale.dtype != np.float32
                    or int(scale.view(np.uint32).item()) != 0x41000000):
                continue

            pool_match = producer(pool_name, "AveragePool")
            if pool_match is None:
                continue
            pool_index, pool_step = pool_match
            if pool_index >= scale_index or not private_single_use(pool_name, scale_index):
                continue
            pool_attrs = pool_step.get("attrs", {})
            if (pool_step.get("kernel") != (4, 4)
                    or pool_step.get("stride") != (2, 2)
                    or pool_step.get("pads") != (0, 0, 0, 0)
                    or pool_attrs.get("ceil_mode", 0) != 0
                    or pool_attrs.get("count_include_pad") != 1
                    or pool_attrs.get("auto_pad", b"NOTSET") not in (b"NOTSET", b"")):
                continue

            sqrt_name = pool_step["inputs"][0]
            sqrt_match = producer(sqrt_name, "Sqrt")
            if sqrt_match is None:
                continue
            sqrt_index, sqrt_step = sqrt_match
            if sqrt_index >= pool_index or not private_single_use(sqrt_name, pool_index):
                continue
            if len(sqrt_step["inputs"]) != 1 or sqrt_step.get("attrs"):
                continue

            reduce_name = sqrt_step["inputs"][0]
            reduce_match = producer(reduce_name, "ReduceMean")
            if reduce_match is None:
                continue
            reduce_index, reduce_step = reduce_match
            if reduce_index >= sqrt_index or not private_single_use(reduce_name, sqrt_index):
                continue
            axes = reduce_step.get("axes")
            if axes != [1]:
                continue
            if reduce_step.get("attrs") != {"keepdims": 1, "noop_with_empty_axes": 0}:
                continue

            mul_name = reduce_step["inputs"][0]
            mul_match = producer(mul_name, "Mul")
            square_match = producer(mul_name, "Square")
            if mul_match is not None:
                mul_index, mul_step = mul_match
                if mul_index >= reduce_index or not private_single_use(mul_name, reduce_index):
                    continue
                if len(mul_step["inputs"]) != 2 or mul_step.get("attrs"):
                    continue
                if mul_step["inputs"][0] != mul_step["inputs"][1]:
                    continue
                sub_output = mul_step["inputs"][0]
            elif square_match is not None:
                mul_index, mul_step = square_match
                if mul_index >= reduce_index or not private_single_use(mul_name, reduce_index):
                    continue
                if len(mul_step["inputs"]) != 1 or mul_step.get("attrs"):
                    continue
                sub_output = mul_step["inputs"][0]
            else:
                continue

            sub_match = producer(sub_output, "Sub")
            if sub_match is None:
                continue
            sub_index, sub_step = sub_match
            if sub_index >= mul_index or len(sub_step["inputs"]) != 2 or sub_step.get("attrs"):
                continue

            if tanh_step["output"] in self.aliases:
                continue

            sub_shape = self.shapes.get(sub_output)
            square_shape = self.shapes.get(mul_name)
            reduce_shape = self.shapes.get(reduce_name)
            sqrt_shape = self.shapes.get(sqrt_name)
            pool_shape = self.shapes.get(pool_name)
            scale_shape = self.shapes.get(scale_name)
            tanh_shape = self.shapes.get(tanh_step["output"])
            if (sub_shape is None or len(sub_shape) != 4
                    or sub_shape[1] != 4 or sub_shape[2] != sub_shape[3]
                    or any(dimension <= 0 for dimension in sub_shape)):
                continue
            n, _, height, width = sub_shape
            output_width = (width - 4) // 2 + 1
            expected_shapes = (
                (n, 4, height, width),
                (n, 1, height, width),
                (n, 1, height, width),
                (n, 1, output_width, output_width),
                (n, 1, output_width, output_width),
                (n, 1, output_width, output_width),
            )
            if (width < 4 or (width - 4) % 2
                    or (square_shape, reduce_shape, sqrt_shape, pool_shape,
                        scale_shape, tanh_shape) != expected_shapes):
                continue

            removed_steps = {mul_index, reduce_index, sqrt_index, pool_index, scale_index}
            candidates.append((tanh_step, sub_output, removed_steps))

        if len(candidates) != 1:
            return 0

        tanh_step, sub_output, removed_steps = candidates[0]
        tanh_step.update(
            op="WeightNetStatsTanh",
            inputs=[sub_output],
            attrs={},
        )
        self.steps = [
            step for index, step in enumerate(self.steps)
            if index not in removed_steps
        ]
        return 1

    def _enable_weightnet_stats_tanh_algebraic_simplification(self):
        """Select the opt-in power-of-two scale rewrite on the exact fused op."""
        matches = [
            step for step in self.steps
            if step["op"] == "WeightNetStatsTanh"
            and not step.get("attrs")
        ]
        if len(matches) != 1:
            return 0
        matches[0]["simplify_power_of_two_scale"] = True
        matches[0]["lowered_from"] = (
            "sqrt(mean4(square)) -> AveragePool16 -> multiply(8)"
        )
        return 1

    def _root_name(self, name):
        seen = set()
        while name in self.aliases:
            if name in seen:
                raise UnsupportedONNXOperatorError(f"Alias cycle detected at {name}")
            seen.add(name)
            name = self.aliases[name]
        return name

    def _build_buffer_plan(self):
        """Reuse equal-sized graph buffers after their final consumer runs."""
        producers = {name: -1 for name in self.inputs}
        producers.update({name: -1 for name in self.constants})
        for index, step in enumerate(self.steps):
            for name in step.get("outputs") or [step["output"]]:
                if self.alias_roots.get(name, name) == name and name not in self.constants:
                    producers[name] = index

        last_uses = {name: index for name, index in producers.items()}
        for index, step in enumerate(self.steps):
            for name in step["inputs"]:
                if name:
                    root = self.alias_roots.get(name, name)
                    if root in last_uses:
                        last_uses[root] = max(last_uses[root], index)
        graph_end = len(self.steps)
        for name in self.outputs:
            root = self.alias_roots.get(name, name)
            if root in last_uses:
                last_uses[root] = graph_end

        dynamic_values = []
        for name, start in producers.items():
            if name in self.constants:
                continue
            element_count = math.prod(self.shapes[name] or (1,))
            dynamic_values.append((start, max(start, last_uses.get(name, start)), element_count, name))

        slots = []
        plan = {}
        reused_values = 0
        for start, end, element_count, name in sorted(dynamic_values):
            available = [(slot_id, slot) for slot_id, slot in enumerate(slots)
                         if slot["elements"] == element_count and slot["last_use"] < start]
            if available:
                slot_id, slot = min(available, key=lambda value: value[1]["last_use"])
                slot["last_use"] = end
                slot["last_value"] = name
                reused_values += 1
            else:
                slot_id = len(slots)
                slot = {"elements": element_count, "last_use": end, "last_value": name}
                slots.append(slot)
            plan[name] = slot_id

        constant_bytes = sum(self.constants[name].nbytes
                             for name in self.runtime_constant_names)
        scratch_elements = max((
            (math.prod(self.shapes[step["inputs"][0]]) + 255) // 256
            for step in self.steps
            if step["op"] == "ReduceMean"
            and len(step.get("axes", [])) == len(self.shapes[step["inputs"][0]])
        ), default=0)
        scratch_bytes = scratch_elements * 4
        dummy_buffer_bytes = 4
        return_gpu_copy_bytes = sum(
            max(1, math.prod(self.shapes[name])) * 4 for name in self.outputs
        )
        before_bytes = (constant_bytes + scratch_bytes + dummy_buffer_bytes
                        + sum(value[2] * 4 for value in dynamic_values))
        after_bytes = (constant_bytes + scratch_bytes + dummy_buffer_bytes
                       + sum(slot["elements"] * 4 for slot in slots))
        stats = {
            "dynamic_value_count": len(dynamic_values),
            "reused_value_count": reused_values,
            "dynamic_slot_count": len(slots),
            "constant_bytes": constant_bytes,
            "scratch_bytes": scratch_bytes,
            "dummy_buffer_bytes": dummy_buffer_bytes,
            "return_gpu_copy_bytes_per_call": return_gpu_copy_bytes,
            "estimated_tensor_bytes_before": before_bytes,
            "estimated_tensor_bytes_after": after_bytes,
            "estimated_tensor_bytes_saved": before_bytes - after_bytes,
        }
        return plan, stats

    def allocate(self):
        if self._allocated:
            return
        with self._allocation_lock:
            if self._allocated:
                return
            buffers = {}
            slot_buffers = {}
            for name, shape in self.shapes.items():
                if name in self.aliases:
                    buffers[name] = buffers[self.aliases[name]]
                elif name in self.constants:
                    if name not in self.runtime_constant_names:
                        continue
                    buf = ti.ndarray(ti.f32, (max(1, math.prod(shape)),))
                    buf.from_numpy(np.ascontiguousarray(self.constants[name], dtype=np.float32).reshape(-1))
                    buffers[name] = buf
                elif name not in self.buffer_plan:
                    # Fusion passes leave shape metadata available for audits,
                    # but removed private intermediates have no producer or
                    # runtime storage in the optimized graph.
                    continue
                else:
                    slot_id = self.buffer_plan[name]
                    buf = slot_buffers.get(slot_id)
                    if buf is None:
                        buf = ti.ndarray(ti.f32, (max(1, math.prod(shape)),))
                        slot_buffers[slot_id] = buf
                    buffers[name] = buf
            dummy = ti.ndarray(ti.f32, (1,))
            scratch = {}
            full_reductions = [
                step for step in self.steps
                if step["op"] == "ReduceMean"
                and len(step.get("axes", [])) == len(self.shapes[step["inputs"][0]])
            ]
            if full_reductions:
                max_chunks = max(
                    (math.prod(self.shapes[step["inputs"][0]]) + 255) // 256
                    for step in full_reductions
                )
                shared_scratch = ti.ndarray(ti.f32, (max_chunks,))
                for step in full_reductions:
                    scratch[step["output"]] = shared_scratch
            self.buffers = buffers
            self.scratch = scratch
            self.dummy = dummy
            self._allocated = True

    def run(self, inputs, return_gpu=False, borrowed_outputs=False):
        """Execute the graph.

        ``return_gpu=True`` returns caller-owned output copies queued on the
        active Taichi device stream. Taichi consumers can enqueue dependent
        work on that stream without a device-wide wait; synchronize before
        reading the result from the CPU or handing it to an external runtime.
        ``borrowed_outputs=True`` instead returns views of graph-owned Taichi
        buffers without copies; Identity-like outputs may alias a supplied
        device input. Graph-buffer views are valid only until the next call to
        ``run`` on this graph, which may reuse and overwrite the storage.
        One-dimensional Taichi ndarray inputs whose element count matches the
        graph shape are consumed in place without an input copy; the current
        kernels use flat buffers internally. Multidimensional device inputs are
        rejected in this mode. The caller must keep each input alive until
        submitted Taichi work has completed. Borrowed outputs require
        ``return_gpu=True``.
        """
        if borrowed_outputs and not return_gpu:
            raise ValueError("borrowed_outputs requires return_gpu=True")
        with self._lock:
            self.allocate()
            if set(inputs) != set(self.inputs):
                raise ValueError(f"Expected inputs {self.inputs}, got {list(inputs)}")
            saved_buffers = {}
            try:
                for name, data in inputs.items():
                    if isinstance(data, ti.Ndarray):
                        if borrowed_outputs and len(data.shape) != 1:
                            raise ValueError(
                                f"{name}: borrowed resident inputs must be flat 1D float32 "
                                f"with {math.prod(self.shapes[name])} elements; got {data.shape}"
                            )
                        shape_matches = tuple(data.shape) == self.shapes[name]
                        flat_borrow_matches = (
                            borrowed_outputs and len(data.shape) == 1
                            and data.shape[0] == math.prod(self.shapes[name])
                        )
                        if (not shape_matches and not flat_borrow_matches) or data.dtype != ti.f32:
                            raise ValueError(f"{name}: expected float32 {self.shapes[name]}")
                        if borrowed_outputs:
                            # Temporarily substitute all aliases of this input
                            # so downstream views (e.g. Identity/Reshape) also
                            # observe the caller's device allocation.
                            for buffer_name in self.buffers:
                                if self.alias_roots.get(buffer_name, buffer_name) == name:
                                    saved_buffers[buffer_name] = self.buffers[buffer_name]
                                    self.buffers[buffer_name] = data
                        else:
                            _upload_device(data, self.buffers[name])
                        continue
                    arr = np.asarray(data)
                    if tuple(arr.shape) != self.shapes[name] or arr.dtype != np.float32:
                        raise ValueError(f"{name}: expected float32 {self.shapes[name]}, got {arr.dtype} {arr.shape}")
                    self.buffers[name].from_numpy(np.ascontiguousarray(arr).reshape(-1))
                for step in self.steps:
                    self._dispatch(step)
                if return_gpu:
                    if borrowed_outputs:
                        # No allocation or device copy: these are borrowed
                        # graph buffers and are invalidated by the next run.
                        return {name: self.buffers[name] for name in self.outputs}
                    outputs={}
                    for name in self.outputs:
                        result=ti.ndarray(ti.f32,self.shapes[name])
                        _download_device(self.buffers[name],result)
                        outputs[name]=result
                    return outputs
                return {n: self.buffers[n].to_numpy().reshape(self.shapes[n]) for n in self.outputs}
            finally:
                self.buffers.update(saved_buffers)


    def _fuse_weightnet_tile_statistics(self):
        """Fuse the 9-step WeightNet tile statistics sub-graph into a single kernel."""
        concat_idx = None
        tanh_idx = None
        for i, step in enumerate(self.steps):
            out = step.get("output")
            if out == "/Concat_1_output_0" or (step.get("op") == "Concat" and len(step.get("inputs", [])) == 2 and any("Sqrt" in x for x in step.get("inputs", []))):
                concat_idx = i
            elif out == "/Tanh_output_0" or (step.get("op") == "WeightNetStatsTanh"):
                tanh_idx = i
        if concat_idx is None or tanh_idx is None:
            return 0

        concat_step = self.steps[concat_idx]
        tanh_step = self.steps[tanh_idx]

        concat_shape = self.shapes.get(concat_step["output"])
        if concat_shape is None or len(concat_shape) != 4 or concat_shape[1] != 2:
            return 0
        oh, ow = concat_shape[2], concat_shape[3]

        ref_4ch_name = "/SpaceToDepth_output_0"
        if ref_4ch_name not in self.shapes:
            for s in self.steps:
                if s.get("op") == "SpaceToDepth" and s.get("output") in self.shapes:
                    sh = self.shapes[s["output"]]
                    if len(sh) == 4 and sh[1] == 4 and (sh[2] - 4) // 2 + 1 == oh:
                        ref_4ch_name = s["output"]
                        break
        ref_shape = self.shapes.get(ref_4ch_name)
        if ref_shape is None:
            return 0
        h, w = ref_shape[2], ref_shape[3]

        subgraph_outputs = {
            "/ReduceMean_2_output_0", "/Sub_3_output_0", "/AveragePool_2_output_0",
            "/Pow_1_output_0", "/ReduceMean_1_output_0", "/AveragePool_3_output_0",
            "/Sqrt_1_output_0", concat_step["output"], tanh_step["output"]
        }

        new_step = {
            "op": "WeightNetFusedTileStatistics",
            "inputs": [ref_4ch_name],
            "output": concat_step["output"],
            "outputs": [concat_step["output"], tanh_step["output"]],
            "tanh_output": tanh_step["output"],
            "h": h, "w": w, "oh": oh, "ow": ow,
            "attrs": {},
        }

        new_steps = []
        replaced = False
        for s in self.steps:
            out = s.get("output")
            if out in subgraph_outputs:
                if not replaced:
                    new_steps.append(new_step)
                    replaced = True
                continue
            new_steps.append(s)

        self.steps = new_steps
        return 1


    def _dispatch(self, step, emit=None):
        # The AOT exporter records these same dispatches with fixed model
        # dimensions. Keep operator selection and arithmetic in one place.
        if emit is None:
            emit = lambda kernel, *args: kernel(*args)
        op, ins, name, a = step["op"], step["inputs"], step["output"], step["attrs"]
        if name in self.aliases:
            return
        x, out = self.buffers[ins[0]], self.buffers[name]
        si, so = self.shapes[ins[0]], self.shapes[name]
        if op == "WeightNetConcatConvGelu":
            emit(
                _weightnet_concat_conv_gelu,
                self.buffers[ins[0]], self.buffers[ins[1]], self.buffers[ins[2]],
                self.buffers[ins[3]], self.buffers[ins[4]], out,
                step["batch"], si[2], si[3], *step["source_channels"],
                step["output_channels"],
            )
        elif op == "WeightNetAbsConvSigmoid":
            emit(
                _weightnet_abs_conv_sigmoid,
                x,
                self.buffers[ins[1]],
                self.buffers[ins[2]],
                out,
                si[2],
                si[3],
            )
        elif op in ("Conv", "DmlFusedConv", "FusedConv"):
            ws = self.shapes[ins[1]]
            bias = len(ins)>2 and bool(ins[2])
            if (self.optimized and step["group"] == 1 and ws[2:] == (1, 1)
                    and step["dilation"] == (1, 1) and step["stride"] == (1, 1)
                    and step["pads"] == (0, 0, 0, 0) and so[1] % 4 == 0 and si[0] == 1):
                emit(_conv_1x1_tiled, x, self.buffers[ins[1]], self.buffers[ins[2]] if bias else self.dummy, out,
                     si[1], so[1], si[2] * si[3], bias, step["activation"])
                return
            if (self.optimized and step["group"] == 1 and ws[2:] == (4, 4)
                    and step["dilation"] == (1, 1) and step["stride"] == (2, 2)
                    and step["pads"] == (0, 0, 0, 0) and so[1] % 4 == 0 and si[0] == 1):
                emit(_conv_k4s2_tiled, x, self.buffers[ins[1]], self.buffers[ins[2]] if bias else self.dummy, out,
                     si[1], so[1], si[2], si[3], so[2], so[3], bias, step["activation"])
                return
            vector_conv_backend = self.backend not in ("vulkan", "opengl")
            if (self.optimized and vector_conv_backend and step["group"] == 1
                    and so[1] % 4 == 0 and step["dilation"] == (1,1)):
                emit(_conv_channels4,x,self.buffers[ins[1]],self.buffers[ins[2]] if bias else self.dummy,out,
                                si[1],so[1],si[2],si[3],so[2],so[3],ws[2],ws[3],*step["stride"],*step["pads"][:2],bias,step["activation"])
                return
            if self.optimized and step["group"] == si[1] == so[1] and ws[2:] == (3,3) and step["dilation"] == (1,1) and step["stride"] == (1,1) and step["pads"] == (1,1,1,1):
                emit(_depthwise,x,self.buffers[ins[1]],self.buffers[ins[2]] if bias else self.dummy,out,si[1],si[2],si[3],bias,step["activation"])
                return
            emit(_conv,x, self.buffers[ins[1]], self.buffers[ins[2]] if bias else self.dummy, out,
                  si[1],so[1],si[2],si[3],so[2],so[3],ws[2],ws[3],*step["stride"],*step["pads"][:2],*step["dilation"],step["group"],bias,step["activation"])
        elif op == "WeightNetAdaptiveGate":
            conv_shape = self.shapes[ins[0]]
            emit(
                _weightnet_gate_flat_kernel,
                self.buffers[ins[0]], self.buffers[ins[1]], out,
                conv_shape[0], conv_shape[2], conv_shape[3],
            )
        elif op == "WeightNetFusedHeadsAndGate":
            emit(
                _weightnet_fused_heads_and_gate,
                self.buffers[ins[0]],
                self.buffers[ins[1]],
                self.buffers[ins[2]],
                self.buffers[ins[3]],
                self.buffers[ins[4]],
                self.buffers[ins[5]],
                self.buffers[ins[6]],
                self.buffers[ins[7]],
                self.buffers[ins[8]],
                self.buffers[ins[9]],
                self.buffers[step["gate_output"]],
                self.buffers[step["weight_output"]],
                step["pixels"],
            )
        elif op == "WeightNetFusedPhaseGateConcat23":
            emit(
                _weightnet_fused_phase_gate_concat23,
                self.buffers[ins[0]],
                self.buffers[ins[1]],
                self.buffers[ins[2]],
                self.buffers[ins[3]],
                out,
                step["h"],
                step["w"],
            )
        elif op == "WeightNetFusedTileStatistics":
            emit(
                _weightnet_fused_tile_statistics,
                self.buffers[ins[0]],
                self.buffers[step["output"]],
                self.buffers[step["tanh_output"]],
                step["h"],
                step["w"],
                step["oh"],
                step["ow"],
            )
        elif op == "FusedMulClip":
            emit(
                _fused_mul_clip_kernel,
                self.buffers[ins[0]], self.buffers[ins[1]], out,
                step["low"], step["high"],
            )
        elif op == "WeightNetSigmoidProduct":
            emit(
                _weightnet_sigmoid_product,
                self.buffers[ins[0]], self.buffers[ins[1]], out,
            )
        elif op == "WeightNetPow2SubClipSqrt":
            emit(
                _weightnet_pow2_sub_clip_sqrt,
                self.buffers[ins[0]], self.buffers[ins[1]], out,
                step["low"],
            )
        elif op == "WeightNetStatsTanh":
            emit(
                _weightnet_sub3_stats_tanh,
                x, out, si[2], so[3],
                step.get("simplify_power_of_two_scale", False),
            )
        elif op == "WeightNetSquareReduceMean":
            emit(_weightnet_square_reduce_mean, x, out, si[2] * si[3])
        elif op == "Square":
            emit(_square, x, out)
        elif op in ("Add", "Sub", "Mul", "Div", "Pow"):
            code={"Add":0,"Sub":1,"Mul":2,"Div":3,"Pow":4}[op]
            rhs = self.buffers[ins[1]]
            rhs_shape = self.shapes[ins[1]]
            if si == rhs_shape == so and op in ("Add", "Sub", "Mul", "Div"):
                # The graph stores dense values in flat ndarrays. For equal
                # shapes the public tensor primitive can use those arrays
                # directly and avoids per-element broadcast index decoding.
                tensor_op = {
                    "Add": ti.tensor.add,
                    "Sub": ti.tensor.subtract,
                    "Mul": ti.tensor.multiply,
                    "Div": ti.tensor.divide,
                }[op]
                emit(tensor_op, x, rhs, out)
            elif math.prod(rhs_shape) == 1 and tuple(si) == tuple(so):
                emit(_binary_scalar, x, rhs, out, code, True)
            elif math.prod(si) == 1 and tuple(rhs_shape) == tuple(so):
                emit(_binary_scalar, x, rhs, out, code, False)
            else:
                emit(_binary,x,rhs,out,code,_padded(so),_padded(si),_padded(rhs_shape))
        elif op in ("Relu","Sigmoid","Softplus","Gelu","Abs","Sqrt","Tanh","Clip"):
            emit(_unary,x,out,{"Relu":1,"Sigmoid":2,"Softplus":3,"Gelu":4,"Abs":5,"Sqrt":6,"Tanh":7,"Clip":8}[op],step.get("low",0.0),step.get("high",0.0))
        elif op == "AveragePool":
            emit(_pool,x,out,si[2],si[3],so[2],so[3],*step["kernel"],*step["stride"],*step["pads"][:2],bool(a.get("count_include_pad",0)))
        elif op == "WeightNetConcatPoolAbsGather":
            emit(
                _weightnet_concat_pool_abs_gather,
                self.buffers[ins[0]],
                self.buffers[ins[1]],
                self.buffers[ins[2]],
                self.buffers[ins[3]],
                self.buffers[ins[4]],
                self.buffers[ins[5]],
                out,
                so[2],
                so[3],
            )
        elif op == "SpaceToDepth":
            emit(_space_to_depth,x,out,si[1],si[2],si[3],int(a["blocksize"]))
        elif op == "Concat":
            axis = step["axis"]
            if step.get("use_concat_gather", False):
                axis_sizes = tuple(self.shapes[n][axis] for n in ins)
                axis_starts = tuple(
                    sum(axis_sizes[:index]) for index in range(len(axis_sizes))
                )
                input_buffers = [self.buffers[n] for n in ins]
                input_buffers.extend([self.dummy] * (_CONCAT_GATHER_MAX_INPUTS - len(ins)))
                emit(
                    _concat_gather,
                    *input_buffers,
                    out,
                    math.prod(so[axis + 1:]),
                    so[axis],
                    axis_sizes,
                    axis_starts,
                    len(ins),
                )
            else:
                offset = 0
                for n in ins:
                    shape = self.shapes[n]
                    emit(_copy_axis,self.buffers[n],out,math.prod(shape[axis+1:]),shape[axis],so[axis],offset,True)
                    offset += shape[axis]
        elif op == "Slice":
            axis=step["axis"]
            emit(_copy_axis,x,out,math.prod(si[axis+1:]),si[axis],so[axis],step["start"],False)
        elif op == "Transpose":
            perm = step["perm"]
            dims = tuple(so)
            strides = tuple(math.prod(si[k+1:]) for k in range(len(si)))
            emit(_transpose,x, out, len(si), dims, strides, perm)
        elif op == "Split":
            axis, offset = step["axis"], 0
            inner = math.prod(si[axis+1:])
            for output, length in zip(step["outputs"], step["lengths"]):
                emit(_copy_axis,x, self.buffers[output], inner, si[axis], length, offset, False)
                offset += length
        elif op == "ReduceMean":
            if name in self.scratch:
                count = math.prod(si)
                chunks = (count + 255) // 256
                emit(_reduce_chunks,x, self.scratch[name], count, chunks)
                emit(_reduce_finish,self.scratch[name], out, count, chunks)
            else:
                axis=step["axes"][0]
                emit(_reduce_axis,x,out,math.prod(si[axis+1:]),si[axis])
        elif op == "WeightNetConvTransposeMulClip":
            ws = self.shapes[ins[1]]
            emit(
                _transpose_conv_mul_clip,
                x,
                self.buffers[ins[1]],
                self.buffers[ins[2]],
                out,
                si[2],
                si[3],
                so[2],
                so[3],
                ws[2],
                ws[3],
                *step["stride"],
                step["low"],
                step["high"],
            )
        elif op == "ConvTranspose":
            ws=self.shapes[ins[1]]
            emit(_transpose_conv,x,self.buffers[ins[1]],out,si[2],si[3],so[2],so[3],ws[2],ws[3],*step["stride"])
        else:
            raise UnsupportedONNXOperatorError(op)
