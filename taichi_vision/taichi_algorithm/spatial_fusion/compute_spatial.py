"""
Spatial Merging — Taichi AOT Kernels, Compiler, and Runtime Wrappers.

Canonical home of the ghost-reduction / multi-frame fusion kernels formerly
hosted in the application's ``spatial_core/similarity_taichi`` module.  The
application module now re-exports from here to keep one maintained
implementation.

Graphs packaged by ``compile_spatial_tcm`` (all float32):
    precompute_gradients, clear_f32_2d, equalize_brightness,
    phase1_coarse_analysis, phase2_fine_analysis,
    accumulate_spatial_merging, accumulate_spatial_merging_vec3,
    mean_division_vec3_weight, fine_analysis_and_accumulate,
    generate_fine_weights_4passes
"""

import numpy as np
import os
import zipfile
import sys
import importlib
from functools import lru_cache

# If run directly for compilation, force JIT mode
if __name__ == "__main__":
    os.environ["AOT_MODE"] = "0"

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

calculate_hybrid_gradient_optimized = None
calculate_match_confidence = None

if TAICHI_AVAILABLE:
    from .block_matching import (
        calculate_hybrid_gradient_optimized,
        calculate_match_confidence,
    )
else:
    class DummyTi:
        i32 = "int"
        f32 = "float"
        def kernel(self, f): return f
        def func(self, f): return f
        class Types:
            def ndarray(self, *args, **kwargs): return "ndarray"
        types = Types()
    ti = DummyTi()


@ti.kernel
def precompute_gradients_kernel(
    img: ti.types.ndarray(),
    grad_x: ti.types.ndarray(),
    grad_y: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32
):
    """Precomputes Sobel DX and DY gradients for the entire image to avoid redundant calculations inside windows."""
    for y, x in ti.ndrange(h, w):
        if 0 < y < h - 1 and 0 < x < w - 1:
            gx_center = img[y, x + 1] - img[y, x - 1]
            gx_top = img[y - 1, x + 1] - img[y - 1, x - 1]
            gx_bottom = img[y + 1, x + 1] - img[y + 1, x - 1]
            grad_x[y, x] = (gx_center + gx_top + gx_bottom) * 0.333

            grad_y[y, x] = img[y + 1, x] - img[y - 1, x]
        else:
            grad_x[y, x] = 0.0
            grad_y[y, x] = 0.0


@ti.kernel
def clear_f32_2d_kernel(
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
):
    """Clear a resident f32 plane without a host staging/upload round-trip."""
    for y, x in ti.ndrange(h, w):
        dst[y, x] = 0.0


@ti.kernel
def equalize_brightness_kernel(
    src: ti.types.ndarray(),
    ref: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32
):
    """Calculates global average ratio between src and ref and applies gain to dst."""
    sum_ref = 0.0
    sum_src = 0.0
    for i, j in ti.ndrange(h, w):
        sum_ref += ref[i, j]
        sum_src += src[i, j]

    ratio = 1.0
    if sum_src > 1e-5:
        ratio = sum_ref / sum_src

    # Clamp gain to [0.6, 1.8] to avoid extreme scaling
    ratio = ti.max(0.6, ti.min(1.8, ratio))

    for i, j in ti.ndrange(h, w):
        dst[i, j] = src[i, j] * ratio


@ti.kernel
def phase1_coarse_analysis_kernel(
    current_coarse: ti.types.ndarray(),
    reference_coarse: ti.types.ndarray(),
    coarse_grad_x: ti.types.ndarray(),
    coarse_grad_y: ti.types.ndarray(),
    ref_coarse_grad_x: ti.types.ndarray(),
    ref_coarse_grad_y: ti.types.ndarray(),
    coarse_confidence: ti.types.ndarray(),
    coarse_tile_h: ti.i32,
    coarse_tile_w: ti.i32,
    h_coarse: ti.i32,
    w_coarse: ti.i32,
    noise_sigma: ti.f32,
    motion_sensitivity: ti.f32,
    noise_offset_factor: ti.f32
):
    """Generates a coarse confidence map using hybrid gradient similarity."""
    # ``noise_sigma`` is invariant for the complete dispatch.  Hoist its
    # guarded reciprocal out of the per-tile confidence math so the kernel
    # performs one multiply instead of a max+divide for every coarse tile.
    inv_noise_sigma = 1.0 / ti.max(1e-6, noise_sigma)
    for r, c in coarse_confidence:
        tile_y = r * coarse_tile_h
        tile_x = c * coarse_tile_w
        curr_h = ti.min(coarse_tile_h, h_coarse - tile_y)
        curr_w = ti.min(coarse_tile_w, w_coarse - tile_x)

        if curr_h > 0 and curr_w > 0:
            mad_score = calculate_hybrid_gradient_optimized(
                current_coarse, reference_coarse,
                coarse_grad_x, coarse_grad_y,
                ref_coarse_grad_x, ref_coarse_grad_y,
                tile_y, tile_x,
                curr_h, curr_w, h_coarse, w_coarse,
                noise_sigma, 1.0, 1e-6, 0.0
            )

            diff_ratio = mad_score * inv_noise_sigma
            adjusted = ti.max(0.0, diff_ratio - noise_offset_factor)
            exponent = adjusted * motion_sensitivity * 0.5

            conf = 0.0
            if exponent <= 20.0:
                conf = 1.0 / (1.0 + ti.exp(exponent - 2.0))

            coarse_confidence[r, c] = conf
        else:
            coarse_confidence[r, c] = 0.0


