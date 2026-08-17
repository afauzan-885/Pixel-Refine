"""Native Bayer Pre-Demosaic & Standalone Highlight Recovery Kernels with Dynamic Range Compression."""

import taichi as ti


@ti.kernel
def highlight_recover_rgb(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g: ti.f32,
    wb_b: ti.f32,
    strength: ti.f32,
    h: ti.i32,
    w: ti.i32,
):
    """Pass-through & Standalone Highlight Recovery with Smoothstep Ratio Desaturation and Sigmoid Dynamic Range Compression."""
    inv_wb_r = 1.0 / ti.max(0.1, wb_r)
    inv_wb_g = 1.0 / ti.max(0.1, wb_g)
    inv_wb_b = 1.0 / ti.max(0.1, wb_b)

    for y, x in ti.ndrange(h, w):
        R = src[y, x, 0]
        G = src[y, x, 1]
        B = src[y, x, 2]

        # 1. Estimate RAW Bayer values
        R_raw = R * inv_wb_r
        G_raw = G * inv_wb_g
        B_raw = B * inv_wb_b

        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))

        # 2. Smoothstep highlight factor and neutrality factor
        factor = ti.math.clamp((max_raw - 0.55) / 0.43, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp((ratio - 0.40) / 0.45, 0.0, 1.0)
        neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

        final_factor = factor * neutrality * ti.math.clamp(strength, 0.0, 1.0)

        # 3. Blend in white-balanced space
        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - final_factor) + L * final_factor
        G = G * (1.0 - final_factor) + L * final_factor
        B = B * (1.0 - final_factor) + L * final_factor

        # 4. Apply Algebraic Sigmoid Dynamic Range Compression
        dst[y, x, 0] = R / ti.math.sqrt(1.0 + R * R)
        dst[y, x, 1] = G / ti.math.sqrt(1.0 + G * G)
        dst[y, x, 2] = B / ti.math.sqrt(1.0 + B * B)
