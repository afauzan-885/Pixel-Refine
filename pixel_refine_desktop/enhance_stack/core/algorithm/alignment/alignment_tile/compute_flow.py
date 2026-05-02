"""
Compute Flow - Taichi GPU Implementation
=========================================
Pure GPU-accelerated tile-based optical flow computation.

Matching C++ API: alignment_tile.cpp

Pipeline: Coarse-to-Fine Pyramid → Tile Matching → Median Filter
Note: All pyramid processing stays on GPU to minimize CPU-GPU transfer overhead.
"""

import numpy as np
import time
import os
import ctypes
from platform import system

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

# Import cost function helpers (GPU-compatible)
from . import cost_function

# Import submodule functions directly to avoid package-level shadowing
try:
    from ...taichi_algorithm.pyramid import (
        build_image_pyramid_gpu,
        build_image_pyramid_gpu_4x,
        upsample_flow_gpu,
    )
    from ...taichi_algorithm.ransac import (
        ransac_flow_cleanup_local,
        ransac_flow_cleanup_motion_aware,
    )
    from ...taichi_algorithm.median_filter import median_filter_flow

    # common might be useful
    from ...taichi_algorithm import common

    # Import kernels directly from ncc module to avoid shadowing from taichi_algorithm.ncc function
    from ...taichi_algorithm.ncc import (
        _compute_global_zncc_surface,
        _reduce_min_2d_kernel,
    )

    class _NccModuleWrapper:
        def __init__(self):
            self._compute_global_zncc_surface = _compute_global_zncc_surface
            self._reduce_min_2d_kernel = _reduce_min_2d_kernel

    ncc_module = _NccModuleWrapper()
    from ...taichi_algorithm.taichi_worker import ti_thread

    TAICHI_MODULES_AVAILABLE = True
except ImportError as e:
    print("TAICHI IMPORT ERROR in compute_flow.py:", e)
    TAICHI_MODULES_AVAILABLE = False