@ti.kernel
def phase2_fine_analysis_kernel(
    current: ti.types.ndarray(),
    reference: ti.types.ndarray(),
    curr_grad_x: ti.types.ndarray(),
    curr_grad_y: ti.types.ndarray(),
    ref_grad_x: ti.types.ndarray(),
    ref_grad_y: ti.types.ndarray(),
    guidance_map: ti.types.ndarray(),
    stability_map: ti.types.ndarray(),
    weight_map_sum: ti.types.ndarray(),
    base_window: ti.i32,  # Deprecated but kept for signature compatibility
    row_starts: ti.types.ndarray(),
    col_starts: ti.types.ndarray(),
    pass_idx: ti.i32,
    tile_h: ti.i32,
    tile_w: ti.i32,
    h: ti.i32,
    w: ti.i32,
    noise_sigma: ti.f32,
    motion_sensitivity: ti.f32,
    noise_offset_factor: ti.f32,
    use_stability: ti.i32,
    use_guidance: ti.i32,
    early_exit_threshold: ti.f32
):
    """Performs sliding window analysis for fine weight map accumulation on GPU."""
    pass_row_mod = pass_idx // 2
    # ``pass_idx`` is a non-negative dispatch selector in [0, 3].  The
    # low-bit form is equivalent to modulo here and avoids a second integer
    # remainder operation in every invocation of the fine-analysis graph.
    pass_col_mod = pass_idx & 1

    # The window dimensions and their denominators are invariant for every
    # pixel in this dispatch.  Hoisting the reciprocal removes two floating
    # point divisions from the inner loop while retaining the same Hanning
    # expression and border behavior.
    inv_tile_h = 1.0 / float(tile_h - 1) if tile_h > 1 else 0.0
    inv_tile_w = 1.0 / float(tile_w - 1) if tile_w > 1 else 0.0
    # Keep the original literal to avoid changing the established window
    # phase while still hoisting it out of the pixel loop.
    two_pi = 2.0 * 3.1415926535

    num_rows = row_starts.shape[0]
    num_cols = col_starts.shape[0]

    limit_rows = (num_rows - pass_row_mod + 1) // 2
    limit_cols = (num_cols - pass_col_mod + 1) // 2
    for k, m in ti.ndrange(limit_rows, limit_cols):
        i = pass_row_mod + k * 2
        j = pass_col_mod + m * 2
        r = row_starts[i]
        c = col_starts[j]
        curr_h = ti.min(tile_h, h - r)
        curr_w = ti.min(tile_w, w - c)
        if curr_h > 0 and curr_w > 0:
            center_x = ti.min(c + curr_w // 2, w - 1)
            center_y = ti.min(r + curr_h // 2, h - 1)

            guidance_val = 1.0
            if use_guidance == 1:
                guidance_val = guidance_map[center_y, center_x]

            stab_val = 1.0
            if use_stability == 1:
                stab_val = stability_map[center_y, center_x]

            if guidance_val >= early_exit_threshold and stab_val >= early_exit_threshold:
                # Calculate local block contrast from reference patch
                ref_min = 1.0
                ref_max = 0.0
                # Highly optimized 5-point unrolled local contrast estimation (GPU register friendly)
                c_y = curr_h // 2
                c_x = curr_w // 2
                v0 = reference[r + c_y, c + c_x]
                v1 = reference[r, c]
                v2 = reference[r, c + curr_w - 1]
                v3 = reference[r + curr_h - 1, c]
                v4 = reference[r + curr_h - 1, c + curr_w - 1]

                ref_min = ti.min(v0, ti.min(v1, ti.min(v2, ti.min(v3, v4))))
                ref_max = ti.max(v0, ti.max(v1, ti.max(v2, ti.max(v3, v4))))
                contrast = ref_max - ref_min

                # Flat weight transition mapping with adaptive contrast limits based on local luma
                mean_luma = (v0 + v1 + v2 + v3 + v4) * 0.2
                contrast_limit = 0.12 * ti.max(0.05, mean_luma)
                contrast_range = 0.08 * ti.max(0.05, mean_luma)
                flat_weight = ti.max(0.0, ti.min(1.0, (contrast_limit - contrast) / contrast_range))

                mad_score = calculate_hybrid_gradient_optimized(
                    current, reference,
                    curr_grad_x, curr_grad_y,
                    ref_grad_x, ref_grad_y,
                    r, c, curr_h, curr_w, h, w,
                    noise_sigma, 1.0, 1e-6, flat_weight
                )

                confidence_fine = calculate_match_confidence(
                    mad_score, noise_sigma, motion_sensitivity, noise_offset_factor
                )

                final_conf = confidence_fine * guidance_val * stab_val

                if final_conf >= 1e-6:
                    for y, x in ti.ndrange(curr_h, curr_w):
                        wy = 0.5 * (1.0 - ti.cos(two_pi * float(y) * inv_tile_h)) if tile_h > 1 else 1.0
                        wx = 0.5 * (1.0 - ti.cos(two_pi * float(x) * inv_tile_w)) if tile_w > 1 else 1.0
                        wy = ti.max(wy, 1e-4)
                        wx = ti.max(wx, 1e-4)
                        w_val = wy * wx

                        weight_map_sum[r + y, c + x] += w_val * final_conf


@ti.kernel
def accumulate_spatial_merging_kernel(
    current_image_full: ti.types.ndarray(),
    weight_map_work: ti.types.ndarray(),
    final_image_sum: ti.types.ndarray(),
    weight_map_sum_full: ti.types.ndarray(),
    h_full: ti.i32,
    w_full: ti.i32,
    h_work: ti.i32,
    w_work: ti.i32,
    num_channels: ti.i32
):
    """Bilinearly interpolates work resolution weights to full resolution and accumulates frames."""
    # Coordinate scales are dispatch invariants.  Computing them once avoids
    # two divisions per full-resolution output pixel.
    y_scale = float(h_work) / float(h_full)
    x_scale = float(w_work) / float(w_full)
    for i, j in ti.ndrange(h_full, w_full):
        # Map full-res coordinates to work-res coordinates (floating point)
        y_work_f = float(i) * y_scale
        x_work_f = float(j) * x_scale

        # Bilinear interpolation bounds
        y0 = ti.cast(ti.floor(y_work_f), ti.i32)
        x0 = ti.cast(ti.floor(x_work_f), ti.i32)
        y1 = ti.min(y0 + 1, h_work - 1)
        x1 = ti.min(x0 + 1, w_work - 1)
        y0 = ti.max(0, y0)
        x0 = ti.max(0, x0)

        wy = y_work_f - float(y0)
        wx = x_work_f - float(x0)

        # Compute bilinearly interpolated weight
        w_val = (
            (1.0 - wy) * (1.0 - wx) * weight_map_work[y0, x0] +
            (1.0 - wy) * wx * weight_map_work[y0, x1] +
            wy * (1.0 - wx) * weight_map_work[y1, x0] +
            wy * wx * weight_map_work[y1, x1]
        )

        weight_map_sum_full[i, j] += w_val
        for c in range(num_channels):
            final_image_sum[i, j, c] += current_image_full[i, j, c] * w_val


@ti.kernel
def accumulate_spatial_merging_vec3_kernel(
    current_image_full: ti.types.ndarray(),
    weight_map_work: ti.types.ndarray(),
    final_image_sum: ti.types.ndarray(),
    weight_map_sum_full: ti.types.ndarray(),
    h_full: ti.i32,
    w_full: ti.i32,
    h_work: ti.i32,
    w_work: ti.i32,
    num_channels: ti.i32
):
    """Vec3 variant: bilinearly interpolates per-channel (3D) work-res weights
    to full resolution and accumulates frames with per-channel weighting.

    weight_map_work is (h_work, w_work, 3) — one weight per RGB channel.
    weight_map_sum_full is (h_full, w_full, 3) — per-channel weight accumulator.
    """
    y_scale = float(h_work) / float(h_full)
    x_scale = float(w_work) / float(w_full)
    for i, j in ti.ndrange(h_full, w_full):
        y_work_f = float(i) * y_scale
        x_work_f = float(j) * x_scale

        y0 = ti.cast(ti.floor(y_work_f), ti.i32)
        x0 = ti.cast(ti.floor(x_work_f), ti.i32)
        y1 = ti.min(y0 + 1, h_work - 1)
        x1 = ti.min(x0 + 1, w_work - 1)
        y0 = ti.max(0, y0)
        x0 = ti.max(0, x0)

        wy = y_work_f - float(y0)
        wx = x_work_f - float(x0)

        for c in range(num_channels):
            w_val = (
                (1.0 - wy) * (1.0 - wx) * weight_map_work[y0, x0, c] +
                (1.0 - wy) * wx * weight_map_work[y0, x1, c] +
                wy * (1.0 - wx) * weight_map_work[y1, x0, c] +
                wy * wx * weight_map_work[y1, x1, c]
            )
            weight_map_sum_full[i, j, c] += w_val
            final_image_sum[i, j, c] += current_image_full[i, j, c] * w_val


@ti.kernel
def mean_division_vec3_weight_kernel(
    sum_img: ti.types.ndarray(),
    sum_weight: ti.types.ndarray(),
    ref_img: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32
):
    """Per-channel mean division: dst[i,j,c] = sum_img[i,j,c] / sum_weight[i,j,c].
    Falls back to ref_img where weight is near zero."""
    for i, j in ti.ndrange(h, w):
        for c in range(3):
            w_sum = sum_weight[i, j, c]
            if w_sum > 1e-8:
                dst[i, j, c] = sum_img[i, j, c] / w_sum
            else:
                dst[i, j, c] = ref_img[i, j, c]


def _compile_graphs(module):
    """Register all spatial-merging graphs on an AOT module.

    Shared by ``compile_spatial_tcm`` so the same graph registration is used
    for every backend target.
    """
    # 0. Precompute Gradients Graph
    sym_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "img", dtype=ti.f32, ndim=2)
    sym_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grad_x", dtype=ti.f32, ndim=2)
    sym_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grad_y", dtype=ti.f32, ndim=2)
    sym_h_grad = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w_grad = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)

    g_grad = ti.graph.GraphBuilder()
    g_grad.dispatch(precompute_gradients_kernel, sym_img, sym_grad_x, sym_grad_y, sym_h_grad, sym_w_grad)
    module.add_graph("precompute_gradients", g_grad.compile())

    sym_clear_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype=ti.f32, ndim=2)
    sym_clear_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_clear_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)
    g_clear = ti.graph.GraphBuilder()
    g_clear.dispatch(clear_f32_2d_kernel, sym_clear_dst, sym_clear_h, sym_clear_w)
    module.add_graph("clear_f32_2d", g_clear.compile())

    # Gradient symbols for reuse
    sym_curr_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "curr_grad_x", dtype=ti.f32, ndim=2)
    sym_curr_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "curr_grad_y", dtype=ti.f32, ndim=2)
    sym_ref_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_grad_x", dtype=ti.f32, ndim=2)
    sym_ref_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_grad_y", dtype=ti.f32, ndim=2)

    sym_coarse_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coarse_grad_x", dtype=ti.f32, ndim=2)
    sym_coarse_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coarse_grad_y", dtype=ti.f32, ndim=2)
    sym_ref_coarse_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_coarse_grad_x", dtype=ti.f32, ndim=2)
    sym_ref_coarse_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_coarse_grad_y", dtype=ti.f32, ndim=2)

    # 1. Equalize Brightness Graph
    sym_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype=ti.f32, ndim=2)
    sym_ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", dtype=ti.f32, ndim=2)
    sym_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype=ti.f32, ndim=2)
    sym_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)

    g_eq = ti.graph.GraphBuilder()
    g_eq.dispatch(equalize_brightness_kernel, sym_src, sym_ref, sym_dst, sym_h, sym_w)
    module.add_graph("equalize_brightness", g_eq.compile())

    # 2. Phase 1 Coarse Analysis Graph
    sym_curr_coarse = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current_coarse", dtype=ti.f32, ndim=2)
    sym_ref_coarse = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reference_coarse", dtype=ti.f32, ndim=2)
    sym_coarse_conf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coarse_confidence", dtype=ti.f32, ndim=2)
    sym_coarse_tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "coarse_tile_h", dtype=ti.i32)
    sym_coarse_tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "coarse_tile_w", dtype=ti.i32)
    sym_h_coarse = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_coarse", dtype=ti.i32)
    sym_w_coarse = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_coarse", dtype=ti.i32)
    sym_noise_sigma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "noise_sigma", dtype=ti.f32)
    sym_motion_sens = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "motion_sensitivity", dtype=ti.f32)
    sym_noise_offset = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "noise_offset_factor", dtype=ti.f32)

    g_p1 = ti.graph.GraphBuilder()
    g_p1.dispatch(
        phase1_coarse_analysis_kernel,
        sym_curr_coarse, sym_ref_coarse,
        sym_coarse_grad_x, sym_coarse_grad_y,
        sym_ref_coarse_grad_x, sym_ref_coarse_grad_y,
        sym_coarse_conf,
        sym_coarse_tile_h, sym_coarse_tile_w,
        sym_h_coarse, sym_w_coarse,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
    )
    module.add_graph("phase1_coarse_analysis", g_p1.compile())

    # 3. Phase 2 Fine Analysis Graph (Individual)
    sym_current = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current", dtype=ti.f32, ndim=2)
    sym_reference = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reference", dtype=ti.f32, ndim=2)
    sym_guidance_map = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guidance_map", dtype=ti.f32, ndim=2)
    sym_stability_map = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "stability_map", dtype=ti.f32, ndim=2)
    sym_weight_map_sum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_sum", dtype=ti.f32, ndim=2)
    sym_base_window = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "base_window", dtype=ti.i32)
    sym_row_starts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "row_starts", dtype=ti.i32, ndim=1)
    sym_col_starts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "col_starts", dtype=ti.i32, ndim=1)
    sym_pass_idx = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx", dtype=ti.i32)
    sym_tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", dtype=ti.i32)
    sym_tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", dtype=ti.i32)
    sym_h_fine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w_fine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)
    sym_use_stability = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_stability", dtype=ti.i32)
    sym_use_guidance = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_guidance", dtype=ti.i32)
    sym_early_exit_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "early_exit_threshold", dtype=ti.f32)

    g_p2 = ti.graph.GraphBuilder()
    g_p2.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx,
        sym_tile_h, sym_tile_w,
        sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    module.add_graph("phase2_fine_analysis", g_p2.compile())

    # 4. Accumulate Spatial Merging Graph (Individual) — 2D weight
    sym_curr_img_full = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current_image_full", dtype=ti.f32, ndim=3)
    sym_weight_work = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_work", dtype=ti.f32, ndim=2)
    sym_final_img_sum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "final_image_sum", dtype=ti.f32, ndim=3)
    sym_weight_sum_full = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_sum_full", dtype=ti.f32, ndim=2)
    sym_h_full = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_full", dtype=ti.i32)
    sym_w_full = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_full", dtype=ti.i32)
    sym_h_work = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_work", dtype=ti.i32)
    sym_w_work = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_work", dtype=ti.i32)
    sym_num_channels = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_channels", dtype=ti.i32)

    g_accum = ti.graph.GraphBuilder()
    g_accum.dispatch(
        accumulate_spatial_merging_kernel,
        sym_curr_img_full, sym_weight_work,
        sym_final_img_sum, sym_weight_sum_full,
        sym_h_full, sym_w_full, sym_h_work, sym_w_work, sym_num_channels,
    )
    module.add_graph("accumulate_spatial_merging", g_accum.compile())

    # 4b. Accumulate Spatial Merging Vec3 Graph (per-channel 3D weight map)
    sym_curr_img_full_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current_image_full", dtype=ti.f32, ndim=3)
    sym_weight_work_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_work", dtype=ti.f32, ndim=3)
    sym_final_img_sum_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "final_image_sum", dtype=ti.f32, ndim=3)
    sym_weight_sum_full_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_sum_full", dtype=ti.f32, ndim=3)
    sym_h_full_v3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_full", dtype=ti.i32)
    sym_w_full_v3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_full", dtype=ti.i32)
    sym_h_work_v3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_work", dtype=ti.i32)
    sym_w_work_v3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_work", dtype=ti.i32)
    sym_num_channels_v3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_channels", dtype=ti.i32)

    g_accum_v3 = ti.graph.GraphBuilder()
    g_accum_v3.dispatch(
        accumulate_spatial_merging_vec3_kernel,
        sym_curr_img_full_v3, sym_weight_work_v3,
        sym_final_img_sum_v3, sym_weight_sum_full_v3,
        sym_h_full_v3, sym_w_full_v3, sym_h_work_v3, sym_w_work_v3, sym_num_channels_v3,
    )
    module.add_graph("accumulate_spatial_merging_vec3", g_accum_v3.compile())

    # 4c. Mean Division Vec3 Weight Graph (per-channel normalization)
    sym_sum_img_md = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_img", dtype=ti.f32, ndim=3)
    sym_sum_weight_md = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_weight", dtype=ti.f32, ndim=3)
    sym_ref_img_md = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_img", dtype=ti.f32, ndim=3)
    sym_dst_md = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype=ti.f32, ndim=3)
    sym_h_md = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w_md = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)

    g_md_v3 = ti.graph.GraphBuilder()
    g_md_v3.dispatch(
        mean_division_vec3_weight_kernel,
        sym_sum_img_md, sym_sum_weight_md, sym_ref_img_md, sym_dst_md,
        sym_h_md, sym_w_md,
    )
    module.add_graph("mean_division_vec3_weight", g_md_v3.compile())

    # 5. Combined Fine Analysis and Accumulate Graph
    sym_pass_idx_0 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_0", dtype=ti.i32)
    sym_pass_idx_1 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_1", dtype=ti.i32)
    sym_pass_idx_2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_2", dtype=ti.i32)
    sym_pass_idx_3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_3", dtype=ti.i32)

    g_fine_accum = ti.graph.GraphBuilder()
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_0,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_1,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_2,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_3,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_fine_accum.dispatch(
        accumulate_spatial_merging_kernel,
        sym_curr_img_full,
        sym_weight_map_sum,  # weight_map_work
        sym_final_img_sum,
        sym_weight_sum_full,
        sym_h_full, sym_w_full, sym_h_work, sym_w_work, sym_num_channels,
    )
    module.add_graph("fine_analysis_and_accumulate", g_fine_accum.compile())

    # 5b. Combined Fine Analysis 4 Passes
    g_4passes = ti.graph.GraphBuilder()
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_0,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_1,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_2,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current, sym_reference,
        sym_curr_grad_x, sym_curr_grad_y,
        sym_ref_grad_x, sym_ref_grad_y,
        sym_guidance_map, sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts, sym_col_starts,
        sym_pass_idx_3,
        sym_tile_h, sym_tile_w, sym_h_fine, sym_w_fine,
        sym_noise_sigma, sym_motion_sens, sym_noise_offset,
        sym_use_stability, sym_use_guidance, sym_early_exit_threshold,
    )
    module.add_graph("generate_fine_weights_4passes", g_4passes.compile())


