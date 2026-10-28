"""Opt-in CPU InstanceNormalization kernel matching ORT's Eigen packet-4 path."""

import taichi as ti


@ti.func
def _eigen_sse4_sum(x: ti.types.ndarray(ti.f32, 1), base: ti.i32,
                    spatial: ti.i32, align_start: ti.i32) -> ti.f32:
    packet_count = (spatial - align_start) // 4
    aligned_end = align_start + packet_count * 4
    aligned_end2 = align_start + (packet_count // 2) * 8
    result = 0.0

    if packet_count >= 2:
        # Eigen's LinearVectorizedTraversal uses two packet accumulators,
        # alternating consecutive packets between them.
        a0 = x[base + align_start]
        a1 = x[base + align_start + 1]
        a2 = x[base + align_start + 2]
        a3 = x[base + align_start + 3]
        b0 = x[base + align_start + 4]
        b1 = x[base + align_start + 5]
        b2 = x[base + align_start + 6]
        b3 = x[base + align_start + 7]
        for pair in range(1, packet_count // 2):
            offset = align_start + pair * 8
            a0 += x[base + offset]
            a1 += x[base + offset + 1]
            a2 += x[base + offset + 2]
            a3 += x[base + offset + 3]
            b0 += x[base + offset + 4]
            b1 += x[base + offset + 5]
            b2 += x[base + offset + 6]
            b3 += x[base + offset + 7]

        r0 = a0 + b0
        r1 = a1 + b1
        r2 = a2 + b2
        r3 = a3 + b3
        if packet_count % 2 != 0:
            r0 += x[base + aligned_end2]
            r1 += x[base + aligned_end2 + 1]
            r2 += x[base + aligned_end2 + 2]
            r3 += x[base + aligned_end2 + 3]

        # Eigen SSE predux: add opposite halves, then the low two lanes.
        low_pair = r0 + r2
        high_pair = r1 + r3
        result = low_pair + high_pair
    elif packet_count == 1:
        r0 = x[base + align_start]
        r1 = x[base + align_start + 1]
        r2 = x[base + align_start + 2]
        r3 = x[base + align_start + 3]
        low_pair = r0 + r2
        high_pair = r1 + r3
        result = low_pair + high_pair
    else:
        result = x[base]
        for index in range(1, spatial):
            result += x[base + index]
    if packet_count > 0:
        # Eigen adds scalar head/tail values after the packet reduction.
        for index in range(align_start):
            result += x[base + index]
        for index in range(aligned_end, spatial):
            result += x[base + index]
    return result


@ti.kernel
def nu_instance_norm_packet4_affine_candidate(
    x: ti.types.ndarray(ti.f32, 1),
    scale: ti.types.ndarray(ti.f32, 1),
    bias: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    spatial: ti.i32,
    eps: ti.f32,
    has_scale: ti.i32,
    has_bias: ti.i32,
):
    for idx in range(n_batch * channels):
        channel = idx % channels
        base = idx * spatial
        # CPU AOT buffers are aligned to at least 16 bytes. Each row starts
        # ``spatial`` float elements after the previous row.
        align_start = (4 - (idx * spatial) % 4) % 4
        mean_sum = _eigen_sse4_sum(x, base, spatial, align_start)
        mean = mean_sum / ti.cast(spatial, ti.f32)

        square_sum = 0.0
        if (spatial - align_start) >= 4:
            packet_count = (spatial - align_start) // 4
            aligned_end = align_start + packet_count * 4
            aligned_end2 = align_start + (packet_count // 2) * 8
            if packet_count >= 2:
                # Materialize centered values per logical coefficient before
                # squaring, matching Eigen's cwise-difference then squaredNorm.
                a0 = x[base + align_start] - mean
                a1 = x[base + align_start + 1] - mean
                a2 = x[base + align_start + 2] - mean
                a3 = x[base + align_start + 3] - mean
                b0 = x[base + align_start + 4] - mean
                b1 = x[base + align_start + 5] - mean
                b2 = x[base + align_start + 6] - mean
                b3 = x[base + align_start + 7] - mean
                a0 *= a0
                a1 *= a1
                a2 *= a2
                a3 *= a3
                b0 *= b0
                b1 *= b1
                b2 *= b2
                b3 *= b3
                for pair in range(1, packet_count // 2):
                    offset = align_start + pair * 8
                    v0 = x[base + offset] - mean
                    v1 = x[base + offset + 1] - mean
                    v2 = x[base + offset + 2] - mean
                    v3 = x[base + offset + 3] - mean
                    v0 *= v0
                    v1 *= v1
                    v2 *= v2
                    v3 *= v3
                    a0 += v0
                    a1 += v1
                    a2 += v2
                    a3 += v3
                    v0 = x[base + offset + 4] - mean
                    v1 = x[base + offset + 5] - mean
                    v2 = x[base + offset + 6] - mean
                    v3 = x[base + offset + 7] - mean
                    v0 *= v0
                    v1 *= v1
                    v2 *= v2
                    v3 *= v3
                    b0 += v0
                    b1 += v1
                    b2 += v2
                    b3 += v3

                r0 = a0 + b0
                r1 = a1 + b1
                r2 = a2 + b2
                r3 = a3 + b3
                if packet_count % 2 != 0:
                    offset = aligned_end2
                    v0 = x[base + offset] - mean
                    v1 = x[base + offset + 1] - mean
                    v2 = x[base + offset + 2] - mean
                    v3 = x[base + offset + 3] - mean
                    r0 += v0 * v0
                    r1 += v1 * v1
                    r2 += v2 * v2
                    r3 += v3 * v3
                low_pair = r0 + r2
                high_pair = r1 + r3
                square_sum = low_pair + high_pair
            else:
                r0 = x[base + align_start] - mean
                r1 = x[base + align_start + 1] - mean
                r2 = x[base + align_start + 2] - mean
                r3 = x[base + align_start + 3] - mean
                r0 *= r0
                r1 *= r1
                r2 *= r2
                r3 *= r3
                low_pair = r0 + r2
                high_pair = r1 + r3
                square_sum = low_pair + high_pair
            for index in range(align_start):
                centered = x[base + index] - mean
                square_sum += centered * centered
            for index in range(aligned_end, spatial):
                centered = x[base + index] - mean
                square_sum += centered * centered
        else:
            centered = x[base] - mean
            square_sum = centered * centered
            for index in range(1, spatial):
                centered = x[base + index] - mean
                square_sum += centered * centered

        variance = square_sum / ti.cast(spatial, ti.f32)
        inv_std = 1.0 / ti.sqrt(variance + eps)
        channel_scale = inv_std * (scale[channel] if has_scale != 0 else 1.0)
        channel_bias = bias[channel] if has_bias != 0 else 0.0
        channel_shift = channel_bias - mean * channel_scale
        for index in range(spatial):
            y[base + index] = x[base + index] * channel_scale + channel_shift


ALL_INSTANCE_NORM_CANDIDATE_KERNELS = [
    nu_instance_norm_packet4_affine_candidate,
]