# ============================================================================
# Constants
# ============================================================================
class ImageAlignmentConfig:
    """Configuration constants matching C++ namespace."""

    DEFAULT_DOWNSCALE_FACTOR = 4  # Default for HDR+ style
    MIN_TILE_SIZE = 8
    MIN_PYRAMID_LAYER_SIZE = 190
    EARLY_EXIT_COST = 0.0001
    ADAPTIVE_THRESHOLD = 0.005  # Threshold for expanding search area
    ENABLE_MEDIAN_FILTER = False  # Enable median filter for robust motion suppression


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _block_search_kernel(
        ref_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        comp_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        refined_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        tile_h: ti.i32,
        tile_w: ti.i32,
        search_radius: ti.i32,
    ):
        """Perform a wide-area block search for initial alignment."""
        h, w = ref_layer.shape[0], ref_layer.shape[1]
        step_y, step_x = tile_h, tile_w
        for tile_y, tile_x in ti.ndrange((h + step_y - 1) // step_y, (w + step_x - 1) // step_x):
            y, x = tm.clamp(tile_y * step_y, 0, h - tile_h), tm.clamp(tile_x * step_x, 0, w - tile_w)
            best_cost, best_dx, best_dy = 1e10, 0.0, 0.0
            bias_weight = 0.999
            for dy, dx in ti.ndrange((-search_radius, search_radius + 1), (-search_radius, search_radius + 1)):
                test_y, test_x = y + dy, x + dx
                if not (test_y <= -tile_h or test_x <= -tile_w or test_y >= h or test_x >= w):
                    cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, test_y, test_x, tile_h, tile_w, h, w, h, w)
                    if dx == 0 and dy == 0: cost *= bias_weight
                    if cost < best_cost: best_cost, best_dx, best_dy = cost, float(dx), float(dy)
            
            # Subpixel Refinement (Parabolic)
            if (-search_radius < best_dx < search_radius and -search_radius < best_dy < search_radius):
                c0 = best_cost
                cx_m1 = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int(best_dy), x + int(best_dx) - 1, tile_h, tile_w, h, w, h, w)
                cx_p1 = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int(best_dy), x + int(best_dx) + 1, tile_h, tile_w, h, w, h, w)
                cy_m1 = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int(best_dy) - 1, x + int(best_dx), tile_h, tile_w, h, w, h, w)
                cy_p1 = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int(best_dy) + 1, x + int(best_dx), tile_h, tile_w, h, w, h, w)
                dx_den = 2.0 * (cx_p1 + cx_m1 - 2.0 * c0)
                dy_den = 2.0 * (cy_p1 + cy_m1 - 2.0 * c0)
                if ti.abs(dx_den) > 1e-6: best_dx -= (cx_p1 - cx_m1) / dx_den
                if ti.abs(dy_den) > 1e-6: best_dy -= (cy_p1 - cy_m1) / dy_den

            # Anchor Point Write
            refined_flow[y, x, 0] = best_dx
            refined_flow[y, x, 1] = best_dy

    @ti.kernel
    def _initialize_coarsest_flow_kernel(
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        init_dx: ti.f32, init_dy: ti.f32
    ):
        for r, c in ti.ndrange(flow.shape[0], flow.shape[1]):
            flow[r, c, 0] = init_dx
            flow[r, c, 1] = init_dy

    @ti.kernel
    def _initialize_flow_from_results_kernel(
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        zncc_results: ti.types.ndarray(dtype=ti.f32, ndim=1),
        max_shift: ti.i32
    ):
        best_dy = zncc_results[1] - float(max_shift)
        best_dx = zncc_results[2] - float(max_shift)
        for r, c in ti.ndrange(flow.shape[0], flow.shape[1]):
            flow[r, c, 0] = best_dx
            flow[r, c, 1] = best_dy

    @ti.func
    def _compute_regularization_params(
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        y: int, x: int, tile_h: int, tile_w: int, h_total: int, w_total: int
    ) -> ti.types.vector(3, ti.f32):
        sum_dx, sum_dy, sum_sq_diff, count = 0.0, 0.0, 0.0, 0.0
        center_y, center_x = y + tile_h // 2, x + tile_w // 2
        for dy, dx in ti.ndrange((-1, 2), (-1, 2)):
            if dy == 0 and dx == 0: continue
            ny, nx = center_y + dy * tile_h, center_x + dx * tile_w
            if ny >= 0 and ny < h_total and nx >= 0 and nx < w_total:
                sum_dx += flow[ny, nx, 0]
                sum_dy += flow[ny, nx, 1]
                count += 1.0
        avg_dx, avg_dy = 0.0, 0.0
        lambda_val = 1.5
        if count > 0:
            avg_dx, avg_dy = sum_dx / count, sum_dy / count
            for dy, dx in ti.ndrange((-1, 2), (-1, 2)):
                if dy == 0 and dx == 0: continue
                ny, nx = center_y + dy * tile_h, center_x + dx * tile_w
                if ny >= 0 and ny < h_total and nx >= 0 and nx < w_total:
                    sum_sq_diff += (flow[ny, nx, 0] - avg_dx)**2 + (flow[ny, nx, 1] - avg_dy)**2
            variance = sum_sq_diff / count
            if variance > 5.0: lambda_val *= 0.5
            elif variance < 0.5: lambda_val *= 1.5
        else:
            avg_dx, avg_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        weight = lambda_val * 0.1
        if count < 8.0: weight *= 2.0
        if count < 4.0: weight *= 4.0
        return ti.Vector([avg_dx, avg_dy, weight])

    @ti.kernel
    def _search_coarse_level_kernel(
        ref_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        comp_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        previous_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        refined_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        tile_h: ti.i32, tile_w: ti.i32, search_radius: ti.i32, downscale_factor: ti.i32
    ):
        h, w = ref_layer.shape[0], ref_layer.shape[1]
        tile_area_inv = 1.0 / float(tile_h * tile_w)
        for tile_y, tile_x in ti.ndrange((h + tile_h - 1) // tile_h, (w + tile_w - 1) // tile_w):
            y, x = tm.clamp(tile_y * tile_h, 0, h - tile_h), tm.clamp(tile_x * tile_w, 0, w - tile_w)
            reg = _compute_regularization_params(flow, y, x, tile_h, tile_w, h, w)
            smx, smy, sw = reg[0], reg[1], reg[2]
            center_y, center_x = y + tile_h // 2, x + tile_w // 2
            init_dx, init_dy = int(ti.round(flow[center_y, center_x, 0])), int(ti.round(flow[center_y, center_x, 1]))
            best_cost, best_dx, best_dy = 1e10, float(init_dx), float(init_dy)
            for dy, dx in ti.ndrange((-search_radius, search_radius + 1), (-search_radius, search_radius + 1)):
                cur_dy, cur_dx = init_dy + dy, init_dx + dx
                test_y, test_x = y + cur_dy, x + cur_dx
                if not (test_y <= -tile_h or test_x <= -tile_w or test_y >= h or test_x >= w):
                    vc = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, test_y, test_x, tile_h, tile_w, h, w, h, w) * tile_area_inv
                    ds = (float(cur_dx) - smx)**2 + (float(cur_dy) - smy)**2
                    tc = vc + sw * ds
                    if tc < best_cost: best_cost, best_dx, best_dy = tc, float(cur_dx), float(cur_dy)
            refined_flow[y, x, 0] = best_dx
            refined_flow[y, x, 1] = best_dy

    @ti.kernel
    def _search_fine_level_kernel(
        ref_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        comp_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        previous_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        refined_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        tile_h: ti.i32, tile_w: ti.i32, downscale_factor: ti.i32
    ):
        h, w = ref_layer.shape[0], ref_layer.shape[1]
        tile_area_inv = 1.0 / float(tile_h * tile_w)
        for tile_y, tile_x in ti.ndrange((h + tile_h - 1) // tile_h, (w + tile_w - 1) // tile_w):
            y, x = tm.clamp(tile_y * tile_h, 0, h - tile_h), tm.clamp(tile_x * tile_w, 0, w - tile_w)
            reg = _compute_regularization_params(flow, y, x, tile_h, tile_w, h, w)
            smx, smy, sw = reg[0], reg[1], reg[2]
            center_y, center_x = y + tile_h // 2, x + tile_w // 2
            init_dx, init_dy = int(ti.round(flow[center_y, center_x, 0])), int(ti.round(flow[center_y, center_x, 1]))
            best_cost, best_dx, best_dy = 1e10, float(init_dx), float(init_dy)
            for dy, dx in ti.ndrange((-1, 2), (-1, 2)):
                cur_dy, cur_dx = init_dy + dy, init_dx + dx
                test_y, test_x = y + cur_dy, x + cur_dx
                if not (test_y <= -tile_h or test_x <= -tile_w or test_y >= h or test_x >= w):
                    vc = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, test_y, test_x, tile_h, tile_w, h, w, h, w) * tile_area_inv
                    ds = (float(cur_dx) - smx)**2 + (float(cur_dy) - smy)**2
                    tc = vc + sw * ds
                    if tc < best_cost: best_cost, best_dx, best_dy = tc, float(cur_dx), float(cur_dy)
            refined_flow[y, x, 0] = best_dx
            refined_flow[y, x, 1] = best_dy

    @ti.kernel
    def _parabolic_subpixel_refinement_kernel(
        ref_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        comp_layer: ti.types.ndarray(dtype=ti.f32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        refined_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        tile_h: ti.i32, tile_w: ti.i32
    ):
        h, w = ref_layer.shape[0], ref_layer.shape[1]
        for tile_y, tile_x in ti.ndrange((h + tile_h - 1) // tile_h, (w + tile_w - 1) // tile_w):
            y, x = tm.clamp(tile_y * tile_h, 0, h - tile_h), tm.clamp(tile_x * tile_w, 0, w - tile_w)
            center_y, center_x = y + tile_h // 2, x + tile_w // 2
            int_dx, int_dy = int(ti.round(flow[center_y, center_x, 0])), int(ti.round(flow[center_y, center_x, 1]))
            c0 = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int_dy, x + int_dx, tile_h, tile_w, h, w, h, w)
            cm1x = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int_dy, x + int_dx - 1, tile_h, tile_w, h, w, h, w)
            cp1x = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int_dy, x + int_dx + 1, tile_h, tile_w, h, w, h, w)
            cm1y = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int_dy - 1, x + int_dx, tile_h, tile_w, h, w, h, w)
            cp1y = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, y + int_dy + 1, x + int_dx, tile_h, tile_w, h, w, h, w)
            dx, dy = 0.0, 0.0
            dx_den = 2.0 * (cp1x + cm1x - 2.0 * c0)
            dy_den = 2.0 * (cp1y + cm1y - 2.0 * c0)
            if ti.abs(dx_den) > 1e-6: dx = tm.clamp(-(cp1x - cm1x) / dx_den, -0.5, 0.5)
            if ti.abs(dy_den) > 1e-6: dy = tm.clamp(-(cp1y - cm1y) / dy_den, -0.5, 0.5)
            refined_flow[y, x, 0] = float(int_dx) + dx
            refined_flow[y, x, 1] = float(int_dy) + dy

    @ti.kernel
    def _broadcast_tile_flow_kernel(
        tile_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        full_flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        step_y: ti.i32,
        step_x: ti.i32,
        tile_h: ti.i32,
        tile_w: ti.i32
    ):
        h, w = full_flow.shape[0], full_flow.shape[1]
        for y, x in ti.ndrange(h, w):
            ay, ax = (y // step_y) * step_y, (x // step_x) * step_x
            ay, ax = tm.clamp(ay, 0, h - tile_h), tm.clamp(ax, 0, w - tile_w)
            full_flow[y, x, 0] = tile_flow[ay, ax, 0]
            full_flow[y, x, 1] = tile_flow[ay, ax, 1]

    @ti.kernel
    def _upsample_flow_aot_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        scale: ti.f32
    ):
        sh, sw = src.shape[0], src.shape[1]
        dh, dw = dst.shape[0], dst.shape[1]
        for y, x in ti.ndrange(dh, dw):
            u, v = (float(x) + 0.5) / float(dw), (float(y) + 0.5) / float(dh)
            sx, sy = u * float(sw) - 0.5, v * float(sh) - 0.5
            x0, y0 = int(ti.floor(sx)), int(ti.floor(sy))
            fx, fy = sx - float(x0), sy - float(y0)
            x0, y0 = tm.clamp(x0, 0, sw - 2), tm.clamp(y0, 0, sh - 2)
            for c in ti.static(range(2)):
                v00, v10 = src[y0, x0, c], src[y0, x0 + 1, c]
                v01, v11 = src[y0 + 1, x0, c], src[y0 + 1, x0 + 1, c]
                dst[y, x, c] = ((v00 * (1.0 - fx) + v10 * fx) * (1.0 - fy) + (v01 * (1.0 - fx) + v11 * fx) * fy) * scale

    @ti.kernel
    def _zero_flow_kernel(flow: ti.types.ndarray(dtype=ti.f32, ndim=3)):
        for r, c in ti.ndrange(flow.shape[0], flow.shape[1]):
            flow[r, c, 0] = 0.0
            flow[r, c, 1] = 0.0