def _find_app_assets_dir():
    """Locate ``<workspace>/pixel_refine_desktop/ui/data/aot_assets``.

    The historical application bundle keeps the flat spatial_<arch>.tcm
    fallback here.  When this package runs inside the Pixel Refine
    workspace, walking up from ``taichi_vision/taichi_algorithm/spatial_fusion``
    reaches the workspace root which contains ``pixel_refine_desktop``.
    """
    cur = os.path.abspath(os.path.dirname(__file__))
    while os.path.basename(cur) != "taichi_vision" and len(cur) > 4:
        cur = os.path.dirname(cur)
    workspace = os.path.dirname(cur)
    candidate = os.path.join(
        workspace, "pixel_refine_desktop", "ui", "data", "aot_assets"
    )
    return os.path.abspath(candidate)


def _resolve_backend_arch():
    """Resolve the Taichi arch from the engine-controlled backend setting.

    Priority (matching the canonical ``compile_gaussian_tcm`` convention):
      1. ``PIXEL_REFINE_AOT_ARCH`` / ``TARGET_BACKEND`` / ``AOT_ARCH`` env
         markers set by the engine or the backend suite worker.
      2. The active ``taichi_vision.taichi_aot`` engine backend (engine.py
         owns backend selection at runtime), so a compile after the app
         selects a backend automatically targets that same backend.
      3. ``vulkan`` as a final fallback.

    Returns ``(ti_arch, suffix)``.
    """
    arch_str = (
        os.environ.get("PIXEL_REFINE_AOT_ARCH")
        or os.environ.get("TARGET_BACKEND")
        or os.environ.get("AOT_ARCH")
        or ""
    ).strip().lower()

    if not arch_str:
        # engine.py controls the runtime backend; read it when available.
        try:
            from taichi_vision.taichi_aot import get_engine

            arch_str = str(getattr(get_engine(), "arch", "")).strip().lower()
        except Exception:
            arch_str = ""

    if not arch_str:
        arch_str = "vulkan"

    mapping = {
        "cuda": (ti.cuda, "cuda"),
        "vulkan": (ti.vulkan, "vulkan"),
        "opengl": (ti.opengl, "opengl"),
        "gles": (ti.gles, "gles"),
        # ti.x64 is the canonical CPU arch in Taichi 1.7.4 (ti.cpu alias).
        "cpu": (ti.x64, "cpu"),
        "x64": (ti.x64, "cpu"),
    }
    if arch_str not in mapping:
        raise ValueError(f"Unsupported spatial backend {arch_str!r}; "
                         f"choose from {sorted(mapping)}")
    return mapping[arch_str]