def record_alignment_graph(g: ti.graph.GraphBuilder):
    """Record 'One Big Graph' orchestration for 3-layer alignment."""
    ref_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l0", ti.f32, ndim=2)
    comp_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l0", ti.f32, ndim=2)
    flow_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l0", ti.f32, ndim=3)
    flow_tmp_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_tmp_l0", ti.f32, ndim=3)
    ref_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l1", ti.f32, ndim=2)
    comp_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l1", ti.f32, ndim=2)
    flow_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l1", ti.f32, ndim=3)
    flow_tmp_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_tmp_l1", ti.f32, ndim=3)
    ref_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l2", ti.f32, ndim=2)
    comp_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l2", ti.f32, ndim=2)
    flow_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l2", ti.f32, ndim=3)
    flow_tmp_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_tmp_l2", ti.f32, ndim=3)
    zncc_surf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zncc_surf", ti.f32, ndim=2)
    zncc_res = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zncc_res", ti.f32, ndim=1)
    tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
    tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
    search_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "search_radius", ti.i32)
    coarse_dist = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "coarse_dist", ti.i32)
    scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    ds_fac = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ds_fac", ti.i32)
    zncc_shift = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "zncc_shift", ti.i32)
    step_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step_y", ti.i32)
    step_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step_x", ti.i32)
    g.dispatch(ncc_module._compute_global_zncc_surface, ref_l2, comp_l2, zncc_surf, zncc_shift)
    g.dispatch(ncc_module._reduce_min_2d_kernel, zncc_surf, zncc_res)
    g.dispatch(_initialize_flow_from_results_kernel, flow_l2, zncc_res, zncc_shift)
    g.dispatch(_block_search_kernel, ref_l2, comp_l2, flow_tmp_l2, tile_h, tile_w, search_radius)
    g.dispatch(_broadcast_tile_flow_kernel, flow_tmp_l2, flow_l2, tile_h, tile_w, tile_h, tile_w)
    g.dispatch(_parabolic_subpixel_refinement_kernel, ref_l2, comp_l2, flow_l2, flow_tmp_l2, tile_h, tile_w)
    g.dispatch(_broadcast_tile_flow_kernel, flow_tmp_l2, flow_l2, step_y, step_x, tile_h, tile_w)
    g.dispatch(_upsample_flow_aot_kernel, flow_l2, flow_l1, scale)
    g.dispatch(_search_coarse_level_kernel, ref_l1, comp_l1, flow_l1, flow_l2, flow_tmp_l1, tile_h, tile_w, coarse_dist, ds_fac)
    g.dispatch(_broadcast_tile_flow_kernel, flow_tmp_l1, flow_l1, tile_h, tile_w, tile_h, tile_w)
    g.dispatch(_parabolic_subpixel_refinement_kernel, ref_l1, comp_l1, flow_l1, flow_tmp_l1, tile_h, tile_w)
    g.dispatch(_broadcast_tile_flow_kernel, flow_tmp_l1, flow_l1, step_y, step_x, tile_h, tile_w)
    g.dispatch(_upsample_flow_aot_kernel, flow_l1, flow_l0, scale)
    g.dispatch(_search_fine_level_kernel, ref_l0, comp_l0, flow_l0, flow_l1, flow_tmp_l0, tile_h, tile_w, ds_fac)
    g.dispatch(_broadcast_tile_flow_kernel, flow_tmp_l0, flow_l0, tile_h, tile_w, tile_h, tile_w)