def compile_spatial_tcm(arch=None, suffix=None, out_dir=None, save_path=None):
    """Compile and package the spatial-merging AOT TCM.

    Backend is controlled by ``engine.py`` at runtime and by the canonical
    ``PIXEL_REFINE_AOT_ARCH``/``TARGET_BACKEND``/``AOT_ARCH`` markers when
    invoked from the backend suite, so the process is automatic per backend.

    Args:
        arch:      Optional explicit Taichi arch.  None → engine/env resolved.
        suffix:    Artifact suffix (``vulkan``/``cuda``/``opengl``/``cpu``/``gles``).
                   Auto-derived from ``arch`` when None.
        out_dir:   Optional output directory for ``spatial_{suffix}.tcm``.
        save_path: Optional exact output path (backend-suite ``path``
                   convention).  Overrides ``out_dir``/suffix naming.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi is not available")

    if arch is None:
        arch, auto_suffix = _resolve_backend_arch()
    else:
        auto_suffix = {
            ti.cuda: "cuda",
            ti.vulkan: "vulkan",
            ti.opengl: "opengl",
            ti.gles: "gles",
            ti.x64: "cpu",
            ti.cpu: "cpu",
        }.get(arch)
    if suffix is None:
        suffix = auto_suffix or "vulkan"

    print(f"\n>>> Compiling SPATIAL MERGING AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    # Fail-closed against silent backend fallback.  Taichi's adaptive arch
    # selection can fall back to CPU (e.g. when an OpenGL context cannot be
    # created in the current environment).  Writing a CPU payload under a
    # GPU artifact name would mix ABI/backends and is never acceptable —
    # matching the backend suite's ``_require_backend_artifact`` gate.
    actual_arch = getattr(ti.lang.impl.current_cfg(), "arch", None)
    if actual_arch is not None and int(actual_arch) != int(arch):
        raise RuntimeError(
            f"Taichi fell back to {actual_arch} while compiling for {arch}; "
            "refusing to emit a cross-backend artifact. Compile on an "
            "environment that supports the requested backend."
        )

    module = ti.aot.Module(arch)
    _compile_graphs(module)

    # Save through the canonical archiver.  The old hand-written ZIP path
    # omitted ``aot_metadata.tcb`` for graphics backends, which made otherwise
    # valid Vulkan/OpenGL artifacts fail the LLVM20 compatibility preflight.
    try:
        from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
    except (ImportError, RuntimeError) as import_error:
        # A compiler must be able to emit a graphics artifact before a runtime
        # embedding context exists.  Importing through the package initializer
        # would construct AOTEngine and reject OpenGL without capability JSON;
        # load this stdlib-only archiver directly instead.  Runtime admission
        # remains fail-closed and still requires real capability evidence.
        artifact_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../aot_py/aot_artifact.py",
            )
        )
        spec = importlib.util.spec_from_file_location(
            "pixel_refine_aot_artifact_standalone", artifact_path
        )
        if spec is None or spec.loader is None:
            raise import_error
        artifact_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(artifact_module)
        archive_module = artifact_module.archive_module

    if save_path is not None:
        tcm_path = os.path.abspath(save_path)
        os.makedirs(os.path.dirname(tcm_path), exist_ok=True)
    else:
        # Test/build automation can redirect the packaged artifact without
        # touching the checked-in application assets.  Normal callers retain
        # the historical output location.
        output_override = os.environ.get("PIXEL_REFINE_SPATIAL_TCM_OUTPUT_DIR")
        if out_dir is not None:
            target_dir = os.path.abspath(out_dir)
        elif output_override:
            target_dir = os.path.abspath(output_override)
        else:
            target_dir = _find_app_assets_dir()
        tcm_path = os.path.join(target_dir, f"spatial_{suffix}.tcm")
        os.makedirs(target_dir, exist_ok=True)

    archive_module(module, tcm_path)
    try:
        ti.reset()
    except Exception:
        pass
    print(f"Spatial AOT packaged successfully to: {tcm_path}")
    return tcm_path


# -------------------------------------------------------------------------
# AOT Runtime Wrappers
# -------------------------------------------------------------------------
class SpatialScratchCache:
    """Reusable per-batch GPU scratch buffers for spatial analysis.

    The spatial algorithm is sequential per frame, so a scratch slot can be
    safely overwritten after the previous dispatch has completed.  Slots are
    keyed by purpose and shape; a resolution change transparently replaces
    only the incompatible slot.
    """

    def __init__(self):
        self._slots = {}
        self.reference_token = None

    def acquire(self, engine, name, shape, dtype=np.float32, **kwargs):
        shape = tuple(int(v) for v in shape)
        buf = self._slots.get(name)
        # Shape alone is insufficient for safe reuse: callers may switch
        # analysis precision between batches while keeping the same
        # resolution.  Reusing a mismatched buffer would either force an
        # implicit conversion in the bridge or corrupt the next dispatch.
        if (
            buf is not None
            and tuple(buf.shape) == shape
            and np.dtype(getattr(buf, "dtype", dtype)) == np.dtype(dtype)
        ):
            return buf
        if buf is not None:
            try:
                buf.destroy()
            except Exception:
                pass
        buf = engine.allocate(shape, dtype=dtype, **kwargs)
        self._slots[name] = buf
        return buf

    def clear(self):
        for buf in self._slots.values():
            try:
                buf.destroy()
            except Exception:
                pass
        self._slots.clear()
        self.reference_token = None


def _resolve_spatial_tcm(engine):
    """Resolve the spatial AOT TCM for the active target.

    Rebuilt LLVM20 artifacts live in the canonical target-qualified tree
    (``spatial_<backend>_<arch>_<os>[_<vendor>].tcm``).  Resolve that identity
    first so a fresh target artifact is never shadowed by a stale flat archive.
    The historical ``ui/data/aot_assets`` layout remains an explicit fallback
    for existing application bundles during migration.
    """
    arch = str(getattr(engine, "arch", "cpu")).lower()
    aot_tcm_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../aot_tcm",
        )
    )
    try:
        from taichi_vision.taichi_aot.artifact_targets import (
            detect_target,
            resolve_artifact,
        )
        from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

        target = detect_target(
            backend=arch,
            device=getattr(engine, "gpu_name", ""),
        )
        roots = []
        override = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip()
        if override:
            roots.append(os.path.abspath(override))
        else:
            staged = staged_tcm_root(target.target_id)
            if staged is not None:
                roots.append(os.path.abspath(str(staged)))
            roots.append(aot_tcm_dir)

        seen_roots = set()
        for root in roots:
            root = os.path.normcase(os.path.realpath(root))
            if root in seen_roots or not os.path.isdir(root):
                continue
            seen_roots.add(root)
            resolved = resolve_artifact(
                root,
                "spatial",
                target,
                allow_legacy=True,
            )
            if resolved is not None and os.path.isfile(str(resolved)):
                return os.path.abspath(str(resolved))
    except (ImportError, OSError, RuntimeError, ValueError):
        pass

    # Direct canonical fallback inside taichi_vision/taichi_algorithm/aot_tcm
    candidates = [
        os.path.join(aot_tcm_dir, f"{arch}_x86_64_windows", f"spatial_{arch}_x86_64_windows.tcm"),
        os.path.join(aot_tcm_dir, f"spatial_{arch}_x86_64_windows.tcm"),
        os.path.join(aot_tcm_dir, f"spatial_{arch}.tcm"),
        os.path.join(aot_tcm_dir, "vulkan_x86_64_windows", "spatial_vulkan_x86_64_windows.tcm"),
        os.path.join(aot_tcm_dir, "spatial_vulkan.tcm"),
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return os.path.abspath(cand)

    raise FileNotFoundError(
        f"[SpatialFusion] Could not find spatial TCM in '{aot_tcm_dir}' for backend '{arch}'."
    )


def _tcm_graph_available(tcm_path, graph_name):
    """Return whether *graph_name* is indexed by the current TCM file.

    The public call shape is intentionally unchanged.  The metadata result is
    cached below with the artifact size/mtime in the key so replacing a TCM at
    the same path cannot leave a stale graph decision in a long-running
    process.
    """
    try:
        stat = os.stat(os.fspath(tcm_path))
        fingerprint = (
            int(stat.st_mtime_ns),
            int(getattr(stat, "st_ctime_ns", stat.st_mtime_ns)),
            int(stat.st_size),
        )
    except (OSError, TypeError, ValueError):
        fingerprint = (None, None, None)
    return _tcm_graph_available_cached(
        os.fspath(tcm_path), str(graph_name), *fingerprint
    )


@lru_cache(maxsize=16)
def _tcm_graph_available_cached(
    tcm_path, graph_name, mtime_ns, ctime_ns, file_size
):
    """Check a packaged graph before dispatching an optional newer graph.

    During rolling updates, an older spatial artifact may remain in the
    application tree.  Metadata gating keeps that artifact usable and avoids
    sending an unknown graph name to the native bridge (which could quarantine
    an otherwise valid module).
    """
    try:
        with zipfile.ZipFile(os.fspath(tcm_path), "r") as archive:
            marker = str(graph_name).encode("utf-8")
            # LLVM/CPU/CUDA archives use graphs.tcb; SPIR-V graphics
            # archives use graphs.json.  Both are authoritative graph
            # indexes, so the optional graph gate must understand both.
            for index_name in ("graphs.tcb", "graphs.json"):
                try:
                    if marker in archive.read(index_name):
                        return True
                except KeyError:
                    continue
        return False
    except (OSError, KeyError, zipfile.BadZipFile, TypeError, ValueError):
        return False


def _compute_tile_starts(length, tile, overlap=0.3):
    """Compute tile start indices matching the application convention."""
    overlap = max(0.0, min(float(overlap), 0.9))
    stride = max(1, int(tile * (1.0 - overlap)))
    starts = list(range(0, length, stride))
    if not starts:
        starts = [0]
    return starts


def generate_spatial_weights_taichi(
    current_image,
    reference_image,
    weight_map_sum,
    base_window,
    stability_map,
    row_starts,
    col_starts,
    tile_h,
    tile_w,
    noise_sigma,
    motion_sensitivity,
    noise_offset_factor,
    equalize_brightness,
    buffer_provider,
    **kwargs,
):
    """
    Calculates the weight map for a single frame relative to the reference using Taichi AOT.
    """
    import taichi_vision.taichi_aot as taichi_aot
    engine = taichi_aot.engine
    scratch = kwargs.get("scratch_cache")

    if noise_sigma is None or (isinstance(noise_sigma, (int, float)) and noise_sigma <= 0.0):
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        noise_sigma = float(estimate_noise(reference_image))
    else:
        noise_sigma = float(np.clip(noise_sigma, 1e-5, 0.99999))

    def _alloc(name, shape, dtype=np.float32, **alloc_kwargs):
        if scratch is not None:
            return scratch.acquire(engine, name, shape, dtype=dtype, **alloc_kwargs)
        return engine.allocate(shape, dtype=dtype, **alloc_kwargs)

    def _destroy(buf):
        if scratch is None and buf is not None:
            buf.destroy()

    if not isinstance(row_starts, taichi_aot.TaichiGPUBuffer):
        row_starts = taichi_aot.upload(np.asarray(row_starts, dtype=np.int32))
    if not isinstance(col_starts, taichi_aot.TaichiGPUBuffer):
        col_starts = taichi_aot.upload(np.asarray(col_starts, dtype=np.int32))

    # Load Module (backend-aware)
    tcm_path = _resolve_spatial_tcm(engine)
    mod = engine.load(tcm_path)

    import time
    profile_hotspots = kwargs.get("profile_hotspots", False) or os.environ.get("PROFILE_SPATIAL", "0") == "1"
    hotspots = {}

    t_start = time.perf_counter()

    # 1. Reset weight map sum to 0. New spatial TCMs clear the resident
    # buffer in-place on the active backend, avoiding a full-frame host
    # allocation and upload for every input frame. Older artifacts retain
    # the compatible host reset path until they are rebuilt.
    if _tcm_graph_available(tcm_path, "clear_f32_2d"):
        mod.run(
            "clear_f32_2d",
            dst=weight_map_sum,
            h=int(weight_map_sum.shape[0]),
            w=int(weight_map_sum.shape[1]),
        )
    else:
        zeros = np.zeros(weight_map_sum.shape, dtype=np.float32)
        from taichi_vision.taichi_aot.engine import _LIB, _RUNTIME
        _LIB.write_to_gpu_buffer(
            _RUNTIME,
            weight_map_sum.handle,
            zeros.ctypes.data,
            weight_map_sum.size_bytes,
        )

    if profile_hotspots:
        engine.sync()
        hotspots["1. Reset weight map"] = (time.perf_counter() - t_start) * 1000
        t_prev = time.perf_counter()
    else:
        t_prev = 0.0

    h, w = current_image.shape[0], current_image.shape[1]
    coarse_texture_boost = float(kwargs.get("coarse_texture_boost", 0.30))
    coarse_texture_radius = float(kwargs.get("coarse_texture_radius", 10.0))
    reference_token = (
        getattr(reference_image, "handle", id(reference_image)),
        int(h),
        int(w),
        round(coarse_texture_boost, 6),
        round(coarse_texture_radius, 6),
    )
    reference_cache_names = ["ref_l1", "ref_l2"]
    if coarse_texture_boost > 1e-6:
        reference_cache_names.append("ref_texture_boost")
    reuse_reference = (
        scratch is not None
        and scratch.reference_token == reference_token
        and all(name in scratch._slots for name in reference_cache_names)
    )

    # 2. Coarse texture boost for analysis only.  This never modifies the
    # source RGB frame or the output merge; it only improves texture evidence
    # used by the weight-map kernels.  The invariant reference result is
    # cached for the complete batch.
    curr_texture_boost = None
    if coarse_texture_boost > 1e-6:
        curr_texture_boost = _alloc("curr_texture_boost", (h, w), dtype=np.float32)
        taichi_aot.coarse_texture_boost_gpu(
            current_image,
            texture_amount=coarse_texture_boost,
            radius=coarse_texture_radius,
            dst=curr_texture_boost,
        )

        if reuse_reference:
            ref_texture_boost = scratch._slots["ref_texture_boost"]
        else:
            ref_texture_boost = _alloc("ref_texture_boost", (h, w), dtype=np.float32)
            taichi_aot.coarse_texture_boost_gpu(
                reference_image,
                texture_amount=coarse_texture_boost,
                radius=coarse_texture_radius,
                dst=ref_texture_boost,
            )
    else:
        curr_texture_boost = current_image
        ref_texture_boost = reference_image

    # 3. Brightness Equalization (Optional)
    analysis_input = curr_texture_boost
    analysis_reference = ref_texture_boost
    eq_temp = None
    if equalize_brightness:
        eq_temp = _alloc("equalize", (h, w), dtype=np.float32)
        mod.run("equalize_brightness", src=analysis_input, ref=analysis_reference, dst=eq_temp, h=int(h), w=int(w))
        analysis_input = eq_temp

    if profile_hotspots:
        engine.sync()
        hotspots["2. Brightness Equalization"] = (time.perf_counter() - t_prev) * 1000
        t_prev = time.perf_counter()

    # 4. Phase 1: Coarse Analysis for Guidance Map (Level 2: 1/4 Resolution)
    # Downscale in two steps (L0 -> L1 -> L2) to prevent aliasing
    curr_l0 = analysis_input
    curr_l1 = taichi_aot.resize(curr_l0, (w // 2, h // 2), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                 dst=_alloc("curr_l1", (h // 2, w // 2)))
    curr_l2 = taichi_aot.resize(curr_l1, (w // 4, h // 4), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                 dst=_alloc("curr_l2", (h // 4, w // 4)))

    if reuse_reference:
        ref_l1 = scratch._slots["ref_l1"]
        ref_l2 = scratch._slots["ref_l2"]
    else:
        ref_l0 = analysis_reference
        ref_l1 = taichi_aot.resize(ref_l0, (w // 2, h // 2), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                   dst=_alloc("ref_l1", (h // 2, w // 2)))
        ref_l2 = taichi_aot.resize(ref_l1, (w // 4, h // 4), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                   dst=_alloc("ref_l2", (h // 4, w // 4)))

    if profile_hotspots:
        engine.sync()
        hotspots["3a. Downscaling Pyramids"] = (time.perf_counter() - t_prev) * 1000
        t_prev = time.perf_counter()

    guidance_gpu = None
    level_conf_gpu = None
    curr_coarse_grad_x = None
    curr_coarse_grad_y = None
    ref_coarse_grad_x = None
    ref_coarse_grad_y = None

    try:
        # Run coarse analysis ONLY at the coarsest level (Level 2) to match C++
        curr_level = curr_l2
        ref_level = ref_l2

        h_level, w_level = curr_level.shape[0], curr_level.shape[1]

        # Allocate coarse gradients
        curr_coarse_grad_x = _alloc("curr_coarse_grad_x", (h_level, w_level))
        curr_coarse_grad_y = _alloc("curr_coarse_grad_y", (h_level, w_level))
        ref_coarse_grad_x = _alloc("ref_coarse_grad_x", (h_level, w_level))
        ref_coarse_grad_y = _alloc("ref_coarse_grad_y", (h_level, w_level))

        # Run precompute_gradients on coarse level
        mod.run("precompute_gradients", img=curr_level, grad_x=curr_coarse_grad_x, grad_y=curr_coarse_grad_y, h=int(h_level), w=int(w_level))
        if not reuse_reference:
            mod.run("precompute_gradients", img=ref_level, grad_x=ref_coarse_grad_x, grad_y=ref_coarse_grad_y, h=int(h_level), w=int(w_level))

        if profile_hotspots:
            engine.sync()
            hotspots["3b. Coarse Gradients Precompute"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

        if scratch is not None and not reuse_reference:
            scratch.reference_token = reference_token

        scale_factor = h_level / h
        level_tile_h = max(8, int(tile_h * scale_factor))
        level_tile_w = max(8, int(tile_w * scale_factor))

        num_tiles_h = max(1, h_level // level_tile_h)
        num_tiles_w = max(1, w_level // level_tile_w)

        level_conf_gpu = _alloc("level_conf", (num_tiles_h, num_tiles_w))

        mod.run(
            "phase1_coarse_analysis",
            current_coarse=curr_level,
            reference_coarse=ref_level,
            coarse_grad_x=curr_coarse_grad_x,
            coarse_grad_y=curr_coarse_grad_y,
            ref_coarse_grad_x=ref_coarse_grad_x,
            ref_coarse_grad_y=ref_coarse_grad_y,
            coarse_confidence=level_conf_gpu,
            coarse_tile_h=int(level_tile_h),
            coarse_tile_w=int(level_tile_w),
            h_coarse=int(h_level),
            w_coarse=int(w_level),
            noise_sigma=float(noise_sigma),
            motion_sensitivity=float(motion_sensitivity),
            noise_offset_factor=float(noise_offset_factor),
        )

        if profile_hotspots:
            engine.sync()
            hotspots["3c. Phase 1 Coarse Analysis Kernel"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

        # Upsample coarse tile grid to Level 2 resolution
        guidance_gpu = taichi_aot.resize(
            level_conf_gpu,
            (w_level, h_level),
            interpolation=taichi_aot.INTER_CUBIC,
            return_gpu=True,
            dst=_alloc("guidance_level", (h_level, w_level)),
        )

        # Final upsample from Level 2 resolution to full resolution
        if guidance_gpu is not None and (
            guidance_gpu.shape[0] != h or guidance_gpu.shape[1] != w
        ):
            final_guidance = taichi_aot.resize(
                guidance_gpu, (w, h), interpolation=taichi_aot.INTER_CUBIC, return_gpu=True,
                dst=_alloc("guidance_full", (h, w)),
            )
            _destroy(guidance_gpu)
            guidance_gpu = final_guidance

        if profile_hotspots:
            engine.sync()
            hotspots["3d. Guidance Map Upsampling & Resize"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

    finally:
        # Cleanup pyramids and temp buffers
        _destroy(curr_l1)
        _destroy(curr_l2)
        _destroy(ref_l1)
        _destroy(ref_l2)
        if curr_coarse_grad_x is not None:
            _destroy(curr_coarse_grad_x)
        if curr_coarse_grad_y is not None:
            _destroy(curr_coarse_grad_y)
        if ref_coarse_grad_x is not None:
            _destroy(ref_coarse_grad_x)
        if ref_coarse_grad_y is not None:
            _destroy(ref_coarse_grad_y)
        if level_conf_gpu is not None:
            _destroy(level_conf_gpu)

        if profile_hotspots:
            engine.sync()
            hotspots["3e. Coarse Temp Cleanup"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

    # 4. Phase 2: Fine Analysis (Sliding Window MAD)
    use_stability = 1 if stability_map is not None else 0
    dummy_gpu = None
    if stability_map is None:
        dummy_gpu = _alloc("dummy_stability", (1, 1), dtype=np.float32)
        stability_map = dummy_gpu

    curr_grad_x = None
    curr_grad_y = None
    ref_grad_x = None
    ref_grad_y = None

    try:
        # Allocate fine gradients
        curr_grad_x = _alloc("curr_grad_x", (h, w))
        curr_grad_y = _alloc("curr_grad_y", (h, w))
        ref_grad_x = _alloc("ref_grad_x", (h, w))
        ref_grad_y = _alloc("ref_grad_y", (h, w))

        # Run precompute_gradients on fine level
        mod.run("precompute_gradients", img=analysis_input, grad_x=curr_grad_x, grad_y=curr_grad_y, h=int(h), w=int(w))
        if not reuse_reference:
            mod.run("precompute_gradients", img=analysis_reference, grad_x=ref_grad_x, grad_y=ref_grad_y, h=int(h), w=int(w))

        if profile_hotspots:
            engine.sync()
            hotspots["4a. Fine Gradients Precompute"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

        # Extract early_exit_threshold from kwargs
        early_exit_threshold = float(kwargs.get("early_exit_threshold", 0.05))

        mod.run(
            "generate_fine_weights_4passes",
            current=analysis_input,
            reference=analysis_reference,
            curr_grad_x=curr_grad_x,
            curr_grad_y=curr_grad_y,
            ref_grad_x=ref_grad_x,
            ref_grad_y=ref_grad_y,
            guidance_map=guidance_gpu,
            stability_map=stability_map,
            weight_map_sum=weight_map_sum,
            base_window=0,
            row_starts=row_starts,
            col_starts=col_starts,
            pass_idx_0=0,
            pass_idx_1=1,
            pass_idx_2=2,
            pass_idx_3=3,
            tile_h=int(tile_h),
            tile_w=int(tile_w),
            h=int(h),
            w=int(w),
            noise_sigma=float(noise_sigma),
            motion_sensitivity=float(motion_sensitivity),
            noise_offset_factor=float(noise_offset_factor),
            use_stability=int(use_stability),
            use_guidance=1,
            early_exit_threshold=early_exit_threshold,
        )

        if profile_hotspots:
            engine.sync()
            hotspots["4b. Phase 2 Fine Analysis (4-Pass Kernel)"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()
    finally:
        if curr_grad_x is not None:
            _destroy(curr_grad_x)
        if curr_grad_y is not None:
            _destroy(curr_grad_y)
        if ref_grad_x is not None:
            _destroy(ref_grad_x)
        if ref_grad_y is not None:
            _destroy(ref_grad_y)
        if dummy_gpu is not None:
            _destroy(dummy_gpu)
        if guidance_gpu is not None:
            _destroy(guidance_gpu)
        if eq_temp is not None:
            _destroy(eq_temp)
        if coarse_texture_boost > 1e-6:
            _destroy(curr_texture_boost)
            if not reuse_reference:
                _destroy(ref_texture_boost)

        if profile_hotspots:
            engine.sync()
            hotspots["4c. Fine Cleanup"] = (time.perf_counter() - t_prev) * 1000
            total_t = (time.perf_counter() - t_start) * 1000
            print("\n" + "=" * 60)
            print(" SPATIAL FUSION HOTSPOT PROFILING (ms)")
            print("=" * 60)
            for k, v in hotspots.items():
                print(f" {k:<45} : {v:>8.2f} ms ({v/total_t*100.0:>5.1f}%)")
            print("-" * 60)
            print(f" {'Total GPU Wrapper Time':<45} : {total_t:>8.2f} ms")
            print("=" * 60 + "\n")


def accumulate_spatial_merging_taichi(
    current_image_full,
    weight_map_work,
    final_image_sum,
    weight_map_sum_full,
    **kwargs,
):
    """Accumulates a frame into the global sum using its processed weight map via Taichi AOT.

    Auto-dispatches based on weight_map_work dimensionality:
      - 2D (h_work, w_work):    classic luma-only accumulation (unchanged)
      - 3D (h_work, w_work, 3): per-channel vec3 accumulation (WeightNet chroma gating)

    For the 3D path, weight_map_sum_full must also be 3D (h_full, w_full, 3)
    to support correct per-channel normalization.
    """
    import taichi_vision.taichi_aot as taichi_aot
    engine = taichi_aot.engine

    # Load Module (backend-aware)
    tcm_path = _resolve_spatial_tcm(engine)
    mod = engine.load(tcm_path)

    h_full, w_full = final_image_sum.shape[0], final_image_sum.shape[1]
    h_work, w_work = weight_map_work.shape[0], weight_map_work.shape[1]
    num_channels = final_image_sum.shape[2]

    # Auto-detect: 3D weight map → vec3 accumulation path
    is_vec3_weight = weight_map_work.ndim == 3 and weight_map_work.shape[2] >= 3

    if is_vec3_weight:
        # Fail clearly when the resolved TCM predates the vec3 graph (e.g. an
        # OpenGL artifact that was not rebuilt with the dev toolchain).  Never
        # silently fall back to CPU or mix backends.
        if not _tcm_graph_available(tcm_path, "accumulate_spatial_merging_vec3"):
            raise RuntimeError(
                "accumulate_spatial_merging_vec3 requested but the resolved "
                f"spatial TCM lacks the graph: {tcm_path}. Recompile the "
                "spatial TCM for the active backend (compile_spatial_fusion_tcm)."
            )
        mod.run(
            "accumulate_spatial_merging_vec3",
            current_image_full=current_image_full,
            weight_map_work=weight_map_work,
            final_image_sum=final_image_sum,
            weight_map_sum_full=weight_map_sum_full,
            h_full=int(h_full),
            w_full=int(w_full),
            h_work=int(h_work),
            w_work=int(w_work),
            num_channels=int(num_channels),
        )
    else:
        mod.run(
            "accumulate_spatial_merging",
            current_image_full=current_image_full,
            weight_map_work=weight_map_work,
            final_image_sum=final_image_sum,
            weight_map_sum_full=weight_map_sum_full,
            h_full=int(h_full),
            w_full=int(w_full),
            h_work=int(h_work),
            w_work=int(w_work),
            num_channels=int(num_channels),
        )


def mean_division_vec3_weight_taichi(
    sum_img,
    sum_weight,
    ref_img,
    dst=None,
):
    """Per-channel mean division on GPU using Taichi AOT.

    dst[i,j,c] = sum_img[i,j,c] / sum_weight[i,j,c]
    Falls back to ref_img where weight is near zero.

    Args:
        sum_img:    TaichiGPUBuffer (h, w, 3) — accumulated weighted sum.
        sum_weight: TaichiGPUBuffer (h, w, 3) — per-channel weight accumulator.
        ref_img:    TaichiGPUBuffer (h, w, 3) — reference image for fallback.
        dst:        Optional pre-allocated output buffer.

    Returns:
        TaichiGPUBuffer (h, w, 3) — normalized result.
    """
    import taichi_vision.taichi_aot as taichi_aot
    engine = taichi_aot.engine

    tcm_path = _resolve_spatial_tcm(engine)
    mod = engine.load(tcm_path)

    h, w = sum_img.shape[0], sum_img.shape[1]

    if not _tcm_graph_available(tcm_path, "mean_division_vec3_weight"):
        raise RuntimeError(
            "mean_division_vec3_weight requested but the resolved spatial "
            f"TCM lacks the graph: {tcm_path}. Recompile the spatial TCM for "
            "the active backend (compile_spatial_fusion_tcm)."
        )

    if dst is None:
        dst = engine.allocate(
            sum_img.shape, dtype=sum_img.dtype,
            is_vector=getattr(sum_img, "is_vector", False),
            vector_dim=getattr(sum_img, "vector_dim", 3),
        )

    # The graph kernel indexes sum_img[i, j, c] as a plain scalar 3D ndarray,
    # but the incoming buffers are vector fields (is_vector=True).  Convert
    # them to scalar 3D views with ``view_as_vector(False)`` — matching the
    # accumulate_spatial_merging_vec3 dispatch contract.
    def _scalar_3d(buf):
        if getattr(buf, "is_vector", False):
            return buf.view_as_vector(False)
        return buf

    sum_img_v = _scalar_3d(sum_img)
    sum_weight_v = _scalar_3d(sum_weight)
    ref_img_v = _scalar_3d(ref_img)
    dst_v = _scalar_3d(dst)

    mod.run(
        "mean_division_vec3_weight",
        sum_img=sum_img_v,
        sum_weight=sum_weight_v,
        ref_img=ref_img_v,
        dst=dst_v,
        h=int(h),
        w=int(w),
    )
    return dst