def process_single_layer(
    ref_layer_gpu,
    comp_layer_gpu,
    previous_flow_gpu,
    layer_index: int,
    total_layers: int,
    tile_h,
    tile_w,
    search_dist,
    downscale_factor=4,
    # === AOT RECORDING ARGS ===
    g=None,
    flow_out_arg=None,
    flow_tmp_arg=None,
    z_res_arg=None,
    search_radius_arg=None,
    zncc_shift_arg=None,
    scale_arg=None,
    step_y_arg=None,
    step_x_arg=None,
):
    is_coarsest = (layer_index == total_layers - 1)
    is_finest = (layer_index == 0)

    if g is None:
        flow_gpu = common.get_temp_buffer(ref_layer_gpu.shape[:2] + (2,), ti.f32, buffer_provider="pool")
        refined_flow_gpu = common.get_temp_buffer(ref_layer_gpu.shape[:2] + (2,), ti.f32, buffer_provider="pool")
    else:
        flow_gpu, refined_flow_gpu = flow_out_arg, flow_tmp_arg

    # 1. Initialization
    if is_coarsest:
        if g is None:
            global_dx, global_dy, _ = ncc_module.global_translate_zncc(ref_layer_gpu, comp_layer_gpu, max_shift=32)
            _initialize_flow_from_results_jit(flow_gpu, float(global_dx), float(global_dy))
        else:
            g.dispatch(_initialize_flow_from_results_kernel, flow_gpu, z_res_arg, zncc_shift_arg)
    else:
        if g is None:
            # Note: We use the local _upsample_flow_aot_kernel for parity even in JIT
            _upsample_flow_aot_kernel(previous_flow_gpu, flow_gpu, float(downscale_factor))
        else:
            g.dispatch(_upsample_flow_aot_kernel, previous_flow_gpu, flow_gpu, scale_arg)

    if g is None: _zero_flow_kernel(refined_flow_gpu)
    else: g.dispatch(_zero_flow_kernel, refined_flow_gpu)

    # 2. Search
    if is_finest:
        if g is None:
            _search_fine_level_kernel(ref_layer_gpu, comp_layer_gpu, flow_gpu, previous_flow_gpu, refined_flow_gpu, tile_h, tile_w, downscale_factor)
            _broadcast_tile_flow_kernel(refined_flow_gpu, flow_gpu, tile_h, tile_w, tile_h, tile_w)
        else:
            g.dispatch(_search_fine_level_kernel, ref_layer_gpu, comp_layer_gpu, flow_gpu, previous_flow_gpu, refined_flow_gpu, tile_h, tile_w, downscale_factor)
            g.dispatch(_broadcast_tile_flow_kernel, refined_flow_gpu, flow_gpu, tile_h, tile_w, tile_h, tile_w)
    elif is_coarsest:
        if g is None:
            radius = max(4, int(search_dist * 2))
            _block_search_kernel(ref_layer_gpu, comp_layer_gpu, refined_flow_gpu, tile_h, tile_w, radius)
            _broadcast_tile_flow_kernel(refined_flow_gpu, flow_gpu, tile_h, tile_w, tile_h, tile_w)
        else:
            g.dispatch(_block_search_kernel, ref_layer_gpu, comp_layer_gpu, refined_flow_gpu, tile_h, tile_w, search_radius_arg)
            g.dispatch(_broadcast_tile_flow_kernel, refined_flow_gpu, flow_gpu, tile_h, tile_w, tile_h, tile_w)
    else:
        if g is None:
            dist = max(2, int(search_dist))
            _search_coarse_level_kernel(ref_layer_gpu, comp_layer_gpu, flow_gpu, previous_flow_gpu, refined_flow_gpu, tile_h, tile_w, dist, downscale_factor)
            _broadcast_tile_flow_kernel(refined_flow_gpu, flow_gpu, tile_h, tile_w, tile_h, tile_w)
        else:
            g.dispatch(_search_coarse_level_kernel, ref_layer_gpu, comp_layer_gpu, flow_gpu, previous_flow_gpu, refined_flow_gpu, tile_h, tile_w, search_radius_arg, downscale_factor)
            g.dispatch(_broadcast_tile_flow_kernel, refined_flow_gpu, flow_gpu, tile_h, tile_w, tile_h, tile_w)

    # 3. Refinement (Overlap Smart Fusion)
    if not is_finest:
        if g is None:
            sy, sx = tile_h // 2, tile_w // 2
            _parabolic_subpixel_refinement_kernel(ref_layer_gpu, comp_layer_gpu, flow_gpu, refined_flow_gpu, tile_h, tile_w)
            _broadcast_tile_flow_kernel(refined_flow_gpu, flow_gpu, sy, sx, tile_h, tile_w)
        else:
            g.dispatch(_parabolic_subpixel_refinement_kernel, ref_layer_gpu, comp_layer_gpu, flow_gpu, refined_flow_gpu, tile_h, tile_w)
            g.dispatch(_broadcast_tile_flow_kernel, refined_flow_gpu, flow_gpu, step_y_arg, step_x_arg, tile_h, tile_w)

    if g is None:
        common.release_temp_buffer(refined_flow_gpu)
        return flow_gpu
    return None


def compute_alignment_flow(
    ref_work_data: np.ndarray,
    current_work_data: np.ndarray,
    tile_h: int = 16,
    tile_w: int = 16,
    n_layers: int = 3,
    search_dist: float = 2.0,
    downscale_factor: int = 4,
    min_pyramid_size: int = ImageAlignmentConfig.MIN_PYRAMID_LAYER_SIZE,
    return_confidence: bool = False,
) -> any:
    """
    Compute alignment flow - Pure Taichi JIT implementation.
    """

    if not TAICHI_AVAILABLE or not TAICHI_MODULES_AVAILABLE:
        raise ImportError("Taichi not ready")

    ti.sync()
    t_total_start = time.perf_counter()

    ref_gpu, ref_is_temp = common.ensure_taichi_field(ref_work_data, dtype=ti.f32)
    comp_gpu, comp_is_temp = common.ensure_taichi_field(current_work_data, dtype=ti.f32)

    print(f"Pyramid Initiation ({downscale_factor}x):")
    t_pyr_ref_start = time.perf_counter()
    ref_pyramid = build_image_pyramid_gpu(
        ref_gpu,
        n_levels=n_layers,
        min_size=min_pyramid_size,
        downscale_factor=downscale_factor,
    )
    ti.sync()
    t_pyr_ref = (time.perf_counter() - t_pyr_ref_start) * 1000
    print(f" - Ref Pyramid: {t_pyr_ref:.2f}ms ({len(ref_pyramid)} levels)")
    for lvl_i, lvl in enumerate(ref_pyramid):
        print(f"   Level {lvl_i}: {lvl.shape[0]}x{lvl.shape[1]}")

    t_pyr_comp_start = time.perf_counter()
    current_pyramid = build_image_pyramid_gpu(
        comp_gpu,
        n_levels=n_layers,
        min_size=min_pyramid_size,
        downscale_factor=downscale_factor,
    )
    ti.sync()
    t_pyr_comp = (time.perf_counter() - t_pyr_comp_start) * 1000
    print(f" - Comp Pyramid: {t_pyr_comp:.2f}ms")

    actual_layers = min(len(ref_pyramid), len(current_pyramid))

    # ── AOT-style header log (for direct comparison) ───────────────────────
    radius = int(search_dist * 2)
    dist   = int(search_dist)
    print(f"[ComputeFlowJIT] graph='align_end_to_end_{actual_layers}layer' "
          f"tile=({tile_h},{tile_w}) radius={radius} dist={dist} "
          f"scale={float(downscale_factor):.1f} ds={downscale_factor} zncc_shift=32")
    for i in range(actual_layers):
        rh, rw = ref_pyramid[i].shape[0], ref_pyramid[i].shape[1]
        ch, cw = current_pyramid[i].shape[0], current_pyramid[i].shape[1]
        print(f"[ComputeFlowJIT]   L{i}: ref({rh},{rw}) comp({ch},{cw})")

    # ── Layer-by-layer flow computation ───────────────────────────────────
    flow_gpu = None

    for i in range(actual_layers - 1, -1, -1):
        prev_flow = flow_gpu
        is_finest = i == 0

        t_layer = time.perf_counter()
        flow_gpu = process_single_layer(
            ref_pyramid[i],
            current_pyramid[i],
            prev_flow,
            i,
            actual_layers,
            tile_h,
            tile_w,
            search_dist,
            downscale_factor,
        )
        ti.sync()
        ms_layer = (time.perf_counter() - t_layer) * 1000
        print(f"[ComputeFlowJIT]   layer {i} done in {ms_layer:.2f} ms")

        # Store the final result
        if is_finest:
            pass  # No cost map storage anymore

        if prev_flow is not None:
            common.release_temp_buffer(prev_flow)

    # No final RANSAC cleanup - return raw flow

    # Release Buffers
    for i in range(len(ref_pyramid)):
        common.release_temp_buffer(ref_pyramid[i])
    for i in range(len(current_pyramid)):
        common.release_temp_buffer(current_pyramid[i])

    if ref_is_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_is_temp:
        common.release_temp_buffer(comp_gpu)

    ti.sync()
    t_total = (time.perf_counter() - t_total_start) * 1000
    print(f"[ComputeFlowJIT] Done in {t_total:.2f} ms\n")

    return flow_gpu


def free_flow_memory(flow_data):
    """Free flow memory (no-op in Python)."""
    pass
